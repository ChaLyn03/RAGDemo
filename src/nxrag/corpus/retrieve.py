"""Hybrid retrieval placeholder implementation."""

from __future__ import annotations

from typing import Sequence

from nxrag.ir.schema_v1 import Chunk


def retrieve_chunks(query: str, corpus: Sequence[Chunk], limit: int = 5) -> list[Chunk]:
    """Return the first N chunks as a stub retrieval result."""
    return list(corpus)[:limit]
