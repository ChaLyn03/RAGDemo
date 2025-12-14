"""Evidence tracking utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class Evidence:
    chunk_id: str
    start_line: int
    end_line: int


@dataclass
class EvidenceSet:
    items: Sequence[Evidence]
