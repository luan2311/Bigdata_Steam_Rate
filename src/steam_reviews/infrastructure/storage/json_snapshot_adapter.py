import json
from pathlib import Path
from typing import Optional
from steam_reviews.application.ports.analytics_reader_port import AnalyticsReaderPort
from steam_reviews.application.dto.dashboard_dto import (
    DashboardSnapshotDTO,
    DashboardMetadataDTO,
    DataQualitySummaryDTO,
    GameAnalyticsItemDTO,
    MonthlyTrendItemDTO,
    LanguageDistributionItemDTO,
    PlaytimeBinItemDTO,
    ModelMetricsDTO,
)


class JsonSnapshotAdapter(AnalyticsReaderPort):
    """Adapter đọc dữ liệu snapshot định dạng JSON từ file hệ thống hoặc thư mục lưu trữ."""

    def __init__(self, snapshot_path: Path) -> None:
        self._snapshot_path = Path(snapshot_path)

    def get_latest_snapshot(self, run_id: Optional[str] = None) -> DashboardSnapshotDTO:
        if not self._snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot file not found at: {self._snapshot_path}")

        with open(self._snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = DashboardMetadataDTO(**data["metadata"])
        quality = DataQualitySummaryDTO(**data["quality_summary"])
        games = [GameAnalyticsItemDTO(**item) for item in data["game_summary"]]
        monthly = [MonthlyTrendItemDTO(**item) for item in data["monthly_summary"]]
        langs = [LanguageDistributionItemDTO(**item) for item in data["language_summary"]]
        playtimes = [PlaytimeBinItemDTO(**item) for item in data["playtime_summary"]]
        model = ModelMetricsDTO(**data["model_metrics"])

        return DashboardSnapshotDTO(
            metadata=meta,
            quality_summary=quality,
            game_summary=games,
            monthly_summary=monthly,
            language_summary=langs,
            playtime_summary=playtimes,
            model_metrics=model,
        )
