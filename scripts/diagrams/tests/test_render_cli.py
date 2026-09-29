"""Tests for render-slide-diagram.py — main() flow and engine wrappers.

Covers:
- main() argument/error branches (missing input, unknown format, aspect
  parse failure, render failure, validator failure propagation)
- render_mermaid with a mocked mermaid-cli (success/failure/postprocess)
- render_drawio failure paths and _convert_drawio_to_svg edge cases
- aspect helpers (_resolve_aspect, _pad_output_aspect) and advisory notes

subprocess.run is always mocked: no npx / Mermaid CLI in tests.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

TEMPLATE_DRAWIO = SCRIPT_DIR / "templates" / "drawio" / "system-architecture.drawio"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_module("diagram_routing", "diagram_routing.py")
load_module("design_tokens", "design_tokens.py")
load_module("diagram_models", "diagram_models.py")
load_module("svg_aspect", "svg_aspect.py")
load_module("svg_filters", "svg_filters.py")
load_module("svg_diagram_renderer", "svg_diagram_renderer.py")
load_module("svg_theme_postprocessor", "svg_theme_postprocessor.py")
render = load_module("render_slide_diagram_cli", "render-slide-diagram.py")

AZURE = render.load_theme_style("azure-clarity")


def _main(monkeypatch, *args: str):
    monkeypatch.setattr(sys, "argv", ["render-slide-diagram.py", *args])
    return render.main()


def _write_json(tmp_path: Path, data: dict, name: str = "diagram.json") -> Path:
    source = tmp_path / name
    source.write_text(json.dumps(data), encoding="utf-8")
    return source


def _install_fake_mermaid(monkeypatch, svg_text: str, returncode: int = 0):
    """Fake mermaid-cli: capture the CLI invocation and write the output SVG."""
    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        if returncode == 0:
            dest = Path(cmd[cmd.index("-o") + 1])
            dest.write_text(svg_text, encoding="utf-8")
        return subprocess.CompletedProcess(cmd, returncode, "", "cli failed")

    monkeypatch.setattr(render.subprocess, "run", fake_run)
    return calls


# --- main(): argument & error branches ---------------------------------------


def test_main_exits_when_input_missing(monkeypatch, tmp_path: Path, capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, "-i", str(tmp_path / "nope.mmd"), "-o", str(tmp_path / "o.svg"), "--no-validate")

    assert exc.value.code == 1
    assert "Input file not found" in capsys.readouterr().err


def test_main_rejects_unknown_input_format(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "diagram.txt"
    source.write_text("not a diagram", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, "-i", str(source), "-o", str(tmp_path / "o.svg"), "--no-validate")

    assert exc.value.code == 1
    assert "Unknown input format '.txt'" in capsys.readouterr().err


def test_main_requires_input_or_code(monkeypatch, tmp_path: Path, capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, "-o", str(tmp_path / "o.svg"))

    assert exc.value.code == 1
    assert "Either --input or --code must be specified" in capsys.readouterr().err


def test_main_rejects_invalid_aspect(monkeypatch, tmp_path: Path, capsys) -> None:
    source = _write_json(tmp_path, {"type": "pie", "items": [{"label": "A", "value": 1}]})

    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, "-i", str(source), "-o", str(tmp_path / "o.svg"), "--aspect", "wide")

    assert exc.value.code == 1
    assert "[ERROR]" in capsys.readouterr().err


def test_main_reports_render_failure(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(render, "render_mermaid", lambda *a, **k: False)

    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, "--code", "flowchart LR; A-->B", "-o", str(tmp_path / "o.svg"), "--no-validate")

    assert exc.value.code == 1
    assert "[ERROR] Rendering failed" in capsys.readouterr().err


def test_main_renders_code_snippet(monkeypatch, tmp_path: Path, capsys) -> None:
    output = tmp_path / "o.svg"

    def fake_render(code, out, theme_data, layout, postprocess=True):
        out.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>", encoding="utf-8")
        return True

    monkeypatch.setattr(render, "render_mermaid", fake_render)

    result = _main(monkeypatch, "--code", "flowchart LR; A-->B", "-o", str(output), "--no-validate")

    assert result is None  # no SystemExit == success
    assert output.exists()
    assert "[SUCCESS]" in capsys.readouterr().out


def test_main_mmd_aspect_directive_pads_canvas(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "d.mmd"
    source.write_text("%% aspect: 2.4\nflowchart LR; A-->B\n", encoding="utf-8")
    output = tmp_path / "d.svg"
    _install_fake_mermaid(
        monkeypatch,
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 400" width="1000" height="400"></svg>',
    )

    _main(monkeypatch, "-i", str(source), "-o", str(output), "--no-validate")

    out = capsys.readouterr().out
    padded = output.read_text(encoding="utf-8")
    assert "[SUCCESS]" in out
    assert "Padded canvas to aspect 2.4" in out
    # 1000x400 (2.5) padded down to 2.4 -> height 416.67
    assert re.search(r'viewBox="0 -?\d+(?:\.\d+)? 1000 416\.6', padded)


def test_main_invalid_mermaid_aspect_directive_exits(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "d.mmd"
    source.write_text("%% aspect: wide\nflowchart LR\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, "-i", str(source), "-o", str(tmp_path / "o.svg"), "--no-validate")

    assert exc.value.code == 1
    assert "[ERROR]" in capsys.readouterr().err


def test_main_renders_drawio_input(monkeypatch, tmp_path: Path, capsys) -> None:
    output = tmp_path / "arch.svg"

    _main(monkeypatch, "-i", str(TEMPLATE_DRAWIO), "-o", str(output), "--no-validate")

    out = capsys.readouterr().out
    assert "[SUCCESS]" in out
    assert output.exists()
    assert output.read_text(encoding="utf-8").lstrip().startswith("<svg")


def test_main_json_aspect_override_reflows_height(monkeypatch, tmp_path: Path, capsys) -> None:
    source = _write_json(tmp_path, {"type": "pie", "height": 600, "items": [{"label": "A", "value": 1}]})
    output = tmp_path / "pie.svg"

    _main(monkeypatch, "-i", str(source), "-o", str(output), "--aspect", "2.4", "--no-validate")

    assert "[SUCCESS]" in capsys.readouterr().out
    viewbox = re.search(r'viewBox="([^"]+)"', output.read_text(encoding="utf-8")).group(1)
    assert viewbox.split() == ["0", "0", "1080", "450"]


def test_main_validator_failure_propagates(monkeypatch, tmp_path: Path, capsys) -> None:
    source = _write_json(tmp_path, {"type": "pie", "aspect": 2.4, "items": [{"label": "A", "value": 1}]})
    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 1, "", "")

    monkeypatch.setattr(render.subprocess, "run", fake_run)

    with pytest.raises(SystemExit) as exc:
        _main(monkeypatch, "-i", str(source), "-o", str(tmp_path / "o.svg"))

    captured = capsys.readouterr()
    assert exc.value.code == 1
    assert "failed layout validation" in captured.err
    assert "[SUCCESS]" not in captured.out
    assert str(render.VALIDATOR_PATH) in calls[0][1]
    assert "--layout" in calls[0]


def test_main_validator_success_prints_success(monkeypatch, tmp_path: Path, capsys) -> None:
    source = _write_json(tmp_path, {"type": "pie", "aspect": 2.4, "items": [{"label": "A", "value": 1}]})

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(render.subprocess, "run", fake_run)

    _main(monkeypatch, "-i", str(source), "-o", str(tmp_path / "o.svg"))

    out = capsys.readouterr().out
    assert "Running automated layout validation..." in out
    assert "[SUCCESS]" in out


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
    monkeypatch.setattr(sys, "argv", ["render-slide-diagram.py"])  # -o required

    with pytest.raises(SystemExit) as exc:
        render.main()

    # Reconfigure is skipped; argparse still reports the missing -o.
    assert exc.value.code == 2
    assert any("usage:" in chunk for chunk in err.buffer)


def test_script_entry_point_help_exits_zero(monkeypatch) -> None:
    import runpy

    monkeypatch.setattr(sys, "argv", [render.__file__, "--help"])

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(render.__file__, run_name="__main__")

    assert exc.value.code == 0


# --- render_mermaid ----------------------------------------------------------


def test_render_mermaid_success_postprocesses_output(monkeypatch, tmp_path: Path, capsys) -> None:
    output = tmp_path / "m.svg"
    calls: list[list[str]] = []
    configs: list[dict] = []

    # The config lives in a TemporaryDirectory, so read it during the run.
    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        configs.append(json.loads(Path(cmd[cmd.index("-c") + 1]).read_text(encoding="utf-8")))
        Path(cmd[cmd.index("-o") + 1]).write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><g font-family="Arial"></g></svg>',
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(render.subprocess, "run", fake_run)

    ok = render.render_mermaid("flowchart LR; A-->B", output, AZURE, "full")

    assert ok is True
    cmd = calls[0]
    # argv list, pinned to an exact version, no shell.
    assert isinstance(cmd, list) and all(isinstance(part, str) for part in cmd)
    import os

    assert os.path.basename(cmd[0]).lower().startswith("npx"), cmd
    spec = next(part for part in cmd if part.startswith("@mermaid-js/mermaid-cli"))
    assert spec.count("@") == 2, f"unpinned mermaid spec: {spec}"
    version = spec.rsplit("@", 1)[1]
    assert version[0].isdigit() and not version.startswith(("^", "~")), spec
    # The mermaid config written for the CLI carries the theme tokens.
    assert configs[0] == AZURE.get("mermaid", {})
    written = output.read_text(encoding="utf-8")
    assert "Arial" not in written  # font-family replaced by postprocess
    assert AZURE["fontFamily"].replace('"', "'") in written
    assert "Rendering Mermaid diagram" in capsys.readouterr().out


def test_render_mermaid_cli_failure_returns_false(monkeypatch, tmp_path: Path, capsys) -> None:
    output = tmp_path / "never.svg"
    _install_fake_mermaid(monkeypatch, "", returncode=1)

    ok = render.render_mermaid("flowchart LR", output, AZURE, "full")

    assert ok is False
    assert "Mermaid CLI failed" in capsys.readouterr().err
    assert not output.exists()


def test_render_mermaid_without_postprocess_keeps_raw_svg(monkeypatch, tmp_path: Path) -> None:
    raw = '<svg xmlns="http://www.w3.org/2000/svg"><g font-family="Arial"></g></svg>'
    output = tmp_path / "m.svg"
    _install_fake_mermaid(monkeypatch, raw)

    ok = render.render_mermaid("flowchart LR", output, AZURE, "full", postprocess=False)

    assert ok is True
    assert output.read_text(encoding="utf-8") == raw


# --- render_drawio & converter -----------------------------------------------


def test_render_drawio_parse_error_returns_false(tmp_path: Path, capsys) -> None:
    broken = tmp_path / "broken.drawio"
    broken.write_text("<mxfile><diagram>", encoding="utf-8")

    ok = render.render_drawio(broken, tmp_path / "o.svg", AZURE, "full")

    assert ok is False
    assert "Failed to parse draw.io XML" in capsys.readouterr().err


def test_render_drawio_without_model_returns_false(tmp_path: Path, capsys) -> None:
    empty = tmp_path / "empty.drawio"
    # mxGraphModel without a <root> element -> converter returns "".
    empty.write_text(
        "<mxfile><diagram><mxGraphModel/></diagram></mxfile>",
        encoding="utf-8",
    )

    ok = render.render_drawio(empty, tmp_path / "o.svg", AZURE, "full")

    assert ok is False
    assert "Failed to convert draw.io model to SVG" in capsys.readouterr().err


def _convert(xml: str) -> str:
    return render._convert_drawio_to_svg(ET.ElementTree(ET.fromstring(xml)), AZURE)


def test_convert_requires_diagram_element() -> None:
    assert _convert("<mxfile/>") == ""


def test_convert_requires_graph_model() -> None:
    assert _convert('<mxfile><diagram name="x"/></mxfile>') == ""


def test_convert_requires_root_element() -> None:
    assert _convert("<mxfile><diagram><mxGraphModel/></diagram></mxfile>") == ""


def test_convert_tolerates_missing_geometry_and_dangling_parent() -> None:
    svg = _convert(
        "<mxfile><diagram><mxGraphModel><root>"
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        # no <mxGeometry> -> (0, 0, 0, 0)
        '<mxCell id="g" vertex="1" parent="1" style="rounded=0;fillColor=#FFFFFF;"/>'
        # parent not in the cell map -> break out of the offset walk
        '<mxCell id="h" vertex="1" parent="999" style="rounded=0;fillColor=#FFFFFF;">'
        '<mxGeometry x="10" y="10" width="50" height="30"/></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>"
    )

    assert "x='0' y='0' width='0' height='0'" in svg
    assert "x='10.0' y='10.0'" in svg


def test_convert_renders_edge_with_waypoints() -> None:
    svg = _convert(
        '<mxfile><diagram><mxGraphModel pageWidth="800" pageHeight="400"><root>'
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        '<mxCell id="5" value="Lane" vertex="1" parent="1" '
        'style="swimlane;fillColor=#FFFFFF;strokeColor=#000000;fontColor=#000000;">'
        '<mxGeometry x="20" y="20" width="400" height="200"/></mxCell>'
        '<mxCell id="a" vertex="1" parent="1" style="rounded=0;fillColor=#FFFFFF;'
        'strokeColor=#000000;fontColor=#000000;fontSize=11">'
        '<mxGeometry x="40" y="60" width="80" height="40"/></mxCell>'
        '<mxCell id="b" vertex="1" parent="1" style="rounded=0;fillColor=#FFFFFF;'
        'strokeColor=#000000;fontColor=#000000;fontSize=11">'
        '<mxGeometry x="300" y="60" width="80" height="40"/></mxCell>'
        '<mxCell id="e1" edge="1" parent="5" source="a" target="b" '
        'style="edgeStyle=orthogonalEdgeStyle;strokeColor=#000000;">'
        '<mxGeometry relative="1"><Array as="points">'
        '<mxPoint x="120" y="140"/><mxPoint x="240" y="140"/></Array></mxGeometry></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>"
    )

    assert "fill='none'" in svg  # edge path rendered
    assert "<polygon points=" in svg  # arrowhead rendered
    assert "Lane" in svg  # swimlane chrome/title rendered


def test_convert_waypoint_edge_with_unknown_parent_breaks_origin_walk() -> None:
    # parent="ghost" is not in the cell map: the origin walk terminates
    # immediately and waypoints keep their raw coordinates.
    svg = _convert(
        '<mxfile><diagram><mxGraphModel pageWidth="800" pageHeight="400"><root>'
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        '<mxCell id="a" vertex="1" parent="1" style="rounded=0;fillColor=#FFFFFF;">'
        '<mxGeometry x="40" y="60" width="80" height="40"/></mxCell>'
        '<mxCell id="b" vertex="1" parent="1" style="rounded=0;fillColor=#FFFFFF;">'
        '<mxGeometry x="300" y="60" width="80" height="40"/></mxCell>'
        '<mxCell id="e1" edge="1" parent="ghost" source="a" target="b" '
        'style="edgeStyle=orthogonalEdgeStyle;">'
        '<mxGeometry relative="1"><Array as="points">'
        '<mxPoint x="120" y="140"/></Array></mxGeometry></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>"
    )

    assert "fill='none'" in svg


def test_convert_skips_edge_without_endpoints() -> None:
    svg = _convert(
        "<mxfile><diagram><mxGraphModel><root>"
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        '<mxCell id="e" edge="1" parent="1" style="strokeColor=#000000;">'
        '<mxGeometry relative="1"/></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>"
    )

    assert "<path " not in svg


# --- JSON helpers ------------------------------------------------------------


def test_advisory_note_for_funnel_value_pills_on_col3() -> None:
    with_values = {"type": "funnel", "levels": [{"label": "A", "value": 10}]}
    without_values = {"type": "funnel", "levels": [{"label": "A"}]}
    pie = {"type": "pie", "items": [{"label": "A", "value": 1}]}

    assert render._advisory_note(with_values, "col3")
    assert render._advisory_note(without_values, "col3") == ""
    assert render._advisory_note(with_values, "full") == ""
    assert render._advisory_note(pie, "col3") == ""


def test_json_from_data_reports_validation_failure(capsys) -> None:
    ok = render.render_json_diagram_from_data({"type": "pie", "items": []}, Path("/nonexistent/out.svg"), AZURE, "full")

    assert ok is False
    assert "JSON diagram validation failed" in capsys.readouterr().err


def test_json_from_data_prints_advisory_note(tmp_path: Path, capsys) -> None:
    output = tmp_path / "funnel.svg"
    data = {
        "type": "funnel",
        "layout": "col3",
        "aspect": 1.0,
        "levels": [
            {"label": "Top", "value": 100},
            {"label": "Mid", "value": 50},
            {"label": "End", "value": 10},
        ],
    }

    ok = render.render_json_diagram_from_data(data, output, AZURE, "col3")

    out = capsys.readouterr().out
    assert ok is True
    assert output.exists()
    assert "[NOTE]" in out


def test_json_parse_error_reports_line(tmp_path: Path, capsys) -> None:
    broken = tmp_path / "bad.json"
    broken.write_text("{ not json", encoding="utf-8")

    ok = render.render_json_diagram(broken, tmp_path / "o.svg", AZURE, "full")

    assert ok is False
    assert "JSON parse error" in capsys.readouterr().err


def test_json_read_error_is_reported(tmp_path: Path, capsys) -> None:
    ok = render.render_json_diagram(tmp_path / "missing.json", tmp_path / "o.svg", AZURE, "full")

    assert ok is False
    assert "Failed to read JSON file" in capsys.readouterr().err


def test_json_aspect_overrides_source_height(tmp_path: Path) -> None:
    source = _write_json(tmp_path, {"type": "pie", "height": 600, "items": [{"label": "A", "value": 1}]})
    output = tmp_path / "o.svg"

    ok = render.render_json_diagram(source, output, AZURE, "full", aspect=2.4)

    assert ok is True
    viewbox = re.search(r'viewBox="([^"]+)"', output.read_text(encoding="utf-8")).group(1)
    assert viewbox.split() == ["0", "0", "1080", "450"]


# --- helpers -----------------------------------------------------------------


def test_write_svg_with_and_without_postprocess(tmp_path: Path) -> None:
    raw = '<svg xmlns="http://www.w3.org/2000/svg"><g font-family="Arial"></g></svg>'

    plain = tmp_path / "plain.svg"
    render._write_svg(plain, raw, AZURE, postprocess=False)
    assert plain.read_text(encoding="utf-8") == raw

    processed = tmp_path / "processed.svg"
    render._write_svg(processed, raw, AZURE, postprocess=True)
    assert "Arial" not in processed.read_text(encoding="utf-8")


def test_load_theme_style_returns_normalized_tokens() -> None:
    theme = render.load_theme_style("azure-clarity")

    assert theme["theme"] == "azure-clarity"
    assert theme["colors"]["primary"]
    assert "mermaid" in theme and "drawio" in theme


def test_resolve_aspect_prefers_cli_over_directive(capsys) -> None:
    assert render._resolve_aspect(1.8, "%% aspect: 2.4") == 1.8
    assert render._resolve_aspect(None, "%% aspect: 2.4") == 2.4
    assert render._resolve_aspect(None, "flowchart LR") is None


def test_resolve_aspect_exits_on_invalid_directive(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        render._resolve_aspect(None, "%% aspect: wide")

    assert exc.value.code == 1
    assert "[ERROR]" in capsys.readouterr().err


def test_pad_output_aspect_writes_padded_file(tmp_path: Path, capsys) -> None:
    target = tmp_path / "a.svg"
    target.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 400" width="1000" height="400"></svg>',
        encoding="utf-8",
    )

    render._pad_output_aspect(target, 2.4, "full")

    assert "Padded canvas to aspect 2.4" in capsys.readouterr().out
    assert " 416.6" in target.read_text(encoding="utf-8")


def test_pad_output_aspect_leaves_matching_canvas_untouched(tmp_path: Path, capsys) -> None:
    target = tmp_path / "a.svg"
    original = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 400" width="960" height="400"></svg>'
    target.write_text(original, encoding="utf-8")

    render._pad_output_aspect(target, 2.4, "full")

    assert "Padded" not in capsys.readouterr().out
    assert target.read_text(encoding="utf-8") == original


def test_pad_output_aspect_fails_loudly_when_unreadable(tmp_path: Path, capsys) -> None:
    # _pad_output_aspect returns False (no sys.exit) so the render core stays
    # importable/testable; CLI callers in main() exit 1 on False.
    assert render._pad_output_aspect(tmp_path / "missing.svg", 2.4, "full") is False

    assert "Cannot pad canvas" in capsys.readouterr().err
