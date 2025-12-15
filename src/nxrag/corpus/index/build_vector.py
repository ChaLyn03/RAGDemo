"""Stub for building vector indexes."""

from __future__ import annotations

from nxrag.ir.schema_v1 import Document


def build_vector_index(documents: list[Document]) -> dict[str, str]:
    """Return a placeholder vector index mapping document IDs to embeddings."""
    return {doc.id: "embedding-placeholder" for doc in documents}
