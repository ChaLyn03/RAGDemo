"""Settings loader for nxrag."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

try:  # Optional dependency
    import yaml
except ImportError:  # pragma: no cover - exercised in environments without PyYAML
    yaml = None


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
    raw = _load_yaml(path)

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


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    # Minimal parser for simple key/value YAML files to avoid a hard dependency in demos.
    data: Dict[str, Any] = {}
    stack: list[Tuple[int, Dict[str, Any]]] = [(0, data)]

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"')

        while len(stack) > 1 and indent < stack[-1][0]:
            stack.pop()

        current = stack[-1][1]
        if value:
            current[key] = value
        else:
            current[key] = {}
            stack.append((indent + 2, current[key]))

    return data
