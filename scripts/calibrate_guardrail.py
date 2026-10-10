"""Choose the retrieval-score threshold below which the agent escalates instead of answering.

Compares the top-1 dense retrieval score of in-scope questions (answered by a policy) with
out-of-scope questions (no policy covers them) and reports how well a threshold separates them.

Example:
    python scripts/calibrate_guardrail.py
"""
from __future__ import annotations

import json
from pathlib import Path

from support_agent.config import EVAL_DIR, RESULTS_DIR
from support_agent.ingest import build_chunks
from support_agent.retrieval import DenseRetriever
from support_agent.retrieval.dense import MistralEmbedder


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    retriever = DenseRetriever(build_chunks(), MistralEmbedder())
    inside = load(EVAL_DIR / "retrieval_questions.jsonl")
    outside = load(EVAL_DIR / "out_of_scope_questions.jsonl")

    rows = []
    for q, in_scope in [(q, True) for q in inside] + [(q, False) for q in outside]:
        top = retriever.search(q["question"], k=1)[0]
        rows.append({"id": q["id"], "in_scope": in_scope, "style": q.get("style", ""),
                     "score": round(top.score, 4), "top_doc": top.chunk.doc_id, "question": q["question"]})

    # Candidate thresholds: midpoints between neighbouring scores. Pick the one with the best
    # balanced accuracy (mean of in-scope kept and out-of-scope escalated).
    scores = sorted({r["score"] for r in rows})
    candidates = [(a + b) / 2 for a, b in zip(scores, scores[1:])]

    def evaluate(t):
        kept = sum(r["score"] >= t for r in rows if r["in_scope"]) / len(inside)
        caught = sum(r["score"] < t for r in rows if not r["in_scope"]) / len(outside)
        return (kept + caught) / 2, kept, caught

    best = max(candidates, key=lambda t: (evaluate(t)[0], -t))
    bal, kept, caught = evaluate(best)

    for group, sel in [("in-scope", [r for r in rows if r["in_scope"]]),
                       ("out-of-scope near", [r for r in rows if r["style"] == "near"]),
                       ("out-of-scope far", [r for r in rows if r["style"] == "far"])]:
        s = sorted(r["score"] for r in sel)
        print(f"{group:18} n={len(s):2}  min {s[0]:.3f}  median {s[len(s) // 2]:.3f}  max {s[-1]:.3f}")
    print(f"\nbest threshold {best:.3f}: in-scope kept {kept:.3f}, out-of-scope escalated {caught:.3f}, "
          f"balanced accuracy {bal:.3f}")
    print("\nMisclassified at this threshold:")
    for r in sorted(rows, key=lambda r: r["score"]):
        if (r["score"] >= best) != r["in_scope"]:
            print(f"  {r['id']} score {r['score']:.3f} top {r['top_doc']:22} {r['question']}")

    RESULTS_DIR.mkdir(exist_ok=True)
    out = {"threshold": round(best, 3), "in_scope_kept": round(kept, 3),
           "out_of_scope_escalated": round(caught, 3), "rows": rows}
    (RESULTS_DIR / "guardrail_calibration.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
