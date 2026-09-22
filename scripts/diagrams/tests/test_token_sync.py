from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
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


tokens = load_module("design_tokens", "design_tokens.py")
load_module("diagram_models", "diagram_models.py")
load_module("svg_filters", "svg_filters.py")
renderer = load_module("svg_diagram_renderer", "svg_diagram_renderer.py")
sync_mod = load_module("sync_tokens", "sync-tokens-from-css.py")
render_mod = load_module("render_slide_diagram", "render-slide-diagram.py")


def _theme(name: str) -> dict:
    return tokens.load_design_tokens(name)


def test_sync_check_passes_for_all_themes() -> None:
    for theme in ("azure-clarity", "crimson-clarity", "prism-edge", "nebula-glass", "warm-sunnyday", "slate-minimal"):
        css_text = (sync_mod.THEMES_DIR / sync_mod.THEME_FILES[theme]).read_text(encoding="utf-8")
        vars_ = sync_mod.parse_root_vars(css_text)
        existing = __import__("json").loads((sync_mod.STYLES_DIR / f"{theme}.json").read_text(encoding="utf-8"))
        updates = sync_mod.build_updates(theme, vars_, css_text, existing)
        assert existing.get("signature") == updates["signature"], theme


def test_gradient_defs_present_for_light_themes() -> None:
    svg = renderer.render_diagram(
        {"type": "radial", "center": "C", "items": [{"label": "A"}, {"label": "B"}, {"label": "C"}]},
        _theme("azure-clarity"),
        "full",
    )
    assert 'id="theme-accent-gradient"' in svg
    assert "url(#theme-accent-gradient)" in svg


def test_drawio_status_fill_preserved() -> None:
    theme = _theme("azure-clarity")
    root = ET.fromstring(
        '<mxfile><diagram><mxGraphModel><root>'
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        '<mxCell id="2" vertex="1" parent="1" '
        'style="rounded=1;fillColor=#27AE60;strokeColor=#27AE60;fontColor=#FFFFFF;"/>'
        "</root></mxGraphModel></diagram></mxfile>"
    )
    render_mod._recolor_drawio_xml(root, theme)
    styles = [c.get("style", "") for c in root.iter("mxCell")]
    assert any("fillColor=#27AE60" in s or "fillColor=#27ae60" in s.lower() for s in styles)


def test_drawio_edges_render_above_containers() -> None:
    """Connectors must not be hidden under swimlane box fills.

    z-order: container boxes < edges < header chrome < nodes.
    """
    import xml.etree.ElementTree as ET

    theme = _theme("azure-clarity")
    template = Path(__file__).resolve().parents[1] / "templates" / "drawio" / "system-architecture.drawio"
    tree = ET.parse(template)
    render_mod._recolor_drawio_xml(tree.getroot(), theme)
    svg = render_mod._convert_drawio_to_svg(tree, theme)
    # Edge paths carry fill='none'; cylinder node bodies use a fill color.
    assert "fill='none'" in svg
    # Note: header bars share the container width; the first width='1040'
    # occurrence is a container box (containers render first).
    first_container = svg.index("width='1040")
    first_edge = svg.index("fill='none'")
    first_chrome = svg.index("opacity='0.12'")
    first_node_text = svg.index("text-anchor='middle'")
    assert first_container < first_edge < first_chrome < first_node_text


def test_drawio_arrowheads_sit_on_path_ends() -> None:
    """Arrow tips must coincide with their edge path ends.

    Guards the defect where paths used snapped endpoints while arrowheads
    were still drawn at the pre-snap ports (detached/cut-looking arrows).
    """
    import re
    import xml.etree.ElementTree as ET

    theme = _theme("azure-clarity")
    template = Path(__file__).resolve().parents[1] / "templates" / "drawio" / "system-architecture.drawio"
    tree = ET.parse(template)
    render_mod._recolor_drawio_xml(tree.getroot(), theme)
    svg = render_mod._convert_drawio_to_svg(tree, theme)
    path_ends = re.findall(r"<path d='M [^']*?L ([\d.]+) ([\d.]+)' fill='none'", svg)
    arrow_tips = re.findall(r"<polygon points='([\d.]+),([\d.]+) ", svg)
    assert path_ends, "no edge paths rendered"
    assert len(path_ends) == len(arrow_tips), (path_ends, arrow_tips)
    for (ex, ey), (ax, ay) in zip(sorted(path_ends), sorted(arrow_tips)):
        assert abs(float(ex) - float(ax)) <= 0.1 and abs(float(ey) - float(ay)) <= 0.1, (ex, ey, ax, ay)
