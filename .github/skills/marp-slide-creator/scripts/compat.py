"""compat.py — Windows console encoding guard.

Shipped copy of ``scripts/diagrams/compat.py`` (the single source of truth):
this skill is installed standalone into agent directories, so the guard must
travel with the scripts that call it. ``scripts/sync-skills.py`` copies this
directory as a whole; ``scripts/diagrams/tests/test_compat.py`` fails if this
function drifts from the canonical one.
"""
from __future__ import annotations

import sys


def ensure_utf8_stdio() -> None:
    """Force UTF-8 on stdout/stderr; skip streams that cannot be reconfigured."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
