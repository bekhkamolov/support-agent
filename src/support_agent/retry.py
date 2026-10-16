"""Retry API calls that hit a rate limit."""
from __future__ import annotations

import time


class ModelNotAvailableError(RuntimeError):
    """The API plan allows 0 requests for this model, so retrying cannot help."""


RETRYABLE_STATUS = {429, 500, 502, 503, 504}  # rate limit and transient server errors (e.g. "high demand")


def with_backoff(call, max_retries: int = 6, base_delay: float = 1.0, sleep=time.sleep):
    """Retry `call` on HTTP 429 and 5xx with exponential backoff: 1s, 2s, 4s, ...

    Only for calls without side effects (embeddings, judge): a retried call runs again in full.
    """
    for attempt in range(max_retries + 1):
        try:
            return call()
        except Exception as e:
            if getattr(e, "status_code", None) not in RETRYABLE_STATUS or attempt == max_retries:
                raise
            if (getattr(e, "headers", None) or {}).get("x-ratelimit-limit-req-minute") == "0":
                raise ModelNotAvailableError(
                    "The API key has a limit of 0 requests/minute for this model; choose another model."
                ) from e
            sleep(base_delay * 2**attempt)
