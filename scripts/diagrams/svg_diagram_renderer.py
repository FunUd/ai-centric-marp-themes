from __future__ import annotations

import html
import math
from typing import Iterable

from diagram_models import parse_diagram_data


def _num(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def escape_xml(value: str) -> str:
    return html.escape(str(value), quote=True)


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
    return f"<text {attrs}>{escape_xml(text)}</text>"


def svg_document(width: float, height: float, elements: Iterable[str], background: str = "transparent") -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_num(width)} {_num(height)}" width="{_num(width)}" height="{_num(height)}" style="background:{escape_xml(background)}">{"".join(elements)}</svg>'


def _colors(theme: dict) -> dict[str, str]:
    colors = theme.get("colors", {})
    return {"primary": colors.get("primary", "#2C7BE5"), "dark": colors.get("primaryDark", "#1B5FC0"), "light": colors.get("primaryLight", "#D0EBFF"), "pale": colors.get("primaryPale", "#EDF5FF"), "accent": colors.get("accent", "#1B4F72"), "text": colors.get("text", "#1A1A2E"), "muted": colors.get("textMuted", "#5A6C7D"), "line": colors.get("line", "#2C7BE5"), "surface": colors.get("surface", "#FFFFFF"), "border": colors.get("border", "#B8D4E8"), "success": colors.get("success", "#27AE60"), "warning": colors.get("warning", "#F39C12"), "danger": colors.get("danger", "#E74C3C")}


def _text(x: float, y: float, value: str, colors: dict, size: float = 14, **extra: object) -> str:
    return svg_text(x, y, value, **{"font-family": "sans-serif", "font-size": size, "fill": colors["text"], **extra})


def _chart(data: dict, colors: dict, donut: bool) -> list[str]:
    width, height = data["width"], data["height"]
    cx, cy, radius = width * 0.32, height * 0.55, min(height * 0.34, width * 0.23)
    total = sum(float(item["value"]) for item in data["items"])
    palette = [colors["primary"], colors["accent"], colors["success"], colors["warning"], colors["danger"], colors["dark"]]
    elements: list[str] = []
    start = -math.pi / 2
    for index, item in enumerate(data["items"]):
        end = start + math.tau * float(item["value"]) / total
        large = 1 if end - start > math.pi else 0
        x1, y1 = cx + radius * math.cos(start), cy + radius * math.sin(start)
        x2, y2 = cx + radius * math.cos(end), cy + radius * math.sin(end)
        if donut:
            inner = radius * float(data.get("inner_ratio", 0.58))
            ix2, iy2 = cx + inner * math.cos(end), cy + inner * math.sin(end)
            ix1, iy1 = cx + inner * math.cos(start), cy + inner * math.sin(start)
            d = f"M {_num(x1)} {_num(y1)} A {_num(radius)} {_num(radius)} 0 {large} 1 {_num(x2)} {_num(y2)} L {_num(ix2)} {_num(iy2)} A {_num(inner)} {_num(inner)} 0 {large} 0 {_num(ix1)} {_num(iy1)} Z"
        else:
            d = f"M {_num(cx)} {_num(cy)} L {_num(x1)} {_num(y1)} A {_num(radius)} {_num(radius)} 0 {large} 1 {_num(x2)} {_num(y2)} Z"
        elements.append(svg_path(d, role="node", fill=item.get("color", palette[index % len(palette)]), stroke=colors["surface"], **{"stroke-width": 2}))
        start = end
    if donut:
        elements.append(_text(cx, cy + 5, str(data.get("center_label", "合計")), colors, 16, **{"text-anchor": "middle", "font-weight": "bold"}))
    legend_x = width * 0.62 if data["layout"] == "full" else width * 0.12
    legend_y = height * 0.28 if data["layout"] == "full" else height * 0.84
    for index, item in enumerate(data["items"]):
        x, y = legend_x, legend_y + index * 25
        elements.append(svg_rect(x, y - 11, 12, 12, role="node", fill=item.get("color", palette[index % len(palette)]), stroke="none"))
        value = f" ({item['value']})" if data.get("show_values") else ""
        elements.append(_text(x + 20, y, str(item["label"]) + value, colors, 13))
    if data.get("title"):
        elements.insert(0, _text(width / 2, 28, data["title"], colors, 20, **{"text-anchor": "middle", "font-weight": "bold"}))
    return elements


def _pyramid(data: dict, colors: dict) -> list[str]:
    width, height = data["width"], data["height"]
    levels = data["levels"]
    top, bottom = 58, height - 22
    center = width / 2
    max_width = min(width * 0.82, 500)
    step = (bottom - top) / len(levels)
    elements = [_text(center, 28, data.get("title", ""), colors, 20, **{"text-anchor": "middle", "font-weight": "bold"})] if data.get("title") else []
    for index, level in enumerate(levels):
        visual = index if data.get("direction", "up") == "up" else len(levels) - index - 1
        y1, y2 = top + index * step, top + (index + 1) * step
        w1 = max_width * (visual + 1) / len(levels)
        w2 = max_width * (visual + 2) / len(levels) if visual + 1 < len(levels) else max_width
        points = [(center - w1 / 2, y1), (center + w1 / 2, y1), (center + w2 / 2, y2), (center - w2 / 2, y2)]
        elements.append(svg_polygon(points, fill=colors["primary"] if index % 2 == 0 else colors["light"], stroke=colors["surface"], **{"stroke-width": 2}))
        elements.append(_text(center, y1 + step * 0.48, str(level["label"]), colors, 14, **{"text-anchor": "middle", "font-weight": "bold"}))
    return elements


def _cycle(data: dict, colors: dict) -> list[str]:
    width, height = data["width"], data["height"]
    cx, cy, radius = width / 2, height / 2 + 8, min(width, height) * 0.29
    node_w, node_h = min(150, width * 0.22), 42
    items = data["items"]
    elements = [_text(cx, 28, data.get("title", ""), colors, 20, **{"text-anchor": "middle", "font-weight": "bold"})] if data.get("title") else []
    positions = []
    direction = 1 if data.get("direction", "clockwise") == "clockwise" else -1
    for index, item in enumerate(items):
        angle = -math.pi / 2 + direction * math.tau * index / len(items)
        positions.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    for index, (x, y) in enumerate(positions):
        nx, ny = positions[(index + 1) % len(positions)]
        elements.append(svg_arrow(x, y, nx, ny, colors["line"], role="connector", fill="none"))
    for index, (x, y) in enumerate(positions):
        elements.append(svg_rect(x - node_w / 2, y - node_h / 2, node_w, node_h, fill=colors["pale"], stroke=colors["primary"], rx=8, **{"stroke-width": 1.5}))
        elements.append(_text(x, y + 5, str(items[index]["label"]), colors, 13, **{"text-anchor": "middle"}))
    elements.append(svg_circle(cx, cy, radius * 0.38, fill=colors["surface"], stroke=colors["accent"], **{"stroke-width": 2}))
    elements.append(_text(cx, cy + 5, str(data.get("center", "")), colors, 15, **{"text-anchor": "middle", "font-weight": "bold"}))
    return elements


def _timeline(data: dict, colors: dict) -> list[str]:
    width, height = data["width"], data["height"]
    periods, items = data["periods"], data["items"]
    horizontal = data.get("orientation", "horizontal") == "horizontal"
    elements = [_text(width / 2, 28, data.get("title", ""), colors, 20, **{"text-anchor": "middle", "font-weight": "bold"})] if data.get("title") else []
    status_colors = {"done": colors["success"], "active": colors["primary"], "planned": colors["muted"], "blocked": colors["danger"]}
    if horizontal:
        axis_y, left, usable = height * 0.55, 72, width - 144
        points = [(left + usable * i / max(1, len(periods) - 1), axis_y) for i in range(len(periods))]
        period_index = {period: index for index, period in enumerate(periods)}
        for item in items:
            if item.get("start_period") in period_index and item.get("end_period") in period_index:
                start_x = points[period_index[item["start_period"]]][0]
                end_x = points[period_index[item["end_period"]]][0]
                elements.append(svg_rect(start_x, axis_y - 30, max(12, end_x - start_x), 8, role="marker", fill=status_colors[item.get("status", "planned")], stroke="none", rx=4))
        elements.append(svg_line(left, axis_y, width - left, axis_y, stroke=colors["line"], **{"stroke-width": 2}))
        for i, period in enumerate(periods):
            x, y = points[i]
            elements.append(svg_circle(x, y, 7, role="marker", fill=colors["surface"], stroke=colors["primary"], **{"stroke-width": 2}))
            elements.append(_text(x, axis_y + 28, period, colors, 12, **{"text-anchor": "middle", "font-weight": "bold"}))
            same = [item for item in items if item["period"] == period]
            for offset, item in enumerate(same):
                event_y = axis_y - 58 - (offset % 2) * 60 if offset % 2 == 0 else axis_y + 58 + (offset % 2) * 60
                elements.append(svg_line(x, axis_y, x, event_y + (8 if event_y < axis_y else -8), stroke=colors["line"], **{"stroke-width": 1}))
                elements.append(_text(x, event_y, item["label"], colors, 12, **{"text-anchor": "middle", "font-weight": "bold"}))
                elements.append(svg_circle(x, event_y + (8 if event_y < axis_y else -8), 5, fill=status_colors[item.get("status", "planned")], stroke="none"))
    else:
        axis_x, top, usable = 120, 56, height - 82
        period_index = {period: index for index, period in enumerate(periods)}
        period_points = {period: top + usable * index / max(1, len(periods) - 1) for period, index in period_index.items()}
        for item in items:
            if item.get("start_period") in period_points and item.get("end_period") in period_points:
                start_y = period_points[item["start_period"]]
                end_y = period_points[item["end_period"]]
                elements.append(svg_rect(axis_x - 30, start_y, 8, max(12, end_y - start_y), role="marker", fill=status_colors[item.get("status", "planned")], stroke="none", rx=4))
        elements.append(svg_line(axis_x, top, axis_x, height - 26, stroke=colors["line"], **{"stroke-width": 2}))
        for i, period in enumerate(periods):
            y = top + usable * i / max(1, len(periods) - 1)
            elements.append(svg_circle(axis_x, y, 7, role="marker", fill=colors["surface"], stroke=colors["primary"], **{"stroke-width": 2}))
            elements.append(_text(axis_x - 16, y + 5, period, colors, 12, **{"text-anchor": "end", "font-weight": "bold"}))
            for offset, item in enumerate(item for item in items if item["period"] == period):
                x = axis_x + 34 + offset * 150
                elements.append(svg_line(axis_x, y, x - 10, y, stroke=colors["line"], **{"stroke-width": 1}))
                elements.append(svg_rect(x, y - 19, 130, 38, fill=colors["pale"], stroke=status_colors[item.get("status", "planned")], rx=6))
                elements.append(_text(x + 65, y + 5, item["label"], colors, 12, **{"text-anchor": "middle"}))
    return elements


def _org_chart(data: dict, colors: dict) -> list[str]:
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
    node_w, node_h = min(170, width / max(2, len(levels[-1]) + 1)), 38
    top = 58
    elements = [_text(width / 2, 28, data.get("title", ""), colors, 20, **{"text-anchor": "middle", "font-weight": "bold"})] if data.get("title") else []
    for depth, nodes in enumerate(levels):
        y = top + depth * ((height - top - 20) / max(1, len(levels) - 1))
        spacing = width / (len(nodes) + 1)
        for index, node in enumerate(nodes):
            positions[id(node)] = (spacing * (index + 1), y)
            parent = next((candidate for candidate in sum(levels[:depth], []) if node in candidate.get("children", [])), None)
            if parent:
                px, py = positions[id(parent)]
                elements.append(svg_line(px, py + node_h / 2, spacing * (index + 1), y - node_h / 2, stroke=colors["line"], **{"stroke-width": 1.5}))
    for nodes in levels:
        for node in nodes:
            x, y = positions[id(node)]
            elements.append(svg_rect(x - node_w / 2, y - node_h / 2, node_w, node_h, fill=colors["pale"], stroke=colors["primary"], rx=6))
            elements.append(_text(x, y + 5, node["label"], colors, 12, **{"text-anchor": "middle"}))
    return elements


def _radial(data: dict, colors: dict) -> list[str]:
    width, height = data["width"], data["height"]
    cx, cy = width / 2, height / 2 + 8
    outer = min(width, height) * 0.36
    elements = [_text(width / 2, 28, data.get("title", ""), colors, 20, **{"text-anchor": "middle", "font-weight": "bold"})] if data.get("title") else []
    center_r = min(54, width * 0.12)
    elements.append(svg_circle(cx, cy, center_r, fill=colors["primary"], stroke=colors["dark"], **{"stroke-width": 2}))
    elements.append(_text(cx, cy + 5, data["center"], {**colors, "text": colors["surface"]}, 14, **{"text-anchor": "middle", "font-weight": "bold"}))
    for index, item in enumerate(data["items"]):
        angle = -math.pi / 2 + math.tau * index / len(data["items"])
        x, y = cx + outer * math.cos(angle), cy + outer * math.sin(angle)
        elements.append(svg_line(cx + center_r * math.cos(angle), cy + center_r * math.sin(angle), x, y, stroke=colors["line"], **{"stroke-width": 1.5}))
        elements.append(svg_rect(x - 60, y - 20, 120, 40, fill=colors["pale"], stroke=colors["primary"], rx=7))
        elements.append(_text(x, y + 5, item["label"], colors, 12, **{"text-anchor": "middle", "font-weight": "bold"}))
        children = item.get("children", [])
        for child_index, child in enumerate(children):
            child_angle = angle + (child_index - (len(children) - 1) / 2) * 0.50
            child_radius = min(width, height) * 0.60
            child_x = max(48, min(width - 48, cx + child_radius * math.cos(child_angle)))
            child_y = max(24, min(height - 24, cy + child_radius * math.sin(child_angle)))
            elements.append(svg_line(x, y, child_x, child_y, role="connector", stroke=colors["line"], **{"stroke-width": 1}))
            elements.append(svg_rect(child_x - 42, child_y - 14, 84, 28, role="node", fill=colors["surface"], stroke=colors["border"], rx=5))
            elements.append(_text(child_x, child_y + 4, str(child), colors, 10, **{"text-anchor": "middle"}))
    return elements


def render_diagram(data: dict, theme_data: dict, layout: str) -> str:
    data = parse_diagram_data({**data, "layout": data.get("layout", layout)})
    colors = _colors(theme_data)
    kind = data["type"]
    if kind in {"pie", "donut"}:
        elements = _chart(data, colors, kind == "donut")
    elif kind == "pyramid":
        elements = _pyramid(data, colors)
    elif kind == "cycle":
        elements = _cycle(data, colors)
    elif kind == "timeline":
        elements = _timeline(data, colors)
    elif kind == "org-chart":
        elements = _org_chart(data, colors)
    else:
        elements = _radial(data, colors)
    return svg_document(data["width"], data["height"], elements, theme_data.get("colors", {}).get("background", "transparent"))