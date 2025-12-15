"""Simple client stub for LLM providers."""

from __future__ import annotations

from dataclasses import dataclass


def call_llm(prompt: str, model: str) -> str:
    """Return a placeholder completion."""
    return f"[model={model}] {prompt[:100]}..."


@dataclass
class LLMClient:
    model: str

    def complete(self, prompt: str) -> str:
        return call_llm(prompt, model=self.model)
