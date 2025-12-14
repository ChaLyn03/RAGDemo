"""Render IR into Markdown."""

from __future__ import annotations

from nxrag.ir.schema_v1 import Document


def render_document(document: Document) -> str:
    lines = [f"# {document.title}"]
    for chunk in document.chunks:
        lines.append(f"\n## {chunk.id}\n{chunk.content}")
    return "\n".join(lines)
