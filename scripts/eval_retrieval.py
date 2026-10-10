"""Evaluate retrievers on the labelled question set.

Examples:
    python scripts/eval_retrieval.py --retrievers bm25
    python scripts/eval_retrieval.py --retrievers bm25,dense,hybrid --embedder mistral
    python scripts/eval_retrieval.py --retrievers bm25,dense,hybrid --embedder local
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime
from pathlib import Path

from support_agent.config import EVAL_DIR, RESULTS_DIR
from support_agent.ingest import build_chunks
from support_agent.metrics import reciprocal_rank, recall_at_k
from support_agent.retrieval import BM25Retriever, DenseRetriever, HybridRetriever


def load_questions(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_embedder(kind: str):
    if kind == "mistral":
        from support_agent.retrieval.dense import MistralEmbedder
        return MistralEmbedder()
    if kind == "local":
        from support_agent.retrieval.dense import LocalEmbedder
        return LocalEmbedder()
    raise ValueError(f"Unknown embedder: {kind}")


def evaluate(retriever, questions: list[dict], ks=(1, 3, 5)) -> dict:
    rows, latencies = [], []
    for q in questions:
        t0 = time.perf_counter()
        results = retriever.search(q["question"], k=20)
        latencies.append((time.perf_counter() - t0) * 1000)
        ranked = [r.chunk.doc_id for r in results]
        row = {"id": q["id"], "style": q.get("style", ""), "top_docs": ranked[:5]}
        row.update({f"recall@{k}": recall_at_k(ranked, q["gold"], k) for k in ks})
        row["rr"] = reciprocal_rank(ranked, q["gold"])
        rows.append(row)

    def mean(key, subset=None):
        sel = [r[key] for r in rows if subset is None or r["style"] == subset]
        return round(statistics.mean(sel), 3) if sel else None

    summary = {f"recall@{k}": mean(f"recall@{k}") for k in ks}
    summary["mrr"] = mean("rr")
    summary["recall@5_lexical"] = mean("recall@5", "lexical")
    summary["recall@5_paraphrase"] = mean("recall@5", "paraphrase")
    summary["latency_ms_median"] = round(statistics.median(latencies), 1)
    return {"summary": summary, "rows": rows}


def to_markdown(results: dict[str, dict]) -> str:
    cols = ["recall@1", "recall@3", "recall@5", "mrr", "recall@5_lexical", "recall@5_paraphrase", "latency_ms_median"]
    lines = ["| retriever | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for name, res in results.items():
        lines.append(f"| {name} | " + " | ".join(str(res["summary"][c]) for c in cols) + " |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--retrievers", default="bm25")
    ap.add_argument("--embedder", default="mistral", choices=["mistral", "local"])
    ap.add_argument("--chunk-words", type=int, default=80)
    ap.add_argument("--overlap", type=int, default=20)
    args = ap.parse_args()

    questions = load_questions(EVAL_DIR / "retrieval_questions.jsonl")
    chunks = build_chunks(args.chunk_words, args.overlap)
    wanted = args.retrievers.split(",")

    bm25 = BM25Retriever(chunks)
    dense = None
    if {"dense", "hybrid"} & set(wanted):
        dense = DenseRetriever(chunks, make_embedder(args.embedder))
    available = {"bm25": bm25, "dense": dense, "hybrid": HybridRetriever([bm25, dense]) if dense else None}

    results = {}
    for name in wanted:
        label = name if name == "bm25" else f"{name} ({args.embedder})"
        results[label] = evaluate(available[name], questions)

    print(f"{len(questions)} questions, {len(chunks)} chunks\n")
    table = to_markdown(results)
    print(table)

    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (RESULTS_DIR / f"retrieval_{stamp}.json").write_text(json.dumps(results, indent=2))
    (RESULTS_DIR / "retrieval_latest.md").write_text(table + "\n")
    print(f"\nSaved results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
