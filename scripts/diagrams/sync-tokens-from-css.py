#!/usr/bin/env python3
"""sync-tokens-from-css.py — Sync theme-styles JSON from themes/*.css :root variables.

Single source of truth is the slide CSS. This script parses each theme's
``:root`` custom properties and writes the derived values back into
``scripts/diagrams/theme-styles/<theme>.json`` (colors / shapes / effects /
signature). Manual sections (mermaid / typography / drawio text) are preserved,
except drawio fill/stroke colors and the rounded flag which follow the CSS.

Usage:
    python scripts/diagrams/sync-tokens-from-css.py [--check] [--theme azure-clarity]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
THEMES_DIR = SCRIPT_DIR.parent.parent / "themes"
STYLES_DIR = SCRIPT_DIR / "theme-styles"

THEME_FILES = {
    "azure-clarity": "azure-clarity.css",
    "crimson-clarity": "crimson-clarity.css",
    "prism-edge": "prism-edge.css",
    "nebula-glass": "nebula-glass.css",
    "warm-sunnyday": "warm-sunnyday.css",
    "slate-minimal": "slate-minimal.css",
}

# Per-theme CSS variable prefixes (warm-sunnyday reuses --ac- inside its own file).
# NOTE: PREFIXES is kept for documentation; build_updates uses DIAGRAM_VAR_MAP.


def parse_root_vars(css_text: str) -> dict[str, str]:
    match = re.search(r":root\s*\{(.*?)\}", css_text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    # Strip comments to avoid capturing example vars.
    block = re.sub(r"/\*.*?\*/", "", block, flags=re.DOTALL)
    out: dict[str, str] = {}
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block):
        out[name.strip()] = value.strip()
    return out


def resolve_value(value: str | None, vars_: dict[str, str]) -> str | None:
    """Resolve var(--x) references; return None for unresolvable values."""
    if not value:
        return None
    value = value.strip()
    match = re.match(r"var\(\s*(--[\w-]+)\s*\)", value)
    if match:
        return resolve_value(vars_.get(match.group(1)), vars_)
    if re.match(r"^#[0-9a-fA-F]{3,8}$", value) or value.startswith("rgba(") or value.startswith("rgb("):
        return value
    return None


# Diagram-aware variable mapping per theme. CSS heading inks (e.g. prism
# --pe-accent:#111827) are intentionally NOT used as diagram accents; the
# diagram accent stays the theme's graphic secondary (cyan) for visibility.
DIAGRAM_VAR_MAP = {
    "azure-clarity": {"prefix": "--ac-", "accent": "accent"},
    "crimson-clarity": {"prefix": "--cc-", "accent": "accent"},
    "warm-sunnyday": {"prefix": "--ac-", "accent": "accent"},
    "prism-edge": {"prefix": "--pe-", "accent": "cyan"},
    "slate-minimal": {"prefix": "--sm-", "accent": "accent"},
    "nebula-glass": {"prefix": "--ng-", "accent": "secondary"},
}

# Nebula :root lacks derived palette entries; keep the curated JSON values.
NEBULA_KEEP = {"primaryDark", "primaryLight", "primaryPale", "success", "warning", "surface", "border", "borderLight"}


def px_to_float(value: str | None) -> float | None:
    if not value:
        return None
    match = re.match(r"(-?\d+(?:\.\d+)?)\s*px", value)
    if match:
        return float(match.group(1))
    return None


def build_updates(theme: str, vars_: dict[str, str], css_text: str, existing: dict) -> dict:
    mapping = DIAGRAM_VAR_MAP[theme]
    prefix = mapping["prefix"]
    existing_colors = existing.get("colors", {})
    existing_shapes = existing.get("shapes", {})

    def get(*suffixes: str) -> str | None:
        for suffix in suffixes:
            resolved = resolve_value(vars_.get(prefix + suffix), vars_)
            if resolved:
                return resolved
        return None

    def keep(key: str, css_value: str | None) -> str:
        # Only adopt CSS values that resolve to concrete colors; otherwise
        # keep the curated JSON value (e.g. Nebula derived palette).
        if css_value and (theme not in NEBULA_KEEP or key not in NEBULA_KEEP):
            return css_value
        return existing_colors.get(key, css_value or "")

    if theme == "nebula-glass":
        primary = get("primary") or existing_colors.get("primary", "#8B5CF6")
        accent = get("secondary") or existing_colors.get("accent", "#22D3EE")
        text = get("text") or existing_colors.get("text", "#F5F7FB")
        text_muted = get("text-muted") or existing_colors.get("textMuted", text)
        bg = get("bg") or existing_colors.get("background", "#040712")
        # Keep curated glass borders: faint white 0.09 is too weak for diagram strokes.
        border = existing_colors.get("border", "#38BDF8")
        border_light = existing_colors.get("borderLight", border)
        danger = get("accent") or existing_colors.get("danger", "#FB7185")
        colors = {
            "primary": primary,
            "primaryDark": existing_colors.get("primaryDark", "#6D28D9"),
            "primaryLight": existing_colors.get("primaryLight", "#C4B5FD"),
            "primaryPale": existing_colors.get("primaryPale", "#1E1838"),
            "accent": accent,
            "text": text,
            "textMuted": text_muted,
            "background": bg,
            "surface": existing_colors.get("surface", "#101525"),
            "border": border,
            "borderLight": existing_colors.get("borderLight", border),
            "success": existing_colors.get("success", "#34D399"),
            "warning": existing_colors.get("warning", "#FBBF24"),
            "danger": danger,
        }
        radius = px_to_float(vars_.get("--ng-radius")) or existing_shapes.get("nodeRadius", 14)
        radius_lg = px_to_float(vars_.get("--ng-radius-lg")) or existing_shapes.get("nodeRadiusLg", 20)
        gradient_to = "#22D3EE"
        shadow = None
    else:
        primary = get("primary") or existing_colors.get("primary", "#2C7BE5")
        colors = {
            "primary": primary,
            "primaryDark": keep("primaryDark", get("primary-dark")),
            "primaryLight": keep("primaryLight", get("primary-light")),
            "primaryPale": keep("primaryPale", get("primary-pale")),
            "accent": keep("accent", get(mapping["accent"])),
            "text": keep("text", get("text", "ink-soft")),
            "textMuted": keep("textMuted", get("text-sub", "text-muted")),
            "background": keep("background", get("bg", "background")),
            "surface": keep("surface", get("white")),
            "border": keep("border", get("border")),
            "borderLight": keep("borderLight", get("border-light")),
            "success": keep("success", get("success", "highlight")),
            "warning": keep("warning", get("warning")),
            "danger": keep("danger", get("danger", mapping["accent"])),
        }
        radius = px_to_float(get("radius", "radius-sm"))
        if radius is None:
            radius = existing_shapes.get("nodeRadius", 0)
        radius_lg = px_to_float(get("radius-lg"))
        if radius_lg is None:
            radius_lg = existing_shapes.get("nodeRadiusLg", radius)
        gradient_to = get("cyan", "secondary") or colors["primaryLight"]
        shadow = get("shadow")

    has_top_border = "border-top: 4px" in css_text
    has_glass = "backdrop-filter" in css_text and ("glass" in css_text.lower())
    has_glow = "glow" in css_text.lower()

    return {
        "colors": colors,
        "shapes": {"nodeRadius": float(radius), "nodeRadiusLg": float(radius_lg)},
        "effects": {"nodeShadowColor": shadow},
        "signature": {
            "source": f"themes/{THEME_FILES[theme]}",
            "gradientFrom": colors["primary"],
            "gradientTo": gradient_to,
            "topBorderWidth": 4 if has_top_border else 0,
            "hasGlass": has_glass,
            "hasGlow": has_glow,
        },
    }


def apply_updates(theme: str, updates: dict) -> tuple[bool, list[str]]:
    path = STYLES_DIR / f"{theme}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    changes: list[str] = []

    for key, value in updates["colors"].items():
        if value and data["colors"].get(key) != value:
            changes.append(f"colors.{key}: {data['colors'].get(key)} -> {value}")
            data["colors"][key] = value
    for key, value in updates["shapes"].items():
        if data["shapes"].get(key) != value:
            changes.append(f"shapes.{key}: {data['shapes'].get(key)} -> {value}")
            data["shapes"][key] = value
    shadow = updates["effects"]["nodeShadowColor"]
    if shadow and data["effects"].get("nodeShadowColor") != shadow:
        changes.append(f"effects.nodeShadowColor -> {shadow}")
        data["effects"]["nodeShadowColor"] = shadow
        # Do NOT flip nodeShadowEnabled: slate-minimal sets box-shadow:none
        # and keeps shadows disabled by design.
    if updates["signature"] != data.get("signature"):
        changes.append("signature refreshed")
        data["signature"] = updates["signature"]

    # Keep drawio geometry in sync with the CSS radius + palette.
    rounded = 1 if data["shapes"]["nodeRadius"] else 0
    c = data["colors"]
    drawio_updates = {
        "primaryNodeStyle": f"rounded={rounded};whiteSpace=wrap;html=1;fillColor={c['primaryPale']};strokeColor={c['primary']};fontColor={c['text']};strokeWidth=1.5;",
        "accentNodeStyle": f"rounded={rounded};whiteSpace=wrap;html=1;fillColor={c['primary']};strokeColor={c['primaryDark']};fontColor=#FFFFFF;fontStyle=1;",
        "edgeStyle": f"edgeStyle=orthogonalEdgeStyle;html=1;strokeColor={c['line'] if 'line' in c else c['primary']};strokeWidth=1.5;endArrow=block;endFill=1;",
    }
    for key, value in drawio_updates.items():
        if data["drawio"].get(key) != value:
            changes.append(f"drawio.{key} synced")
            data["drawio"][key] = value

    if changes:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return bool(changes), changes


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync diagram tokens from theme CSS.")
    parser.add_argument("--check", action="store_true", help="Fail if any theme drifts from CSS.")
    parser.add_argument("--theme", choices=sorted(THEME_FILES), help="Sync a single theme.")
    args = parser.parse_args()

    themes = [args.theme] if args.theme else sorted(THEME_FILES)
    drift: list[str] = []
    for theme in themes:
        css_path = THEMES_DIR / THEME_FILES[theme]
        css_text = css_path.read_text(encoding="utf-8")
        vars_ = parse_root_vars(css_text)
        path = STYLES_DIR / f"{theme}.json"
        existing = json.loads(path.read_text(encoding="utf-8"))
        updates = build_updates(theme, vars_, css_text, existing)
        if args.check:
            if existing.get("signature") != updates["signature"]:
                drift.append(theme)
                print(f"[DRIFT] {theme}: signature out of sync with {THEME_FILES[theme]}")
            continue
        changed, changes = apply_updates(theme, updates)
        if changed:
            print(f"[SYNC] {theme}:")
            for line in changes:
                print(f"  - {line}")
        else:
            print(f"[OK] {theme}: already in sync")
    if drift:
        print(f"FAILED: {len(drift)} theme(s) drifted: {', '.join(drift)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
