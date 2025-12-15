"""Render IR into Markdown."""

from __future__ import annotations

from nxrag.ir.schema_v1 import Document


def render_document(document: Document) -> str:
    lines = [f"# {document.title}"]
    for chunk in document.chunks:
        heading = chunk.metadata.get("section", chunk.id)
        lines.append(f"\n## {heading}\n{chunk.content}")
    return "\n".join(lines)
