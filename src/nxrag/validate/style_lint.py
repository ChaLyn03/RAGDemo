"""Style linting for generated documents."""

from __future__ import annotations


def lint_heading_levels(markdown: str) -> bool:
    """Return True if headings appear to be formatted."""
    return markdown.startswith("#")
