from __future__ import annotations

import math
from typing import Any


LAYOUTS = {"full", "col2", "asym", "col3"}
DIAGRAM_TYPES = {"pie", "donut", "pyramid", "cycle", "org-chart", "radial", "funnel"}
LAYOUT_WIDTHS = {"full": 1080, "col2": 520, "asym": 710, "col3": 340}
LAYOUT_HEIGHTS = {"full": 420, "col2": 360, "asym": 420, "col3": 300}
TYPE_LAYOUT_HEIGHTS = {("radial", "asym"): 260}


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


def _validate_type(data: dict[str, Any]) -> None:
    kind = data["type"]
    if kind in {"pie", "donut"}:
        _validate_chart(data)
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
    default_height = TYPE_LAYOUT_HEIGHTS.get((kind, layout), LAYOUT_HEIGHTS[layout])
    height = _finite_number(data.get("height", default_height), "height")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    normalized = dict(data)
    normalized.update({"theme": data.get("theme", "azure-clarity"), "layout": layout, "width": width, "height": height})
    _validate_type(normalized)
    return normalized