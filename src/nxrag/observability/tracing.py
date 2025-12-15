"""Tracing utilities for pipeline steps."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator


def now() -> float:
    return time.perf_counter()


@contextmanager
def timer(label: str) -> Iterator[float]:
    start = now()
    yield start
    duration = now() - start
    print(f"{label} took {duration:.4f}s")
