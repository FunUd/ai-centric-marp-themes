from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout_spec import (
    LAYOUTS as _LAYOUT_ORDER,
    RENDER_DEFAULT_HEIGHT as _RENDER_HEIGHTS,
    RENDER_DEFAULT_WIDTH as _RENDER_WIDTHS,
    TYPE_LAYOUT_HEIGHTS as _TYPE_LAYOUT_HEIGHTS,
)
from svg_aspect import parse_aspect


LAYOUTS = set(_LAYOUT_ORDER)
DIAGRAM_TYPES = {"pie", "donut", "pyramid", "cycle", "org-chart", "radial", "funnel", "bar", "line", "stacked-bar"}
# Cartesian (axis-based) types share the categories/series vocabulary.
CARTESIAN_TYPES = {"bar", "line", "stacked-bar"}
SERIES_TYPES = {"line", "stacked-bar"}
CARTESIAN_MAX_CATEGORIES = 10
CARTESIAN_MAX_SERIES = 4
# Canonical render sizes live in layout_spec.py; aliases kept for importers.
LAYOUT_WIDTHS = dict(_RENDER_WIDTHS)
LAYOUT_HEIGHTS = dict(_RENDER_HEIGHTS)
TYPE_LAYOUT_HEIGHTS = dict(_TYPE_LAYOUT_HEIGHTS)


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    return float(value)


def _items(data: dict[str, Any], field: str = "items") -> list[dict[str, Any]]:
    value = data.get(field)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must contain at least one item")
    if not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{field} entries must be objects")
    return value


def _validate_chart(data: dict[str, Any]) -> None:
    items = _items(data)
    for index, item in enumerate(items):
        label = item.get("label")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"items[{index}].label must not be empty")
        value = _finite_number(item.get("value"), f"items[{index}].value")
        if value <= 0:
            raise ValueError(f"items[{index}].value must be positive")
    if sum(float(item["value"]) for item in items) <= 0:
        raise ValueError("items values must have a positive total")
    if data["type"] == "donut":
        ratio = _finite_number(data.get("inner_ratio", 0.58), "inner_ratio")
        if not 0 < ratio < 1:
            raise ValueError("inner_ratio must be between 0 and 1")


def _non_negative(value: Any, field: str) -> float:
    """Finite number >= 0. Negative values are rejected for now.

    The renderer scale (`svg_diagram_renderer._y_scale`) already handles
    arbitrary min/max ranges; enabling negatives later only requires
    relaxing this check (plus zero-baseline styling tests). `stacked-bar`
    stays non-negative by design (mixed-sign stacking is ambiguous).
    """
    number = _finite_number(value, field)
    if number < 0:
        raise ValueError(f"{field} must be non-negative (negative values are not yet supported)")
    return number


def _validate_y_max(data: dict[str, Any], data_max: float) -> None:
    if "y_max" not in data:
        return
    ceiling = _finite_number(data.get("y_max"), "y_max")
    if ceiling <= 0:
        raise ValueError("y_max must be positive")
    if ceiling < data_max:
        raise ValueError("y_max must not be smaller than the largest data value")


def _validate_categories(data: dict[str, Any]) -> list[str]:
    categories = data.get("categories")
    if not isinstance(categories, list) or not 2 <= len(categories) <= CARTESIAN_MAX_CATEGORIES:
        raise ValueError(f"categories must contain between 2 and {CARTESIAN_MAX_CATEGORIES} entries")
    for index, category in enumerate(categories):
        if not isinstance(category, str) or not category.strip():
            raise ValueError(f"categories[{index}] must not be empty")
    return categories


def _validate_series(data: dict[str, Any], kind: str, min_series: int) -> tuple[list[str], list[dict[str, Any]]]:
    """Validate categories + series shapes (shared by `line` and `stacked-bar`)."""
    categories = _validate_categories(data)
    series = data.get("series")
    if not isinstance(series, list) or not min_series <= len(series) <= CARTESIAN_MAX_SERIES:
        raise ValueError(f"series must contain between {min_series} and {CARTESIAN_MAX_SERIES} entries")
    for s_index, entry in enumerate(series):
        if not isinstance(entry, dict) or not str(entry.get("label", "")).strip():
            raise ValueError(f"series[{s_index}].label must not be empty")
        values = entry.get("values")
        if not isinstance(values, list) or len(values) != len(categories):
            raise ValueError(f"series[{s_index}].values must have one entry per category")
        for v_index, value in enumerate(values):
            _non_negative(value, f"series[{s_index}].values[{v_index}]")
    return categories, series


def _series_max(series: list[dict[str, Any]], stacked: bool) -> float:
    if stacked:
        count = len(series[0]["values"])
        return max(sum(float(entry["values"][index]) for entry in series) for index in range(count))
    return max(float(value) for entry in series for value in entry["values"])


def _validate_type(data: dict[str, Any]) -> None:
    kind = data["type"]
    if kind in {"pie", "donut"}:
        _validate_chart(data)
    elif kind == "bar":
        items = _items(data)
        if not 2 <= len(items) <= CARTESIAN_MAX_CATEGORIES:
            raise ValueError(f"items must contain between 2 and {CARTESIAN_MAX_CATEGORIES} entries")
        for index, item in enumerate(items):
            if not isinstance(item.get("label"), str) or not item["label"].strip():
                raise ValueError(f"items[{index}].label must not be empty")
            _non_negative(item.get("value"), f"items[{index}].value")
        _validate_y_max(data, max(float(item["value"]) for item in items))
    elif kind == "line":
        _, series = _validate_series(data, kind, min_series=1)
        _validate_y_max(data, _series_max(series, stacked=False))
    elif kind == "stacked-bar":
        _, series = _validate_series(data, kind, min_series=2)
        _validate_y_max(data, _series_max(series, stacked=True))
    elif kind == "pyramid":
        levels = data.get("levels")
        if not isinstance(levels, list) or not 3 <= len(levels) <= 6:
            raise ValueError("levels must contain between 3 and 6 entries")
        if data.get("direction", "up") not in {"up", "down"}:
            raise ValueError("direction must be up or down")
        for index, level in enumerate(levels):
            if not isinstance(level, dict) or not str(level.get("label", "")).strip():
                raise ValueError(f"levels[{index}].label must not be empty")
    elif kind == "cycle":
        items = _items(data)
        if not 3 <= len(items) <= 8:
            raise ValueError("items must contain between 3 and 8 entries")
        if data.get("direction", "clockwise") not in {"clockwise", "counterclockwise"}:
            raise ValueError("direction must be clockwise or counterclockwise")
        for index, item in enumerate(items):
            if not str(item.get("label", "")).strip():
                raise ValueError(f"items[{index}].label must not be empty")
    elif kind == "org-chart":
        root = data.get("root")
        if not isinstance(root, dict) or not str(root.get("label", "")).strip():
            raise ValueError("root.label must not be empty")
        def visit(node: dict[str, Any], depth: int) -> None:
            if depth > 4:
                raise ValueError("root depth must not exceed 4")
            children = node.get("children", [])
            if not isinstance(children, list) or len(children) > 6:
                raise ValueError("children must contain at most 6 entries")
            for child in children:
                if not isinstance(child, dict) or not str(child.get("label", "")).strip():
                    raise ValueError("every organization node needs a label")
                visit(child, depth + 1)
        visit(root, 1)
    elif kind == "radial":
        if not str(data.get("center", "")).strip():
            raise ValueError("center must not be empty")
        items = _items(data)
        if not 3 <= len(items) <= 8:
            raise ValueError("items must contain between 3 and 8 entries")
        for index, item in enumerate(items):
            if not str(item.get("label", "")).strip():
                raise ValueError(f"items[{index}].label must not be empty")
    elif kind == "funnel":
        levels = data.get("levels")
        if not isinstance(levels, list) or not 3 <= len(levels) <= 6:
            raise ValueError("levels must contain between 3 and 6 entries")
        if data.get("direction", "down") not in {"down", "up"}:
            raise ValueError("direction must be down or up")
        for index, level in enumerate(levels):
            if not isinstance(level, dict) or not str(level.get("label", "")).strip():
                raise ValueError(f"levels[{index}].label must not be empty")
            if "value" in level:
                value = _finite_number(level["value"], f"levels[{index}].value")
                if value < 0:
                    raise ValueError(f"levels[{index}].value must not be negative")


def parse_diagram_data(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a JSON diagram definition."""
    if not isinstance(data, dict):
        raise ValueError("diagram root must be an object")
    kind = data.get("type")
    if kind not in DIAGRAM_TYPES:
        raise ValueError("type must be one of: " + ", ".join(sorted(DIAGRAM_TYPES)))
    layout = data.get("layout", "full")
    if layout not in LAYOUTS:
        raise ValueError("layout must be one of: " + ", ".join(sorted(LAYOUTS)))
    width = _finite_number(data.get("width", LAYOUT_WIDTHS[layout]), "width")
    if "aspect" in data:
        if data.get("height") is not None:
            raise ValueError("aspect and height are mutually exclusive; specify only one")
        height = width / parse_aspect(data["aspect"])
    else:
        default_height = TYPE_LAYOUT_HEIGHTS.get((kind, layout), LAYOUT_HEIGHTS[layout])
        height = _finite_number(data.get("height", default_height), "height")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    normalized = dict(data)
    normalized.update({"theme": data.get("theme", "azure-clarity"), "layout": layout, "width": width, "height": height})
    _validate_type(normalized)
    return normalized