"""IR extraction (v1/v1.1).

Iteration 4:
- Add parsing for real NXOpen Python scripts (heuristic, line-evidence).
- Keep IR conservative: only emit what we can justify from input text/code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from nxrag.inputs.nxopen_python import looks_like_nxopen_python, parse_nxopen_python


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
class IRParameter:
    name: str
    value: str
    evidence: str


def _norm(s: str) -> str:
    return (s or "").strip()


def extract_ir(
    raw_text: str,
    *,
    source_path: str,
    source_type: str,
) -> dict[str, Any]:
    """Extract an intermediate representation from input.

    Supported source_type values (MVP):
      - "nxopen_python_text"  (NXOpen Python script as text)
      - "text"                (plain request text)
    """
    text = raw_text or ""

    ir: dict[str, Any] = {
        "ir_version": "v1",
        "source": {"type": source_type, "path": source_path},
        "part": {"name": None, "units": None},
        "materials": [],
        "tolerances": [],
        "features": [],
        "parameters": [],
        "evidence": {"notes": ""},
    }

    # Treat NXOpen python specially if either:
    # - source_type indicates it, OR
    # - it obviously imports NXOpen
    is_nx = (source_type.lower().startswith("nxopen")) or looks_like_nxopen_python(text)

    if is_nx:
        parsed = parse_nxopen_python(text, source_path=source_path)

        ir["part"]["name"] = parsed.get("part_name")
        ir["part"]["units"] = parsed.get("units")

        for m in parsed.get("materials") or []:
            ir["materials"].append(asdict(IRMaterial(value=_norm(m.get("value")), evidence=_norm(m.get("evidence")))))

        for t in parsed.get("tolerances") or []:
            ir["tolerances"].append(asdict(IRTolerance(value=_norm(t.get("value")), evidence=_norm(t.get("evidence")))))

        for f in parsed.get("features") or []:
            ir["features"].append(asdict(IRFeature(kind=_norm(f.get("kind")), evidence=_norm(f.get("evidence")))))

        for p in parsed.get("parameters") or []:
            ir["parameters"].append(
                asdict(IRParameter(name=_norm(p.get("name")), value=_norm(p.get("value")), evidence=_norm(p.get("evidence"))))
            )

        ir["evidence"]["notes"] = (
            "IR extracted from NXOpen Python using heuristic line-based parser (Iteration 4). "
            "Features/materials/tolerances are best-effort and backed by line evidence."
        )
        return ir

    # Fallback: plain text request (previous behavior, conservative)
    # We only do best-effort part name from first non-empty line.
    first_line = None
    for line in text.splitlines():
        if line.strip():
            first_line = line.strip()
            break

    if first_line:
        ir["part"]["name"] = first_line

    ir["evidence"]["notes"] = (
        "IR extracted from plain text (no NXOpen parser used). "
        "Material/tolerances/features are intentionally not inferred at this stage."
    )
    return ir


def render_ir_summary(ir: dict[str, Any]) -> str:
    part = ir.get("part") or {}
    mats = ir.get("materials") or []
    tols = ir.get("tolerances") or []
    feats = ir.get("features") or []
    params = ir.get("parameters") or []

    lines: list[str] = []
    lines.append(f"IR version: {ir.get('ir_version')}")
    src = ir.get("source") or {}
    lines.append(f"Source: {src.get('type')}  ({src.get('path')})")
    lines.append("")
    lines.append(f"Part name: {part.get('name') or 'Not detected'}")
    lines.append(f"Units: {part.get('units') or 'Not detected'}")
    lines.append("")

    lines.append("Materials:")
    if mats:
        for m in mats:
            lines.append(f"- {m.get('value')}  [{m.get('evidence')}]")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Tolerances:")
    if tols:
        for t in tols:
            lines.append(f"- {t.get('value')}  [{t.get('evidence')}]")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Features:")
    if feats:
        for f in feats:
            lines.append(f"- {f.get('kind')}  [{f.get('evidence')}]")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Parameters:")
    if params:
        for p in params:
            lines.append(f"- {p.get('name')} = {p.get('value')}  [{p.get('evidence')}]")
    else:
        lines.append("- (none)")

    lines.append("")
    ev = ir.get("evidence") or {}
    lines.append(f"Notes: {ev.get('notes') or ''}".strip())

    return "\n".join(lines) + "\n"
