"""NX Open Python input utilities.

Iteration 4:
- Heuristic parser for real NXOpen Python scripts (line-based, no AST required).
- Extracts units, part name, materials, tolerances, features, and simple parameters with evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


# ----------------------------
# Regex patterns (heuristic)
# ----------------------------

_IMPORT_NXOPEN = re.compile(r"^\s*(import\s+NXOpen|from\s+NXOpen\b)", re.IGNORECASE | re.MULTILINE)

_UNITS_MM = re.compile(r"\b(Millimeters|Millimetres|mm)\b", re.IGNORECASE)
_UNITS_IN = re.compile(r"\b(Inches|inch|in)\b", re.IGNORECASE)

# Often appears as NXOpen.Part.Units.Millimeters / Inches
_UNITS_ENUM_MM = re.compile(r"NXOpen\.\w*\.Units\.(Millimeters|Millimetres)\b", re.IGNORECASE)
_UNITS_ENUM_IN = re.compile(r"NXOpen\.\w*\.Units\.Inches\b", re.IGNORECASE)

# Part name patterns (best effort; NXOpen scripts vary a lot)
_PARTNAME_SET = re.compile(r"\b(SetPartName|SetName)\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
_PARTNAME_COMMENT = re.compile(r"^\s*#\s*Part\s*[:=]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)

# Material patterns (common: library name strings, or “6061-T6” in comments/strings)
_MATERIAL = re.compile(
    r"\b(6061[-\s]?T6|7075[-\s]?T6|stainless\s+steel|steel|aluminum|aluminium|titanium|inconel)\b",
    re.IGNORECASE,
)
_MATERIAL_LOAD = re.compile(r"(LoadFromLibrary|FindMaterial|AssignMaterial)\s*\(", re.IGNORECASE)

# Tolerance patterns (strings/comments ±0.05 mm, +0.1/-0.0, etc.)
_TOL_PM = re.compile(r"±\s*\d+(?:\.\d+)?\s*(?:mm|in)?\b", re.IGNORECASE)
_TOL_PLUS_MINUS = re.compile(r"\+\s*\d+(?:\.\d+)?\s*/\s*-\s*\d+(?:\.\d+)?\s*(?:mm|in)?\b", re.IGNORECASE)
_TOL_API = re.compile(r"\b(Tolerance|PlusMinus|SetTolerance|ToleranceType)\b", re.IGNORECASE)

# Feature builder detection (NXOpen.Features.*Builder)
_FEATURE_BUILDERS: dict[str, re.Pattern[str]] = {
    "hole": re.compile(r"\b(CreateHoleBuilder|HoleBuilder)\b"),
    "fillet": re.compile(r"\b(CreateEdgeBlendBuilder|EdgeBlendBuilder)\b"),
    "chamfer": re.compile(r"\b(CreateChamferBuilder|ChamferBuilder)\b"),
    "block": re.compile(r"\b(CreateBlockFeatureBuilder|BlockFeatureBuilder|CreateBlockBuilder)\b"),
    "extrude": re.compile(r"\b(CreateExtrudeBuilder|ExtrudeBuilder)\b"),
    "revolve": re.compile(r"\b(CreateRevolveBuilder|RevolveBuilder)\b"),
    "sketch": re.compile(r"\b(CreateSketch|SketchBuilder)\b"),
    "pocket": re.compile(r"\b(CreatePocketBuilder|PocketBuilder)\b"),
    "pattern": re.compile(r"\b(CreatePatternFeatureBuilder|PatternFeatureBuilder)\b"),
}

# Parameter-ish assignments (very heuristic; catches common .Diameter.RightHandSide = "10")
_PARAM_ASSIGN = re.compile(
    r"""(?P<lhs>\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*){1,6})\s*=\s*(?P<rhs>["'][^"']+["']|\d+(?:\.\d+)?)""",
    re.VERBOSE,
)


@dataclass
class LineEvidence:
    line_no: int
    text: str

    def as_str(self) -> str:
        # stable, human-readable evidence
        return f"L{self.line_no}: {self.text}".strip()


def looks_like_nxopen_python(text: str) -> bool:
    return _IMPORT_NXOPEN.search(text or "") is not None


def _iter_lines(text: str) -> Iterable[tuple[int, str]]:
    for i, line in enumerate((text or "").splitlines(), start=1):
        yield i, line.rstrip("\n")


def _detect_units(text: str) -> str | None:
    if _UNITS_ENUM_MM.search(text) or re.search(r"\bPartUnits\s*=\s*.*Millimeters\b", text, re.IGNORECASE):
        return "mm"
    if _UNITS_ENUM_IN.search(text) or re.search(r"\bPartUnits\s*=\s*.*Inches\b", text, re.IGNORECASE):
        return "in"

    # fallback: plain tokens (lower confidence)
    if _UNITS_MM.search(text):
        return "mm"
    if _UNITS_IN.search(text):
        return "in"
    return None


def _detect_part_name(text: str, *, source_path: str | None = None) -> tuple[str | None, str | None]:
    # 1) explicit setter
    m = _PARTNAME_SET.search(text or "")
    if m:
        return m.group(2).strip(), f"call:{m.group(1)}(...)"

    # 2) comment convention
    m2 = _PARTNAME_COMMENT.search(text or "")
    if m2:
        return m2.group(1).strip(), "comment:# Part: ..."

    # 3) file stem fallback
    if source_path:
        try:
            p = Path(source_path)
            return p.stem, "fallback:file_stem"
        except Exception:
            pass

    return None, None


def parse_nxopen_python(text: str, *, source_path: str | None = None) -> dict[str, Any]:
    """Return extracted signals from an NXOpen Python script.

    Output keys:
      units, part_name, part_name_source, features[], materials[], tolerances[], parameters[]
    Each list entry includes an evidence string with line number.
    """
    units = _detect_units(text or "")
    part_name, part_name_source = _detect_part_name(text or "", source_path=source_path)

    features: list[dict[str, str]] = []
    materials: list[dict[str, str]] = []
    tolerances: list[dict[str, str]] = []
    parameters: list[dict[str, str]] = []

    # Feature detection: line-based builder hits
    for ln, line in _iter_lines(text):
        # Skip empty lines fast
        if not line.strip():
            continue

        # features
        for kind, rx in _FEATURE_BUILDERS.items():
            if rx.search(line):
                features.append({"kind": kind, "evidence": LineEvidence(ln, line.strip()).as_str()})
                break

        # materials
        if _MATERIAL.search(line) or _MATERIAL_LOAD.search(line):
            mm = _MATERIAL.search(line)
            val = mm.group(0) if mm else "material_api_call"
            materials.append({"value": val, "evidence": LineEvidence(ln, line.strip()).as_str()})

        # tolerances
        if _TOL_PM.search(line) or _TOL_PLUS_MINUS.search(line) or _TOL_API.search(line):
            mpm = _TOL_PM.search(line)
            mpl = _TOL_PLUS_MINUS.search(line)
            val = (mpm.group(0) if mpm else (mpl.group(0) if mpl else "tolerance_api_usage"))
            tolerances.append({"value": val, "evidence": LineEvidence(ln, line.strip()).as_str()})

        # parameters (best effort)
        ma = _PARAM_ASSIGN.search(line)
        if ma:
            lhs = ma.group("lhs")
            rhs = ma.group("rhs").strip().strip("'\"")
            # Filter out trivial assignments (common noise); keep when lhs suggests geometry/dimensioning
            if any(tok in lhs.lower() for tok in ("diam", "radius", "length", "width", "height", "thick", "tol", "angle")):
                parameters.append(
                    {
                        "name": lhs,
                        "value": rhs,
                        "evidence": LineEvidence(ln, line.strip()).as_str(),
                    }
                )

    return {
        "units": units,
        "part_name": part_name,
        "part_name_source": part_name_source,
        "features": features,
        "materials": materials,
        "tolerances": tolerances,
        "parameters": parameters,
    }
