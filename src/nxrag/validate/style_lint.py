"""Style/claim lint (MVP).

Goal: prevent the model from adding 'helpful' but unsupported justifications.

Lexical + conservative:
- Flags phrases only if they appear in output and DO NOT appear anywhere in sources_text.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StyleValidation:
    ok: bool
    missing: list[str]


FORBIDDEN_PHRASES = [
    "known for",
    "corrosion resistance",
    "strength and",
    "crucial role",
    "ensures",
    "ensuring",
    "providing",
]


def validate_no_new_claims(*, output_text: str, sources_text: str) -> StyleValidation:
    out_l = (output_text or "").lower()
    src_l = (sources_text or "").lower()

    violations: list[str] = []
    for phrase in FORBIDDEN_PHRASES:
        if phrase in out_l and phrase not in src_l:
            violations.append(f"contains unsupported phrasing: '{phrase}'")

    return StyleValidation(ok=(len(violations) == 0), missing=violations)
