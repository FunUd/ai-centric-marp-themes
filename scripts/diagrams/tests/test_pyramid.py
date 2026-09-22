from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
models_spec = importlib.util.spec_from_file_location("diagram_models_pyramid", SCRIPT_DIR / "diagram_models.py")
assert models_spec and models_spec.loader
models = importlib.util.module_from_spec(models_spec)
sys.modules[models_spec.name] = models
models_spec.loader.exec_module(models)

design_tokens_spec = importlib.util.spec_from_file_location("design_tokens_pyramid", SCRIPT_DIR / "design_tokens.py")
assert design_tokens_spec and design_tokens_spec.loader
design_tokens = importlib.util.module_from_spec(design_tokens_spec)
sys.modules["design_tokens"] = design_tokens
design_tokens_spec.loader.exec_module(design_tokens)

renderer_spec = importlib.util.spec_from_file_location("svg_renderer_pyramid", SCRIPT_DIR / "svg_diagram_renderer.py")
assert renderer_spec and renderer_spec.loader
renderer = importlib.util.module_from_spec(renderer_spec)
sys.modules["diagram_models"] = models
sys.modules[renderer_spec.name] = renderer
renderer_spec.loader.exec_module(renderer)


def test_pyramid_has_apex_and_progressive_layer_widths() -> None:
    data = models.parse_diagram_data(
        {
            "type": "pyramid",
            "levels": [{"label": "成果"}, {"label": "協働"}, {"label": "基盤"}],
        }
    )
    ctx = design_tokens.theme_context({"colors": {}})
    svg = renderer._pyramid(data, ctx)
    polygons = [element for element in svg if element.startswith("<polygon")]

    assert len(polygons) == 3
    widths: list[tuple[float, float]] = []
    for polygon in polygons:
        coords = [float(value) for value in re.findall(r"[\d.]+", polygon.split('points="', 1)[1].split('"', 1)[0])]
        xs = coords[0::2]
        widths.append((min(xs), max(xs)))
    # Truncated apex: top edge is narrow but non-degenerate ...
    assert widths[0][1] - widths[0][0] > 10
    # ... and every tier grows progressively toward the base.
    assert widths[0][1] - widths[0][0] < widths[1][1] - widths[1][0] < widths[2][1] - widths[2][0]
    # Straight sides: left/right edge slopes are consistent across tiers.
    left = [low for low, _ in widths]
    assert left[0] > left[1] > left[2]