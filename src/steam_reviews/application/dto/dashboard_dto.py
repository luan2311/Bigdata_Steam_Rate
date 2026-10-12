from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass(frozen=True)
class DashboardMetadataDTO:
    run_id: str
    dataset_version: str
    created_at: str
    total_games: int
    total_valid_reviews: int
    is_fixture: bool = False


@dataclass(frozen=True)
class DataQualitySummaryDTO:
    raw_records: int
    valid_records: int
    duplicate_records: int
    quarantine_records: int
    quarantine_by_reason: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class GameAnalyticsItemDTO:
    app_id: str
    app_name: str
    total_reviews: int
    recommended_count: int
    recommendation_rate: float


@dataclass(frozen=True)
class MonthlyTrendItemDTO:
    year_month: str
    total_reviews: int
    recommended_count: int
    recommendation_rate: float
    app_id: Optional[str] = None
    language: Optional[str] = None


@dataclass(frozen=True)
class LanguageDistributionItemDTO:
    language: str
    total_reviews: int
    recommendation_rate: float


@dataclass(frozen=True)
class PlaytimeBinItemDTO:
    bin_label: str
    min_hours: float
    max_hours: Optional[float]
    total_reviews: int
    recommendation_rate: float


@dataclass(frozen=True)
class ModelMetricsDTO:
    split_manifest: Dict[str, int]
    baseline_metrics: Dict[str, float]
    model_metrics: Dict[str, float]
    confusion_matrix: Dict[str, int]
    sample_errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class DashboardSnapshotDTO:
    metadata: DashboardMetadataDTO
    quality_summary: DataQualitySummaryDTO
    game_summary: List[GameAnalyticsItemDTO]
    monthly_summary: List[MonthlyTrendItemDTO]
    language_summary: List[LanguageDistributionItemDTO]
    playtime_summary: List[PlaytimeBinItemDTO]
    model_metrics: ModelMetricsDTO
