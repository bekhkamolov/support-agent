"""API tests with a scripted model (no network, no API key)."""
import base64

import pytest
from fastapi.testclient import TestClient
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from support_agent import api
from support_agent.agent import SupportAgent
from support_agent.tracing import langfuse_config


class NoRetriever:
    name = "none"

    def search(self, query, k=5):
        return []


def final(info: AgentInfo, message: str) -> ModelResponse:
    return ModelResponse(parts=[ToolCallPart(tool_name=info.output_tools[0].name, args={"message": message})])


def echo_model() -> FunctionModel:
    """Replies with all customer messages it has seen, so tests can check the conversation history."""

    def fn(messages, info):
        prompts = [p.content for m in messages for p in m.parts if p.part_kind == "user-prompt"]
        return final(info, " | ".join(prompts))

    return FunctionModel(fn)


def return_jeans_model() -> FunctionModel:
    """Starts a return for anna's jeans, then reports the tool outcome."""

    def fn(messages, info):
        last_prompt = max(i for i, m in enumerate(messages) if any(p.part_kind == "user-prompt" for p in m.parts))
        returns = [p for m in messages[last_prompt:] for p in m.parts
                   if p.part_kind == "tool-return" and p.tool_name == "start_return"]
        if not returns:
            args = {"order_id": "NW-100001", "email": "anna@example.com", "skus": ["JNS-001"], "reason": "wrong_size"}
            return ModelResponse(parts=[ToolCallPart(tool_name="start_return", args=args)])
        return final(info, returns[-1].content.status)

    return FunctionModel(fn)


def client_for(model) -> TestClient:
    app = api.create_app(agent_factory=lambda store: SupportAgent(model, NoRetriever(), store), tracing=False)
    return TestClient(app)


def test_health_reports_not_ready_without_api_key(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    with TestClient(api.create_app(tracing=False)) as client:
        assert client.get("/health").json() == {"status": "ok", "agent_ready": False, "tracing": False}
        assert client.post("/chat", json={"message": "hi"}).status_code == 503


def test_conversation_continues_with_session_id():
    with client_for(echo_model()) as client:
        first = client.post("/chat", json={"message": "Where is my order?"}).json()
        second = client.post("/chat", json={"message": "NW-100004", "session_id": first["session_id"]}).json()
    assert second["session_id"] == first["session_id"]
    assert second["message"] == "Where is my order? | NW-100004"


def test_unknown_session_id_starts_a_new_session():
    with client_for(echo_model()) as client:
        r = client.post("/chat", json={"message": "hello", "session_id": "does-not-exist"}).json()
    assert r["session_id"] != "does-not-exist" and r["message"] == "hello"


def test_sessions_have_separate_order_databases():
    with client_for(return_jeans_model()) as client:
        a = client.post("/chat", json={"message": "Return jeans NW-100001 anna@example.com"}).json()
        a2 = client.post("/chat", json={"message": "Return jeans NW-100001 anna@example.com",
                                        "session_id": a["session_id"]}).json()
        b = client.post("/chat", json={"message": "Return jeans NW-100001 anna@example.com"}).json()
    assert a["message"] == "started" and a["tool_calls"] == [{"tool": "start_return", "outcome": "started"}]
    assert a2["message"] == "rejected"  # already returned in this session
    assert b["message"] == "started"  # another visitor is not affected


@pytest.mark.parametrize("body", [
    {"message": ""},
    {"message": "x" * 2001},
    {"message": "hi", "session_id": "bad id!"},
    {},
])
def test_invalid_requests_are_rejected(body):
    with client_for(echo_model()) as client:
        assert client.post("/chat", json=body).status_code == 422


def test_conversation_length_is_limited(monkeypatch):
    monkeypatch.setattr(api, "MAX_TURNS", 2)
    with client_for(echo_model()) as client:
        sid = client.post("/chat", json={"message": "1"}).json()["session_id"]
        assert client.post("/chat", json={"message": "2", "session_id": sid}).status_code == 200
        assert client.post("/chat", json={"message": "3", "session_id": sid}).status_code == 409


def test_model_outage_returns_502_without_internal_details():
    def broken(messages, info):
        raise ModelHTTPError(status_code=503, model_name="m", body="secret upstream details")

    with client_for(FunctionModel(broken)) as client:
        r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 502 and "secret" not in r.text


def test_old_sessions_are_dropped_beyond_the_limit():
    store = api.SessionStore(lambda s: object(), max_sessions=2)
    first, _ = store.get_or_create(None)
    store.get_or_create(None)
    store.get_or_create(None)
    again, _ = store.get_or_create(first)
    assert again != first  # the oldest session was evicted, so a new one is created


def test_chat_page_is_served():
    with client_for(echo_model()) as client:
        r = client.get("/")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
    assert 'fetch("chat"' in r.text and ".innerHTML" not in r.text  # replies are inserted as text only


def test_rate_limit_per_client(monkeypatch):
    app = api.create_app(agent_factory=lambda store: SupportAgent(echo_model(), NoRetriever(), store),
                         tracing=False, rate_limit=2)
    with TestClient(app) as client:
        assert [client.post("/chat", json={"message": str(i)}).status_code for i in range(2)] == [200, 200]
        r = client.post("/chat", json={"message": "3"})
    assert r.status_code == 429 and int(r.headers["Retry-After"]) > 0


def test_rate_limiter_window_and_separate_clients(monkeypatch):
    now = [1000.0]
    monkeypatch.setattr(api.time, "monotonic", lambda: now[0])
    limiter = api.RateLimiter(limit=2, window_s=60)
    assert [limiter.retry_after("a") for _ in range(3)] == [0, 0, 61]
    assert limiter.retry_after("b") == 0  # other clients are not affected
    now[0] += 61
    assert limiter.retry_after("a") == 0  # window has passed


def test_forwarded_ip_is_only_trusted_when_configured():
    class Req:
        headers = {"x-forwarded-for": "203.0.113.7, 10.0.0.1"}
        client = type("C", (), {"host": "10.0.0.1"})()

    assert api.client_ip(Req(), trust_proxy=True) == "203.0.113.7"
    assert api.client_ip(Req(), trust_proxy=False) == "10.0.0.1"  # header could be forged


def test_health_checks_are_not_traced_but_chat_requests_are():
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    from support_agent.tracing import health_check_sampler

    from opentelemetry import trace

    # A real FastAPI request, not hand-made spans: the request span is named only "GET" when the
    # sampler runs (a first version filtered on the final name "GET /health" and let everything through).
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=health_check_sampler())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    previous = trace.get_tracer_provider()
    trace._TRACER_PROVIDER = provider  # set_tracer_provider() refuses to override; restore below
    try:
        with client_for(echo_model()) as client:
            client.get("/health")
            client.post("/chat", json={"message": "hi"})
    finally:
        trace._TRACER_PROVIDER = previous
    names = {s.name for s in exporter.get_finished_spans()}
    assert "POST /chat" in names and "chat turn" in names
    assert not any("health" in s.name or (s.attributes or {}).get("url.path") == "/health"
                   for s in exporter.get_finished_spans())


def test_langfuse_config_is_off_without_keys():
    assert langfuse_config({}) is None
    assert langfuse_config({"LANGFUSE_PUBLIC_KEY": "pk"}) is None


def test_langfuse_config_builds_otlp_endpoint_and_basic_auth():
    cfg = langfuse_config({"LANGFUSE_PUBLIC_KEY": "pk-lf-1", "LANGFUSE_SECRET_KEY": "sk-lf-2",
                           "LANGFUSE_HOST": "https://us.cloud.langfuse.com/", "LANGFUSE_INCLUDE_CONTENT": "false"})
    assert cfg.endpoint == "https://us.cloud.langfuse.com/api/public/otel/v1/traces"
    assert base64.b64decode(cfg.headers["Authorization"].removeprefix("Basic ")) == b"pk-lf-1:sk-lf-2"
    assert cfg.include_content is False
    assert langfuse_config({"LANGFUSE_PUBLIC_KEY": "a", "LANGFUSE_SECRET_KEY": "b"}).endpoint.startswith(
        "https://cloud.langfuse.com/")  # EU region by default
