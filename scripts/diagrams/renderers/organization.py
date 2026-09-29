from __future__ import annotations

from .primitives import _node_rect, _text, _title, svg_line


def _org_chart(data: dict, ctx: dict) -> list[str]:
    width, height = data["width"], data["height"]
    levels: list[list[dict]] = []

    def collect(node: dict, depth: int) -> None:
        while len(levels) <= depth:
            levels.append([])
        levels[depth].append(node)
        for child in node.get("children", []):
            collect(child, depth + 1)

    collect(data["root"], 0)
    positions: dict[int, tuple[float, float]] = {}
    max_level_nodes = max(len(nodes) for nodes in levels)
    node_gap = 12
    node_w = min(170, (width - node_gap * (max_level_nodes + 1)) / max_level_nodes)
    node_h = 38
    # Fixed pitch + vertical centering: connector length stays constant no
    # matter how many generations the tree has (up to 5 rows); the pitch only
    # compresses when more rows need to share the canvas.
    available = height - 22 - 58
    if len(levels) > 1:
        pitch = min(node_h + 56, max(node_h + 32, (available - node_h) / (len(levels) - 1)))
    else:
        pitch = node_h + 56
    block = pitch * (len(levels) - 1) + node_h
    # Optical top-weighting: center small trees but keep the title gap tight.
    top = 58 + min(16.0, max(0.0, (available - block) / 2))
    elements = _title(ctx, width, data.get("title"))
    for depth, nodes in enumerate(levels):
        y = top + depth * pitch + node_h / 2
        row_width = len(nodes) * node_w + max(0, len(nodes) - 1) * node_gap
        row_start = (width - row_width) / 2
        for index, node in enumerate(nodes):
            node_x = row_start + node_w / 2 + index * (node_w + node_gap)
            positions[id(node)] = (node_x, y)
            parent = next(
                (candidate for candidate in sum(levels[:depth], []) if node in candidate.get("children", [])), None
            )
            if parent:
                px, py = positions[id(parent)]
                elements.append(
                    svg_line(
                        px,
                        py + node_h / 2,
                        node_x,
                        y - node_h / 2,
                        stroke=ctx["line"],
                        **{"stroke-width": ctx["shapes"]["strokeWidth"]},
                    )
                )
    for nodes in levels:
        for node in nodes:
            x, y = positions[id(node)]
            elements.append(_node_rect(x - node_w / 2, y - node_h / 2, node_w, node_h, ctx))
            elements.append(
                _text(x, y + 5, node["label"], ctx, "captionSize", max_chars=12, **{"text-anchor": "middle"})
            )
    return elements
