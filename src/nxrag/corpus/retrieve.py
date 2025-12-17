"""Deterministic corpus retrieval (MVP).

- selects 1 template
- selects up to N exemplars
- selects 1 style rules doc
- optionally selects 1 glossary doc
- returns concatenated context text + retrieval log

Improvements in this version:
- section headers use paths relative to the repo root (or corpus root fallback)
- retrieval log includes missing/empty directories for clarity
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _list_md(dir_path: Path) -> list[Path]:
    if not dir_path.exists():
        return []
    return sorted([p for p in dir_path.glob("*.md") if p.is_file()])


def _relpath(p: Path, repo_root: Path, corpus_root: Path) -> str:
    """Prefer repo-relative paths (e.g., assets/...), else corpus-relative, else absolute."""
    try:
        return p.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        try:
            return p.resolve().relative_to(corpus_root.resolve()).as_posix()
        except Exception:
            return p.resolve().as_posix()


def retrieve_context(
    corpus_root: Path,
    *,
    repo_root: Path | None = None,
    max_exemplars: int = 2,
    max_chars_per_doc: int = 2000,
) -> tuple[str, str, dict[str, Any]]:
    """Return (context_text, exemplar_text, retrieval_log).

    corpus_root should be: assets/corpus
    containing subfolders: templates/, exemplars/, style_rules/, glossary/
    """
    corpus_root = corpus_root.resolve()
    repo_root = (repo_root or Path.cwd()).resolve()

    templates_dir = corpus_root / "templates"
    exemplars_dir = corpus_root / "exemplars"
    style_rules_dir = corpus_root / "style_rules"
    glossary_dir = corpus_root / "glossary"

    templates = _list_md(templates_dir)
    exemplars = _list_md(exemplars_dir)
    style_rules = _list_md(style_rules_dir)
    glossaries = _list_md(glossary_dir)

    selected_template = templates[0] if templates else None
    selected_exemplars = exemplars[: max_exemplars if max_exemplars > 0 else 0]
    selected_style = style_rules[0] if style_rules else None
    selected_glossary = glossaries[0] if glossaries else None

    sections: list[str] = []
    exemplar_sections: list[str] = []
    files_used: list[str] = []

    def add_section(title: str, p: Path | None) -> None:
        nonlocal sections, files_used
        if p is None:
            return
        rel = _relpath(p, repo_root=repo_root, corpus_root=corpus_root)
        text = _read_text(p).strip()
        if max_chars_per_doc and len(text) > max_chars_per_doc:
            text = text[:max_chars_per_doc].rstrip() + "\n\n[TRUNCATED]"
        block = f"### {title}: {rel}\n\n{text}"
        if title.startswith("EXEMPLAR"):
            exemplar_sections.append(block)
        else:
            sections.append(block)
        files_used.append(rel)

    add_section("TEMPLATE", selected_template)
    for i, ex in enumerate(selected_exemplars, start=1):
        add_section(f"EXEMPLAR {i}", ex)
    add_section("STYLE RULES", selected_style)
    add_section("GLOSSARY", selected_glossary)

    context_text = "\n\n---\n\n".join(sections) if sections else "- No template/style/glossary retrieved."
    exemplar_text = "\n\n---\n\n".join(exemplar_sections) if exemplar_sections else "- No exemplars retrieved."

    retrieval_log: dict[str, Any] = {
        "retriever": "static_v1",
        "corpus_root": _relpath(corpus_root, repo_root=repo_root, corpus_root=corpus_root),
        "dirs": {
            "templates": _relpath(templates_dir, repo_root=repo_root, corpus_root=corpus_root),
            "exemplars": _relpath(exemplars_dir, repo_root=repo_root, corpus_root=corpus_root),
            "style_rules": _relpath(style_rules_dir, repo_root=repo_root, corpus_root=corpus_root),
            "glossary": _relpath(glossary_dir, repo_root=repo_root, corpus_root=corpus_root),
        },
        "selected": {
            "template": _relpath(selected_template, repo_root, corpus_root) if selected_template else None,
            "exemplars": [_relpath(p, repo_root, corpus_root) for p in selected_exemplars],
            "style_rules": _relpath(selected_style, repo_root, corpus_root) if selected_style else None,
            "glossary": _relpath(selected_glossary, repo_root, corpus_root) if selected_glossary else None,
        },
        "files_used": files_used,
        "counts": {
            "templates": len(templates),
            "exemplars": len(exemplars),
            "style_rules": len(style_rules),
            "glossary": len(glossaries),
        },
        "limits": {
            "max_exemplars": max_exemplars,
            "max_chars_per_doc": max_chars_per_doc,
        },
        "notes": "Deterministic retrieval (first files by sorted name). Replace with vector/BM25 later.",
    }

    return context_text, exemplar_text, retrieval_log
