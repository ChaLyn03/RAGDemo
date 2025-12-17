"""Simple validator to ensure exemplar-backed details appear in the output.

MVP approach:
- If retrieved context contains strong exemplar signals (e.g., 6061-T6, ±0.05, threadlocker/anti-seize/torque),
  require the model output to include at least one item from each category present.

This is intentionally blunt and lexical. Replace later with IR + citation-based validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ValidationResult:
    ok: bool
    missing: List[str]


_MATERIAL_PATTERNS = [
    r"\b6061[-\s]?t6\b",
    r"\baluminum\b",
    r"\baluminium\b",
]

_TOLERANCE_PATTERNS = [
    r"±\s*\d+(\.\d+)?\s*mm",
    r"\b\+\s*/\s*-\s*\d+(\.\d+)?\s*mm\b",
    r"\btolerance\b",
]

_VIBE_PRACTICE_PATTERNS = [
    r"\bthreadlocker\b",
    r"\banti-?seize\b",
    r"\btorque\b",
    r"\bsocket head cap screws\b",
]


def _contains_any(text: str, patterns: list[str]) -> bool:
    t = text.lower()
    return any(re.search(p, t, flags=re.IGNORECASE) for p in patterns)


_PRACTICE_SUBTOPICS = {
    "threadlocker": [r"\bthreadlocker\b"],
    "anti_seize": [r"\banti-?seize\b"],
    "torque": [r"\btorque\b", r"\bN[·.]m\b", r"\bN\s*·\s*m\b"],
}


def validate_exemplar_inclusion(exemplar_text: str, output_text: str) -> ValidationResult:
    """Require exemplar-backed categories (and subtopics) to appear in the output."""
    missing: list[str] = []

    # Determine which categories are "present" in retrieved exemplars
    needs_material = _contains_any(exemplar_text, _MATERIAL_PATTERNS)
    needs_tolerance = _contains_any(exemplar_text, _TOLERANCE_PATTERNS)
    needs_practices = _contains_any(exemplar_text, _VIBE_PRACTICE_PATTERNS)

    # Check output for those categories
    if needs_material and not _contains_any(output_text, _MATERIAL_PATTERNS):
        missing.append("material detail from exemplars (e.g., 6061-T6 aluminum)")

    # Tolerance: if context has explicit ±...mm, require that form; otherwise tolerate generic "tolerance"
    if needs_tolerance:
        # Prefer explicit ± mm if present in context
        explicit_in_ctx = _contains_any(exemplar_text, [r"±\s*\d+(\.\d+)?\s*mm"])
        if explicit_in_ctx:
            if not _contains_any(output_text, [r"±\s*\d+(\.\d+)?\s*mm"]):
                missing.append("explicit tolerance from exemplars (e.g., ±0.05 mm)")
        else:
            if not _contains_any(output_text, _TOLERANCE_PATTERNS):
                missing.append("tolerance detail from exemplars")

    if needs_practices:
        for label, patterns in _PRACTICE_SUBTOPICS.items():
            if _contains_any(exemplar_text, patterns) and not _contains_any(output_text, patterns):
                missing.append(f"{label.replace('_', ' ')} practice from exemplars")

    return ValidationResult(ok=(len(missing) == 0), missing=missing)
