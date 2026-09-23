"""Targeted branch tests for diagram_routing.py.

Each test drives one line that the shared routing/connector suites never
reach: missing-geometry guards, explicit ports, _first_outside/_trim_inside
fallbacks, _port_sides corner ports, all _elbow_for_stub outcomes,
snap_edge_points' elbow insertion, the unreachable-end fallback in
_grid_route, and _simplify's collinear collapse.
"""
from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


routing = load_module("diagram_routing_edge_cases", "diagram_routing.py")


# --- XML guards --------------------------------------------------------------


def test_geometry_to_rect_without_geometry_is_zero() -> None:
    cell = ET.fromstring('<mxCell id="x"/>')

    assert routing.geometry_to_rect(cell) == (0.0, 0.0, 0.0, 0.0)
    geometry_cell = ET.fromstring(
        '<mxCell id="y"><mxGeometry x="1" y="2" width="3" height="4"/></mxCell>'
    )
    assert routing.geometry_to_rect(geometry_cell) == (1.0, 2.0, 3.0, 4.0)


def test_get_edge_waypoints_without_geometry_is_empty() -> None:
    edge = ET.fromstring('<mxCell id="e" edge="1"/>')

    assert routing.get_edge_waypoints(edge) == []


def test_edge_endpoints_honor_explicit_ports() -> None:
    source = (0.0, 0.0, 100.0, 50.0)
    target = (200.0, 0.0, 100.0, 50.0)

    start, end = routing.edge_endpoints(source, target, "exitX=0.25;exitY=0.5;entryX=0.75;entryY=0.5")

    assert start == (25.0, 25.0)
    assert end == (275.0, 25.0)


# --- _first_outside / _trim_inside -------------------------------------------


def test_first_outside_falls_back_when_every_point_is_inside() -> None:
    rect = (0.0, 0.0, 100.0, 100.0)
    points = [(10.0, 10.0), (20.0, 20.0)]

    assert routing._first_outside(points, rect, forward=True) == (20.0, 20.0)
    assert routing._first_outside(points, rect, forward=False) == (10.0, 10.0)


def test_trim_inside_short_circuit_and_loops() -> None:
    rect = (0.0, 0.0, 100.0, 100.0)

    # Fewer than two points: returned untouched.
    single = [(5.0, 5.0)]
    assert routing._trim_inside(single, rect, forward=True) == single

    # Forward walk: interior leftovers between the ends are dropped.
    forward = [(200.0, 200.0), (10.0, 10.0), (60.0, 60.0), (50.0, 50.0)]
    assert routing._trim_inside(forward, rect, forward=True) == [(200.0, 200.0), (50.0, 50.0)]

    # Backward walk: same cleanup from the tail side.
    backward = [(10.0, 10.0), (60.0, 60.0), (50.0, 50.0), (200.0, 200.0)]
    assert routing._trim_inside(backward, rect, forward=False) == [(10.0, 10.0), (200.0, 200.0)]


# --- _port_sides -------------------------------------------------------------


def test_port_sides_reports_corner_ports() -> None:
    rect = (0.0, 0.0, 100.0, 50.0)

    assert routing._port_sides(rect, (0.0, 50.0)) == {"W", "S"}
    assert routing._port_sides(rect, (100.0, 0.0)) == {"E", "N"}
    assert routing._port_sides(rect, (50.0, 25.0)) == set()


# --- _elbow_for_stub ---------------------------------------------------------


@pytest.mark.parametrize(
    "port, neighbor, expected",
    [
        ((100.0, 25.0), (160.0, 45.0), (160.0, 25.0)),  # E port, dx dominant
        ((50.0, 0.0), (70.0, 40.0), (50.0, 40.0)),      # N port, dy dominant
        ((50.0, 0.0), (90.0, 20.0), (50.0, 20.0)),      # N port, dx dominant -> N/S fallback
        ((100.0, 25.0), (130.0, 60.0), (130.0, 25.0)),  # E port, dy dominant -> E/W fallback
        ((50.0, 25.0), (300.0, 400.0), None),           # interior port: no border side
        ((100.0, 25.0), (160.0, 26.0), None),           # straight stub: |dy| <= 1
        ((100.0, 25.0), (160.0, 25.0), None),           # perfectly horizontal
    ],
)
def test_elbow_for_stub_outcomes(port, neighbor, expected) -> None:
    rect = (0.0, 0.0, 100.0, 50.0)

    assert routing._elbow_for_stub(rect, port, neighbor) == expected


# --- snap_edge_points --------------------------------------------------------


def test_snap_edge_points_short_circuits_for_single_point() -> None:
    points = [(5.0, 5.0)]

    result = routing.snap_edge_points((0.0, 0.0, 40.0, 40.0), (200.0, 0.0, 40.0, 40.0), "", points)

    assert result == points
    assert result is not points  # defensive copy


def test_snap_edge_points_inserts_orthogonal_elbow_at_source() -> None:
    source = (0.0, 0.0, 60.0, 40.0)
    target = (300.0, 0.0, 60.0, 40.0)
    points = [(30.0, -30.0), (150.0, 80.0), (330.0, -30.0)]

    result = routing.snap_edge_points(source, target, "", points)

    # Source port snaps to (60, 36); the diagonal stub gets an elbow so the
    # icon-side segment stabs straight into the border.
    assert result[0] == (60.0, 36.0)
    assert result[1] == (150.0, 36.0)
    assert result[-1] == (300.0, 36.0)


# --- _grid_route / _simplify -------------------------------------------------


def test_grid_route_returns_direct_jump_when_end_is_unreachable() -> None:
    """An obstacle covering the target port removes `end` from the usable grid."""
    start = (60.0, 20.0)
    end = (300.0, 20.0)
    obstacles = [(290.0, -20.0, 100.0, 100.0)]  # covers the target's west port

    route = routing._grid_route(start, end, obstacles)

    assert route == [start, end]


def test_grid_route_skips_stale_heap_entries() -> None:
    """A node relaxed after being pushed leaves a stale heap entry that must be
    skipped instead of re-expanded; this config triggers exactly that pop."""
    start = (474.0, 76.0)
    end = (93.0, 93.0)
    obstacles = [
        (119.0, 3.0, 63.0, 104.0),
        (35.0, 42.0, 65.0, 75.0),
        (242.0, 8.0, 47.0, 32.0),
        (354.0, 319.0, 163.0, 108.0),
    ]

    route = routing._grid_route(start, end, obstacles)

    assert route == [start, end]


def test_simplify_collapses_collinear_points() -> None:
    assert routing._simplify([(0, 0), (0, 0), (0, 5), (0, 10)]) == [(0, 0), (0, 10)]
    assert routing._simplify([(0, 0), (5, 5)]) == [(0, 0), (5, 5)]


def test_route_edge_around_obstacle_stays_on_grid() -> None:
    source = (0.0, 0.0, 60.0, 40.0)
    target = (300.0, 0.0, 60.0, 40.0)
    obstacle = (120.0, -30.0, 60.0, 120.0)  # wall between the two nodes

    route = routing.route_edge(source, target, "", [source, target, obstacle])

    assert len(route) >= 2
    # No route segment cuts through the wall interior.
    for start, end in zip(route, route[1:]):
        assert not routing.segment_intersects_rect(start, end, (112.0, -38.0, 76.0, 136.0))
