from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
models_spec = importlib.util.spec_from_file_location("diagram_models_text", SCRIPT_DIR / "diagram_models.py")
assert models_spec and models_spec.loader
models = importlib.util.module_from_spec(models_spec)
sys.modules["diagram_models"] = models
models_spec.loader.exec_module(models)

renderer_spec = importlib.util.spec_from_file_location("svg_renderer_text", SCRIPT_DIR / "svg_diagram_renderer.py")
assert renderer_spec and renderer_spec.loader
renderer = importlib.util.module_from_spec(renderer_spec)
sys.modules[renderer_spec.name] = renderer
renderer_spec.loader.exec_module(renderer)


def test_svg_text_wraps_explicit_lines() -> None:
    svg = renderer.svg_text(20, 30, "目的と優先順位\n判断基準", **{"text-anchor": "middle"})

    assert "<tspan" in svg
    assert "目的と優先順位" in svg
    assert "判断基準" in svg


def test_theme_font_is_used_by_rendered_labels() -> None:
    svg = renderer.render_diagram(
        {"type": "cycle", "items": [{"label": "A"}, {"label": "B"}, {"label": "C"}]},
        {"fontFamily": "Test Font", "colors": {}},
        "col2",
    )

    assert 'font-family="Test Font"' in svg


def test_long_cycle_labels_are_wrapped_automatically() -> None:
    svg = renderer.render_diagram(
        {
            "type": "cycle",
            "items": [
                {"label": "観察と課題の発見"},
                {"label": "小さな実験"},
                {"label": "振り返りと学習"},
            ],
        },
        {"fontFamily": "Test Font", "colors": {}},
        "col2",
    )

    assert svg.count("<tspan") >= 2