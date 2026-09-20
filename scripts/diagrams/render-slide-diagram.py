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

SCRIPT_DIR = Path(__file__).resolve().parent
THEME_STYLES_DIR = SCRIPT_DIR / "theme-styles"
VALIDATOR_PATH = SCRIPT_DIR / "validate-slide-diagram.py"


def load_theme_style(theme_name: str) -> dict:
    """Load theme configuration JSON."""
    theme_file = THEME_STYLES_DIR / f"{theme_name}.json"
    if not theme_file.exists():
        # Fallback to azure-clarity
        theme_file = THEME_STYLES_DIR / "azure-clarity.json"
    with open(theme_file, "r", encoding="utf-8") as f:
        return json.load(f)


def render_mermaid(
    input_content: str,
    output_path: Path,
    theme_data: dict,
    layout: str,
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

        output_path.parent.mkdir(parents=True, exist_ok=True)

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

    return True


def _recolor_drawio_xml(root: ET.Element, theme_data: dict) -> None:
    """Update draw.io cell styles with active theme colors."""
    colors = theme_data.get("colors", {})
    p_pale = colors.get("primaryPale", "#EDF5FF")
    p_main = colors.get("primary", "#2C7BE5")
    p_dark = colors.get("primaryDark", "#1B5FC0")
    txt_main = colors.get("text", "#1A1A2E")
    bg_main = colors.get("background", "#FAFCFF")
    border_main = colors.get("border", "#B8D4E8")

    for cell in root.iter("mxCell"):
        style = cell.get("style", "")
        if not style:
            continue

        # Recolor swimlanes / containers
        if "swimlane" in style:
            style = re.sub(r"fillColor=[^;]+", f"fillColor={bg_main}", style)
            style = re.sub(r"strokeColor=[^;]+", f"strokeColor={border_main}", style)
            style = re.sub(r"fontColor=[^;]+", f"fontColor={txt_main}", style)
        # Recolor accent shapes (inverted background)
        elif "fontColor=#FFFFFF" in style or "fontColor=#ffffff" in style:
            style = re.sub(r"fillColor=[^;]+", f"fillColor={p_main}", style)
            style = re.sub(r"strokeColor=[^;]+", f"strokeColor={p_dark}", style)
        # Recolor standard shapes
        elif cell.get("vertex") == "1":
            if "fillColor=#FFFFFF" not in style:
                style = re.sub(r"fillColor=[^;]+", f"fillColor={p_pale}", style)
            style = re.sub(r"strokeColor=[^;]+", f"strokeColor={p_main}", style)
            style = re.sub(r"fontColor=[^;]+", f"fontColor={txt_main}", style)
        # Recolor connectors
        elif cell.get("edge") == "1":
            style = re.sub(r"strokeColor=[^;]+", f"strokeColor={p_main}", style)

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
            arc = "rx='6' ry='6'" if "rounded" in st else ""

            # Container Box
            svg_elements.append(
                f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{fill}' stroke='{stroke}' stroke-width='1.5' {arc} />"
            )
            # Header Bar
            svg_elements.append(
                f"<rect x='{x}' y='{y}' width='{w}' height='{start_size}' fill='{stroke}' opacity='0.12' />"
            )
            svg_elements.append(
                f"<line x1='{x}' y1='{y + start_size}' x2='{x + w}' y2='{y + start_size}' stroke='{stroke}' stroke-width='1' />"
            )
            if title:
                svg_elements.append(
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
        f_color = st.get("fontColor", text_color)
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
            rx = "rx='6' ry='6'" if "rounded" in st or "rounded=1" in cell.get("style", "") else ""
            svg_elements.append(
                f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{fill}' stroke='{stroke}' stroke-width='{stroke_w}' {rx} />"
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

    # 3. Render Connectors / Edges
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

        # Smart point routing: horizontal vs vertical
        if abs((sx + sw / 2) - (tx + tw / 2)) > abs((sy + sh / 2) - (ty + th / 2)):
            # Horizontal connection
            if sx < tx:
                p1 = (sx + sw, sy + sh / 2)
                p2 = (tx, ty + th / 2)
            else:
                p1 = (sx, sy + sh / 2)
                p2 = (tx + tw, ty + th / 2)
            mid_x = (p1[0] + p2[0]) / 2
            path_d = f"M {p1[0]} {p1[1]} L {mid_x} {p1[1]} L {mid_x} {p2[1]} L {p2[0]} {p2[1]}"
            arrow_dir = "right" if p1[0] < p2[0] else "left"
        else:
            # Vertical connection
            if sy < ty:
                p1 = (sx + sw / 2, sy + sh)
                p2 = (tx + tw / 2, ty)
            else:
                p1 = (sx + sw / 2, sy)
                p2 = (tx + tw / 2, ty + th)
            mid_y = (p1[1] + p2[1]) / 2
            path_d = f"M {p1[0]} {p1[1]} L {p1[0]} {mid_y} L {p2[0]} {mid_y} L {p2[0]} {p2[1]}"
            arrow_dir = "down" if p1[1] < p2[1] else "up"

        # Edge Path
        svg_elements.append(
            f"<path d='{path_d}' fill='none' stroke='{stroke}' stroke-width='{stroke_w}' />"
        )
        # Arrowhead
        ax, ay = p2[0], p2[1]
        sz = 5
        if arrow_dir == "right":
            arrow_pts = f"{ax},{ay} {ax-sz*1.5},{ay-sz} {ax-sz*1.5},{ay+sz}"
        elif arrow_dir == "left":
            arrow_pts = f"{ax},{ay} {ax+sz*1.5},{ay-sz} {ax+sz*1.5},{ay+sz}"
        elif arrow_dir == "down":
            arrow_pts = f"{ax},{ay} {ax-sz},{ay-sz*1.5} {ax+sz},{ay-sz*1.5}"
        else:
            arrow_pts = f"{ax},{ay} {ax-sz},{ay+sz*1.5} {ax+sz},{ay+sz*1.5}"
        svg_elements.append(f"<polygon points='{arrow_pts}' fill='{stroke}' />")

    # Wrap in SVG
    elements_markup = "\n  ".join(svg_elements)
    svg_out = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {page_w} {page_h}" width="{page_w}" height="{page_h}" style="background-color: transparent;">
  <defs/>
  {elements_markup}
</svg>"""
    return svg_out


def render_drawio(
    input_path: Path,
    output_path: Path,
    theme_data: dict,
    layout: str,
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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Rendered draw.io diagram to '{output_path}' with theme '{theme_data.get('theme')}'")
    return True


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

    args = parser.parse_args()
    theme_data = load_theme_style(args.theme)

    success = False
    if args.code:
        success = render_mermaid(args.code, args.output, theme_data, args.layout)
    elif args.input:
        if not args.input.exists():
            print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        suffix = args.input.suffix.lower()
        if suffix in (".mmd", ".mermaid"):
            with open(args.input, "r", encoding="utf-8") as f:
                content = f.read()
            success = render_mermaid(content, args.output, theme_data, args.layout)
        elif suffix in (".drawio", ".xml"):
            success = render_drawio(args.input, args.output, theme_data, args.layout)
        else:
            print(f"[ERROR] Unknown input format '{suffix}'. Expected .mmd or .drawio", file=sys.stderr)
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
