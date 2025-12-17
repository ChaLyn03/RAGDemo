from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import Iterable


@dataclass
class PackedPrompt:
    system: str
    user: str
    exemplar_text: str


def _read(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def _render_block(title: str, path: str | Path) -> str:
    return f"### {title}: {path}\n\n{_read(path)}\n\n---\n"


def pack_part_description_prompt(
    *,
    system_prompt_path: str | Path,
    user_prompt_path: str | Path,
    request_text: str,
    ir_json_text: str,
    retrieved: dict,
) -> PackedPrompt:
    system = _read(system_prompt_path)
    template = _read(user_prompt_path)

    blocks: list[str] = []

    # Template
    if retrieved["selected"].get("template"):
        blocks.append(_render_block(
            "TEMPLATE", retrieved["selected"]["template"]
        ))

    # Exemplars (CRITICAL)
    for ex in retrieved["selected"].get("exemplars", []):
        blocks.append(_render_block("EXEMPLAR", ex))

    # Style rules
    if retrieved["selected"].get("style_rules"):
        blocks.append(_render_block(
            "STYLE RULES", retrieved["selected"]["style_rules"]
        ))

    # Glossary
    if retrieved["selected"].get("glossary"):
        blocks.append(_render_block(
            "GLOSSARY", retrieved["selected"]["glossary"]
        ))

    context = "\n".join(blocks).strip()

    user = (
        template
        .replace("{{request}}", request_text.strip())
        .replace("{{ir_json}}", ir_json_text.strip())
        .replace("{{context}}", context)
    ).strip()

    return PackedPrompt(
        system=system,
        user=user,
        exemplar_text=context,  # SAME TEXT validator sees
    )
