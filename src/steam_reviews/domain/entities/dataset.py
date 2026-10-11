"""Dataset and run identity shared by every pipeline stage."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class DatasetLevel(str, Enum):
    """Scale levels from Plan.md section 3.2."""

    SMOKE = "smoke"
    CORE = "core"
    FULL = "full"


@dataclass(frozen=True)
class DatasetReference:
    """Location and identity of one input dataset; never the rows themselves."""

    uri: str
    dataset_version: str
    level: DatasetLevel
    sha256: str | None = None


@dataclass(frozen=True)
class RunId:
    """Identifier tying silver, gold, metrics and snapshots of one run together."""

    value: str

    @classmethod
    def new(cls, level: DatasetLevel, now: datetime | None = None) -> "RunId":
        stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
        return cls(f"{level.value}-{stamp}")

    def __str__(self) -> str:
        return self.value
