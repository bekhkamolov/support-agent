from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel

from ..ingest import Chunk


class SearchResult(BaseModel):
    chunk: Chunk
    score: float


class Retriever(Protocol):
    name: str

    def search(self, query: str, k: int = 5) -> list[SearchResult]: ...
