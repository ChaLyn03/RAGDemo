"""
Lexical MVP validator: if retrieved exemplars/style/template contain concrete facts,
the model output must include them.

This module MUST expose `validate_exemplar_inclusion` because the pipeline imports it.
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


def _exemplar_demands(retrieved_context: str) -> list[str]:
    demands: list[str] = []

    if _has_any(_TOL_RE, retrieved_context):
        demands.append("tolerance")

    if _has_any(_MATERIAL_RE, retrieved_context):
        demands.append("material")

    if _has_any(_TORQUE_RE, retrieved_context):
        demands.append("torque")

    if _any_substring(retrieved_context, _FASTENER_HINTS):
        demands.append("fastener_practice")

    return demands


def validate_require_exemplars(output_text: str, retrieved_context: str) -> ExemplarValidation:
    """
    Core validator: decide what details are required (based on retrieved_context),
    then ensure output_text contains them.
    """
    missing: list[str] = []
    demands = _exemplar_demands(retrieved_context)
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


# ---------------------------------------------------------------------
# Compatibility shim: this is what your pipeline currently imports.
# run.py calls:
#   validation = validate_exemplar_inclusion(exemplar_text=..., output_text=...)
#   if not validation.ok: ...
# ---------------------------------------------------------------------
def validate_exemplar_inclusion(*, exemplar_text: str, output_text: str) -> ExemplarValidation:
    return validate_require_exemplars(output_text=output_text, retrieved_context=exemplar_text)
