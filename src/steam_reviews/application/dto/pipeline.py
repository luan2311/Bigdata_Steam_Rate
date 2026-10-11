"""Requests and results of the batch pipeline: small values, no DataFrames."""

from __future__ import annotations

from dataclasses import dataclass, field

from steam_reviews.domain.entities.dataset import DatasetReference, RunId


@dataclass(frozen=True)
class CleanRequest:
    source: DatasetReference
    run_id: RunId
    silver_uri: str
    quarantine_uri: str


@dataclass(frozen=True)
class QualityCounts:
    """Counts behind quality_summary and reconciliation check V4."""

    rows_parsed: int
    invalid_by_reason: dict[str, int]
    valid_pre_dedup: int
    duplicates_removed: int
    silver_rows: int
    blank_text: int
    missing_created_at: int
    missing_playtime_at_review: int

    @property
    def invalid_records(self) -> int:
        return sum(self.invalid_by_reason.values())

    def reconciliation_errors(self) -> list[str]:
        errors = []
        if self.rows_parsed != self.invalid_records + self.valid_pre_dedup:
            errors.append(
                f"rows_parsed {self.rows_parsed} != invalid {self.invalid_records}"
                f" + valid_pre_dedup {self.valid_pre_dedup}"
            )
        if self.silver_rows != self.valid_pre_dedup - self.duplicates_removed:
            errors.append(
                f"silver {self.silver_rows} != valid_pre_dedup {self.valid_pre_dedup}"
                f" - duplicates {self.duplicates_removed}"
            )
        return errors


@dataclass(frozen=True)
class CleanResult:
    run_id: RunId
    silver_uri: str
    quarantine_uri: str
    counts: QualityCounts


@dataclass(frozen=True)
class AnalyticsRequest:
    run_id: RunId
    silver_uri: str
    gold_uri: str
    counts: QualityCounts


@dataclass(frozen=True)
class AnalyticsResult:
    run_id: RunId
    gold_uri: str
    table_rows: dict[str, int]
    check_errors: list[str] = field(default_factory=list)
