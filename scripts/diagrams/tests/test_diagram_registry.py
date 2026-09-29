"""test_diagram_registry.py — Model ↔ renderer ↔ template ↔ docs consistency.

Guards the ADD_NEW_DIAGRAM_TYPE.md procedure: every type in DIAGRAM_TYPES must
have a renderer, a validation branch, at least one template, and documentation
in both template-catalog.md and README.md.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ROOT_DIR = SCRIPT_DIR.parent.parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


models = load_module("diagram_models", "diagram_models.py")
layout_spec = load_module("layout_spec", "layout_spec.py")
renderer_mod = load_module("svg_diagram_renderer_registry", "svg_diagram_renderer.py")


def _renderer_names() -> set[str]:
    source = (SCRIPT_DIR / "svg_diagram_renderer.py").read_text(encoding="utf-8")
    match = re.search(r"renderers\s*=\s*\{(.*?)\}", source, re.DOTALL)
    assert match, "renderers map not found in svg_diagram_renderer.py"
    return set(re.findall(r'"([\w-]+)"\s*:', match.group(1)))


def _templates_by_type() -> dict[str, list[str]]:
    import json

    found: dict[str, list[str]] = {}
    for path in (SCRIPT_DIR / "templates").rglob("*.json"):
        try:
            kind = json.loads(path.read_text(encoding="utf-8")).get("type")
        except (ValueError, OSError):
            continue
        if kind:
            found.setdefault(kind, []).append(path.name)
    return found


def test_layout_spec_matches_model_widths() -> None:
    assert set(models.LAYOUT_WIDTHS) == set(layout_spec.RENDER_DEFAULT_WIDTH)
    assert set(models.LAYOUT_HEIGHTS) == set(layout_spec.RENDER_DEFAULT_HEIGHT)
    for layout, width in models.LAYOUT_WIDTHS.items():
        assert width == layout_spec.RENDER_DEFAULT_WIDTH[layout], layout
        assert width <= layout_spec.VALIDATOR_LIMITS[layout]["max_w"], layout
    for layout, height in models.LAYOUT_HEIGHTS.items():
        assert height == layout_spec.RENDER_DEFAULT_HEIGHT[layout], layout
        assert height <= layout_spec.VALIDATOR_LIMITS[layout]["max_h"], layout


def test_every_type_has_renderer() -> None:
    assert set(models.DIAGRAM_TYPES) == _renderer_names()


def test_every_type_has_template() -> None:
    by_type = _templates_by_type()
    missing = [kind for kind in models.DIAGRAM_TYPES if kind not in by_type]
    assert not missing, f"diagram types without a JSON template: {missing}"


def test_every_type_documented() -> None:
    catalog = (ROOT_DIR / "skills" / "marp-diagram-creator" / "references" / "template-catalog.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT_DIR / "docs" / "diagrams.md").read_text(encoding="utf-8")
    by_type = _templates_by_type()
    for kind in models.DIAGRAM_TYPES:
        for template in by_type.get(kind, []):
            assert template in catalog, f"{template} missing in template-catalog.md"
            assert template in readme, f"{template} missing in docs/diagrams.md Available Templates"
