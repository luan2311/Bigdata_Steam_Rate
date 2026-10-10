"""Entity quản lý metadata cho các lần thực thi pipeline."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RunMetadata:
    """Metadata đại diện cho một lần thực thi chu trình xử lý dữ liệu lớn."""
    run_id: str
    dataset_version: str
    tier: str  # 'smoke', 'core', 'full'
    total_records_read: int
    valid_records_count: int
    created_at: datetime
