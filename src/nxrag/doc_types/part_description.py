"""Part description helpers for the demo pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from nxrag.corpus.ids import chunk_id
from nxrag.ir.evidence import Evidence
from nxrag.ir.schema_v1 import Chunk, Document, build_chunk


@dataclass
class PartSection:
    heading: str
    body: str
    evidence: Sequence[Evidence]


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "part"


def required_sections() -> Sequence[str]:
    return ["Overview", "Recommended approach", "Evidence"]


def assemble_part_description(title: str, request: str, retrieved: Sequence[Chunk], llm_summary: str) -> Document:
    """Build a Markdown-friendly document using retrieved evidence and a generated summary."""

    overview_content = f"{title}\n\n{request.strip()}\n\n{llm_summary.strip()}"

    recommendations_lines = []
    for chunk in retrieved:
        clean = chunk.content.strip().replace("\n", " ")
        recommendations_lines.append(f"- {clean}")
    recommendations = "\n".join(recommendations_lines) or "- No matching corpus passages found."

    evidence_lines = [chunk.metadata.get("source", chunk.id) for chunk in retrieved]
    evidence_body = "\n".join(f"- {line}" for line in evidence_lines) or "- No evidence available."

    sections = [
        build_chunk(
            chunk_id(f"{title}-section", 0, overview_content),
            overview_content,
            {"section": "Overview"},
        ),
        build_chunk(
            chunk_id(f"{title}-section", 1, recommendations),
            recommendations,
            {"section": "Recommended approach"},
        ),
        build_chunk(
            chunk_id(f"{title}-section", 2, evidence_body),
            evidence_body,
            {"section": "Evidence"},
        ),
    ]

    evidence_set = [
        Evidence(chunk_id=chunk.id, start_line=1, end_line=len(chunk.content.splitlines()))
        for chunk in retrieved
    ]

    if evidence_set:
        sections[0].metadata["evidence"] = [e.__dict__ for e in evidence_set]

    return Document(
        id=_slugify(title),
        title=f"Part description: {title}",
        chunks=sections,
    )
