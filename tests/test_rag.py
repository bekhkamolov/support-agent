from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from support_agent.ingest import Chunk
from support_agent.llm import Usage, usage_from_response
from support_agent.rag import SYSTEM_PROMPT, RagAnswer, RagPipeline, build_user_prompt
from support_agent.retrieval import SearchResult

CHUNKS = [
    Chunk(chunk_id="ret#0", doc_id="ret", title="Returns", text="Return items within 30 days"),
    Chunk(chunk_id="ship#0", doc_id="ship", title="Shipping", text="Shipping costs EUR 4.95 in Germany"),
]


class FakeRetriever:
    name = "fake"

    def search(self, query, k=5):
        return [SearchResult(chunk=c, score=1.0) for c in CHUNKS[:k]]


class FakeLLM:
    """Returns a fixed answer and records what it was called with (no network)."""

    name = "fake"

    def __init__(self, answer: RagAnswer):
        self.answer = answer
        self.calls = []

    def parse(self, system, user, schema, cache_key=None):
        self.calls.append({"system": system, "user": user, "schema": schema, "cache_key": cache_key})
        return self.answer, Usage(prompt_tokens=100, completion_tokens=20, cached_tokens=60)


def test_user_prompt_contains_excerpts_and_question():
    prompt = build_user_prompt("How long can I return?", FakeRetriever().search("x"))
    assert 'doc_id="ret"' in prompt and 'doc_id="ship"' in prompt
    assert prompt.endswith("Customer question: How long can I return?")


def test_pipeline_keeps_valid_citations_and_drops_invented_ones():
    llm = FakeLLM(RagAnswer(answer="30 days.", cited_doc_ids=["ret", "ret", "made-up"], confidence="high"))
    result = RagPipeline(FakeRetriever(), llm).answer("How long can I return?")
    assert result.answer.cited_doc_ids == ["ret"]
    assert result.invalid_citations == ["made-up"]
    assert result.retrieved_doc_ids == ["ret", "ship"]
    assert result.usage.cached_tokens == 60


def test_system_prompt_is_static_and_sent_first():
    llm = FakeLLM(RagAnswer(answer="ok", cited_doc_ids=[], confidence="low"))
    pipeline = RagPipeline(FakeRetriever(), llm)
    pipeline.answer("question one")
    pipeline.answer("a different question")
    assert llm.calls[0]["system"] == llm.calls[1]["system"] == SYSTEM_PROMPT
    assert "question one" in llm.calls[0]["user"]


def test_cache_key_is_sent_only_when_enabled():
    answer = RagAnswer(answer="ok", cited_doc_ids=[], confidence="low")
    on, off = FakeLLM(answer), FakeLLM(answer)
    RagPipeline(FakeRetriever(), on, use_cache=True).answer("q")
    RagPipeline(FakeRetriever(), off, use_cache=False).answer("q")
    assert on.calls[0]["cache_key"] and off.calls[0]["cache_key"] is None


def test_rag_answer_rejects_unknown_confidence():
    with pytest.raises(ValidationError):
        RagAnswer(answer="x", cited_doc_ids=[], confidence="very high")


@pytest.mark.parametrize(
    "usage, cached",
    [
        (SimpleNamespace(prompt_tokens=10, completion_tokens=2, prompt_tokens_details={"cached_tokens": 7}), 7),
        (SimpleNamespace(prompt_tokens=10, completion_tokens=2, prompt_tokens_details=SimpleNamespace(cached_tokens=5)), 5),
        (SimpleNamespace(prompt_tokens=10, completion_tokens=2, model_extra={"prompt_tokens_details": {"cached_tokens": 3}}), 3),
        (SimpleNamespace(prompt_tokens=10, completion_tokens=2), 0),
    ],
)
def test_usage_reads_cached_tokens_from_any_sdk_shape(usage, cached):
    u = usage_from_response(usage)
    assert (u.prompt_tokens, u.completion_tokens, u.cached_tokens) == (10, 2, cached)
