"""Error-path tests for svg_aspect.py not covered by test_aspect.py:
non-scalar aspect values, non-positive content dimensions, and a
malformed viewBox."""
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


aspect = load_module("svg_aspect_errors", "svg_aspect.py")


def test_parse_aspect_rejects_non_scalars() -> None:
    with pytest.raises(ValueError, match="aspect must be a number"):
        aspect.parse_aspect([16, 9])
    with pytest.raises(ValueError, match="aspect must be a number"):
        aspect.parse_aspect({"w": 16})
    with pytest.raises(ValueError, match="aspect must be a number"):
        aspect.parse_aspect(True)


def test_feasible_range_rejects_non_positive_content() -> None:
    with pytest.raises(ValueError, match="dimensions must be positive"):
        aspect.feasible_aspect_range(0, 400)
    with pytest.raises(ValueError, match="dimensions must be positive"):
        aspect.feasible_aspect_range(800, -10)


def test_pad_viewbox_rejects_malformed_viewbox() -> None:
    with pytest.raises(ValueError, match="malformed viewBox"):
        aspect.pad_viewbox('<svg viewBox="0 0 100"></svg>', 2.4)


def test_pad_viewbox_requires_geometry(monkeypatch) -> None:
    with pytest.raises(ValueError, match="neither a viewBox nor numeric width/height"):
        aspect.pad_viewbox("<svg></svg>", 2.4)
    with pytest.raises(ValueError, match="SVG root element not found"):
        aspect.pad_viewbox("<div></div>", 2.4)


def test_check_aspect_feasible_reports_infeasible_ratio() -> None:
    problem = aspect.check_aspect_feasible(10.0, 800, 400, "full")

    assert problem is not None
    assert "not reachable by padding" in problem
    assert aspect.check_aspect_feasible(2.4, 800, 400, "full") is None
