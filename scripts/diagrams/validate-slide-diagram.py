#!/usr/bin/env python3
"""
validate-slide-diagram.py — Slide diagram layout & overflow validator.

Validates that generated diagram SVG or .drawio files strictly conform
to Marp slide canvas constraints to prevent overflow and text distortion.

Usage:
    python scripts/diagrams/validate-slide-diagram.py <file.svg|file.drawio> [--layout full|col2|asym|col3] [--strict]

Exit codes:
    0  Validation passed (or warnings only in non-strict mode)
    1  One or more validation errors found
"""
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Layout canvas constraints (pixels)
LAYOUT_LIMITS = {
    "full": {"max_w": 1140, "max_h": 470, "min_aspect": 1.2, "max_aspect": 4.5},
    "col2": {"max_w": 540, "max_h": 470, "min_aspect": 0.6, "max_aspect": 2.2},
    "asym": {"max_w": 730, "max_h": 470, "min_aspect": 0.9, "max_aspect": 3.0},
    "col3": {"max_w": 360, "max_h": 470, "min_aspect": 0.4, "max_aspect": 1.8},
}


def _parse_dimension(val: str | None) -> float | None:
    """Extract numeric value from px/pt/raw string."""
    if not val:
        return None
    val = val.strip().lower()
    if val.endswith("%"):
        return None
    val = re.sub(r"[a-z]+$", "", val)
    try:
        return float(val)
    except ValueError:
        return None


def validate_svg(path: Path, layout: str) -> tuple[list[str], list[str]]:
    """Validate SVG dimension, aspect ratio, and potential text issues."""
    errors: list[str] = []
    warnings: list[str] = []
    limits = LAYOUT_LIMITS.get(layout, LAYOUT_LIMITS["full"])

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return [f"SVG XML parse error: {e}"], []

    root = tree.getroot()
    # Check if root is svg (handling namespace)
    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if tag != "svg":
        return [f"Root element must be <svg>, got <{root.tag}>"], []

    # 1. Dimension & ViewBox Extraction
    view_box = root.get("viewBox")
    width_attr = _parse_dimension(root.get("width"))
    height_attr = _parse_dimension(root.get("height"))

    w, h = None, None
    if view_box:
        parts = [float(p) for p in view_box.replace(",", " ").split() if p.strip()]
        if len(parts) == 4:
            w, h = parts[2], parts[3]
    if w is None or h is None:
        w, h = width_attr, height_attr

    if w is None or h is None or w <= 0 or h <= 0:
        warnings.append(f"Could not determine positive width/height from SVG attributes or viewBox in {path.name}")
    else:
        aspect = w / h
        # Boundary checks
        if h > limits["max_h"]:
            errors.append(
                f"Height ({h:.1f}px) exceeds max allowed height ({limits['max_h']}px) for layout '{layout}'. "
                f"This will cause slide vertical overflow!"
            )
        if w > limits["max_w"]:
            errors.append(
                f"Width ({w:.1f}px) exceeds max allowed width ({limits['max_w']}px) for layout '{layout}'. "
                f"This will cause slide horizontal overflow!"
            )

        # Aspect ratio checks
        if aspect < limits["min_aspect"]:
            warnings.append(
                f"Diagram is too tall/narrow (aspect ratio {aspect:.2f} < {limits['min_aspect']}). "
                f"When placed on a slide, it will be heavily shrunk vertically, making fonts unreadable."
            )
        elif aspect > limits["max_aspect"]:
            warnings.append(
                f"Diagram is extremely wide/short (aspect ratio {aspect:.2f} > {limits['max_aspect']}). "
                f"Consider using multi-row layout or splitting into columns."
            )

    # 2. Check for long unbroken text lines in foreignObject or text nodes
    for elem in root.iter():
        text_content = (elem.text or "").strip()
        if len(text_content) > 30 and not any(sep in text_content for sep in [" ", "\n", "、", "。"]):
            warnings.append(f"Long unbroken text detected ('{text_content[:20]}...'). May cause node overflow.")

    return errors, warnings


def validate_drawio(path: Path, layout: str) -> tuple[list[str], list[str]]:
    """Validate .drawio XML structure and cell bounds."""
    errors: list[str] = []
    warnings: list[str] = []
    limits = LAYOUT_LIMITS.get(layout, LAYOUT_LIMITS["full"])

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return [f"draw.io XML parse error: {e}"], []

    root = tree.getroot()
    if root.tag != "mxfile":
        return [f"Root element must be <mxfile>, got <{root.tag}>"], []

    diagrams = root.findall("diagram")
    if not diagrams:
        return ["No <diagram> element found inside <mxfile>"], []

    for d_idx, diag in enumerate(diagrams):
        graph_model = diag.find("mxGraphModel")
        if graph_model is None:
            continue
        root_elem = graph_model.find("root")
        if root_elem is None:
            errors.append(f"Page {d_idx}: Missing <root> inside <mxGraphModel>")
            continue

        cells = root_elem.findall("mxCell")
        cell_ids: set[str] = set()
        has_id0, has_id1 = False, False

        for cell in cells:
            cid = cell.get("id")
            if not cid:
                errors.append(f"Page {d_idx}: Found <mxCell> without 'id'")
                continue
            if cid in cell_ids:
                errors.append(f"Page {d_idx}: Duplicate cell id='{cid}'")
            cell_ids.add(cid)
            if cid == "0":
                has_id0 = True
            if cid == "1":
                has_id1 = True

            # Geometry boundary check for top-level shapes
            if cell.get("parent") == "1" and cell.get("vertex") == "1":
                geom = cell.find("mxGeometry")
                if geom is not None:
                    x = _parse_dimension(geom.get("x")) or 0
                    y = _parse_dimension(geom.get("y")) or 0
                    w = _parse_dimension(geom.get("width")) or 0
                    h = _parse_dimension(geom.get("height")) or 0
                    if x + w > limits["max_w"]:
                        errors.append(
                            f"Cell id='{cid}' bounds ({x+w:.0f}px) exceed canvas width ({limits['max_w']}px)"
                        )
                    if y + h > limits["max_h"]:
                        errors.append(
                            f"Cell id='{cid}' bounds ({y+h:.0f}px) exceed canvas height ({limits['max_h']}px)"
                        )

        if not has_id0 or not has_id1:
            errors.append(f"Page {d_idx}: Missing required root cells (id='0' or id='1')")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate diagram file against slide constraints.")
    parser.add_argument("path", type=Path, help="Path to .svg or .drawio file")
    parser.add_argument(
        "--layout",
        choices=["full", "col2", "asym", "col3"],
        default="full",
        help="Target slide layout (default: full)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()

    target_path: Path = args.path
    if not target_path.exists():
        print(f"[ERROR] File not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    suffix = target_path.suffix.lower()
    if suffix == ".svg":
        errors, warnings = validate_svg(target_path, args.layout)
    elif suffix in (".drawio", ".xml"):
        errors, warnings = validate_drawio(target_path, args.layout)
    else:
        print(f"[ERROR] Unsupported file extension '{suffix}'. Expected .svg or .drawio", file=sys.stderr)
        sys.exit(1)

    # Print results
    print(f"=== Diagram Validation: {target_path.name} (Layout: {args.layout}) ===")
    for w in warnings:
        print(f"  [WARN] {w}")
    for e in errors:
        print(f"  [ERROR] {e}")

    if errors or (args.strict and warnings):
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"PASSED: Diagram conforms to slide canvas specifications. ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
