from __future__ import annotations

import html
import math
import re
from typing import Iterable

from design_tokens import best_text_on, node_style, theme_context
from diagram_models import parse_diagram_data
from svg_filters import build_filter_defs


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
    return " ".join(f'{key}="{escape_xml(_num(value) if isinstance(value, float) else str(value))}"' for key, value in values.items() if value is not None)


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
    return svg_line(x1, y1, x2, y2, stroke=color, **kwargs) + svg_polygon([(x2, y2), left, right], role="connector", fill=color)


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


def svg_document(width: float, height: float, elements: Iterable[str], background: str = "transparent", filter_defs: str = "") -> str:
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
    return svg_text(x, y, value, **{"font-family": ctx["font"], "font-size": size, "fill": extra.pop("fill", ctx["text"]), "font-weight": weight, **extra})


def _title(ctx: dict, width: float, title: str | None, x: float | None = None) -> list[str]:
    if not title:
        return []
    return [_text(width / 2 if x is None else x, 28, title, ctx, "titleSize", **{"text-anchor": "middle"})]


def _node_rect(x: float, y: float, width: float, height: float, ctx: dict, variant: str = "primary", large: bool = False, **extra: object) -> str:
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


CHART_CY_FULL = 0.53
CHART_R_FULL = 0.37


def _chart(data: dict, ctx: dict, donut: bool) -> list[str]:
    width, height = data["width"], data["height"]
    compact = data["layout"] != "full"
    cx = width / 2 if compact else width * 0.32
    cy = height * (0.42 if compact else CHART_CY_FULL)
    radius = min(height * (0.24 if compact else CHART_R_FULL), width * 0.23)
    total = sum(float(item["value"]) for item in data["items"])
    # Designed slice order: lead with primary, then varied hues for slide legibility.
    # (Accent placed 4th to avoid two adjacent blues on light themes.)
    palette = [ctx["primary"], ctx["success"], ctx["warning"], ctx["accent"], ctx["danger"], ctx["dark"]]
    elements: list[str] = []
    start = -math.pi / 2
    label_size = float(ctx["typography"]["labelSize"])
    pct_size = float(ctx["typography"]["captionSize"])
    for index, item in enumerate(data["items"]):
        end = start + math.tau * float(item["value"]) / total
        large = 1 if end - start > math.pi else 0
        x1, y1 = cx + radius * math.cos(start), cy + radius * math.sin(start)
        x2, y2 = cx + radius * math.cos(end), cy + radius * math.sin(end)
        fill = item.get("color", palette[index % len(palette)])
        if donut:
            inner = radius * float(data.get("inner_ratio", 0.58))
            ix2, iy2 = cx + inner * math.cos(end), cy + inner * math.sin(end)
            ix1, iy1 = cx + inner * math.cos(start), cy + inner * math.sin(start)
            d = f"M {_num(x1)} {_num(y1)} A {_num(radius)} {_num(radius)} 0 {large} 1 {_num(x2)} {_num(y2)} L {_num(ix2)} {_num(iy2)} A {_num(inner)} {_num(inner)} 0 {large} 0 {_num(ix1)} {_num(iy1)} Z"
        else:
            d = f"M {_num(cx)} {_num(cy)} L {_num(x1)} {_num(y1)} A {_num(radius)} {_num(radius)} 0 {large} 1 {_num(x2)} {_num(y2)} Z"
        elements.append(svg_path(d, role="node", fill=fill, stroke=ctx["surface"], **{"stroke-width": 2.5}))
        # Direct in-slice labeling: label + ratio when the slice fits both,
        # ratio only for narrow slices, legend-only fallback otherwise.
        frac = float(item["value"]) / total
        if frac > 0:
            raw_pct = frac * 100
            pct_text = f"{raw_pct:.0f}%" if raw_pct >= 0.5 else "<1%"
            mid_angle = (start + end) / 2
            if donut:
                r_mid = (radius + inner) / 2
                radial_two, radial_one = (radius - inner) >= 32, (radius - inner) >= 14
            else:
                r_mid = radius * 0.62
                radial_two, radial_one = radius >= 60, radius >= 40
            arc = r_mid * (end - start)
            label_text = str(item["label"])
            ink = best_text_on(fill, "#FFFFFF")
            tx = cx + r_mid * math.cos(mid_angle)
            ty = cy + r_mid * math.sin(mid_angle)
            tw_label = _text_width(label_text, pct_size)
            tw_pct = _text_width(pct_text, pct_size)

            def inside(px: float, py: float) -> bool:
                dist = math.hypot(px - cx, py - cy)
                if dist > radius - 2:
                    return False
                if donut and dist < inner + 2:
                    return False
                return True

            def fits_centered(tw: float, half_h: float) -> bool:
                # Horizontal text in a curved slice: the arc length alone is
                # not enough, both text ends must stay inside the ring/disc.
                return (
                    arc >= tw + 12
                    and inside(tx - tw / 2, ty)
                    and inside(tx + tw / 2, ty)
                    and inside(tx, ty - half_h)
                    and inside(tx, ty + half_h)
                )

            label_ok = fits_centered(tw_label, 8.0)
            pct_ok = fits_centered(tw_pct, 7.0)
            if radial_two and label_ok and pct_ok:
                elements.append(_text(tx, ty - 8, label_text, ctx, "captionSize", fill=ink, **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"}))
                elements.append(_text(tx, ty + 10, pct_text, ctx, "captionSize", fill=ink, **{"text-anchor": "middle", "dominant-baseline": "middle"}))
            elif radial_one and pct_ok:
                elements.append(_text(tx, ty, pct_text, ctx, "captionSize", fill=ink, **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"}))
        start = end
    if donut:
        elements.append(_text(cx, cy + 5, str(data.get("center_label", "合計")), ctx, "labelSize", **{"text-anchor": "middle", "font-weight": "bold"}))
    legend_gap = 36.0
    if data["layout"] == "full":
        legend_x = cx + radius + legend_gap
        legend_y = cy - ((len(data["items"]) - 1) * 25) / 2 - 6
    else:
        legend_x = width * 0.12
        legend_y = max(height * 0.58, height - len(data["items"]) * 25 - 10)
    marker = _marker_rx(ctx)
    for index, item in enumerate(data["items"]):
        x, y = legend_x, legend_y + index * 25
        legend_style = {"fill": item.get("color", palette[index % len(palette)]), "stroke": "none", "role": "node"}
        if marker:
            legend_style["rx"] = marker
            legend_style["ry"] = marker
        elements.append(svg_rect(x, y - 11, 12, 12, **legend_style))
        value = f" ({item['value']})" if data.get("show_values") else ""
        elements.append(_text(x + 20, y, str(item["label"]) + value, ctx, "captionSize", max_chars=20))
    return _title(ctx, width, data.get("title"), cx) + elements


def _pyramid(data: dict, ctx: dict) -> list[str]:
    """Segmented pyramid with a true triangular silhouette.

    Straight side edges run from a slightly truncated apex to the base, so the
    overall shape always reads as one clean triangle. Tiers use a monochrome
    primary progression (no alternating pale bands) with a unifying outline;
    labels that cannot fit inside narrow tiers move outside with a connector.
    """
    width, height = data["width"], data["height"]
    levels = data["levels"]
    count = len(levels)
    inverted = data.get("direction", "up") == "down"
    top, bottom = 58, height - 22
    span = max(1.0, bottom - top)
    max_width = min(width * 0.60, 560)
    apex_w = max(28.0, max_width * 0.12)
    step = span / count
    gap = 3.0 if step > 30 else 2.0
    center = width / 2
    label_size = float(ctx["typography"]["labelSize"])
    caption_size = float(ctx["typography"]["captionSize"])

    def width_at(y: float) -> float:
        ratio = (y - top) / span
        if inverted:  # apex at the bottom
            return max_width - (max_width - apex_w) * ratio
        return apex_w + (max_width - apex_w) * ratio

    fills = _tiered_fills(ctx, count)
    elements = _title(ctx, width, data.get("title"), center)
    for index in range(count):
        level = levels[index]
        y1 = top + index * step + (gap / 2 if index > 0 else 0.0)
        y2 = top + (index + 1) * step - (gap / 2 if index < count - 1 else 0.0)
        w1, w2 = width_at(y1), width_at(y2)
        points = [(center - w1 / 2, y1), (center + w1 / 2, y1), (center + w2 / 2, y2), (center - w2 / 2, y2)]
        fill = fills[index]
        elements.append(svg_polygon(points, fill=fill, stroke=ctx["surface"], **{"stroke-width": 1.5}))
        # Subtle top-edge highlight for a premium sheen (skipped on tiny tiers).
        if min(w1, w2) > 44:
            elements.append(
                svg_line(center - w1 / 2 + 6, y1 + 1.2, center + w1 / 2 - 6, y1 + 1.2,
                         stroke="#FFFFFF", role="connector", **{"stroke-width": 1.2, "opacity": 0.28})
            )
        label = str(level["label"])
        description = str(level.get("description", "") or "")
        mid = (y1 + y2) / 2
        mid_w = (w1 + w2) / 2
        label_color = best_text_on(fill, "#FFFFFF")
        # Descriptions use tighter padding than labels: a caption that is only
        # slightly wider than the tier should still render inside the tier.
        show_desc_inside = bool(description) and step >= 56 and _fits_inside(description, caption_size, mid_w, padding=16.0)

        def outside_description(y: float) -> None:
            """Leader line + description text placed to the right of the tier."""
            edge_x = center + mid_w / 2
            available = width - (edge_x + 14) - 6
            wrap_chars = max(4, int(available // max(caption_size, 1.0)))
            elements.append(svg_line(edge_x - 2, y, edge_x + 10, y, stroke=ctx["line"],
                                     role="connector", **{"stroke-width": 1.2}))
            elements.append(_text(edge_x + 14, y + 1, description, ctx, "captionSize", fill=ctx["muted"],
                                  max_chars=wrap_chars, **{"dominant-baseline": "middle"}))

        if _fits_inside(label, label_size, mid_w):
            if show_desc_inside:
                elements.append(_text(center, mid - 6, label, ctx, "labelSize", fill=label_color,
                                      max_chars=10, **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"}))
                elements.append(_text(center, mid + 14, description, ctx, "captionSize", fill=label_color,
                                      max_chars=14, **{"text-anchor": "middle", "dominant-baseline": "middle", "opacity": 0.85}))
            elif description:
                # Label fits but the description does not: keep the label inside
                # and move the description outside instead of dropping it.
                elements.append(_text(center, mid, label, ctx, "labelSize", fill=label_color,
                                      max_chars=10, **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"}))
                outside_description(mid)
            else:
                elements.append(_text(center, mid, label, ctx, "labelSize", fill=label_color,
                                      max_chars=10, **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"}))
        else:
            # Outside label keeps the triangle silhouette free of overflowing text.
            edge_x = center + mid_w / 2
            elements.append(svg_line(edge_x - 2, mid, edge_x + 10, mid, stroke=ctx["line"],
                                     role="connector", **{"stroke-width": 1.2}))
            elements.append(_text(edge_x + 14, mid + 1, label, ctx, "labelSize", fill=ctx["text"],
                                  max_chars=12, **{"font-weight": "bold", "dominant-baseline": "middle"}))
            if description:
                elements.append(_text(edge_x + 14, mid + 17, description, ctx, "captionSize", fill=ctx["muted"],
                                      max_chars=16, **{"dominant-baseline": "middle"}))
    # Unifying triangular outline: apex flat, base, straight sides.
    top_w, base_w = (max_width, apex_w) if inverted else (apex_w, max_width)
    outline = (
        f"M {_num(center - top_w / 2)} {_num(top)} "
        f"L {_num(center + top_w / 2)} {_num(top)} "
        f"L {_num(center + base_w / 2)} {_num(bottom)} "
        f"L {_num(center - base_w / 2)} {_num(bottom)} Z"
    )
    elements.append(svg_path(outline, role="connector", fill="none", stroke=ctx["dark"],
                             **{"stroke-width": 2, "stroke-linejoin": "round"}))
    return elements


def _cycle(data: dict, ctx: dict) -> list[str]:
    """Cycle with size-derived orbit: parts never touch each other.

    The orbit radius is built from the center-disc radius plus a minimum gap
    plus the largest radial extent of a node, so side nodes keep the same
    clearance as top/bottom ones. Connectors run edge-to-edge so arrowheads
    stay visible instead of being buried under the next node.
    """
    width, height = data["width"], data["height"]
    items = data["items"]
    node_w, node_h = min(150, width * 0.22), 42
    half_w, half_h = node_w / 2, node_h / 2
    # Center disc sized as before (fraction of the old orbit), then the orbit
    # is derived from real part sizes.
    center_r = min(width, height) * 0.29 * 0.38
    min_gap = 28.0
    direction = 1 if data.get("direction", "clockwise") == "clockwise" else -1
    angles = [-math.pi / 2 + direction * math.tau * index / len(items) for index in range(len(items))]

    def radial_extent(angle: float) -> float:
        return abs(math.cos(angle)) * half_w + abs(math.sin(angle)) * half_h

    radius = center_r + min_gap + max(radial_extent(angle) for angle in angles)
    # Keep the whole orbit (nodes included) inside the canvas.
    max_radius = min(width / 2 - half_w - 8, height / 2 - half_h - 30)
    radius = min(radius, max_radius)
    cx, cy = width / 2, height / 2 + 8
    positions = [(cx + radius * math.cos(angle), cy + radius * math.sin(angle)) for angle in angles]
    elements = _title(ctx, width, data.get("title"))

    def edge_toward(px: float, py: float, tx: float, ty: float) -> tuple[float, float]:
        dx, dy = tx - px, ty - py
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        scale = min(half_w / abs(ux) if abs(ux) > 1e-6 else float("inf"), half_h / abs(uy) if abs(uy) > 1e-6 else float("inf"))
        return px + ux * scale, py + uy * scale

    for index, (x, y) in enumerate(positions):
        nx, ny = positions[(index + 1) % len(positions)]
        start = edge_toward(x, y, nx, ny)
        end = edge_toward(nx, ny, x, y)
        # Stop the arrow tip just short of the target edge.
        dx, dy = nx - x, ny - y
        length = math.hypot(dx, dy) or 1.0
        tip = (end[0] - dx / length * 4, end[1] - dy / length * 4)
        elements.append(svg_arrow(start[0], start[1], tip[0], tip[1], ctx["line"], role="connector", fill="none"))
    for index, (x, y) in enumerate(positions):
        elements.append(_node_rect(x - node_w / 2, y - node_h / 2, node_w, node_h, ctx))
        elements.append(_text(x, y + 5, str(items[index]["label"]), ctx, "captionSize", max_chars=6, **{"text-anchor": "middle"}))
    elements.append(svg_circle(cx, cy, center_r, fill=_accent_fill(ctx), stroke=ctx["dark"], **{"stroke-width": ctx["shapes"]["strokeWidthBold"]}))
    elements.append(_text(cx, cy + 5, str(data.get("center", "")), ctx, "labelSize", fill=ctx["surface"], **{"text-anchor": "middle", "font-weight": "bold"}))
    return elements


def _org_chart(data: dict, ctx: dict) -> list[str]:
    width, height = data["width"], data["height"]
    levels: list[list[dict]] = []

    def collect(node: dict, depth: int) -> None:
        while len(levels) <= depth:
            levels.append([])
        levels[depth].append(node)
        for child in node.get("children", []):
            collect(child, depth + 1)

    collect(data["root"], 0)
    positions: dict[int, tuple[float, float]] = {}
    max_level_nodes = max(len(nodes) for nodes in levels)
    node_gap = 12
    node_w = min(170, (width - node_gap * (max_level_nodes + 1)) / max_level_nodes)
    node_h = 38
    # Fixed pitch + vertical centering: connector length stays constant no
    # matter how many generations the tree has (up to 5 rows); the pitch only
    # compresses when more rows need to share the canvas.
    available = height - 22 - 58
    if len(levels) > 1:
        pitch = min(node_h + 56, max(node_h + 32, (available - node_h) / (len(levels) - 1)))
    else:
        pitch = node_h + 56
    block = pitch * (len(levels) - 1) + node_h
    # Optical top-weighting: center small trees but keep the title gap tight.
    top = 58 + min(16.0, max(0.0, (available - block) / 2))
    elements = _title(ctx, width, data.get("title"))
    for depth, nodes in enumerate(levels):
        y = top + depth * pitch + node_h / 2
        row_width = len(nodes) * node_w + max(0, len(nodes) - 1) * node_gap
        row_start = (width - row_width) / 2
        for index, node in enumerate(nodes):
            node_x = row_start + node_w / 2 + index * (node_w + node_gap)
            positions[id(node)] = (node_x, y)
            parent = next((candidate for candidate in sum(levels[:depth], []) if node in candidate.get("children", [])), None)
            if parent:
                px, py = positions[id(parent)]
                elements.append(svg_line(px, py + node_h / 2, node_x, y - node_h / 2, stroke=ctx["line"], **{"stroke-width": ctx["shapes"]["strokeWidth"]}))
    for nodes in levels:
        for node in nodes:
            x, y = positions[id(node)]
            elements.append(_node_rect(x - node_w / 2, y - node_h / 2, node_w, node_h, ctx))
            elements.append(_text(x, y + 5, node["label"], ctx, "captionSize", max_chars=12, **{"text-anchor": "middle"}))
    return elements


def _radial(data: dict, ctx: dict) -> list[str]:
    width, height = data["width"], data["height"]
    cx, cy = width / 2, height / 2 + 8
    # SSoT: geometry adapts to canvas width here (not in templates).
    # Narrow layouts (col2/col3) keep full-layout geometry byte-identical;
    # only sub-750px canvases use scaled boxes + shorter child radius so the
    # max()/min() clamps below rarely collapse distinct nodes onto each other.
    compact = width < 750
    main_hw, main_hh = (48.0, 16.0) if compact else (60.0, 20.0)
    child_hw, child_hh = (36.0, 12.0) if compact else (42.0, 14.0)
    child_radius_factor = 0.42 if compact else 0.54
    child_spread = 0.42 if compact else 0.50
    elements = _title(ctx, width, data.get("title"))
    center_r = min(54, width * 0.12)
    center_style = node_style(ctx, "accent")
    elements.append(svg_circle(cx, cy, center_r, fill=_accent_fill(ctx), stroke=center_style["stroke"], **{"stroke-width": center_style["stroke-width"]}))
    elements.append(_text(cx, cy + 5, data["center"], ctx, "labelSize", fill=ctx["surface"], **{"text-anchor": "middle", "font-weight": "bold"}))

    def edge_point(origin_x: float, origin_y: float, target_x: float, target_y: float, half_width: float, half_height: float) -> tuple[float, float]:
        dx, dy = target_x - origin_x, target_y - origin_y
        length = math.hypot(dx, dy) or 1
        ux, uy = dx / length, dy / length
        scale = min(half_width / abs(ux) if abs(ux) > 1e-6 else float("inf"), half_height / abs(uy) if abs(uy) > 1e-6 else float("inf"))
        return origin_x + ux * scale, origin_y + uy * scale

    for index, item in enumerate(data["items"]):
        if width / height > 2 and len(data["items"]) == 3:
            angle = (-math.pi / 2, 0, math.pi)[index]
        else:
            angle = -math.pi / 2 + math.tau * index / len(data["items"])
        half_width, half_height = main_hw, main_hh
        rectangle_extent = abs(math.cos(angle)) * half_width + abs(math.sin(angle)) * half_height
        gap = 32
        radial_distance = center_r + gap + rectangle_extent
        x, y = cx + radial_distance * math.cos(angle), cy + radial_distance * math.sin(angle)
        start_x, start_y = cx + center_r * math.cos(angle), cy + center_r * math.sin(angle)
        end_x, end_y = edge_point(x, y, cx, cy, main_hw, main_hh)
        elements.append(svg_line(start_x, start_y, end_x, end_y, stroke=ctx["line"], **{"stroke-width": ctx["shapes"]["strokeWidth"]}))
        children = item.get("children", [])
        for child_index, child in enumerate(children):
            child_angle = angle + (child_index - (len(children) - 1) / 2) * child_spread
            child_radius = min(width, height) * child_radius_factor
            child_x = max(48, min(width - 48, cx + child_radius * math.cos(child_angle)))
            child_y = max(24, min(height - 24, cy + child_radius * math.sin(child_angle)))
            # Edge-to-edge on both ends, collected before any box is painted
            # so no line ever crosses a box interior.
            child_start = edge_point(x, y, child_x, child_y, main_hw, main_hh)
            child_end = edge_point(child_x, child_y, x, y, child_hw, child_hh)
            elements.append(svg_line(child_start[0], child_start[1], child_end[0], child_end[1], role="connector", stroke=ctx["line"], **{"stroke-width": ctx["shapes"]["strokeWidth"]}))
    for index, item in enumerate(data["items"]):
        if width / height > 2 and len(data["items"]) == 3:
            angle = (-math.pi / 2, 0, math.pi)[index]
        else:
            angle = -math.pi / 2 + math.tau * index / len(data["items"])
        half_width, half_height = main_hw, main_hh
        rectangle_extent = abs(math.cos(angle)) * half_width + abs(math.sin(angle)) * half_height
        gap = 32
        radial_distance = center_r + gap + rectangle_extent
        x, y = cx + radial_distance * math.cos(angle), cy + radial_distance * math.sin(angle)
        elements.append(_node_rect(x - main_hw, y - main_hh, main_hw * 2, main_hh * 2, ctx))
        elements.append(_text(x, y + 5, item["label"], ctx, "captionSize", max_chars=10, **{"text-anchor": "middle", "font-weight": "bold"}))
        children = item.get("children", [])
        for child_index, child in enumerate(children):
            child_angle = angle + (child_index - (len(children) - 1) / 2) * child_spread
            child_radius = min(width, height) * child_radius_factor
            child_x = max(48, min(width - 48, cx + child_radius * math.cos(child_angle)))
            child_y = max(24, min(height - 24, cy + child_radius * math.sin(child_angle)))
            elements.append(_node_rect(child_x - child_hw, child_y - child_hh, child_hw * 2, child_hh * 2, ctx, variant="surface"))
            elements.append(_text(child_x, child_y + 4, str(child), ctx, "captionSize", **{"text-anchor": "middle"}))
    return elements


def _funnel(data: dict, ctx: dict) -> list[str]:
    """Premium funnel with straight sides and an annotation gutter.

    Widths follow one straight taper from mouth to neck (never kinked), so the
    silhouette stays a clean triangle. Stage values are shown in pills in a
    reserved right gutter with conversion rates between stages instead of
    distorting widths or painting unreadable text on the canvas background.
    """
    width, height = data["width"], data["height"]
    levels = data["levels"]
    count = len(levels)
    flared = data.get("direction", "down") == "up"  # narrow mouth at the top
    top, bottom = 58, height - 22
    span = max(1.0, bottom - top)
    has_values = any(level.get("value") is not None for level in levels)
    if has_values:
        max_width = min(width * 0.60, 380)
        center = (width - 100) / 2
    else:
        max_width = min(width * 0.60, 560)
        center = width / 2
    neck_w = max(48.0, max_width * 0.20)
    step = span / count
    gap = 3.0 if step > 30 else 2.0
    label_size = float(ctx["typography"]["labelSize"])
    caption_size = float(ctx["typography"]["captionSize"])

    def width_at(y: float) -> float:
        ratio = (y - top) / span
        if flared:  # megaphone: narrow top, wide bottom
            return neck_w + (max_width - neck_w) * ratio
        return max_width - (max_width - neck_w) * ratio

    fills = _tiered_fills(ctx, count)
    elements = _title(ctx, width, data.get("title"), center)
    pill_w = 0.0
    pill_x = 0.0
    if has_values:
        pill_w = max(52.0, min(84.0, width - (center + max_width / 2) - 28.0))
        pill_x = min(center + max_width / 2 + 16.0, width - pill_w - 10.0)
    pill_rx = _marker_rx(ctx) or 10.0
    for index, level in enumerate(levels):
        y1 = top + index * step + (gap / 2 if index > 0 else 0.0)
        y2 = top + (index + 1) * step - (gap / 2 if index < count - 1 else 0.0)
        w1, w2 = width_at(y1), width_at(y2)
        points = [(center - w1 / 2, y1), (center + w1 / 2, y1), (center + w2 / 2, y2), (center - w2 / 2, y2)]
        fill = fills[index]
        elements.append(svg_polygon(points, fill=fill, stroke=ctx["surface"], **{"stroke-width": 1.5}))
        if min(w1, w2) > 44:
            elements.append(
                svg_line(center - w1 / 2 + 6, y1 + 1.2, center + w1 / 2 - 6, y1 + 1.2,
                         stroke="#FFFFFF", role="connector", **{"stroke-width": 1.2, "opacity": 0.28})
            )
        label = str(level["label"])
        mid = (y1 + y2) / 2
        mid_w = (w1 + w2) / 2
        label_color = best_text_on(fill, "#FFFFFF")
        if _fits_inside(label, label_size, mid_w):
            elements.append(_text(center, mid, label, ctx, "labelSize", fill=label_color,
                                  max_chars=10, **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"}))
        else:
            # Overflow labels go to the free side so the taper stays crisp.
            if has_values:
                edge_x = center - mid_w / 2
                elements.append(svg_line(edge_x - 10, mid, edge_x + 2, mid, stroke=ctx["line"],
                                         role="connector", **{"stroke-width": 1.2}))
                elements.append(_text(edge_x - 14, mid + 1, label, ctx, "labelSize", fill=ctx["text"],
                                      max_chars=12, **{"text-anchor": "end", "font-weight": "bold", "dominant-baseline": "middle"}))
            else:
                edge_x = center + mid_w / 2
                elements.append(svg_line(edge_x - 2, mid, edge_x + 10, mid, stroke=ctx["line"],
                                         role="connector", **{"stroke-width": 1.2}))
                elements.append(_text(edge_x + 14, mid + 1, label, ctx, "labelSize", fill=ctx["text"],
                                      max_chars=12, **{"font-weight": "bold", "dominant-baseline": "middle"}))
        if has_values and level.get("value") is not None:
            pill_mid = mid
            pill_y = pill_mid - 10
            edge_right = center + mid_w / 2
            elements.append(svg_line(edge_right - 1, pill_mid, pill_x - 3, pill_mid, stroke=ctx["line"],
                                     role="connector", **{"stroke-width": 1.1, "opacity": 0.7}))
            elements.append(svg_rect(pill_x, pill_y, pill_w, 20, role="marker", fill=ctx["surface"],
                                     stroke=ctx["border"], **{"stroke-width": 1.2, "rx": pill_rx, "ry": pill_rx}))
            elements.append(_text(pill_x + pill_w / 2, pill_mid + 0.5, str(level["value"]), ctx, "captionSize",
                                  fill=ctx["text"], max_chars=10,
                                  **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"}))
    if has_values:
        # Conversion rates sit on the gutter at each stage boundary.
        for index in range(count - 1):
            current, following = levels[index].get("value"), levels[index + 1].get("value")
            if current is None or following is None:
                continue
            try:
                base = float(current)
            except (TypeError, ValueError):
                continue
            if base <= 0:
                continue
            try:
                rate = float(following) / base * 100.0
            except (TypeError, ValueError):
                continue
            boundary = top + (index + 1) * step
            elements.append(_text(pill_x + pill_w / 2, boundary + 0.5, f"{rate:.0f}%", ctx, "captionSize",
                                  fill=ctx["muted"], **{"text-anchor": "middle", "dominant-baseline": "middle"}))
    # Unifying funnel outline with straight sides.
    mouth_w, tail_w = (neck_w, max_width) if flared else (max_width, neck_w)
    outline = (
        f"M {_num(center - mouth_w / 2)} {_num(top)} "
        f"L {_num(center + mouth_w / 2)} {_num(top)} "
        f"L {_num(center + tail_w / 2)} {_num(bottom)} "
        f"L {_num(center - tail_w / 2)} {_num(bottom)} Z"
    )
    elements.append(svg_path(outline, role="connector", fill="none", stroke=ctx["dark"],
                             **{"stroke-width": 2, "stroke-linejoin": "round"}))
    return elements


def _fmt_tick(value: float) -> str:
    """Compact axis tick label (supports negatives for future ranges)."""
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    if magnitude >= 1_000_000:
        return f"{sign}{magnitude / 1_000_000:g}M"
    if magnitude >= 1000:
        return f"{sign}{magnitude / 1000:g}k"
    return f"{sign}{magnitude:g}"


def _y_scale(y_min: float, y_max: float, ticks: int = 4) -> dict:
    """Nice axis scale for an arbitrary [min, max] range.

    Negative ranges already work (zero baseline floats mid-plot); v1 callers
    always pass y_min=0 because the model rejects negatives. Enabling
    negatives later requires no change here.
    """
    span = y_max - y_min
    if not math.isfinite(span) or span <= 0:
        y_min, y_max, span = 0.0, 1.0, 1.0
    raw_step = span / max(1, ticks)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    step = next(m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw_step)
    floor = math.floor(y_min / step) * step
    ceiling = math.ceil(y_max / step) * step
    count = int(round((ceiling - floor) / step))
    return {"min": floor, "max": ceiling, "step": step,
            "ticks": [floor + index * step for index in range(count + 1)]}


def _legend_row(ctx: dict, width: float, y: float, entries: list[tuple[str, str]]) -> list[str]:
    """Centered single-row legend (swatch + label per series)."""
    caption = float(ctx["typography"]["captionSize"])
    gap, swatch = 18.0, 12.0
    widths = [swatch + 6 + _text_width(label, caption) for label, _ in entries]
    total = sum(widths) + gap * (len(entries) - 1)
    elements: list[str] = []
    cursor = (width - total) / 2
    marker = _marker_rx(ctx)
    for (label, color), block in zip(entries, widths):
        style: dict[str, object] = {"fill": color, "stroke": "none", "role": "node"}
        if marker:
            style["rx"] = marker
            style["ry"] = marker
        elements.append(svg_rect(cursor, y - 11, swatch, swatch, **style))
        elements.append(_text(cursor + swatch + 6, y, label, ctx, "captionSize", max_chars=10))
        cursor += block + gap
    return elements


def _cartesian_frame(
    data: dict,
    ctx: dict,
    x_labels: list[str],
    y_min: float,
    y_max: float,
    legend: list[tuple[str, str]] | None = None,
) -> dict:
    """Shared axes, gridlines, and coordinate mapping for bar/line/stacked-bar.

    Gridlines and axes use role="axis" (ignored by the validator's
    node-crossing check); only bars/segments are role="node".
    """
    width, height = data["width"], data["height"]
    title = data.get("title")
    unit = str(data.get("unit", "") or "")
    scale = _y_scale(y_min, y_max)
    elements = _title(ctx, width, title)

    cursor_y = 54.0 if title else 34.0
    if legend:
        elements += _legend_row(ctx, width, cursor_y, legend)
        cursor_y += 22.0
    # Left gutter sized from the widest tick label (top tick carries the
    # unit). Prevents labels like "200 百万円" from clipping at x=0 under
    # wide fallback fonts.
    caption_size = float(ctx["typography"]["captionSize"])
    tick_labels = [
        _fmt_tick(tick) + (" " + unit if unit and position == len(scale["ticks"]) - 1 else "")
        for position, tick in enumerate(scale["ticks"])
    ]
    widest = max((_text_width(label, caption_size) for label in tick_labels), default=0.0)
    plot_left = min(width * 0.25, max(64.0, widest + 20.0))
    plot_top = cursor_y + 12.0
    plot_bottom = height - 34.0
    plot_right = width - 20.0
    plot_w = plot_right - plot_left
    plot_h = max(1.0, plot_bottom - plot_top)
    count = len(x_labels)
    slot = plot_w / max(1, count)

    def x_pos(index: int) -> float:
        return plot_left + slot * (index + 0.5)

    def y_pos(value: float) -> float:
        ratio = (value - scale["min"]) / (scale["max"] - scale["min"])
        return plot_top + plot_h * (1.0 - ratio)

    muted = ctx["muted"]
    # Horizontal gridlines + tick labels (top tick carries the unit, if any).
    for y, label in ((y_pos(tick), text) for tick, text in zip(scale["ticks"], tick_labels)):
        elements.append(svg_line(plot_left, y, plot_right, y, stroke=muted,
                                 role="axis", **{"stroke-width": 1, "opacity": 0.45}))
        elements.append(_text(plot_left - 8, y + 4, label, ctx, "captionSize",
                              fill=muted, max_chars=14, **{"text-anchor": "end"}))
    # Axes baselines.
    elements.append(svg_line(plot_left, plot_top, plot_left, plot_bottom, stroke=muted,
                             role="axis", **{"stroke-width": 1.2}))
    elements.append(svg_line(plot_left, y_pos(scale["min"] if scale["min"] > 0 else 0), plot_right,
                             y_pos(scale["min"] if scale["min"] > 0 else 0),
                             stroke=ctx["line"], role="axis", **{"stroke-width": 1.5}))
    # X labels.
    for index, label in enumerate(x_labels):
        elements.append(_text(x_pos(index), plot_bottom + 18, label, ctx, "captionSize",
                              max_chars=8, **{"text-anchor": "middle"}))
    return {"elements": elements, "x": x_pos, "y": y_pos, "slot": slot,
            "plot_left": plot_left, "plot_top": plot_top, "plot_bottom": plot_bottom,
            "scale": scale, "tick_labels": tick_labels}


CARTESIAN_PALETTE = ["primary", "success", "warning", "accent", "danger", "dark"]


def _series_colors(ctx: dict, count: int) -> list[str]:
    return [ctx[CARTESIAN_PALETTE[index % len(CARTESIAN_PALETTE)]] for index in range(count)]


def _bar(data: dict, ctx: dict) -> list[str]:
    labels = [str(item["label"]) for item in data["items"]]
    values = [float(item["value"]) for item in data["items"]]
    ceiling = float(data.get("y_max", _y_scale(0.0, max(values))["max"]))
    frame = _cartesian_frame(data, ctx, labels, 0.0, ceiling)
    elements = frame["elements"]
    bar_w = min(frame["slot"] * 0.62, 120.0)
    show_values = bool(data.get("show_values", True))
    # Single-series default stays single-primary (length already encodes rank;
    # multicolor would add rainbow noise against the one-accent rule). An
    # explicit per-item `color` opts into nominal coloring when bars are
    # categories rather than an ordered ranking.
    for index, (item, value) in enumerate(zip(data["items"], values)):
        x, top, base = frame["x"](index), frame["y"](value), frame["y"](0.0)
        fill = item.get("color", ctx["primary"]) if isinstance(item, dict) else ctx["primary"]
        elements.append(svg_rect(x - bar_w / 2, top, bar_w, max(0.0, base - top),
                                 role="node", fill=fill, stroke="none"))
        if show_values:
            elements.append(_text(x, top - 8, _fmt_tick(value), ctx, "captionSize",
                                  max_chars=10, **{"text-anchor": "middle", "font-weight": "bold"}))
    return elements


def _line(data: dict, ctx: dict) -> list[str]:
    categories = [str(category) for category in data["categories"]]
    series = data["series"]
    colors = _series_colors(ctx, len(series))
    stacked_max = max(float(value) for entry in series for value in entry["values"])
    ceiling = float(data.get("y_max", _y_scale(0.0, stacked_max)["max"]))
    legend = [(str(entry["label"]), color) for entry, color in zip(series, colors)] if len(series) > 1 else None
    frame = _cartesian_frame(data, ctx, categories, 0.0, ceiling, legend)
    elements = frame["elements"]
    show_values = bool(data.get("show_values", False))
    for entry, color in zip(series, colors):
        points = [(frame["x"](index), frame["y"](float(value))) for index, value in enumerate(entry["values"])]
        path = "M " + " L ".join(f"{_num(x)} {_num(y)}" for x, y in points)
        elements.append(svg_path(path, role="connector", fill="none", stroke=color, **{"stroke-width": 2.5}))
        for (x, y), value in zip(points, entry["values"]):
            elements.append(svg_circle(x, y, 4.5, role="marker", fill=ctx["surface"], stroke=color, **{"stroke-width": 2}))
            if show_values:
                elements.append(_text(x, y - 12, _fmt_tick(float(value)), ctx, "captionSize",
                                      max_chars=10, **{"text-anchor": "middle"}))
    return elements


def _stacked_bar(data: dict, ctx: dict) -> list[str]:
    categories = [str(category) for category in data["categories"]]
    series = data["series"]
    colors = _series_colors(ctx, len(series))
    totals = [sum(float(entry["values"][index]) for entry in series) for index in range(len(categories))]
    ceiling = float(data.get("y_max", _y_scale(0.0, max(totals))["max"]))
    legend = [(str(entry["label"]), color) for entry, color in zip(series, colors)]
    frame = _cartesian_frame(data, ctx, categories, 0.0, ceiling, legend)
    elements = frame["elements"]
    bar_w = min(frame["slot"] * 0.62, 120.0)
    show_values = bool(data.get("show_values", True))
    for index in range(len(categories)):
        base = frame["y"](0.0)
        running = 0.0
        for entry, color in zip(series, colors):
            running += float(entry["values"][index])
            top = frame["y"](running)
            seg_h = base - top
            x = frame["x"](index)
            elements.append(svg_rect(x - bar_w / 2, top, bar_w, max(0.0, seg_h),
                                     role="node", fill=color, stroke=ctx["surface"], **{"stroke-width": 1.5}))
            if show_values and seg_h >= 20:
                elements.append(_text(x, top + seg_h / 2 + 4, _fmt_tick(float(entry["values"][index])),
                                      ctx, "captionSize", fill=best_text_on(color, "#FFFFFF"),
                                      max_chars=8, **{"text-anchor": "middle", "font-weight": "bold"}))
            base = top
        if show_values:
            elements.append(_text(frame["x"](index), frame["y"](totals[index]) - 8, _fmt_tick(totals[index]),
                                  ctx, "captionSize", max_chars=10,
                                  **{"text-anchor": "middle", "font-weight": "bold"}))
    return elements


def _hbar(data: dict, ctx: dict) -> list[str]:
    """Horizontal single-series bars. Long Japanese labels fit the left gutter."""
    labels = [str(item["label"]) for item in data["items"]]
    values = [float(item["value"]) for item in data["items"]]
    width, height = data["width"], data["height"]
    ceiling = float(data.get("y_max", _y_scale(0.0, max(values))["max"]))
    scale = _y_scale(0.0, ceiling)
    elements = _title(ctx, width, data.get("title"))
    label_size = float(ctx["typography"]["labelSize"])
    cursor_y = 54.0 if data.get("title") else 34.0
    # Left gutter from the widest row label (measured at label size); right gutter reserves value text.
    widest = max((_text_width(label, label_size) for label in labels), default=0.0)
    label_w = min(width * 0.35, max(88.0, widest + 20.0))
    plot_left = label_w + 12.0
    plot_right = width - 64.0
    plot_top = cursor_y + 12.0
    plot_bottom = height - 30.0
    plot_w = max(1.0, plot_right - plot_left)
    plot_h = max(1.0, plot_bottom - plot_top)
    count = len(labels)
    slot = plot_h / max(1, count)
    bar_h = min(slot * 0.55, 44.0)

    def x_pos(value: float) -> float:
        ratio = (value - scale["min"]) / (scale["max"] - scale["min"])
        return plot_left + plot_w * ratio

    muted = ctx["muted"]
    for tick in scale["ticks"]:
        x = x_pos(tick)
        elements.append(svg_line(x, plot_top, x, plot_bottom, stroke=muted,
                                 role="axis", **{"stroke-width": 1, "opacity": 0.45}))
        unit = str(data.get("unit", "") or "")
        tag = _fmt_tick(tick) + (" " + unit if unit and tick == scale["ticks"][-1] else "")
        elements.append(_text(x, plot_bottom + 18, tag, ctx, "captionSize",
                              fill=muted, max_chars=14, **{"text-anchor": "middle"}))
    elements.append(svg_line(plot_left, plot_top, plot_left, plot_bottom, stroke=muted,
                             role="axis", **{"stroke-width": 1.2}))
    elements.append(svg_line(plot_left, plot_bottom, plot_right, plot_bottom, stroke=ctx["line"],
                             role="axis", **{"stroke-width": 1.5}))
    show_values = bool(data.get("show_values", True))
    # Ordered single-series ranking: keep the single-primary default so length
    # alone encodes order (one-accent rule; adjacent saturated hues are banned).
    # A per-item `color` is honored for nominal categories, but the showcase
    # template intentionally omits it.
    for index, (item, label, value) in enumerate(zip(data["items"], labels, values)):
        y_center = plot_top + slot * (index + 0.5)
        elements.append(_text(plot_left - 8, y_center + 5, label, ctx, "labelSize",
                              max_chars=12, **{"text-anchor": "end"}))
        x_end = x_pos(value)
        bar_len = max(0.0, x_end - plot_left)
        y_top = y_center - bar_h / 2
        fill = item.get("color", ctx["primary"]) if isinstance(item, dict) else ctx["primary"]
        elements.append(svg_rect(plot_left, y_top, bar_len, bar_h,
                                 role="node", fill=fill, stroke="none"))
        if show_values:
            tag = _fmt_tick(value)
            if bar_len >= 64:
                elements.append(_text(x_end - 8, y_center + 5, tag, ctx, "labelSize",
                                      fill=best_text_on(fill, "#FFFFFF"),
                                      max_chars=10, **{"text-anchor": "end", "font-weight": "bold"}))
            else:
                elements.append(_text(x_end + 8, y_center + 5, tag, ctx, "labelSize",
                                      max_chars=10, **{"text-anchor": "start", "font-weight": "bold"}))
    return elements


def _stacked_bar_100(data: dict, ctx: dict) -> list[str]:
    """100% stacked bars. Same input as stacked-bar; segments normalized per category."""
    categories = [str(category) for category in data["categories"]]
    series = data["series"]
    colors = _series_colors(ctx, len(series))
    totals = [sum(float(entry["values"][index]) for entry in series) for index in range(len(categories))]
    pct: list[list[float]] = []
    for entry in series:
        row = []
        for index, value in enumerate(entry["values"]):
            total = totals[index]
            row.append(0.0 if total <= 0 else float(value) / total * 100.0)
        pct.append(row)
    frame_data = dict(data)
    frame_data["unit"] = str(data.get("unit", "") or "%")
    legend = [(str(entry["label"]), color) for entry, color in zip(series, colors)]
    frame = _cartesian_frame(frame_data, ctx, categories, 0.0, 100.0, legend)
    elements = frame["elements"]
    bar_w = min(frame["slot"] * 0.62, 120.0)
    show_values = bool(data.get("show_values", True))
    for index in range(len(categories)):
        base = frame["y"](0.0)
        running = 0.0
        for row, color in zip(pct, colors):
            running += row[index]
            top = frame["y"](running)
            seg_h = base - top
            x = frame["x"](index)
            elements.append(svg_rect(x - bar_w / 2, top, bar_w, max(0.0, seg_h),
                                     role="node", fill=color, stroke=ctx["surface"], **{"stroke-width": 1.5}))
            if show_values and seg_h >= 26:
                elements.append(_text(x, top + seg_h / 2 + 5, f"{row[index]:.0f}%",
                                      ctx, "captionSize", fill=best_text_on(color, "#FFFFFF"),
                                      max_chars=8, **{"text-anchor": "middle", "font-weight": "bold", "font-size": 16}))
            base = top
    return elements


def _matrix(data: dict, ctx: dict) -> list[str]:
    """Scored comparison matrix (rows=criteria 2-6, columns=options 2-4, scores 0-5)."""
    columns = [str(column) for column in data["columns"]]
    rows = data["rows"]
    width, height = data["width"], data["height"]
    elements = _title(ctx, width, data.get("title"))
    label_size = float(ctx["typography"]["labelSize"])
    top = 54.0 if data.get("title") else 34.0
    legend_reserve = 46.0
    grid_bottom = height - legend_reserve
    n_rows, n_cols = len(rows), len(columns)
    widest = max((_text_width(str(row.get("label", "")), label_size) for row in rows), default=0.0)
    label_w = min(width * 0.34, max(84.0, widest + 20.0))
    grid_x = 10.0 + label_w
    grid_w = max(1.0, width - 10.0 - grid_x)
    col_w = grid_w / max(1, n_cols)
    header_h = 30.0
    row_h = min(max(1.0, (grid_bottom - top - header_h) / max(1, n_rows)), 64.0)
    marker = _marker_rx(ctx)
    # Column headers.
    for j, column in enumerate(columns):
        cx = grid_x + col_w * (j + 0.5)
        elements.append(_text(cx, top + 20, column, ctx, "labelSize",
                              max_chars=10, **{"text-anchor": "middle", "font-weight": "bold"}))
    # Rows + cells. The row winner (max score) gets a dark ring as focal point.
    for i, row in enumerate(rows):
        scores = [max(0, min(5, int(float(score)))) for score in row.get("scores", [])]
        winner = max(scores) if scores else 0
        y = top + header_h + row_h * i
        cy = y + row_h / 2 + 5
        elements.append(_text(grid_x - 8, cy, str(row.get("label", "")), ctx, "labelSize",
                              max_chars=12, **{"text-anchor": "end", "font-weight": "bold"}))
        for j, level in enumerate(scores):
            if level == 0:
                fill = ctx["surface"]
            else:
                fill = _mix_hex(ctx["surface"], ctx["primary"], 0.22 + 0.78 * (level / 5.0))
            x = grid_x + col_w * j
            style: dict[str, object] = {"fill": fill, "stroke": ctx["line"], "stroke-width": 1, "role": "node"}
            if level == winner and winner > 0:
                style.update({"stroke": ctx["dark"], "stroke-width": 2.5})
            if marker:
                style["rx"] = marker
                style["ry"] = marker
            elements.append(svg_rect(x + 1, y + 1, col_w - 2, row_h - 2, **style))
            elements.append(_text(x + col_w / 2, cy, str(level), ctx, "labelSize",
                                  fill=best_text_on(fill, "#FFFFFF"),
                                  **{"text-anchor": "middle", "font-weight": "bold", "font-size": 26}))
    # Scale legend (0-5 swatches + low/high ends) so the hue steps read at a glance.
    swatch_w, swatch_h, gap = 26.0, 16.0, 6.0
    legend_cells = 6
    legend_w = legend_cells * swatch_w + (legend_cells - 1) * gap
    legend_x = (width - legend_w) / 2
    legend_y = grid_bottom + 14.0
    muted = ctx["muted"]
    elements.append(_text(legend_x - 10, legend_y + 12, "Low", ctx, "captionSize",
                          fill=muted, **{"text-anchor": "end"}))
    for level in range(legend_cells):
        if level == 0:
            legend_fill = ctx["surface"]
        else:
            legend_fill = _mix_hex(ctx["surface"], ctx["primary"], 0.22 + 0.78 * (level / 5.0))
        sx = legend_x + level * (swatch_w + gap)
        sw_style: dict[str, object] = {"fill": legend_fill, "stroke": ctx["line"], "stroke-width": 1, "role": "node"}
        if marker:
            sw_style["rx"] = marker
            sw_style["ry"] = marker
        elements.append(svg_rect(sx, legend_y, swatch_w, swatch_h, **sw_style))
        elements.append(_text(sx + swatch_w / 2, legend_y + 12, str(level), ctx, "captionSize",
                              fill=best_text_on(legend_fill, "#FFFFFF"),
                              **{"text-anchor": "middle", "font-weight": "bold"}))
    elements.append(_text(legend_x + legend_w + 10, legend_y + 12, "High", ctx, "captionSize",
                          fill=muted, **{"text-anchor": "start"}))
    return elements


def render_diagram(data: dict, theme_data: dict, layout: str) -> str:
    data = parse_diagram_data({**data, "layout": data.get("layout", layout)})
    ctx = theme_context(theme_data)
    kind = data["type"]
    renderers = {
        "pie": lambda: _chart(data, ctx, False),
        "donut": lambda: _chart(data, ctx, True),
        "pyramid": lambda: _pyramid(data, ctx),
        "cycle": lambda: _cycle(data, ctx),
        "org-chart": lambda: _org_chart(data, ctx),
        "radial": lambda: _radial(data, ctx),
        "funnel": lambda: _funnel(data, ctx),
        "bar": lambda: _bar(data, ctx),
        "hbar": lambda: _hbar(data, ctx),
        "line": lambda: _line(data, ctx),
        "stacked-bar": lambda: _stacked_bar(data, ctx),
        "stacked-bar-100": lambda: _stacked_bar_100(data, ctx),
        "matrix": lambda: _matrix(data, ctx),
    }
    elements = renderers[kind]()
    defs_parts: list[str] = []
    filters = build_filter_defs(ctx["effects"])
    if filters:
        inner = re.sub(r"^<defs>|</defs>$", "", filters.strip())
        if inner.strip():
            defs_parts.append(inner)
    gradient = _gradient_defs(ctx)
    if gradient:
        inner = re.sub(r"^<defs>|</defs>$", "", gradient.strip())
        if inner.strip():
            defs_parts.append(inner)
    filter_defs = f"<defs>{''.join(defs_parts)}</defs>" if defs_parts else ""
    return svg_document(data["width"], data["height"], elements, ctx["background"], filter_defs)
