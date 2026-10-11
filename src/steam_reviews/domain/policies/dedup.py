"""Deduplication rule (Plan.md section 3.3).

Keep one row per `review_id` across the whole run scope. The winner is the row
that sorts first by DEDUP_ORDER; the final key (`source_row` within
`source_file`) makes ties deterministic even when timestamps are equal or null.
"""

from __future__ import annotations

from dataclasses import dataclass

DEDUP_KEY = "review_id"


@dataclass(frozen=True)
class SortKey:
    column: str
    descending: bool
    nulls_last: bool = True


DEDUP_ORDER: tuple[SortKey, ...] = (
    SortKey("updated_at", descending=True),
    SortKey("created_at", descending=True),
    SortKey("source_file", descending=False),
    SortKey("source_row", descending=False),
)
