"""Convert DTOs to JSON-compatible dicts for RunRecorder, and back.

JSON turns integer dict keys (class labels) into strings; the readers below
restore them so a later step sees the same values the earlier step produced.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any

from steam_reviews.application.dto.modeling import (
    ClassificationMetrics,
    FittedModel,
    ModelConfig,
    SplitSummary,
    TrainResult,
)
from steam_reviews.application.dto.pipeline import QualityCounts
from steam_reviews.domain.entities.dataset import RunId
from steam_reviews.domain.policies.split import Split


def to_payload(value: Any) -> Any:
    if isinstance(value, RunId):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: to_payload(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(to_payload(k)): to_payload(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_payload(v) for v in value]
    return value


def _int_keys(mapping: dict[str, Any]) -> dict[int, Any]:
    return {int(k): v for k, v in mapping.items()}


def quality_counts_from(payload: dict[str, Any]) -> QualityCounts:
    return QualityCounts(**payload)


def split_summary_from(payload: dict[str, Any]) -> SplitSummary:
    return SplitSummary(
        splits_uri=payload["splits_uri"],
        rows=payload["rows"],
        label_counts={split: _int_keys(counts) for split, counts in payload["label_counts"].items()},
        excluded=payload["excluded"],
        leakage=payload["leakage"],
    )


def metrics_from(payload: dict[str, Any]) -> ClassificationMetrics:
    values = dict(payload)
    values["split"] = Split(values["split"])
    for key in ("precision", "recall", "f1"):
        values[key] = _int_keys(values[key])
    return ClassificationMetrics(**values)


def train_result_from(payload: dict[str, Any]) -> TrainResult:
    selected = payload["selected"]
    return TrainResult(
        run_id=RunId(payload["run_id"]),
        baseline_validation=metrics_from(payload["baseline_validation"]),
        validation={name: metrics_from(m) for name, m in payload["validation"].items()},
        selected=FittedModel(ModelConfig(**selected["config"]), selected["model_uri"]),
        majority_label=int(payload["majority_label"]),
    )
