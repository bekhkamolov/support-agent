"""Run evaluation cases against the agent, with every run cached on disk."""
from __future__ import annotations

import hashlib

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage

from ..agent import INSTRUCTIONS, MAX_REQUESTS_PER_TURN, MIN_RETRIEVAL_SCORE, SupportAgent
from .cache import DiskCache, cache_key
from .cases import EvalCase

# Bump when tools, checks or guardrails change in a way the instructions hash does not capture.
AGENT_VERSION = "agent-v1"
AGENT_FINGERPRINT = hashlib.sha256(
    f"{AGENT_VERSION}|{INSTRUCTIONS}|{MIN_RETRIEVAL_SCORE}|{MAX_REQUESTS_PER_TURN}".encode()
).hexdigest()[:8]


def tool_context(history: list[ModelMessage]) -> list[str]:
    """Everything the agent received from its tools, as text for the judge."""
    out = []
    for message in history:
        for part in message.parts:
            if part.part_kind == "tool-return" and part.tool_name in {
                "search_policies", "get_order_status", "start_return", "escalate_to_human"
            }:
                content = part.content.model_dump_json() if isinstance(part.content, BaseModel) else str(part.content)
                out.append(f"[{part.tool_name}] {content}")
    return out


def run_case(agent: SupportAgent, case: EvalCase) -> dict:
    """Play all turns of a case. Tool calls, tokens and latency are summed over turns;
    the reply, citations and judge input come from the final turn."""
    history, tool_calls = None, []
    totals = {"input_tokens": 0, "output_tokens": 0, "cached_tokens": 0, "requests": 0, "latency_ms": 0.0}
    escalated, guardrail, failures = False, False, []
    for turn in case.turns:
        result, history = agent.ask(turn, history)
        tool_calls += [c.model_dump() for c in result.tool_calls]
        for k in totals:
            totals[k] += getattr(result, k)
        escalated |= result.escalated
        guardrail |= result.guardrail_triggered
        if result.failure:
            failures.append(result.failure)
    return {
        "message": result.message,
        "cited_doc_ids": result.cited_doc_ids,
        "invalid_citations": result.invalid_citations,
        "tool_calls": tool_calls,
        "escalated": escalated,
        "guardrail_triggered": guardrail,
        "failures": failures,
        "context": tool_context(history or []),
        **totals,
    }


def run_key(model_name: str, case: EvalCase) -> str:
    """Only what the agent sees: expectations can be corrected without re-running the agent."""
    return cache_key({"model": model_name, "agent": AGENT_FINGERPRINT, "id": case.id, "turns": case.turns})


def run_case_cached(agent: SupportAgent, model_name: str, case: EvalCase, cache: DiskCache | None = None) -> dict:
    cache = cache or DiskCache("agent_runs")
    key = run_key(model_name, case)
    if (hit := cache.get(key)) is not None:
        return {**hit, "from_cache": True}
    record = run_case(agent, case)
    cache.put(key, record)
    return {**record, "from_cache": False}
