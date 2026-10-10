"""Chat with the support agent in the terminal.

Demo orders (reference date 2026-10-10): NW-100001 anna@example.com, NW-100002 ben@example.com,
NW-100003 carla@example.com, NW-100004 david@example.com, NW-100005 eva@example.com,
NW-100006 farid@example.com, NW-100007 greta@example.com, NW-100008 hannah@example.com.

Examples:
    python scripts/chat.py
    python scripts/chat.py -m "Where is my order NW-100004? My e-mail is david@example.com"
    python scripts/chat.py -m "I want to return my jeans" -m "NW-100001, anna@example.com"
"""
from __future__ import annotations

import argparse
import os

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from support_agent.agent import SupportAgent, mistral_model
from support_agent.ingest import build_chunks
from support_agent.orders import OrderStore
from support_agent.retrieval import DenseRetriever
from support_agent.retrieval.dense import MistralEmbedder


def show(result) -> None:
    print(f"agent> {result.message}")
    for c in result.tool_calls:
        print(f"        [tool] {c.tool}({c.args}) -> {c.outcome}")
    extras = []
    if result.cited_doc_ids:
        extras.append(f"cited {result.cited_doc_ids}")
    if result.invalid_citations:
        extras.append(f"removed invented citations {result.invalid_citations}")
    if result.guardrail_triggered:
        extras.append("GUARDRAIL escalated")
    if result.best_retrieval_score is not None:
        extras.append(f"best retrieval score {result.best_retrieval_score:.3f}")
    extras.append(
        f"{result.requests} model calls, {result.input_tokens} in ({result.cached_tokens} cached) / "
        f"{result.output_tokens} out tokens, {result.latency_ms:.0f} ms"
    )
    print("        " + " | ".join(extras))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--message", action="append", help="send these messages as consecutive turns, then exit")
    ap.add_argument("--model", default="ministral-14b-latest")
    args = ap.parse_args()

    agent = SupportAgent(mistral_model(args.model), DenseRetriever(build_chunks(), MistralEmbedder()), OrderStore())
    history = None
    messages = args.message or iter(lambda: input("you> "), "")
    for text in messages:
        if args.message:
            print(f"you> {text}")
        if text.strip().lower() in {"exit", "quit"}:
            break
        result, history = agent.ask(text, history)
        show(result)


if __name__ == "__main__":
    main()
