# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Theme token pipeline: `scripts/diagrams/sync-tokens-from-css.py` (CSS `:root` → `theme-styles/*.json`, `--check` for CI drift), `design_tokens.py` (incl. luminance-based `best_text_on`), `svg_theme_postprocessor.py`, `svg_filters.py`.
- Golden regression fixtures: `scripts/diagrams/tests/fixtures/diagram-golden/` (6 themes × 3 engines) with `regenerate-golden.py` and `test_golden.py`.
- `sales-funnel.json` template; CSS-native `grid-quadrant axes` and `steps arrows` patterns with `prism-edge` samples.
- Regression suites (92 tests): token sync, contrast, connector geometry, golden, funnel/pyramid/radial/pie, postprocessor, text quality, visual balance.

### Changed
- draw.io routing (`diagram_routing.py`, renderer, validator share one path): perpendicular port snapping, container→edge→node z-order, arrowheads on path ends, cylinder port spans.
- Mermaid postprocessing: edges/arrowheads in theme line color, gray-shadow removal, 1.5px+ strokes; pie palette order, 2.5px separators; title 22 / label 15 typography.
- `theme-styles/*.json` schema (colors/shapes/effects/typography/signature) synced from `themes/*.css`; Nebula dark-fill contrast fix.
- `marp-diagram-creator` skill: engine decision tree + quick ref; template catalog updated.

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
