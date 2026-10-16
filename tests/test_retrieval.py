import numpy as np

from support_agent.ingest import Chunk
from support_agent.retrieval import BM25Retriever, DenseRetriever, HybridRetriever

CHUNKS = [
    Chunk(chunk_id="ship#0", doc_id="ship", title="Shipping", text="Shipping costs EUR 4.95 in Germany"),
    Chunk(chunk_id="ret#0", doc_id="ret", title="Returns", text="Return items within 30 days"),
    Chunk(chunk_id="pay#0", doc_id="pay", title="Payment", text="We accept PayPal and Klarna"),
]


class FakeEmbedder:
    """Deterministic bag-of-words embedder for tests (no network)."""

    name = "fake"
    vocab = ["shipping", "return", "paypal", "germany", "days", "klarna"]

    def embed(self, texts):
        return np.array([[t.lower().count(w) + 0.01 for w in self.vocab] for t in texts], dtype=np.float32)


def test_bm25_finds_keyword_match():
    assert BM25Retriever(CHUNKS).search("paypal", k=1)[0].chunk.doc_id == "pay"


def test_dense_with_fake_embedder(tmp_path, monkeypatch):
    monkeypatch.setattr("support_agent.retrieval.dense.CACHE_DIR", tmp_path)
    r = DenseRetriever(CHUNKS, FakeEmbedder())
    assert r.search("return within days", k=1)[0].chunk.doc_id == "ret"


def test_hybrid_fuses_rankings(tmp_path, monkeypatch):
    monkeypatch.setattr("support_agent.retrieval.dense.CACHE_DIR", tmp_path)
    hybrid = HybridRetriever([BM25Retriever(CHUNKS), DenseRetriever(CHUNKS, FakeEmbedder())])
    results = hybrid.search("shipping germany", k=3)
    assert results[0].chunk.doc_id == "ship"
    assert len({r.chunk.chunk_id for r in results}) == len(results)


class _RateLimited(Exception):
    status_code = 429


def test_backoff_retries_on_429_then_succeeds():
    from support_agent.retry import with_backoff

    calls, sleeps = [], []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise _RateLimited()
        return "ok"

    assert with_backoff(flaky, sleep=sleeps.append) == "ok"
    assert sleeps == [1.0, 2.0]


def test_backoff_retries_transient_server_errors():
    from support_agent.retry import with_backoff

    class Overloaded(Exception):
        status_code = 503

    calls = []

    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise Overloaded()
        return "ok"

    assert with_backoff(flaky, sleep=lambda s: None) == "ok" and len(calls) == 2


def test_backoff_fails_fast_when_plan_allows_zero_requests():
    import pytest

    from support_agent.retry import ModelNotAvailableError, with_backoff

    class Blocked(Exception):
        status_code = 429
        headers = {"x-ratelimit-limit-req-minute": "0"}

    def blocked():
        raise Blocked()

    sleeps = []
    with pytest.raises(ModelNotAvailableError):
        with_backoff(blocked, sleep=sleeps.append)
    assert sleeps == []


def test_backoff_does_not_retry_other_errors():
    import pytest

    from support_agent.retry import with_backoff

    def broken():
        raise ValueError("bad request")

    with pytest.raises(ValueError):
        with_backoff(broken, sleep=lambda s: None)
