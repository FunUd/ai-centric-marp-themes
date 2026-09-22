#!/usr/bin/env python3
"""
render-slide-diagram.py — Universal Slide Diagram Engine.

Renders Mermaid and draw.io diagrams into slide-optimized SVGs that perfectly
harmonize with all 6 Marp presentation themes, enforcing strict canvas constraints
to prevent visual breakage and overflow.

Usage:
    python scripts/diagrams/render-slide-diagram.py -i input.mmd -o output.svg --theme azure-clarity --layout full
    python scripts/diagrams/render-slide-diagram.py -i input.drawio -o output.svg --theme nebula-glass --layout full
    python scripts/diagrams/render-slide-diagram.py --code "flowchart LR; A-->B" -o output.svg --theme prism-edge

Exit codes:
    0  Success
    1  Render or validation error
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from diagram_routing import edge_endpoints, get_edge_waypoints, node_shape, route_edge, snap_edge_points

from design_tokens import best_text_on, drawio_rect_radius, load_design_tokens
from diagram_models import parse_diagram_data
from svg_diagram_renderer import render_diagram
from svg_filters import build_filter_defs
from svg_theme_postprocessor import postprocess_svg

SCRIPT_DIR = Path(__file__).resolve().parent
THEME_STYLES_DIR = SCRIPT_DIR / "theme-styles"
VALIDATOR_PATH = SCRIPT_DIR / "validate-slide-diagram.py"


def load_theme_style(theme_name: str) -> dict:
    """Load normalized theme configuration including design tokens."""
    return load_design_tokens(theme_name)


def _write_svg(output_path: Path, svg_content: str, theme_data: dict, postprocess: bool) -> None:
    if postprocess:
        svg_content = postprocess_svg(svg_content, theme_data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content, encoding="utf-8")


def render_mermaid(
    input_content: str,
    output_path: Path,
    theme_data: dict,
    layout: str,
    postprocess: bool = True,
) -> bool:
    """Render Mermaid syntax to SVG using @mermaid-js/mermaid-cli with theme injection."""
    mermaid_config = theme_data.get("mermaid", {})
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        cfg_file = tmp_path / "mermaid-config.json"
        mmd_file = tmp_path / "diagram.mmd"

        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(mermaid_config, f, indent=2, ensure_ascii=False)

        with open(mmd_file, "w", encoding="utf-8") as f:
            f.write(input_content)

        cmd = [
            "npx",
            "-y",
            "@mermaid-js/mermaid-cli",
            "-i",
            str(mmd_file),
            "-o",
            str(output_path),
            "-c",
            str(cfg_file),
            "-b",
            "transparent",
        ]

        print(f"Rendering Mermaid diagram with theme '{theme_data.get('theme')}'...")
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if res.returncode != 0:
            print(f"[ERROR] Mermaid CLI failed:\n{res.stderr}", file=sys.stderr)
            return False

    if postprocess and output_path.exists():
        _write_svg(output_path, output_path.read_text(encoding="utf-8"), theme_data, True)

    return True


def _recolor_drawio_xml(root: ET.Element, theme_data: dict) -> None:
    """Update draw.io cell styles with active theme colors.

    Semantic status fills (success/warning/danger) are preserved so
    state machines and timelines keep their meaning across themes.
    Font colors follow the final fill luminance so light nodes keep dark
    text even on dark themes (e.g. white boxes on Nebula Glass).
    """
    colors = theme_data.get("colors", {})
    p_pale = colors.get("primaryPale", "#EDF5FF")
    p_main = colors.get("primary", "#2C7BE5")
    p_dark = colors.get("primaryDark", "#1B5FC0")
    line_main = colors.get("line", p_main)
    txt_main = colors.get("text", "#1A1A2E")
    bg_main = colors.get("background", "#FAFCFF")
    border_main = colors.get("border", "#B8D4E8")
    status_fills = {
        (colors.get("success", "#27AE60") or "").lower(),
        (colors.get("warning", "#F39C12") or "").lower(),
        (colors.get("danger", "#E74C3C") or "").lower(),
        "#27ae60", "#f39c12", "#e74c3c", "#10b981", "#f59e0b", "#ef4444",
        "#78c2ad", "#ffc074", "#f38181", "#34d399", "#fbbf24", "#fb7185",
    }

    def _fill_of(style: str) -> str:
        match = re.search(r"fillColor=([^;]+)", style)
        return (match.group(1) if match else "").lower()

    for cell in root.iter("mxCell"):
        style = cell.get("style", "")
        if not style:
            continue

        # Recolor swimlanes / containers
        if "swimlane" in style:
            style = re.sub(r"fillColor=[^;]+", f"fillColor={bg_main}", style)
            style = re.sub(r"strokeColor=[^;]+", f"strokeColor={border_main}", style)
            style = re.sub(r"fontColor=[^;]+", f"fontColor={best_text_on(bg_main, txt_main)}", style)
        # Recolor accent shapes (inverted background) — keep status fills.
        elif "fontColor=#FFFFFF" in style or "fontColor=#ffffff" in style:
            if _fill_of(style) not in status_fills:
                style = re.sub(r"fillColor=[^;]+", f"fillColor={p_main}", style)
            style = re.sub(r"strokeColor=[^;]+", f"strokeColor={p_dark}", style)
        # Recolor standard shapes (keep semantic status fills)
        elif cell.get("vertex") == "1":
            if "fillColor=#FFFFFF" not in style and _fill_of(style) not in status_fills:
                style = re.sub(r"fillColor=[^;]+", f"fillColor={p_pale}", style)
                font_fill = p_pale
            else:
                font_fill = _fill_of(style) or p_pale
            style = re.sub(r"strokeColor=[^;]+", f"strokeColor={p_main}", style)
            style = re.sub(r"fontColor=[^;]+", f"fontColor={best_text_on(font_fill, txt_main)}", style)
        # Recolor connectors (theme line color, e.g. cyan on Nebula Glass)
        elif cell.get("edge") == "1":
            style = re.sub(r"strokeColor=[^;]+", f"strokeColor={line_main}", style)

        cell.set("style", style)


def _convert_drawio_to_svg(tree: ET.ElementTree, theme_data: dict) -> str:
    """Generate a clean, standalone SVG from draw.io mxGraph model."""
    root = tree.getroot()
    diagram = root.find("diagram")
    if diagram is None:
        return ""
    graph_model = diagram.find("mxGraphModel")
    if graph_model is None:
        return ""
    root_elem = graph_model.find("root")
    if root_elem is None:
        return ""

    page_w = int(graph_model.get("pageWidth", "1080"))
    page_h = int(graph_model.get("pageHeight", "420"))

    # Map cells by id
    cells = root_elem.findall("mxCell")
    cell_map = {c.get("id"): c for c in cells if c.get("id")}

    svg_elements: list[str] = []
    container_elements: list[str] = []  # swimlane boxes (bottom layer)
    chrome_elements: list[str] = []  # header bars, titles (above edges)
    edge_elements: list[str] = []   # connectors (above containers, below nodes)
    # Collect styles
    font_fam = theme_data.get("fontFamily", "sans-serif")
    text_color = theme_data.get("colors", {}).get("text", "#1A1A2E")

    def parse_style_map(s: str) -> dict[str, str]:
        res = {}
        for item in s.split(";"):
            if "=" in item:
                k, v = item.split("=", 1)
                res[k.strip()] = v.strip()
            elif item.strip():
                res[item.strip()] = "1"
        return res

    def get_absolute_geom(c: ET.Element) -> tuple[float, float, float, float]:
        geom = c.find("mxGeometry")
        if geom is None:
            return 0, 0, 0, 0
        x = float(geom.get("x", "0"))
        y = float(geom.get("y", "0"))
        w = float(geom.get("width", "0"))
        h = float(geom.get("height", "0"))

        parent_id = c.get("parent")
        while parent_id and parent_id not in ("0", "1"):
            p_cell = cell_map.get(parent_id)
            if p_cell is None:
                break
            p_geom = p_cell.find("mxGeometry")
            if p_geom is not None:
                x += float(p_geom.get("x", "0"))
                y += float(p_geom.get("y", "0"))
            parent_id = p_cell.get("parent")
        return x, y, w, h

    def get_absolute_origin(cell_id: str | None) -> tuple[float, float]:
        x, y = 0.0, 0.0
        parent_id = cell_id
        while parent_id and parent_id not in ("0", "1"):
            parent = cell_map.get(parent_id)
            if parent is None:
                break
            geometry = parent.find("mxGeometry")
            if geometry is not None:
                x += float(geometry.get("x", "0"))
                y += float(geometry.get("y", "0"))
            parent_id = parent.get("parent")
        return x, y

    # 1. Render Containers / Swimlanes first
    for cell in cells:
        if cell.get("vertex") != "1":
            continue
        st = parse_style_map(cell.get("style", ""))
        if "swimlane" in st:
            x, y, w, h = get_absolute_geom(cell)
            fill = st.get("fillColor", "#FAFCFF")
            stroke = st.get("strokeColor", "#B8D4E8")
            start_size = float(st.get("startSize", "26"))
            title = html.escape(cell.get("value", "") or "")
            rx_val = drawio_rect_radius(theme_data, st)
            arc = f"rx='{rx_val}' ry='{rx_val}'" if rx_val else ""

            # Container Box (bottom layer — edges must stay visible above it)
            container_elements.append(
                f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{fill}' stroke='{stroke}' stroke-width='1.5' {arc} />"
            )
            # Header Bar (chrome — kept above edges so titles stay readable)
            chrome_elements.append(
                f"<rect x='{x}' y='{y}' width='{w}' height='{start_size}' fill='{stroke}' opacity='0.12' />"
            )
            chrome_elements.append(
                f"<line x1='{x}' y1='{y + start_size}' x2='{x + w}' y2='{y + start_size}' stroke='{stroke}' stroke-width='1' />"
            )
            if title:
                chrome_elements.append(
                    f"<text x='{x + 12}' y='{y + start_size - 8}' font-family=\"{font_fam}\" font-size='12' font-weight='bold' fill='{text_color}'>{title}</text>"
                )

    # 2. Render Non-swimlane Vertices
    for cell in cells:
        if cell.get("vertex") != "1":
            continue
        st = parse_style_map(cell.get("style", ""))
        if "swimlane" in st:
            continue
        x, y, w, h = get_absolute_geom(cell)
        fill = st.get("fillColor", "#FFFFFF")
        stroke = st.get("strokeColor", "#2C7BE5")
        stroke_w = st.get("strokeWidth", "1.5")
        f_color = st.get("fontColor", best_text_on(fill, text_color))
        f_size = st.get("fontSize", "11")
        f_weight = "bold" if "fontStyle" in st and st["fontStyle"] == "1" else "normal"
        val = (cell.get("value", "") or "").replace("&#xa;", "\n")

        # Cylinder Shape
        if "shape=cylinder3" in cell.get("style", "") or "cylinder3" in st:
            r_h = 10
            svg_elements.append(
                f"<path d='M {x} {y + r_h} A {w/2} {r_h} 0 0 1 {x + w} {y + r_h} L {x + w} {y + h - r_h} A {w/2} {r_h} 0 0 1 {x} {y + h - r_h} Z' fill='{fill}' stroke='{stroke}' stroke-width='{stroke_w}' />"
            )
            svg_elements.append(
                f"<ellipse cx='{x + w/2}' cy='{y + r_h}' rx='{w/2}' ry='{r_h}' fill='{fill}' stroke='{stroke}' stroke-width='{stroke_w}' />"
            )
        # Standard Rect / Card
        else:
            rx_val = drawio_rect_radius(theme_data, st)
            rx = f"rx='{rx_val}' ry='{rx_val}'" if rx_val else ""
            filter_attr = ""
            effects = theme_data.get("effects", {})
            if effects.get("glowEnabled"):
                filter_attr = " filter='url(#theme-glow)'"
            elif effects.get("nodeShadowEnabled"):
                filter_attr = " filter='url(#theme-shadow)'"
            svg_elements.append(
                f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{fill}' stroke='{stroke}' stroke-width='{stroke_w}' {rx}{filter_attr} />"
            )

        # Text inside shape
        if val:
            lines = val.split("\n")
            line_h = float(f_size) * 1.35
            start_ty = y + (h - (len(lines) * line_h)) / 2 + float(f_size) * 0.85
            for i, line in enumerate(lines):
                cur_y = start_ty + i * line_h
                cx = x + w / 2
                escaped_line = html.escape(line)
                svg_elements.append(
                    f"<text x='{cx}' y='{cur_y}' text-anchor='middle' font-family=\"{font_fam}\" font-size='{f_size}' font-weight='{f_weight}' fill='{f_color}'>{escaped_line}</text>"
                )

    # 3. Render Connectors / Edges  (above containers, below nodes)
    vertex_obstacles = [
        get_absolute_geom(cell)
        for cell in cells
        if cell.get("vertex") == "1" and "swimlane" not in parse_style_map(cell.get("style", ""))
    ]
    for cell in cells:
        if cell.get("edge") != "1":
            continue
        st = parse_style_map(cell.get("style", ""))
        src_id = cell.get("source")
        tgt_id = cell.get("target")
        if not src_id or not tgt_id or src_id not in cell_map or tgt_id not in cell_map:
            continue

        sx, sy, sw, sh = get_absolute_geom(cell_map[src_id])
        tx, ty, tw, th = get_absolute_geom(cell_map[tgt_id])
        stroke = st.get("strokeColor", "#2C7BE5")
        stroke_w = st.get("strokeWidth", "1.5")

        source_geometry = (sx, sy, sw, sh)
        target_geometry = (tx, ty, tw, th)
        edge_style = cell.get("style", "")
        source_shape = node_shape((cell_map[src_id].get("style") or ""))
        target_shape = node_shape((cell_map[tgt_id].get("style") or ""))
        p1, p2 = edge_endpoints(source_geometry, target_geometry, edge_style)
        waypoints = get_edge_waypoints(cell)
        if waypoints:
            origin_x, origin_y = get_absolute_origin(cell.get("parent"))
            points = snap_edge_points(
                source_geometry,
                target_geometry,
                edge_style,
                [p1] + [(x + origin_x, y + origin_y) for x, y in waypoints] + [p2],
                source_shape,
                target_shape,
            )
        else:
            points = route_edge(
                source_geometry, target_geometry, edge_style, vertex_obstacles, source_shape=source_shape, target_shape=target_shape
            )

        path_d = " ".join(
            [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
            + [f"L {x:.1f} {y:.1f}" for x, y in points[1:]]
        )

        previous, current = points[-2], points[-1]
        if abs(current[0] - previous[0]) >= abs(current[1] - previous[1]):
            arrow_dir = "right" if current[0] > previous[0] else "left"
        else:
            arrow_dir = "down" if current[1] > previous[1] else "up"

        # Edge path (no fill, so it never covers boxes visually)
        edge_elements.append(
            f"<path d='{path_d}' fill='none' stroke='{stroke}' stroke-width='{stroke_w}' />"
        )

        # Arrowhead at the (snapped) path end, stabbing along travel direction
        ax, ay = current[0], current[1]
        sz = 5
        if arrow_dir == "right":
            arrow_pts = f"{ax:.1f},{ay:.1f} {ax-sz*1.5:.1f},{ay-sz:.1f} {ax-sz*1.5:.1f},{ay+sz:.1f}"
        elif arrow_dir == "left":
            arrow_pts = f"{ax:.1f},{ay:.1f} {ax+sz*1.5:.1f},{ay-sz:.1f} {ax+sz*1.5:.1f},{ay+sz:.1f}"
        elif arrow_dir == "down":
            arrow_pts = f"{ax:.1f},{ay:.1f} {ax-sz:.1f},{ay-sz*1.5:.1f} {ax+sz:.1f},{ay-sz*1.5:.1f}"
        else:
            arrow_pts = f"{ax:.1f},{ay:.1f} {ax-sz:.1f},{ay+sz*1.5:.1f} {ax+sz:.1f},{ay+sz*1.5:.1f}"
        edge_elements.append(f"<polygon points='{arrow_pts}' fill='{stroke}' />")

    # Wrap in SVG — z-order: container boxes < edges < header chrome < nodes < text
    # (edges above container fills so connectors stay visible; nodes above edges)
    all_elements = container_elements + edge_elements + chrome_elements + svg_elements
    elements_markup = "\n  ".join(all_elements)
    filter_defs = build_filter_defs(theme_data.get("effects", {}))
    defs_block = filter_defs if filter_defs else "<defs/>"
    svg_out = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {page_w} {page_h}" width="{page_w}" height="{page_h}" style="background-color: transparent;">
  {defs_block}
  {elements_markup}
</svg>"""
    return svg_out


def render_drawio(
    input_path: Path,
    output_path: Path,
    theme_data: dict,
    layout: str,
    postprocess: bool = True,
) -> bool:
    """Recolor draw.io XML and export to standalone SVG."""
    try:
        tree = ET.parse(input_path)
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse draw.io XML: {e}", file=sys.stderr)
        return False

    root = tree.getroot()
    _recolor_drawio_xml(root, theme_data)

    svg_content = _convert_drawio_to_svg(tree, theme_data)
    if not svg_content:
        print("[ERROR] Failed to convert draw.io model to SVG", file=sys.stderr)
        return False

    _write_svg(output_path, svg_content, theme_data, postprocess)

    print(f"Rendered draw.io diagram to '{output_path}' with theme '{theme_data.get('theme')}'")
    return True


def _advisory_note(data: dict, layout: str) -> str:
    """Return a usage note for JSON types with known text limitations."""
    kind = data.get("type")
    if kind == "funnel" and layout == "col3":
        if any("value" in level for level in data.get("levels", [])):
            return (
                "value pills share a narrow gutter on col3. "
                "Prefer label-only levels and put figures in slide text."
            )
    return ""


def render_json_diagram_from_data(
    data: dict,
    output_path: Path,
    theme_data: dict,
    layout: str,
) -> bool:
    """Render a validated JSON diagram definition to standalone SVG."""
    try:
        svg_content = render_diagram(data, theme_data, layout)
    except (TypeError, ValueError, KeyError) as error:
        print(f"[ERROR] JSON diagram validation failed: {error}", file=sys.stderr)
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content, encoding="utf-8")
    print(f"Rendered JSON diagram to '{output_path}' with theme '{theme_data.get('theme')}'")
    note = _advisory_note(data, layout)
    if note:
        print(f"[NOTE] {note}")
    return True


def render_json_diagram(
    input_path: Path,
    output_path: Path,
    theme_data: dict,
    layout: str,
) -> bool:
    """Load and render a JSON diagram, reporting syntax location on failure."""
    try:
        with input_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        print(f"[ERROR] JSON parse error in {input_path} at line {error.lineno}: {error.msg}", file=sys.stderr)
        return False
    except OSError as error:
        print(f"[ERROR] Failed to read JSON file {input_path}: {error}", file=sys.stderr)
        return False
    return render_json_diagram_from_data(data, output_path, theme_data, layout)


def main():
    parser = argparse.ArgumentParser(description="Render Mermaid or draw.io diagram to slide-optimized SVG.")
    parser.add_argument("-i", "--input", type=Path, help="Input .mmd or .drawio file")
    parser.add_argument("--code", type=str, help="Direct Mermaid diagram string")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Target output .svg path")
    parser.add_argument(
        "--theme",
        default="azure-clarity",
        choices=["azure-clarity", "crimson-clarity", "prism-edge", "nebula-glass", "warm-sunnyday", "slate-minimal"],
        help="Target presentation theme (default: azure-clarity)",
    )
    parser.add_argument(
        "--layout",
        default="full",
        choices=["full", "col2", "asym", "col3"],
        help="Target slide layout (default: full)",
    )
    parser.add_argument("--no-validate", action="store_true", help="Skip post-render validation")
    parser.add_argument("--no-postprocess", action="store_true", help="Skip SVG theme post-processing")

    args = parser.parse_args()
    theme_data = load_theme_style(args.theme)
    postprocess = not args.no_postprocess

    success = False
    if args.code:
        success = render_mermaid(args.code, args.output, theme_data, args.layout, postprocess)
    elif args.input:
        if not args.input.exists():
            print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        suffix = args.input.suffix.lower()
        if suffix in (".mmd", ".mermaid"):
            with open(args.input, "r", encoding="utf-8") as f:
                content = f.read()
            success = render_mermaid(content, args.output, theme_data, args.layout, postprocess)
        elif suffix in (".drawio", ".xml"):
            success = render_drawio(args.input, args.output, theme_data, args.layout, postprocess)
        elif suffix == ".json":
            success = render_json_diagram(args.input, args.output, theme_data, args.layout)
        else:
            print(f"[ERROR] Unknown input format '{suffix}'. Expected .mmd, .drawio, or .json", file=sys.stderr)
            sys.exit(1)
    else:
        print("[ERROR] Either --input or --code must be specified", file=sys.stderr)
        sys.exit(1)

    if not success:
        print("[ERROR] Rendering failed", file=sys.stderr)
        sys.exit(1)

    # Automated Validation
    if not args.no_validate and VALIDATOR_PATH.exists():
        print("Running automated layout validation...")
        val_res = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(args.output), "--layout", args.layout],
            text=True,
        )
        if val_res.returncode != 0:
            print("[WARN] Diagram passed rendering but raised layout validation warnings/errors.")

    print(f"[SUCCESS] Slide diagram ready: {args.output}")


if __name__ == "__main__":
    main()
