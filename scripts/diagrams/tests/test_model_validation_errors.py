"""Parametrized rejection tests for diagram_models.parse_diagram_data.

Every case asserts one validation error branch that earlier tests never
exercised (empty/non-list items, label/value constraints, y_max rules,
per-type shape rules for pyramid/cycle/org-chart/radial/funnel, and the
root/size/aspect guards).
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


models = load_module("diagram_models_rejects", "diagram_models.py")


@pytest.mark.parametrize(
    "data, message",
    [
        # --- root / size / aspect guards -------------------------------------
        ([], "diagram root must be an object"),
        ({"type": "mystery"}, "type must be one of"),
        ({"type": "pie", "layout": "sideways", "items": [{"label": "A", "value": 1}]}, "layout must be one of"),
        (
            {"type": "pie", "aspect": 2.0, "height": 100, "items": [{"label": "A", "value": 1}]},
            "aspect and height are mutually exclusive",
        ),
        ({"type": "pie", "width": -10, "items": [{"label": "A", "value": 1}]}, "width and height must be positive"),
        ({"type": "pie", "width": True, "items": [{"label": "A", "value": 1}]}, "width must be a finite number"),
        ({"type": "pie", "width": "wide", "items": [{"label": "A", "value": 1}]}, "width must be a finite number"),
        (
            {"type": "pie", "height": float("inf"), "items": [{"label": "A", "value": 1}]},
            "height must be a finite number",
        ),
        # --- items containers -------------------------------------------------
        ({"type": "pie", "items": []}, "must contain at least one item"),
        ({"type": "pie", "items": "A,B"}, "must contain at least one item"),
        ({"type": "pie", "items": [1, 2]}, "entries must be objects"),
        # --- chart (pie/donut) rules -----------------------------------------
        ({"type": "pie", "items": [{"label": "   ", "value": 1}]}, "label must not be empty"),
        ({"type": "pie", "items": [{"label": "A", "value": 0}]}, "value must be positive"),
        ({"type": "pie", "items": [{"label": "A", "value": -3}]}, "value must be positive"),
        (
            {"type": "donut", "inner_ratio": 1.4, "items": [{"label": "A", "value": 1}]},
            "inner_ratio must be between 0 and 1",
        ),
        (
            {"type": "donut", "inner_ratio": 0.0, "items": [{"label": "A", "value": 1}]},
            "inner_ratio must be between 0 and 1",
        ),
        (
            {"type": "donut", "inner_ratio": "golden", "items": [{"label": "A", "value": 1}]},
            "inner_ratio must be a finite number",
        ),
        # --- bar rules --------------------------------------------------------
        ({"type": "bar", "items": [{"label": "A", "value": 1}]}, "items must contain between 2 and 10 entries"),
        ({"type": "bar", "items": [{"label": "A", "value": -1}, {"label": "B", "value": 1}]}, "must be non-negative"),
        ({"type": "bar", "items": [{"label": "", "value": 1}, {"label": "B", "value": 1}]}, "label must not be empty"),
        (
            {"type": "bar", "y_max": 0, "items": [{"label": "A", "value": 1}, {"label": "B", "value": 1}]},
            "y_max must be positive",
        ),
        (
            {"type": "bar", "y_max": 2, "items": [{"label": "A", "value": 5}, {"label": "B", "value": 1}]},
            "y_max must not be smaller",
        ),
        # --- line / stacked-bar (categories + series) -------------------------
        (
            {"type": "line", "categories": ["only"], "series": [{"label": "s", "values": [1]}]},
            "categories must contain between 2 and 10",
        ),
        (
            {"type": "line", "categories": ["a", "b"], "series": [{"label": "", "values": [1, 2]}]},
            "label must not be empty",
        ),
        (
            {"type": "line", "categories": ["a", "b"], "series": [{"label": "s", "values": [1]}]},
            "values must have one entry per category",
        ),
        (
            {"type": "line", "categories": ["a", "b"], "series": [{"label": "s", "values": [1, -2]}]},
            "must be non-negative",
        ),
        ({"type": "line", "categories": ["a", "b"], "series": [7]}, "label must not be empty"),
        (
            {"type": "line", "categories": ["a", "b"], "y_max": -1, "series": [{"label": "s", "values": [1, 2]}]},
            "y_max must be positive",
        ),
        (
            {"type": "stacked-bar", "categories": ["a", "b"], "series": [{"label": "s", "values": [1, 2]}]},
            "series must contain between 2 and 4",
        ),
        ({"type": "line", "categories": ["a", "b"], "series": []}, "series must contain between 1 and 4"),
        ({"type": "line", "categories": ["a", 2], "series": [{"label": "s", "values": [1, 2]}]}, "must not be empty"),
        # --- pyramid ----------------------------------------------------------
        ({"type": "pyramid"}, "levels must contain between 3 and 6"),
        ({"type": "pyramid", "levels": [{"label": "A"}, {"label": "B"}]}, "levels must contain between 3 and 6"),
        (
            {"type": "pyramid", "levels": [{"label": "A"}, {"label": "B"}, {"label": "C"}], "direction": "left"},
            "direction must be up or down",
        ),
        ({"type": "pyramid", "levels": [{"label": "A"}, {"label": " "}, {"label": "C"}]}, "label must not be empty"),
        # --- cycle ------------------------------------------------------------
        ({"type": "cycle", "items": [{"label": "A"}, {"label": "B"}]}, "items must contain between 3 and 8"),
        (
            {"type": "cycle", "items": [{"label": "A"}, {"label": "B"}, {"label": "C"}], "direction": "sideways"},
            "direction must be clockwise or counterclockwise",
        ),
        ({"type": "cycle", "items": [{"label": "A"}, {"label": ""}, {"label": "C"}]}, "label must not be empty"),
        # --- org-chart --------------------------------------------------------
        ({"type": "org-chart", "root": {"children": []}}, "root.label must not be empty"),
        (
            {
                "type": "org-chart",
                "root": {
                    "label": "R",
                    "children": [
                        {
                            "label": "A",
                            "children": [
                                {
                                    "label": "B",
                                    "children": [
                                        {"label": "C", "children": [{"label": "D", "children": [{"label": "E"}]}]}
                                    ],
                                }
                            ],
                        }
                    ],
                },
            },
            "root depth must not exceed 4",
        ),
        (
            {
                "type": "org-chart",
                "root": {
                    "label": "R",
                    "children": [
                        {"label": "1"},
                        {"label": "2"},
                        {"label": "3"},
                        {"label": "4"},
                        {"label": "5"},
                        {"label": "6"},
                        {"label": "7"},
                    ],
                },
            },
            "children must contain at most 6 entries",
        ),
        (
            {"type": "org-chart", "root": {"label": "R", "children": [{"children": []}]}},
            "every organization node needs a label",
        ),
        # --- radial -----------------------------------------------------------
        (
            {"type": "radial", "center": "  ", "items": [{"label": "A"}, {"label": "B"}, {"label": "C"}]},
            "center must not be empty",
        ),
        (
            {"type": "radial", "center": "C", "items": [{"label": "A"}, {"label": "B"}]},
            "items must contain between 3 and 8",
        ),
        (
            {"type": "radial", "center": "C", "items": [{"label": "A"}, {"label": "B"}, {"label": ""}]},
            "label must not be empty",
        ),
        # --- funnel -----------------------------------------------------------
        ({"type": "funnel"}, "levels must contain between 3 and 6"),
        (
            {"type": "funnel", "levels": [{"label": "A"}, {"label": "B"}, {"label": "C"}], "direction": "left"},
            "direction must be down or up",
        ),
        ({"type": "funnel", "levels": [{"label": "A"}, {"label": "B"}, {"label": ""}]}, "label must not be empty"),
        (
            {"type": "funnel", "levels": [{"label": "A", "value": -1}, {"label": "B"}, {"label": "C"}]},
            "must not be negative",
        ),
        (
            {"type": "funnel", "levels": [{"label": "A", "value": "ten"}, {"label": "B"}, {"label": "C"}]},
            "value must be a finite number",
        ),
    ],
)
def test_parse_diagram_data_rejects_invalid_input(data, message) -> None:
    with pytest.raises(ValueError, match=message):
        models.parse_diagram_data(data)


def test_parse_diagram_data_normalizes_valid_org_chart() -> None:
    diagram = models.parse_diagram_data({"type": "org-chart", "root": {"label": "CEO", "children": [{"label": "CTO"}]}})

    assert diagram["width"] == 1080
    assert diagram["height"] == 420
    assert diagram["theme"] == "azure-clarity"
