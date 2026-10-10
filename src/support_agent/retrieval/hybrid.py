"""Hybrid retrieval: combine rankings with Reciprocal Rank Fusion (RRF)."""
from __future__ import annotations

from .base import Retriever, SearchResult


class HybridRetriever:
    name = "hybrid"

    def __init__(self, retrievers: list[Retriever], rrf_k: int = 60, candidates: int = 20):
        self.retrievers = retrievers
        self.rrf_k = rrf_k
        self.candidates = candidates

    def search(self, query: str, k: int = 5) -> list[SearchResult]:
        fused: dict[str, float] = {}
        by_id: dict[str, SearchResult] = {}
        for r in self.retrievers:
            for rank, res in enumerate(r.search(query, k=self.candidates), start=1):
                cid = res.chunk.chunk_id
                fused[cid] = fused.get(cid, 0.0) + 1.0 / (self.rrf_k + rank)
                by_id.setdefault(cid, res)
        top = sorted(fused, key=fused.get, reverse=True)[:k]
        return [SearchResult(chunk=by_id[c].chunk, score=fused[c]) for c in top]
