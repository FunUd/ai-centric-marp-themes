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


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _has_port(values: dict[str, str], prefix: str) -> bool:
    return f"{prefix}X" in values and f"{prefix}Y" in values


# Half-height of the cylinder cap ellipse drawn by the SVG converter.
# Keep in sync with the r_h literal in render-slide-diagram.py.
CYLINDER_CAP_RY = 10.0
# Usable fraction of the cap half-width for top/bottom ports (the visible
# curve dips away from the tangent line toward the rim).
CYLINDER_TOP_SPAN = 0.5


def node_shape(style: str) -> str:
    """Icon shape class driving port placement: 'cylinder' or 'rect'."""
    return "cylinder" if "cylinder3" in (style or "") else "rect"


def _port_spans(rect: Rect, shape: str, pad: float) -> dict[str, tuple[float, float] | None]:
    """Clamp spans per side. Cylinders restrict ports to the visible shape."""
    x, y, width, height = rect
    center_x, center_y = x + width / 2, y + height / 2
    if shape == "cylinder":
        half = (width / 2) * CYLINDER_TOP_SPAN
        ns_span: tuple[float, float] | None = (center_x - half, center_x + half)
        body_top, body_bottom = y + CYLINDER_CAP_RY, y + height - pad
        ew_span: tuple[float, float] | None = (
            (body_top, body_bottom) if body_top <= body_bottom else (center_y, center_y)
        )
        return {"N": ns_span, "S": ns_span, "E": ew_span, "W": ew_span}
    y_low, y_high = (y + pad, y + height - pad) if height >= 2 * pad else (center_y, center_y)
    x_low, x_high = (x + pad, x + width - pad) if width >= 2 * pad else (center_x, center_x)
    return {"N": (x_low, x_high), "S": (x_low, x_high), "E": (y_low, y_high), "W": (y_low, y_high)}


def snap_endpoint(rect: Rect, neighbor: Point, pad: float = 4.0, shape: str = "rect") -> Point:
    """Place a connection point on the icon side facing the neighbor.

    The port sits on the dominant-axis side at the neighbor's clamped
    coordinate, so the stub segment always stabs perpendicular into the icon
    instead of sliding in from the wrong side.
    """
    x, y, width, height = rect
    center_x, center_y = x + width / 2, y + height / 2
    dx, dy = neighbor[0] - center_x, neighbor[1] - center_y
    spans = _port_spans(rect, shape, pad)
    if abs(dx) >= abs(dy):
        side = "E" if dx >= 0 else "W"
        low, high = spans[side] or (center_y, center_y)
        return (x + width if dx >= 0 else x, _clamp(neighbor[1], low, high))
    side = "S" if dy >= 0 else "N"
    low, high = spans[side] or (center_x, center_x)
    return (_clamp(neighbor[0], low, high), y + height if dy >= 0 else y)


def _point_on_or_in_rect(point: Point, rect: Rect, tol: float = 0.5) -> bool:
    x, y = point
    rx, ry, width, height = rect
    return rx - tol <= x <= rx + width + tol and ry - tol <= y <= ry + height + tol


def _side_candidates(
    rect: Rect, neighbor: Point, pad: float = 0.5, tol: float = 0.5, shape: str = "rect"
) -> list[tuple[str, Point, float]]:
    """Sides genuinely facing the neighbor: beyond the border with the projection inside the span.

    The inset is a hairline corner guard only; route grid nodes sit exactly on
    obstacle edge lines, so a wide pad would bend stubs sideways.
    """
    x, y, width, height = rect
    nx, ny = neighbor
    spans = _port_spans(rect, shape, pad)
    candidates: list[tuple[str, Point, float]] = []

    def span_ok(side: str, value: float) -> bool:
        span = spans[side]
        if span is None:
            return False
        low, high = span
        return low - tol <= value <= high + tol

    if nx > x + width + tol and span_ok("E", ny):
        low, high = spans["E"] or (ny, ny)
        candidates.append(("E", (x + width, _clamp(ny, low, high)), nx - (x + width)))
    if nx < x - tol and span_ok("W", ny):
        low, high = spans["W"] or (ny, ny)
        candidates.append(("W", (x, _clamp(ny, low, high)), x - nx))
    if ny > y + height + tol and span_ok("S", nx):
        low, high = spans["S"] or (nx, nx)
        candidates.append(("S", (_clamp(nx, low, high), y + height), ny - (y + height)))
    if ny < y - tol and span_ok("N", nx):
        low, high = spans["N"] or (nx, nx)
        candidates.append(("N", (_clamp(nx, low, high), y), y - ny))
    return candidates


def _best_port(rect: Rect, neighbor: Point, shape: str = "rect") -> Point:
    """Port on the icon side the wire actually travels toward.

    Prefers sides facing the neighbor (longest stub wins, dominant axis breaks
    ties) so stubs always stab perpendicular into the icon. Falls back to the
    dominant-axis side when the neighbor hugs the border.
    """
    candidates = _side_candidates(rect, neighbor, shape=shape)
    if candidates:
        x, y, width, height = rect
        dx, dy = neighbor[0] - (x + width / 2), neighbor[1] - (y + height / 2)
        dominant = "EW" if abs(dx) >= abs(dy) else "NS"
        candidates.sort(key=lambda item: (-item[2], 0 if item[0] in dominant else 1))
        return candidates[0][1]
    return snap_endpoint(rect, neighbor, shape=shape)


def _first_outside(points: list[Point], rect: Rect, forward: bool) -> Point:
    """First route point outside the icon (inclusive of its border).

    Routes often start by hugging their own icon border; using such a point
    as the snap reference picks the wrong side. Walk past it instead.
    """
    sequence = points[1:] if forward else points[-2::-1]
    for point in sequence:
        if not _point_on_or_in_rect(point, rect):
            return point
    return points[1] if forward else points[-2]


def _trim_inside(points: list[Point], rect: Rect, forward: bool) -> list[Point]:
    """Drop route leftovers lying on or inside the icon itself.

    The grid route may travel along its own icon border (the icon is not an
    obstacle to itself); after endpoint snapping those leftovers would dip
    the wire back into the icon. Keep the snapped end plus the first point
    outside the icon.
    """
    if len(points) < 2:
        return list(points)
    if forward:
        index = 1
        while index < len(points) - 1 and _point_on_or_in_rect(points[index], rect):
            index += 1
        return [points[0]] + points[index:]
    index = len(points) - 2
    while index > 0 and _point_on_or_in_rect(points[index], rect):
        index -= 1
    return points[: index + 1] + [points[-1]]


def _port_sides(rect: Rect, port: Point, tol: float = 1.0) -> set[str]:
    """Border sides a port sits on (corner ports report two sides)."""
    x, y, width, height = rect
    sides: set[str] = set()
    if abs(port[0] - x) <= tol:
        sides.add("W")
    if abs(port[0] - (x + width)) <= tol:
        sides.add("E")
    if abs(port[1] - y) <= tol:
        sides.add("N")
    if abs(port[1] - (y + height)) <= tol:
        sides.add("S")
    return sides


def _elbow_for_stub(rect: Rect, port: Point, neighbor: Point) -> Point | None:
    """Elbow point keeping a diagonal stub's icon-side segment perpendicular.

    Returns None when the stub already stabs straight into its side.
    """
    dx, dy = neighbor[0] - port[0], neighbor[1] - port[1]
    if abs(dx) <= 1.0 or abs(dy) <= 1.0:
        return None
    sides = _port_sides(rect, port)
    if abs(dx) >= abs(dy) and sides & {"E", "W"}:
        return (neighbor[0], port[1])
    if abs(dy) > abs(dx) and sides & {"N", "S"}:
        return (port[0], neighbor[1])
    if sides & {"N", "S"}:
        return (port[0], neighbor[1])
    if sides & {"E", "W"}:
        return (neighbor[0], port[1])
    return None


def snap_edge_points(
    source_geometry: Rect,
    target_geometry: Rect,
    style: str,
    points: list[Point],
    source_shape: str = "rect",
    target_shape: str = "rect",
) -> list[Point]:
    """Snap polyline ends onto icon borders perpendicular to travel direction.

    Ends with explicit draw.io exit/entry ports are left untouched.
    Diagonal leftover stubs get an orthogonal elbow so the icon-side
    segment always stabs straight in.
    """
    if len(points) < 2:
        return list(points)
    values = parse_style(style)
    snapped = list(points)
    if not _has_port(values, "exit"):
        snapped[0] = _best_port(
            source_geometry, _first_outside(points, source_geometry, True), source_shape
        )
    if not _has_port(values, "entry"):
        snapped[-1] = _best_port(
            target_geometry, _first_outside(points, target_geometry, False), target_shape
        )
    snapped = _trim_inside(snapped, source_geometry, True)
    snapped = _trim_inside(snapped, target_geometry, False)
    if len(snapped) >= 2:
        elbow = _elbow_for_stub(source_geometry, snapped[0], snapped[1])
        if elbow is not None:
            snapped = [snapped[0], elbow] + snapped[1:]
    if len(snapped) >= 2:
        elbow = _elbow_for_stub(target_geometry, snapped[-1], snapped[-2])
        if elbow is not None:
            snapped = snapped[:-1] + [elbow, snapped[-1]]
    return _simplify(snapped)


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
    source_shape: str = "rect",
    target_shape: str = "rect",
) -> list[Point]:
    source, target = edge_endpoints(source_geometry, target_geometry, style)
    blocked = [
        _inflate(obstacle, margin)
        for obstacle in obstacles
        if not _same_rect(obstacle, source_geometry) and not _same_rect(obstacle, target_geometry)
    ]
    points = _simplify(_grid_route(source, target, blocked))
    # Re-snap ends so stubs stab perpendicular into the approached side.
    return snap_edge_points(
        source_geometry, target_geometry, style, points, source_shape, target_shape
    )