from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackedPrompt:
    system: str
    user: str


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def pack_part_description_prompt(
    *,
    system_prompt_path: str | Path,
    user_prompt_path: str | Path,
    request_text: str,
    ir_json_text: str,
    retrieved_context_text: str,
) -> PackedPrompt:
    system = _read_text(system_prompt_path).strip()
    template = _read_text(user_prompt_path)

    # Keep context as-is. Do not “sanitize” away lines; the validator depends on this.
    user = (
        template.replace("{{request}}", request_text.strip())
        .replace("{{ir_json}}", ir_json_text.strip())
        .replace("{{context}}", retrieved_context_text.strip())
    ).strip()

    return PackedPrompt(system=system, user=user)
