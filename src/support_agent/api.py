"""HTTP API for the support agent (FastAPI).

Run:
    uvicorn support_agent.api:create_app --factory --port 8000

Endpoints:
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
from collections import OrderedDict
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from pydantic import BaseModel, Field
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError
from pydantic_ai.messages import ModelMessage

from .agent import SupportAgent
from .orders import OrderStore

MAX_SESSIONS = 500  # oldest sessions are dropped beyond this (bounded memory)
SESSION_TTL_S = 60 * 60
MAX_TURNS = 20  # per session; bounds prompt size and cost

AgentFactory = Callable[[OrderStore], SupportAgent]
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


def create_app(agent_factory: AgentFactory | None = None, tracing: bool | None = None) -> FastAPI:
    """App factory. Tests pass a factory with a scripted model; production builds it from env vars."""

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

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "agent_ready": app.state.sessions is not None, "tracing": app.state.tracing}

    @app.post("/chat", response_model=ChatResponse)
    def chat(req: ChatRequest) -> ChatResponse:
        # A sync endpoint: FastAPI runs it in a worker thread, so a slow model call does not block
        # other requests.
        if app.state.sessions is None:
            raise HTTPException(503, "Agent not configured: set MISTRAL_API_KEY.")
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
