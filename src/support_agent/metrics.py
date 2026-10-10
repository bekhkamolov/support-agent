"""Retrieval metrics computed at document level."""
from __future__ import annotations

from collections.abc import Sequence


def dedupe_docs(doc_ids: Sequence[str]) -> list[str]:
    """Keep the first occurrence of each document, preserving rank order."""
    seen, out = set(), []
    for d in doc_ids:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def recall_at_k(ranked_doc_ids: Sequence[str], gold: Sequence[str], k: int) -> float:
    """1.0 if any gold document is among the top-k distinct documents, else 0.0."""
    top = dedupe_docs(ranked_doc_ids)[:k]
    return 1.0 if any(g in top for g in gold) else 0.0


def reciprocal_rank(ranked_doc_ids: Sequence[str], gold: Sequence[str]) -> float:
    for rank, d in enumerate(dedupe_docs(ranked_doc_ids), start=1):
        if d in gold:
            return 1.0 / rank
    return 0.0
