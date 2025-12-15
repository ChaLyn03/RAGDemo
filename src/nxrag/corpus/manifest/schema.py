"""Manifest record schema."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class ManifestEntry:
    path: Path
    tags: Sequence[str]
