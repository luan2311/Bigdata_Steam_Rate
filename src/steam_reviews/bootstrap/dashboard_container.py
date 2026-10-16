import os
from pathlib import Path
from steam_reviews.application.use_cases.get_dashboard_analytics import GetDashboardAnalyticsUseCase
from steam_reviews.infrastructure.storage.json_snapshot_adapter import JsonSnapshotAdapter


from typing import Optional, Union


def create_dashboard_use_case(
    snapshot_path: Optional[Union[Path, str]] = None,
) -> GetDashboardAnalyticsUseCase:
    """Composition root: khởi tạo use case và inject adapter snapshot phù hợp."""
    default_fixture = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "dashboard_snapshot_fixture.json"
    snapshot_path_env = os.environ.get("STEAM_DASHBOARD_SNAPSHOT_PATH")
    
    if snapshot_path is not None:
        target_path = Path(snapshot_path)
    elif snapshot_path_env:
        target_path = Path(snapshot_path_env)
    else:
        target_path = default_fixture

    adapter = JsonSnapshotAdapter(snapshot_path=target_path)
    return GetDashboardAnalyticsUseCase(reader=adapter)

