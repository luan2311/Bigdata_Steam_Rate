"""Entities đại diện cho tổng hợp trò chơi và phân nhóm dữ liệu."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GameSummary:
    """Thực thể tổng hợp thống kê cho một tựa game."""
    app_id: int
    app_name: str
    total_reviews: int
    recommended_count: int
    not_recommended_count: int
    recommendation_rate: Optional[float]
    avg_playtime_hours: Optional[float] = None
    median_playtime_hours: Optional[float] = None


@dataclass(frozen=True)
class LanguageMetric:
    """Thực thể thống kê theo ngôn ngữ."""
    language: str
    total_reviews: int
    recommended_count: int
    recommendation_rate: Optional[float]
    percentage_of_total: float = 0.0


@dataclass(frozen=True)
class PlaytimeMetric:
    """Thực thể thống kê theo phân nhóm giờ chơi."""
    playtime_bucket: str
    bucket_order: int
    total_reviews: int
    recommended_count: int
    recommendation_rate: Optional[float]
