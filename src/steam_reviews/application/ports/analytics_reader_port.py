from abc import ABC, abstractmethod
from typing import Optional
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO


class AnalyticsReaderPort(ABC):
    """Port trừu tượng cho việc đọc dữ liệu phân tích / snapshot Dashboard."""

    @abstractmethod
    def get_latest_snapshot(self, run_id: Optional[str] = None) -> DashboardSnapshotDTO:
        """Lấy snapshot phân tích gần nhất hoặc theo run_id chỉ định."""
        raise NotImplementedError
