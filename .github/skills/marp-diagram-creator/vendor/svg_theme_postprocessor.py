from __future__ import annotations

import re
from typing import Any

from design_tokens import (
    FALLBACK_INK,
    best_text_on,
    contrast_ratio,
    ensure_graphical_contrast,
    graphical_ink,
    mermaid_postprocess_rules,
    normalize_color,
    soften_mindmap_fill,
    theme_context,
)
from svg_filters import build_filter_defs


def _replace_rect_radius(svg: str, radius: float, large_radius: float) -> str:
    def replacer(match: re.Match[str]) -> str:
        tag = match.group(0)
        if 'data-diagram-role="marker"' in tag or 'role="marker"' in tag:
            rx = max(0, radius // 2) if radius else 0
        elif "swimlane" in tag.lower():
            rx = large_radius
        else:
            rx = radius
        # Convert to int if it's a whole number
        rx_val = int(rx) if rx == int(rx) else rx
        if rx:
            if re.search(r"\brx=", tag):
                tag = re.sub(r"\brx='[^']*'", f"rx='{rx_val}'", tag)
                tag = re.sub(r'\brx="[^"]*"', f'rx="{rx_val}"', tag)
                tag = re.sub(r"\bry='[^']*'", f"ry='{rx_val}'", tag)
                tag = re.sub(r'\bry="[^"]*"', f'ry="{rx_val}"', tag)
            else:
                # Add rx/ry before the closing
                if "/>" in tag:
                    tag = tag.replace("/>", f" rx='{rx_val}' ry='{rx_val}'/>")
                else:
                    tag = tag.replace(">", f" rx='{rx_val}' ry='{rx_val}'>", 1)
        else:
            tag = re.sub(r"\s*rx='[^']*'", "", tag)
            tag = re.sub(r'\s*rx="[^"]*"', "", tag)
            tag = re.sub(r"\s*ry='[^']*'", "", tag)
            tag = re.sub(r'\s*ry="[^"]*"', "", tag)
        return tag

    return re.sub(r"<rect\b[^>]*/?>", replacer, svg)


def _replace_font_family(svg: str, font_family: str) -> str:
    escaped = font_family.replace('"', "'")
    svg = re.sub(r'font-family="[^"]*"', f'font-family="{escaped}"', svg)
    svg = re.sub(r"font-family='[^']*'", f"font-family='{escaped}'", svg)
    if "font-family" not in svg:
        svg = svg.replace("<text ", f'<text font-family="{escaped}" ', 1)
    return svg


def _inject_node_filters(svg: str, effects: dict[str, Any]) -> str:
    if not effects.get("nodeShadowEnabled") and not effects.get("glowEnabled"):
        return svg
    filter_id = "theme-glow" if effects.get("glowEnabled") else "theme-shadow"
    if f'id="{filter_id}"' not in svg and f"id='{filter_id}'" not in svg:
        # Insert only the inner <filter> element into the first existing
        # <defs> block. Mermaid emits several <defs> blocks, so a whole
        # <defs>...</defs> wrapper must NOT be spliced in (orphaned <filter>).
        inner = build_filter_defs(effects)
        inner = re.sub(r"^\s*<defs>|</defs>\s*$", "", inner)
        if "<defs/>" in svg:
            svg = svg.replace("<defs/>", f"<defs>{inner}</defs>", 1)
        elif "<defs>" in svg:
            svg = svg.replace("<defs>", f"<defs>{inner}", 1)
        else:
            svg = re.sub(r"(<svg[^>]*>)", rf"\1<defs>{inner}</defs>", svg, count=1)

    def add_filter(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "filter=" in tag or 'data-diagram-role="connector"' in tag:
            return tag
        if "stroke=" not in tag and "fill=" not in tag:
            return tag
        return tag.replace("/>", f' filter="url(#{filter_id})"/>')

    return re.sub(r"<rect\b[^>]*/?>", add_filter, svg)


def _recolor_arrows(svg: str, line_color: str) -> str:
    """Force Mermaid's default black/gray arrowheads onto the theme line color."""
    svg = re.sub(r"#0b0b0b", line_color, svg, flags=re.IGNORECASE)
    svg = re.sub(
        r"(\.arrowheadPath\s*\{\s*fill\s*:\s*)#[0-9a-fA-F]{3,6}",
        r"\1" + line_color,
        svg,
    )
    return svg


def _remove_default_gray_shadow(svg: str) -> str:
    """Drop Mermaid's built-in gray drop-shadow so only the theme filter remains."""
    svg = re.sub(
        r"filter\s*:\s*drop-shadow\s*\(\s*1px\s+2px\s+2px\s+rgba\(185,185,185,1\)\s*\)",
        "filter:none",
        svg,
    )
    return svg


def _bolden_mindmap_labels(svg: str) -> str:
    """Bold Mermaid mindmap node labels for slide legibility.

    Mindmap node text lives in foreignObject HTML (span.nodeLabel, not SVG
    <text>), rendered at 15px regular — thin CJK strokes wash out at a
    distance. Bold only; the original section ink (#111827 on pastel fills)
    is preserved so contrast never regresses. CJK advances are full-width
    so bold does not reflow node boxes. Scoped to mindmap diagrams only;
    layout untouched.
    """
    if "mindmapDiagram" not in svg or "</style>" not in svg:
        return svg
    override = ".mindmapDiagram span.nodeLabel,.mindmapDiagram span.nodeLabel p{font-weight:700 !important;}"
    return svg.replace("</style>", override + "</style>", 1)


def _fix_gantt_contrast(svg: str, theme_data: dict[str, Any]) -> str:
    """Guarantee Gantt bars stay visible on the slide canvas.

    Mermaid derives `activeTaskBkgColor` as `lighten(primaryColor, 23)` and
    `activeTaskBorderColor` as `primaryColor`. For pale palettes
    (azure `#EDF5FF`, warm `#FFF0E5`, slate `#F8FAFC`) both resolve to
    near-white, so the active bar (e.g.「設計」) is 1.0-1.1:1 vs the slide
    background — invisible except for its dark text floating in space.
    Normal tasks survive only via their primary border; warm's primary
    border (`#FF8C42` vs `#FFFDF9` = 2.3:1) fails even that.

    Fix: when *both* fill and stroke of a task family (active/task/done/
    crit) fall below 3:1 vs the canvas, pin the stroke to the theme's
    graphical ink (line/primaryDark — always >=3:1 by construction) and
    repair the inside text to `best_text_on(fill)` when it falls below
    4.5:1. Fills are preserved so the design intent (pale tasks, grey
    done) survives; only the invisible boundary is repaired. Layout
    untouched — CSS values only.
    """
    if "</style>" not in svg:
        return svg
    # Heuristic: Gantt SVGs carry task classes and no mindmap marker.
    if "mindmapDiagram" in svg or (".taskText" not in svg and ".active0" not in svg):
        return svg
    ctx = theme_context(theme_data)
    background = ctx.get("background", "#FFFFFF")
    ink = graphical_ink(theme_data, 3.0)

    # Family fills for text-contrast anchors (done=lightgrey needs dark ink
    # on dark themes even when active/task are dark with light ink).
    def _family_fill(name: str) -> str | None:
        m = re.search(r"\." + name + r"\d[^{]*\{[^}]*fill:([^;!]+)", svg, re.IGNORECASE)
        if not m:
            # `.done0` writes `stroke:...;fill:...` (stroke first).
            m = re.search(r"\." + name + r"\d[^{]*\{[^}]*?fill:([^;!]+)", svg, re.IGNORECASE)
        return normalize_color(m.group(1)) if m else None

    family_fills = {
        "active": _family_fill("active"),
        "task": _family_fill("task"),
        "done": _family_fill("done") or _family_fill("doneCrit"),
        "crit": _family_fill("crit"),
    }

    def _repair_rule(match: re.Match[str]) -> str:
        selector, body = match.group(1), match.group(2)
        sel = selector.lower()
        is_task_fill = any(key in sel for key in (".active", ".task0", ".task1", ".task2", ".task3", ".done", ".crit"))
        is_task_text = "tasktext" in sel or "donetext" in sel or "crittext" in sel
        if not (is_task_fill or is_task_text):
            return match.group(0)
        fill_m = re.search(r"fill:([^;!]+)", body)
        stroke_m = re.search(r"stroke:([^;!]+)", body)
        new_body = body
        if is_task_fill:
            fill_hex = normalize_color(fill_m.group(1)) if fill_m else None
            stroke_hex = normalize_color(stroke_m.group(1)) if stroke_m else None
            fill_ok = contrast_ratio(fill_hex, background) >= 3.0 if fill_hex else True
            stroke_ok = contrast_ratio(stroke_hex, background) >= 3.0 if stroke_hex else True
            # Both invisible -> the bar disappears; pin the boundary to ink.
            if fill_hex and stroke_hex and not fill_ok and not stroke_ok:
                new_body = re.sub(r"stroke:[^;!]+", f"stroke:{ink}", new_body, count=1)
            elif stroke_hex and not stroke_ok and not fill_m:
                new_body = re.sub(r"stroke:[^;!]+", f"stroke:{ink}", new_body, count=1)
            # Warm-sunnyday primary border (2.3:1) fails alone: lift any
            # task stroke below 3:1 to ink even when the fill is also pale.
            elif stroke_hex and not stroke_ok and ".active" not in sel:
                # Only touch task-family strokes, never grid/section washes.
                if any(k in sel for k in (".task", ".done", ".crit")):
                    new_body = re.sub(r"stroke:[^;!]+", f"stroke:{ink}", new_body, count=1)
        if is_task_text and fill_m:
            text_hex = normalize_color(fill_m.group(1))
            if text_hex:
                # Family-specific anchor: done text lives on lightgrey even
                # when active/task are dark (nebula), so a single global
                # anchor misses the failure.
                if "donecrittext" in sel:
                    anchor = family_fills.get("done")
                elif "donetext" in sel:
                    anchor = family_fills.get("done")
                elif "crittext" in sel:
                    anchor = family_fills.get("crit")
                elif "activetext" in sel:
                    anchor = family_fills.get("active")
                else:
                    anchor = family_fills.get("task") or family_fills.get("active")
                anchor = anchor or "#FFFFFF"
                if contrast_ratio(text_hex, anchor) < 4.5:
                    fixed = best_text_on(anchor, "#FFFFFF", FALLBACK_INK)
                    # Never regress: only replace when the pick is stronger.
                    if contrast_ratio(fixed, anchor) > contrast_ratio(text_hex, anchor):
                        new_body = re.sub(r"fill:[^;!]+", f"fill:{fixed}", new_body, count=1)
        return f"{selector}{{{new_body}}}"

    return re.sub(r"([^{}]+)\{([^}]*)\}", _repair_rule, svg)


def _fix_mindmap_contrast(svg: str, theme_data: dict[str, Any]) -> str:
    """Guarantee mindmap text (>=4.5:1), edges (>=3:1), and node bounds.

    Mermaid derives mindmap fills/edges (`cScale*`) by darkening the theme
    `primaryColor` 25% (light) / 75% (dark). For our palettes that yields
    saturated mid fills with thin dark ink (vibration at a distance) and
    pastel edges at 1.1-2.8:1 vs the canvas (invisible connectors). Nodes
    carry no stroke, so pale fills on light canvases float as borderless
    text. Nebula dark mode is worse: near-black fills on a near-black
    canvas (1.0:1) — nodes disappear entirely.

    Fix, CSS-only (no layout): per section, keeping hue,
    (a) soften the node fill on light canvases (`soften_mindmap_fill`:
        +0.12 lightness, ×0.75 saturation) so dark bold CJK sits 8+:1 on a
        premium pastel instead of vibrating on saturated mid-tone;
    (b) repair label ink (`text` SVG + `span` HTML) to `best_text_on(fill)`
        when below 4.5:1, lightening the fill itself when even the best ink
        falls short;
    (c) nudge the `section-edge` stroke to 3:1 vs the canvas and reuse that
        same passing hue as the node `stroke` (1.5px, added when missing),
        so pale nodes keep a visible boundary instead of floating;
    (d) hide the stray per-node underline (`.section-N line`, Mermaid's
        3px brown/rainbow `<line class="node-line-">` 5px below each box),
        which duplicates the (c) border and clashes hue (brown on blue).
    Dark canvases keep deep fills with white ink; the new light node stroke
    carries the boundary. Fills/edges diverge by design: fill serves text,
    stroke serves canvas.
    """
    if "mindmapDiagram" not in svg or "</style>" not in svg:
        return svg
    ctx = theme_context(theme_data)
    background = ctx.get("background", "#FFFFFF")

    # Collect section fills: `.section-N rect,...{fill:...}` (first wins).
    fills: dict[str, str] = {}
    for match in re.finditer(r"\.section-(-?\d+)[^{]*\{[^}]*fill:([^;!]+)", svg):
        sec, raw = match.group(1), match.group(2)
        norm = normalize_color(raw)
        if norm and sec not in fills:
            fills[sec] = norm

    for sec, fill_hex in fills.items():
        # (a0) Soften saturated fills on light canvases before anything else:
        # hue is preserved, text contrast only improves (lighter vs dark ink),
        # and the harsh rainbow vibration drops to a premium pastel.
        soft = soften_mindmap_fill(fill_hex, background) or fill_hex
        if soft != fill_hex:
            for _pat_str in (
                r"(\.section-" + re.escape(sec) + r"\s+(?:rect|path|circle|polygon)[^{]*\{[^}]*?fill:)([^;!]+)",
                r"(\[data-look=\"neo\"\]\.mindmap-node\.section-" + re.escape(sec) + r"[^{]*\{[^}]*?fill:)([^;!]+)",
            ):
                svg = re.compile(_pat_str).sub(lambda m, _new=soft: m.group(1) + _new, svg)
            fill_hex = soft
        # (a) label ink: `.section-N text{fill:...}` (SVG) and
        # `.section-N span{color:...}` (foreignObject HTML).
        # When even the best ink falls below 4.5:1, lighten/darken the fill
        # itself (preserving hue) so text can pass — text legibility outranks
        # preserving the exact pastel shade. Edges stay on their own
        # background-contrast track (b) below, so structure never washes out.
        best_ink = best_text_on(fill_hex, "#FFFFFF", FALLBACK_INK)
        target_fill = fill_hex
        if contrast_ratio(best_ink, fill_hex) < 4.5:
            from design_tokens import adjust_lightness as _adjust

            # Dark ink wants a lighter fill; light ink wants a darker fill.
            step = 0.05 if best_ink.upper() == FALLBACK_INK.upper() else -0.05
            candidate = fill_hex
            for _ in range(12):
                nxt = _adjust(candidate, step)
                if nxt is None or nxt == candidate:
                    break
                candidate = nxt
                ink = best_text_on(candidate, "#FFFFFF", FALLBACK_INK)
                if contrast_ratio(ink, candidate) >= 4.5:
                    target_fill = candidate
                    break
            if target_fill != fill_hex:
                # Rewrite only the node fills for this section, never the edge.
                fill_pat = re.compile(
                    r"(\.section-" + re.escape(sec) + r"\s+(?:rect|path|circle|polygon)[^{]*\{[^}]*?fill:)([^;!]+)",
                )

                def _repair_fill(m: re.Match[str], _new: str = target_fill) -> str:
                    return m.group(1) + _new

                svg = fill_pat.sub(_repair_fill, svg)
                # Neo-look duplicate rules (`[data-look="neo"]...`) carry the
                # same fill; repair them too so old and new engines agree.
                neo_pat = re.compile(
                    r"(\[data-look=\"neo\"\]\.mindmap-node\.section-" + re.escape(sec) + r"[^{]*\{[^}]*?fill:)([^;!]+)",
                )
                svg = neo_pat.sub(lambda m, _new=target_fill: m.group(1) + _new, svg)
                fill_hex = target_fill
        for kind, prop in (("text", "fill"), ("span", "color")):
            pat = re.compile(
                r"(\.section-" + re.escape(sec) + r"\s+" + kind + r"\{[^}]*?" + prop + r":)([^;!]+)",
            )

            def _repair_ink(m: re.Match[str], _fill: str = fill_hex) -> str:
                current = normalize_color(m.group(2))
                if current is None:
                    return m.group(0)
                if contrast_ratio(current, _fill) >= 4.5:
                    return m.group(0)
                fixed = best_text_on(_fill, "#FFFFFF", FALLBACK_INK)
                if contrast_ratio(fixed, _fill) <= contrast_ratio(current, _fill):
                    return m.group(0)
                return m.group(1) + fixed

            svg = pat.sub(_repair_ink, svg)
        # (b) edge stroke: `.section-edge-N{stroke:...}`.
        # Resolve the passing edge hue first so nodes can reuse it for their
        # own boundary (c) — one hue per branch for fill, edge, and border.
        edge_pat = re.compile(r"(\.section-edge-" + re.escape(sec) + r"\{[^}]*?stroke:)([^;!]+)")
        _edge_match = edge_pat.search(svg)
        _edge_current = normalize_color(_edge_match.group(2)) if _edge_match else None
        if _edge_current is None:
            edge_fixed: str | None = graphical_ink(theme_data, 3.0)
        elif contrast_ratio(_edge_current, background) >= 3.0:
            edge_fixed = _edge_current
        else:
            edge_fixed = ensure_graphical_contrast(_edge_current, background, 3.0)
            if edge_fixed is None or contrast_ratio(edge_fixed, background) < 3.0:
                edge_fixed = graphical_ink(theme_data, 3.0)

        def _repair_edge(m: re.Match[str], _fixed: str | None = edge_fixed) -> str:
            if _fixed is None:
                return m.group(0)
            return m.group(1) + _fixed

        svg = edge_pat.sub(_repair_edge, svg)
        # Neo duplicate edge rules carry the same stroke; keep them in sync.
        svg = re.compile(r"(\[data-look=\"neo\"\]\.section-edge-" + re.escape(sec) + r"\{[^}]*?stroke:)([^;!]+)").sub(
            lambda m, _fixed=edge_fixed: m.group(1) + (_fixed or m.group(2)), svg
        )

        # (c) node boundary: pale fills float borderless on light canvases
        # (fill vs bg ~1.1-1.8:1). Pin the node stroke to the passing edge
        # hue at 1.5px so each branch keeps a visible shape without changing
        # geometry. Dark canvases get the same light stroke for free.
        if edge_fixed and contrast_ratio(edge_fixed, background) >= 3.0:
            node_pat = re.compile(
                r"(\.section-" + re.escape(sec) + r"\s+(?:rect|path|circle|polygon)[^{]*\{)([^}]*?)(\})",
            )

            def _repair_node(m: re.Match[str], _stroke: str = edge_fixed) -> str:
                head, body, tail = m.group(1), m.group(2), m.group(3)
                if re.search(r"stroke\s*:", body):
                    body = re.sub(r"stroke\s*:[^;!]+", f"stroke:{_stroke}", body, count=1)
                else:
                    body = body.rstrip()
                    if body and not body.endswith(";"):
                        body += ";"
                    body += f"stroke:{_stroke};stroke-width:1.5"
                if re.search(r"stroke-width\s*:", body):
                    body = re.sub(r"stroke-width\s*:[^;!]+", "stroke-width:1.5", body, count=1)
                return head + body + tail

            svg = node_pat.sub(_repair_node, svg)
            svg = re.compile(
                r"(\[data-look=\"neo\"\]\.mindmap-node\.section-" + re.escape(sec) + r"[^{]*\{)([^}]*?)(\})",
            ).sub(
                lambda m, _s=edge_fixed: (
                    m.group(1)
                    + re.sub(
                        r"stroke\s*:[^;!]+",
                        f"stroke:{_s}",
                        (
                            m.group(2)
                            if re.search(r"stroke\s*:", m.group(2))
                            else (
                                m.group(2).rstrip()
                                + (";" if m.group(2).rstrip() and not m.group(2).rstrip().endswith(";") else "")
                                + f"stroke:{_s};stroke-width:1.5"
                            )
                        ),
                        count=1,
                    )
                    + m.group(3)
                ),
                svg,
            )

    # (d) stray underlines: Mermaid emits one 3px `<line class="node-line-">`
    # 5px below every branch/leaf box, stroked per-section in clashing
    # rainbow hues (azure: brown `rgb(182,99,0)` under blue fills, olive
    # under purple, ...). It duplicates the node border added in (c),
    # doubles the ink under each label, and breaks the one-hue-per-branch
    # rule — the reported "brown line". Hide it (stroke:none, geometry and
    # viewBox untouched). Scoped to mindmap `section-*-line` rules only;
    # connectors (`section-edge-*`) are never matched.
    svg = re.sub(
        r"(\.section-(?:-?\d+|root)\s+line\{[^}]*?)stroke:[^;!]+",
        r"\1stroke:none",
        svg,
    )

    return svg


def _thicken_edges(svg: str, stroke_width: float) -> str:
    """Lift Mermaid's 1px edges toward the theme stroke width for slide legibility."""
    target = max(1.5, float(stroke_width))
    width_token = ("%g" % target) + "px"
    svg = re.sub(
        r"(\.edgePath\s+\.path\s*\{\s*stroke\s*:[^;]+;\s*stroke-width\s*:\s*)1px",
        r"\g<1>" + width_token,
        svg,
    )
    svg = re.sub(
        r"(\.flowchart-link\s*\{\s*stroke\s*:[^;]+;\s*)fill\s*:\s*none",
        r"\g<1>stroke-width:" + width_token + ";fill:none",
        svg,
    )
    return svg


def postprocess_svg(svg: str, theme_data: dict[str, Any]) -> str:
    """Apply theme tokens to an external-engine SVG without changing layout."""
    rules = mermaid_postprocess_rules(theme_data)
    ctx = theme_context(theme_data)
    svg = _replace_font_family(svg, rules["fontFamily"])
    svg = _replace_rect_radius(svg, float(rules["nodeRadius"]), float(rules["nodeRadiusLg"]))
    svg = _recolor_arrows(svg, ctx["line"])
    svg = _remove_default_gray_shadow(svg)
    svg = _thicken_edges(svg, float(rules["strokeWidth"]))
    svg = _fix_gantt_contrast(svg, theme_data)
    svg = _fix_mindmap_contrast(svg, theme_data)
    svg = _bolden_mindmap_labels(svg)
    svg = _inject_node_filters(svg, ctx["effects"])
    return svg
