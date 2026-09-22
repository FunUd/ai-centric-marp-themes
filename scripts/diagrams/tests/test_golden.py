from __future__ import annotations

import re
from pathlib import Path


GOLDEN_DIR = Path(__file__).resolve().parent / "fixtures" / "diagram-golden"

THEME_LINES = {
    "azure-clarity": "#2C7BE5",
    "crimson-clarity": "#D32F2F",
    "prism-edge": "#4F46E5",
    "nebula-glass": "#22D3EE",
    "warm-sunnyday": "#FF8C42",
    "slate-minimal": "#475569",
}

# Expected draw.io rect radius per theme (None = sharp, no rx attribute).
THEME_RX = {
    "azure-clarity": None,
    "crimson-clarity": None,
    "prism-edge": None,
    "nebula-glass": "14",
    "warm-sunnyday": "12",
    "slate-minimal": "4",
}


def _read(theme: str, kind: str) -> str:
    path = GOLDEN_DIR / f"{theme}-{kind}.svg"
    assert path.exists(), f"missing golden: {path.name} (run regenerate-golden.py)"
    return path.read_text(encoding="utf-8")


def test_golden_flowchart_has_no_cheap_defaults() -> None:
    for theme, line in THEME_LINES.items():
        svg = _read(theme, "flowchart")
        assert "#0b0b0b" not in svg.lower(), theme
        assert "rgba(185,185,185,1)" not in svg, theme
        assert line.lower() in svg.lower(), theme


def test_golden_architecture_matches_theme_radius_and_line() -> None:
    for theme, line in THEME_LINES.items():
        svg = _read(theme, "architecture")
        assert line.lower() in svg.lower(), theme
        rects = re.findall(r"<rect x='[^']*'[^>]*>", svg)
        assert rects, theme
        expected = THEME_RX[theme]
        if expected is None:
            assert not any("rx='" in r or 'rx="' in r for r in rects), theme
        else:
            assert any(f"rx='{expected}'" in r or f'rx="{expected}"' in r for r in rects), theme


def test_golden_pie_uses_theme_primary() -> None:
    import json

    for theme in THEME_LINES:
        svg = _read(theme, "pie")
        style_path = Path(__file__).resolve().parents[1] / "theme-styles" / f"{theme}.json"
        primary = json.loads(style_path.read_text(encoding="utf-8"))["colors"]["primary"]
        assert primary.lower() in svg.lower(), theme
