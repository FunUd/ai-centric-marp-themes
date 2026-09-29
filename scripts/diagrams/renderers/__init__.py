"""JSON SVG diagram renderers (P2-1 modularisation of `svg_diagram_renderer.py`).

Layout:
- `primitives`: low-level SVG element builders and shared context helpers
  (`svg_rect`, `svg_text`, `wrap_text`, `_title`, `_node_rect`, ...).
- `charts`: cartesian and proportional charts (`bar`, `line`, `pie`,
  `donut`, `hbar`, `stacked-bar`, `stacked-bar-100`).
- `concepts`: conceptual diagrams (`pyramid`, `funnel`, `radial`,
  `matrix`, `cycle`).
- `organization`: hierarchy diagrams (`org-chart`).

`scripts/diagrams/svg_diagram_renderer.py` remains the public entry point:
it re-exports every renderer helper (tests and the vendored skill copy
import it directly) and owns the `render_diagram()` dispatcher.
"""
