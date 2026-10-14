import os
from pathlib import Path
from steam_reviews.application.use_cases.get_dashboard_analytics import GetDashboardAnalyticsUseCase
from steam_reviews.infrastructure.storage.json_snapshot_adapter import JsonSnapshotAdapter


def create_dashboard_use_case() -> GetDashboardAnalyticsUseCase:
    """Composition root: khởi tạo use case và inject adapter snapshot phù hợp."""
    default_fixture = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "dashboard_snapshot_fixture.json"
    snapshot_path_env = os.environ.get("STEAM_DASHBOARD_SNAPSHOT_PATH")
    
    target_path = Path(snapshot_path_env) if snapshot_path_env else default_fixture
    adapter = JsonSnapshotAdapter(snapshot_path=target_path)
    return GetDashboardAnalyticsUseCase(reader=adapter)
