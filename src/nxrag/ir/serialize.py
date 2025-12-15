"""Serialization helpers for IR objects."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from nxrag.ir.schema_v1 import Chunk, Document


def serialize_chunk(chunk: Chunk) -> str:
    ordered = asdict(chunk)
    return json.dumps(ordered, ensure_ascii=False, sort_keys=True, indent=2)


def serialize_document(document: Document) -> str:
    ordered: dict[str, Any] = {
        "id": document.id,
        "title": document.title,
        "chunks": [asdict(chunk) for chunk in document.chunks],
    }
    return json.dumps(ordered, ensure_ascii=False, sort_keys=True, indent=2)
