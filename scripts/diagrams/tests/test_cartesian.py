"""test_cartesian.py — bar / line / stacked-bar validation and rendering."""

from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

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


models = load_module("diagram_models", "diagram_models.py")
tokens = load_module("design_tokens", "design_tokens.py")
renderer = load_module("svg_diagram_renderer", "svg_diagram_renderer.py")
validator = load_module("validate_slide_diagram", "validate-slide-diagram.py")

THEMES = ("azure-clarity", "crimson-clarity", "prism-edge", "nebula-glass", "warm-sunnyday", "slate-minimal")

BAR_2 = {"type": "bar", "items": [{"label": "A", "value": 137}, {"label": "B", "value": 163}]}
LINE_2 = {
    "type": "line",
    "categories": ["Q1", "Q2"],
    "series": [{"label": "S1", "values": [137, 163]}, {"label": "S2", "values": [41, 59]}],
}
STACKED_2 = {
    "type": "stacked-bar",
    "categories": ["Q1", "Q2"],
    "series": [{"label": "S1", "values": [100, 120]}, {"label": "S2", "values": [37, 43]}],
}


def _ctx(theme: str = "azure-clarity") -> dict:
    return tokens.theme_context(tokens.load_design_tokens(theme))


# --- validation ---


def test_bar_rejects_negative_value() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        models.parse_diagram_data({"type": "bar", "items": [{"label": "A", "value": 1}, {"label": "B", "value": -2}]})


def test_line_rejects_series_length_mismatch() -> None:
    with pytest.raises(ValueError, match="one entry per category"):
        models.parse_diagram_data({"type": "line", "categories": ["A", "B"], "series": [{"label": "S", "values": [1]}]})


def test_stacked_bar_requires_two_series() -> None:
    with pytest.raises(ValueError, match="between 2 and"):
        models.parse_diagram_data(
            {"type": "stacked-bar", "categories": ["A", "B"], "series": [{"label": "S", "values": [1, 2]}]}
        )


def test_too_many_categories_rejected() -> None:
    with pytest.raises(ValueError, match="between 2 and"):
        models.parse_diagram_data({"type": "bar", "items": [{"label": f"C{i}", "value": 1} for i in range(11)]})


def test_y_max_below_data_rejected() -> None:
    with pytest.raises(ValueError, match="y_max"):
        models.parse_diagram_data({**BAR_2, "y_max": 100})


def test_zero_values_allowed() -> None:
    data = models.parse_diagram_data({"type": "bar", "items": [{"label": "A", "value": 0}, {"label": "B", "value": 0}]})
    svg = renderer.render_diagram(data, _ctx(), "full")
    assert ET.fromstring(svg) is not None


# --- negative-ready scale (future path, model still rejects negatives) ---


def test_nice_ticks() -> None:
    assert renderer._y_scale(0.0, 120.0)["ticks"] == [0, 50, 100, 150]
    assert renderer._y_scale(0.0, 90.0)["ticks"] == [0, 25, 50, 75, 100]


def test_y_scale_handles_negative_range() -> None:
    scale = renderer._y_scale(-50.0, 150.0)
    assert scale["min"] < 0 < scale["max"]
    assert any(tick < 0 for tick in scale["ticks"])
    frame = renderer._cartesian_frame({"width": 1080, "height": 420}, _ctx(), ["A", "B"], -50.0, 150.0)
    zero_y = frame["y"](0.0)
    assert frame["plot_top"] < zero_y < frame["plot_bottom"]


# --- rendering ---


def test_left_gutter_fits_unit_tick_label() -> None:
    """Regression: top tick "200 百万円" must not clip at x=0 (warm-sunnyday case)."""
    frame = renderer._cartesian_frame(
        {"width": 1080, "height": 420, "unit": "百万円"},
        _ctx("warm-sunnyday"),
        ["Q1", "Q2", "Q3", "Q4"],
        0.0,
        190.0,
    )
    caption = float(_ctx()["typography"]["captionSize"])
    for label in frame["tick_labels"]:
        left_edge = frame["plot_left"] - 8 - renderer._text_width(label, caption)
        assert left_edge >= 0, label


def test_value_label_defaults() -> None:
    bar_svg = renderer.render_diagram(models.parse_diagram_data(BAR_2), _ctx(), "full")
    line_svg = renderer.render_diagram(models.parse_diagram_data(LINE_2), _ctx(), "full")
    assert "137" in bar_svg  # bar defaults show_values=True
    assert "137" not in line_svg  # line defaults show_values=False


def test_cartesian_renders_in_all_themes() -> None:
    import json

    for template in ("sales-bar.json", "quarterly-line.json", "channel-stacked-bar.json"):
        raw = json.loads((SCRIPT_DIR / "templates" / "charts" / template).read_text(encoding="utf-8"))
        for theme in THEMES:
            data = models.parse_diagram_data(dict(raw))
            svg = renderer.render_diagram(data, _ctx(theme), "full")
            assert ET.fromstring(svg) is not None
            primary = tokens.load_design_tokens(theme)["colors"]["primary"]
            assert primary.lower() in svg.lower(), (template, theme)


def test_cartesian_passes_strict_validation(tmp_path: Path) -> None:
    import json

    for template in ("sales-bar.json", "quarterly-line.json", "channel-stacked-bar.json"):
        raw = json.loads((SCRIPT_DIR / "templates" / "charts" / template).read_text(encoding="utf-8"))
        for layout in ("full", "col2", "asym", "col3"):
            data = models.parse_diagram_data({**raw, "layout": layout})
            svg = renderer.render_diagram(data, _ctx(), layout)
            target = tmp_path / f"{template}-{layout}.svg"
            target.write_text(svg, encoding="utf-8")
            errors, _ = validator.validate_svg(target, layout)
            assert errors == [], (template, layout, errors)
