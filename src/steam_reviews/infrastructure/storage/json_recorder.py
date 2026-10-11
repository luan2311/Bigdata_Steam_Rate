"""RunRecorder writing small JSON artifacts to artifacts/metrics/<run_id>/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from steam_reviews.domain.entities.dataset import RunId


class JsonRunRecorder:
    def __init__(self, root: Path) -> None:
        self._root = root

    def _path(self, run_id: RunId, name: str) -> Path:
        return self._root / str(run_id) / f"{name}.json"

    def save(self, run_id: RunId, name: str, payload: dict[str, Any]) -> str:
        path = self._path(run_id, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        tmp.replace(path)
        return path.as_posix()

    def load(self, run_id: RunId, name: str) -> dict[str, Any]:
        path = self._path(run_id, name)
        if not path.exists():
            raise FileNotFoundError(f"{path} not found; run the previous step for {run_id} first")
        return json.loads(path.read_text(encoding="utf-8"))
