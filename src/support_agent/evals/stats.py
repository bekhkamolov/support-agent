"""Agreement statistics for validating the LLM judge against human labels."""
from __future__ import annotations

from collections.abc import Sequence


def percent_agreement(a: Sequence[bool], b: Sequence[bool]) -> float:
    return sum(x == y for x, y in zip(a, b, strict=True)) / len(a)


def cohen_kappa(a: Sequence[bool], b: Sequence[bool]) -> float | None:
    """Agreement corrected for chance: 1 = perfect, 0 = chance level, < 0 = worse than chance.

    Returns None when undefined (both raters use a single, identical label for every item).
    """
    n = len(a)
    if n == 0 or n != len(b):
        raise ValueError("need two label lists of equal, non-zero length")
    observed = percent_agreement(a, b)
    pa, pb = sum(a) / n, sum(b) / n
    expected = pa * pb + (1 - pa) * (1 - pb)
    if expected == 1:
        return None
    return (observed - expected) / (1 - expected)
