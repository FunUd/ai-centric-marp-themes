#!/usr/bin/env python3
"""check-catalog-sync.py — Verify the diagram template registry is in sync.

Compares three sources and fails on any mismatch:

1. Templates on disk: ``templates/mermaid/*.mmd``, ``templates/drawio/*.drawio``,
   ``templates/charts|concepts|organization/*.json``
2. ``skills/marp-diagram-creator/references/template-catalog.md``
3. ``README.md`` → Available Templates table

Usage:
    python scripts/diagrams/check-catalog-sync.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
CATALOG_PATH = ROOT_DIR / "skills" / "marp-diagram-creator" / "references" / "template-catalog.md"
README_PATH = ROOT_DIR / "README.md"


def templates_on_disk() -> set[str]:
    found: set[str] = set()
    for pattern in ("mermaid/*.mmd", "drawio/*.drawio", "charts/*.json", "concepts/*.json", "organization/*.json"):
        for path in sorted((SCRIPT_DIR / "templates").glob(pattern)):
            found.add(path.name)
    return found


def mentions_in(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"[\w-]+\.(?:mmd|drawio|json)", text))


def main() -> int:
    on_disk = templates_on_disk()
    raw_catalog = mentions_in(CATALOG_PATH)
    raw_readme = mentions_in(README_PATH)

    errors: list[str] = []
    for name in sorted(on_disk - raw_catalog):
        errors.append(f"[CATALOG] template on disk but missing in template-catalog.md: {name}")
    for name in sorted(on_disk - raw_readme):
        errors.append(f"[README] template on disk but missing in README Available Templates: {name}")
    for name in sorted((raw_catalog | raw_readme) - on_disk):
        errors.append(f"[STALE] documented but file does not exist: {name}")

    if errors:
        for line in errors:
            print(line)
        print(f"FAILED: {len(errors)} mismatch(es)", file=sys.stderr)
        return 1
    print(f"[OK] {len(on_disk)} templates in sync across disk, template-catalog.md, and README.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
