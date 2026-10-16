"""LLM-as-judge for answer correctness and groundedness.

Provider-pluggable: the judge takes any PydanticAI model (Gemini, Mistral, a scripted test model).
Verdicts are cached on disk, keyed by judge model, judge prompt and input.
"""
from __future__ import annotations

import hashlib

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import Model

from ..config import get_env
from ..retry import with_backoff
from .cache import DiskCache, cache_key

JUDGE_INSTRUCTIONS = """You evaluate replies of the customer-support assistant of the online shop Nordwind.

You get:
- CUSTOMER: what the customer wrote.
- CONTEXT: everything the assistant received from its tools (policy excerpts, order data, results of
  actions). This is the ONLY source of facts the assistant was allowed to use.
- REFERENCE (optional): the policy document that answers the customer's question.
- REPLY: the assistant's final reply.

Judge two things.

1. grounded: Is every factual claim in REPLY about the shop supported by CONTEXT?
   Factual claims include policies, prices, fees, deadlines, dates, delivery times, order details,
   and actions the assistant says it took or that will happen (e.g. "you will receive a label by email").
   Not factual claims (need no support): greetings, apologies, questions to the customer, offering
   help, saying it cannot answer, and saying the request is handed to a human colleague.
   First list every unsupported claim in `unsupported_claims`, then set `grounded` to true only if the
   list is empty. Claims that are general knowledge but not about the shop also count as unsupported.

2. correct (only if a REFERENCE is given, otherwise null): Does REPLY answer the customer's question
   in line with REFERENCE?
   - true: the main question is answered and nothing contradicts REFERENCE (missing minor details is fine).
   - false: a stated fact contradicts REFERENCE, the answer is wrong or misleading, or the question is not
     answered (e.g. only handed over or asked back although REFERENCE answers it).

Be strict and literal. Judge only the REPLY, not what the assistant should ideally have said."""

JUDGE_PROMPT_VERSION = hashlib.sha256(JUDGE_INSTRUCTIONS.encode()).hexdigest()[:8]


class JudgeInput(BaseModel):
    customer: list[str]
    context: list[str]
    reply: str
    reference: str | None = None


class JudgeVerdict(BaseModel):
    unsupported_claims: list[str] = Field(description="Claims in REPLY not supported by CONTEXT.")
    grounded: bool
    correct: bool | None = Field(description="null if no REFERENCE was given.")
    explanation: str = Field(description="One or two sentences.")


def render(item: JudgeInput) -> str:
    parts = ["CUSTOMER:\n" + "\n".join(f"- {t}" for t in item.customer)]
    parts.append("CONTEXT:\n" + ("\n".join(item.context) if item.context else "(the assistant used no tools)"))
    if item.reference:
        parts.append("REFERENCE:\n" + item.reference)
    parts.append("REPLY:\n" + item.reply)
    return "\n\n".join(parts)


_judge_agent = Agent(output_type=JudgeVerdict, instructions=JUDGE_INSTRUCTIONS, retries=2)


class Judge:
    def __init__(self, model: Model, name: str, cache: DiskCache | None = None):
        self.model = model
        self.name = name
        self.cache = cache or DiskCache("judge")

    def __call__(self, item: JudgeInput) -> JudgeVerdict:
        key = cache_key({"judge": self.name, "prompt": JUDGE_PROMPT_VERSION, "input": item.model_dump()})
        if (hit := self.cache.get(key)) is not None:
            return JudgeVerdict(**hit)
        run = with_backoff(lambda: _judge_agent.run_sync(render(item), model=self.model))
        verdict = run.output
        if item.reference is None:
            verdict = verdict.model_copy(update={"correct": None})
        self.cache.put(key, verdict.model_dump())
        return verdict


def gemini_judge(model: str = "gemini-3.8-flash") -> Judge:
    """Pinned model version (not "-latest"), so verdicts do not change silently."""
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider

    provider = GoogleProvider(api_key=get_env("GEMINI_API_KEY"))
    return Judge(GoogleModel(model, provider=provider, settings={"temperature": 0.0}), name=f"google:{model}")


def mistral_judge(model: str = "ministral-14b-latest") -> Judge:
    from ..agent import mistral_model

    return Judge(mistral_model(model), name=f"mistral:{model}")
