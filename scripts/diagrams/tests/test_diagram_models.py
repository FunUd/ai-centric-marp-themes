from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_module("svg_filters", "svg_filters.py")
models = load_module("diagram_models", "diagram_models.py")
renderer = load_module("svg_diagram_renderer", "svg_diagram_renderer.py")


def test_minimal_diagram_defaults_are_applied() -> None:
    diagram = models.parse_diagram_data({"type": "pie", "items": [{"label": "A", "value": 1}]})

    assert diagram["type"] == "pie"
    assert diagram["theme"] == "azure-clarity"
    assert diagram["layout"] == "full"
    assert diagram["width"] == 1080
    assert diagram["height"] == 420


def test_layout_defaults_use_slide_safe_widths() -> None:
    diagram = models.parse_diagram_data({"type": "pie", "layout": "col2", "items": [{"label": "A", "value": 1}]})

    assert diagram["width"] == 520


def test_col3_default_height_is_compact_for_embedded_diagrams() -> None:
    diagram = models.parse_diagram_data({"type": "cycle", "layout": "col3", "items": [{"label": "A"}, {"label": "B"}, {"label": "C"}]})

    assert diagram["height"] == 300


@pytest.mark.parametrize(
    "data, message",
    [
        ({}, "type"),
        ({"type": "unknown"}, "type"),
        ({"type": "pie", "layout": "bad", "items": [{"label": "A", "value": 1}]}, "layout"),
        ({"type": "pie", "items": [{"label": "A", "value": float("nan")}]}, "value"),
    ],
)
def test_invalid_common_fields_are_rejected(data: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        models.parse_diagram_data(data)


def test_xml_text_is_escaped() -> None:
    assert renderer.escape_xml("A & <B> \"C\"") == "A &amp; &lt;B&gt; &quot;C&quot;"


def test_svg_document_has_viewbox_and_roles() -> None:
    svg = renderer.svg_document(
        100,
        80,
        [renderer.svg_rect(1, 2, 30, 20, role="node"), renderer.svg_text(10, 15, "ラベル")],
    )

    assert 'viewBox="0 0 100 80"' in svg
    assert 'data-diagram-role="node"' in svg
    assert 'data-diagram-role="label"' in svg