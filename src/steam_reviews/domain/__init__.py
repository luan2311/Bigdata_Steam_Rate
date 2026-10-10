"""
Clean Architecture Domain Layer (Framework-independent concepts and business policies).
Hoàn toàn độc lập với Apache Spark, Hadoop, NiFi, Streamlit và mọi thư viện bên ngoài.
"""

from steam_reviews.domain.entities import (
    AuthorInfo,
    GameSummary,
    LanguageMetric,
    PlaytimeMetric,
    Review,
    ReviewEngagement,
    RunMetadata,
)
from steam_reviews.domain.policies import (
    aggregate_recommendation_rate,
    categorize_playtime_bucket,
    clean_review_text,
    get_playtime_bucket_order,
    is_review_eligible_for_ml,
    is_valid_app_id,
    is_valid_review_id,
    label_to_numeric,
    minutes_to_hours,
    parse_recommended_label,
    safe_recommendation_rate,
)

__all__ = [
    "AuthorInfo",
    "ReviewEngagement",
    "Review",
    "GameSummary",
    "LanguageMetric",
    "PlaytimeMetric",
    "RunMetadata",
    "safe_recommendation_rate",
    "parse_recommended_label",
    "label_to_numeric",
    "aggregate_recommendation_rate",
    "is_valid_review_id",
    "is_valid_app_id",
    "clean_review_text",
    "is_review_eligible_for_ml",
    "categorize_playtime_bucket",
    "get_playtime_bucket_order",
    "minutes_to_hours",
]
