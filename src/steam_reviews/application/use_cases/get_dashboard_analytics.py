from typing import Optional
from steam_reviews.application.ports.analytics_reader_port import AnalyticsReaderPort
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO


class GetDashboardAnalyticsUseCase:
    """Use case điều phối truy xuất dữ liệu phân tích phục vụ Dashboard hiển thị."""

    def __init__(self, reader: AnalyticsReaderPort) -> None:
        self._reader = reader

    def execute(self, run_id: Optional[str] = None) -> DashboardSnapshotDTO:
        return self._reader.get_latest_snapshot(run_id=run_id)
