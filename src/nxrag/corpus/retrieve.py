"""
Deterministic corpus retrieval (static_v1) for MVP.

Returns:
- context_text: TEMPLATE + STYLE RULES + GLOSSARY (authoritative framing)
- approved_defaults_text: EXEMPLARS (defaults/practices the validator enforces)
- retrieval_log: JSON-serializable run log
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Tuple


def _read_text(path: Path, max_chars: int) -> str:
    txt = path.read_text(encoding="utf-8", errors="replace")
    if len(txt) > max_chars:
        txt = txt[:max_chars] + "\n\n[TRUNCATED]\n"
    return txt


def _block(kind: str, path: Path, max_chars: int) -> str:
    body = _read_text(path, max_chars=max_chars).strip()
    return f"### {kind}: {path.as_posix()}\n\n{body}\n\n---\n"


def _first_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    files = sorted([p for p in dir_path.iterdir() if p.is_file()])
    return files[0] if files else None


def _first_n_files(dir_path: Path, n: int) -> list[Path]:
    if not dir_path.exists():
        return []
    files = sorted([p for p in dir_path.iterdir() if p.is_file()])
    return files[:n]


def retrieve_context(
    corpus_root: Path,
    *,
    repo_root: Path,
    max_exemplars: int = 2,
    max_chars_per_doc: int = 2000,
) -> tuple[str, str, dict[str, Any]]:
    """
    Deterministic retrieval:
    - template: first file in templates/
    - exemplars: first N files in exemplars/
    - style_rules: first file in style_rules/
    - glossary: first file in glossary/
    """
    corpus_root = Path(corpus_root)

    templates_dir = corpus_root / "templates"
    exemplars_dir = corpus_root / "exemplars"
    style_dir = corpus_root / "style_rules"
    glossary_dir = corpus_root / "glossary"

    template = _first_file(templates_dir)
    exemplars = _first_n_files(exemplars_dir, max_exemplars)
    style_rules = _first_file(style_dir)
    glossary = _first_file(glossary_dir)

    # Render text blocks
    context_blocks: list[str] = []
    defaults_blocks: list[str] = []

    if template:
        context_blocks.append(_block("TEMPLATE", template, max_chars=max_chars_per_doc))

    # EXEMPLARS go into "approved defaults" so validator and prompt share same string.
    for ex in exemplars:
        defaults_blocks.append(_block("EXEMPLAR", ex, max_chars=max_chars_per_doc))

    if style_rules:
        context_blocks.append(_block("STYLE RULES", style_rules, max_chars=max_chars_per_doc))

    if glossary:
        context_blocks.append(_block("GLOSSARY", glossary, max_chars=max_chars_per_doc))

    context_text = "\n".join(context_blocks).strip()
    approved_defaults_text = "\n".join(defaults_blocks).strip()

    # Log paths relative to repo_root for readability
    def rel(p: Path | None) -> str | None:
        if p is None:
            return None
        try:
            return str(p.relative_to(repo_root))
        except Exception:
            return str(p)

    def rel_list(ps: list[Path]) -> list[str]:
        out: list[str] = []
        for p in ps:
            try:
                out.append(str(p.relative_to(repo_root)))
            except Exception:
                out.append(str(p))
        return out

    files_used: list[str] = []
    if template:
        files_used.append(rel(template) or str(template))
    files_used.extend(rel_list(exemplars))
    if style_rules:
        files_used.append(rel(style_rules) or str(style_rules))
    if glossary:
        files_used.append(rel(glossary) or str(glossary))

    retrieval_log: dict[str, Any] = {
        "retriever": "static_v1",
        "corpus_root": rel(corpus_root) or str(corpus_root),
        "dirs": {
            "templates": rel(templates_dir) or str(templates_dir),
            "exemplars": rel(exemplars_dir) or str(exemplars_dir),
            "style_rules": rel(style_dir) or str(style_dir),
            "glossary": rel(glossary_dir) or str(glossary_dir),
        },
        "selected": {
            "template": rel(template),
            "exemplars": rel_list(exemplars),
            "style_rules": rel(style_rules),
            "glossary": rel(glossary),
        },
        "files_used": files_used,
        "counts": {
            "templates": 1 if template else 0,
            "exemplars": len(exemplars),
            "style_rules": 1 if style_rules else 0,
            "glossary": 1 if glossary else 0,
        },
        "limits": {
            "max_exemplars": max_exemplars,
            "max_chars_per_doc": max_chars_per_doc,
        },
        "notes": "Deterministic retrieval (first files by sorted name). Replace with vector/BM25 later.",
    }

    return context_text, approved_defaults_text, retrieval_log
