from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_script_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


routing = load_script_module("diagram_routing", "diagram_routing.py")
validator = load_script_module("diagram_validator", "validate-slide-diagram.py")


def make_cell(cell_id: str, x: float, y: float, width: float, height: float) -> ET.Element:
    cell = ET.Element("mxCell", {"id": cell_id, "vertex": "1", "parent": "1"})
    ET.SubElement(
        cell,
        "mxGeometry",
        {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"},
    )
    return cell


def test_explicit_waypoints_are_read_from_edge_geometry() -> None:
    edge = ET.fromstring(
        """
        <mxCell id="edge" edge="1" source="source" target="target">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="80" y="40" />
              <mxPoint x="80" y="90" />
            </Array>
          </mxGeometry>
        </mxCell>
        """
    )

    assert routing.get_edge_waypoints(edge) == [(80.0, 40.0), (80.0, 90.0)]


def test_automatic_route_avoids_intermediate_box() -> None:
    source = make_cell("source", 0, 40, 40, 20)
    blocker = make_cell("blocker", 70, 30, 40, 40)
    target = make_cell("target", 140, 40, 40, 20)

    points = routing.route_edge(
        source_geometry=(0, 40, 40, 20),
        target_geometry=(140, 40, 40, 20),
        style="edgeStyle=orthogonalEdgeStyle;",
        obstacles=[routing.geometry_to_rect(blocker), routing.geometry_to_rect(source), routing.geometry_to_rect(target)],
    )

    assert len(points) >= 4
    assert not any(
        routing.segment_intersects_rect(start, end, routing.geometry_to_rect(blocker))
        for start, end in zip(points, points[1:])
    )


def test_drawio_validation_rejects_edge_that_crosses_a_box(tmp_path: Path) -> None:
    drawio = tmp_path / "crossing.drawio"
    drawio.write_text(
        """
        <mxfile>
          <diagram>
            <mxGraphModel pageWidth="200" pageHeight="120">
              <root>
                <mxCell id="0" />
                <mxCell id="1" parent="0" />
                <mxCell id="source" vertex="1" parent="1">
                  <mxGeometry x="0" y="40" width="40" height="20" as="geometry" />
                </mxCell>
                <mxCell id="blocker" vertex="1" parent="1">
                  <mxGeometry x="70" y="30" width="40" height="40" as="geometry" />
                </mxCell>
                <mxCell id="target" vertex="1" parent="1">
                  <mxGeometry x="140" y="40" width="40" height="20" as="geometry" />
                </mxCell>
                <mxCell id="edge" edge="1" source="source" target="target" parent="1"
                        style="edgeStyle=orthogonalEdgeStyle;" >
                  <mxGeometry relative="1" as="geometry">
                    <Array as="points">
                      <mxPoint x="70" y="50" />
                    </Array>
                  </mxGeometry>
                </mxCell>
              </root>
            </mxGraphModel>
          </diagram>
        </mxfile>
        """,
        encoding="utf-8",
    )

    errors, _ = validator.validate_drawio(drawio, "full")

    assert any("cross" in error.lower() for error in errors)


def test_system_architecture_template_has_no_routed_edge_crossings() -> None:
    template = SCRIPT_DIR / "templates" / "drawio" / "system-architecture.drawio"
    root = ET.parse(template).getroot()
    graph_model = root.find("diagram/mxGraphModel")
    assert graph_model is not None
    graph_root = graph_model.find("root")
    assert graph_root is not None

    cells = graph_root.findall("mxCell")
    cell_map = {cell.get("id"): cell for cell in cells if cell.get("id")}

    def absolute_geometry(cell: ET.Element) -> tuple[float, float, float, float]:
        x, y, width, height = routing.geometry_to_rect(cell)
        parent_id = cell.get("parent")
        while parent_id and parent_id not in ("0", "1"):
            parent = cell_map[parent_id]
            parent_x, parent_y, _, _ = routing.geometry_to_rect(parent)
            x += parent_x
            y += parent_y
            parent_id = parent.get("parent")
        return x, y, width, height

    vertices = {
        cell_id: absolute_geometry(cell)
        for cell_id, cell in cell_map.items()
        if cell.get("vertex") == "1" and "swimlane" not in cell.get("style", "")
    }
    obstacles = list(vertices.values())

    for edge in (cell for cell in cells if cell.get("edge") == "1"):
        source_id = edge.get("source")
        target_id = edge.get("target")
        assert source_id in vertices and target_id in vertices
        points = routing.route_edge(
            vertices[source_id],
            vertices[target_id],
            edge.get("style", ""),
            obstacles,
        )
        for start, end in zip(points, points[1:]):
            assert not any(
                vertex_id not in (source_id, target_id)
                and routing.segment_intersects_rect(start, end, obstacle)
                for vertex_id, obstacle in vertices.items()
            ), edge.get("id")


def _template_points(template_name: str) -> list[tuple[str, list[tuple[float, float]], tuple[float, float, float, float], tuple[float, float, float, float]]]:
    """Resolve every edge of a draw.io template exactly like the renderer does."""
    template = SCRIPT_DIR / "templates" / "drawio" / template_name
    root = ET.parse(template).getroot()
    graph_root = root.find("diagram/mxGraphModel/root")
    assert graph_root is not None
    cells = graph_root.findall("mxCell")
    cell_map = {cell.get("id"): cell for cell in cells if cell.get("id")}

    def absolute_geometry(cell: ET.Element) -> tuple[float, float, float, float]:
        x, y, width, height = routing.geometry_to_rect(cell)
        parent_id = cell.get("parent")
        while parent_id and parent_id not in ("0", "1"):
            parent = cell_map[parent_id]
            parent_x, parent_y, _, _ = routing.geometry_to_rect(parent)
            x += parent_x
            y += parent_y
            parent_id = parent.get("parent")
        return x, y, width, height

    vertices = {
        cell_id: absolute_geometry(cell)
        for cell_id, cell in cell_map.items()
        if cell.get("vertex") == "1" and "swimlane" not in cell.get("style", "")
    }
    resolved = []
    for edge in (cell for cell in cells if cell.get("edge") == "1"):
        source_id, target_id = edge.get("source"), edge.get("target")
        assert source_id in vertices and target_id in vertices, edge.get("id")
        style = edge.get("style", "")
        waypoints = routing.get_edge_waypoints(edge)
        if waypoints:
            first, last = routing.edge_endpoints(vertices[source_id], vertices[target_id], style)
            points = routing.snap_edge_points(
                vertices[source_id], vertices[target_id], style, [first, *waypoints, last]
            )
        else:
            points = routing.route_edge(
                vertices[source_id], vertices[target_id], style, list(vertices.values())
            )
        resolved.append((edge.get("id") or "?", points, vertices[source_id], vertices[target_id]))
    return resolved


def _assert_perpendicular_stub(
    edge_id: str, rect: tuple[float, float, float, float], port: tuple[float, float], neighbor: tuple[float, float]
) -> None:
    x, y, width, height = rect
    dx, dy = neighbor[0] - port[0], neighbor[1] - port[1]
    assert abs(dx) >= 0.01 or abs(dy) >= 0.01, f"{edge_id}: zero-length stub at {port}"
    axis = "EW" if abs(dx) >= abs(dy) else "NS"
    lateral = abs(dy) if axis == "EW" else abs(dx)
    assert lateral <= 1.0, f"{edge_id}: stub not perpendicular (lateral {lateral:.1f}px)"
    on_sides = set()
    if abs(port[0] - x) <= 1.0:
        on_sides.add("W")
    if abs(port[0] - (x + width)) <= 1.0:
        on_sides.add("E")
    if abs(port[1] - y) <= 1.0:
        on_sides.add("N")
    if abs(port[1] - (y + height)) <= 1.0:
        on_sides.add("S")
    assert on_sides, f"{edge_id}: port {port} not on icon border"
    assert any(side in axis for side in on_sides), f"{edge_id}: port sides {on_sides} vs travel {axis}"


def test_template_edges_stab_perpendicular_into_icons() -> None:
    """Every connector stub must leave/enter through the approached side.

    Guards the reported defect where wires entered an icon's right side
    arriving from above (side/direction mismatch).
    """
    for template_name in ("system-architecture.drawio", "cloud-infrastructure.drawio"):
        for edge_id, points, source, target in _template_points(template_name):
            assert len(points) >= 2, edge_id
            _assert_perpendicular_stub(edge_id, source, points[0], points[1])
            _assert_perpendicular_stub(edge_id, target, points[-1], points[-2])


def test_explicit_exit_entry_ports_are_respected() -> None:
    style = "edgeStyle=orthogonalEdgeStyle;exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
    points = routing.snap_edge_points((0, 0, 40, 20), (100, 0, 40, 20), style, [(40, 10), (60, 10), (100, 10)])
    assert points[0] == (40, 10)
    assert points[-1] == (100, 10)


def test_cylinder_top_ports_stay_on_visible_curve() -> None:
    """DB icons: top/bottom ports must sit where the cap curve is near-flat.

    The bounding rect's top edge is only tangent at the center; rim ports
    float above the visible ellipse. Clamp to center +/- 0.5*rx.
    """
    rect = (220.0, 317.0, 180.0, 52.0)  # db1 geometry
    port = routing._best_port(rect, (400.0, 243.0), "cylinder")
    assert port[1] == 317.0
    assert 265.0 <= port[0] <= 355.0


def test_cylinder_side_ports_stay_on_body() -> None:
    rect = (500.0, 317.0, 180.0, 52.0)  # cache1 geometry
    port = routing._best_port(rect, (720.0, 317.0), "cylinder")
    assert port[0] == 680.0
    assert 327.0 <= port[1] <= 369.0


def test_diagonal_stubs_get_orthogonal_elbow() -> None:
    points = routing.snap_edge_points(
        (630.0, 185.0, 180.0, 50.0), (220.0, 317.0, 180.0, 52.0),
        "edgeStyle=orthogonalEdgeStyle;",
        [(630.5, 235.0), (630.0, 243.0), (400.0, 243.0), (355.0, 317.0)],
        "rect", "cylinder",
    )
    assert (355.0, 243.0) in points
    for start, end in zip(points, points[1:]):
        dx, dy = end[0] - start[0], end[1] - start[1]
        assert abs(dx) <= 1.0 or abs(dy) <= 1.0
