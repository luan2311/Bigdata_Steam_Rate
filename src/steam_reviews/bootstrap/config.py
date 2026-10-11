"""Runtime configuration from environment variables.

Local defaults keep the lake under data/lake. On the cluster TV1 sets
STEAM_LAKE_ROOT=hdfs://namenode:8020/steam and SPARK_MASTER=spark://master:7077;
no code changes are needed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from steam_reviews.domain.entities.dataset import RunId

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class AppConfig:
    lake_root: str
    artifacts_root: Path
    spark_master: str
    driver_memory: str
    shuffle_partitions: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            lake_root=os.environ.get("STEAM_LAKE_ROOT", (PROJECT_ROOT / "data" / "lake").as_posix()),
            artifacts_root=Path(os.environ.get("STEAM_ARTIFACTS_ROOT", PROJECT_ROOT / "artifacts")),
            spark_master=os.environ.get("SPARK_MASTER", "local[*]"),
            driver_memory=os.environ.get("SPARK_DRIVER_MEMORY", "4g"),
            shuffle_partitions=int(os.environ.get("SPARK_SHUFFLE_PARTITIONS", "16")),
        )

    def lake(self, zone: str, run_id: RunId) -> str:
        return f"{self.lake_root.rstrip('/')}/{zone}/{run_id}"

    def models_uri(self, run_id: RunId) -> str:
        return (self.artifacts_root / "models" / str(run_id)).as_posix()
