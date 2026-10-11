"""Record-level quality rules and quarantine reasons.

A record is quarantined only when it cannot support any analysis: missing or
non-numeric review id, missing game id, or an invalid label. Missing text or
timestamps keep the record; it is only excluded from ML or time charts.
Reasons are checked in the order below and each record gets exactly one,
so quarantine counts never overlap in the reconciliation equation.
"""

from __future__ import annotations

from enum import Enum


class QuarantineReason(str, Enum):
    MALFORMED_RECORD = "malformed_record"
    MISSING_REVIEW_ID = "missing_review_id"
    INVALID_REVIEW_ID = "invalid_review_id"
    MISSING_APP_ID = "missing_app_id"
    INVALID_APP_ID = "invalid_app_id"
    INVALID_LABEL = "invalid_label"


QUARANTINE_ORDER: tuple[QuarantineReason, ...] = tuple(QuarantineReason)

# Language values are trimmed and lower-cased; missing ones become this group.
UNKNOWN_LANGUAGE = "unknown"


def normalize_language(raw: str | None) -> str:
    if raw is None or not raw.strip():
        return UNKNOWN_LANGUAGE
    return raw.strip().lower()
