"""Checks model outputs against intermediate representation."""

from __future__ import annotations

from nxrag.ir.schema_v1 import Chunk


def check_claims(chunks: list[Chunk]) -> bool:
    """Placeholder consistency check returning True when chunks exist."""
    return bool(chunks)
