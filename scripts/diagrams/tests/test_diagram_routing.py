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
