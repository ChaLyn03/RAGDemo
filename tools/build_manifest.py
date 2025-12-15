"""CLI helper to build corpus manifest."""

from __future__ import annotations

from nxrag.corpus.manifest.build import build_manifest


def main(corpus_root: str) -> None:
    manifest = build_manifest(corpus_root)
    for entry in manifest:
        print(entry.path)
