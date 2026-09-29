#!/usr/bin/env python3
"""sync-theme-classes.py — Regenerate the theme class manifest for marp-lint.py.

``marp-lint.py`` is copied standalone into agent directories by
``sync-skills.py`` and cannot import from ``scripts/``. It therefore reads a
generated JSON manifest instead of hard-coding class sets.

This script is the only writer of that manifest. Run it after changing
``theme_classes.py`` or any ``themes/*.css``:

    python scripts/diagrams/sync-theme-classes.py           # rewrite
    python scripts/diagrams/sync-theme-classes.py --check   # fail on drift
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import theme_classes  # noqa: E402
from compat import ensure_utf8_stdio  # noqa: E402


def main() -> int:
    ensure_utf8_stdio()

    parser = argparse.ArgumentParser(description="Sync the theme class manifest used by marp-lint.py.")
    parser.add_argument("--check", action="store_true", help="Fail if the manifest is stale.")
    args = parser.parse_args()

    path = theme_classes.manifest_path()
    payload = json.dumps(theme_classes.build_manifest(), indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not path.exists():
            print(
                f"[DRIFT] {path.name} is missing. Run: python scripts/diagrams/sync-theme-classes.py", file=sys.stderr
            )
            return 1
        current = path.read_text(encoding="utf-8")
        if current != payload:
            print(
                f"[DRIFT] {path.name} is out of sync with theme_classes.py / themes/*.css.\n"
                f"        Run: python scripts/diagrams/sync-theme-classes.py",
                file=sys.stderr,
            )
            return 1
        print(f"[OK] {path.name} is in sync.")
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == payload:
        print(f"[OK] {path.name} already in sync.")
        return 0

    path.write_text(payload, encoding="utf-8")
    print(f"[SYNC] wrote {path.relative_to(theme_classes.ROOT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
