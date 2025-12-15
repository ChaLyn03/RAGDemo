"""Simple client stub for LLM providers."""

from __future__ import annotations

from dataclasses import dataclass


def call_llm(prompt: str, model: str) -> str:
    """Return a deterministic summary of the prompt for demo purposes."""

    request_section = prompt.split("User request:", maxsplit=1)[-1]
    request_body = request_section.split("Relevant corpus", maxsplit=1)[0].strip()
    key_lines = [line.strip() for line in request_body.splitlines() if line.strip()]

    summary = key_lines[0] if key_lines else prompt[:160]
    return f"{summary} (model={model})"


@dataclass
class LLMClient:
    model: str

    def complete(self, prompt: str) -> str:
        return call_llm(prompt, model=self.model)
