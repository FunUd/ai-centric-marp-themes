from __future__ import annotations

import json
from pathlib import Path
from typing import Any

THEME_STYLES_DIR = Path(__file__).resolve().parent / "theme-styles"
DEFAULT_THEME = "azure-clarity"
VALID_THEMES = {
    "azure-clarity",
    "crimson-clarity",
    "prism-edge",
    "nebula-glass",
    "warm-sunnyday",
    "slate-minimal",
}

DEFAULT_SHAPES: dict[str, float | int] = {
    "nodeRadius": 0,
    "nodeRadiusLg": 0,
    "markerRadius": 0,
    "strokeWidth": 1.5,
    "strokeWidthBold": 2.5,
    "nodePaddingX": 12,
    "nodePaddingY": 8,
}

DEFAULT_EFFECTS: dict[str, Any] = {
    "nodeShadowEnabled": False,
    "nodeShadowColor": "rgba(0, 0, 0, 0.08)",
    "nodeShadowBlur": 12,
    "nodeShadowOffsetY": 4,
    "glowEnabled": False,
    "glowColor": None,
    "glowBlur": 10,
    "glassEnabled": False,
    "glassFill": None,
    "glassStroke": None,
}

DEFAULT_TYPOGRAPHY: dict[str, Any] = {
    "titleSize": 22,
    "labelSize": 15,
    "captionSize": 12,
    "titleWeight": "bold",
    "labelWeight": "normal",
}

NODE_VARIANTS = {
    "primary": ("pale", "primary"),
    "accent": ("primary", "dark"),
    "secondary": ("light", "primary"),
    "surface": ("surface", "border"),
    "marker": ("primary", "primary"),
}

# Near-black ink for text on light fills (used when the theme text color
# itself is light, e.g. Nebula Glass dark mode + white node).
FALLBACK_INK = "#1A1A2E"


def _luminance(hex_color: str) -> float | None:
    """Relative luminance (0-1) of a #rgb/#rrggbb color, or None if unparsable."""
    value = hex_color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    if len(value) != 6:
        return None
    try:
        channels = [int(value[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    except ValueError:
        return None
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def best_text_on(background: str | None, light: str, dark: str = FALLBACK_INK, threshold: float = 0.4) -> str:
    """Pick the readable text color for a fill: dark ink on light fills."""
    if not background or not background.strip().startswith("#"):
        return light
    luminance = _luminance(background.strip())
    if luminance is None:
        return light
    return dark if luminance > threshold else light


def _merge_section(defaults: dict[str, Any], overrides: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(defaults)
    if overrides:
        merged.update(overrides)
    return merged


def load_design_tokens(theme_name: str) -> dict[str, Any]:
    """Load and normalize theme design tokens from theme-styles JSON."""
    resolved = theme_name if theme_name in VALID_THEMES else DEFAULT_THEME
    theme_file = THEME_STYLES_DIR / f"{resolved}.json"
    if not theme_file.exists():
        theme_file = THEME_STYLES_DIR / f"{DEFAULT_THEME}.json"
    with theme_file.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    colors = raw.get("colors", {})
    return {
        "theme": raw.get("theme", resolved),
        "name": raw.get("name", resolved),
        "mode": raw.get("mode", "light"),
        "fontFamily": raw.get("fontFamily", "sans-serif"),
        "colors": colors,
        "shapes": _merge_section(DEFAULT_SHAPES, raw.get("shapes")),
        "effects": _merge_section(DEFAULT_EFFECTS, raw.get("effects")),
        "typography": _merge_section(DEFAULT_TYPOGRAPHY, raw.get("typography")),
        "signature": raw.get("signature", {}),
        "mermaid": raw.get("mermaid", {}),
        "drawio": raw.get("drawio", {}),
    }


def theme_context(theme_data: dict[str, Any]) -> dict[str, Any]:
    """Build a flat rendering context from theme JSON (colors + tokens)."""
    colors = theme_data.get("colors", {})
    shapes = _merge_section(DEFAULT_SHAPES, theme_data.get("shapes"))
    effects = _merge_section(DEFAULT_EFFECTS, theme_data.get("effects"))
    typography = _merge_section(DEFAULT_TYPOGRAPHY, theme_data.get("typography"))
    return {
        "primary": colors.get("primary", "#2C7BE5"),
        "dark": colors.get("primaryDark", "#1B5FC0"),
        "light": colors.get("primaryLight", "#D0EBFF"),
        "pale": colors.get("primaryPale", "#EDF5FF"),
        "accent": colors.get("accent", "#1B4F72"),
        "text": colors.get("text", "#1A1A2E"),
        "muted": colors.get("textMuted", "#5A6C7D"),
        "line": colors.get("line", "#2C7BE5"),
        "surface": colors.get("surface", "#FFFFFF"),
        "border": colors.get("border", "#B8D4E8"),
        "background": colors.get("background", "transparent"),
        "success": colors.get("success", "#27AE60"),
        "warning": colors.get("warning", "#F39C12"),
        "danger": colors.get("danger", "#E74C3C"),
        "font": theme_data.get("fontFamily", "sans-serif"),
        "shapes": shapes,
        "effects": effects,
        "typography": typography,
        "signature": theme_data.get("signature", {}),
    }


def node_style(ctx: dict[str, Any], variant: str = "primary", *, large: bool = False) -> dict[str, Any]:
    """Return SVG rect styling kwargs for a themed node."""
    fill_key, stroke_key = NODE_VARIANTS.get(variant, NODE_VARIANTS["primary"])
    effects = ctx["effects"]
    fill = effects.get("glassFill") if effects.get("glassEnabled") and variant == "primary" else ctx[fill_key]
    stroke = effects.get("glassStroke") if effects.get("glassEnabled") and variant == "primary" else ctx[stroke_key]
    radius = ctx["shapes"]["nodeRadiusLg" if large else "nodeRadius"]
    style: dict[str, Any] = {
        "fill": fill,
        "stroke": stroke,
        "stroke-width": ctx["shapes"]["strokeWidth"],
    }
    if radius:
        style["rx"] = radius
        style["ry"] = radius
    filter_id = None
    if effects.get("glowEnabled"):
        filter_id = "theme-glow"
    elif effects.get("nodeShadowEnabled"):
        filter_id = "theme-shadow"
    if filter_id:
        style["filter"] = f"url(#{filter_id})"
    return style


def drawio_rect_radius(theme_data: dict[str, Any], style_map: dict[str, str]) -> float:
    """Compute draw.io rect corner radius from theme tokens."""
    shapes = _merge_section(DEFAULT_SHAPES, theme_data.get("shapes"))
    if "swimlane" in style_map:
        return float(shapes["nodeRadiusLg"])
    return float(shapes["nodeRadius"])


def mermaid_postprocess_rules(theme_data: dict[str, Any]) -> dict[str, Any]:
    """Rules for Mermaid/draw.io SVG post-processing."""
    ctx = theme_context(theme_data)
    return {
        "fontFamily": theme_data.get("fontFamily", "sans-serif"),
        "nodeRadius": ctx["shapes"]["nodeRadius"],
        "nodeRadiusLg": ctx["shapes"]["nodeRadiusLg"],
        "strokeWidth": ctx["shapes"]["strokeWidth"],
        "shadowEnabled": ctx["effects"]["nodeShadowEnabled"],
        "glowEnabled": ctx["effects"]["glowEnabled"],
    }
