from __future__ import annotations

import math

from design_tokens import best_text_on, ensure_inside_label, node_style

from .primitives import (
    _accent_fill,
    _fits_inside,
    _marker_rx,
    _mix_hex,
    _node_rect,
    _num,
    _text,
    _text_width,
    _tiered_fills,
    _title,
    svg_arrow,
    svg_circle,
    svg_line,
    svg_path,
    svg_polygon,
    svg_rect,
)


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
                svg_line(
                    center - w1 / 2 + 6,
                    y1 + 1.2,
                    center + w1 / 2 - 6,
                    y1 + 1.2,
                    stroke="#FFFFFF",
                    role="connector",
                    **{"stroke-width": 1.2, "opacity": 0.28},
                )
            )
        label = str(level["label"])
        description = str(level.get("description", "") or "")
        mid = (y1 + y2) / 2
        mid_w = (w1 + w2) / 2
        label_color = best_text_on(fill, "#FFFFFF")
        # Descriptions use tighter padding than labels: a caption that is only
        # slightly wider than the tier should still render inside the tier.
        show_desc_inside = (
            bool(description) and step >= 56 and _fits_inside(description, caption_size, mid_w, padding=16.0)
        )

        def outside_description(y: float) -> None:
            """Leader line + description text placed to the right of the tier."""
            edge_x = center + mid_w / 2
            available = width - (edge_x + 14) - 6
            wrap_chars = max(4, int(available // max(caption_size, 1.0)))
            elements.append(
                svg_line(edge_x - 2, y, edge_x + 10, y, stroke=ctx["line"], role="connector", **{"stroke-width": 1.2})
            )
            elements.append(
                _text(
                    edge_x + 14,
                    y + 1,
                    description,
                    ctx,
                    "captionSize",
                    fill=ctx["muted"],
                    max_chars=wrap_chars,
                    **{"dominant-baseline": "middle"},
                )
            )

        if _fits_inside(label, label_size, mid_w):
            if show_desc_inside:
                elements.append(
                    _text(
                        center,
                        mid - 6,
                        label,
                        ctx,
                        "labelSize",
                        fill=label_color,
                        max_chars=10,
                        **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"},
                    )
                )
                elements.append(
                    _text(
                        center,
                        mid + 14,
                        description,
                        ctx,
                        "captionSize",
                        fill=label_color,
                        max_chars=14,
                        **{"text-anchor": "middle", "dominant-baseline": "middle", "opacity": 0.85},
                    )
                )
            elif description:
                # Label fits but the description does not: keep the label inside
                # and move the description outside instead of dropping it.
                elements.append(
                    _text(
                        center,
                        mid,
                        label,
                        ctx,
                        "labelSize",
                        fill=label_color,
                        max_chars=10,
                        **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"},
                    )
                )
                outside_description(mid)
            else:
                elements.append(
                    _text(
                        center,
                        mid,
                        label,
                        ctx,
                        "labelSize",
                        fill=label_color,
                        max_chars=10,
                        **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"},
                    )
                )
        else:
            # Outside label keeps the triangle silhouette free of overflowing text.
            edge_x = center + mid_w / 2
            elements.append(
                svg_line(
                    edge_x - 2, mid, edge_x + 10, mid, stroke=ctx["line"], role="connector", **{"stroke-width": 1.2}
                )
            )
            elements.append(
                _text(
                    edge_x + 14,
                    mid + 1,
                    label,
                    ctx,
                    "labelSize",
                    fill=ctx["text"],
                    max_chars=12,
                    **{"font-weight": "bold", "dominant-baseline": "middle"},
                )
            )
            if description:
                elements.append(
                    _text(
                        edge_x + 14,
                        mid + 17,
                        description,
                        ctx,
                        "captionSize",
                        fill=ctx["muted"],
                        max_chars=16,
                        **{"dominant-baseline": "middle"},
                    )
                )
    # Unifying triangular outline: apex flat, base, straight sides.
    top_w, base_w = (max_width, apex_w) if inverted else (apex_w, max_width)
    outline = (
        f"M {_num(center - top_w / 2)} {_num(top)} "
        f"L {_num(center + top_w / 2)} {_num(top)} "
        f"L {_num(center + base_w / 2)} {_num(bottom)} "
        f"L {_num(center - base_w / 2)} {_num(bottom)} Z"
    )
    elements.append(
        svg_path(
            outline,
            role="connector",
            fill="none",
            stroke=ctx["dark"],
            **{"stroke-width": 2, "stroke-linejoin": "round"},
        )
    )
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
        scale = min(
            half_w / abs(ux) if abs(ux) > 1e-6 else float("inf"), half_h / abs(uy) if abs(uy) > 1e-6 else float("inf")
        )
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
        elements.append(
            _text(x, y + 5, str(items[index]["label"]), ctx, "captionSize", max_chars=6, **{"text-anchor": "middle"})
        )
    elements.append(
        svg_circle(
            cx,
            cy,
            center_r,
            fill=_accent_fill(ctx),
            stroke=ctx["dark"],
            **{"stroke-width": ctx["shapes"]["strokeWidthBold"]},
        )
    )
    elements.append(
        _text(
            cx,
            cy + 5,
            str(data.get("center", "")),
            ctx,
            "labelSize",
            fill=ctx["surface"],
            **{"text-anchor": "middle", "font-weight": "bold"},
        )
    )
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
    elements.append(
        svg_circle(
            cx,
            cy,
            center_r,
            fill=_accent_fill(ctx),
            stroke=center_style["stroke"],
            **{"stroke-width": center_style["stroke-width"]},
        )
    )
    elements.append(
        _text(
            cx,
            cy + 5,
            data["center"],
            ctx,
            "labelSize",
            fill=ctx["surface"],
            **{"text-anchor": "middle", "font-weight": "bold"},
        )
    )

    def edge_point(
        origin_x: float, origin_y: float, target_x: float, target_y: float, half_width: float, half_height: float
    ) -> tuple[float, float]:
        dx, dy = target_x - origin_x, target_y - origin_y
        length = math.hypot(dx, dy) or 1
        ux, uy = dx / length, dy / length
        scale = min(
            half_width / abs(ux) if abs(ux) > 1e-6 else float("inf"),
            half_height / abs(uy) if abs(uy) > 1e-6 else float("inf"),
        )
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
        elements.append(
            svg_line(
                start_x, start_y, end_x, end_y, stroke=ctx["line"], **{"stroke-width": ctx["shapes"]["strokeWidth"]}
            )
        )
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
            elements.append(
                svg_line(
                    child_start[0],
                    child_start[1],
                    child_end[0],
                    child_end[1],
                    role="connector",
                    stroke=ctx["line"],
                    **{"stroke-width": ctx["shapes"]["strokeWidth"]},
                )
            )
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
        elements.append(
            _text(
                x,
                y + 5,
                item["label"],
                ctx,
                "captionSize",
                max_chars=10,
                **{"text-anchor": "middle", "font-weight": "bold"},
            )
        )
        children = item.get("children", [])
        for child_index, child in enumerate(children):
            child_angle = angle + (child_index - (len(children) - 1) / 2) * child_spread
            child_radius = min(width, height) * child_radius_factor
            child_x = max(48, min(width - 48, cx + child_radius * math.cos(child_angle)))
            child_y = max(24, min(height - 24, cy + child_radius * math.sin(child_angle)))
            elements.append(
                _node_rect(child_x - child_hw, child_y - child_hh, child_hw * 2, child_hh * 2, ctx, variant="surface")
            )
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
                svg_line(
                    center - w1 / 2 + 6,
                    y1 + 1.2,
                    center + w1 / 2 - 6,
                    y1 + 1.2,
                    stroke="#FFFFFF",
                    role="connector",
                    **{"stroke-width": 1.2, "opacity": 0.28},
                )
            )
        label = str(level["label"])
        mid = (y1 + y2) / 2
        mid_w = (w1 + w2) / 2
        label_color = best_text_on(fill, "#FFFFFF")
        if _fits_inside(label, label_size, mid_w):
            elements.append(
                _text(
                    center,
                    mid,
                    label,
                    ctx,
                    "labelSize",
                    fill=label_color,
                    max_chars=10,
                    **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"},
                )
            )
        else:
            # Overflow labels go to the free side so the taper stays crisp.
            if has_values:
                edge_x = center - mid_w / 2
                elements.append(
                    svg_line(
                        edge_x - 10, mid, edge_x + 2, mid, stroke=ctx["line"], role="connector", **{"stroke-width": 1.2}
                    )
                )
                elements.append(
                    _text(
                        edge_x - 14,
                        mid + 1,
                        label,
                        ctx,
                        "labelSize",
                        fill=ctx["text"],
                        max_chars=12,
                        **{"text-anchor": "end", "font-weight": "bold", "dominant-baseline": "middle"},
                    )
                )
            else:
                edge_x = center + mid_w / 2
                elements.append(
                    svg_line(
                        edge_x - 2, mid, edge_x + 10, mid, stroke=ctx["line"], role="connector", **{"stroke-width": 1.2}
                    )
                )
                elements.append(
                    _text(
                        edge_x + 14,
                        mid + 1,
                        label,
                        ctx,
                        "labelSize",
                        fill=ctx["text"],
                        max_chars=12,
                        **{"font-weight": "bold", "dominant-baseline": "middle"},
                    )
                )
        if has_values and level.get("value") is not None:
            pill_mid = mid
            pill_y = pill_mid - 10
            edge_right = center + mid_w / 2
            elements.append(
                svg_line(
                    edge_right - 1,
                    pill_mid,
                    pill_x - 3,
                    pill_mid,
                    stroke=ctx["line"],
                    role="connector",
                    **{"stroke-width": 1.1, "opacity": 0.7},
                )
            )
            elements.append(
                svg_rect(
                    pill_x,
                    pill_y,
                    pill_w,
                    20,
                    role="marker",
                    fill=ctx["surface"],
                    stroke=ctx["border"],
                    **{"stroke-width": 1.2, "rx": pill_rx, "ry": pill_rx},
                )
            )
            elements.append(
                _text(
                    pill_x + pill_w / 2,
                    pill_mid + 0.5,
                    str(level["value"]),
                    ctx,
                    "captionSize",
                    fill=ctx["text"],
                    max_chars=10,
                    **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"},
                )
            )
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
            elements.append(
                _text(
                    pill_x + pill_w / 2,
                    boundary + 0.5,
                    f"{rate:.0f}%",
                    ctx,
                    "captionSize",
                    fill=ctx["muted"],
                    **{"text-anchor": "middle", "dominant-baseline": "middle"},
                )
            )
    # Unifying funnel outline with straight sides.
    mouth_w, tail_w = (neck_w, max_width) if flared else (max_width, neck_w)
    outline = (
        f"M {_num(center - mouth_w / 2)} {_num(top)} "
        f"L {_num(center + mouth_w / 2)} {_num(top)} "
        f"L {_num(center + tail_w / 2)} {_num(bottom)} "
        f"L {_num(center - tail_w / 2)} {_num(bottom)} Z"
    )
    elements.append(
        svg_path(
            outline,
            role="connector",
            fill="none",
            stroke=ctx["dark"],
            **{"stroke-width": 2, "stroke-linejoin": "round"},
        )
    )
    return elements


def _matrix_cell(ctx: dict, level: int) -> tuple[str, str]:
    """Return `(fill, ink)` for a 0-5 matrix cell with inside text >= 4.5:1.

    The surface→primary mix can land mid-tone (crimson L4 `#DA4F4F` at
    4.2:1); the shared nudge keeps cells and legend swatches identical.
    """
    if level == 0:
        fill = ctx["surface"]
    else:
        fill = _mix_hex(ctx["surface"], ctx["primary"], 0.22 + 0.78 * (level / 5.0))
    ink, adj = ensure_inside_label(fill)
    return adj or fill, ink


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
        elements.append(
            _text(
                cx, top + 20, column, ctx, "labelSize", max_chars=10, **{"text-anchor": "middle", "font-weight": "bold"}
            )
        )
    # Rows + cells. The row winner (max score) gets a dark ring as focal point.
    for i, row in enumerate(rows):
        scores = [max(0, min(5, int(float(score)))) for score in row.get("scores", [])]
        winner = max(scores) if scores else 0
        y = top + header_h + row_h * i
        cy = y + row_h / 2 + 5
        elements.append(
            _text(
                grid_x - 8,
                cy,
                str(row.get("label", "")),
                ctx,
                "labelSize",
                max_chars=12,
                **{"text-anchor": "end", "font-weight": "bold"},
            )
        )
        for j, level in enumerate(scores):
            fill, ink = _matrix_cell(ctx, level)
            x = grid_x + col_w * j
            style: dict[str, object] = {"fill": fill, "stroke": ctx["line"], "stroke-width": 1, "role": "node"}
            if level == winner and winner > 0:
                style.update({"stroke": ctx["dark"], "stroke-width": 2.5})
            if marker:
                style["rx"] = marker
                style["ry"] = marker
            elements.append(svg_rect(x + 1, y + 1, col_w - 2, row_h - 2, **style))
            elements.append(
                _text(
                    x + col_w / 2,
                    cy,
                    str(level),
                    ctx,
                    "labelSize",
                    fill=ink,
                    **{"text-anchor": "middle", "font-weight": "bold", "font-size": 26},
                )
            )
    # Scale legend (0-5 swatches + low/high ends) so the hue steps read at a glance.
    swatch_w, swatch_h, gap = 26.0, 16.0, 6.0
    legend_cells = 6
    legend_w = legend_cells * swatch_w + (legend_cells - 1) * gap
    legend_x = (width - legend_w) / 2
    legend_y = grid_bottom + 14.0
    muted = ctx["muted"]
    elements.append(
        _text(legend_x - 10, legend_y + 12, "Low", ctx, "captionSize", fill=muted, **{"text-anchor": "end"})
    )
    for level in range(legend_cells):
        legend_fill, legend_ink = _matrix_cell(ctx, level)
        sx = legend_x + level * (swatch_w + gap)
        sw_style: dict[str, object] = {"fill": legend_fill, "stroke": ctx["line"], "stroke-width": 1, "role": "node"}
        if marker:
            sw_style["rx"] = marker
            sw_style["ry"] = marker
        elements.append(svg_rect(sx, legend_y, swatch_w, swatch_h, **sw_style))
        elements.append(
            _text(
                sx + swatch_w / 2,
                legend_y + 12,
                str(level),
                ctx,
                "captionSize",
                fill=legend_ink,
                **{"text-anchor": "middle", "font-weight": "bold"},
            )
        )
    elements.append(
        _text(
            legend_x + legend_w + 10, legend_y + 12, "High", ctx, "captionSize", fill=muted, **{"text-anchor": "start"}
        )
    )
    return elements
