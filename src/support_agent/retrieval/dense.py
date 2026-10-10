"""Dense retrieval with pluggable embedding backends and an on-disk cache."""
from __future__ import annotations

import hashlib
import json
from typing import Protocol

import numpy as np

from ..config import CACHE_DIR, get_env
from ..ingest import Chunk
from .base import SearchResult


class Embedder(Protocol):
    name: str

    def embed(self, texts: list[str]) -> np.ndarray: ...


class MistralEmbedder:
    """Embeddings via the Mistral API (model: mistral-embed)."""

    def __init__(self, model: str = "mistral-embed", batch_size: int = 32):
        from mistralai import Mistral  # optional dependency

        self.client = Mistral(api_key=get_env("MISTRAL_API_KEY"))
        self.model = model
        self.name = f"mistral:{model}"
        self.batch_size = batch_size

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for i in range(0, len(texts), self.batch_size):
            resp = self.client.embeddings.create(model=self.model, inputs=texts[i : i + self.batch_size])
            vectors.extend(d.embedding for d in resp.data)
        return np.asarray(vectors, dtype=np.float32)


class LocalEmbedder:
    """Local embeddings with sentence-transformers (no API key needed)."""

    def __init__(self, model: str = "BAAI/bge-small-en-v1.5"):
        from sentence_transformers import SentenceTransformer  # optional dependency

        self.model = SentenceTransformer(model)
        self.name = f"local:{model}"

    def embed(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, normalize_embeddings=True), dtype=np.float32)


def _normalize(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.clip(norms, 1e-12, None)


class DenseRetriever:
    name = "dense"

    def __init__(self, chunks: list[Chunk], embedder: Embedder, use_cache: bool = True):
        self.chunks = chunks
        self.embedder = embedder
        self.matrix = _normalize(self._embed_chunks(use_cache))

    def _embed_chunks(self, use_cache: bool) -> np.ndarray:
        texts = [c.text for c in self.chunks]
        key = hashlib.sha256(json.dumps([self.embedder.name, texts]).encode()).hexdigest()[:16]
        path = CACHE_DIR / f"emb_{key}.npy"
        if use_cache and path.exists():
            return np.load(path)
        matrix = self.embedder.embed(texts)
        if use_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            np.save(path, matrix)
        return matrix

    def search(self, query: str, k: int = 5) -> list[SearchResult]:
        q = _normalize(self.embedder.embed([query]))[0]
        scores = self.matrix @ q
        order = np.argsort(-scores)[:k]
        return [SearchResult(chunk=self.chunks[i], score=float(scores[i])) for i in order]
