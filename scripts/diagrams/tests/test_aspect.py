from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# svg_aspect inserts scripts/diagrams onto sys.path so the validator's plain
# `from diagram_routing import ...` resolves when loaded below.
svg_aspect = load_module("svg_aspect", "svg_aspect.py")
models = load_module("diagram_models", "diagram_models.py")
validator = load_module("validate_slide_diagram", "validate-slide-diagram.py")


# --- parse_aspect -----------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2.4", 2.4),
        ("16:9", pytest.approx(16 / 9)),
        ("16 : 9", pytest.approx(16 / 9)),
        (2.4, 2.4),
        (3, 3.0),
        ("0.5", 0.5),
        ("4:1", 4.0),
    ],
)
def test_parse_aspect_accepts_decimal_and_ratio(value, expected) -> None:
    assert svg_aspect.parse_aspect(value) == expected


@pytest.mark.parametrize(
    "value",
    ["abc", "-1", "0", "16:9:1", "", None, "16:", ":9", "nan", "inf", "a:b", "16:0", True],
)
def test_parse_aspect_rejects_invalid(value) -> None:
    with pytest.raises(ValueError):
        svg_aspect.parse_aspect(value)


# --- Mermaid %% aspect directive -------------------------------------------


def test_extract_mermaid_aspect_decimal_directive() -> None:
    source = "%% aspect: 2.4\nflowchart LR; A-->B"
    assert svg_aspect.extract_mermaid_aspect(source) == pytest.approx(2.4)


def test_extract_mermaid_aspect_ratio_directive() -> None:
    source = "flowchart LR\n  %% aspect: 16:9\n  A-->B"
    assert svg_aspect.extract_mermaid_aspect(source) == pytest.approx(16 / 9)


def test_extract_mermaid_aspect_absent_returns_none() -> None:
    assert svg_aspect.extract_mermaid_aspect("flowchart LR; A-->B") is None


def test_extract_mermaid_aspect_invalid_value_raises() -> None:
    with pytest.raises(ValueError, match="aspect"):
        svg_aspect.extract_mermaid_aspect("%% aspect: wide\nflowchart LR; A-->B")


def test_extract_mermaid_aspect_ignores_unrelated_comments() -> None:
    assert svg_aspect.extract_mermaid_aspect("%% just a note\nflowchart LR; A-->B") is None


# --- feasible range ---------------------------------------------------------


def test_feasible_aspect_range_full_layout() -> None:
    low, high = svg_aspect.feasible_aspect_range(800, 400, "full")
    assert low == pytest.approx(800 / 470)
    assert high == pytest.approx(1140 / 400)


def test_feasible_aspect_range_rejects_oversized_content() -> None:
    with pytest.raises(ValueError, match="already exceeds"):
        svg_aspect.feasible_aspect_range(1200, 400, "full")


def test_check_aspect_feasible_reports_range() -> None:
    problem = svg_aspect.check_aspect_feasible(4.0, 800, 400, "full")
    assert problem is not None
    assert "feasible range" in problem
    assert svg_aspect.check_aspect_feasible(2.5, 800, 400, "full") is None


# --- pad_viewbox ------------------------------------------------------------

WIDE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 100" width="900" height="100">'
    '<rect x="10" y="10" width="50" height="20" fill="#000"/>'
    "</svg>"
)
TALL_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400">'
    '<rect x="10" y="10" width="50" height="20" fill="#000"/>'
    "</svg>"
)
MERMAID_SVG = (
    '<svg id="my-svg" width="100%" style="max-width: 400px; background-color: transparent;" '
    'viewBox="0 0 400 400"><rect x="0" y="0" width="10" height="10"/></svg>'
)


def _viewbox(svg: str) -> list[float]:
    import re

    match = re.search(r'viewBox="([^"]+)"', svg)
    assert match, "viewBox not found"
    return [float(part) for part in match.group(1).split()]


def test_pad_viewbox_grows_height_and_centers() -> None:
    out = svg_aspect.pad_viewbox(WIDE_SVG, 4.5, "full")
    min_x, min_y, width, height = _viewbox(out)
    assert width == pytest.approx(900)
    assert height == pytest.approx(200)  # 900 / 4.5
    assert min_y == pytest.approx(-50)  # centered: (200-100)/2 above
    assert min_x == pytest.approx(0)
    assert 'width="900"' in out and 'height="200"' in out
    assert '<rect x="10" y="10" width="50" height="20"' in out  # content untouched


def test_pad_viewbox_grows_width_and_centers() -> None:
    out = svg_aspect.pad_viewbox(TALL_SVG, 1.2, "full")
    min_x, min_y, width, height = _viewbox(out)
    assert width == pytest.approx(480)  # 400 * 1.2
    assert height == pytest.approx(400)
    assert min_x == pytest.approx(-90)  # centered: (480-300)/2 left
    assert min_y == pytest.approx(0)
    assert 'width="480"' in out


def test_pad_viewbox_mermaid_style_attrs() -> None:
    out = svg_aspect.pad_viewbox(MERMAID_SVG, 2.4, "full")
    min_x, _min_y, width, height = _viewbox(out)
    assert width == pytest.approx(960)  # 400 * 2.4
    assert height == pytest.approx(400)
    assert min_x == pytest.approx(-280)
    assert 'width="100%"' in out  # percentage width preserved
    assert "max-width: 960px" in out  # mermaid sizing hint kept in sync
    assert '<rect x="0" y="0"' in out


def test_pad_viewbox_noop_at_target_ratio() -> None:
    svg = '<svg viewBox="0 0 900 450" width="900" height="450"><rect x="0" y="0" width="5" height="5"/></svg>'
    assert svg_aspect.pad_viewbox(svg, "16:8", "full") == svg


def test_pad_viewbox_infeasible_aspect_raises_with_range() -> None:
    at_limit = (
        '<svg viewBox="0 0 1140 470" width="1140" height="470">'
        '<rect x="0" y="0" width="5" height="5"/></svg>'
    )
    with pytest.raises(ValueError, match="feasible range"):
        svg_aspect.pad_viewbox(at_limit, 1.0, "full")


def test_pad_viewbox_oversized_content_raises() -> None:
    oversized = (
        '<svg viewBox="0 0 1200 470" width="1200" height="470">'
        '<rect x="0" y="0" width="5" height="5"/></svg>'
    )
    with pytest.raises(ValueError, match="already exceeds"):
        svg_aspect.pad_viewbox(oversized, 2.4, "full")


def test_pad_viewbox_derives_from_width_height_without_viewbox() -> None:
    svg = '<svg width="600" height="400"><rect x="0" y="0" width="5" height="5"/></svg>'
    out = svg_aspect.pad_viewbox(svg, 2.0, "full")
    min_x, _min_y, width, height = _viewbox(out)
    assert (min_x, width, height) == pytest.approx((-100, 800, 400))
    assert 'width="800"' in out


def test_pad_viewbox_unresolvable_canvas_raises() -> None:
    with pytest.raises(ValueError, match="viewBox"):
        svg_aspect.pad_viewbox('<svg width="100%"></svg>', 2.0, "full")


def test_pad_viewbox_missing_root_raises() -> None:
    with pytest.raises(ValueError, match="root"):
        svg_aspect.pad_viewbox("<rect/>", 2.0, "full")


# --- JSON model aspect field ------------------------------------------------


def test_model_aspect_derives_height_from_width() -> None:
    diagram = models.parse_diagram_data({"type": "pie", "aspect": 2.4, "items": [{"label": "A", "value": 1}]})
    assert diagram["width"] == 1080
    assert diagram["height"] == pytest.approx(450)


def test_model_aspect_accepts_ratio_string_and_layout_width() -> None:
    diagram = models.parse_diagram_data(
        {"type": "cycle", "layout": "col2", "aspect": "16:9", "items": [{"label": "A"}, {"label": "B"}, {"label": "C"}]}
    )
    assert diagram["width"] == 520
    assert diagram["height"] == pytest.approx(520 / (16 / 9))


def test_model_rejects_aspect_with_explicit_height() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        models.parse_diagram_data(
            {"type": "pie", "aspect": 2.4, "height": 420, "items": [{"label": "A", "value": 1}]}
        )


# --- validator aspect hint --------------------------------------------------


def test_validator_too_tall_warning_mentions_aspect_flag(tmp_path: Path) -> None:
    svg = tmp_path / "tall.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400"/>',
        encoding="utf-8",
    )
    _errors, warnings = validator.validate_svg(svg, "full")
    assert any("--aspect" in warning for warning in warnings), warnings


def test_validator_too_wide_warning_mentions_aspect_flag(tmp_path: Path) -> None:
    svg = tmp_path / "wide.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" width="1000" height="100"/>',
        encoding="utf-8",
    )
    _errors, warnings = validator.validate_svg(svg, "full")
    assert any("--aspect 4.5" in warning for warning in warnings), warnings


# --- end-to-end render wiring ----------------------------------------------


def _load_render_script():
    for name, filename in (
        ("svg_filters", "svg_filters.py"),
        ("diagram_models", "diagram_models.py"),
        ("svg_diagram_renderer", "svg_diagram_renderer.py"),
        ("diagram_routing", "diagram_routing.py"),
    ):
        if name not in sys.modules:
            load_module(name, filename)
    spec = importlib.util.spec_from_file_location("render_slide_diagram", SCRIPT_DIR / "render-slide-diagram.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_render_json_diagram_aspect_reflows_canvas(tmp_path: Path) -> None:
    import json

    script = _load_render_script()
    source = tmp_path / "diagram.json"
    output = tmp_path / "diagram.svg"
    source.write_text(
        json.dumps({"type": "pie", "aspect": 2.4, "items": [{"label": "A", "value": 1}]}),
        encoding="utf-8",
    )

    assert script.render_json_diagram(source, output, script.load_theme_style("azure-clarity"), "full")
    assert _viewbox(output.read_text(encoding="utf-8"))[2:] == pytest.approx([1080, 450])


def test_render_json_diagram_cli_aspect_overrides_source_height(tmp_path: Path) -> None:
    import json

    script = _load_render_script()
    source = tmp_path / "diagram.json"
    output = tmp_path / "diagram.svg"
    source.write_text(
        json.dumps({"type": "pie", "height": 420, "items": [{"label": "A", "value": 1}]}),
        encoding="utf-8",
    )

    assert script.render_json_diagram(
        source, output, script.load_theme_style("azure-clarity"), "full", aspect=2.0
    )
    assert _viewbox(output.read_text(encoding="utf-8"))[2:] == pytest.approx([1080, 540])


def test_pad_output_aspect_round_trip(tmp_path: Path) -> None:
    """Mermaid-style render → pad → validator passes without aspect warnings."""
    script = _load_render_script()
    theme_data = script.load_theme_style("prism-edge")
    original = script.postprocess_svg(
        '<svg id="x" width="100%" style="max-width: 752.484px; background-color: transparent;" '
        'viewBox="0 0 752.484375 58.5"><rect x="0" y="0" width="10" height="10"/></svg>',
        theme_data,
    )
    output = tmp_path / "padded.svg"
    output.write_text(svg_aspect.pad_viewbox(original, 4.5, "full"), encoding="utf-8")

    errors, warnings = validator.validate_svg(output, "full")
    assert not errors, errors
    assert not [w for w in warnings if "aspect" in w.lower()], warnings
