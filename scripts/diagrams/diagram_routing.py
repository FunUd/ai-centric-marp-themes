"""Shared orthogonal routing helpers for draw.io diagrams."""
from __future__ import annotations

from heapq import heappop, heappush
from math import inf
import xml.etree.ElementTree as ET

Point = tuple[float, float]
Rect = tuple[float, float, float, float]


def parse_style(style: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in style.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def geometry_to_rect(cell: ET.Element) -> Rect:
    geometry = cell.find("mxGeometry")
    if geometry is None:
        return 0.0, 0.0, 0.0, 0.0
    return tuple(float(geometry.get(key, "0")) for key in ("x", "y", "width", "height"))  # type: ignore[return-value]


def get_edge_waypoints(edge: ET.Element) -> list[Point]:
    geometry = edge.find("mxGeometry")
    if geometry is None:
        return []
    points = geometry.find("Array[@as='points']")
    if points is None:
        return []
    return [
        (float(point.get("x", "0")), float(point.get("y", "0")))
        for point in points.findall("mxPoint")
    ]


def _inflate(rect: Rect, margin: float) -> Rect:
    x, y, width, height = rect
    return x - margin, y - margin, width + 2 * margin, height + 2 * margin


def _same_rect(left: Rect, right: Rect) -> bool:
    return all(abs(a - b) < 0.001 for a, b in zip(left, right))


def segment_intersects_rect(start: Point, end: Point, rect: Rect) -> bool:
    """Return whether an axis-aligned segment enters the interior of a rectangle."""
    x1, y1 = start
    x2, y2 = end
    rx, ry, rw, rh = rect
    right = rx + rw
    bottom = ry + rh

    if abs(x1 - x2) < 0.001:
        return rx < x1 < right and max(min(y1, y2), ry) < min(max(y1, y2), bottom)
    if abs(y1 - y2) < 0.001:
        return ry < y1 < bottom and max(min(x1, x2), rx) < min(max(x1, x2), right)
    return False


def _clear_segment(start: Point, end: Point, obstacles: list[Rect]) -> bool:
    return not any(segment_intersects_rect(start, end, obstacle) for obstacle in obstacles)


def _port_point(rect: Rect, other: Rect, style: dict[str, str], prefix: str) -> Point:
    x, y, width, height = rect
    coordinate_x = style.get(f"{prefix}X")
    coordinate_y = style.get(f"{prefix}Y")
    if coordinate_x is not None and coordinate_y is not None:
        return x + width * float(coordinate_x), y + height * float(coordinate_y)

    other_x, other_y, other_width, other_height = other
    center = (x + width / 2, y + height / 2)
    other_center = (other_x + other_width / 2, other_y + other_height / 2)
    if abs(center[0] - other_center[0]) >= abs(center[1] - other_center[1]):
        return (x + width, center[1]) if center[0] < other_center[0] else (x, center[1])
    return (center[0], y + height) if center[1] < other_center[1] else (center[0], y)


def edge_endpoints(source_geometry: Rect, target_geometry: Rect, style: str) -> tuple[Point, Point]:
    style_values = parse_style(style)
    return (
        _port_point(source_geometry, target_geometry, style_values, "exit"),
        _port_point(target_geometry, source_geometry, style_values, "entry"),
    )


def _grid_route(start: Point, end: Point, obstacles: list[Rect]) -> list[Point]:
    x_values = {start[0], end[0]}
    y_values = {start[1], end[1]}
    for x, y, width, height in obstacles:
        x_values.update((x, x + width))
        y_values.update((y, y + height))

    points = [(x, y) for x in sorted(x_values) for y in sorted(y_values)]
    usable = [point for point in points if all(point not in ((x, y), (x + width, y + height)) and not (x < point[0] < x + width and y < point[1] < y + height) for x, y, width, height in obstacles)]
    neighbors: dict[Point, list[Point]] = {point: [] for point in usable}
    for point in usable:
        for candidate in usable:
            if point == candidate or (point[0] != candidate[0] and point[1] != candidate[1]):
                continue
            if _clear_segment(point, candidate, obstacles):
                neighbors[point].append(candidate)

    distances: dict[Point, float] = {start: 0}
    previous: dict[Point, Point] = {}
    queue: list[tuple[float, Point]] = [(0, start)]
    while queue:
        distance, current = heappop(queue)
        if distance != distances.get(current):
            continue
        if current == end:
            break
        for candidate in neighbors.get(current, []):
            step = abs(current[0] - candidate[0]) + abs(current[1] - candidate[1])
            new_distance = distance + step
            if new_distance < distances.get(candidate, inf):
                distances[candidate] = new_distance
                previous[candidate] = current
                heappush(queue, (new_distance, candidate))

    if end not in distances:
        return [start, end]
    route = [end]
    while route[-1] != start:
        route.append(previous[route[-1]])
    route.reverse()
    return route


def _simplify(points: list[Point]) -> list[Point]:
    simplified: list[Point] = []
    for point in points:
        if simplified and point == simplified[-1]:
            continue
        if len(simplified) >= 2:
            previous, current = simplified[-2], simplified[-1]
            if (previous[0] == current[0] == point[0]) or (previous[1] == current[1] == point[1]):
                simplified[-1] = point
                continue
        simplified.append(point)
    return simplified


def route_edge(
    source_geometry: Rect,
    target_geometry: Rect,
    style: str,
    obstacles: list[Rect],
    margin: float = 8.0,
) -> list[Point]:
    source, target = edge_endpoints(source_geometry, target_geometry, style)
    blocked = [
        _inflate(obstacle, margin)
        for obstacle in obstacles
        if not _same_rect(obstacle, source_geometry) and not _same_rect(obstacle, target_geometry)
    ]
    return _simplify(_grid_route(source, target, blocked))