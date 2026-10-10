"""Ask the RAG pipeline a single question.

Example:
    python scripts/ask.py "Can I return earrings?"
"""
from __future__ import annotations

import argparse

from support_agent.ingest import build_chunks
from support_agent.llm import MistralChat
from support_agent.rag import RagPipeline
from support_agent.retrieval import DenseRetriever
from support_agent.retrieval.dense import MistralEmbedder


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--model", default="ministral-14b-latest")
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    pipeline = RagPipeline(DenseRetriever(build_chunks(), MistralEmbedder()), MistralChat(args.model), k=args.k)
    r = pipeline.answer(args.question)
    print(r.answer.answer)
    print(f"\ncited: {r.answer.cited_doc_ids}  confidence: {r.answer.confidence}")
    if r.invalid_citations:
        print(f"removed invented citations: {r.invalid_citations}")
    print(
        f"retrieved: {r.retrieved_doc_ids}\n"
        f"tokens: {r.usage.prompt_tokens} in ({r.usage.cached_tokens} cached), {r.usage.completion_tokens} out | "
        f"retrieval {r.retrieval_ms:.0f} ms, generation {r.generation_ms:.0f} ms"
    )


if __name__ == "__main__":
    main()
