"""Export run artifacts for analysis."""

from __future__ import annotations

from pathlib import Path
import shutil

RUNS_ROOT = Path("var/runs")


def export(destination: str) -> None:
    dest_path = Path(destination)
    dest_path.mkdir(parents=True, exist_ok=True)
    for item in RUNS_ROOT.glob("**/*"):
        if item.is_file():
            target = dest_path / item.name
            shutil.copy2(item, target)
