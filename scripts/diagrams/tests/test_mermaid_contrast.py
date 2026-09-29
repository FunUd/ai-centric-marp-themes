"""Mermaid Gantt/mindmap contrast guards (WCAG text 4.5:1, graphical 3:1).

Regression for `new-diagrams-showcase` findings:
- Gantt active bar (「設計」) was white fill + pale stroke on a near-white
  canvas (1.0:1) — invisible except floating dark text.
- Mindmap pastel edges were 1.1-2.8:1 vs the canvas (invisible connectors)
  and several section fills were 4.1-4.4:1 vs dark ink (thin CJK washes out).

`render-slide-diagram.py` now pins Gantt task borders via
`theme-styles/*.json::mermaid.themeVariables` AND repairs any remaining
failures in `svg_theme_postprocessor` (`_fix_gantt_contrast`,
`_fix_mindmap_contrast`), so future Mermaid defaults cannot regress this.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

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


tokens = load_module("design_tokens_mermaid_contrast", "design_tokens.py")
post = load_module("postprocessor_mermaid_contrast", "svg_theme_postprocessor.py")

THEMES = (
    "azure-clarity",
    "crimson-clarity",
    "prism-edge",
    "nebula-glass",
    "warm-sunnyday",
    "slate-minimal",
)


def _norm(color: str | None) -> str | None:
    return tokens.normalize_color(color)


def _ratio(first: str, second: str) -> float:
    return tokens.contrast_ratio(first, second)


# --- token helpers -----------------------------------------------------------


def test_normalize_color_handles_mermaid_outputs() -> None:
    assert tokens.normalize_color("#fff") == "#FFFFFF"
    assert tokens.normalize_color("white") == "#FFFFFF"
    assert tokens.normalize_color("lightgrey") == "#D3D3D3"
    assert tokens.normalize_color("grey") == "#808080"
    assert tokens.normalize_color("hsl(213.33, 100%, 100%)") == "#FFFFFF"
    assert tokens.normalize_color("transparent") is None
    assert tokens.normalize_color("var(--x)") is None
    assert tokens.normalize_color("#zzzzzz") is None


def test_graphical_ink_clears_non_text_floor_on_every_theme() -> None:
    for theme in THEMES:
        data = tokens.load_design_tokens(theme)
        bg = tokens.theme_context(data)["background"]
        ink = tokens.graphical_ink(data, 3.0)
        assert _ratio(ink, bg) >= 3.0, f"{theme} ink {ink} vs {bg}"


def test_soften_mindmap_fill_keeps_hue_lifts_dark_text() -> None:
    # Saturated azure branch fill softens to a premium pastel with the same
    # hue family, and dark ink only gains contrast (6.0 -> 8+:1).
    before = "#489BFF"
    after = tokens.soften_mindmap_fill(before, "#FAFCFF")
    assert after and after != before
    assert _ratio("#1A1A2E", after) > _ratio("#1A1A2E", before)
    assert _ratio("#1A1A2E", after) >= 4.5
    # Dark canvases keep deep fills (white ink already passes).
    assert tokens.soften_mindmap_fill("#0B0000", "#040712") == "#0B0000"


def test_gantt_theme_variables_pin_visible_borders() -> None:
    import json

    for theme in THEMES:
        path = SCRIPT_DIR / "theme-styles" / f"{theme}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        tv = data["mermaid"]["themeVariables"]
        bg = data["colors"]["background"]
        for key in ("taskBorderColor", "activeTaskBorderColor"):
            assert key in tv, f"{theme} missing {key}"
            assert _ratio(tv[key], bg) >= 3.0, f"{theme} {key} {tv[key]} vs {bg}"


# --- postprocessor unit guards (offline, no npx) ------------------------------


def _gantt_fixture(active_fill: str = "hsl(213, 100%, 100%)", active_stroke: str = "#EDF5FF") -> str:
    return (
        '<svg aria-roledescription="gantt"><style>'
        f".active0{{fill:{active_fill};stroke:{active_stroke};}}"
        ".task0{fill:#EDF5FF;stroke:#2C7BE5;}"
        ".taskText0{fill:#1A1A2E;}"
        "</style></svg>"
    )


def test_fix_gantt_lifts_invisible_active_border() -> None:
    data = tokens.load_design_tokens("azure-clarity")
    out = post._fix_gantt_contrast(_gantt_fixture(), data)
    m = re.search(r"\.active0\{([^}]*)\}", out)
    assert m, out
    stroke = re.search(r"stroke:([^;!]+)", m.group(1))
    assert stroke
    bg = tokens.theme_context(data)["background"]
    assert _ratio(_norm(stroke.group(1)), bg) >= 3.0


def test_fix_gantt_repairs_done_text_on_dark_theme() -> None:
    fixture = (
        '<svg aria-roledescription="gantt"><style>'
        ".done0{stroke:grey;fill:lightgrey;}"
        ".doneText0{fill:#F5F7FB;}"
        ".active0{fill:#152438;stroke:#22D3EE;}"
        "</style></svg>"
    )
    data = tokens.load_design_tokens("nebula-glass")
    out = post._fix_gantt_contrast(fixture, data)
    m = re.search(r"\.doneText0\{([^}]*)\}", out)
    assert m, out
    fill = re.search(r"fill:([^;!]+)", m.group(1))
    assert fill
    # lightgrey done fill needs dark ink, not near-white.
    assert _ratio(_norm(fill.group(1)), "#D3D3D3") >= 4.5


def _mindmap_fixture(fill: str = "hsl(30, 100%, 73%)", edge: str = "hsl(30, 100%, 73%)", ink: str = "#4A4A4A") -> str:
    return (
        '<svg class="mindmapDiagram"><style>'
        f".section-0 rect{{fill:{fill};}}"
        f".section-0 text{{fill:{ink};}}"
        f".section-0 span{{color:{ink};}}"
        f".section-edge-0{{stroke:{edge};}}"
        "</style></svg>"
    )


def test_fix_mindmap_lifts_pale_edge_to_graphical_floor() -> None:
    data = tokens.load_design_tokens("warm-sunnyday")
    bg = tokens.theme_context(data)["background"]
    assert _ratio(_norm("hsl(30, 100%, 73%)"), bg) < 3.0
    out = post._fix_mindmap_contrast(_mindmap_fixture(), data)
    m = re.search(r"\.section-edge-0\{[^}]*stroke:([^;!]+)", out)
    assert m, out
    assert _ratio(_norm(m.group(1)), bg) >= 3.0


def test_fix_mindmap_repairs_thin_ink_to_text_floor() -> None:
    # slate sec0 pair was 4.1:1 with theme ink; postprocessor must reach 4.5.
    data = tokens.load_design_tokens("slate-minimal")
    fixture = _mindmap_fixture(fill="hsl(214.29, 31.8%, 66.37%)", edge="hsl(214.29, 31.8%, 66.37%)", ink="#334155")
    assert _ratio("#334155", _norm("hsl(214.29, 31.8%, 66.37%)")) < 4.5
    out = post._fix_mindmap_contrast(fixture, data)
    m = re.search(r"\.section-0 span\{[^}]*color:([^;!]+)", out)
    assert m, out
    # Either the ink darkened or the fill lightened — but the pair must pass.
    fill_m = re.search(r"\.section-0 rect\{[^}]*fill:([^;!]+)", out)
    assert fill_m, out
    assert _ratio(_norm(m.group(1)), _norm(fill_m.group(1))) >= 4.5


def test_fix_mindmap_adds_passing_node_boundary() -> None:
    # Pale fills float borderless on light canvases; the postprocessor pins a
    # 1.5px node stroke in the passing edge hue so each branch keeps a shape.
    data = tokens.load_design_tokens("azure-clarity")
    bg = tokens.theme_context(data)["background"]
    out = post._fix_mindmap_contrast(_mindmap_fixture(fill="#489BFF", edge="#489BFF"), data)
    m = re.search(r"\.section-0 rect\{([^}]*)\}", out)
    assert m and "stroke:" in m.group(1), out
    stroke = re.search(r"stroke:([^;!]+)", m.group(1))
    assert stroke and _ratio(_norm(stroke.group(1)), bg) >= 3.0


def test_fix_mindmap_hides_brown_underlines() -> None:
    # Mermaid's per-node `<line class="node-line-">` ships in clashing
    # rainbow hues (brown rgb(182,99,0) under blue fills); it duplicates the
    # node border, so the postprocessor hides it without touching geometry.
    data = tokens.load_design_tokens("azure-clarity")
    fixture = (
        '<svg class="mindmapDiagram"><style>'
        ".section-0 rect{fill:#94BEF0;}"
        ".section-0 line{stroke:rgb(182.5, 99.5454545456, 0);stroke-width:3;}"
        ".section-edge-0{stroke:#2E8DFF;}"
        "</style></svg>"
    )
    out = post._fix_mindmap_contrast(fixture, data)
    m = re.search(r"\.section-0 line\{([^}]*)\}", out)
    assert m, out
    assert "stroke:none" in m.group(1).replace(" ", "")
    # Connectors are never matched by the underline rule.
    assert "#2E8DFF" in out


# --- full-pipeline integration (needs npx + mermaid-cli) ----------------------


def _render(template: str, theme: str, out_dir: Path) -> Path:
    src = SCRIPT_DIR / "templates" / template
    out = out_dir / f"{Path(template).stem}-{theme}.svg"
    res = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "render-slide-diagram.py"),
            "-i",
            str(src),
            "-o",
            str(out),
            "--theme",
            theme,
            "--layout",
            "full",
            "--no-validate",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    return out


def _style_of(svg_path: Path) -> str:
    text = svg_path.read_text(encoding="utf-8")
    m = re.search(r"<style>(.*?)</style>", text, re.DOTALL)
    assert m, svg_path
    return m.group(1)


def test_gantt_bars_and_text_clear_floors_every_theme() -> None:
    try:
        import shutil

        if shutil.which("npx") is None and shutil.which("npx.cmd") is None:
            import pytest

            pytest.skip("npx unavailable")
    except ImportError:
        pass
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        for theme in THEMES:
            data = tokens.load_design_tokens(theme)
            bg = tokens.theme_context(data)["background"]
            style = _style_of(_render("mermaid/gantt-milestone.mmd", theme, out_dir))
            # Active + task families: at least the boundary must clear 3:1,
            # inside text must clear 4.5:1 vs its own fill.
            for family, text_cls in (("active", "activeText"), ("task", "taskText")):
                fill_m = re.search(rf"\.{family}0[^{{]*\{{[^}}]*fill:([^;!]+)", style)
                stroke_m = re.search(rf"\.{family}0[^{{]*\{{[^}}]*stroke:([^;!]+)", style)
                assert fill_m and stroke_m, f"{theme} {family} rule missing"
                fill, stroke = _norm(fill_m.group(1)), _norm(stroke_m.group(1))
                assert max(_ratio(fill, bg), _ratio(stroke, bg)) >= 3.0, (
                    f"{theme} {family} invisible: fill {fill} stroke {stroke} vs {bg}"
                )
                text_m = re.search(rf"\.{text_cls}0[^{{]*\{{[^}}]*fill:([^;!]+)", style)
                if text_m:
                    assert _ratio(_norm(text_m.group(1)), fill) >= 4.5, (
                        f"{theme} {family} text {text_m.group(1)} on {fill}"
                    )


def test_mindmap_text_and_edges_clear_floors_every_theme() -> None:
    try:
        import shutil

        if shutil.which("npx") is None and shutil.which("npx.cmd") is None:
            import pytest

            pytest.skip("npx unavailable")
    except ImportError:
        pass
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        for theme in THEMES:
            data = tokens.load_design_tokens(theme)
            bg = tokens.theme_context(data)["background"]
            text = _style_of(_render("mermaid/mindmap-compact.mmd", theme, out_dir))
            fills: dict[str, str] = {}
            for m in re.finditer(r"\.section-(-?\d+)[^{]*\{[^}]*fill:([^;!]+)", text):
                normed = _norm(m.group(2))
                if normed and m.group(1) not in fills:
                    fills[m.group(1)] = normed
            assert fills, theme
            for sec, fill in fills.items():
                if sec == "-1":
                    continue  # root shares the palette; branches carry the load
                ink_m = re.search(r"\.section-" + re.escape(sec) + r"\s+span\{[^}]*color:([^;!]+)", text)
                if ink_m:
                    assert _ratio(_norm(ink_m.group(1)), fill) >= 4.5, (
                        f"{theme} sec{sec} ink {ink_m.group(1)} on {fill}"
                    )
                edge_m = re.search(r"\.section-edge-" + re.escape(sec) + r"\{[^}]*stroke:([^;!]+)", text)
                if edge_m:
                    assert _ratio(_norm(edge_m.group(1)), bg) >= 3.0, f"{theme} sec{sec} edge {edge_m.group(1)} vs {bg}"
                node_m = re.search(
                    r"\.section-" + re.escape(sec) + r"\s+(?:rect|path|circle|polygon)[^{]*\{([^}]*)\}",
                    text,
                )
                if node_m:
                    stroke_m = re.search(r"stroke:([^;!]+)", node_m.group(1))
                    assert stroke_m, f"{theme} sec{sec} node missing boundary stroke"
                    assert _ratio(_norm(stroke_m.group(1)), bg) >= 3.0, (
                        f"{theme} sec{sec} node stroke {stroke_m.group(1)} vs {bg}"
                    )
            # Stray per-node underlines (brown/rainbow) must stay hidden on
            # every theme; connectors (`section-edge-*`) are excluded by the
            # required whitespace before `line`. A zero-width line is already
            # invisible (Nebula root emits `stroke-width:0`), so accept it.
            for line_m in re.finditer(r"\.section-(?:-?\d+|root)\s+line\{([^}]*)\}", text):
                body = line_m.group(1).replace(" ", "")
                assert ("stroke:none" in body) or ("stroke-width:0" in body), (
                    f"{theme} underline not hidden: {line_m.group(0)[:80]}"
                )
