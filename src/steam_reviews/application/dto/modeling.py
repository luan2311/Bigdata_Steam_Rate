"""Model configuration, split summaries and metrics as plain values."""

from __future__ import annotations

from dataclasses import dataclass, field

from steam_reviews.domain.entities.dataset import RunId
from steam_reviews.domain.policies.split import Split, SplitPolicy


@dataclass(frozen=True)
class ModelConfig:
    name: str
    num_features: int = 2**16
    max_iter: int = 30
    reg_param: float = 0.01
    class_weighting: bool = False


BASELINE_NAME = "baseline_majority"


@dataclass(frozen=True)
class SplitRequest:
    run_id: RunId
    silver_uri: str
    splits_uri: str
    policy: SplitPolicy
    max_rows: int | None


@dataclass(frozen=True)
class SplitSummary:
    splits_uri: str
    rows: dict[str, int]
    label_counts: dict[str, dict[int, int]]
    excluded: dict[str, int]
    leakage: dict[str, int]
    """Overlap counts per split pair for review_id and text hash; all must be 0."""


@dataclass(frozen=True)
class ClassificationMetrics:
    model: str
    split: Split
    rows: int
    precision: dict[int, float]
    recall: dict[int, float]
    f1: dict[int, float]
    macro_f1: float
    accuracy: float
    pr_auc_positive: float | None
    confusion: dict[str, int]
    """Keys tp, fp, tn, fn with label 1 (recommended) as the positive class."""


@dataclass(frozen=True)
class FittedModel:
    config: ModelConfig
    model_uri: str


@dataclass(frozen=True)
class TrainRequest:
    run_id: RunId
    splits: SplitSummary
    models_uri: str
    configs: tuple[ModelConfig, ...]


@dataclass(frozen=True)
class TrainResult:
    run_id: RunId
    baseline_validation: ClassificationMetrics
    validation: dict[str, ClassificationMetrics]
    selected: FittedModel
    majority_label: int


@dataclass(frozen=True)
class EvaluateResult:
    run_id: RunId
    baseline_test: ClassificationMetrics
    model_test: ClassificationMetrics
    error_examples_uri: str | None = None
    notes: list[str] = field(default_factory=list)
