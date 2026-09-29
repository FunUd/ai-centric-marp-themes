"""test_embed_guards.py — Recurrence guards for the new-diagram quality fixes.

Locks in three lessons so they cannot silently regress:

1. Mermaid/draw.io SVGs keep their native viewBox ratio: embedding a
   narrow-native SVG at the 1050px JSON default overflows vertically
   (ER at 1050px rendered ~3700px tall). Every such template declares a
   fitting full-slide width in ``check-templates.py::RECOMMENDED_EMBED_WIDTH``
   (height gate enforced there, in CI with npx); this file checks the
   manifest side plus the catalog mirror without needing npx.
2. Data-ink digits must stay readable: matrix scores >= 20px,
   100%-stacked segment labels >= 14px, hbar labels/values >= 15px.
3. The Gantt template must keep enough gridlines to read: ``axisFormat``
   plus a bounded dated-entry count and a milestone.
4. Showcase decks themselves must fit: every SVG embed in ``slides/``
   is scaled by its committed viewBox and must stay within the canvas.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ROOT_DIR = SCRIPT_DIR.parent.parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


models = load_module("diagram_models", "diagram_models.py")
tokens = load_module("design_tokens", "design_tokens.py")
renderer = load_module("svg_diagram_renderer", "svg_diagram_renderer.py")
checker = load_module("check_templates", "check-templates.py")

CATALOG_PATH = ROOT_DIR / "skills" / "marp-diagram-creator" / "references" / "template-catalog.md"

CANVAS_MAX_W, CANVAS_MAX_H = 1120.0, 460.0


def _ctx(theme: str = "azure-clarity") -> dict:
    return tokens.theme_context(tokens.load_design_tokens(theme))


def _font_sizes(svg: str) -> list[tuple[str, float]]:
    """(text content, font-size) for every <text> element."""
    root = ET.fromstring(svg)
    found = []
    for elem in root.iter():
        if elem.tag.split("}")[-1] != "text":
            continue
        size = elem.get("font-size")
        if size is None:
            continue
        try:
            found.append(("".join(elem.itertext()).strip(), float(size)))
        except ValueError:
            continue
    return found


# --- 1. embed-width manifest (stdlib side; height gate runs in check-templates.py) ---


def test_embed_map_covers_every_mermaid_and_drawio_template() -> None:
    on_disk = checker.templates_on_disk()
    missing = [
        name for name in sorted(on_disk)
        if checker._engine_of(name) in ("mermaid", "drawio")
        and name not in checker.RECOMMENDED_EMBED_WIDTH
    ]
    assert missing == []


def test_embed_map_widths_are_within_canvas() -> None:
    for name, width in checker.RECOMMENDED_EMBED_WIDTH.items():
        assert 0 < width <= CANVAS_MAX_W, f"{name}: {width}"


def test_catalog_embeds_mirror_the_map() -> None:
    """template-catalog.md Embed column must state each mapped width."""
    catalog = CATALOG_PATH.read_text(encoding="utf-8")
    rows = [line for line in catalog.splitlines() if line.startswith("| `")]
    by_file = {}
    for row in rows:
        match = re.match(r"\|\s*`([^`]+)`", row)
        if match:
            by_file[match.group(1)] = row
    missing = []
    for rel, width in checker.RECOMMENDED_EMBED_WIDTH.items():
        row = by_file.get(Path(rel).name)
        if row is None or f"{width}px" not in row:
            missing.append(rel)
    assert missing == [], f"catalog Embed column out of sync: {missing}"


# --- 2. data-ink font floors ---


def test_matrix_scores_stay_large() -> None:
    raw = (SCRIPT_DIR / "templates" / "concepts" / "tech-selection-matrix.json").read_text(encoding="utf-8")
    import json

    svg = renderer.render_diagram(models.parse_diagram_data(json.loads(raw)), _ctx(), "full")
    digits = [(text, size) for text, size in _font_sizes(svg) if re.fullmatch(r"[0-5]", text)]
    large = [size for _, size in digits if size >= 24]
    assert len(large) == 12, f"expected 12 large score cells, got {len(large)}: {digits}"


def test_stacked100_segment_labels_stay_readable() -> None:
    raw = (SCRIPT_DIR / "templates" / "charts" / "channel-100-bar.json").read_text(encoding="utf-8")
    import json

    svg = renderer.render_diagram(models.parse_diagram_data(json.loads(raw)), _ctx(), "full")
    segments = [(text, size) for text, size in _font_sizes(svg) if re.fullmatch(r"\d+%", text)]
    assert segments, "no segment labels found"
    assert all(size >= 16 for _, size in segments), segments


def test_hbar_labels_and_values_stay_readable() -> None:
    raw = (SCRIPT_DIR / "templates" / "charts" / "task-hbar.json").read_text(encoding="utf-8")
    import json

    svg = renderer.render_diagram(models.parse_diagram_data(json.loads(raw)), _ctx(), "full")
    bold = [(text, size) for text, size in _font_sizes(svg) if _is_bold_text(svg, text)]
    assert bold, "no bold labels found"
    assert all(size >= 15 for _, size in bold), bold


def _is_bold_text(svg: str, content: str) -> bool:
    root = ET.fromstring(svg)
    for elem in root.iter():
        if elem.tag.split("}")[-1] != "text":
            continue
        if "".join(elem.itertext()).strip() == content and elem.get("font-weight") == "bold":
            return True
    return False


# --- 3. gantt density ---


def test_gantt_keeps_dense_gridlines() -> None:
    text = (SCRIPT_DIR / "templates" / "mermaid" / "gantt-milestone.mmd").read_text(encoding="utf-8")
    assert "axisFormat" in text, "gantt lost its dense date axis"
    dated = [line for line in text.splitlines() if re.match(r"^ {8}\S", line) and "," in line]
    assert 7 <= len(dated) <= 9, f"gantt dated entries out of range: {len(dated)}"
    assert "milestone" in text, "gantt lost its milestone marker"


# --- 4. decks fit: every committed SVG embed stays within the canvas ---

EMBED_RE = re.compile(r"!\[(?:(width|height):(\d+)px[^\]]*)?\]\(([^)]+)\)")


def _svg_viewbox(svg_path: Path) -> tuple[float, float]:
    root = ET.parse(svg_path).getroot()
    view_box = root.get("viewBox", "")
    parts = [p for p in re.split(r"[,\s]+", view_box.strip()) if p]
    assert len(parts) == 4, f"{svg_path.name}: bad viewBox {view_box!r}"
    return float(parts[2]), float(parts[3])


def test_all_deck_diagram_embeds_fit_canvas() -> None:
    slides_dir = ROOT_DIR / "slides"
    assert slides_dir.is_dir()
    violations = []
    checked = 0
    for md_path in sorted(slides_dir.rglob("*.md")):
        for match in EMBED_RE.finditer(md_path.read_text(encoding="utf-8")):
            dim, value, target = match.group(1), match.group(2), match.group(3)
            svg_path = (md_path.parent / target.split("#")[0]).resolve()
            if svg_path.suffix.lower() != ".svg" or not svg_path.is_file():
                continue
            checked += 1
            vb_w, vb_h = _svg_viewbox(svg_path)
            if dim == "height":
                scaled_h = float(value)
            elif dim == "width":
                scaled_h = vb_h / vb_w * float(value)
            else:
                scaled_h = vb_h
            if scaled_h > CANVAS_MAX_H:
                violations.append(f"{md_path.name}: {target} -> {scaled_h:.0f}px tall")
    assert violations == [], f"deck diagrams overflow the canvas: {violations}"
