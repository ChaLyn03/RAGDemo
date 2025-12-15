"""Deterministic chunking rules for corpus documents."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def chunk_markdown(path: str | Path, max_lines: int = 40) -> Iterable[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for idx in range(0, len(lines), max_lines):
        yield "\n".join(lines[idx : idx + max_lines])
