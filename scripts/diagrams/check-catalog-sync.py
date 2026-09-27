#!/usr/bin/env python3
"""check-catalog-sync.py — Verify the diagram template registry is in sync.

Compares three sources and fails on any mismatch:

1. Templates on disk: ``templates/mermaid/*.mmd``, ``templates/drawio/*.drawio``,
   ``templates/charts|concepts|organization/*.json``
2. ``skills/marp-diagram-creator/references/template-catalog.md``
3. ``docs/diagrams.md`` → Available Templates table

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
DIAGRAMS_DOC_PATH = ROOT_DIR / "docs" / "diagrams.md"


def templates_on_disk() -> set[str]:
    found: set[str] = set()
    seen_basename: dict[str, str] = {}
    for pattern in ("mermaid/*.mmd", "drawio/*.drawio", "charts/*.json", "concepts/*.json", "organization/*.json"):
        for path in sorted((SCRIPT_DIR / "templates").glob(pattern)):
            # Basename is the registry key used by docs/catalog tables.
            # Two different directories must never share one.
            if path.name in seen_basename and seen_basename[path.name] != pattern:
                raise RuntimeError(
                    f"duplicate template basename {path.name!r} in {seen_basename[path.name]} and {pattern}"
                )
            seen_basename[path.name] = pattern
            found.add(path.name)
    return found


TEMPLATE_RE = re.compile(r"[\w-]+\.(?:mmd|drawio|json)")

# docs/diagrams.md mentions JSON files that are not templates
# (`theme-classes.json`, `theme-styles/*.json`), so only the Available
# Templates table is scanned. Anchoring on the heading keeps a new unrelated
# `*.json` mention elsewhere in the doc out of this check.
DOCS_TABLE_HEADING = "### Available Templates"


def mentions_in(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        raise RuntimeError(f"cannot read {path}: {error}") from error
    if path.name == "diagrams.md":
        start = text.find(DOCS_TABLE_HEADING)
        if start == -1:
            return set()
        # The table runs until the next heading of any level.
        rest = text[start + len(DOCS_TABLE_HEADING):]
        end = re.search(r"^#{1,6}\s", rest, re.MULTILINE)
        section = rest[: end.start()] if end else rest
        return set(TEMPLATE_RE.findall(section))
    return set(TEMPLATE_RE.findall(text))


def main() -> int:
    try:
        on_disk = templates_on_disk()
        raw_catalog = mentions_in(CATALOG_PATH)
        raw_readme = mentions_in(DIAGRAMS_DOC_PATH)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"FAILED: cannot read inputs: {error}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for name in sorted(on_disk - raw_catalog):
        errors.append(f"[CATALOG] template on disk but missing in template-catalog.md: {name}")
    for name in sorted(on_disk - raw_readme):
        errors.append(f"[DOCS] template on disk but missing in docs/diagrams.md Available Templates: {name}")
    for name in sorted((raw_catalog | raw_readme) - on_disk):
        errors.append(f"[STALE] documented but file does not exist: {name}")

    if errors:
        for line in errors:
            print(line)
        print(f"FAILED: {len(errors)} mismatch(es)", file=sys.stderr)
        return 1
    print(f"[OK] {len(on_disk)} templates in sync across disk, template-catalog.md, and docs/diagrams.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
