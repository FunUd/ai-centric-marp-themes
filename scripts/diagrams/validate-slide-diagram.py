#!/usr/bin/env python3
"""
validate-slide-diagram.py — Slide diagram layout & overflow validator.

Validates that generated diagram SVG or .drawio files strictly conform
to Marp slide canvas constraints to prevent overflow and text distortion.

Usage:
    python scripts/diagrams/validate-slide-diagram.py <file.svg|file.drawio> [--layout full|col2|asym|col3] [--strict]

Exit codes:
    0  Validation passed (or warnings only in non-strict mode)
    1  One or more validation errors found
"""
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from diagram_routing import edge_endpoints, get_edge_waypoints, node_shape, route_edge, segment_intersects_rect, snap_edge_points

# Layout canvas constraints (pixels)
LAYOUT_LIMITS = {
    "full": {"max_w": 1140, "max_h": 470, "min_aspect": 1.2, "max_aspect": 4.5},
    "col2": {"max_w": 540, "max_h": 470, "min_aspect": 0.6, "max_aspect": 2.2},
    "asym": {"max_w": 730, "max_h": 470, "min_aspect": 0.9, "max_aspect": 3.0},
    "col3": {"max_w": 360, "max_h": 470, "min_aspect": 0.4, "max_aspect": 1.8},
}


def _parse_dimension(val: str | None) -> float | None:
    """Extract numeric value from px/pt/raw string."""
    if not val:
        return None
    val = val.strip().lower()
    if val.endswith("%"):
        return None
    val = re.sub(r"[a-z]+$", "", val)
    try:
        return float(val)
    except ValueError:
        return None


def _svg_element_rect(elem: ET.Element) -> tuple[float, float, float, float] | None:
    """Return a conservative bounding box for common JSON SVG primitives."""
    tag = elem.tag.split("}")[-1]
    try:
        if tag == "rect":
            return tuple(float(elem.get(key, "0")) for key in ("x", "y", "width", "height"))
        if tag == "circle":
            cx, cy, radius = (float(elem.get(key, "0")) for key in ("cx", "cy", "r"))
            return cx - radius, cy - radius, radius * 2, radius * 2
        if tag == "ellipse":
            cx, cy, rx, ry = (float(elem.get(key, "0")) for key in ("cx", "cy", "rx", "ry"))
            return cx - rx, cy - ry, rx * 2, ry * 2
        if tag == "polygon":
            points = []
            for pair in (elem.get("points", "").replace(",", " ").split()):
                points.append(float(pair))
            if len(points) >= 4:
                xs, ys = points[::2], points[1::2]
                return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    except ValueError:
        return None
    return None


def _svg_segments(elem: ET.Element) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    tag = elem.tag.split("}")[-1]
    if tag == "line":
        try:
            return [((float(elem.get("x1", "0")), float(elem.get("y1", "0"))), (float(elem.get("x2", "0")), float(elem.get("y2", "0"))))]
        except ValueError:
            return []
    if tag != "path":
        return []
    numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", elem.get("d", ""))]
    points = list(zip(numbers[::2], numbers[1::2]))
    return list(zip(points, points[1:]))


def _rects_overlap(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> bool:
    fx, fy, fw, fh = first
    sx, sy, sw, sh = second
    return fx < sx + sw and sx < fx + fw and fy < sy + sh and sy < fy + fh


def _point_in_rect(point: tuple[float, float], rect: tuple[float, float, float, float]) -> bool:
    x, y = point
    rx, ry, width, height = rect
    return rx <= x <= rx + width and ry <= y <= ry + height


def validate_svg(path: Path, layout: str) -> tuple[list[str], list[str]]:
    """Validate SVG dimension, aspect ratio, and potential text issues."""
    errors: list[str] = []
    warnings: list[str] = []
    limits = LAYOUT_LIMITS.get(layout, LAYOUT_LIMITS["full"])

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return [f"SVG XML parse error: {e}"], []

    root = tree.getroot()
    # Check if root is svg (handling namespace)
    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if tag != "svg":
        return [f"Root element must be <svg>, got <{root.tag}>"], []

    # 1. Dimension & ViewBox Extraction
    view_box = root.get("viewBox")
    width_attr = _parse_dimension(root.get("width"))
    height_attr = _parse_dimension(root.get("height"))

    w, h = None, None
    if view_box:
        parts = [float(p) for p in view_box.replace(",", " ").split() if p.strip()]
        if len(parts) == 4:
            w, h = parts[2], parts[3]
    if w is None or h is None:
        w, h = width_attr, height_attr

    if w is None or h is None or w <= 0 or h <= 0:
        warnings.append(f"Could not determine positive width/height from SVG attributes or viewBox in {path.name}")
    else:
        aspect = w / h
        # Boundary checks
        if h > limits["max_h"]:
            errors.append(
                f"Height ({h:.1f}px) exceeds max allowed height ({limits['max_h']}px) for layout '{layout}'. "
                f"This will cause slide vertical overflow!"
            )
        if w > limits["max_w"]:
            errors.append(
                f"Width ({w:.1f}px) exceeds max allowed width ({limits['max_w']}px) for layout '{layout}'. "
                f"This will cause slide horizontal overflow!"
            )

        # Aspect ratio checks
        if aspect < limits["min_aspect"]:
            warnings.append(
                f"Diagram is too tall/narrow (aspect ratio {aspect:.2f} < {limits['min_aspect']}). "
                f"When placed on a slide, it will be heavily shrunk vertically, making fonts unreadable."
            )
        elif aspect > limits["max_aspect"]:
            warnings.append(
                f"Diagram is extremely wide/short (aspect ratio {aspect:.2f} > {limits['max_aspect']}). "
                f"Consider using multi-row layout or splitting into columns."
            )

    # 2. JSON renderer geometry checks. Elements without diagram roles are ignored.
    node_rects: list[tuple[float, float, float, float]] = []
    connectors: list[tuple[tuple[float, float], tuple[float, float]]] = []
    if w is not None and h is not None and w > 0 and h > 0:
        for elem in root.iter():
            role = elem.get("data-diagram-role")
            if not role:
                continue
            bounds = _svg_element_rect(elem)
            if bounds is not None:
                x, y, width, height = bounds
                if x < 0 or y < 0 or x + width > w or y + height > h:
                    errors.append(f"Element role='{role}' is outside the SVG viewBox")
                if role == "node":
                    node_rects.append(bounds)
            if role == "connector":
                connectors.extend(_svg_segments(elem))

            if role == "label":
                font_size = _parse_dimension(elem.get("font-size"))
                if font_size is not None and font_size < 8:
                    warnings.append(f"Label font size ({font_size:.1f}px) is below the recommended minimum of 8px")

        for index, first in enumerate(node_rects):
            for second in node_rects[index + 1:]:
                if _rects_overlap(first, second):
                    errors.append("JSON diagram nodes overlap")
                    break

        for start, end in connectors:
            for node in node_rects:
                if (_point_in_rect(start, node) or _point_in_rect(end, node)):
                    continue
                if segment_intersects_rect(start, end, node):
                    errors.append("JSON diagram connector crosses a node")
                    break

    # 3. Check for long unbroken text lines in foreignObject or text nodes
    for elem in root.iter():
        text_content = (elem.text or "").strip()
        if len(text_content) > 30 and not any(sep in text_content for sep in [" ", "\n", "、", "。"]):
            warnings.append(f"Long unbroken text detected ('{text_content[:20]}...'). May cause node overflow.")

    return errors, warnings


def validate_drawio(path: Path, layout: str) -> tuple[list[str], list[str]]:
    """Validate .drawio XML structure and cell bounds."""
    errors: list[str] = []
    warnings: list[str] = []
    limits = LAYOUT_LIMITS.get(layout, LAYOUT_LIMITS["full"])

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return [f"draw.io XML parse error: {e}"], []

    root = tree.getroot()
    if root.tag != "mxfile":
        return [f"Root element must be <mxfile>, got <{root.tag}>"], []

    diagrams = root.findall("diagram")
    if not diagrams:
        return ["No <diagram> element found inside <mxfile>"], []

    for d_idx, diag in enumerate(diagrams):
        graph_model = diag.find("mxGraphModel")
        if graph_model is None:
            continue
        root_elem = graph_model.find("root")
        if root_elem is None:
            errors.append(f"Page {d_idx}: Missing <root> inside <mxGraphModel>")
            continue

        cells = root_elem.findall("mxCell")
        cell_map = {cell.get("id"): cell for cell in cells if cell.get("id")}
        cell_ids: set[str] = set()
        has_id0, has_id1 = False, False

        def get_absolute_geom(cell: ET.Element) -> tuple[float, float, float, float]:
            geometry = cell.find("mxGeometry")
            if geometry is None:
                return 0.0, 0.0, 0.0, 0.0
            x = float(geometry.get("x", "0"))
            y = float(geometry.get("y", "0"))
            width = float(geometry.get("width", "0"))
            height = float(geometry.get("height", "0"))
            parent_id = cell.get("parent")
            while parent_id and parent_id not in ("0", "1"):
                parent = cell_map.get(parent_id)
                if parent is None:
                    break
                parent_geometry = parent.find("mxGeometry")
                if parent_geometry is not None:
                    x += float(parent_geometry.get("x", "0"))
                    y += float(parent_geometry.get("y", "0"))
                parent_id = parent.get("parent")
            return x, y, width, height

        def get_absolute_origin(cell_id: str | None) -> tuple[float, float]:
            x, y = 0.0, 0.0
            parent_id = cell_id
            while parent_id and parent_id not in ("0", "1"):
                parent = cell_map.get(parent_id)
                if parent is None:
                    break
                geometry = parent.find("mxGeometry")
                if geometry is not None:
                    x += float(geometry.get("x", "0"))
                    y += float(geometry.get("y", "0"))
                parent_id = parent.get("parent")
            return x, y

        for cell in cells:
            cid = cell.get("id")
            if not cid:
                errors.append(f"Page {d_idx}: Found <mxCell> without 'id'")
                continue
            if cid in cell_ids:
                errors.append(f"Page {d_idx}: Duplicate cell id='{cid}'")
            cell_ids.add(cid)
            if cid == "0":
                has_id0 = True
            if cid == "1":
                has_id1 = True

            # Geometry boundary check for top-level shapes
            if cell.get("parent") == "1" and cell.get("vertex") == "1":
                geom = cell.find("mxGeometry")
                if geom is not None:
                    x = _parse_dimension(geom.get("x")) or 0
                    y = _parse_dimension(geom.get("y")) or 0
                    w = _parse_dimension(geom.get("width")) or 0
                    h = _parse_dimension(geom.get("height")) or 0
                    if x + w > limits["max_w"]:
                        errors.append(
                            f"Cell id='{cid}' bounds ({x+w:.0f}px) exceed canvas width ({limits['max_w']}px)"
                        )
                    if y + h > limits["max_h"]:
                        errors.append(
                            f"Cell id='{cid}' bounds ({y+h:.0f}px) exceed canvas height ({limits['max_h']}px)"
                        )

        vertices = {
            cid: get_absolute_geom(cell)
            for cid, cell in cell_map.items()
            if cell.get("vertex") == "1" and "swimlane" not in cell.get("style", "")
        }
        obstacles = list(vertices.items())
        for edge in cells:
            if edge.get("edge") != "1":
                continue
            source_id = edge.get("source")
            target_id = edge.get("target")
            if source_id not in vertices or target_id not in vertices:
                continue
            source_geometry = vertices[source_id]
            target_geometry = vertices[target_id]
            waypoints = get_edge_waypoints(edge)
            edge_style = edge.get("style", "")
            source_shape = node_shape(cell_map[source_id].get("style") or "")
            target_shape = node_shape(cell_map[target_id].get("style") or "")
            if waypoints:
                origin_x, origin_y = get_absolute_origin(edge.get("parent"))
                first, last = edge_endpoints(source_geometry, target_geometry, edge_style)
                points = snap_edge_points(
                    source_geometry,
                    target_geometry,
                    edge_style,
                    [first, *[(x + origin_x, y + origin_y) for x, y in waypoints], last],
                    source_shape,
                    target_shape,
                )
            else:
                points = route_edge(
                    source_geometry,
                    target_geometry,
                    edge_style,
                    [geometry for _, geometry in obstacles],
                    source_shape=source_shape,
                    target_shape=target_shape,
                )
            for start, end in zip(points, points[1:]):
                for vertex_id, obstacle in obstacles:
                    if vertex_id in (source_id, target_id):
                        continue
                    if segment_intersects_rect(start, end, obstacle):
                        errors.append(
                            f"Edge id='{edge.get('id')}' crosses vertex id='{vertex_id}'"
                        )
                        break

        if not has_id0 or not has_id1:
            errors.append(f"Page {d_idx}: Missing required root cells (id='0' or id='1')")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate diagram file against slide constraints.")
    parser.add_argument("path", type=Path, help="Path to .svg or .drawio file")
    parser.add_argument(
        "--layout",
        choices=["full", "col2", "asym", "col3"],
        default="full",
        help="Target slide layout (default: full)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()

    target_path: Path = args.path
    if not target_path.exists():
        print(f"[ERROR] File not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    suffix = target_path.suffix.lower()
    if suffix == ".svg":
        errors, warnings = validate_svg(target_path, args.layout)
    elif suffix in (".drawio", ".xml"):
        errors, warnings = validate_drawio(target_path, args.layout)
    else:
        print(f"[ERROR] Unsupported file extension '{suffix}'. Expected .svg or .drawio", file=sys.stderr)
        sys.exit(1)

    # Print results
    print(f"=== Diagram Validation: {target_path.name} (Layout: {args.layout}) ===")
    for w in warnings:
        print(f"  [WARN] {w}")
    for e in errors:
        print(f"  [ERROR] {e}")

    if errors or (args.strict and warnings):
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"PASSED: Diagram conforms to slide canvas specifications. ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
