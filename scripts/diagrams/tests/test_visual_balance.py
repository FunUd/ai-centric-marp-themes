from __future__ import annotations

import importlib.util
import math
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
models_spec = importlib.util.spec_from_file_location("diagram_models_balance", SCRIPT_DIR / "diagram_models.py")
assert models_spec and models_spec.loader
models = importlib.util.module_from_spec(models_spec)
sys.modules["diagram_models"] = models
models_spec.loader.exec_module(models)
design_tokens_spec = importlib.util.spec_from_file_location("design_tokens_balance", SCRIPT_DIR / "design_tokens.py")
assert design_tokens_spec and design_tokens_spec.loader
design_tokens = importlib.util.module_from_spec(design_tokens_spec)
sys.modules["design_tokens"] = design_tokens
design_tokens_spec.loader.exec_module(design_tokens)
renderer_spec = importlib.util.spec_from_file_location("svg_renderer_balance", SCRIPT_DIR / "svg_diagram_renderer.py")
assert renderer_spec and renderer_spec.loader
renderer = importlib.util.module_from_spec(renderer_spec)
sys.modules[renderer_spec.name] = renderer
renderer_spec.loader.exec_module(renderer)


def test_radial_connector_gaps_are_equal_for_cardinal_nodes() -> None:
    data = models.parse_diagram_data({"type": "radial", "layout": "asym", "width": 710, "height": 300, "center": "成果", "items": [{"label": "目的"}, {"label": "役割"}, {"label": "対話"}]})
    svg = renderer.render_diagram(data, {"colors": {}}, "asym")
    lines = re.findall(r'<line data-diagram-role="connector" x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', svg)
    lengths = [math.hypot(float(x2) - float(x1), float(y2) - float(y1)) for x1, y1, x2, y2 in lines]

    assert len(lengths) == 3
    assert max(lengths) - min(lengths) <= 1.0


def test_compact_chart_title_has_clearance_from_chart() -> None:
    data = models.parse_diagram_data({"type": "donut", "layout": "col3", "title": "構成", "items": [{"label": "A", "value": 1}, {"label": "B", "value": 1}]})
    ctx = design_tokens.theme_context({"colors": {}})
    elements = renderer._chart(data, ctx, donut=True)
    chart_path = next(element for element in elements if element.startswith("<path"))
    first_y = float(re.search(r"M [\d.]+ ([\d.]+)", chart_path).group(1))

    assert first_y >= 50