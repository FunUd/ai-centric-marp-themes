from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_module("design_tokens", "design_tokens.py")
load_module("svg_filters", "svg_filters.py")
postprocessor = load_module("svg_theme_postprocessor", "svg_theme_postprocessor.py")
tokens = sys.modules["design_tokens"]

SAMPLE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs/>
  <rect x="10" y="10" width="40" height="20" fill="#fff" stroke="#000"/>
  <text x="20" y="20" font-family="Arial">A</text>
</svg>"""


def test_postprocessor_applies_theme_font_and_radius() -> None:
    theme = tokens.load_design_tokens("warm-sunnyday")
    result = postprocessor.postprocess_svg(SAMPLE, theme)
    assert "Zen Maru Gothic" in result
    assert 'rx="12"' in result or "rx='12'" in result


def test_postprocessor_keeps_layout_coordinates() -> None:
    theme = tokens.load_design_tokens("azure-clarity")
    result = postprocessor.postprocess_svg(SAMPLE, theme)
    assert 'x="10"' in result or "x='10'" in result
    assert 'width="40"' in result or "width='40'" in result


MERMAID_SAMPLE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><style>#s .arrowheadPath{fill:#0b0b0b;}.edgePath .path{stroke:#2C7BE5;stroke-width:1px;}[data-look="neo"].node rect{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}</style><g class="nodes"><rect x="10" y="10" width="40" height="20" fill="#EDF5FF" stroke="#2C7BE5"/></g></svg>"""


def test_postprocessor_recolors_black_arrowheads_to_theme_line() -> None:
    theme = tokens.load_design_tokens("azure-clarity")
    result = postprocessor.postprocess_svg(MERMAID_SAMPLE, theme)
    assert "#0b0b0b" not in result.lower()
    assert "#2C7BE5" in result


def test_postprocessor_removes_default_gray_shadow() -> None:
    theme = tokens.load_design_tokens("azure-clarity")
    result = postprocessor.postprocess_svg(MERMAID_SAMPLE, theme)
    assert "rgba(185,185,185,1)" not in result


MULTI_DEFS_SAMPLE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><g><rect x="10" y="10" width="40" height="20" fill="#EDF5FF" stroke="#2C7BE5"/></g><defs><filter id="a"><feDropShadow dx="1" dy="1" stdDeviation="0"/></filter></defs><defs><filter id="b"><feDropShadow dx="2" dy="2" stdDeviation="0"/></filter></defs></svg>"""


def test_postprocessor_keeps_multi_defs_blocks_valid_xml() -> None:
    import xml.etree.ElementTree as ET

    theme = tokens.load_design_tokens("azure-clarity")
    result = postprocessor.postprocess_svg(MULTI_DEFS_SAMPLE, theme)
    ET.fromstring(result)  # must not raise: no orphaned <filter> outside <defs>
    assert 'id="theme-shadow"' in result
