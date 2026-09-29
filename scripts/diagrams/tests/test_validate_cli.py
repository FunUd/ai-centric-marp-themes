"""Tests for validate-slide-diagram.py — main() CLI flow plus the
validate_svg / validate_drawio branches that previous tests never reach
(parse errors, root-element checks, dimension fallbacks, draw.io cell
structure, waypoint edges, main()'s exit-code contract).
"""

from __future__ import annotations

import importlib.util
import sys
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


load_module("diagram_routing", "diagram_routing.py")
validator = load_module("validate_slide_diagram_cli", "validate-slide-diagram.py")


def _main(monkeypatch, *args: str):
    monkeypatch.setattr(sys, "argv", ["validate-slide-diagram.py", *args])
    return validator.main()


def _svg(tmp_path: Path, body: str = "", viewBox: str = "0 0 900 400", name: str = "d.svg") -> Path:
    path = tmp_path / name
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}">{body}</svg>',
        encoding="utf-8",
    )
    return path


def _drawio(tmp_path: Path, xml: str, name: str = "d.drawio") -> Path:
    path = tmp_path / name
    path.write_text(xml, encoding="utf-8")
    return path


# --- _parse_dimension & geometry helpers -------------------------------------


class _NoReconfigureStream:
    """stdout/stderr stand-in without reconfigure() (AttributeError branch)."""

    def __init__(self) -> None:
        self.buffer: list[str] = []

    def write(self, text: str) -> int:
        self.buffer.append(text)
        return len(text)

    def flush(self) -> None:
        pass


def test_main_tolerates_streams_without_reconfigure(monkeypatch) -> None:
    out, err = _NoReconfigureStream(), _NoReconfigureStream()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    monkeypatch.setattr(sys, "argv", ["validate-slide-diagram.py"])  # path required

    with pytest.raises(SystemExit) as exc:
        validator.main()

    assert exc.value.code == 2
    assert any("usage:" in chunk for chunk in err.buffer)


def test_script_entry_point_help_exits_zero(monkeypatch) -> None:
    import runpy

    monkeypatch.setattr(sys, "argv", [validator.__file__, "--help"])

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(validator.__file__, run_name="__main__")

    assert exc.value.code == 0


def test_parse_dimension_variants() -> None:
    assert validator._parse_dimension(None) is None
    assert validator._parse_dimension("") is None
    assert validator._parse_dimension("50%") is None
    assert validator._parse_dimension("abc") is None  # ValueError branch
    assert validator._parse_dimension(" 12.5px") == 12.5
    assert validator._parse_dimension("10pt") == 10.0
    assert validator._parse_dimension("42") == 42.0


def test_svg_element_rect_for_primitives(tmp_path: Path) -> None:
    # Elements parsed from a namespaced document need the {*} wildcard
    # (Element.iter() does not support patterns; findall() does).
    circle = validator.ET.parse(_svg(tmp_path, '<circle cx="10" cy="10" r="5"/>')).getroot().findall(".//{*}circle")[0]
    ellipse = validator.ET.fromstring('<ellipse cx="20" cy="10" rx="8" ry="4"/>')
    polygon = validator.ET.fromstring('<polygon points="10,10 50,10 50,50 10,50"/>')
    bad = validator.ET.fromstring('<circle r="big"/>')
    other = validator.ET.fromstring("<g/>")

    assert validator._svg_element_rect(circle) == (5, 5, 10, 10)
    assert validator._svg_element_rect(ellipse) == (12, 6, 16, 8)
    assert validator._svg_element_rect(polygon) == (10, 10, 40, 40)
    assert validator._svg_element_rect(bad) is None
    assert validator._svg_element_rect(other) is None


def test_svg_segments_for_line_path_and_others() -> None:
    line = validator.ET.fromstring('<line x1="0" y1="30" x2="100" y2="30"/>')
    broken_line = validator.ET.fromstring('<line x1="abc" y1="0" x2="1" y2="1"/>')
    path = validator.ET.fromstring('<path d="M 0 0 L 10 10 L 20 10"/>')
    rect = validator.ET.fromstring("<rect/>")

    assert validator._svg_segments(line) == [((0.0, 30.0), (100.0, 30.0))]
    assert validator._svg_segments(broken_line) == []
    assert validator._svg_segments(path) == [((0.0, 0.0), (10.0, 10.0)), ((10.0, 10.0), (20.0, 10.0))]
    assert validator._svg_segments(rect) == []


# --- validate_svg branches ---------------------------------------------------


def test_validate_svg_parse_error(tmp_path: Path) -> None:
    broken = tmp_path / "broken.svg"
    broken.write_text("<svg", encoding="utf-8")

    errors, warnings = validator.validate_svg(broken, "full")

    assert errors and errors[0].startswith("SVG XML parse error")
    assert warnings == []


def test_validate_svg_rejects_non_svg_root(tmp_path: Path) -> None:
    page = tmp_path / "page.svg"
    page.write_text("<html><body/></html>", encoding="utf-8")

    errors, _ = validator.validate_svg(page, "full")

    assert errors and "Root element must be <svg>" in errors[0]


def test_validate_svg_falls_back_to_width_height_attributes(tmp_path: Path) -> None:
    path = tmp_path / "dims.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200"></svg>',
        encoding="utf-8",
    )

    errors, warnings = validator.validate_svg(path, "full")

    # No viewBox -> width/height attrs are used; aspect 4.0 is within full limits.
    assert errors == []
    assert warnings == []


def test_validate_svg_warns_when_dimensions_undeterminable(tmp_path: Path) -> None:
    path = tmp_path / "empty.svg"
    path.write_text("<svg></svg>", encoding="utf-8")

    errors, warnings = validator.validate_svg(path, "full")

    assert errors == []
    assert any("Could not determine positive width/height" in w for w in warnings)


def test_validate_svg_rejects_oversized_height(tmp_path: Path) -> None:
    path = _svg(tmp_path, viewBox="0 0 1000 600")

    errors, _ = validator.validate_svg(path, "full")

    assert any("exceeds max allowed height" in e for e in errors)


def test_validate_svg_rejects_oversized_width(tmp_path: Path) -> None:
    path = _svg(tmp_path, viewBox="0 0 2000 400")

    errors, _ = validator.validate_svg(path, "full")

    assert any("exceeds max allowed width" in e for e in errors)


def test_validate_svg_ellipse_out_of_viewbox_is_rejected(tmp_path: Path) -> None:
    path = _svg(tmp_path, '<ellipse data-diagram-role="node" cx="95" cy="50" rx="20" ry="10"/>', viewBox="0 0 100 100")

    errors, _ = validator.validate_svg(path, "col2")

    assert any("outside" in e for e in errors)


def test_validate_svg_polygon_and_circle_bounds_are_checked(tmp_path: Path) -> None:
    path = _svg(
        tmp_path,
        '<circle data-diagram-role="node" cx="20" cy="20" r="10"/>'
        '<polygon data-diagram-role="node" points="50,50 80,50 80,80 50,80"/>'
        '<polygon data-diagram-role="node" points="90,90 broken"/>',
        viewBox="0 0 100 100",
    )

    errors, _ = validator.validate_svg(path, "col2")

    # In-bounds shapes pass; the malformed polygon is skipped (ValueError -> None).
    assert errors == []


def test_validate_svg_connector_touching_node_is_allowed(tmp_path: Path) -> None:
    path = _svg(
        tmp_path,
        '<rect data-diagram-role="node" x="40" y="20" width="20" height="20"/>'
        '<path data-diagram-role="connector" d="M 50 30 L 120 30"/>',
        viewBox="0 0 200 100",
    )

    errors, _ = validator.validate_svg(path, "col2")

    # Endpoint inside the node -> `continue`, no false crossing error.
    assert errors == []


def test_validate_svg_mixed_connector_shapes(tmp_path: Path) -> None:
    path = _svg(
        tmp_path,
        '<line data-diagram-role="connector" x1="10" y1="80" x2="90" y2="80"/>'
        '<line data-diagram-role="connector" x1="abc" y1="0" x2="1" y2="1"/>'
        '<rect data-diagram-role="connector" x="1" y="1" width="5" height="5"/>',
        viewBox="0 0 100 100",
    )

    errors, _ = validator.validate_svg(path, "col2")

    # Valid line parses, broken line and rect produce no segments, no crossings.
    assert errors == []


def test_validate_svg_warns_on_long_unbroken_text(tmp_path: Path) -> None:
    path = _svg(tmp_path, '<text data-diagram-role="label">ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789</text>')

    _, warnings = validator.validate_svg(path, "full")

    assert any("Long unbroken text" in w for w in warnings)


# --- validate_drawio branches ------------------------------------------------


def test_validate_drawio_parse_error(tmp_path: Path) -> None:
    broken = _drawio(tmp_path, "<mxfile", name="broken.drawio")

    errors, _ = validator.validate_drawio(broken, "full")

    assert errors and errors[0].startswith("draw.io XML parse error")


def test_validate_drawio_walks_unknown_parent_refs(tmp_path: Path) -> None:
    # Vertex and edge parented to an id missing from the cell map: both
    # absolute-position walks hit their break guards and fall back to local
    # geometry instead of raising.
    path = _drawio(
        tmp_path,
        "<mxfile><diagram><mxGraphModel><root>"
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        '<mxCell id="v1" vertex="1" parent="ghost" style="rounded=0;">'
        '<mxGeometry x="10" y="10" width="80" height="40"/></mxCell>'
        '<mxCell id="v2" vertex="1" parent="1" style="rounded=0;">'
        '<mxGeometry x="300" y="10" width="80" height="40"/></mxCell>'
        '<mxCell id="e1" edge="1" parent="ghost" source="v1" target="v2" '
        'style="edgeStyle=orthogonalEdgeStyle;">'
        '<mxGeometry relative="1"><Array as="points">'
        '<mxPoint x="150" y="80"/></Array></mxGeometry></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>",
        name="ghost.drawio",
    )

    errors, warnings = validator.validate_drawio(path, "full")

    assert isinstance(errors, list) and isinstance(warnings, list)


def test_validate_drawio_rejects_non_mxfile_root(tmp_path: Path) -> None:
    path = _drawio(tmp_path, "<other/>", name="wrong.drawio")

    errors, _ = validator.validate_drawio(path, "full")

    assert errors and "Root element must be <mxfile>" in errors[0]


def test_validate_drawio_requires_diagram_element(tmp_path: Path) -> None:
    path = _drawio(tmp_path, "<mxfile/>", name="nodiag.drawio")

    errors, _ = validator.validate_drawio(path, "full")

    assert errors == ["No <diagram> element found inside <mxfile>"]


def test_validate_drawio_skips_diagram_without_graph_model(tmp_path: Path) -> None:
    path = _drawio(tmp_path, '<mxfile><diagram name="x"/></mxfile>', name="nogmodel.drawio")

    errors, warnings = validator.validate_drawio(path, "full")

    assert errors == [] and warnings == []


def test_validate_drawio_requires_root_element(tmp_path: Path) -> None:
    path = _drawio(tmp_path, "<mxfile><diagram><mxGraphModel/></diagram></mxfile>", name="noroot.drawio")

    errors, _ = validator.validate_drawio(path, "full")

    assert any("Missing <root>" in e for e in errors)


def test_validate_drawio_cell_structure_and_bounds(tmp_path: Path) -> None:
    path = _drawio(
        tmp_path,
        "<mxfile><diagram><mxGraphModel><root>"
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        # exceeds canvas width (1000+200 > 1140)
        '<mxCell id="wide" vertex="1" parent="1">'
        '<mxGeometry x="1000" y="10" width="200" height="50"/></mxCell>'
        # exceeds canvas height (430+60 > 470)
        '<mxCell id="tall" vertex="1" parent="1">'
        '<mxGeometry x="10" y="430" width="50" height="60"/></mxCell>'
        # no geometry -> (0,0,0,0)
        '<mxCell id="nogeom" vertex="1" parent="1"/>'
        # nested parent chain -> absolute offset walk
        '<mxCell id="outer" vertex="1" parent="1">'
        '<mxGeometry x="100" y="100" width="80" height="40"/></mxCell>'
        '<mxCell id="child" vertex="1" parent="outer">'
        '<mxGeometry x="5" y="5" width="20" height="20"/></mxCell>'
        # missing id
        '<mxCell vertex="1" parent="1"><mxGeometry x="1" y="1" width="5" height="5"/></mxCell>'
        # duplicate id
        '<mxCell id="dup" vertex="1" parent="1">'
        '<mxGeometry x="1" y="1" width="5" height="5"/></mxCell>'
        '<mxCell id="dup" vertex="1" parent="1">'
        '<mxGeometry x="1" y="1" width="5" height="5"/></mxCell>'
        # edge with waypoints inside a non-root parent -> origin walk
        '<mxCell id="e-way" edge="1" parent="outer" source="outer" target="child" '
        'style="strokeColor=#000000;">'
        '<mxGeometry relative="1"><Array as="points">'
        '<mxPoint x="150" y="60"/></Array></mxGeometry></mxCell>'
        # edge whose source is not a vertex -> skipped
        '<mxCell id="e-ghost" edge="1" parent="1" source="ghost" target="outer" '
        'style="strokeColor=#000000;"><mxGeometry relative="1"/></mxCell>'
        # plain edge without waypoints -> grid route
        '<mxCell id="e-simple" edge="1" parent="1" source="wide" target="tall" '
        'style="strokeColor=#000000;"><mxGeometry relative="1"/></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>",
        name="cells.drawio",
    )

    errors, _ = validator.validate_drawio(path, "full")

    text = "\n".join(errors)
    assert "bounds (1200px) exceed canvas width (1140px)" in text
    assert "bounds (490px) exceed canvas height (470px)" in text
    assert "Found <mxCell> without 'id'" in text
    assert "Duplicate cell id='dup'" in text


def test_validate_drawio_requires_root_cells(tmp_path: Path) -> None:
    path = _drawio(
        tmp_path,
        "<mxfile><diagram><mxGraphModel><root>"
        '<mxCell id="n" vertex="1" parent="1">'
        '<mxGeometry x="10" y="10" width="50" height="50"/></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>",
        name="norootcells.drawio",
    )

    errors, _ = validator.validate_drawio(path, "full")

    assert any("Missing required root cells" in e for e in errors)


def test_validate_drawio_passes_for_clean_template() -> None:
    template = SCRIPT_DIR / "templates" / "drawio" / "system-architecture.drawio"

    errors, warnings = validator.validate_drawio(template, "full")

    assert errors == []
    assert warnings == []


# --- main() ------------------------------------------------------------------


def test_main_exits_when_file_missing(monkeypatch, tmp_path: Path, capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, str(tmp_path / "missing.svg"))

    assert exc.value.code == 1
    assert "File not found" in capsys.readouterr().err


def test_main_rejects_unsupported_extension(monkeypatch, tmp_path: Path, capsys) -> None:
    path = tmp_path / "d.txt"
    path.write_text("hello", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, str(path))

    assert exc.value.code == 1
    assert "Unsupported file extension '.txt'" in capsys.readouterr().err


def test_main_passes_clean_svg(monkeypatch, tmp_path: Path, capsys) -> None:
    path = _svg(tmp_path)

    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, str(path))

    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert "PASSED" in captured.out


def test_main_fails_oversized_svg(monkeypatch, tmp_path: Path, capsys) -> None:
    path = _svg(tmp_path, viewBox="0 0 1000 600")

    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, str(path), "--layout", "full")

    captured = capsys.readouterr()
    assert exc.value.code == 1
    assert "[ERROR]" in captured.out
    assert "FAILED" in captured.out


def test_main_warning_passes_unless_strict(monkeypatch, tmp_path: Path, capsys) -> None:
    path = _svg(tmp_path, '<text data-diagram-role="label">ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789</text>')

    with pytest.raises(SystemExit) as non_strict:
        _main(monkeypatch, str(path))
    assert non_strict.value.code == 0
    assert "[WARN]" in capsys.readouterr().out

    with pytest.raises(SystemExit) as strict:
        _main(monkeypatch, str(path), "--strict")
    assert strict.value.code == 1
    assert "FAILED" in capsys.readouterr().out


def test_main_accepts_drawio_and_xml_extensions(monkeypatch, tmp_path: Path, capsys) -> None:
    drawio = _drawio(
        tmp_path,
        "<mxfile><diagram><mxGraphModel><root>"
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        '<mxCell id="n1" vertex="1" parent="1"><mxGeometry x="10" y="10" width="100" height="60"/></mxCell>'
        '<mxCell id="n2" vertex="1" parent="1"><mxGeometry x="300" y="10" width="100" height="60"/></mxCell>'
        '<mxCell id="e" edge="1" parent="1" source="n1" target="n2">'
        '<mxGeometry relative="1"/></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>",
        name="clean.drawio",
    )
    as_xml = tmp_path / "clean.xml"
    as_xml.write_text(drawio.read_text(encoding="utf-8"), encoding="utf-8")

    for target in (drawio, as_xml):
        with pytest.raises(SystemExit) as exc:
            _main(monkeypatch, str(target), "--layout", "col2")
        assert exc.value.code == 0, capsys.readouterr().out
    assert "PASSED" in capsys.readouterr().out
