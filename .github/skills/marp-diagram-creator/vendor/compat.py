"""compat.py — Windows console encoding guard (single source of truth).

Windows consoles default to cp932, which cannot encode Japanese text, emoji
progress output, or non-ASCII file names. Every CLI in this repository must
force UTF-8 on stdout/stderr instead of carrying its own copy of the
try/except. Import and call once:

    from compat import ensure_utf8_stdio
    ensure_utf8_stdio()

Best-effort by design: streams replaced by a test harness (or pipes that
cannot be reconfigured) are skipped silently. ``errors="replace"`` keeps
output flowing rather than crashing mid-run; it can mask mojibake, so prefer
fixing the emitter over widening this guard.
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
