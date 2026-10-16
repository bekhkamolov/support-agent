"""Disk cache for model and judge outputs, so reruns do not call the APIs again."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..config import CACHE_DIR


def cache_key(parts: dict) -> str:
    """Stable hash of everything that determines an output (model, inputs, prompt version, ...)."""
    return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]


class DiskCache:
    def __init__(self, name: str, root: Path = CACHE_DIR / "eval"):
        self.dir = root / name

    def get(self, key: str) -> dict | None:
        path = self.dir / f"{key}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def put(self, key: str, value: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / f"{key}.json").write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")
