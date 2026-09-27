#!/usr/bin/env python3
"""check-class-docs.py — Verify docs/classes.md documents the theme class system.

The class reference promises "All themes share a unified class system", but the promise
was never checked. It had drifted in both directions:

- **Undocumented**: 35 user-facing classes (``text-accent``, ``badge``,
  ``quote-large``, ``align-*``, ``bg-*``, ``section-number``, ...) were
  implemented in the CSS but absent from the reference, so users could not
  discover them.
- **Overstated**: the reference listed classes as available everywhere when
  specific themes lacked them (``v-middle`` missing from nebula-glass and
  slate-minimal, ``pagination-left`` missing from nebula-glass,
  ``text-left/center/right`` missing from slate-minimal).

This checker treats ``themes/*.css`` as the authority for what exists, and the
docs/classes.md as the documentation of it. It never rewrites prose; it reports the
specific classes involved so a human decides where each one belongs.

Usage:
    python scripts/diagrams/check-class-docs.py
    python scripts/diagrams/check-class-docs.py --list-undocumented
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import theme_classes  # noqa: E402
from compat import ensure_utf8_stdio  # noqa: E402

ROOT_DIR = theme_classes.ROOT_DIR
CLASSES_DOC = ROOT_DIR / "docs" / "classes.md"

# Classes that exist in the CSS but are structural rather than user-facing.
# Either Marp/Pygments internals, or per-theme child selectors that only make
# sense inside a specific layout (e.g. `section.timeline ol li::marker`).
INTERNAL_CLASSES = frozenset({
    # Marp / Pygments code highlighting
    *(f"hljs-{name}" for name in (
        "addition", "attr", "attribute", "built_in", "bullet", "class", "comment",
        "deletion", "keyword", "literal", "name", "number", "quote", "regexp",
        "selector-tag", "string", "symbol", "tag", "title", "type",
    )),
    # structural child elements the layouts require
    "columns", "col", "cell", "grid", "card", "content",
    "profile-layout", "profile-image", "profile-content",
    # callout/badge colour modifiers, documented as prose ("types: blue, green,
    # orange, red") rather than as standalone class names
    "blue", "green", "orange", "red",
    # Prism-only gradient text tints, documented in the Components table
    "cyan", "violet", "rose", "magenta",
    # token values, not selectors
    "ink", "org", "w3", "ttf", "side", "meta", "subtitle",
})


_FENCE_RE = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.S | re.M)


def readme_backticked_classes(text: str) -> set[str]:
    """Class-like names the reference mentions in inline code spans.

    Two forms count as documented:
    - a bare identifier: `` `cols-2` ``
    - a class inside a code span: `` `<div class="callout blue">` ``

    Fenced blocks are stripped first: their ``` fences would otherwise pair up
    with the inline backticks and scramble every span in the document.
    """
    prose = _FENCE_RE.sub("", text)
    found: set[str] = set()
    for span in re.findall(r"`([^`\n]+)`", prose):
        stripped = span.strip()
        if " " not in stripped:
            found |= set(re.findall(r"\b([a-z][a-z0-9_-]*)\b", stripped))
        for attr in re.findall(r'class="([^"]+)"', span):
            found |= set(re.findall(r"\b([a-z][a-z0-9_-]*)\b", attr))
    # `*(Theme)*` qualifiers are prose, never classes.
    found -= set(re.findall(r"\*\(([^)]*)\)\*", prose))
    return found


def readme_documented_table_classes(text: str) -> set[str]:
    """Classes listed in the Layout / Utility tables of the reference.

    Scoped to the two tables so a class mentioned only in prose does not count
    as documented in the class reference.
    """
    documented: set[str] = set()
    for table in re.findall(r"^###\s+.*?\n\n(\|.*?)\n\n", text, re.S | re.M):
        for row in table.splitlines():
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if not cells or set("".join(cells)) <= set("-: "):
                continue
            for cell in cells:
                # Theme qualifiers look like *(Prism Edge)* and are not classes.
                cell = re.sub(r"\*\([^)]*\)\*", "", cell)
                documented |= readme_backticked_classes(cell)
    return documented


def user_facing_classes() -> set[str]:
    """Slide-level classes plus component classes, minus internals."""
    return (theme_classes.all_section_classes() | theme_classes.all_component_classes()) - INTERNAL_CLASSES


def undocumented(readme_text: str) -> dict[str, list[str]]:
    """Implemented classes the reference never mentions, with the themes providing them."""
    mentioned = readme_backticked_classes(readme_text)
    result: dict[str, list[str]] = {}
    for cls in sorted(user_facing_classes() - mentioned):
        providers = [t for t in theme_classes.THEMES if cls in theme_classes.theme_all_classes(t)]
        result[cls] = providers
    return result


def missing_per_theme(documented: set[str]) -> dict[str, list[str]]:
    """Documented classes a given theme does not implement.

    Not automatically a defect: the reference marks theme-specific classes
    (*(Prism Edge)*). This surfaces the ones nobody claimed, which is the
    actual drift signal.
    """
    result: dict[str, list[str]] = {}
    for theme in theme_classes.THEMES:
        available = theme_classes.theme_all_classes(theme)
        missing = sorted(documented & user_facing_classes() - available)
        if missing:
            result[theme] = missing
    return result


def theme_specific_markers(readme_text: str) -> set[str]:
    """Classes the reference explicitly scopes with a *(Theme)* qualifier.

    A row such as::

        | `text-cyan` | *(Nebula Glass)* accent tints |

    marks its classes as intentionally theme-specific, so a theme lacking them
    is not drift. The marker may appear in any cell of the row.
    Only class-like tokens that actually exist in the CSS are returned, so
    prose words in the same row (e.g. `accent`, `tints`) do not pollute the set.
    """
    scoped: set[str] = set()
    for line in readme_text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        if not re.search(r"\*\([^)]*\)\*", line):
            continue
        scoped |= readme_backticked_classes(line)
    try:
        valid = user_facing_classes() | INTERNAL_CLASSES
    except RuntimeError:
        return scoped
    return scoped & valid


def main() -> int:
    ensure_utf8_stdio()

    parser = argparse.ArgumentParser(description="Check docs/classes.md against the theme class system.")
    parser.add_argument(
        "--list-undocumented",
        action="store_true",
        help="Print every implemented-but-undocumented class (default behaviour).",
    )
    parser.add_argument(
        "--allow-unlisted",
        action="store_true",
        help="Report undocumented classes as warnings and exit 0. Use while "
             "incrementally documenting; CI runs without it.",
    )
    args = parser.parse_args()

    readme_text = CLASSES_DOC.read_text(encoding="utf-8")
    doc_classes = readme_documented_table_classes(readme_text)
    missing_docs = undocumented(readme_text)
    gaps = missing_per_theme(doc_classes)
    scoped = theme_specific_markers(readme_text)

    print(f"docs/classes.md class reference: {len(doc_classes)} classes in the layout/utility tables")
    print(f"CSS inventory:         {len(user_facing_classes())} user-facing classes across {len(theme_classes.THEMES)} themes")

    # --- undocumented classes ------------------------------------------------
    if missing_docs:
        print(f"\n[UNDOCUMENTED] {len(missing_docs)} implemented class(es) absent from the reference:")
        for cls, providers in missing_docs.items():
            where = ", ".join(providers)
            print(f"  - {cls:20} ({where})")
        print(
            "\n  Add each to the Layout Classes, Alignment & Utilities, or Components table,\n"
            "  or add it to INTERNAL_CLASSES in check-class-docs.py if it is structural."
        )
    else:
        print("\n[OK] every user-facing class is mentioned in the reference.")

    # --- per-theme gaps ------------------------------------------------------
    unclaimed = {
        theme: [c for c in missing if c not in scoped]
        for theme, missing in gaps.items()
    }
    unclaimed = {theme: items for theme, items in unclaimed.items() if items}
    if unclaimed:
        print(f"\n[UNSCOPED] documented as universal, but these themes do not implement them:")
        for theme, items in unclaimed.items():
            print(f"  - {theme:16} {', '.join(items)}")
        print(
            "\n  Either implement the class in the theme, or mark it in docs/classes.md with a\n"
            "  *(Theme)* qualifier so users do not rely on it there."
        )
    else:
        print("[OK] every theme gap in the reference is explicitly scoped.")

    hard_fail = bool(missing_docs) or bool(unclaimed)
    if hard_fail and args.allow_unlisted:
        print("\n[WARN] drift present, but --allow-unlisted was passed.")
        return 0
    if hard_fail:
        print(
            f"\nFAILED: {len(missing_docs)} undocumented class(es), "
            f"{sum(len(v) for v in unclaimed.values())} unscoped theme gap(s).",
            file=sys.stderr,
        )
        return 1

    print("\n[OK] docs/classes.md and theme class system are in sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
