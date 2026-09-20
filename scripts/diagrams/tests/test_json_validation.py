from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
routing_spec = importlib.util.spec_from_file_location("diagram_routing", SCRIPT_DIR / "diagram_routing.py")
assert routing_spec and routing_spec.loader
routing = importlib.util.module_from_spec(routing_spec)
sys.modules["diagram_routing"] = routing
routing_spec.loader.exec_module(routing)
spec = importlib.util.spec_from_file_location("diagram_validator_json", SCRIPT_DIR / "validate-slide-diagram.py")
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def write_svg(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "diagram.svg"
    path.write_text(f'<svg viewBox="0 0 100 80" width="100" height="80">{body}</svg>', encoding="utf-8")
    return path


def test_json_svg_out_of_bounds_is_rejected(tmp_path: Path) -> None:
    errors, _ = validator.validate_svg(write_svg(tmp_path, '<rect data-diagram-role="node" x="90" y="1" width="20" height="10" />'), "col2")

    assert any("outside" in error.lower() for error in errors)


def test_json_svg_overlapping_nodes_are_rejected(tmp_path: Path) -> None:
    errors, _ = validator.validate_svg(
        write_svg(tmp_path, '<rect data-diagram-role="node" x="1" y="1" width="20" height="20" /><rect data-diagram-role="node" x="10" y="10" width="20" height="20" />'),
        "col2",
    )

    assert any("overlap" in error.lower() for error in errors)


def test_json_svg_connector_crossing_node_is_rejected(tmp_path: Path) -> None:
    errors, _ = validator.validate_svg(
        write_svg(tmp_path, '<rect data-diagram-role="node" x="40" y="20" width="20" height="20" /><path data-diagram-role="connector" d="M 0 30 L 100 30" />'),
        "col2",
    )

    assert any("connector" in error.lower() for error in errors)


def test_json_svg_small_text_is_warned(tmp_path: Path) -> None:
    _, warnings = validator.validate_svg(write_svg(tmp_path, '<text data-diagram-role="label" x="1" y="10" font-size="7">A</text>'), "col2")

    assert any("font" in warning.lower() for warning in warnings)