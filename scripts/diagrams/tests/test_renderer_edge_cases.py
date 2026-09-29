"""Branch tests for svg_diagram_renderer.py.

Covers the still-uncovered branches: _top_border_width/_top_accent_bar
(dead-by-default helpers), pyramid description/label overflow placement,
funnel overflow labels + conversion-rate guards, _fmt_tick abbreviations,
single-level org charts, and line charts with show_values.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_module("diagram_routing", "diagram_routing.py")
tokens = load_module("design_tokens", "design_tokens.py")
load_module("diagram_models", "diagram_models.py")
load_module("svg_aspect", "svg_aspect.py")
load_module("svg_filters", "svg_filters.py")
renderer = load_module("svg_diagram_renderer_edge_cases", "svg_diagram_renderer.py")

CTX = tokens.theme_context(tokens.load_design_tokens("azure-clarity"))
THEME = tokens.load_design_tokens("azure-clarity")


def _render(data: dict) -> str:
    return renderer.render_diagram(data, THEME, data.get("layout", "full"))


def _stripped(elements) -> str:
    """Rendered text content with all markup removed."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", "".join(elements)))


# --- low-level svg helpers & color fallbacks ---------------------------------


def test_svg_helper_functions_and_fallbacks() -> None:
    # wrap_text with a non-positive budget returns the input untouched.
    assert renderer.wrap_text("hello", 0) == "hello"

    group = renderer.svg_group(["<a/>"], transform="translate(0 0)")
    assert group.startswith("<g ") and group.endswith("><a/></g>")
    assert 'transform="translate(0 0)"' in group
    assert '<g data-diagram-role="group">' in renderer.svg_group(["<a/>"])

    ellipse = renderer.svg_ellipse(5, 6, 3, 2, fill="#FFF")
    assert ellipse.startswith("<ellipse ") and 'rx="3"' in ellipse and 'ry="2"' in ellipse

    # _hex_to_rgb: short-form expansion, length guard, non-hex guard.
    assert renderer._hex_to_rgb("#abc") == (170, 187, 204)
    assert renderer._hex_to_rgb("ab") == (44, 123, 229)
    assert renderer._hex_to_rgb("#zzzzzz") == (44, 123, 229)

    # _tiered_fills: empty and single-tier guards.
    assert renderer._tiered_fills(CTX, 0) == []
    assert renderer._tiered_fills(CTX, 1) == [CTX["primary"]]


# --- top accent bar helpers --------------------------------------------------


def test_top_border_width_parsing() -> None:
    assert renderer._top_border_width({"signature": {"topBorderWidth": 4}}) == 4.0
    assert renderer._top_border_width({}) == 0.0
    assert renderer._top_border_width({"signature": {"topBorderWidth": "wide"}}) == 0.0


def test_top_accent_bar_draws_or_stays_empty() -> None:
    bar = renderer._top_accent_bar(10, 20, 100, {"signature": {"topBorderWidth": 4}, "primary": "#2C7BE5"})

    assert 'data-diagram-role="marker"' in bar
    assert 'height="4"' in bar
    assert "#2C7BE5" in bar

    assert renderer._top_accent_bar(10, 20, 100, {"primary": "#2C7BE5"}) == ""
    assert renderer._top_accent_bar(10, 20, 100, {"signature": {"topBorderWidth": "wide"}}) == ""


# --- pyramid placement -------------------------------------------------------


def test_pyramid_down_direction_uses_inverted_width_formula() -> None:
    elements = renderer._pyramid(
        {
            "width": 1080,
            "height": 420,
            "direction": "down",  # apex at the bottom -> inverted width_at()
            "levels": [{"label": "Stage %d" % i, "description": "desc %d" % i} for i in range(4)],
        },
        CTX,
    )

    assert len(elements) > 5


def test_pyramid_outside_label_renders_description_below_it() -> None:
    long_label = "ExtremelyLongLevelLabelThatCannotFitInsideTheTier"
    elements = renderer._pyramid(
        {
            "width": 1080,
            "height": 420,
            "levels": [{"label": long_label, "description": "A description goes here"} for _ in range(3)],
        },
        CTX,
    )

    text = _stripped(elements)
    # Label moved outside its tier, description rendered underneath it.
    assert long_label[:20] in text
    assert "A description goes here" in text


def test_pie_and_donut_long_labels_fall_back_without_dropping_text() -> None:
    long_label = "VeryLongPieLabelOverflowingTheSlice"
    base = {
        "width": 1080,
        "height": 420,
        "layout": "full",
        "items": [{"label": long_label, "value": 1}, {"label": "B", "value": 1}],
    }

    pie = renderer._chart(dict(base), CTX, False)
    donut = renderer._chart({**base, "inner_ratio": 0.7}, CTX, True)

    # The centered label does not fit the slice (radius/inner-ring guards);
    # rendering still completes and keeps the text visible.
    for elements in (pie, donut):
        text = _stripped(elements)
        assert long_label[:20] in text
        assert "50%" in text


def test_pyramid_moves_description_outside_when_tier_is_narrow() -> None:
    svg = _render(
        {
            "type": "pyramid",
            "levels": [
                {
                    "label": "Top",
                    "description": (
                        "This description is deliberately far too long to fit inside the "
                        "narrow top tier of the pyramid diagram on a slide."
                    ),
                },
                {"label": "Middle"},
                {"label": "Base"},
            ],
        }
    )

    # Label stays inside its tier...
    assert ">Top</text>" in svg
    # ...while the description moves outside behind a leader line.
    assert "This description is deliberately" in svg
    assert svg.count('data-diagram-role="connector"') >= 3  # outline + leader + highlights


def test_pyramid_moves_overflowing_label_outside() -> None:
    long_label = "ExtremelyLongLabelThatCannotFitInsideTheTier"
    svg = _render(
        {
            "type": "pyramid",
            "levels": [
                {"label": long_label},
                {"label": "Middle"},
                {"label": "Base"},
            ],
        }
    )

    # Wrapped at 12 chars by the outside-label path.
    assert long_label[:12] in svg


# --- funnel labels & conversion-rate guards ----------------------------------


def test_funnel_overflow_label_moves_left_when_values_present() -> None:
    svg = _render(
        {
            "type": "funnel",
            "levels": [
                {"label": "Visit", "value": 1000},
                {"label": "Signup", "value": 200},
                {"label": "ExtremelyLongBottomStageLabelThatOverflowsTheNeck", "value": 10},
            ],
        }
    )

    assert "ExtremelyLon" in svg
    assert "1000" in svg and "200" in svg  # value pills in the gutter


def test_funnel_overflow_label_moves_right_without_values() -> None:
    svg = _render(
        {
            "type": "funnel",
            "levels": [
                {"label": "Visit"},
                {"label": "Signup"},
                {"label": "ExtremelyLongBottomStageLabelThatOverflowsTheNeck"},
            ],
        }
    )

    assert "ExtremelyLon" in svg
    # No conversion-rate text without values ('%' also appears in defs attrs).
    text_bodies = re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S)
    assert text_bodies and all("%" not in body for body in text_bodies)


def test_funnel_conversion_rate_guards() -> None:
    """Direct _funnel calls exercise guards that model validation would reject."""
    base = {"width": 1080, "height": 420}

    # Non-numeric current value -> float() fails and the pair is skipped.
    renderer._funnel(
        {
            **base,
            "levels": [{"label": "A", "value": "abc"}, {"label": "B", "value": 100}, {"label": "C", "value": "xyz"}],
        },
        CTX,
    )
    # Non-numeric following value -> rate computation fails and is skipped.
    renderer._funnel(
        {
            **base,
            "levels": [{"label": "A", "value": 100}, {"label": "B", "value": "abc"}, {"label": "C", "value": "xyz"}],
        },
        CTX,
    )
    # Zero base -> division guard.
    renderer._funnel(
        {**base, "levels": [{"label": "A", "value": 0}, {"label": "B", "value": 5}, {"label": "C", "value": 3}]},
        CTX,
    )
    # Mixed presence -> None guard (has_values stays True via level A).
    renderer._funnel(
        {**base, "levels": [{"label": "A", "value": 100}, {"label": "B"}, {"label": "C", "value": 50}]},
        CTX,
    )


def test_funnel_renders_with_partial_values_through_the_model() -> None:
    svg = _render(
        {
            "type": "funnel",
            "levels": [
                {"label": "Visit", "value": 100},
                {"label": "Signup"},
                {"label": "Paid", "value": 25},
            ],
        }
    )

    assert "25%" not in svg  # no adjacent value pair -> no rate


# --- tick formatting ---------------------------------------------------------


def test_fmt_tick_abbreviates_large_values() -> None:
    assert renderer._fmt_tick(1_500_000) == "1.5M"
    assert renderer._fmt_tick(2_000_000) == "2M"
    assert renderer._fmt_tick(1500) == "1.5k"
    assert renderer._fmt_tick(-2500) == "-2.5k"
    assert renderer._fmt_tick(12.5) == "12.5"
    assert renderer._fmt_tick(0) == "0"


# --- org chart / line --------------------------------------------------------


def test_org_chart_single_level_uses_fallback_pitch() -> None:
    svg = _render({"type": "org-chart", "root": {"label": "Solo"}})

    assert "Solo</text>" in svg


def test_line_chart_show_values_adds_point_labels() -> None:
    data = {
        "type": "line",
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        # 41 is not a "nice" axis tick, so it only appears as a point label.
        "series": [{"label": "Revenue", "values": [7, 13, 29, 41]}],
    }

    plain = _render(dict(data))
    with_values = _render({**data, "show_values": True})

    assert with_values.count("<text") > plain.count("<text")
    # Values render through _fmt_tick (41 -> "41").
    assert ">41<" in with_values
    assert ">41<" not in plain
