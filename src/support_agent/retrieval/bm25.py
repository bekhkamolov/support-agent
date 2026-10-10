"""Lexical retrieval with BM25."""
from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from ..ingest import Chunk
from .base import SearchResult

_STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "is", "are", "be", "it",
    "i", "my", "me", "you", "your", "we", "do", "does", "can", "with", "if", "what", "how",
    "when", "this", "that", "at", "by", "from", "after", "have", "has", "will", "not",
}
_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOPWORDS]


class BM25Retriever:
    name = "bm25"

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self._bm25 = BM25Okapi([tokenize(c.text) for c in chunks])

    def search(self, query: str, k: int = 5) -> list[SearchResult]:
        scores = self._bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [SearchResult(chunk=self.chunks[i], score=float(scores[i])) for i in order]
