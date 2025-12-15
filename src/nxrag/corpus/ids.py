"""Stable chunk ID helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path


def chunk_id(path: str | Path, index: int, content: str) -> str:
    digest = hashlib.sha1(content.encode("utf-8")).hexdigest()[:8]
    return f"{Path(path).stem}-{index:04d}-{digest}"
