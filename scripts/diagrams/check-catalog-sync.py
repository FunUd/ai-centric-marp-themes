#!/usr/bin/env python3
"""check-catalog-sync.py — Verify the diagram template registry is in sync.

Compares three sources and fails on any mismatch:

1. Templates on disk: ``templates/mermaid/*.mmd``, ``templates/drawio/*.drawio``,
   ``templates/charts|concepts|organization/*.json``
2. ``skills/marp-diagram-creator/references/template-catalog.md``
3. ``docs/diagrams.md`` → Available Templates table

Layout columns are verified too, not just template names: the Verified
Layouts cells in the catalog and the ✅ matrix in ``docs/diagrams.md``
must equal ``check-templates.py::ALLOWED_LAYOUTS`` per template (the
authority — every template renders at ``full``, so each cell must contain
at least ``full``). Previously only names were compared and the layout
columns rotted silently.

Usage:
    python scripts/diagrams/check-catalog-sync.py
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
CATALOG_PATH = ROOT_DIR / "skills" / "marp-diagram-creator" / "references" / "template-catalog.md"
DIAGRAMS_DOC_PATH = ROOT_DIR / "docs" / "diagrams.md"

KNOWN_LAYOUTS = ("full", "col2", "asym", "col3")


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
    errors.extend(check_layout_columns())

    if errors:
        for line in errors:
            print(line)
        print(f"FAILED: {len(errors)} mismatch(es)", file=sys.stderr)
        return 1
    print(f"[OK] {len(on_disk)} templates in sync across disk, template-catalog.md, and docs/diagrams.md.")
    return 0


def _load_allowed_layouts() -> dict[str, tuple[str, ...]]:
    """`check-templates.py::ALLOWED_LAYOUTS`, the layout authority.

    Imported from file so this script keeps working through its own relative
    paths. The module is dropped from `sys.modules` afterwards so repeated
    calls — e.g. under pytest with a monkeypatched `SCRIPT_DIR` — never
    reuse a stale copy.
    """
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    name = "check_templates_layouts"
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / "check-templates.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        return dict(module.ALLOWED_LAYOUTS)
    finally:
        sys.modules.pop(name, None)


def _layout_tokens(cell: str) -> set[str] | None:
    """Normalized layout keys in a table cell, or None when it names none."""
    found = {token.strip().lower() for token in cell.split(",")}
    found = {token for token in found if token in KNOWN_LAYOUTS}
    unknown = {
        token.strip().lower()
        for token in cell.split(",")
        if token.strip() and token.strip().lower() not in KNOWN_LAYOUTS
    }
    if unknown and found:
        raise RuntimeError(f"unknown layout token(s) {sorted(unknown)} in {cell!r}")
    return found or None


def _catalog_layouts(text: str) -> dict[str, set[str]]:
    """Basename -> layouts from the catalog §§1-3 Verified Layouts cells."""
    out: dict[str, set[str]] = {}
    for section in re.split(r"^## \d+\. ", text, flags=re.MULTILINE)[1:4]:
        for line in section.splitlines():
            if not line.startswith("|"):
                continue
            name_match = TEMPLATE_RE.search(line)
            if not name_match:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            for cell in cells:
                if "full" in cell.lower() and name_match.group(0) not in cell:
                    tokens = _layout_tokens(cell)
                    if tokens:
                        out[name_match.group(0)] = tokens
                    break
    return out


def _docs_matrix_layouts(text: str) -> dict[str, set[str]]:
    """Basename -> layouts from the docs ✅ support matrix."""
    lines = text.splitlines()
    header_idx: int | None = None
    columns: list[str] = []
    for index, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`").lower() for cell in line.strip().strip("|").split("|")]
        if set(cells[1:]) == set(KNOWN_LAYOUTS):
            header_idx, columns = index, cells[1:]
            break
    if header_idx is None:
        raise RuntimeError("support matrix header (full/col2/asym/col3) not found")
    out: dict[str, set[str]] = {}
    for line in lines[header_idx + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        name_match = TEMPLATE_RE.search(cells[0])
        if not name_match:
            continue
        out[name_match.group(0)] = {
            layout for layout, cell in zip(columns, cells[1:]) if "✅" in cell
        }
    return out


def check_layout_columns() -> list[str]:
    """Cross-check layout cells against the `ALLOWED_LAYOUTS` authority."""
    try:
        allowed = _load_allowed_layouts()
        by_basename: dict[str, str] = {}
        for rel in allowed:
            base = Path(rel).name
            if base in by_basename:
                raise RuntimeError(f"duplicate template basename {base!r}")
            by_basename[base] = rel
        catalog = _catalog_layouts(CATALOG_PATH.read_text(encoding="utf-8"))
        docs = _docs_matrix_layouts(DIAGRAMS_DOC_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, RuntimeError) as error:
        return [f"[LAYOUT] cannot read layout sources: {error}"]
    errors: list[str] = []
    for base, rel in sorted(by_basename.items()):
        expected = set(allowed[rel])
        for source, found in (("template-catalog.md", catalog.get(base)), ("docs/diagrams.md", docs.get(base))):
            if found is None:
                errors.append(f"[LAYOUT] {base}: no layouts listed in {source}")
            elif found != expected:
                errors.append(
                    f"[LAYOUT] {base}: {source} lists {sorted(found)}, "
                    f"authority is {sorted(expected)}"
                )
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
