"""
Timed step lines for Colab notebooks (stdout + optional logger).

- ``GOVERNANCE_STEP_TIMING`` (default on) — ``▶`` / ``✓`` with elapsed seconds
- ``GOVERNANCE_STEP_TIMESTAMPS`` (default on) — ``HH:MM:SS`` prefix on each line
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator, Optional


def step_timing_enabled() -> bool:
    return os.environ.get("GOVERNANCE_STEP_TIMING", "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )


def wall_clock_enabled() -> bool:
    return os.environ.get("GOVERNANCE_STEP_TIMESTAMPS", "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )


def wall_clock_prefix() -> str:
    if wall_clock_enabled():
        return datetime.now().strftime("%H:%M:%S ")
    return ""


def _emit(
    msg: str,
    *,
    prefix: str,
    logger: Optional[logging.Logger],
) -> None:
    line = f"{prefix}{wall_clock_prefix()}{msg}"
    print(line, flush=True)
    if logger is not None:
        logger.info(line)


def log_line(
    msg: str,
    *,
    prefix: str = "  ",
    logger: Optional[logging.Logger] = None,
) -> None:
    """Print one line with optional wall-clock prefix (and mirror to ``logger``)."""
    _emit(msg, prefix=prefix, logger=logger)


@contextmanager
def timed_step(
    label: str,
    *,
    prefix: str = "  ",
    logger: Optional[logging.Logger] = None,
) -> Iterator[None]:
    """Print ``▶ label …`` then ``✓ label — N.Ns`` (and mirror to ``logger`` if set)."""
    if not step_timing_enabled():
        yield
        return
    t0 = time.perf_counter()
    _emit(f"▶ {label} …", prefix=prefix, logger=logger)
    try:
        yield
    finally:
        elapsed = time.perf_counter() - t0
        _emit(f"✓ {label} — {format_elapsed(elapsed)}", prefix=prefix, logger=logger)


def format_elapsed(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    return f"{int(seconds // 60)}m {seconds % 60:.0f}s"
