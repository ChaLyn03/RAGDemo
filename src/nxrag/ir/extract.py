"""IR extraction v1 (heuristic).

This module extracts conservative facts from:
- plain text requests
- NX Open Python-ish text blobs

Design principles:
- Best-effort extraction; never invent values.
- Keep evidence small and local: store matched snippets.
- Prefer "unknown" over guessing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable, Optional


# ----------------------------
# Data model (IR v1)
# ----------------------------

@dataclass
class IRSource:
    type: str
    path: str


@dataclass
class IRPart:
    name: Optional[str] = None
    units: Optional[str] = None  # "mm" | "in" | None


@dataclass
class IRMaterial:
    value: str
    evidence: str


@dataclass
class IRTolerance:
    value: str
    evidence: str


@dataclass
class IRFeature:
    kind: str
    evidence: str


@dataclass
class IRv1:
    ir_version: str
    source: IRSource
    part: IRPart
    materials: list[IRMaterial]
    tolerances: list[IRTolerance]
    features: list[IRFeature]
    parameters: list[dict[str, Any]]
    evidence: dict[str, Any]


# ----------------------------
# Regex helpers
# ----------------------------

_RE_WS = re.compile(r"\s+")
_RE_UNITS_MM = re.compile(r"\b(mm|millimet(er|re)s?)\b", re.IGNORECASE)
_RE_UNITS_IN = re.compile(r"\b(inches|inch|in)\b", re.IGNORECASE)

# Common tolerance patterns in text:
# - ±0.05 mm
# - +/- 0.05 mm
# - + / - 0.05 mm
_RE_TOL_PM = re.compile(r"(±\s*\d+(?:\.\d+)?\s*(?:mm|in)?)", re.IGNORECASE)
_RE_TOL_PLUS_MINUS = re.compile(
    r"(\+\/-\s*\d+(?:\.\d+)?\s*(?:mm|in)?)", re.IGNORECASE
)
_RE_TOL_SPACED = re.compile(
    r"(\+\s*/\s*-\s*\d+(?:\.\d+)?\s*(?:mm|in)?)", re.IGNORECASE
)

# Materials: conservative list (extend as needed)
# We only extract if one of these tokens appears.
_MATERIAL_KEYWORDS = [
    r"\b6061[-\s]?t6\b",
    r"\b7075[-\s]?t6\b",
    r"\baluminum\b",
    r"\baluminium\b",
    r"\bstainless steel\b",
    r"\bcarbon steel\b",
    r"\btitanium\b",
    r"\binconel\b",
    r"\bpolycarbonate\b",
    r"\babs\b",
    r"\bnylon\b",
    r"\bdelrin\b",
    r"\bacetal\b",
]
_RE_MATERIALS = [re.compile(p, re.IGNORECASE) for p in _MATERIAL_KEYWORDS]

# "Feature" keywords (very best-effort)
_FEATURE_PATTERNS = {
    "hole": re.compile(r"\bhole(s)?\b|\bdrill(ed)?\b", re.IGNORECASE),
    "fillet": re.compile(r"\bfillet(s)?\b|\bracelet(s)?\b", re.IGNORECASE),
    "chamfer": re.compile(r"\bchamfer(s)?\b", re.IGNORECASE),
    "slot": re.compile(r"\bslot(s)?\b", re.IGNORECASE),
    "pocket": re.compile(r"\bpocket(s)?\b", re.IGNORECASE),
    "boss": re.compile(r"\bboss(es)?\b", re.IGNORECASE),
    "thread": re.compile(r"\bthread(ed|ing)?\b|\bM\d+\b", re.IGNORECASE),
    "mounting_interface": re.compile(r"\bmount(ing)? interface\b|\bmounting\b", re.IGNORECASE),
    "vent": re.compile(r"\bvent(ing)?\b|\bslot(s)? for thermal\b", re.IGNORECASE),
    "seal": re.compile(r"\bseal(ing)?\b|\bgasket(s)?\b|\bo-?ring(s)?\b", re.IGNORECASE),
    "fastener": re.compile(r"\bfastener(s)?\b|\bscrew(s)?\b|\bbolt(s)?\b", re.IGNORECASE),
}

# NX Open-ish signals (optional use)
_RE_NX_CALL = re.compile(r"\b(nxopen|NXOpen)\b", re.IGNORECASE)
_RE_NX_FEATURE_HINT = re.compile(r"\b(Create|Add|Insert)\w*\b", re.IGNORECASE)


def _norm_line(s: str) -> str:
    return _RE_WS.sub(" ", s).strip()


def _first_nonempty_line(text: str) -> Optional[str]:
    for raw in text.splitlines():
        line = raw.strip()
        if line:
            return line
    return None


def _detect_units(text: str) -> Optional[str]:
    # Preference: explicit "mm" mention beats ambiguous "in" token.
    if _RE_UNITS_MM.search(text):
        return "mm"
    # "in" is ambiguous (english preposition), so require stronger signals:
    if re.search(r"\b(inch|inches)\b", text, flags=re.IGNORECASE):
        return "in"
    # If NXOpen code contains Unit enums, add rules here later.
    return None


def _extract_tolerances(text: str) -> list[IRTolerance]:
    out: list[IRTolerance] = []
    seen: set[str] = set()

    for rx in (_RE_TOL_PM, _RE_TOL_PLUS_MINUS, _RE_TOL_SPACED):
        for m in rx.finditer(text):
            val = _norm_line(m.group(1))
            if val.lower() in seen:
                continue
            seen.add(val.lower())
            # Evidence: capture a small window around the match for traceability
            start = max(0, m.start() - 60)
            end = min(len(text), m.end() + 60)
            ev = _norm_line(text[start:end])
            out.append(IRTolerance(value=val, evidence=ev))

    return out


def _extract_materials(text: str) -> list[IRMaterial]:
    out: list[IRMaterial] = []
    seen: set[str] = set()

    for rx in _RE_MATERIALS:
        for m in rx.finditer(text):
            val = _norm_line(m.group(0))
            key = val.lower()
            if key in seen:
                continue
            seen.add(key)

            start = max(0, m.start() - 60)
            end = min(len(text), m.end() + 60)
            ev = _norm_line(text[start:end])
            out.append(IRMaterial(value=val, evidence=ev))

    return out


def _extract_features(text: str) -> list[IRFeature]:
    out: list[IRFeature] = []
    for kind, rx in _FEATURE_PATTERNS.items():
        m = rx.search(text)
        if not m:
            continue
        start = max(0, m.start() - 60)
        end = min(len(text), m.end() + 60)
        ev = _norm_line(text[start:end])
        out.append(IRFeature(kind=kind, evidence=ev))
    return out


def _best_effort_part_name(text: str, *, filename_hint: str | None = None) -> Optional[str]:
    # 1) If the first non-empty line looks like a title (short), use it.
    first = _first_nonempty_line(text)
    if first:
        # Heuristic: short-ish line, not a full sentence.
        if len(first) <= 80 and not first.endswith("."):
            return first.strip()

    # 2) If filename hint exists, use stem in a readable way.
    if filename_hint:
        stem = Path(filename_hint).stem
        # Convert snake_case / kebab-case to title case
        candidate = re.sub(r"[_-]+", " ", stem).strip()
        if candidate:
            return candidate.title()

    return None


def extract_ir(
    input_text: str,
    *,
    source_path: str,
    source_type: str = "nxopen_python_text",
) -> dict[str, Any]:
    """Return IR as a JSON-serializable dict."""
    part_name = _best_effort_part_name(input_text, filename_hint=source_path)
    units = _detect_units(input_text)

    materials = _extract_materials(input_text)
    tolerances = _extract_tolerances(input_text)

    # Feature extraction: try from text; if NX code is present, still ok (heuristics).
    features = _extract_features(input_text)

    # Optional flags about what we think the input is
    looks_like_nx = bool(_RE_NX_CALL.search(input_text) or _RE_NX_FEATURE_HINT.search(input_text))

    ir = IRv1(
        ir_version="v1",
        source=IRSource(type=source_type, path=source_path),
        part=IRPart(name=part_name, units=units),
        materials=materials,
        tolerances=tolerances,
        features=features,
        parameters=[],
        evidence={
            "looks_like_nxopen": looks_like_nx,
            "notes": "IR extraction v1 is heuristic; values are extracted only if explicitly present in input.",
        },
    )

    # Convert dataclasses to plain dicts
    return asdict(ir)


def render_ir_summary(ir: dict[str, Any]) -> str:
    """Human-readable summary for quick inspection."""
    part = ir.get("part", {}) or {}
    mats = ir.get("materials", []) or []
    tols = ir.get("tolerances", []) or []
    feats = ir.get("features", []) or []

    lines: list[str] = []
    lines.append("IR SUMMARY (v1)")
    lines.append("")
    lines.append(f"Part name: {part.get('name') or 'Not detected'}")
    lines.append(f"Units: {part.get('units') or 'Not detected'}")
    lines.append("")

    lines.append("Materials:")
    if mats:
        for m in mats:
            lines.append(f"- {m.get('value')}  [evidence: {m.get('evidence')}]")
    else:
        lines.append("- None detected")
    lines.append("")

    lines.append("Tolerances:")
    if tols:
        for t in tols:
            lines.append(f"- {t.get('value')}  [evidence: {t.get('evidence')}]")
    else:
        lines.append("- None detected")
    lines.append("")

    lines.append("Features (best-effort):")
    if feats:
        for f in feats:
            lines.append(f"- {f.get('kind')}  [evidence: {f.get('evidence')}]")
    else:
        lines.append("- None detected")

    lines.append("")
    return "\n".join(lines)
