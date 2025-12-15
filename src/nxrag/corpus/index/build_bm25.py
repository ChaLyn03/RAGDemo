"""Stub for building BM25 indexes."""

from __future__ import annotations

from nxrag.ir.schema_v1 import Document


def build_bm25_index(documents: list[Document]) -> dict[str, str]:
    """Return a placeholder BM25 index mapping document IDs to token strings."""
    return {doc.id: "bm25-placeholder" for doc in documents}
