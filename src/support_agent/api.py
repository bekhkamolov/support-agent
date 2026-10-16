"""HTTP API for the support agent (FastAPI).

Run:
    uvicorn support_agent.api:create_app --factory --port 8000

Endpoints:
    GET  /         chat page (static HTML, no build step)
    GET  /health   liveness and configuration status
    POST /chat     one customer message; pass the returned session_id to continue a conversation

Sessions live in memory: each has its own conversation history and its own copy of the demo order
database, so visitors of a public demo cannot affect each other's orders. Restarting the server
clears all sessions.
"""
from __future__ import annotations

import os
import threading
import time
import uuid
from collections import OrderedDict, deque
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from opentelemetry import trace
from pydantic import BaseModel, Field
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError
from pydantic_ai.messages import ModelMessage

from .agent import SupportAgent
from .orders import OrderStore

MAX_SESSIONS = 500  # oldest sessions are dropped beyond this (bounded memory)
SESSION_TTL_S = 60 * 60
MAX_TURNS = 20  # per session; bounds prompt size and cost

STATIC_DIR = Path(__file__).parent / "static"

AgentFactory = Callable[[OrderStore], SupportAgent]


class RateLimiter:
    """Sliding-window limit per client, so a public demo cannot exhaust the model API quota."""

    def __init__(self, limit: int, window_s: float = 3600, max_clients: int = 10_000):
        self.limit, self.window_s, self.max_clients = limit, window_s, max_clients
        self._hits: OrderedDict[str, deque] = OrderedDict()
        self._lock = threading.Lock()

    def retry_after(self, client: str) -> int:
        """0 if the request is allowed (and counted), else seconds until the next one is."""
        now = time.monotonic()
        with self._lock:
            hits = self._hits.setdefault(client, deque())
            self._hits.move_to_end(client)
            while hits and now - hits[0] > self.window_s:
                hits.popleft()
            if len(hits) >= self.limit:
                return int(self.window_s - (now - hits[0])) + 1
            hits.append(now)
            while len(self._hits) > self.max_clients:
                self._hits.popitem(last=False)
            return 0


def client_ip(request: Request, trust_proxy: bool) -> str:
    """Client address. Behind a reverse proxy (e.g. Hugging Face Spaces) the real client is the first
    X-Forwarded-For entry; the header is only trusted when configured, because clients can set it."""
    if trust_proxy and (forwarded := request.headers.get("x-forwarded-for")):
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
tracer = trace.get_tracer("support_agent.api")  # no-op unless tracing.setup_tracing() was called


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{8,64}$")


class ToolCall(BaseModel):
    tool: str
    outcome: str


class ChatResponse(BaseModel):
    session_id: str
    message: str
    cited_doc_ids: list[str]
    escalated: bool
    ticket_id: str | None
    tool_calls: list[ToolCall]
    latency_ms: float


@dataclass
class Session:
    agent: SupportAgent
    history: list[ModelMessage] | None = None
    turns: int = 0
    last_used: float = field(default_factory=time.monotonic)
    lock: threading.Lock = field(default_factory=threading.Lock)


class SessionStore:
    def __init__(self, factory: AgentFactory, max_sessions: int = MAX_SESSIONS, ttl_s: float = SESSION_TTL_S):
        self.factory, self.max_sessions, self.ttl_s = factory, max_sessions, ttl_s
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._lock = threading.Lock()

    def get_or_create(self, session_id: str | None) -> tuple[str, Session]:
        now = time.monotonic()
        with self._lock:
            for sid in [s for s, v in self._sessions.items() if now - v.last_used > self.ttl_s]:
                del self._sessions[sid]
            if session_id and session_id in self._sessions:
                self._sessions.move_to_end(session_id)
                session = self._sessions[session_id]
            else:  # unknown or expired ids start a new session (ids are never reused across sessions)
                session_id = uuid.uuid4().hex
                session = self._sessions[session_id] = Session(agent=self.factory(OrderStore()))
                while len(self._sessions) > self.max_sessions:
                    self._sessions.popitem(last=False)
            session.last_used = now
            return session_id, session


def default_agent_factory() -> AgentFactory | None:
    """Agent backed by Mistral; None if no API key is configured (the API then reports not ready)."""
    if not os.getenv("MISTRAL_API_KEY", "").strip():
        return None
    from .agent import mistral_model
    from .ingest import build_chunks
    from .retrieval import DenseRetriever
    from .retrieval.dense import MistralEmbedder

    model = mistral_model(os.getenv("AGENT_MODEL", "").strip() or "ministral-14b-latest")  # empty = default
    retriever = DenseRetriever(build_chunks(), MistralEmbedder())
    return lambda store: SupportAgent(model, retriever, store)


def create_app(
    agent_factory: AgentFactory | None = None, tracing: bool | None = None, rate_limit: int | None = None
) -> FastAPI:
    """App factory. Tests pass a factory with a scripted model; production builds it from env vars.

    rate_limit: messages per client and hour (default: env RATE_LIMIT_PER_HOUR, else 60).
    """
    limiter = RateLimiter(rate_limit or int(os.getenv("RATE_LIMIT_PER_HOUR", "").strip() or 60))
    trust_proxy = os.getenv("TRUST_PROXY_HEADERS", "").strip() == "1"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from . import config  # noqa: F401  (loads .env)
        from .tracing import setup_tracing

        app.state.tracing = setup_tracing() if tracing is None else tracing
        factory = agent_factory or default_agent_factory()
        app.state.sessions = SessionStore(factory) if factory else None
        yield
        if app.state.tracing:
            trace.get_tracer_provider().shutdown()  # flush spans that are still buffered

    app = FastAPI(title="Nordwind support agent", version="0.1.0", lifespan=lifespan)

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "agent_ready": app.state.sessions is not None, "tracing": app.state.tracing}

    @app.post("/chat", response_model=ChatResponse)
    def chat(req: ChatRequest, request: Request) -> ChatResponse:
        # A sync endpoint: FastAPI runs it in a worker thread, so a slow model call does not block
        # other requests.
        if app.state.sessions is None:
            raise HTTPException(503, "Agent not configured: set MISTRAL_API_KEY.")
        if wait := limiter.retry_after(client_ip(request, trust_proxy)):
            raise HTTPException(429, f"Too many messages from this address; try again in {wait // 60 + 1} min.",
                                headers={"Retry-After": str(wait)})
        session_id, session = app.state.sessions.get_or_create(req.session_id)
        with session.lock:  # one message at a time per conversation
            if session.turns >= MAX_TURNS:
                raise HTTPException(409, f"Conversation limit of {MAX_TURNS} messages reached; start a new session.")
            with tracer.start_as_current_span("chat turn") as span:
                span.set_attribute("langfuse.session.id", session_id)
                span.set_attribute("session.turn", session.turns + 1)
                try:
                    result, session.history = session.agent.ask(req.message, session.history)
                except (ModelAPIError, ModelHTTPError) as e:
                    span.record_exception(e)
                    raise HTTPException(502, "The language model is unavailable, please try again.") from e
                span.set_attribute("agent.escalated", result.escalated)
                span.set_attribute("agent.guardrail_triggered", result.guardrail_triggered)
                span.set_attribute("agent.tools", [c.tool for c in result.tool_calls])
            session.turns += 1
        return ChatResponse(
            session_id=session_id,
            message=result.message,
            cited_doc_ids=result.cited_doc_ids,
            escalated=result.escalated,
            ticket_id=result.ticket_id,
            tool_calls=[ToolCall(tool=c.tool, outcome=c.outcome) for c in result.tool_calls],
            latency_ms=round(result.latency_ms, 1),
        )

    return app
