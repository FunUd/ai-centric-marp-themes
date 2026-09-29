#!/usr/bin/env python3
"""print-engine-path.py — Print the absolute path to the vendored diagram engine.

Skills get installed to different locations depending on the agent
(`~/.claude/skills/`, `~/.cursor/`, `.github/skills/` inside a checkout, ...), so
no hard-coded relative path can be correct everywhere. Run this once per session
and reuse the result:

    ENGINE=$(python <skill-dir>/scripts/print-engine-path.py)
    python "$ENGINE/render-slide-diagram.py" -i ... -o ...

Exits 0 and prints one line on success, 1 with a diagnostic on failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VENDOR_DIR = SCRIPT_DIR.parent / "vendor"
RENDERER = VENDOR_DIR / "render-slide-diagram.py"


def main() -> int:
    if not RENDERER.is_file():
        print(
            f"[ERROR] vendored renderer missing: {RENDERER}\n"
            f"        The skill installation is incomplete. Re-sync it from\n"
            f"        ai-centric-marp-themes:  python scripts/sync-skills.py",
            file=sys.stderr,
        )
        return 1
    print(VENDOR_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
