"""Rate limit utilities."""

from __future__ import annotations

import time
from contextlib import contextmanager


def sleep_seconds(seconds: float) -> None:
    time.sleep(seconds)


@contextmanager
def rate_limit(seconds: float):
    yield
    sleep_seconds(seconds)
