from __future__ import annotations

import math

from design_tokens import best_text_on, ensure_inside_label

from .primitives import (
    _marker_rx,
    _num,
    _text,
    _text_width,
    _title,
    svg_circle,
    svg_line,
    svg_path,
    svg_rect,
)


CHART_CY_FULL = 0.53


CHART_R_FULL = 0.37


CARTESIAN_PALETTE = ["primary", "success", "warning", "accent", "danger", "dark"]


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
                elements.append(
                    _text(
                        tx,
                        ty - 8,
                        label_text,
                        ctx,
                        "captionSize",
                        fill=ink,
                        **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"},
                    )
                )
                elements.append(
                    _text(
                        tx,
                        ty + 10,
                        pct_text,
                        ctx,
                        "captionSize",
                        fill=ink,
                        **{"text-anchor": "middle", "dominant-baseline": "middle"},
                    )
                )
            elif radial_one and pct_ok:
                elements.append(
                    _text(
                        tx,
                        ty,
                        pct_text,
                        ctx,
                        "captionSize",
                        fill=ink,
                        **{"text-anchor": "middle", "font-weight": "bold", "dominant-baseline": "middle"},
                    )
                )
        start = end
    if donut:
        elements.append(
            _text(
                cx,
                cy + 5,
                str(data.get("center_label", "合計")),
                ctx,
                "labelSize",
                **{"text-anchor": "middle", "font-weight": "bold"},
            )
        )
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
    return {"min": floor, "max": ceiling, "step": step, "ticks": [floor + index * step for index in range(count + 1)]}


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
        elements.append(
            svg_line(plot_left, y, plot_right, y, stroke=muted, role="axis", **{"stroke-width": 1, "opacity": 0.45})
        )
        elements.append(
            _text(plot_left - 8, y + 4, label, ctx, "captionSize", fill=muted, max_chars=14, **{"text-anchor": "end"})
        )
    # Axes baselines.
    elements.append(
        svg_line(plot_left, plot_top, plot_left, plot_bottom, stroke=muted, role="axis", **{"stroke-width": 1.2})
    )
    elements.append(
        svg_line(
            plot_left,
            y_pos(scale["min"] if scale["min"] > 0 else 0),
            plot_right,
            y_pos(scale["min"] if scale["min"] > 0 else 0),
            stroke=ctx["line"],
            role="axis",
            **{"stroke-width": 1.5},
        )
    )
    # X labels.
    for index, label in enumerate(x_labels):
        elements.append(
            _text(x_pos(index), plot_bottom + 18, label, ctx, "captionSize", max_chars=8, **{"text-anchor": "middle"})
        )
    return {
        "elements": elements,
        "x": x_pos,
        "y": y_pos,
        "slot": slot,
        "plot_left": plot_left,
        "plot_top": plot_top,
        "plot_bottom": plot_bottom,
        "scale": scale,
        "tick_labels": tick_labels,
    }


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
        elements.append(
            svg_rect(x - bar_w / 2, top, bar_w, max(0.0, base - top), role="node", fill=fill, stroke="none")
        )
        if show_values:
            elements.append(
                _text(
                    x,
                    top - 8,
                    _fmt_tick(value),
                    ctx,
                    "captionSize",
                    max_chars=10,
                    **{"text-anchor": "middle", "font-weight": "bold"},
                )
            )
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
            elements.append(
                svg_circle(x, y, 4.5, role="marker", fill=ctx["surface"], stroke=color, **{"stroke-width": 2})
            )
            if show_values:
                elements.append(
                    _text(
                        x,
                        y - 12,
                        _fmt_tick(float(value)),
                        ctx,
                        "captionSize",
                        max_chars=10,
                        **{"text-anchor": "middle"},
                    )
                )
    return elements


def _stacked_bar(data: dict, ctx: dict) -> list[str]:
    categories = [str(category) for category in data["categories"]]
    series = data["series"]
    colors = _series_colors(ctx, len(series))
    # Inside value labels need 4.5:1 vs their segment; nudge the shared
    # palette entry when even the best ink falls short (azure/nebula primary
    # at 4.1-4.2:1) so segments and legend swatches stay identical.
    colors = [ensure_inside_label(color)[1] or color for color in colors]
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
            elements.append(
                svg_rect(
                    x - bar_w / 2,
                    top,
                    bar_w,
                    max(0.0, seg_h),
                    role="node",
                    fill=color,
                    stroke=ctx["surface"],
                    **{"stroke-width": 1.5},
                )
            )
            if show_values and seg_h >= 20:
                elements.append(
                    _text(
                        x,
                        top + seg_h / 2 + 4,
                        _fmt_tick(float(entry["values"][index])),
                        ctx,
                        "captionSize",
                        fill=best_text_on(color, "#FFFFFF"),
                        max_chars=8,
                        **{"text-anchor": "middle", "font-weight": "bold"},
                    )
                )
            base = top
        if show_values:
            elements.append(
                _text(
                    frame["x"](index),
                    frame["y"](totals[index]) - 8,
                    _fmt_tick(totals[index]),
                    ctx,
                    "captionSize",
                    max_chars=10,
                    **{"text-anchor": "middle", "font-weight": "bold"},
                )
            )
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
        elements.append(
            svg_line(x, plot_top, x, plot_bottom, stroke=muted, role="axis", **{"stroke-width": 1, "opacity": 0.45})
        )
        unit = str(data.get("unit", "") or "")
        tag = _fmt_tick(tick) + (" " + unit if unit and tick == scale["ticks"][-1] else "")
        elements.append(
            _text(x, plot_bottom + 18, tag, ctx, "captionSize", fill=muted, max_chars=14, **{"text-anchor": "middle"})
        )
    elements.append(
        svg_line(plot_left, plot_top, plot_left, plot_bottom, stroke=muted, role="axis", **{"stroke-width": 1.2})
    )
    elements.append(
        svg_line(
            plot_left, plot_bottom, plot_right, plot_bottom, stroke=ctx["line"], role="axis", **{"stroke-width": 1.5}
        )
    )
    show_values = bool(data.get("show_values", True))
    # Ordered single-series ranking: keep the single-primary default so length
    # alone encodes order (one-accent rule; adjacent saturated hues are banned).
    # A per-item `color` is honored for nominal categories, but the showcase
    # template intentionally omits it.
    for index, (item, label, value) in enumerate(zip(data["items"], labels, values)):
        y_center = plot_top + slot * (index + 0.5)
        elements.append(
            _text(plot_left - 8, y_center + 5, label, ctx, "labelSize", max_chars=12, **{"text-anchor": "end"})
        )
        x_end = x_pos(value)
        bar_len = max(0.0, x_end - plot_left)
        y_top = y_center - bar_h / 2
        fill = item.get("color", ctx["primary"]) if isinstance(item, dict) else ctx["primary"]
        # Inside values need 4.5:1; nudge the bar fill when even the best ink
        # falls short (azure/nebula primary at 4.1-4.2:1). Hue is preserved.
        bar_ink, bar_fill = ensure_inside_label(fill)
        elements.append(svg_rect(plot_left, y_top, bar_len, bar_h, role="node", fill=bar_fill, stroke="none"))
        if show_values:
            tag = _fmt_tick(value)
            if bar_len >= 64:
                elements.append(
                    _text(
                        x_end - 8,
                        y_center + 5,
                        tag,
                        ctx,
                        "labelSize",
                        fill=bar_ink,
                        max_chars=10,
                        **{"text-anchor": "end", "font-weight": "bold"},
                    )
                )
            else:
                elements.append(
                    _text(
                        x_end + 8,
                        y_center + 5,
                        tag,
                        ctx,
                        "labelSize",
                        max_chars=10,
                        **{"text-anchor": "start", "font-weight": "bold"},
                    )
                )
    return elements


def _stacked_bar_100(data: dict, ctx: dict) -> list[str]:
    """100% stacked bars. Same input as stacked-bar; segments normalized per category."""
    categories = [str(category) for category in data["categories"]]
    series = data["series"]
    colors = _series_colors(ctx, len(series))
    # Same inside-label guarantee as _stacked_bar: nudge shared fills so
    # segments and legend swatches stay identical.
    colors = [ensure_inside_label(color)[1] or color for color in colors]
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
            elements.append(
                svg_rect(
                    x - bar_w / 2,
                    top,
                    bar_w,
                    max(0.0, seg_h),
                    role="node",
                    fill=color,
                    stroke=ctx["surface"],
                    **{"stroke-width": 1.5},
                )
            )
            if show_values and seg_h >= 26:
                elements.append(
                    _text(
                        x,
                        top + seg_h / 2 + 5,
                        f"{row[index]:.0f}%",
                        ctx,
                        "captionSize",
                        fill=best_text_on(color, "#FFFFFF"),
                        max_chars=8,
                        **{"text-anchor": "middle", "font-weight": "bold", "font-size": 16},
                    )
                )
            base = top
    return elements
