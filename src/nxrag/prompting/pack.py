"""Combine prompt components into a final payload."""

from __future__ import annotations

from pathlib import Path


def load_prompt(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def build_prompt(system_path: str | Path, template_path: str | Path) -> str:
    system = load_prompt(system_path)
    template = load_prompt(template_path)
    return f"{system}\n\n{template}"
