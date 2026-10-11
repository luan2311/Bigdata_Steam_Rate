"""KPI formulas shared by gold tables, checks and the dashboard (Plan.md 5.1)."""

from __future__ import annotations

import math
from collections.abc import Iterable

MIN_REVIEWS_FOR_RANKING = 100

MINUTES_PER_HOUR = 60
# Half-open hour ranges [lower, upper); the last one is unbounded.
PLAYTIME_BUCKETS: tuple[tuple[str, float, float], ...] = (
    ("[0,2)", 0, 2),
    ("[2,10)", 2, 10),
    ("[10,50)", 10, 50),
    ("[50,100)", 50, 100),
    ("[100,inf)", 100, math.inf),
)
PLAYTIME_MISSING = "missing"
PLAYTIME_NEGATIVE = "negative"


def recommendation_rate(recommended_count: int, valid_label_count: int) -> float | None:
    """Return the rate, or None (shown as N/A) when the denominator is zero."""
    if valid_label_count < 0 or recommended_count < 0 or recommended_count > valid_label_count:
        raise ValueError("counts must satisfy 0 <= recommended <= total")
    if valid_label_count == 0:
        return None
    return recommended_count / valid_label_count


def combined_rate(groups: Iterable[tuple[int, int]]) -> float | None:
    """Sum numerators and denominators first; never average per-group rates."""
    recommended = total = 0
    for group_recommended, group_total in groups:
        recommended += group_recommended
        total += group_total
    return recommendation_rate(recommended, total)


def playtime_bucket(minutes: float | None) -> str:
    if minutes is None or math.isnan(minutes):
        return PLAYTIME_MISSING
    if minutes < 0:
        return PLAYTIME_NEGATIVE
    hours = minutes / MINUTES_PER_HOUR
    for label, lower, upper in PLAYTIME_BUCKETS:
        if lower <= hours < upper:
            return label
    raise AssertionError("unreachable: buckets cover [0, inf)")
