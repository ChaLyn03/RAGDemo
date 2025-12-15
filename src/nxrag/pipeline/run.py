"""Top-level pipeline runner."""

from __future__ import annotations

from pathlib import Path

from nxrag.settings import load_settings


def run_pipeline(input_path: str | Path, config_path: str | Path) -> None:
    settings = load_settings(config_path)
    print(f"Running pipeline for {input_path} with model {settings.default_model}")
