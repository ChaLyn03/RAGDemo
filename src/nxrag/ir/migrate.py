"""IR migration helpers."""

from __future__ import annotations

from nxrag.ir.schema_v1 import Document


def migrate_v1_to_v1(document: Document) -> Document:
    """Placeholder migration that returns the document unchanged."""
    return document
