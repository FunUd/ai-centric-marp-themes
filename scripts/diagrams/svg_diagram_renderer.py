"""SVG diagram renderer — public facade.

Rendering logic lives in :mod:`renderers` (see ``renderers/__init__.py`` for
the layout); this module re-exports every helper so existing importers keep
working unchanged:

- ``render-slide-diagram.py`` (``from svg_diagram_renderer import render_diagram``)
- the test-suite, which also exercises private helpers (``_y_scale``,
  ``_cartesian_frame``, ``_cycle``, ...) directly off this module
- the vendored skill copy (``skills/marp-diagram-creator/vendor/``)

It also owns the :func:`render_diagram` dispatcher (the ``renderers`` map is
asserted by ``tests/test_diagram_registry.py`` to live in this file).
"""

from __future__ import annotations

import re

from design_tokens import theme_context
from diagram_models import parse_diagram_data
from renderers.charts import (
    CARTESIAN_PALETTE,
    CHART_CY_FULL,
    CHART_R_FULL,
    _bar,
    _cartesian_frame,
    _chart,
    _fmt_tick,
    _hbar,
    _legend_row,
    _line,
    _series_colors,
    _stacked_bar,
    _stacked_bar_100,
    _y_scale,
)
from renderers.concepts import _cycle, _funnel, _matrix, _matrix_cell, _pyramid, _radial
from renderers.organization import _org_chart
from renderers.primitives import (
    _accent_fill,
    _attrs,
    _fits_inside,
    _gradient_defs,
    _hex_to_rgb,
    _marker_rx,
    _mix_hex,
    _node_rect,
    _num,
    _rgb_to_hex,
    _text,
    _text_width,
    _tiered_fills,
    _title,
    _top_accent_bar,
    _top_border_width,
    escape_xml,
    svg_arrow,
    svg_circle,
    svg_document,
    svg_ellipse,
    svg_group,
    svg_line,
    svg_path,
    svg_polygon,
    svg_rect,
    svg_text,
    wrap_text,
)
from svg_filters import build_filter_defs

__all__ = [
    "render_diagram",
    "CARTESIAN_PALETTE",
    "CHART_CY_FULL",
    "CHART_R_FULL",
    "_num",
    "escape_xml",
    "wrap_text",
    "_attrs",
    "svg_group",
    "svg_rect",
    "svg_circle",
    "svg_ellipse",
    "svg_polygon",
    "svg_path",
    "svg_line",
    "svg_arrow",
    "svg_text",
    "svg_document",
    "_hex_to_rgb",
    "_rgb_to_hex",
    "_mix_hex",
    "_tiered_fills",
    "_text_width",
    "_fits_inside",
    "_text",
    "_title",
    "_node_rect",
    "_marker_rx",
    "_gradient_defs",
    "_accent_fill",
    "_top_border_width",
    "_top_accent_bar",
    "_chart",
    "_fmt_tick",
    "_y_scale",
    "_legend_row",
    "_cartesian_frame",
    "_series_colors",
    "_bar",
    "_line",
    "_stacked_bar",
    "_hbar",
    "_stacked_bar_100",
    "_pyramid",
    "_cycle",
    "_radial",
    "_funnel",
    "_matrix_cell",
    "_matrix",
    "_org_chart",
]


def render_diagram(data: dict, theme_data: dict, layout: str) -> str:
    data = parse_diagram_data({**data, "layout": data.get("layout", layout)})
    ctx = theme_context(theme_data)
    kind = data["type"]
    renderers = {
        "pie": lambda: _chart(data, ctx, False),
        "donut": lambda: _chart(data, ctx, True),
        "pyramid": lambda: _pyramid(data, ctx),
        "cycle": lambda: _cycle(data, ctx),
        "org-chart": lambda: _org_chart(data, ctx),
        "radial": lambda: _radial(data, ctx),
        "funnel": lambda: _funnel(data, ctx),
        "bar": lambda: _bar(data, ctx),
        "hbar": lambda: _hbar(data, ctx),
        "line": lambda: _line(data, ctx),
        "stacked-bar": lambda: _stacked_bar(data, ctx),
        "stacked-bar-100": lambda: _stacked_bar_100(data, ctx),
        "matrix": lambda: _matrix(data, ctx),
    }
    elements = renderers[kind]()
    defs_parts: list[str] = []
    filters = build_filter_defs(ctx["effects"])
    if filters:
        inner = re.sub(r"^<defs>|</defs>$", "", filters.strip())
        if inner.strip():
            defs_parts.append(inner)
    gradient = _gradient_defs(ctx)
    if gradient:
        inner = re.sub(r"^<defs>|</defs>$", "", gradient.strip())
        if inner.strip():
            defs_parts.append(inner)
    filter_defs = f"<defs>{''.join(defs_parts)}</defs>" if defs_parts else ""
    return svg_document(data["width"], data["height"], elements, ctx["background"], filter_defs)
