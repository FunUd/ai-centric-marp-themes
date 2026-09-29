from __future__ import annotations

import importlib.util
import re
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
render_mod = load_module("render_contrast_check", "render-slide-diagram.py")


def _recolored_styles(theme_name: str, template: str = "system-architecture.drawio") -> list[str]:
    theme = tokens.load_design_tokens(theme_name)
    tree = ET.parse(SCRIPT_DIR / "templates" / "drawio" / template)
    render_mod._recolor_drawio_xml(tree.getroot(), theme)
    return [cell.get("style", "") for cell in tree.getroot().iter("mxCell")]


def test_best_text_on_picks_dark_for_light_fills() -> None:
    assert tokens.best_text_on("#FFFFFF", "#F5F7FB") == "#1A1A2E"
    assert tokens.best_text_on("#C4B5FD", "#F5F7FB") == "#1A1A2E"
    assert tokens.best_text_on("#EDF5FF", "#1A1A2E") == "#1A1A2E"


def test_best_text_on_keeps_light_for_dark_fills() -> None:
    assert tokens.best_text_on("#1E1838", "#F5F7FB") == "#F5F7FB"
    assert tokens.best_text_on("#8B5CF6", "#FFFFFF") == "#FFFFFF"
    assert tokens.best_text_on("#040712", "#F5F7FB") == "#F5F7FB"


def test_nebula_white_nodes_get_dark_text() -> None:
    styles = _recolored_styles("nebula-glass")
    white_nodes = [s for s in styles if "fillColor=#FFFFFF" in s and "vertex" not in s]
    assert white_nodes, "template should contain white-fill nodes"
    for style in white_nodes:
        match = re.search(r"fontColor=([^;]+)", style)
        assert match, style
        assert match.group(1).lower() not in ("#f5f7fb", "#ffffff"), style


def test_light_theme_white_nodes_unchanged() -> None:
    styles = _recolored_styles("azure-clarity")
    white_nodes = [s for s in styles if "fillColor=#FFFFFF" in s]
    assert white_nodes
    for style in white_nodes:
        match = re.search(r"fontColor=([^;]+)", style)
        assert match and match.group(1) == "#1A1A2E", style


def test_accent_nodes_clear_text_floor_on_every_theme() -> None:
    """Accent (inverted) shapes must keep readable ink on every palette.

    The recolor used to keep fixed white text: warm `primary` with white is
    2.3:1 and azure/nebula primaries sit at 4.1-4.2:1. The fill is now
    nudged within its hue until the best ink clears 4.5:1.
    """
    for theme in ("azure-clarity", "crimson-clarity", "prism-edge", "nebula-glass", "warm-sunnyday", "slate-minimal"):
        for template in ("system-architecture.drawio", "cloud-infrastructure.drawio"):
            styles = _recolored_styles(theme, template)
            accents = [s for s in styles if "fontStyle=1" in s and "swimlane" not in s]
            assert accents, f"{theme} {template}: no accent nodes found"
            for style in styles:
                if "swimlane" in style:
                    continue
                font = re.search(r"fontColor=([^;]+)", style)
                fill = re.search(r"fillColor=([^;]+)", style)
                if not font or not fill:
                    continue
                ratio = _contrast_ratio(font.group(1), fill.group(1))
                assert ratio >= 4.5, (
                    f"{theme} {template}: {font.group(1)} on {fill.group(1)} = {ratio:.1f}:1 ({style[:80]})"
                )


def _contrast_ratio(first: str, second: str) -> float:
    return tokens.contrast_ratio(first, second)


def test_nebula_text_contrast_on_shapes() -> None:
    """Every Nebula text node must contrast against the shape behind it."""
    theme = tokens.load_design_tokens("nebula-glass")
    tree = ET.parse(SCRIPT_DIR / "templates" / "drawio" / "system-architecture.drawio")
    render_mod._recolor_drawio_xml(tree.getroot(), theme)
    svg = render_mod._convert_drawio_to_svg(tree, theme)

    boxes: list[tuple[float, float, float, float, str]] = []
    for match in re.finditer(
        r"<rect x='([\d.]+)' y='([\d.]+)' width='([\d.]+)' height='([\d.]+)' fill='(#[0-9A-Fa-f]{6})'[^>]*>", svg
    ):
        x, y, w, h, fill, tag = (*match.groups(), match.group(0))
        if "opacity" in tag:
            continue  # header bars are translucent washes over the dark base
        boxes.append((float(x), float(y), float(w), float(h), fill))
    for match in re.finditer(
        r"<ellipse cx='([\d.]+)' cy='([\d.]+)' rx='([\d.]+)' ry='([\d.]+)' fill='(#[0-9A-Fa-f]{6})'", svg
    ):
        cx, cy, rx, ry, fill = match.groups()
        boxes.append((float(cx) - float(rx), float(cy) - float(ry), 2 * float(rx), 2 * float(ry), fill))
    for match in re.finditer(r"<path d='([^']+)' fill='(#[0-9A-Fa-f]{6})'", svg):
        d, fill = match.groups()
        # M/L endpoints only: arc flags (A rx ry rot large sweep x y) would pollute the bbox.
        coords = re.findall(r"[ML]\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", d)
        if not coords:
            continue
        xs = [float(c[0]) for c in coords]
        ys = [float(c[1]) for c in coords]
        boxes.append((min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys), fill))
    assert boxes
    weak: list[str] = []
    for match in re.finditer(r"<text x='([\d.]+)' y='([\d.]+)'[^>]*fill='(#[0-9A-Fa-f]{6})'>([^<]*)<", svg):
        x, y, fill, label = match.groups()
        candidates = [b for b in boxes if b[0] <= float(x) <= b[0] + b[2] and b[1] <= float(y) <= b[1] + b[3]]
        if not candidates:
            continue
        # Topmost (last painted) smallest containing box wins.
        box = sorted(candidates, key=lambda b: b[2] * b[3])[0]
        ratio = _contrast_ratio(fill, box[4])
        if ratio < 3.0:
            weak.append(f"{label.strip()[:12]} text {fill} on {box[4]} = {ratio:.1f}:1")
    assert not weak, weak
