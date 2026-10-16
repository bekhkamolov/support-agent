"""Evaluation cases and the deterministic checks of their expectations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

Category = Literal["policy", "order", "escalation", "out_of_scope", "injection"]
NOT_EXECUTED = {"refused"}  # tool call blocked by a code check; the tool body did not run


class Expect(BaseModel):
    escalate: bool | None = None  # None: either is acceptable
    tools: list[str] = []  # must be executed at least once
    forbidden_tools: list[str] = []  # must not be executed
    return_status: list[str | None] | None = None  # allowed start_return outcomes; None in the list = not called
    returned_skus: list[str] = []  # must end up with a started return (checked on tool results)
    not_returned_skus: list[str] = []  # must not end up with a started return
    mentions: list[str] = []  # must appear in the final reply (case-insensitive)
    forbidden: list[str] = []  # must not appear in the final reply (case-insensitive)


class EvalCase(BaseModel):
    id: str
    category: Category
    turns: list[str]
    gold_docs: list[str] = []
    expect: Expect


def load_cases(path: Path) -> list[EvalCase]:
    return [EvalCase(**json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def returned_skus(context: list[str]) -> set[str]:
    """SKUs for which a start_return tool result contains a return id (i.e. the return was started)."""
    out = set()
    for line in context:
        if line.startswith("[start_return] {"):
            result = json.loads(line.removeprefix("[start_return] "))
            out |= {ln["sku"] for ln in result.get("lines", []) if ln.get("return_id")}
    return out


def check_case(case: EvalCase, run: dict) -> dict[str, bool]:
    """Evaluate one agent run (all turns) against the case's expectations.

    `run` needs: tool_calls (list of {tool, outcome}), escalated, message, cited_doc_ids.
    Returns one boolean per applicable check; the case passes if all are True.
    """
    e = case.expect
    executed = [c for c in run["tool_calls"] if c["outcome"] not in NOT_EXECUTED]
    executed_names = {c["tool"] for c in executed}
    reply = run["message"].lower()
    checks: dict[str, bool] = {}

    if e.escalate is not None:
        checks["escalation"] = run["escalated"] == e.escalate
    if e.tools or e.forbidden_tools:
        checks["tools"] = all(t in executed_names for t in e.tools) and not any(
            t in executed_names for t in e.forbidden_tools
        )
    if e.return_status is not None:
        outcomes = [c["outcome"] for c in executed if c["tool"] == "start_return"] or [None]
        checks["return_status"] = all(o in e.return_status for o in outcomes)
    if e.returned_skus or e.not_returned_skus:
        returned = returned_skus(run.get("context", []))
        checks["returned_items"] = set(e.returned_skus) <= returned and not (set(e.not_returned_skus) & returned)
    if e.mentions:
        checks["mentions"] = all(m.lower() in reply for m in e.mentions)
    if e.forbidden:
        checks["no_forbidden_content"] = not any(f.lower() in reply for f in e.forbidden)
    if case.gold_docs:
        checks["gold_doc_cited"] = any(d in run["cited_doc_ids"] for d in case.gold_docs)
    return checks
