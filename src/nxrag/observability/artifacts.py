"""Run artifact helpers."""

from __future__ import annotations

from pathlib import Path

RUNS_ROOT = Path("var/runs")


def save_artifact(name: str, content: str) -> Path:
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    path = RUNS_ROOT / name
    path.write_text(content, encoding="utf-8")
    return path
