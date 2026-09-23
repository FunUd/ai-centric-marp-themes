"""Branch tests for svg_theme_postprocessor.py:
marker/swimlane radius rules, rx/ry replacement & insertion, radius-zero
cleanup, and _inject_node_filters guard clauses."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_module("design_tokens", "design_tokens.py")
load_module("svg_filters", "svg_filters.py")
post = load_module("svg_theme_postprocessor_branches", "svg_theme_postprocessor.py")


# --- _replace_rect_radius ----------------------------------------------------


def test_radius_rules_per_rect_role() -> None:
    svg = (
        "<svg>"
        '<rect data-diagram-role="marker" rx=\'9\' ry=\'9\'/>'
        '<rect style="swimlane" rx=\'9\' ry=\'9\'/>'
        '<rect rx="9" ry="8"/>'
        "</svg>"
    )

    out = post._replace_rect_radius(svg, 6.0, 12.0)

    # Markers get half the radius (int-normalized), swimlanes get the large one.
    marker = out[out.index("marker") : out.index("marker") + 120]
    assert "rx='3'" in marker
    swimlane = out[out.index("swimlane") : out.index("swimlane") + 120]
    assert "rx='12'" in swimlane
    # Plain rect: existing double-quoted rx/ry replaced.
    assert 'rx="6"' in out and 'ry="6"' in out
    assert 'rx="9"' not in out


def test_radius_inserted_into_tag_without_rx() -> None:
    svg = '<svg><rect x="1" y="2" width="3" height="4"></rect></svg>'

    out = post._replace_rect_radius(svg, 6.0, 12.0)

    assert 'rx=\'6\' ry=\'6\'>' in out or 'rx="6"' in out
    assert "<rect x=\"1\" y=\"2\" width=\"3\" height=\"4\" rx='6' ry='6'>" in out


def test_zero_radius_strips_existing_rx_ry() -> None:
    svg = '<svg><rect x="1" y="2" width="3" height="4" rx="5" ry="7"/></svg>'

    out = post._replace_rect_radius(svg, 0.0, 0.0)

    assert "rx=" not in out and "ry=" not in out


# --- _inject_node_filters ----------------------------------------------------


def test_inject_node_filters_noop_without_effects() -> None:
    svg = '<svg><defs/><rect fill="#fff" stroke="#000"/></svg>'

    assert post._inject_node_filters(svg, {}) == svg
    assert post._inject_node_filters(svg, {"nodeShadowEnabled": False, "glowEnabled": False}) == svg


def test_inject_node_filters_into_empty_defs() -> None:
    svg = '<svg><defs/><rect fill="#fff" stroke="#000"/></svg>'
    effects = {"nodeShadowEnabled": True, "nodeShadowBlur": 12, "nodeShadowOffsetY": 4}

    out = post._inject_node_filters(svg, effects)

    assert '<defs><filter id="theme-shadow"' in out
    assert 'filter="url(#theme-shadow)"' in out


def test_inject_node_filters_skips_decorated_and_roleless_rects() -> None:
    effects = {"glowEnabled": True, "glowBlur": 10, "nodeShadowEnabled": False}
    svg = (
        "<svg><defs>"
        '<filter id="theme-glow"></filter>'
        "</defs>"
        '<rect fill="#fff" stroke="#000" filter="url(#existing)"/>'
        '<rect data-diagram-role="connector" stroke="#000"/>'
        "<rect/></svg>"
    )

    out = post._inject_node_filters(svg, effects)

    # Existing filter, connector-role rect, and stroke-less/fill-less rect untouched.
    assert out.count('filter="url(#theme-glow)"') == 0
    assert 'filter="url(#existing)"' in out


# --- postprocess_svg smoke ---------------------------------------------------


def test_postprocess_svg_end_to_end() -> None:
    theme = load_module("design_tokens_for_post", "design_tokens.py").load_design_tokens("azure-clarity")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<style>.edgePath .path { stroke:#333; stroke-width:1px; }</style>'
        '<style>.arrowheadPath { fill: #abcdef; }</style>'
        "</svg>"
    )

    out = post.postprocess_svg(svg, theme)

    # Mermaid default arrow color forced onto the theme line color.
    assert "#0b0b0b" not in out
    # 1px edges lifted toward the theme stroke width.
    assert "stroke-width:1.5px" in out
