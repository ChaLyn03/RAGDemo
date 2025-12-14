"""Build search indexes for the corpus."""

from __future__ import annotations

from nxrag.corpus.index.build_bm25 import build_bm25_index
from nxrag.corpus.index.build_vector import build_vector_index
from nxrag.corpus.index.store import save_index
from nxrag.ir.schema_v1 import Document


def main(documents: list[Document]) -> None:
    vector = build_vector_index(documents)
    bm25 = build_bm25_index(documents)
    save_index("vector", vector)
    save_index("bm25", bm25)
