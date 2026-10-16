"""Evaluate the agent with several models on the case set, plus an LLM judge.

The default judge is ministral-14b: Gemini's free tier allows only 20 requests per day, so Gemini
judges only the hand-labelled subset (scripts/judge_agreement.py), where both judges are validated.

Every agent run and every judge verdict is cached in .cache/eval/, so reruns are free and an
interrupted run (e.g. judge quota exhausted) continues where it stopped.

Examples:
    python scripts/eval_agent.py
    python scripts/eval_agent.py --models ministral-3b-latest --limit 5 --judge none
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from collections import defaultdict
from datetime import datetime

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError  # noqa: E402

from support_agent.agent import SupportAgent, mistral_model  # noqa: E402
from support_agent.config import EVAL_DIR, RESULTS_DIR  # noqa: E402
from support_agent.evals.cases import check_case, load_cases  # noqa: E402
from support_agent.evals.judge import JudgeInput, gemini_judge, mistral_judge  # noqa: E402
from support_agent.evals.runner import AGENT_FINGERPRINT, run_case_cached  # noqa: E402
from support_agent.ingest import build_chunks, load_documents  # noqa: E402
from support_agent.orders import OrderStore  # noqa: E402
from support_agent.retrieval import DenseRetriever  # noqa: E402
from support_agent.retrieval.dense import MistralEmbedder  # noqa: E402

DEFAULT_MODELS = "ministral-3b-latest,ministral-8b-latest,ministral-14b-latest"

# USD per 1M tokens: (input, cached input, output). Source: docs.mistral.ai/inference/pricing,
# retrieved 2026-10-11. List prices; the free API plan used here costs nothing.
# Query embeddings (mistral-embed) are not included: no price is listed for them.
PRICES = {
    "ministral-3b-latest": (0.10, 0.01, 0.10),
    "ministral-8b-latest": (0.15, 0.015, 0.15),
    "ministral-14b-latest": (0.20, 0.02, 0.20),
}


def cost_usd(model: str, r: dict) -> float | None:
    if model not in PRICES:
        return None
    p_in, p_cached, p_out = PRICES[model]
    uncached = r["input_tokens"] - r["cached_tokens"]
    return (uncached * p_in + r["cached_tokens"] * p_cached + r["output_tokens"] * p_out) / 1e6


def run_with_retries(llm, retriever, model: str, case, attempts: int = 3) -> dict:
    """Run a case; on a transient API error (timeout, 5xx) start the case again from scratch.

    Every attempt gets a fresh agent and order database, so a half-finished attempt leaves no
    side effects. Only successful runs are cached.
    """
    for attempt in range(1, attempts + 1):
        try:
            return run_case_cached(SupportAgent(llm, retriever, OrderStore()), model, case)
        except (ModelAPIError, ModelHTTPError) as e:
            if attempt == attempts:
                raise
            print(f"  {case.id}: {type(e).__name__} ({str(e)[:80]}), retrying ({attempt}/{attempts - 1})")
            time.sleep(10 * attempt)


def rate(values: list[bool]) -> float | None:
    return round(sum(values) / len(values), 3) if values else None


def p95(values: list[float]) -> float:
    return sorted(values)[max(0, round(0.95 * len(values)) - 1)]


def summarise(model: str, rows: list[dict]) -> dict:
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r["passed"])

    esc = [r for r in rows if r["expected_escalate"] is not None]
    tp = sum(r["escalated"] and r["expected_escalate"] for r in esc)
    predicted, actual = sum(r["escalated"] for r in esc), sum(r["expected_escalate"] for r in esc)
    judged = [r["judge"] for r in rows if r.get("judge")]
    costs = [c for r in rows if (c := cost_usd(model, r)) is not None]
    return {
        "cases": len(rows),
        "pass_rate": rate([r["passed"] for r in rows]),
        **{f"pass_{cat}": rate(v) for cat, v in sorted(by_cat.items())},
        "tool_check": rate([r["checks"]["tools"] for r in rows if "tools" in r["checks"]]),
        "return_status_check": rate([r["checks"]["return_status"] for r in rows if "return_status" in r["checks"]]),
        "escalation_precision": round(tp / predicted, 3) if predicted else None,
        "escalation_recall": round(tp / actual, 3) if actual else None,
        "gold_doc_cited": rate([r["checks"]["gold_doc_cited"] for r in rows if "gold_doc_cited" in r["checks"]]),
        "judge_correct": rate([j["correct"] for j in judged if j["correct"] is not None]),
        "judge_grounded": rate([j["grounded"] for j in judged]),
        "judged": len(judged),
        "aborted_runs": sum(bool(r["failures"]) for r in rows),
        "requests_mean": round(statistics.mean(r["requests"] for r in rows), 2),
        "input_tokens_mean": round(statistics.mean(r["input_tokens"] for r in rows)),
        "output_tokens_mean": round(statistics.mean(r["output_tokens"] for r in rows)),
        "cached_share": round(sum(r["cached_tokens"] for r in rows) / max(1, sum(r["input_tokens"] for r in rows)), 3),
        "latency_ms_median": round(statistics.median(r["latency_ms"] for r in rows)),
        "latency_ms_p95": round(p95([r["latency_ms"] for r in rows])),
        "cost_usd_per_case": round(statistics.mean(costs), 6) if costs else None,
    }


COLUMNS = [
    ("pass_rate", "pass (all)"), ("pass_policy", "policy"), ("pass_order", "order"),
    ("pass_escalation", "escalation"), ("pass_out_of_scope", "out of scope"), ("pass_injection", "injection"),
    ("tool_check", "tool check"), ("escalation_precision", "esc. precision"), ("escalation_recall", "esc. recall"),
    ("judge_correct", "correct (judge)"), ("judge_grounded", "grounded (judge)"), ("aborted_runs", "aborted"),
    ("requests_mean", "model calls"), ("latency_ms_median", "latency ms (median)"),
    ("latency_ms_p95", "latency ms (p95)"), ("cost_usd_per_case", "USD / case"),
]


def to_markdown(summaries: dict[str, dict]) -> str:
    lines = ["| model | " + " | ".join(label for _, label in COLUMNS) + " |", "|" + "---|" * (len(COLUMNS) + 1)]
    for model, s in summaries.items():
        lines.append(f"| {model} | " + " | ".join(str(s.get(k)) for k, _ in COLUMNS) + " |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=DEFAULT_MODELS)
    ap.add_argument("--judge", default="mistral", choices=["mistral", "gemini", "none"])
    ap.add_argument("--limit", type=int, default=None, help="only the first N cases")
    args = ap.parse_args()

    cases = load_cases(EVAL_DIR / "agent_cases.jsonl")[: args.limit]
    docs = {d.doc_id: f"{d.title}\n{d.text}" for d in load_documents()}
    retriever = DenseRetriever(build_chunks(), MistralEmbedder())
    judge = {"mistral": mistral_judge, "gemini": gemini_judge}.get(args.judge, lambda: None)()
    judge_stopped = None

    all_rows: dict[str, list[dict]] = {}
    for model in args.models.split(","):
        llm = mistral_model(model)
        rows = []
        for i, case in enumerate(cases, 1):
            record = run_with_retries(llm, retriever, model, case)
            checks = check_case(case, record)
            row = {"id": case.id, "category": case.category, "expected_escalate": case.expect.escalate,
                   **record, "checks": checks, "passed": all(checks.values())}
            if judge and not judge_stopped and not record["failures"]:
                reference = "\n\n".join(docs[d] for d in case.gold_docs) or None
                try:
                    row["judge"] = judge(JudgeInput(customer=case.turns, context=record["context"],
                                                    reply=record["message"], reference=reference)).model_dump()
                except Exception as e:  # e.g. daily quota exhausted: keep going without the judge
                    judge_stopped = f"{type(e).__name__}: {str(e)[:800]}"
                    print(f"  judge stopped: {judge_stopped}")
            rows.append(row)
            status = "PASS" if row["passed"] else "FAIL " + ",".join(k for k, v in checks.items() if not v)
            print(f"[{model}] {i:2}/{len(cases)} {case.id} {status}{' (cached)' if record['from_cache'] else ''}")
        all_rows[model] = rows

    summaries = {m: summarise(m, rows) for m, rows in all_rows.items()}
    table = to_markdown(summaries)
    print(f"\n{len(cases)} cases, agent {AGENT_FINGERPRINT}, judge {judge.name if judge else 'none'}\n")
    print(table)
    if judge_stopped:
        print(f"\nJudge stopped early ({judge_stopped}). Rerun later: finished verdicts are cached.")

    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = {"agent": AGENT_FINGERPRINT, "judge": judge.name if judge else None, "judge_stopped": judge_stopped,
           "summaries": summaries, "rows": all_rows}
    (RESULTS_DIR / f"agent_eval_{stamp}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    (RESULTS_DIR / "agent_eval_latest.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    (RESULTS_DIR / "agent_eval_latest.md").write_text(table + "\n", encoding="utf-8")
    print(f"\nSaved results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
