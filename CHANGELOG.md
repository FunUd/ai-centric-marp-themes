# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- JSON diagram types `bar`, `line` (multi-series `categories`+`series`), and `stacked-bar` with shared cartesian frame (nice-tick axes, themed legends): `templates/charts/sales-bar.json`, `quarterly-line.json`, `channel-stacked-bar.json`.
- Theme token pipeline: `scripts/diagrams/sync-tokens-from-css.py` (CSS `:root` → `theme-styles/*.json`, `--check` for CI drift), `design_tokens.py` (incl. luminance-based `best_text_on`), `svg_theme_postprocessor.py`, `svg_filters.py`.
- Golden regression fixtures: `scripts/diagrams/tests/fixtures/diagram-golden/` (6 themes × 3 engines) with `regenerate-golden.py` and `test_golden.py`.
- `sales-funnel.json` template; CSS-native `grid-quadrant axes` and `steps arrows` patterns with `prism-edge` samples.
- Regression suites (175 tests): token sync, contrast, connector geometry, golden, funnel/pyramid/radial/pie, postprocessor, text quality, visual balance, aspect control, key-message theme contract, CLI exit-code/encoding contract.
- Aspect-ratio control: new `scripts/diagrams/svg_aspect.py` (`parse_aspect` accepting `2.4`/`16:9`, `%% aspect:` Mermaid directive extraction, `pad_viewbox` centering padding within `VALIDATOR_LIMITS`), JSON `"aspect"` field (derives `height` from `width`, mutually exclusive with `height`), and `render-slide-diagram.py --aspect 2.4|16:9` for all three engines. Validator aspect warnings now include an actionable re-render hint with the suggested ratio.
- Contract tests: `tests/test_theme_keymessage.py` (static + Playwright computed-style checks that the key-message quote inherits/differs from the subtitle in all 6 themes) and `tests/test_cli_contract.py` (non-zero exit on validation failure, `--no-validate` escape hatch, UTF-8 output under a cp932 console).

### Changed
- draw.io routing (`diagram_routing.py`, renderer, validator share one path): perpendicular port snapping, container→edge→node z-order, arrowheads on path ends, cylinder port spans.
- Mermaid postprocessing: edges/arrowheads in theme line color, gray-shadow removal, 1.5px+ strokes; pie palette order, 2.5px separators; title 22 / label 15 typography.
- `theme-styles/*.json` schema (colors/shapes/effects/typography/signature) synced from `themes/*.css`; Nebula dark-fill contrast fix.
- `marp-diagram-creator` skill: engine decision tree + quick ref; template catalog updated; `aspect`/`--aspect` documented in `SKILL.md` and `diagram-patterns.md` §1; `ADD_NEW_DIAGRAM_TYPE.md` notes that `aspect` is inherited centrally.
- `templates/mermaid/flowchart-linear.mmd` pins `%% aspect: 2.4` (recommended full-slide ratio, embeds at 1050x437); the 6 golden flowchart fixtures were regenerated accordingly and now validate with 0 warnings.

### Fixed
- CLI exit codes: `render-slide-diagram.py` now exits non-zero when layout validation fails (it previously printed `[WARN]` and still reported `[SUCCESS]` with exit 0, letting broken geometry through automation); `regenerate-golden.py` inherits this strictness because it already propagates render return codes.
- Windows console encoding: `render-slide-diagram.py`, `validate-slide-diagram.py`, `marp-lint.py`, and `marp-diagnostics.py` force UTF-8 on stdout/stderr, so Japanese text and file names no longer require manually setting `PYTHONIOENCODING=utf-8` (cp932 consoles/pipes).
- Validator overlap epsilon: `_rects_overlap` in `validate-slide-diagram.py` now uses `OVERLAP_EPSILON = 0.05` so sub-pixel node borders no longer false-positive as overlap.
- Pyramid renderer no longer drops level descriptions that outgrow the trapezoid — `svg_diagram_renderer.py::_pyramid` pads to 16px and falls back to outside placement (`outside_description()`).
- `key-message` quote text: `section.key-message blockquote p` now inherits size/color in all 6 themes (`azure-clarity`, `crimson-clarity`, `warm-sunnyday`, `slate-minimal` gained the rule alongside the earlier `prism-edge` fix; `nebula-glass` already specified its own explicit size).

### Removed
- Orphan docs: `docs/diagram-engine-selection-guide.md`, `docs/diagram-quality-baseline.md`, `docs/plans/`, `docs/diagram-golden/README.md`.
- Superseded templates: JSON `timeline` type, `comparison-matrix.drawio`, `timelines/product-roadmap.json` (CSS Native replaces them); `slides/diagram-demo/` generated artifacts.

## [0.1.0] - 2026-05-15

### Added
- **Initial Public Release**: A curated collection of AI-optimized Marp themes.
- **5 Professional Themes**:
  - `azure-clarity`: Clean corporate blue.
  - `crimson-clarity`: High-impact corporate red.
  - `prism-edge`: Modern bold indigo-cyan.
  - `nebula-glass`: Dark glassmorphism tech-premium.
  - `warm-sunnyday`: Friendly warm orange.
- **AI Agent Integration**:
  - Custom "Skills" for Claude Code, Windsurf, Cursor, Kiro, and GitHub Copilot.
  - `scripts/sync-skills.py`: Easy setup script for syncing skills to local AI agents.
- **Unified Component System**: Ready-to-use classes for covers, grids, timelines, callouts, and multi-column layouts.
- **Toolkit**: Pre-render linter (`marp-lint.py`) and layout diagnostics helper (`marp-diagnostics.py`).
- **Sample Decks**: Complete demonstration slides for each theme.
