from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
models_spec = importlib.util.spec_from_file_location("diagram_models_pie", SCRIPT_DIR / "diagram_models.py")
assert models_spec and models_spec.loader
models = importlib.util.module_from_spec(models_spec)
sys.modules["diagram_models"] = models
models_spec.loader.exec_module(models)

design_tokens_spec = importlib.util.spec_from_file_location("design_tokens_pie", SCRIPT_DIR / "design_tokens.py")
assert design_tokens_spec and design_tokens_spec.loader
design_tokens = importlib.util.module_from_spec(design_tokens_spec)
sys.modules["design_tokens"] = design_tokens
design_tokens_spec.loader.exec_module(design_tokens)

renderer_spec = importlib.util.spec_from_file_location("svg_renderer_pie", SCRIPT_DIR / "svg_diagram_renderer.py")
assert renderer_spec and renderer_spec.loader
renderer = importlib.util.module_from_spec(renderer_spec)
sys.modules[renderer_spec.name] = renderer
renderer_spec.loader.exec_module(renderer)


def test_compact_donut_moves_chart_above_legend() -> None:
    data = models.parse_diagram_data(
        {
            "type": "donut",
            "layout": "col3",
            "items": [{"label": "A", "value": 1}, {"label": "B", "value": 1}, {"label": "C", "value": 1}],
        }
    )
    ctx = design_tokens.theme_context({"colors": {}})
    elements = renderer._chart(data, ctx, donut=True)

    assert not any('M 108.8 86.8' in element for element in elements)