"""Chat models that return Pydantic-validated structured output."""
from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

from .config import get_env
from .retry import with_backoff

T = TypeVar("T", bound=BaseModel)


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0  # prompt tokens served from the provider's prompt cache


class ChatModel(Protocol):
    name: str

    def parse(self, system: str, user: str, schema: type[T], cache_key: str | None = None) -> tuple[T, Usage]: ...


def usage_from_response(usage) -> Usage:
    """Read token counts from a Mistral usage object.

    `prompt_tokens_details` is not a declared field in every SDK version, so it may arrive as an
    attribute, as an extra field, or not at all.
    """
    if usage is None:
        return Usage()
    details = getattr(usage, "prompt_tokens_details", None) or (getattr(usage, "model_extra", None) or {}).get(
        "prompt_tokens_details"
    )
    if isinstance(details, dict):
        cached = details.get("cached_tokens") or 0
    else:
        cached = getattr(details, "cached_tokens", 0) or 0
    return Usage(
        prompt_tokens=usage.prompt_tokens or 0,
        completion_tokens=usage.completion_tokens or 0,
        cached_tokens=cached,
    )


class MistralChat:
    """Mistral chat completions with strict JSON-schema output."""

    def __init__(self, model: str = "ministral-14b-latest", temperature: float = 0.0):
        try:  # mistralai >= 2.x moved the client into mistralai.client
            from mistralai.client import Mistral
        except ImportError:  # mistralai 1.x
            from mistralai import Mistral

        self.client = Mistral(api_key=get_env("MISTRAL_API_KEY"))
        self.model = model
        self.name = f"mistral:{model}"
        self.temperature = temperature

    def parse(self, system: str, user: str, schema: type[T], cache_key: str | None = None) -> tuple[T, Usage]:
        kwargs = {"prompt_cache_key": cache_key} if cache_key else {}
        resp = with_backoff(
            lambda: self.client.chat.parse(
                schema,
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=self.temperature,
                **kwargs,
            )
        )
        message = resp.choices[0].message
        parsed = message.parsed if message.parsed is not None else schema.model_validate_json(message.content)
        return parsed, usage_from_response(resp.usage)
