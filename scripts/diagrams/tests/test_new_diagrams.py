"""test_new_diagrams.py — hbar / stacked-bar-100 / matrix validation and rendering."""
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

HBAR_2 = {"type": "hbar", "items": [{"label": "A", "value": 137}, {"label": "B", "value": 163}]}
STACKED100_2 = {
    "type": "stacked-bar-100",
    "categories": ["Q1", "Q2"],
    "series": [{"label": "S1", "values": [100, 120]}, {"label": "S2", "values": [37, 43]}],
}
MATRIX_2 = {
    "type": "matrix",
    "columns": ["A", "B"],
    "rows": [{"label": "R1", "scores": [5, 3]}, {"label": "R2", "scores": [2, 4]}],
}


def _ctx(theme: str = "azure-clarity") -> dict:
    return tokens.theme_context(tokens.load_design_tokens(theme))


def test_hbar_rejects_negative_value() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        models.parse_diagram_data({"type": "hbar", "items": [{"label": "A", "value": 1}, {"label": "B", "value": -2}]})


def test_hbar_rejects_single_item() -> None:
    with pytest.raises(ValueError, match="between 2 and"):
        models.parse_diagram_data({"type": "hbar", "items": [{"label": "A", "value": 1}]})


def test_stacked100_requires_two_series() -> None:
    with pytest.raises(ValueError, match="between 2 and"):
        models.parse_diagram_data(
            {"type": "stacked-bar-100", "categories": ["A", "B"], "series": [{"label": "S", "values": [1, 2]}]}
        )


def test_matrix_rejects_score_out_of_range() -> None:
    with pytest.raises(ValueError, match="0-5"):
        models.parse_diagram_data(
            {"type": "matrix", "columns": ["A", "B"], "rows": [{"label": "R1", "scores": [6, 3]}, {"label": "R2", "scores": [2, 4]}]}
        )


def test_matrix_rejects_column_mismatch() -> None:
    with pytest.raises(ValueError, match="one entry per column"):
        models.parse_diagram_data(
            {"type": "matrix", "columns": ["A", "B"], "rows": [{"label": "R1", "scores": [5]}, {"label": "R2", "scores": [2, 4]}]}
        )


def test_new_types_render_xml() -> None:
    for raw in (HBAR_2, STACKED100_2, MATRIX_2):
        svg = renderer.render_diagram(models.parse_diagram_data(dict(raw)), _ctx(), "full")
        assert ET.fromstring(svg) is not None


def test_new_types_render_in_all_themes() -> None:
    import json

    for template in ("task-hbar.json", "channel-100-bar.json", "tech-selection-matrix.json"):
        folder = "concepts" if "matrix" in template else "charts"
        raw = json.loads((SCRIPT_DIR / "templates" / folder / template).read_text(encoding="utf-8"))
        for theme in THEMES:
            svg = renderer.render_diagram(models.parse_diagram_data(dict(raw)), _ctx(theme), "full")
            assert ET.fromstring(svg) is not None
            primary = tokens.load_design_tokens(theme)["colors"]["primary"]
            assert primary.lower() in svg.lower(), (template, theme)


def test_new_types_pass_strict_validation(tmp_path: Path) -> None:
    import json

    cases = (
        ("charts", "task-hbar.json"),
        ("charts", "channel-100-bar.json"),
        ("concepts", "tech-selection-matrix.json"),
    )
    for folder, template in cases:
        raw = json.loads((SCRIPT_DIR / "templates" / folder / template).read_text(encoding="utf-8"))
        for layout in ("full", "col2", "asym", "col3"):
            data = models.parse_diagram_data({**raw, "layout": layout})
            svg = renderer.render_diagram(data, _ctx(), layout)
            target = tmp_path / f"{template}-{layout}.svg"
            target.write_text(svg, encoding="utf-8")
            errors, _ = validator.validate_svg(target, layout)
            assert errors == [], (template, layout, errors)
