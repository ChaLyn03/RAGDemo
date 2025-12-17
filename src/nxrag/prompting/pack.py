"""Prompt packing utilities.

Single source of truth for how prompt placeholders are bound and what the validator sees.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PackedPrompt:
    prompt_text: str
    exemplar_text: str  # must match what validator checks


def pack_part_description_prompt(
    *,
    template_text: str,
    request_text: str,
    facts_text: str,
    approved_defaults_text: str,
    context_text: str,
) -> PackedPrompt:
    """Strict substitution for prompt template placeholders.

    Required placeholders in template:
      {request}, {facts}, {approved_defaults}, {context}
    """
    prompt = (
        template_text.replace("{request}", request_text)
        .replace("{facts}", facts_text)
        .replace("{approved_defaults}", approved_defaults_text)
        .replace("{context}", context_text)
    )

    # The validator must validate against the same exemplar text the model saw.
    return PackedPrompt(prompt_text=prompt, exemplar_text=approved_defaults_text)
