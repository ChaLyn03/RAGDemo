"""LLM client (MVP).

Supports two modes:
- stub (default): deterministic placeholder, no network/API keys required
- openai: real call if OPENAI_API_KEY is set and `openai` python package is installed

Mode is controlled by settings (preferred) or env:
- settings.llm_provider (if present) else env NX_RAG_LLM_PROVIDER else "stub"
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _stub_complete(prompt: str, model: str) -> str:
    head = prompt.strip().replace("\n", " ")
    return (
        "## Overview\n"
        f"Generated stub output for model `{model}` (uses exemplar defaults).\n\n"
        "## Materials & tolerances\n"
        "Recommended default (from exemplar): 6061-T6 aluminum with ±0.05 mm on mounting interface.\n\n"
        "## Vibration reliability practices\n"
        "- Recommended default (from exemplar): Use blue threadlocker on screws.\n"
        "- Recommended default (from exemplar): Apply anti-seize on aluminum interfaces.\n"
        "- Recommended default (from exemplar): Torque M5 screws to 4.5 N·m.\n"
        f"\n\n(Stub preview: {head[:160]}{'...' if len(head) > 160 else ''})\n"
    )


def _openai_complete(prompt: str, model: str, max_tokens: int) -> str:
    """Real OpenAI call (Chat Completions). Requires OPENAI_API_KEY and `openai` package."""
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "OpenAI provider selected but `openai` package is not installed. "
            "Install with: pip install openai"
        ) from e

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OpenAI provider selected but OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    # Minimal, predictable: one user message containing the packed prompt.
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def call_llm(
    prompt: str,
    *,
    model: str,
    max_tokens: int = 800,
    provider: str = "stub",
) -> str:
    provider = (provider or "stub").strip().lower()

    if provider == "stub":
        return _stub_complete(prompt, model=model)

    if provider == "openai":
        return _openai_complete(prompt, model=model, max_tokens=max_tokens)

    raise ValueError(f"Unknown LLM provider: {provider!r} (expected 'stub' or 'openai')")


@dataclass
class LLMClient:
    model: str
    max_tokens: int = 800
    provider: str = "stub"

    def complete(self, prompt: str) -> str:
        return call_llm(
            prompt,
            model=self.model,
            max_tokens=self.max_tokens,
            provider=self.provider,
        )
