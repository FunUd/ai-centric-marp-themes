from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_script():
    models_spec = importlib.util.spec_from_file_location("diagram_models", SCRIPT_DIR / "diagram_models.py")
    assert models_spec and models_spec.loader
    models = importlib.util.module_from_spec(models_spec)
    sys.modules["diagram_models"] = models
    models_spec.loader.exec_module(models)
    renderer_spec = importlib.util.spec_from_file_location("svg_diagram_renderer", SCRIPT_DIR / "svg_diagram_renderer.py")
    assert renderer_spec and renderer_spec.loader
    renderer = importlib.util.module_from_spec(renderer_spec)
    sys.modules["svg_diagram_renderer"] = renderer
    renderer_spec.loader.exec_module(renderer)
    routing_spec = importlib.util.spec_from_file_location("diagram_routing", SCRIPT_DIR / "diagram_routing.py")
    assert routing_spec and routing_spec.loader
    routing = importlib.util.module_from_spec(routing_spec)
    sys.modules["diagram_routing"] = routing
    routing_spec.loader.exec_module(routing)
    spec = importlib.util.spec_from_file_location("render_slide_diagram", SCRIPT_DIR / "render-slide-diagram.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_json_renderer_writes_standalone_svg(tmp_path: Path) -> None:
    script = load_script()
    source = tmp_path / "diagram.json"
    output = tmp_path / "diagram.svg"
    source.write_text(json.dumps({"type": "pie", "items": [{"label": "A", "value": 1}]}), encoding="utf-8")

    assert script.render_json_diagram(source, output, script.load_theme_style("azure-clarity"), "full")
    assert output.read_text(encoding="utf-8").startswith("<svg ")


def test_all_json_diagram_types_render(tmp_path: Path) -> None:
    script = load_script()
    definitions = [
        {"type": "pie", "items": [{"label": "A", "value": 1}]},
        {"type": "donut", "items": [{"label": "A", "value": 1}]},
        {"type": "pyramid", "levels": [{"label": "A"}, {"label": "B"}, {"label": "C"}]},
        {"type": "cycle", "items": [{"label": "A"}, {"label": "B"}, {"label": "C"}]},
        {"type": "timeline", "periods": ["Q1"], "items": [{"period": "Q1", "label": "A"}]},
        {"type": "org-chart", "root": {"label": "A", "children": [{"label": "B"}]}},
        {"type": "radial", "center": "A", "items": [{"label": "B"}, {"label": "C"}, {"label": "D"}]},
    ]

    for index, definition in enumerate(definitions):
        output = tmp_path / f"diagram-{index}.svg"
        assert script.render_json_diagram_from_data(definition, output, script.load_theme_style("slate-minimal"), "col2")
        assert 'viewBox=' in output.read_text(encoding="utf-8")