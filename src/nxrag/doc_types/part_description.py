"""Part description contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from nxrag.ir.evidence import EvidenceSet


@dataclass
class PartSection:
    heading: str
    body: str
    evidence: EvidenceSet


def required_sections() -> Sequence[str]:
    return ["Overview", "Specifications", "Evidence"]
