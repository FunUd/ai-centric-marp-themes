from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1]
THEMES = ["azure-clarity", "crimson-clarity", "prism-edge", "nebula-glass", "warm-sunnyday", "slate-minimal"]


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
    return sys.modules["design_tokens"], sys.modules["svg_diagram_renderer"]


tokens, renderer = load_modules()

CYCLE = {"type": "cycle", "items": [{"label": "A"}, {"label": "B"}, {"label": "C"}]}


@pytest.mark.parametrize("theme,expected_rx", [
    ("azure-clarity", None),
    ("warm-sunnyday", 12),
    ("slate-minimal", 4),
    ("nebula-glass", 14),
])
def test_cycle_node_radius_matches_theme(theme: str, expected_rx: int | None) -> None:
    theme_data = tokens.load_design_tokens(theme)
    svg = renderer.render_diagram(CYCLE, theme_data, "full")
    if expected_rx is None:
        assert 'rx="0"' not in svg
        assert "rx='0'" not in svg
        assert 'rx="8"' not in svg
    else:
        assert f'rx="{expected_rx}"' in svg or f"rx='{expected_rx}'" in svg


def test_nebula_glass_includes_glow_filter() -> None:
    theme_data = tokens.load_design_tokens("nebula-glass")
    svg = renderer.render_diagram(CYCLE, theme_data, "full")
    assert 'id="theme-glow"' in svg


@pytest.mark.parametrize("theme", THEMES)
def test_all_core_types_render_for_every_theme(theme: str) -> None:
    theme_data = tokens.load_design_tokens(theme)
    definitions = [
        {"type": "pie", "items": [{"label": "A", "value": 1}, {"label": "B", "value": 2}]},
        {"type": "funnel", "levels": [{"label": "A"}, {"label": "B"}, {"label": "C"}]},
    ]
    for definition in definitions:
        svg = renderer.render_diagram(definition, theme_data, "full")
        assert svg.startswith("<svg ")
        assert re.search(r"viewBox=\"0 0", svg)
