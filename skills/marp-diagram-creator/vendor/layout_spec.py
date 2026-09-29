"""layout_spec.py — Single source of truth for slide diagram geometry.

Four layout profiles (``full`` / ``col2`` / ``asym`` / ``col3``) are used across
the diagram ecosystem. Each profile has four related — but distinct — numbers:

- ``CANVAS_MAX``: documented slide safe area (``diagram-patterns.md`` §1).
  ``marp-lint.py`` gates Markdown embed widths against these values.
- ``RENDER_DEFAULT``: default SVG output size used by the JSON renderer
  (``diagram_models.py``). Slightly smaller than the canvas so titles and
  padding never touch the slide chrome.
- ``EMBED_WIDTH``: recommended ``width:NNNpx`` in Markdown examples.
  Slightly under ``CANVAS_MAX`` for breathing room.
- ``VALIDATOR_LIMITS``: hard-fail bounds in ``validate-slide-diagram.py``.
  Intentionally ~20px above ``CANVAS_MAX`` as tolerance slack; the linter
  (not the validator) is the strict gate for embed widths.

All three consumers must import from here instead of hardcoding copies.
``marp-lint.py`` lives under ``skills/`` (copied to agent dirs by
``sync-skills.py``) so it keeps a local mirror — the values below are
authoritative when they disagree.
"""

from __future__ import annotations

LAYOUTS = ("full", "col2", "asym", "col3")

# Documented safe area on a 1280x720 slide (title + header/footer excluded).
CANVAS_MAX = {
    "full": {"max_w": 1120, "max_h": 460},
    "col2": {"max_w": 520, "max_h": 460},
    "asym": {"max_w": 710, "max_h": 460},
    "col3": {"max_w": 340, "max_h": 460},
}

# Default SVG output dimensions of the JSON diagram renderer.
RENDER_DEFAULT_WIDTH = {"full": 1080, "col2": 520, "asym": 710, "col3": 340}
RENDER_DEFAULT_HEIGHT = {"full": 420, "col2": 360, "asym": 420, "col3": 300}

# Recommended Markdown embed widths (``![width:NNNpx ...]``).
EMBED_WIDTH = {"full": 1050, "col2": 500, "asym": 680, "col3": 320}

# Hard-fail bounds for the post-render validator (CANVAS_MAX + ~20px slack).
VALIDATOR_LIMITS = {
    "full": {"max_w": 1140, "max_h": 470, "min_aspect": 1.2, "max_aspect": 4.5},
    "col2": {"max_w": 540, "max_h": 470, "min_aspect": 0.6, "max_aspect": 2.2},
    "asym": {"max_w": 730, "max_h": 470, "min_aspect": 0.9, "max_aspect": 3.0},
    "col3": {"max_w": 360, "max_h": 470, "min_aspect": 0.4, "max_aspect": 1.8},
}

# Marp ``_class`` directives mapped to a layout profile.
# NOTE 1: ``split-asym`` / ``split-asym-reverse`` are asymmetric (710px), NOT col2.
# NOTE 2: ``split-glass`` is a 50/50 grid (nebula-glass.css: 1fr 1fr) and
#         ``glass-card-layout`` is a single centered column, so both are budgeted
#         as col2 -- the narrowest of the three so an over-wide embed is caught.
#         ``glass-card-layout`` therefore has more room than its budget allows;
#         that errs toward a false DIAGRAM_OVERFLOW_WIDTH, never a silent overflow.
CLASS_TO_LAYOUT = {
    "cols-2": "col2",
    "split-2": "col2",
    "split-glass": "col2",
    "glass-card-layout": "col2",
    "cols-3": "col3",
    "split-3": "col3",
    "split-asym": "asym",
    "split-asym-reverse": "asym",
}

# Per-type height overrides: (diagram_type, layout) -> height.
TYPE_LAYOUT_HEIGHTS = {("radial", "asym"): 260}
