from __future__ import annotations

import html
import math
from typing import Iterable

from design_tokens import node_style


def _num(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def escape_xml(value: str) -> str:
    return html.escape(str(value), quote=True)


def wrap_text(value: str, max_chars: int) -> str:
    """Wrap labels by characters without breaking explicit line breaks."""
    if max_chars <= 0:
        return str(value)
    lines: list[str] = []
    for source_line in str(value).splitlines() or [""]:
        while len(source_line) > max_chars:
            lines.append(source_line[:max_chars])
            source_line = source_line[max_chars:]
        lines.append(source_line)
    return "\n".join(lines)


def _attrs(role: str, attrs: dict[str, object]) -> str:
    values = {"data-diagram-role": role, **attrs}
    return " ".join(
        f'{key}="{escape_xml(_num(value) if isinstance(value, float) else str(value))}"'
        for key, value in values.items()
        if value is not None
    )


def svg_group(elements: Iterable[str], transform: str | None = None, role: str = "group") -> str:
    attrs = _attrs(role, {"transform": transform})
    return f"<g {attrs}>{''.join(elements)}</g>"


def svg_rect(x: float, y: float, width: float, height: float, **kwargs: object) -> str:
    role = str(kwargs.pop("role", "node"))
    return f"<rect {_attrs(role, {'x': x, 'y': y, 'width': width, 'height': height, **kwargs})} />"


def svg_circle(cx: float, cy: float, radius: float, **kwargs: object) -> str:
    role = str(kwargs.pop("role", "node"))
    return f"<circle {_attrs(role, {'cx': cx, 'cy': cy, 'r': radius, **kwargs})} />"


def svg_ellipse(cx: float, cy: float, rx: float, ry: float, **kwargs: object) -> str:
    role = str(kwargs.pop("role", "node"))
    return f"<ellipse {_attrs(role, {'cx': cx, 'cy': cy, 'rx': rx, 'ry': ry, **kwargs})} />"


def svg_polygon(points: Iterable[tuple[float, float]], **kwargs: object) -> str:
    role = str(kwargs.pop("role", "node"))
    point_text = " ".join(f"{_num(x)},{_num(y)}" for x, y in points)
    return f"<polygon {_attrs(role, {'points': point_text, **kwargs})} />"


def svg_path(d: str, **kwargs: object) -> str:
    role = str(kwargs.pop("role", "connector"))
    return f"<path {_attrs(role, {'d': d, **kwargs})} />"


def svg_line(x1: float, y1: float, x2: float, y2: float, **kwargs: object) -> str:
    role = str(kwargs.pop("role", "connector"))
    return f"<line {_attrs(role, {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, **kwargs})} />"


def svg_arrow(x1: float, y1: float, x2: float, y2: float, color: str, **kwargs: object) -> str:
    angle = math.atan2(y2 - y1, x2 - x1)
    size = float(kwargs.pop("size", 7))
    left = (x2 - size * math.cos(angle - math.pi / 6), y2 - size * math.sin(angle - math.pi / 6))
    right = (x2 - size * math.cos(angle + math.pi / 6), y2 - size * math.sin(angle + math.pi / 6))
    return svg_line(x1, y1, x2, y2, stroke=color, **kwargs) + svg_polygon(
        [(x2, y2), left, right], role="connector", fill=color
    )


def svg_text(x: float, y: float, text: str, **kwargs: object) -> str:
    role = str(kwargs.pop("role", "label"))
    attrs = _attrs(role, {"x": x, "y": y, **kwargs})
    lines = str(text).splitlines() or [""]
    if len(lines) == 1:
        content = escape_xml(lines[0])
    else:
        line_height = float(kwargs.get("font-size", 14)) * 1.2
        content = "".join(
            f'<tspan x="{_num(x)}" dy="{_num(0 if index == 0 else line_height)}">{escape_xml(line)}</tspan>'
            for index, line in enumerate(lines)
        )
    return f"<text {attrs}>{content}</text>"


def svg_document(
    width: float, height: float, elements: Iterable[str], background: str = "transparent", filter_defs: str = ""
) -> str:
    defs = filter_defs or ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_num(width)} {_num(height)}" width="{_num(width)}" height="{_num(height)}" style="background:{escape_xml(background)}">{defs}{"".join(elements)}</svg>'


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    """Parse #rgb/#rrggbb into channels; fall back to a neutral blue."""
    text = str(value or "").strip().lstrip("#")
    if len(text) == 3:
        text = "".join(char * 2 for char in text)
    if len(text) != 6:
        return (44, 123, 229)
    try:
        return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
    except ValueError:
        return (44, 123, 229)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    clamped = tuple(max(0, min(255, int(round(channel)))) for channel in rgb)
    return f"#{clamped[0]:02X}{clamped[1]:02X}{clamped[2]:02X}"


def _mix_hex(first: str, second: str, amount: float) -> str:
    """Linear mix of two hex colors; amount=0 returns first."""
    ratio = max(0.0, min(1.0, amount))
    left, right = _hex_to_rgb(first), _hex_to_rgb(second)
    return _rgb_to_hex(tuple(left[index] + (right[index] - left[index]) * ratio for index in range(3)))


def _tiered_fills(ctx: dict, count: int) -> list[str]:
    """Premium monochrome progression: vivid primary at the top, deep tone at the base."""
    if count <= 0:
        return []
    if count == 1:
        return [ctx["primary"]]
    return [_mix_hex(ctx["primary"], ctx["dark"], index / (count - 1) * 0.88) for index in range(count)]


def _text_width(value: str, size: float) -> float:
    """Rough advance width supporting CJK (full-width) and latin glyphs."""
    total = 0.0
    for char in str(value).splitlines()[0] if str(value) else "":
        total += size * (1.0 if ord(char) > 255 else 0.60)
    return total


def _fits_inside(value: str, size: float, available: float, padding: float = 24.0) -> bool:
    return _text_width(value, size) <= max(0.0, available - padding)


def _text(x: float, y: float, value: str, ctx: dict, size_key: str = "labelSize", **extra: object) -> str:
    max_chars = int(extra.pop("max_chars", 0))
    value = wrap_text(value, max_chars) if max_chars else value
    size = ctx["typography"][size_key]
    weight = ctx["typography"]["titleWeight"] if size_key == "titleSize" else ctx["typography"]["labelWeight"]
    return svg_text(
        x,
        y,
        value,
        **{
            "font-family": ctx["font"],
            "font-size": size,
            "fill": extra.pop("fill", ctx["text"]),
            "font-weight": weight,
            **extra,
        },
    )


def _title(ctx: dict, width: float, title: str | None, x: float | None = None) -> list[str]:
    if not title:
        return []
    return [_text(width / 2 if x is None else x, 28, title, ctx, "titleSize", **{"text-anchor": "middle"})]


def _node_rect(
    x: float,
    y: float,
    width: float,
    height: float,
    ctx: dict,
    variant: str = "primary",
    large: bool = False,
    **extra: object,
) -> str:
    style = node_style(ctx, variant, large=large)
    style.update(extra)
    return svg_rect(x, y, width, height, **style)


def _marker_rx(ctx: dict) -> float:
    return float(ctx["shapes"]["markerRadius"])


def _gradient_defs(ctx: dict) -> str:
    """Accent gradient matching the slide theme (e.g. key-message backgrounds)."""
    sig = ctx.get("signature", {})
    start, end = sig.get("gradientFrom"), sig.get("gradientTo")
    if not start or not end or start == end:
        return ""
    return (
        '<defs><linearGradient id="theme-accent-gradient" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{escape_xml(start)}"/>'
        f'<stop offset="1" stop-color="{escape_xml(end)}"/>'
        "</linearGradient></defs>"
    )


def _accent_fill(ctx: dict) -> str:
    sig = ctx.get("signature", {})
    start, end = sig.get("gradientFrom"), sig.get("gradientTo")
    if start and end and start != end:
        return "url(#theme-accent-gradient)"
    return ctx["primary"]


def _top_border_width(ctx: dict) -> float:
    try:
        return float(ctx.get("signature", {}).get("topBorderWidth", 0))
    except (TypeError, ValueError):
        return 0.0


def _top_accent_bar(x: float, y: float, width: float, ctx: dict) -> str:
    """Steps-card top bar mirroring the theme's `border-top: 4px solid primary`."""
    bar_h = _top_border_width(ctx)
    if not bar_h:
        return ""
    return svg_rect(x, y, width, bar_h, role="marker", fill=ctx["primary"], stroke="none")
