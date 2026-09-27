"""theme_classes.py — Single source of truth for theme class semantics.

`themes/*.css` is the authority for *which* classes exist in each theme. This
module adds the semantics the linter needs but CSS cannot express on its own:

- ``CENTERED_CLASSES``   — layouts that centre their content, where a bullet
  list renders badly. Derived from an explicit list plus a CSS assertion, so a
  class cannot be added here without existing in at least one theme.
- ``TITLE_EXEMPT_CLASSES`` — title-only layouts where a generic heading
  ("概要", "Summary") is the intended usage, not a "So What?" failure.
- ``DIAGRAM_LAYOUT_CLASSES`` — layout class -> ``layout_spec`` profile, used to
  budget diagram embed widths.
- ``THEMES`` / ``theme_classes()`` — the inventory parsed from the CSS.

Why this exists: ``marp-lint.py`` previously hard-coded three overlapping class
sets. They disagreed with each other *and* with the CSS, so ``cover-nebula``
(a cover layout, documented in docs/classes.md and used by the skill's own quick
start) produced a false ``WEAK_TITLE`` warning, and ``split-glass`` was treated
as a single column for bullet limits while being a 2-column layout for diagram
widths.

The generated ``skills/marp-slide-creator/scripts/theme-classes.json`` is what
``marp-lint.py`` reads at runtime (it is copied standalone into agent
directories and cannot import from ``scripts/``).
``test_theme_classes.py`` fails if the JSON drifts from this module.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
THEMES_DIR = ROOT_DIR / "themes"

THEMES = (
    "azure-clarity",
    "crimson-clarity",
    "prism-edge",
    "nebula-glass",
    "warm-sunnyday",
    "slate-minimal",
)

# --- semantic sets ----------------------------------------------------------
#
# A class belongs here because of what it *does*, and must exist in the CSS of at
# least one theme. `test_theme_classes.py` enforces both directions.

# Layouts where a bullet list is a design error, whatever the text alignment.
# These are title and single-message slides: they exist to land one idea, so a
# list either renders as centred dots (visually broken) or undercuts the
# message. Centring is the common case, but several themes deliberately
# left-align covers (`slate-minimal`, `cover-diagonal`, `nebula-glass`
# `key-message`), so the rule keys on the layout's *purpose* rather than on a
# CSS property that varies per theme.
#
# `glass-card-layout` is deliberately absent: it centres the slide but the
# inner `.card` inherits the section's left alignment, so a bulleted feature
# list inside it renders correctly (see the nebula-glass sample, slide 2).
LIST_UNSUITABLE_CLASSES = frozenset({
    "align-center",
    "cover",
    "cover-aurora",
    "cover-diagonal",
    "cover-nebula",
    "cover-noir",
    "cover-wave",
    "hero",
    "key-message",
    "title-elegant",
    "title-only",
})

# Layouts where a generic heading is the intended usage: covers carry a product
# or deck name, and title slides exist precisely to state one thing. Exempting
# these from `lint_weak_title` avoids demanding a "So What?" takeaway from a
# slide that has no other content to support one.
TITLE_EXEMPT_CLASSES = frozenset({
    "cover",
    "cover-aurora",
    "cover-diagonal",
    "cover-nebula",
    "cover-noir",
    "cover-wave",
    "glass-card-layout",
    "hero",
    "key-message",
    "title-elegant",
    "title-only",
    "toc",
    "toc-focus",
})

# Layouts where many list items are structural, not a readability problem.
LIST_EXEMPT_CLASSES = frozenset({
    "checklist",
    "steps",
    "timeline",
    "timetable",
    "toc",
    "toc-focus",
})


def _layout_classes() -> dict[str, str]:
    """Class -> layout_spec profile.

    Values come from ``layout_spec.CLASS_TO_LAYOUT`` so diagram width budgets
    have exactly one definition. Re-exported here so consumers of the generated
    manifest do not need to import ``scripts/`` themselves.
    """
    import sys

    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    import layout_spec  # noqa: E402

    return dict(layout_spec.CLASS_TO_LAYOUT)


DIAGRAM_LAYOUT_CLASSES: dict[str, str] = _layout_classes()


# --- CSS inventory ----------------------------------------------------------

_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
_SECTION_CLASS_RE = re.compile(r"section\.([a-zA-Z0-9_-]+)")
# Exclude url(...) contents (font paths, data-URIs) and file extensions —
# otherwise `Poppins-Regular.ttf` becomes a fake "component class".
_URL_RE = re.compile(r"url\([^)]*\)", re.S)
_ANY_CLASS_RE = re.compile(r"\.([a-zA-Z][\w-]*)")


def _strip_comments(css: str) -> str:
    css = _COMMENT_RE.sub("", css)
    return _URL_RE.sub("url()", css)


def theme_section_classes(theme: str) -> set[str]:
    """Slide-level classes implemented by one theme (``section.<class>``)."""
    try:
        css = _strip_comments((THEMES_DIR / f"{theme}.css").read_text(encoding="utf-8"))
    except OSError as error:
        raise RuntimeError(f"cannot read theme CSS for {theme}: {error}") from error
    return set(_SECTION_CLASS_RE.findall(css))


def theme_all_classes(theme: str) -> set[str]:
    """Every class token in one theme, including component classes
    (``callout``, ``badge``, ``text-accent``) that are not slide-level."""
    try:
        css = _strip_comments((THEMES_DIR / f"{theme}.css").read_text(encoding="utf-8"))
    except OSError as error:
        raise RuntimeError(f"cannot read theme CSS for {theme}: {error}") from error
    return set(_ANY_CLASS_RE.findall(css))


def theme_classes() -> dict[str, set[str]]:
    """theme -> slide-level classes."""
    return {theme: theme_section_classes(theme) for theme in THEMES}


def all_section_classes() -> set[str]:
    return set().union(*theme_classes().values())


def all_component_classes() -> set[str]:
    return set().union(*(theme_all_classes(theme) for theme in THEMES))


# --- generated manifest -----------------------------------------------------


def build_manifest() -> dict[str, Any]:
    """The payload written to ``theme-classes.json`` for ``marp-lint.py``."""
    inventory = theme_classes()
    return {
        "themes": list(THEMES),
        "list_unsuitable": sorted(LIST_UNSUITABLE_CLASSES),
        "title_exempt": sorted(TITLE_EXEMPT_CLASSES),
        "list_exempt": sorted(LIST_EXEMPT_CLASSES),
        "diagram_layout": dict(sorted(DIAGRAM_LAYOUT_CLASSES.items())),
        "section_classes": {theme: sorted(classes) for theme, classes in sorted(inventory.items())},
    }


def manifest_path() -> Path:
    return ROOT_DIR / "skills/marp-slide-creator/scripts/theme-classes.json"
