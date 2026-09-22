from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
models_spec = importlib.util.spec_from_file_location("diagram_models_radial", SCRIPT_DIR / "diagram_models.py")
assert models_spec and models_spec.loader
models = importlib.util.module_from_spec(models_spec)
sys.modules["diagram_models"] = models
models_spec.loader.exec_module(models)
renderer_spec = importlib.util.spec_from_file_location("svg_renderer_radial", SCRIPT_DIR / "svg_diagram_renderer.py")
assert renderer_spec and renderer_spec.loader
renderer = importlib.util.module_from_spec(renderer_spec)
sys.modules[renderer_spec.name] = renderer
renderer_spec.loader.exec_module(renderer)


def _rects_overlap(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> bool:
    fx, fy, fw, fh = first
    sx, sy, sw, sh = second
    return fx < sx + sw and sx < fx + fw and fy < sy + sh and sy < fy + fh


def test_radial_parent_and_children_do_not_overlap() -> None:
    svg = renderer.render_diagram(
        {
            "type": "radial",
            "center": "成果",
            "items": [
                {"label": "目的", "children": ["判断基準", "優先順位"]},
                {"label": "役割", "children": ["責任", "連携"]},
                {"label": "対話", "children": ["共有", "学習"]},
            ],
        },
        {"colors": {}},
        "full",
    )
    root = ET.fromstring(svg)
    rects = []
    for element in root:
        if element.tag.endswith("rect") and element.get("data-diagram-role") == "node":
            rects.append(tuple(float(element.get(key, "0")) for key in ("x", "y", "width", "height")))

    assert all(not _rects_overlap(first, second) for index, first in enumerate(rects) for second in rects[index + 1:])