# Adding a New JSON Diagram Type

This is the checklist for extending the JSON SVG engine with a new diagram
type (e.g. `bar`, `radar`, `gantt`). All five steps are required — the
registry test (`tests/test_diagram_registry.py`) and the catalog check
(`check-catalog-sync.py`) fail until each one is done.

## 1. Model (`diagram_models.py`)

- Add the type name to `DIAGRAM_TYPES` (imported from `layout_spec.py` — no geometry here).
- Add a `_validate_<kind>()` branch in `_validate_type()` covering required fields, ranges, and limits (counts, depth, non-empty labels).
- If the type needs a non-standard default height for a layout, add an entry to `layout_spec.py::TYPE_LAYOUT_HEIGHTS`.
- Canvas `aspect` (`{"aspect": 2.4}` → `height = width / aspect`, mutually exclusive with `height`)
  is resolved centrally in `parse_diagram_data()` — new types inherit it for free. Renderers just
  read `data["width"]` / `data["height"]` as usual. Mermaid/draw.io aspect padding lives in
  `svg_aspect.py` and is likewise engine-agnostic.

## 2. Renderer (`svg_diagram_renderer.py`)

- Implement `_render_<kind>(data, ctx)` returning a list of SVG element strings.
- Use only `theme_context()` tokens (`primary`, `surface`, `text`, `muted`, `line`, …) — never hardcode theme colors.
- Respect `data["width"]` / `data["height"]`; keep labels ≥12px and wrap via `wrap_text()`.
- Register the renderer in `render_diagram()`'s `renderers` map.

## 3. Template (`templates/<group>/<name>.json`)

- Add a minimal runnable example, e.g. `templates/charts/sales-bar.json`.
- Must include `"type"`, representative labels/values, and optionally `"title"`.
- Render it once per theme to confirm no overflow:
  `python render-slide-diagram.py -i templates/<group>/<name>.json -o /tmp/check.svg --theme <each-theme> --layout full`

## 4. Docs (both files — the catalog check enforces this)

- `skills/marp-diagram-creator/references/template-catalog.md`: add a row to the JSON SVG table.
- `README.md` → Available Templates: add the matching row.
- If the type introduces a new selection rule, update the decision table in `references/diagram-patterns.md` §3 and the summary in `SKILL.md` §2 (they must stay identical).

## 5. Tests (`tests/`)

- Add `tests/test_<kind>.py`: validation rejects bad input, renderer output parses as XML, no node overlaps, connectors never cross nodes, labels within bounds.
- `test_diagram_registry.py` automatically picks up the new type and asserts model ↔ renderer ↔ template ↔ docs consistency.
