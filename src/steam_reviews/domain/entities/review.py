"""Entities đại diện cho bài đánh giá và tác giả trên nền tảng Steam (Thuần Python)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class AuthorInfo:
    """Thông tin về người viết đánh giá."""
    steamid: Optional[str] = None
    num_games_owned: int = 0
    num_reviews: int = 0
    playtime_forever_minutes: Optional[float] = None
    playtime_at_review_minutes: Optional[float] = None


@dataclass(frozen=True)
class ReviewEngagement:
    """Thông tin tương tác cộng đồng của bài đánh giá."""
    votes_helpful: int = 0
    votes_funny: int = 0
    weighted_vote_score: float = 0.0
    comment_count: int = 0


@dataclass(frozen=True)
class Review:
    """
    Thực thể bài đánh giá trò chơi Steam (Clean Architecture Domain Entity).
    Tuyệt đối độc lập với Spark và mọi framework bên ngoài.
    """
    review_id: int
    app_id: int
    app_name: str
    language: str
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime
    recommended: bool
    author: AuthorInfo
    engagement: ReviewEngagement
    steam_purchase: bool = True
    received_for_free: bool = False
    written_during_early_access: bool = False

    def is_positive(self) -> bool:
        """Đánh giá có khuyến nghị hay không."""
        return self.recommended

    def has_content(self) -> bool:
        """Đánh giá có chứa nội dung văn bản chữ hay không."""
        return bool(self.review_text and self.review_text.strip())

    @property
    def label(self) -> float:
        """Nhãn số học phục vụ mô hình máy học (1.0 = True, 0.0 = False)."""
        return 1.0 if self.recommended else 0.0
