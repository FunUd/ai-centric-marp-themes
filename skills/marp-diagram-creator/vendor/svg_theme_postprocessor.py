from __future__ import annotations

import re
from typing import Any

from design_tokens import mermaid_postprocess_rules, theme_context
from svg_filters import build_filter_defs


def _replace_rect_radius(svg: str, radius: float, large_radius: float) -> str:
    def replacer(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "data-diagram-role=\"marker\"" in tag or "role=\"marker\"" in tag:
            rx = max(0, radius // 2) if radius else 0
        elif "swimlane" in tag.lower():
            rx = large_radius
        else:
            rx = radius
        # Convert to int if it's a whole number
        rx_val = int(rx) if rx == int(rx) else rx
        if rx:
            if re.search(r"\brx=", tag):
                tag = re.sub(r"\brx='[^']*'", f"rx='{rx_val}'", tag)
                tag = re.sub(r'\brx="[^"]*"', f'rx="{rx_val}"', tag)
                tag = re.sub(r"\bry='[^']*'", f"ry='{rx_val}'", tag)
                tag = re.sub(r'\bry="[^"]*"', f'ry="{rx_val}"', tag)
            else:
                # Add rx/ry before the closing
                if "/>" in tag:
                    tag = tag.replace("/>", f" rx='{rx_val}' ry='{rx_val}'/>")
                else:
                    tag = tag.replace(">", f" rx='{rx_val}' ry='{rx_val}'>", 1)
        else:
            tag = re.sub(r"\s*rx='[^']*'", "", tag)
            tag = re.sub(r'\s*rx="[^"]*"', "", tag)
            tag = re.sub(r"\s*ry='[^']*'", "", tag)
            tag = re.sub(r'\s*ry="[^"]*"', "", tag)
        return tag

    return re.sub(r"<rect\b[^>]*/?>", replacer, svg)


def _replace_font_family(svg: str, font_family: str) -> str:
    escaped = font_family.replace('"', "'")
    svg = re.sub(r'font-family="[^"]*"', f'font-family="{escaped}"', svg)
    svg = re.sub(r"font-family='[^']*'", f"font-family='{escaped}'", svg)
    if "font-family" not in svg:
        svg = svg.replace("<text ", f'<text font-family="{escaped}" ', 1)
    return svg


def _inject_node_filters(svg: str, effects: dict[str, Any]) -> str:
    if not effects.get("nodeShadowEnabled") and not effects.get("glowEnabled"):
        return svg
    filter_id = "theme-glow" if effects.get("glowEnabled") else "theme-shadow"
    if f'id="{filter_id}"' not in svg and f"id='{filter_id}'" not in svg:
        # Insert only the inner <filter> element into the first existing
        # <defs> block. Mermaid emits several <defs> blocks, so a whole
        # <defs>...</defs> wrapper must NOT be spliced in (orphaned <filter>).
        inner = build_filter_defs(effects)
        inner = re.sub(r"^\s*<defs>|</defs>\s*$", "", inner)
        if "<defs/>" in svg:
            svg = svg.replace("<defs/>", f"<defs>{inner}</defs>", 1)
        elif "<defs>" in svg:
            svg = svg.replace("<defs>", f"<defs>{inner}", 1)
        else:
            svg = re.sub(r"(<svg[^>]*>)", rf"\1<defs>{inner}</defs>", svg, count=1)

    def add_filter(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "filter=" in tag or "data-diagram-role=\"connector\"" in tag:
            return tag
        if "stroke=" not in tag and "fill=" not in tag:
            return tag
        return tag.replace("/>", f' filter="url(#{filter_id})"/>')

    return re.sub(r"<rect\b[^>]*/?>", add_filter, svg)


def _recolor_arrows(svg: str, line_color: str) -> str:
    """Force Mermaid's default black/gray arrowheads onto the theme line color."""
    svg = re.sub(r"#0b0b0b", line_color, svg, flags=re.IGNORECASE)
    svg = re.sub(
        r"(\.arrowheadPath\s*\{\s*fill\s*:\s*)#[0-9a-fA-F]{3,6}",
        r"\1" + line_color,
        svg,
    )
    return svg


def _remove_default_gray_shadow(svg: str) -> str:
    """Drop Mermaid's built-in gray drop-shadow so only the theme filter remains."""
    svg = re.sub(
        r"filter\s*:\s*drop-shadow\s*\(\s*1px\s+2px\s+2px\s+rgba\(185,185,185,1\)\s*\)",
        "filter:none",
        svg,
    )
    return svg


def _thicken_edges(svg: str, stroke_width: float) -> str:
    """Lift Mermaid's 1px edges toward the theme stroke width for slide legibility."""
    target = max(1.5, float(stroke_width))
    width_token = ("%g" % target) + "px"
    svg = re.sub(
        r"(\.edgePath\s+\.path\s*\{\s*stroke\s*:[^;]+;\s*stroke-width\s*:\s*)1px",
        r"\g<1>" + width_token,
        svg,
    )
    svg = re.sub(
        r"(\.flowchart-link\s*\{\s*stroke\s*:[^;]+;\s*)fill\s*:\s*none",
        r"\g<1>stroke-width:" + width_token + ";fill:none",
        svg,
    )
    return svg


def postprocess_svg(svg: str, theme_data: dict[str, Any]) -> str:
    """Apply theme tokens to an external-engine SVG without changing layout."""
    rules = mermaid_postprocess_rules(theme_data)
    ctx = theme_context(theme_data)
    svg = _replace_font_family(svg, rules["fontFamily"])
    svg = _replace_rect_radius(svg, float(rules["nodeRadius"]), float(rules["nodeRadiusLg"]))
    svg = _recolor_arrows(svg, ctx["line"])
    svg = _remove_default_gray_shadow(svg)
    svg = _thicken_edges(svg, float(rules["strokeWidth"]))
    svg = _inject_node_filters(svg, ctx["effects"])
    return svg
