from __future__ import annotations

import importlib.util
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
models_spec = importlib.util.spec_from_file_location("diagram_models_geometry", SCRIPT_DIR / "diagram_models.py")
assert models_spec and models_spec.loader
models = importlib.util.module_from_spec(models_spec)
sys.modules["diagram_models"] = models
models_spec.loader.exec_module(models)
design_tokens_spec = importlib.util.spec_from_file_location("design_tokens_geometry", SCRIPT_DIR / "design_tokens.py")
assert design_tokens_spec and design_tokens_spec.loader
design_tokens = importlib.util.module_from_spec(design_tokens_spec)
sys.modules["design_tokens"] = design_tokens
design_tokens_spec.loader.exec_module(design_tokens)
renderer_spec = importlib.util.spec_from_file_location("svg_renderer_geometry", SCRIPT_DIR / "svg_diagram_renderer.py")
assert renderer_spec and renderer_spec.loader
renderer = importlib.util.module_from_spec(renderer_spec)
sys.modules[renderer_spec.name] = renderer
renderer_spec.loader.exec_module(renderer)


def test_compact_chart_is_centered_on_canvas() -> None:
    data = models.parse_diagram_data(
        {"type": "donut", "layout": "col3", "items": [{"label": "A", "value": 1}, {"label": "B", "value": 1}]}
    )
    ctx = design_tokens.theme_context({"colors": {}})
    svg = "".join(renderer._chart(data, ctx, donut=True))

    assert 'cx="170"' in svg or 'M 170' in svg


def test_org_chart_leaf_boxes_have_a_gap() -> None:
    data = models.parse_diagram_data({"type": "org-chart", "layout": "col3", "root": {"label": "Root", "children": [{"label": "A"}, {"label": "B"}]}})
    svg = renderer.render_diagram(data, {"colors": {}}, "col3")
    root = ET.fromstring(svg)
    boxes = [
        element for element in root if element.tag.endswith("rect") and element.get("data-diagram-role") == "node"
    ]
    child_boxes = sorted(boxes[1:], key=lambda element: float(element.get("x", "0")))

    first_end = float(child_boxes[0].get("x", "0")) + float(child_boxes[0].get("width", "0"))
    second_start = float(child_boxes[1].get("x", "0"))
    assert second_start - first_end >= 8


def test_pyramid_labels_use_contrast_and_middle_alignment() -> None:
    data = models.parse_diagram_data({"type": "pyramid", "levels": [{"label": "成果"}, {"label": "協働"}, {"label": "基盤"}]})
    ctx = design_tokens.theme_context({"colors": {}})
    svg = "".join(renderer._pyramid(data, ctx))

    assert 'fill="#FFFFFF"' in svg
    assert 'dominant-baseline="middle"' in svg


def test_radial_connectors_end_at_box_edges() -> None:
    data = models.parse_diagram_data({"type": "radial", "layout": "asym", "width": 710, "height": 300, "center": "成果", "items": [{"label": "目的"}, {"label": "役割"}, {"label": "対話"}]})
    svg = renderer.render_diagram(data, {"colors": {}}, "asym")
    line = re.search(r'<line data-diagram-role="connector" x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', svg)
    assert line
    x1, y1, x2, y2 = (float(value) for value in line.groups())

    assert not (abs(x2 - 0) < 1e-6 and abs(y2 - 0) < 1e-6)
    assert abs(x1 - x2) > 0 or abs(y1 - y2) > 0