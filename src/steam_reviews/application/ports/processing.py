"""Batch-level contracts implemented by Spark / MLlib / storage adapters."""

from __future__ import annotations

from typing import Any, Protocol

from steam_reviews.application.dto.modeling import (
    ClassificationMetrics,
    FittedModel,
    ModelConfig,
    SplitRequest,
    SplitSummary,
)
from steam_reviews.application.dto.pipeline import (
    AnalyticsRequest,
    AnalyticsResult,
    CleanRequest,
    CleanResult,
)
from steam_reviews.domain.entities.dataset import RunId
from steam_reviews.domain.policies.split import Split


class ReviewBatchProcessor(Protocol):
    def clean(self, request: CleanRequest) -> CleanResult:
        """Normalize, quarantine and deduplicate; write silver; return counts."""


class AnalyticsProcessor(Protocol):
    def build(self, request: AnalyticsRequest) -> AnalyticsResult:
        """Write gold tables from silver; return row counts and failed checks."""


class ModelTrainer(Protocol):
    def prepare_splits(self, request: SplitRequest) -> SplitSummary:
        """Filter the ML scope, assign splits by text hash and persist them."""

    def majority_label(self, splits: SplitSummary) -> int:
        """Most frequent label in train only."""

    def score_baseline(self, splits: SplitSummary, label: int, split: Split) -> ClassificationMetrics:
        ...

    def fit(self, splits: SplitSummary, config: ModelConfig, models_uri: str) -> FittedModel:
        """Fit the feature pipeline and classifier on train only."""

    def score(self, model: FittedModel, splits: SplitSummary, split: Split) -> ClassificationMetrics:
        ...

    def error_examples(self, model: FittedModel, splits: SplitSummary, split: Split,
                       limit: int) -> list[dict[str, Any]]:
        """A deterministic sample of misclassified rows for manual error analysis."""


class RunRecorder(Protocol):
    def save(self, run_id: RunId, name: str, payload: dict[str, Any]) -> str:
        """Persist a small JSON artifact (metrics, manifest) and return its location."""

    def load(self, run_id: RunId, name: str) -> dict[str, Any]:
        """Read back an artifact saved by an earlier step of the same run."""
