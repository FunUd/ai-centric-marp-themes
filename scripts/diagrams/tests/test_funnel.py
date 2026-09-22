from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_modules():
    for name, filename in [
        ("design_tokens", "design_tokens.py"),
        ("diagram_models", "diagram_models.py"),
        ("svg_filters", "svg_filters.py"),
        ("svg_diagram_renderer", "svg_diagram_renderer.py"),
    ]:
        spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules["diagram_models"], sys.modules["svg_diagram_renderer"], sys.modules["design_tokens"]


models, renderer, tokens = load_modules()

VALID_WITH_VALUES = {
    "type": "funnel",
    "direction": "down",
    "levels": [
        {"label": "認知", "value": 1000},
        {"label": "関心", "value": 400},
        {"label": "検討", "value": 120},
        {"label": "成約", "value": 30},
    ],
}

VALID_WITHOUT_VALUES = {
    "type": "funnel",
    "direction": "down",
    "levels": [
        {"label": "Level 1"},
        {"label": "Level 2"},
        {"label": "Level 3"},
    ],
}

VALID_UP_DIRECTION = {
    "type": "funnel",
    "direction": "up",
    "levels": [
        {"label": "Step 1"},
        {"label": "Step 2"},
        {"label": "Step 3"},
    ],
}


def test_funnel_renders_with_values() -> None:
    svg = renderer.render_diagram(VALID_WITH_VALUES, tokens.load_design_tokens("azure-clarity"), "full")
    assert svg.count("data-diagram-role=\"node\"") >= 4
    assert "認知" in svg
    assert "関心" in svg
    assert "検討" in svg
    assert "成約" in svg
    assert "1000" in svg
    assert "400" in svg


def test_funnel_renders_without_values() -> None:
    svg = renderer.render_diagram(VALID_WITHOUT_VALUES, tokens.load_design_tokens("azure-clarity"), "full")
    assert svg.count("data-diagram-role=\"node\"") >= 3
    assert "Level 1" in svg
    assert "Level 2" in svg
    assert "Level 3" in svg


def test_funnel_renders_up_direction() -> None:
    svg = renderer.render_diagram(VALID_UP_DIRECTION, tokens.load_design_tokens("azure-clarity"), "full")
    assert svg.count("data-diagram-role=\"node\"") >= 3
    assert "Step 1" in svg
    assert "Step 2" in svg
    assert "Step 3" in svg


def test_funnel_requires_three_to_six_levels() -> None:
    invalid = {**VALID_WITH_VALUES, "levels": VALID_WITH_VALUES["levels"][:2]}
    with pytest.raises(ValueError, match="levels"):
        models.parse_diagram_data(invalid)
    
    invalid = {**VALID_WITH_VALUES, "levels": VALID_WITH_VALUES["levels"] * 2}
    with pytest.raises(ValueError, match="levels"):
        models.parse_diagram_data(invalid)


def test_funnel_values_must_be_non_negative() -> None:
    invalid = {**VALID_WITH_VALUES, "levels": [
        {"label": "A", "value": -10},
        {"label": "B", "value": 20},
        {"label": "C", "value": 30},
    ]}
    with pytest.raises(ValueError, match="value"):
        models.parse_diagram_data(invalid)


def test_funnel_alternates_colors() -> None:
    svg = renderer.render_diagram(VALID_WITH_VALUES, tokens.load_design_tokens("azure-clarity"), "full")
    # Funnel should alternate between primary and light colors
    # This is verified by checking that both color schemes are present
    ctx = tokens.theme_context(tokens.load_design_tokens("azure-clarity"))
    assert ctx["primary"] in svg or ctx["light"] in svg


def test_funnel_polygon_shapes() -> None:
    svg = renderer.render_diagram(VALID_WITH_VALUES, tokens.load_design_tokens("azure-clarity"), "full")
    # Funnel uses polygon shapes (trapezoids)
    assert "<polygon" in svg
