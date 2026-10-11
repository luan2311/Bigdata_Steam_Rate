"""ML dataset and split rules (Plan.md section 5.2).

Rows are grouped by normalized review text, and every group goes to exactly one
split. Identical texts therefore never appear in both train and test. The hash
itself is computed by the adapter; this module fixes what is hashed, the seed
and the bucket thresholds so every adapter assigns the same split.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

ML_LANGUAGE = "english"
ML_MAX_ROWS_CORE = 200_000

_WHITESPACE = re.compile(r"\s+")


class Split(str, Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


def normalize_text(text: str | None) -> str:
    """Grouping key for leakage control: single-spaced, trimmed, lower-cased.

    Spark equivalent: lower(trim(regexp_replace(text, '(?U)\\s+', ' '))).
    """
    if text is None:
        return ""
    return _WHITESPACE.sub(" ", text).strip(" ").lower()


@dataclass(frozen=True)
class SplitPolicy:
    seed: str = "steam2021-tv2"
    buckets: int = 10_000
    train_ratio: float = 0.70
    validation_ratio: float = 0.15

    def __post_init__(self) -> None:
        if not 0 < self.train_ratio < 1 or not 0 < self.validation_ratio < 1:
            raise ValueError("ratios must be in (0, 1)")
        if self.train_ratio + self.validation_ratio >= 1:
            raise ValueError("test ratio must stay positive")

    @property
    def train_upper(self) -> int:
        return round(self.buckets * self.train_ratio)

    @property
    def validation_upper(self) -> int:
        return round(self.buckets * (self.train_ratio + self.validation_ratio))

    def assign(self, bucket: int) -> Split:
        if not 0 <= bucket < self.buckets:
            raise ValueError(f"bucket must be in [0, {self.buckets})")
        if bucket < self.train_upper:
            return Split.TRAIN
        if bucket < self.validation_upper:
            return Split.VALIDATION
        return Split.TEST
