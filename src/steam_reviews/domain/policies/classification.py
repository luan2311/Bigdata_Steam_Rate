"""Binary classification metrics from a confusion matrix (Plan.md 5.2).

Label 1 (recommended) is the positive class. Macro-F1 is the unweighted mean of
the F1 of both classes; it is never replaced by weighted-F1.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Confusion:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


@dataclass(frozen=True)
class BinaryScores:
    precision: dict[int, float]
    recall: dict[int, float]
    f1: dict[int, float]
    macro_f1: float
    accuracy: float


def binary_scores(c: Confusion) -> BinaryScores:
    precision = {1: _ratio(c.tp, c.tp + c.fp), 0: _ratio(c.tn, c.tn + c.fn)}
    recall = {1: _ratio(c.tp, c.tp + c.fn), 0: _ratio(c.tn, c.tn + c.fp)}
    f1 = {label: _f1(precision[label], recall[label]) for label in (0, 1)}
    return BinaryScores(precision, recall, f1, (f1[0] + f1[1]) / 2, _ratio(c.tp + c.tn, c.total))


def class_weights(label_counts: dict[int, int]) -> dict[int, float]:
    """Balanced weights n / (2 * n_c) computed from train counts only."""
    total = sum(label_counts.values())
    return {label: total / (2 * n) for label, n in label_counts.items() if n}
