"""Schema definitions for version 1 of the IR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class Chunk:
    id: str
    content: str
    metadata: dict[str, str]


def build_chunk(chunk_id: str, content: str, metadata: dict[str, str] | None = None) -> Chunk:
    return Chunk(id=chunk_id, content=content, metadata=metadata or {})


@dataclass
class Document:
    id: str
    title: str
    chunks: Sequence[Chunk]
