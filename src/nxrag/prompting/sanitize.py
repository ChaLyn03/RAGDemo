"""Prompt sanitation helpers."""

from __future__ import annotations


def strip_trailing_whitespace(prompt: str) -> str:
    return "\n".join(line.rstrip() for line in prompt.splitlines())
