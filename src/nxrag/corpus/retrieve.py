"""Lightweight retrieval utilities for the demo pipeline."""

from __future__ import annotations

from typing import Sequence

from nxrag.ir.schema_v1 import Chunk


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in text.replace("\n", " ").split() if token.strip()}


def retrieve_chunks(query: str, corpus: Sequence[Chunk], limit: int = 5) -> list[Chunk]:
    """Return top chunks using simple term overlap scoring."""

    if not corpus:
        return []

    query_terms = _tokenize(query)

    def score(chunk: Chunk) -> int:
        chunk_terms = _tokenize(chunk.content)
        return len(query_terms.intersection(chunk_terms))

    ranked = sorted(corpus, key=score, reverse=True)
    return [chunk for chunk in ranked if score(chunk) > 0][:limit] or ranked[: limit or 1]
