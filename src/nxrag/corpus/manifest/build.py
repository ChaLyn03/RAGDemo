"""Builds a corpus manifest from assets."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from nxrag.corpus.manifest.schema import ManifestEntry


def iter_markdown_files(corpus_root: str | Path) -> Iterable[Path]:
    for path in Path(corpus_root).rglob("*.md"):
        yield path


def build_manifest(corpus_root: str | Path) -> list[ManifestEntry]:
    entries: list[ManifestEntry] = []
    for path in iter_markdown_files(corpus_root):
        heading = path.read_text(encoding="utf-8").splitlines()[0].lstrip("# ") if path.exists() else ""
        tags = [heading] if heading else []
        entries.append(ManifestEntry(path=path, tags=tags))
    return entries
