"""Placeholder adapter for Nx Open Python files."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_script(path: str | Path) -> dict[str, Any]:
    """Return a stub representation of a Nx Open Python script."""
    source = Path(path).read_text(encoding="utf-8") if Path(path).exists() else ""
    return {"path": str(path), "source": source}
