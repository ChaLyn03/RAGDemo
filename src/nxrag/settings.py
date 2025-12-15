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

    # paths
    assets_path: Path
    corpus_path: Path
    outputs_path: Path

    # limits
    max_chunks: int
    max_tokens: int

    # llm
    llm_provider: str  # "stub" or "openai"


DEFAULT_CONFIG_PATH = Path("configs/app.yaml")


def load_settings(config_path: str | os.PathLike | None = None) -> AppSettings:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    app = raw.get("app", {}) or {}
    paths = raw.get("paths", {}) or {}
    limits = raw.get("limits", {}) or {}
    llm = raw.get("llm", {}) or {}

    # Allow env override without breaking config-driven use
    env_provider = os.getenv("NX_RAG_LLM_PROVIDER")

    return AppSettings(
        app_name=app.get("name", "nxrag"),
        default_model=app.get("default_model", "gpt-4o"),
        assets_path=Path(paths.get("assets", "assets")),
        corpus_path=Path(paths.get("corpus", "assets/corpus")),
        outputs_path=Path(paths.get("outputs", "var/runs")),
        max_chunks=int(limits.get("max_chunks", 10)),
        max_tokens=int(limits.get("max_tokens", 2000)),
        llm_provider=(env_provider or llm.get("provider", "stub")),
    )
