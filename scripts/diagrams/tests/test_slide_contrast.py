"""Slide-level contrast guarantees (WCAG AA, computed from the token SSoT).

`scripts/diagrams/theme-styles/*.json` is generated from `themes/*.css`,
so these tests fail the moment a palette edit breaks readability — replacing
the hand-measured values previously kept only in the CHANGELOG:

- body and muted text on the slide background: >= 4.5:1 (AA normal text);
- keyboard focus indicator (`section:focus-visible`) on the background:
  >= 3.0:1 (WCAG 2.4.11 non-text contrast). warm-sunnyday's primary orange
  only reaches 2.3:1, which is why its indicator uses `--ws-primary-dark`
  (3.9:1) — pinned below so the reason cannot silently rot;
- `best_text_on` picks on every palette fill: the max-ratio side, with a
  >= 3.0:1 floor (fills below 4.5, e.g. azure danger 4.5, are documented
  follow-ups, not silent passes).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ROOT_DIR = SCRIPT_DIR.parent.parent

THEMES = (
    "azure-clarity",
    "crimson-clarity",
    "prism-edge",
    "nebula-glass",
    "warm-sunnyday",
    "slate-minimal",
)

DARK_INK = "#1A1A2E"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tokens = load_module("design_tokens_slide_contrast", "design_tokens.py")


def palette(theme: str) -> dict[str, str]:
    path = SCRIPT_DIR / "theme-styles" / f"{theme}.json"
    return json.loads(path.read_text(encoding="utf-8"))["colors"]


def test_body_and_muted_text_meet_aa_on_background() -> None:
    for theme in THEMES:
        colors = palette(theme)
        background = colors["background"]
        for key in ("text", "textMuted"):
            ratio = tokens.contrast_ratio(colors[key], background)
            assert ratio >= 4.5, f"{theme} {key} {colors[key]} on {background} = {ratio:.2f}:1"


def test_focus_indicator_meets_non_text_contrast() -> None:
    """`section:focus-visible` uses `--xx-primary`, except warm-sunnyday whose
    primary orange (2.3:1) documents why it uses `--ws-primary-dark`."""
    for theme in THEMES:
        colors = palette(theme)
        background = colors["background"]
        if theme == "warm-sunnyday":
            primary_ratio = tokens.contrast_ratio(colors["primary"], background)
            assert primary_ratio < 3.0, f"warm primary now passes; use it: {primary_ratio:.2f}:1"
            ratio = tokens.contrast_ratio(colors["primaryDark"], background)
            assert ratio >= 3.0, f"warm primaryDark {ratio:.2f}:1"
        else:
            ratio = tokens.contrast_ratio(colors["primary"], background)
            assert ratio >= 3.0, f"{theme} primary {colors['primary']} on {background} = {ratio:.2f}:1"


def test_warm_focus_rule_uses_primary_dark() -> None:
    text = (ROOT_DIR / "themes/warm-sunnyday.css").read_text(encoding="utf-8")
    assert "section:focus-visible" in text
    block = text.split("section:focus-visible")[1].split("}")[0]
    assert "--ws-primary-dark" in block


def test_best_text_on_picks_meet_graphical_floor_on_palette() -> None:
    for theme in THEMES:
        colors = palette(theme)
        for key in ("primary", "primaryDark", "success", "warning", "danger", "accent"):
            fill = colors.get(key)
            if not fill:
                continue
            pick = tokens.best_text_on(fill, "#FFFFFF")
            ratio = tokens.contrast_ratio(pick, fill)
            assert ratio >= 3.0, f"{theme} {key} pick {pick} on {fill} = {ratio:.2f}:1"


def test_a11y_sections_live_in_the_base() -> None:
    """Reduced-motion and focus rules ship through `themes/_base.css` so one
    edit covers every theme; the sync gate keeps the copies identical."""
    base = (ROOT_DIR / "themes/_base.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in base
    assert "section:focus-visible" in base
