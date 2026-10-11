"""Recommendation label rules (Plan.md section 3.3).

`recommended` is a binary recommend / not-recommend choice, not a three-class
sentiment label. Missing or unknown values are rejected, never mapped to False.
"""

from __future__ import annotations

POSITIVE_LABEL = 1  # recommended
NEGATIVE_LABEL = 0  # not recommended

# Only the raw values observed in the source CSV are accepted.
LABEL_MAPPING: dict[str, bool] = {"true": True, "false": False}


def parse_recommended(raw: str | None) -> bool | None:
    """Return the label, or None when the raw value is missing or not published."""
    if raw is None:
        return None
    return LABEL_MAPPING.get(raw.strip().lower())
