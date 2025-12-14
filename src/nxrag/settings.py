"""Settings loader for nxrag."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class AppSettings:
    app_name: str
    default_model: str
    assets_path: Path
    corpus_path: Path
    outputs_path: Path
    max_chunks: int
    max_tokens: int


DEFAULT_CONFIG_PATH = Path("configs/app.yaml")


def load_settings(config_path: str | os.PathLike | None = None) -> AppSettings:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    app = raw.get("app", {})
    paths = raw.get("paths", {})
    limits = raw.get("limits", {})

    return AppSettings(
        app_name=app.get("name", "nxrag"),
        default_model=app.get("default_model", "gpt-4o"),
        assets_path=Path(paths.get("assets", "assets")),
        corpus_path=Path(paths.get("corpus", "assets/corpus")),
        outputs_path=Path(paths.get("outputs", "var/runs")),
        max_chunks=int(limits.get("max_chunks", 10)),
        max_tokens=int(limits.get("max_tokens", 2000)),
    )
