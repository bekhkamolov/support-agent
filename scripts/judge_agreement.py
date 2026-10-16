"""Compare LLM judges with the human labels: agreement, Cohen's kappa and self-preference.

Runs the Gemini judge and a Mistral judge (ministral-14b, the same model family as the agent) on
the hand-labelled items. Verdicts are cached, so this only calls the APIs once.

Example:
    python scripts/judge_agreement.py
"""
from __future__ import annotations

import argparse
import csv
import json
import os

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from pathlib import Path  # noqa: E402

from support_agent.config import EVAL_DIR, RESULTS_DIR  # noqa: E402
from support_agent.evals.judge import JudgeInput, gemini_judge, mistral_judge  # noqa: E402
from support_agent.evals.stats import cohen_kappa, percent_agreement  # noqa: E402

YES, NO = {"yes", "y", "true", "1"}, {"no", "n", "false", "0"}


def parse(value: str) -> bool | None:
    v = value.strip().lower()
    return True if v in YES else False if v in NO else None


def fmt(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.2f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="hand_labels.csv", help="label file in data/eval/")
    args = ap.parse_args()

    items = {it["label_id"]: it for it in json.loads((EVAL_DIR / "hand_label_items.json").read_text(encoding="utf-8"))}
    with (EVAL_DIR / args.labels).open(encoding="utf-8") as f:
        labels = {row["label_id"]: row for row in csv.DictReader(f)}
    missing = [lid for lid, row in labels.items() if parse(row["grounded"]) is None]
    if missing:
        raise SystemExit(f"Fill in 'grounded' (yes/no) for: {', '.join(missing)}")

    judges = [gemini_judge(), mistral_judge()]
    verdicts = {j.name: {} for j in judges}
    unavailable: dict[str, str] = {}
    for j in judges:
        for lid, it in items.items():
            try:
                verdicts[j.name][lid] = j(JudgeInput(**it["judge_input"]))
            except Exception as e:  # e.g. provider overloaded or daily quota used up: report what we have
                unavailable[j.name] = f"{type(e).__name__}: {str(e)[:150]}"
                break

    lines = [f"Hand-labelled items: {len(items)} (labels: {args.labels})\n"]
    for name, why in unavailable.items():
        lines.append(f"**{name} incomplete** ({len(verdicts[name])} of {len(items)} items judged; stopped on {why}). "
                     "Rerun later: finished verdicts are cached.\n")
    lines += [
             "| judge | criterion | n | agreement | Cohen's kappa | judge says yes | human says yes |",
             "|---|---|---|---|---|---|---|"]
    def pairs(judge_name: str, criterion: str, sel=None) -> list[tuple[bool, bool]]:
        """(human, judge) label pairs where both exist."""
        out = []
        for lid, v in verdicts[judge_name].items():
            h, jv = parse(labels[lid][criterion]), getattr(v, criterion)
            if h is not None and jv is not None and (sel is None or lid in sel):
                out.append((h, jv))
        return out

    for criterion in ["correct", "grounded"]:
        for j in judges:
            p = pairs(j.name, criterion)
            if not p:
                lines.append(f"| {j.name} | {criterion} | 0 | n/a | n/a | n/a | n/a |")
                continue
            human, judged = [h for h, _ in p], [jv for _, jv in p]
            lines.append(f"| {j.name} | {criterion} | {len(p)} | {fmt(percent_agreement(human, judged))} | "
                         f"{fmt(cohen_kappa(human, judged))} | {sum(judged)} | {sum(human)} |")

    # Self-preference: is the Mistral judge more lenient (says yes where the human says no) on
    # answers written by its own model (ministral-14b) than on answers by the smaller models?
    lines += ["\nLenient verdicts (judge yes, human no), by the model that wrote the answer:\n",
              "| judge | answers by ministral-14b | answers by other models |", "|---|---|---|"]
    for j in judges:
        cells = []
        for own in (True, False):
            sel = {lid for lid in items if ("14b" in items[lid]["model"]) == own}
            p = pairs(j.name, "correct", sel) + pairs(j.name, "grounded", sel)
            cells.append(f"{sum(jv and not h for h, jv in p)} of {len(p)}")
        lines.append(f"| {j.name} | {cells[0]} | {cells[1]} |")

    lines.append("\nDisagreements with the human label:\n")
    for lid, it in items.items():
        for j in judges:
            v = verdicts[j.name].get(lid)
            if v is None:
                continue
            for c in ("correct", "grounded"):
                h, jv = parse(labels[lid][c]), getattr(v, c)
                if h is not None and jv is not None and h != jv:
                    lines.append(f"- {lid} ({it['case_id']}, {it['model']}) {j.name} {c}: judge={jv}, "
                                 f"human={h}. Judge: {v.explanation}")

    report = "\n".join(lines)
    print(report)
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / f"judge_agreement_{Path(args.labels).stem}.md").write_text(report + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
