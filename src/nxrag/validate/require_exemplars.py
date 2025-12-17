"""Lexical MVP validator: if retrieved exemplars contain concrete facts,
the model output must include them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


_TOL_RE = re.compile(r"±\s*\d+(?:\.\d+)?\s*(?:mm|in)\b", re.IGNORECASE)
_MATERIAL_RE = re.compile(
    r"\b(6061[-\s]?T6|7075[-\s]?T6|stainless\s+steel|aluminum|aluminium)\b",
    re.IGNORECASE,
)
_TORQUE_RE = re.compile(r"\b\d+(?:\.\d+)?\s*N[·\. ]?m\b", re.IGNORECASE)

_FASTENER_HINTS = [
    "threadlocker",
    "anti-seize",
    "socket head cap screws",
    "torque",
]


@dataclass
class ExemplarValidation:
    ok: bool
    missing: list[str]


def _has_any(pattern: re.Pattern[str], text: str) -> bool:
    return pattern.search(text) is not None


def _any_substring(haystack: str, needles: Iterable[str]) -> bool:
    h = haystack.lower()
    return any(n.lower() in h for n in needles)


def _exemplar_demands(exemplar_text: str) -> set[str]:
    demands: set[str] = set()
    if _has_any(_TOL_RE, exemplar_text):
        demands.add("tolerance")
    if _has_any(_MATERIAL_RE, exemplar_text):
        demands.add("material")
    if _has_any(_TORQUE_RE, exemplar_text):
        demands.add("torque")
    if _any_substring(exemplar_text, _FASTENER_HINTS):
        demands.add("fastener_practice")
    return demands


def validate_exemplar_inclusion(*, exemplar_text: str, output_text: str) -> ExemplarValidation:
    missing: list[str] = []
    demands = _exemplar_demands(exemplar_text)
    out = output_text.strip()

    if "tolerance" in demands and not _has_any(_TOL_RE, out):
        missing.append("explicit tolerance from exemplars (e.g., ±0.05 mm)")
    if "material" in demands and not _has_any(_MATERIAL_RE, out):
        missing.append("material from exemplars (e.g., 6061-T6)")
    if "torque" in demands and not _has_any(_TORQUE_RE, out):
        missing.append("torque value from exemplars (e.g., 4.5 N·m)")
    if "fastener_practice" in demands and not _any_substring(out, _FASTENER_HINTS):
        missing.append("fastener practice from exemplars (e.g., threadlocker / anti-seize)")

    return ExemplarValidation(ok=(len(missing) == 0), missing=missing)
