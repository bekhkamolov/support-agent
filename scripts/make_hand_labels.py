"""Pick ~20 agent replies from the latest evaluation for blind human labelling.

Writes:
    data/eval/hand_labels.md          what to read: customer, tool context, reference, reply
    data/eval/hand_labels.csv         what to fill in: correct / grounded (yes or no) and notes
    data/eval/hand_label_items.json   the exact judge inputs, used by scripts/judge_agreement.py

Judge verdicts are deliberately NOT shown, so the human labels are independent of the judge.
The sample is stratified: policy questions (both criteria) and other categories (grounded only),
spread evenly over the evaluated models; fixed random seed for reproducibility.

Example:
    python scripts/make_hand_labels.py
"""
from __future__ import annotations

import argparse
import csv
import json
import random

from support_agent.config import EVAL_DIR, RESULTS_DIR
from support_agent.evals.cases import load_cases
from support_agent.ingest import load_documents

N_POLICY, N_OTHER, SEED = 14, 6, 42


def readable(line: str) -> str:
    """Display form of one tool result (the judge gets the raw text; this is only for reading)."""
    tool, _, payload = line.partition("] ")
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return line
    if tool == "[search_policies" and "excerpts" in data:
        body = "\n\n".join(f"  [{e['doc_id']}] {e['text']}" for e in data["excerpts"]) or f"  {data.get('note')}"
        return f"{tool}]\n{body}"
    return f"{tool}]\n" + json.dumps(data, indent=2, ensure_ascii=False)


def pick(rows: list[dict], n: int, rng: random.Random) -> list[dict]:
    """Round-robin over models so each model contributes about equally."""
    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r)
    for group in by_model.values():
        rng.shuffle(group)
    chosen, models = [], sorted(by_model)
    while len(chosen) < n and any(by_model.values()):
        for m in models:
            if by_model[m] and len(chosen) < n:
                chosen.append(by_model[m].pop())
    return chosen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite an existing label file")
    args = ap.parse_args()

    csv_path = EVAL_DIR / "hand_labels.csv"
    if csv_path.exists() and not args.force:
        raise SystemExit(f"{csv_path} exists (may contain your labels). Use --force to overwrite.")

    results = json.loads((RESULTS_DIR / "agent_eval_latest.json").read_text(encoding="utf-8"))
    cases = {c.id: c for c in load_cases(EVAL_DIR / "agent_cases.jsonl")}
    docs = {d.doc_id: f"{d.title}\n{d.text}" for d in load_documents()}
    candidates = [
        {**r, "model": model}
        for model, rows in results["rows"].items()
        for r in rows
        if not r["failures"]
    ]
    rng = random.Random(SEED)
    sample = pick([r for r in candidates if r["category"] == "policy"], N_POLICY, rng) + pick(
        [r for r in candidates if r["category"] != "policy"], N_OTHER, rng
    )

    items, md = [], ["# Hand labels\n", "Read each item, then fill in `hand_labels.csv` (yes / no).",
                     "Criteria: see the README section \"Judge validation\".\n"]
    for n, r in enumerate(sample, 1):
        case = cases[r["id"]]
        reference = "\n\n".join(docs[d] for d in case.gold_docs) or None
        label_id = f"L{n:02d}"
        items.append({"label_id": label_id, "case_id": r["id"], "model": r["model"], "category": r["category"],
                      "judge_input": {"customer": case.turns, "context": r["context"], "reply": r["message"],
                                      "reference": reference}})
        md.append(f"## {label_id} ({r['id']}, {r['category']})\n")
        md.append("**Customer:**\n" + "\n".join(f"> {t}" for t in case.turns) + "\n")
        md.append("**Context (tool results the assistant saw):**\n```text\n"
                  + ("\n\n".join(map(readable, r["context"])) or "(no tools used)") + "\n```\n")
        if reference:
            md.append("**Reference policy:**\n```text\n" + reference + "\n```\n")
        md.append("**Reply to label:**\n```text\n" + r["message"] + "\n```\n")
        md.append("Label `correct`: " + ("yes / no" if reference else "leave empty (no reference)") +
                  ". Label `grounded`: yes / no.\n")

    (EVAL_DIR / "hand_label_items.json").write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
    (EVAL_DIR / "hand_labels.md").write_text("\n".join(md), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label_id", "case_id", "correct", "grounded", "notes"])
        for it in items:
            w.writerow([it["label_id"], it["case_id"], "", "", ""])
    print(f"Wrote {len(items)} items: {EVAL_DIR / 'hand_labels.md'} and {csv_path}")


if __name__ == "__main__":
    main()
