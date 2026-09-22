from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_modules():
    for name, filename in [
        ("design_tokens", "design_tokens.py"),
        ("diagram_models", "diagram_models.py"),
        ("svg_filters", "svg_filters.py"),
        ("svg_diagram_renderer", "svg_diagram_renderer.py"),
    ]:
        spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules["diagram_models"], sys.modules["svg_diagram_renderer"], sys.modules["design_tokens"]


models, renderer, tokens = load_modules()


def _ctx():
    return tokens.theme_context(tokens.load_design_tokens("prism-edge"))


def _rects(svg: str) -> list[tuple[float, float, float, float]]:
    return [
        (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
        for m in re.finditer(r"<rect[^>]*x=\"([\d.]+)\" y=\"([\d.]+)\" width=\"([\d.]+)\" height=\"([\d.]+)\"", svg)
    ]


def test_chart_legend_sits_next_to_chart() -> None:
    data = models.parse_diagram_data(
        {"type": "pie", "layout": "full", "items": [{"label": "A", "value": 45}, {"label": "B", "value": 30}, {"label": "C", "value": 25}]}
    )
    svg = renderer.render_diagram(dict(data), tokens.load_design_tokens("prism-edge"), "full")
    width, height = data["width"], data["height"]
    cx, cy = width * 0.32, height * renderer.CHART_CY_FULL
    radius = min(height * renderer.CHART_R_FULL, width * 0.23)
    legend = [r for r in _rects(svg) if r[2] == 12 and r[3] == 12]
    assert legend, "legend markers missing"
    gap = min(x for x, _, _, _ in legend) - (cx + radius)
    assert 30 <= gap <= 44, f"legend gap {gap}"
    legend_mid = sum(y + h / 2 for _, y, _, h in legend) / len(legend)
    assert abs(legend_mid - cy) <= 14, f"legend not centered on chart: {legend_mid} vs {cy}"


def _circle(svg: str) -> tuple[float, float, float]:
    m = re.search(r"<circle[^>]*cx=\"([\d.]+)\" cy=\"([\d.]+)\" r=\"([\d.]+)\"", svg)
    assert m, "center circle missing"
    return float(m.group(1)), float(m.group(2)), float(m.group(3))


def test_cycle_nodes_keep_clearance_and_arrows_visible() -> None:
    data = models.parse_diagram_data(
        {"type": "cycle", "layout": "full", "center": "学習",
         "items": [{"label": "計画"}, {"label": "実行"}, {"label": "検証"}, {"label": "振り返り"}]}
    )
    svg = "".join(renderer._cycle(data, _ctx()))
    ccx, ccy, cr = _circle(svg)
    boxes = [r for r in _rects(svg)]
    assert len(boxes) == 4
    for x, y, w, h in boxes:
        nearest_x = min(max(ccx, x), x + w)
        nearest_y = min(max(ccy, y), y + h)
        clearance = ((ccx - nearest_x) ** 2 + (ccy - nearest_y) ** 2) ** 0.5 - cr
        assert clearance >= 20, f"node too close to center disc: {clearance}"
    # Arrowheads must land outside every node box.
    for m in re.finditer(r"<polygon[^>]*points=\"([^\"]+)\"", svg):
        pts = [tuple(map(float, p.split(","))) for p in m.group(1).split()]
        tip = pts[0]
        for x, y, w, h in boxes:
            assert not (x < tip[0] < x + w and y < tip[1] < y + h), "arrowhead buried under node"


def test_org_chart_uses_compact_centered_rows() -> None:
    data = models.parse_diagram_data(
        {"type": "org-chart", "layout": "full",
         "root": {"label": "責任者", "children": [{"label": "開発", "children": [{"label": "実装"}]}, {"label": "設計"}]}},
    )
    svg = renderer.render_diagram(dict(data), tokens.load_design_tokens("prism-edge"), "full")
    lines = [(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
             for m in re.finditer(r"<line[ >][^>]*x1=\"([\d.]+)\" y1=\"([\d.]+)\" x2=\"([\d.]+)\" y2=\"([\d.]+)\"", svg)]
    assert lines
    for x1, y1, x2, y2 in lines:
        assert 40 <= abs(y2 - y1) <= 70, f"connector length off: {abs(y2 - y1)}"
    boxes = _rects(svg)
    top_edge = min(y for _, y, _, _ in boxes)
    bottom_edge = max(y + h for _, y, _, h in boxes)
    block_mid = (top_edge + bottom_edge) / 2
    assert abs(block_mid - (data["height"] / 2 + 10)) <= 40, "tree not vertically centered"


def test_org_chart_title_gap_stays_tight() -> None:
    data = models.parse_diagram_data(
        {"type": "org-chart", "layout": "full",
         "root": {"label": "責任者", "children": [{"label": "開発", "children": [{"label": "実装"}]}, {"label": "設計"}]}},
    )
    svg = renderer.render_diagram(dict(data), tokens.load_design_tokens("prism-edge"), "full")
    boxes = _rects(svg)
    gap = min(y for _, y, _, _ in boxes) - 28
    assert gap <= 50, f"title-body gap too large: {gap}"


def test_org_chart_four_rows_fit_canvas() -> None:
    def chain(depth: int) -> dict:
        return {"label": f"L{depth}", "children": [chain(depth + 1)] if depth < 3 else []}

    data = models.parse_diagram_data({"type": "org-chart", "layout": "full", "root": chain(0)})
    svg = renderer.render_diagram(dict(data), tokens.load_design_tokens("prism-edge"), "full")
    for _, y, _, h in _rects(svg):
        assert 0 <= y and y + h <= data["height"], "row outside canvas"


def test_pie_shows_in_slice_labels_and_ratios() -> None:
    data = models.parse_diagram_data(
        {"type": "pie", "layout": "full", "show_values": True,
         "items": [{"label": "製品A", "value": 45}, {"label": "製品B", "value": 30}, {"label": "サービス", "value": 25}]}
    )
    svg = renderer.render_diagram(dict(data), tokens.load_design_tokens("prism-edge"), "full")
    texts = re.findall(r"<text[^>]*>(.*?)</text>", svg)
    for expected in ("製品A", "45%", "製品B", "30%", "サービス", "25%"):
        assert any(expected in t for t in texts), f"missing in-slice text: {expected}"


def test_pie_narrow_slice_falls_back_to_ratio_only() -> None:
    data = models.parse_diagram_data(
        {"type": "pie", "layout": "full",
         "items": [{"label": "主力", "value": 90}, {"label": "その他いろいろ", "value": 5}, {"label": "残り", "value": 5}]}
    )
    svg = renderer.render_diagram(dict(data), tokens.load_design_tokens("prism-edge"), "full")
    texts = re.findall(r"<text[^>]*>(.*?)</text>", svg)
    assert any("5%" in t for t in texts), "narrow slice should still show its ratio"
    assert any("その他いろいろ" in t for t in texts), "legend must keep the full label"


def test_donut_shows_in_ring_labels_and_ratios() -> None:
    data = models.parse_diagram_data(
        {"type": "donut", "layout": "full", "show_values": True, "center_label": "100%",
         "items": [{"label": "サブスク", "value": 58}, {"label": "従量課金", "value": 27}, {"label": "その他", "value": 15}]}
    )
    width, height = data["width"], data["height"]
    cx = width * 0.32
    radius = min(height * renderer.CHART_R_FULL, width * 0.23)
    svg = renderer.render_diagram(dict(data), tokens.load_design_tokens("prism-edge"), "full")
    in_chart = []
    for m in re.finditer(r"<text[^>]*x=\"([\d.]+)\"[^>]*>(.*?)</text>", svg):
        if float(m.group(1)) < cx + radius + 5:
            in_chart.append(m.group(2))
    body = " ".join(in_chart)
    # All three slices carry label + ratio inside the ring.
    for expected in ("サブスク", "58%", "従量課金", "27%", "その他", "15%"):
        assert expected in body, f"missing in-ring text: {expected}"


def _title_x(svg: str) -> float:
    m = re.search(r"<text[^>]*x=\"([\d.]+)\" y=\"28\"[^>]*>", svg)
    assert m, "title element missing"
    return float(m.group(1))


def test_chart_title_centers_on_chart_body() -> None:
    for kind in ("pie", "donut"):
        data = models.parse_diagram_data(
            {"type": kind, "title": "T", "layout": "full", "items": [{"label": "A", "value": 2}, {"label": "B", "value": 1}]}
        )
        svg = renderer.render_diagram(dict(data), tokens.load_design_tokens("prism-edge"), "full")
        assert abs(_title_x(svg) - data["width"] * 0.32) <= 1.0, kind


def test_pyramid_funnel_titles_center_on_body() -> None:
    pyramid = models.parse_diagram_data(
        {"type": "pyramid", "title": "T", "layout": "full", "levels": [{"label": "A"}, {"label": "B"}, {"label": "C"}]}
    )
    svg = renderer.render_diagram(dict(pyramid), tokens.load_design_tokens("prism-edge"), "full")
    assert abs(_title_x(svg) - pyramid["width"] / 2) <= 1.0
    funnel = models.parse_diagram_data(
        {"type": "funnel", "title": "T", "layout": "full",
         "levels": [{"label": "A", "value": 9}, {"label": "B", "value": 4}, {"label": "C", "value": 1}]}
    )
    svg = renderer.render_diagram(dict(funnel), tokens.load_design_tokens("prism-edge"), "full")
    assert abs(_title_x(svg) - (funnel["width"] - 100) / 2) <= 1.0


def _point_in_rect(px: float, py: float, rect: tuple[float, float, float, float], margin: float = 1.0) -> bool:
    x, y, w, h = rect
    return x + margin < px < x + w - margin and y + margin < py < y + h - margin


def test_radial_connectors_never_cross_box_interiors() -> None:
    data = models.parse_diagram_data(
        {"type": "radial", "layout": "full", "center": "成果",
         "items": [{"label": "目的", "children": ["判断基準", "優先順位"]},
                   {"label": "役割", "children": ["責任", "連携"]},
                   {"label": "対話", "children": ["共有", "学習"]}]},
    )
    svg = "".join(renderer._radial(data, _ctx()))
    boxes = _rects(svg)
    assert len(boxes) == 9, f"expected 3 item + 6 child boxes, got {len(boxes)}"
    lines = [(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
             for m in re.finditer(r"<line[ >][^>]*x1=\"([\d.]+)\" y1=\"([\d.]+)\" x2=\"([\d.]+)\" y2=\"([\d.]+)\"", svg)]
    assert len(lines) == 9, f"expected 9 connectors, got {len(lines)}"
    for x1, y1, x2, y2 in lines:
        for t in (0.05, 0.5, 0.95):
            px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            assert not any(_point_in_rect(px, py, box) for box in boxes), "connector crosses a box interior"
