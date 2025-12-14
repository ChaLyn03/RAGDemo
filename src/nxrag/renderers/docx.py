"""Placeholder docx renderer."""

from __future__ import annotations

from nxrag.ir.schema_v1 import Document


def render_document(document: Document) -> str:
    """Simulate rendering to docx by returning a status string."""
    return f"docx-rendered:{document.id}"
