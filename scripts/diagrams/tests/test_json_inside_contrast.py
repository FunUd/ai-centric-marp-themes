"""Inside-label contrast floors for JSON SVG diagrams (text >= 4.5:1).

Regression: white inside values on `primary` sat at 4.1-4.2:1 on
azure/nebula (hbar values, stacked-bar/100% percents, matrix max cells),
and crimson matrix mid-mixes at 4.2:1 with dark ink — `best_text_on`
picks the stronger side but both sides can fall short. The renderer now
routes inside labels through `design_tokens.ensure_inside_label`, which
nudges the fill within its hue until the best ink clears 4.5:1, keeping
segments and legend swatches identical.
"""
from __future__ import annotations

import importlib.util
import json
import re
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


tokens = load_module("design_tokens_inside", "design_tokens.py")
render_mod = load_module("render_inside_check", "render-slide-diagram.py")

THEMES = (
    "azure-clarity",
    "crimson-clarity",
    "prism-edge",
    "nebula-glass",
    "warm-sunnyday",
    "slate-minimal",
)


def _ratio(first: str, second: str) -> float:
    return tokens.contrast_ratio(first, second)


def test_ensure_inside_label_repairs_azure_primary() -> None:
    ink, fill = tokens.ensure_inside_label("#2C7BE5")
    assert fill and _ratio(ink, fill) >= 4.5
    # Hue preserved: still a blue, only slightly deepened.
    assert fill.upper() != "#2C7BE5"
    assert _ratio("#FFFFFF", fill) >= 4.5


def test_ensure_inside_label_keeps_passing_pairs_untouched() -> None:
    ink, fill = tokens.ensure_inside_label("#FF8C42")
    assert fill == "#FF8C42"  # dark ink already ~8:1 on warm orange
    assert ink == "#1A1A2E"
    ink, fill = tokens.ensure_inside_label("#FFFFFF")
    assert fill == "#FFFFFF" and ink == "#1A1A2E"


def test_ensure_inside_label_repairs_crimson_mid_mix() -> None:
    ink, fill = tokens.ensure_inside_label("#DA4F4F")
    assert fill and _ratio(ink, fill) >= 4.5


def _inside_texts(svg: str) -> list[tuple[str, str, str]]:
    """(label, text ink, containing box fill) for texts inside shapes."""
    q = r'["\']'
    boxes: list[tuple[float, float, float, float, str]] = []
    for m in re.finditer(
        r"<rect [^>]*x=" + q + r"([\d.]+)" + q + r" y=" + q + r"([\d.]+)" + q
        + r" width=" + q + r"([\d.]+)" + q + r" height=" + q + r"([\d.]+)" + q
        + r" fill=" + q + r"(#[0-9A-Fa-f]{6})" + q,
        svg,
    ):
        x, y, w, h, f = m.groups()
        boxes.append((float(x), float(y), float(w), float(h), f))
    found = []
    for m in re.finditer(
        r"<text [^>]*x=" + q + r"([\d.]+)" + q + r" y=" + q + r"([\d.]+)" + q
        + r"[^>]*fill=" + q + r"(#[0-9A-Fa-f]{6})" + q + r"[^>]*>([^<]*)<",
        svg,
    ):
        x, y, f, label = m.groups()
        cand = [
            b for b in boxes
            if b[0] <= float(x) <= b[0] + b[2] and b[1] - 6 <= float(y) <= b[1] + b[3] + 6
        ]
        if cand:
            box = sorted(cand, key=lambda b: b[2] * b[3])[0]
            found.append((label.strip(), f, box[4]))
    return found


def test_inside_labels_clear_text_floor_on_all_themes() -> None:
    templates = [
        "charts/task-hbar.json",
        "charts/channel-stacked-bar.json",
        "charts/channel-100-bar.json",
        "concepts/tech-selection-matrix.json",
    ]
    weak: list[str] = []
    for theme in THEMES:
        tdata = tokens.load_design_tokens(theme)
        for rel in templates:
            data = json.loads((SCRIPT_DIR / "templates" / rel).read_text(encoding="utf-8"))
            svg = render_mod.render_diagram(data, tdata, "full")
            for label, ink, fill in _inside_texts(svg):
                ratio = _ratio(ink, fill)
                if ratio < 4.5:
                    weak.append(f"{theme} {rel} {label!r} {ink} on {fill} = {ratio:.2f}")
    assert not weak, weak
