"""Persistence helpers for indexes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


INDEX_ROOT = Path("var/indexes")


def save_index(name: str, payload: dict[str, Any]) -> Path:
    INDEX_ROOT.mkdir(parents=True, exist_ok=True)
    path = INDEX_ROOT / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_index(name: str) -> dict[str, Any]:
    path = INDEX_ROOT / f"{name}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
