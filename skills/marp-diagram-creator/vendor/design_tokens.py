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

# Named CSS colors Mermaid may emit in Gantt SVGs (fill:lightgrey etc.).
NAMED_COLORS = {
    "black": "#000000",
    "white": "#FFFFFF",
    "lightgrey": "#D3D3D3",
    "lightgray": "#D3D3D3",
    "grey": "#808080",
    "gray": "#808080",
    "red": "#FF0000",
    "navy": "#000080",
    "lightblue": "#ADD8E6",
    "green": "#008000",
    "yellow": "#FFFF00",
}


def normalize_color(value: str | None) -> str | None:
    """Normalize a CSS color to `#RRGGBB` uppercase, or None if unparsable.

    Handles `#rgb`/`#rrggbb`, `hsl(h, s%, l%)`, `rgb(r, g, b)`, and the
    small named-color set Mermaid emits (`white`, `lightgrey`, `grey`,
    `red`, `navy`). `transparent`/`var()`/empty return None.
    """
    import colorsys
    import re as _re

    if not value or not isinstance(value, str):
        return None
    text = value.strip().lower()
    if text in ("transparent", "none", "currentcolor"):
        return None
    if text.startswith("var("):
        return None
    if text in NAMED_COLORS:
        return NAMED_COLORS[text]
    if text.startswith("#"):
        body = text.lstrip("#")
        if len(body) == 3:
            body = "".join(ch * 2 for ch in body)
        if len(body) != 6:
            return None
        try:
            int(body, 16)
        except ValueError:
            return None
        return "#" + body.upper()
    hsl = _re.match(
        r"hsla?\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%", text
    )
    if hsl:
        try:
            h, s, light = float(hsl.group(1)), float(hsl.group(2)), float(hsl.group(3))
        except ValueError:
            return None
        r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, light / 100.0, s / 100.0)
        return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))
    rgb = _re.match(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)", text)
    if rgb:
        try:
            r, g, b = (max(0, min(255, round(float(rgb.group(i))))) for i in (1, 2, 3))
        except ValueError:
            return None
        return "#%02X%02X%02X" % (r, g, b)
    return None


def adjust_lightness(hex_color: str, delta: float) -> str | None:
    """Shift an `#RRGGBB` color's lightness by `delta` (-1..1)."""
    import colorsys

    norm = normalize_color(hex_color)
    if norm is None:
        return None
    body = norm.lstrip("#")
    r, g, b = (int(body[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, light, s = colorsys.rgb_to_hls(r, g, b)
    light = max(0.0, min(1.0, light + delta))
    r2, g2, b2 = colorsys.hls_to_rgb(h, light, s)
    return "#%02X%02X%02X" % (round(r2 * 255), round(g2 * 255), round(b2 * 255))


def soften_mindmap_fill(hex_color: str, background: str | None) -> str | None:
    """Soften a saturated mindmap fill for light canvases (premium pastel).

    Keeps hue, lifts lightness ~+0.12 (cap 0.88) and trims saturation to
    75% (floor 0.35) so dark bold CJK stays 8+:1 while the rainbow harshness
    drops. Dark canvases keep the original fill — white ink already passes
    and lightening would only wash out the node vs the dark base.
    """
    import colorsys

    norm = normalize_color(hex_color)
    bg = normalize_color(background)
    if norm is None or bg is None:
        return norm
    if (_luminance(bg) or 1.0) <= 0.4:
        return norm
    body = norm.lstrip("#")
    r, g, b = (int(body[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, light, s = colorsys.rgb_to_hls(r, g, b)
    light = min(0.88, light + 0.12)
    s = max(0.35, s * 0.75)
    r2, g2, b2 = colorsys.hls_to_rgb(h, light, s)
    return "#%02X%02X%02X" % (round(r2 * 255), round(g2 * 255), round(b2 * 255))


def ensure_graphical_contrast(
    foreground: str | None, background: str | None, minimum: float = 3.0
) -> str | None:
    """Nudge `foreground` lightness until it reaches `minimum` vs `background`.

    Preserves hue/saturation; darkens on light backgrounds and lightens on
    dark ones. Returns the original (normalized) color when it already passes
    or when either side is unparsable.
    """
    fg = normalize_color(foreground)
    bg = normalize_color(background)
    if fg is None or bg is None:
        return fg
    if contrast_ratio(fg, bg) >= minimum:
        return fg
    bg_lum = _luminance(bg)
    if bg_lum is None:
        return fg
    # Light canvas -> darken in 5% steps; dark canvas -> lighten.
    step = -0.05 if bg_lum > 0.4 else 0.05
    candidate: str | None = fg
    for _ in range(20):
        nxt = adjust_lightness(candidate or fg, step)
        if nxt is None or nxt == candidate:
            break
        candidate = nxt
        if contrast_ratio(candidate, bg) >= minimum:
            return candidate
    return candidate


def graphical_ink(theme_data: dict[str, Any], minimum: float = 3.0) -> str:
    """Stroke color guaranteed `minimum` vs the slide background.

    Prefers the theme line color, then primary/primaryDark/text, so Gantt
    bars and mindmap edges stay visible even when Mermaid's derived fills
    (white active tasks, pastel mindmap edges) wash out on the canvas.
    """
    ctx = theme_context(theme_data)
    background = ctx.get("background", "#FFFFFF")
    candidates = [
        ctx.get("line"),
        ctx.get("primary"),
        ctx.get("dark"),
        ctx.get("accent"),
        ctx.get("text"),
    ]
    best: str | None = None
    best_ratio = 0.0
    for cand in candidates:
        norm = normalize_color(cand) if isinstance(cand, str) else None
        if norm is None:
            continue
        ratio = contrast_ratio(norm, background)
        if ratio > best_ratio:
            best_ratio, best = ratio, norm
        if ratio >= minimum:
            return norm
    if best is not None:
        fixed = ensure_graphical_contrast(best, background, minimum)
        return fixed or best
    return FALLBACK_INK


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


def contrast_ratio(first: str, second: str) -> float:
    """WCAG contrast ratio (1-21) of two `#rgb`/`#rrggbb` colors.

    Returns 1.0 when either side is unparsable, so callers degrade to
    "no information" instead of crashing on `transparent` or `var()` input.
    """
    first_lum = _luminance(first.strip()) if isinstance(first, str) else None
    second_lum = _luminance(second.strip()) if isinstance(second, str) else None
    if first_lum is None or second_lum is None:
        return 1.0
    lighter, darker = sorted((first_lum, second_lum), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def best_text_on(background: str | None, light: str, dark: str = FALLBACK_INK, threshold: float = 0.4) -> str:
    """Pick the more readable of `light`/`dark` text on a fill.

    Selection is by maximum WCAG contrast ratio — a fixed luminance threshold
    picked white-on-green (2.9:1) for saturated mid-luminance fills. `threshold`
    is kept for signature compatibility and no longer consulted.
    """
    if not background or not background.strip().startswith("#"):
        return light
    if _luminance(background.strip()) is None:
        return light
    if contrast_ratio(light, background) >= contrast_ratio(dark, background):
        return light
    return dark


def _merge_section(defaults: dict[str, Any], overrides: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(defaults)
    if overrides:
        merged.update(overrides)
    return merged


def load_design_tokens(theme_name: str) -> dict[str, Any]:
    """Load and normalize theme design tokens from theme-styles JSON."""
    import sys

    resolved = theme_name if theme_name in VALID_THEMES else DEFAULT_THEME
    if theme_name not in VALID_THEMES:
        print(
            f"[WARN] unknown theme {theme_name!r}; falling back to {DEFAULT_THEME!r} "
            f"(valid: {sorted(VALID_THEMES)})",
            file=sys.stderr,
        )
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
