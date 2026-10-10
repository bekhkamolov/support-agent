"""Evaluate RAG answers on the labelled question set, with and without prompt caching.

Answer correctness needs reference answers and an LLM judge (Day 4). This script measures what can
be checked automatically today: citation accuracy against the gold documents, invented citations,
confidence distribution, tokens (incl. cached tokens) and latency.

Examples:
    python scripts/eval_rag.py
    python scripts/eval_rag.py --cache on --limit 10
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

from support_agent.config import EVAL_DIR, RESULTS_DIR
from support_agent.ingest import build_chunks
from support_agent.llm import MistralChat
from support_agent.rag import PROMPT_VERSION, RagPipeline
from support_agent.retrieval import DenseRetriever
from support_agent.retrieval.dense import MistralEmbedder


def load_questions(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def p95(values: list[float]) -> float:
    return sorted(values)[max(0, round(0.95 * len(values)) - 1)]


def evaluate(pipeline: RagPipeline, questions: list[dict]) -> dict:
    rows = []
    for q in questions:
        try:
            r = pipeline.answer(q["question"])
        except Exception as e:  # keep going, but count failures (e.g. schema violations)
            rows.append({"id": q["id"], "error": f"{type(e).__name__}: {e}"[:300]})
            continue
        cited = r.answer.cited_doc_ids
        rows.append(
            {
                "id": q["id"],
                "style": q.get("style", ""),
                "gold": q["gold"],
                "retrieved": r.retrieved_doc_ids,
                "cited": cited,
                "invalid_citations": r.invalid_citations,
                "confidence": r.answer.confidence,
                "answer": r.answer.answer,
                "gold_retrieved": any(g in r.retrieved_doc_ids for g in q["gold"]),
                "gold_cited": any(g in cited for g in q["gold"]),
                "only_gold_cited": bool(cited) and all(c in q["gold"] for c in cited),
                **r.usage.model_dump(),
                "retrieval_ms": round(r.retrieval_ms, 1),
                "generation_ms": round(r.generation_ms, 1),
            }
        )

    ok = [r for r in rows if "error" not in r]
    n = len(ok)

    def rate(key):
        return round(sum(r[key] for r in ok) / n, 3) if n else None

    def mean(key):
        return round(statistics.mean(r[key] for r in ok), 1) if n else None

    gen = [r["generation_ms"] for r in ok]
    summary = {
        "questions": len(rows),
        "errors": len(rows) - n,
        "gold_retrieved": rate("gold_retrieved"),
        "gold_cited": rate("gold_cited"),
        "only_gold_cited": rate("only_gold_cited"),
        "answers_with_invented_citation": round(sum(bool(r["invalid_citations"]) for r in ok) / n, 3) if n else None,
        "confidence": dict(Counter(r["confidence"] for r in ok)),
        "prompt_tokens_mean": mean("prompt_tokens"),
        "cached_tokens_mean": mean("cached_tokens"),
        "completion_tokens_mean": mean("completion_tokens"),
        "generation_ms_median": round(statistics.median(gen), 1) if gen else None,
        "generation_ms_p95": round(p95(gen), 1) if gen else None,
    }
    return {"summary": summary, "rows": rows}


def to_markdown(results: dict[str, dict]) -> str:
    cols = [
        "gold_retrieved", "gold_cited", "only_gold_cited", "answers_with_invented_citation", "errors",
        "prompt_tokens_mean", "cached_tokens_mean", "completion_tokens_mean",
        "generation_ms_median", "generation_ms_p95",
    ]
    lines = ["| run | " + " | ".join(cols) + " | confidence |", "|" + "---|" * (len(cols) + 2)]
    for name, res in results.items():
        s = res["summary"]
        lines.append(f"| {name} | " + " | ".join(str(s[c]) for c in cols) + f" | {s['confidence']} |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ministral-14b-latest")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--cache", default="both", choices=["on", "off", "both"])
    ap.add_argument("--limit", type=int, default=None, help="only the first N questions")
    args = ap.parse_args()

    questions = load_questions(EVAL_DIR / "retrieval_questions.jsonl")[: args.limit]
    retriever = DenseRetriever(build_chunks(), MistralEmbedder())
    llm = MistralChat(args.model)

    runs = {"on": [True], "off": [False], "both": [False, True]}[args.cache]
    results = {}
    for use_cache in runs:
        label = f"{args.model}, k={args.k}, cache {'on' if use_cache else 'off'}"
        print(f"Running: {label} ...")
        results[label] = evaluate(RagPipeline(retriever, llm, k=args.k, use_cache=use_cache), questions)

    print(f"\n{len(questions)} questions, prompt {PROMPT_VERSION}, dense retrieval (mistral-embed)\n")
    table = to_markdown(results)
    print(table)

    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (RESULTS_DIR / f"rag_{stamp}.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (RESULTS_DIR / "rag_latest.md").write_text(table + "\n", encoding="utf-8")
    print(f"\nSaved results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
