"""Detect input type based on extension."""

from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS = {".md": "markdown", ".txt": "text", ".py": "nxopen_python"}


def detect_type(path: str | Path) -> str:
    extension = Path(path).suffix.lower()
    return SUPPORTED_EXTENSIONS.get(extension, "unknown")
