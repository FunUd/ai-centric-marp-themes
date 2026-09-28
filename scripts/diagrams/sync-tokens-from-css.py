#!/usr/bin/env python3
"""sync-tokens-from-css.py — Sync theme-styles JSON from themes/*.css :root variables.

Single source of truth is the slide CSS. This script parses each theme's
``:root`` custom properties and writes the derived values back into
``scripts/diagrams/theme-styles/<theme>.json`` (colors / shapes / effects /
signature). Manual sections (mermaid / typography / drawio text) are preserved,
except drawio fill/stroke colors and the rounded flag which follow the CSS.

Usage:
    python scripts/diagrams/sync-tokens-from-css.py [--check] [--theme azure-clarity]

``--check`` is the CI gate. It reports drift for *every* field the sync would
write — colors, shapes, effects, signature and the derived draw.io styles — by
running the write path against a deep copy, so the gate can never disagree
with what a real sync produces.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
THEMES_DIR = SCRIPT_DIR.parent.parent / "themes"
STYLES_DIR = SCRIPT_DIR / "theme-styles"

sys.path.insert(0, str(SCRIPT_DIR))
from design_tokens import ensure_inside_label  # noqa: E402

THEME_FILES = {
    "azure-clarity": "azure-clarity.css",
    "crimson-clarity": "crimson-clarity.css",
    "prism-edge": "prism-edge.css",
    "nebula-glass": "nebula-glass.css",
    "warm-sunnyday": "warm-sunnyday.css",
    "slate-minimal": "slate-minimal.css",
}

# Per-theme CSS variable prefixes.
# NOTE: PREFIXES is kept for documentation; build_updates uses DIAGRAM_VAR_MAP.


def parse_root_vars(css_text: str) -> dict[str, str]:
    # Strip comments first: a `}` inside a comment would otherwise truncate :root.
    css_text = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    match = re.search(r":root\s*\{(.*?)\}", css_text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    out: dict[str, str] = {}
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block):
        out[name.strip()] = value.strip()
    return out


def resolve_value(value: str | None, vars_: dict[str, str]) -> str | None:
    """Resolve var(--x) / var(--x, fallback) references; None when unresolvable."""
    if not value:
        return None
    value = value.strip()
    match = re.match(r"var\(\s*(--[\w-]+)\s*(?:,\s*(.+?))?\s*\)$", value)
    if match:
        ref, fallback = match.group(1), match.group(2)
        resolved = resolve_value(vars_.get(ref), vars_)
        if resolved:
            return resolved
        if fallback:
            return resolve_value(fallback.strip(), vars_)
        return None
    if re.match(r"^#[0-9a-fA-F]{3,8}$", value) or value.startswith("rgba(") or value.startswith("rgb("):
        return value
    return None


# Diagram-aware variable mapping per theme. The diagram accent lives in CSS
# (`--pe-diagram-accent` / `--ng-diagram-accent`); the second suffix in each
# tuple is the legacy fallback so an older checkout without the token still
# resolves. Slide heading inks (e.g. prism --pe-accent:#111827) are
# intentionally NOT used as diagram accents.
DIAGRAM_VAR_MAP = {
    "azure-clarity": {"prefix": "--ac-", "accent": ("accent",)},
    "crimson-clarity": {"prefix": "--cc-", "accent": ("accent",)},
    "warm-sunnyday": {"prefix": "--ws-", "accent": ("accent",)},
    "prism-edge": {"prefix": "--pe-", "accent": ("diagram-accent", "cyan")},
    "slate-minimal": {"prefix": "--sm-", "accent": ("accent",)},
    "nebula-glass": {"prefix": "--ng-", "accent": ("diagram-accent", "secondary")},
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
        # For nebula-glass the NEBULA_KEEP keys are curated by design.
        if css_value and not (theme == "nebula-glass" and key in NEBULA_KEEP):
            return css_value
        return existing_colors.get(key, css_value or "")

    if theme == "nebula-glass":
        primary = get("primary") or existing_colors.get("primary", "#8B5CF6")
        accent = get(*mapping["accent"]) or existing_colors.get("accent", "#22D3EE")
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
            "accent": keep("accent", get(*mapping["accent"])),
            "text": keep("text", get("text", "ink-soft")),
            "textMuted": keep("textMuted", get("text-sub", "text-muted")),
            "background": keep("background", get("bg", "background")),
            "surface": keep("surface", get("white")),
            "border": keep("border", get("border")),
            "borderLight": keep("borderLight", get("border-light")),
            "success": keep("success", get("success", "highlight")),
            "warning": keep("warning", get("warning")),
            "danger": keep("danger", get("danger", *mapping["accent"])),
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


def drawio_updates(colors: dict, node_radius: float) -> dict[str, str]:
    """Derive the draw.io style strings from the (possibly just-updated) palette.

    Takes the *post-sync* colors and radius so the generated styles always
    match the palette written in the same pass. The accent node guarantees
    inside text >= 4.5:1 via `ensure_inside_label` (warm `primary` with
    white is 2.3:1, azure/nebula primaries sit 4.1-4.2:1), nudging the fill
    within its hue when even the best ink falls short.
    """
    rounded = 1 if node_radius else 0
    # `line` is an optional future token; today build_updates() never emits it,
    # so this falls back to `primary` by design.
    line = colors.get("line", colors["primary"])
    accent_ink, accent_fill = ensure_inside_label(colors["primary"])
    accent_fill = accent_fill or colors["primary"]
    return {
        "primaryNodeStyle": f"rounded={rounded};whiteSpace=wrap;html=1;fillColor={colors['primaryPale']};strokeColor={colors['primary']};fontColor={colors['text']};strokeWidth=1.5;",
        "accentNodeStyle": f"rounded={rounded};whiteSpace=wrap;html=1;fillColor={accent_fill};strokeColor={colors['primaryDark']};fontColor={accent_ink};fontStyle=1;",
        "edgeStyle": f"edgeStyle=orthogonalEdgeStyle;html=1;strokeColor={line};strokeWidth=1.5;endArrow=block;endFill=1;",
    }


def apply_to(data: dict, updates: dict) -> list[str]:
    """Mutate ``data`` in place and return one change line per field updated.

    This is the single source of truth for *what counts as drift*: ``--check``
    runs it against a deep copy, the write path runs it against the real
    document, so the CI gate can never disagree with what a sync would write.
    Covers colors, shapes, effects, signature and the derived draw.io styles.
    """
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

    for key, value in drawio_updates(data["colors"], data["shapes"]["nodeRadius"]).items():
        if data["drawio"].get(key) != value:
            changes.append(f"drawio.{key} synced")
            data["drawio"][key] = value

    return changes


def apply_updates(theme: str, updates: dict) -> tuple[bool, list[str]]:
    import tempfile

    path = STYLES_DIR / f"{theme}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RuntimeError(f"cannot read {path}: {error}") from error
    changes = apply_to(data, updates)

    if changes:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=str(path.parent), delete=False
            ) as tmp:
                json.dump(data, tmp, indent=2, ensure_ascii=False)
                tmp.write("\n")
                tmp_path = Path(tmp.name)
            tmp_path.replace(path)
        except OSError as error:
            raise RuntimeError(f"cannot write {path}: {error}") from error
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
        path = STYLES_DIR / f"{theme}.json"
        try:
            css_text = css_path.read_text(encoding="utf-8")
            vars_ = parse_root_vars(css_text)
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print(f"[FAILED] {theme}: cannot read input: {error}", file=sys.stderr)
            drift.append(theme)
            continue
        updates = build_updates(theme, vars_, css_text, existing)
        if args.check:
            # Probe a copy with the very same code the write path uses, so the
            # gate reports drift for *every* synced field (colors, shapes,
            # effects, signature, draw.io styles) — not just `signature`.
            probe = copy.deepcopy(existing)
            pending = apply_to(probe, updates)
            if pending:
                drift.append(theme)
                print(f"[DRIFT] {theme}: {len(pending)} field(s) out of sync with {THEME_FILES[theme]}")
                for line in pending:
                    print(f"    - {line}")
                print(f"    fix: python scripts/diagrams/sync-tokens-from-css.py --theme {theme}")
            continue
        changed, changes = apply_updates(theme, updates)
        if changed:
            print(f"[SYNC] {theme}:")
            for line in changes:
                print(f"  - {line}")
        else:
            print(f"[OK] {theme}: already in sync")
    if drift:
        print(
            f"FAILED: {len(drift)} theme(s) drifted: {', '.join(drift)}\n"
            f"       run: python scripts/diagrams/sync-tokens-from-css.py",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
