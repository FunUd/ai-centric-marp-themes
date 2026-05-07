---
name: theme-expert-common
description: Shared Marp layout reference for theme-expert-* skills. Read this only when a theme skill points here or when you need generic cover, TOC, column, grid, density, timeline, checklist, callout, alignment, or image guidance.
---

# Theme Expert Common

This file contains shared Marp layout mechanics that are reused across the theme-specific skills.
Load it only when you need the generic class syntax or when a theme skill explicitly points here.

## Critical Structure Rules

**Container classes require proper nesting. Missing wrapper divs will break layout:**

- `callout` → Must wrap individual blocks, not entire slides
- `cols-2/3`, `split-2/3` → Requires `<div class="columns">` + child `<div class="col">` or `<div>`
- `grid-quadrant/sharp` → Requires `<div class="grid">` + exactly four `<div class="cell">` children. **DO NOT hallucinate wrapper divs like `<div class="cell side"><div>`. Use EXACTLY `<div class="cell">`.**
- `profile` → Requires `<div class="profile-layout">` + `profile-image` + `profile-content`
- Inline classes (`badge`, `gradient-text`) → Use `<span>`, not `<div>`
- Alignment (`v-center`, `text-center`) → Apply to column divs, not slide-level `_class`

> **🚨 DO NOT HALLUCINATE CLASSES:**
> Do not use classes that are not explicitly documented in the theme-specific skill or this common file (e.g., `accent-left`). If you need an asymmetrical layout, check if the theme specifically supports it (like `split-asym` in Prism Edge), otherwise use standard classes like `cols-2`.

**For the exact HTML structure of these patterns, please read `references/layout-snippets.md`.**

> **🚨 CRITICAL FAILURE WARNING — #1 CAUSE OF BROKEN SLIDES:**
> Writing `<div class="columns">` or `<div class="grid">` WITHOUT the matching `<!-- _class: ... -->` directive is the single most common and destructive AI mistake. **The HTML wrapper alone does NOTHING.** The CSS layout activates ONLY when the `section` element has the correct class.
>
> **WRONG (layout will NOT activate — content stacks vertically and overflows):**
> ```markdown
> <!-- _class: with-header -->
> # Title
> <div class="columns">
> <div class="col">Left</div>
> <div class="col">Right</div>
> </div>
> ```
>
> **CORRECT:**
> ```markdown
> <!-- _class: cols-2 with-header -->
> # Title
> <div class="columns">
> <div class="col">Left</div>
> <div class="col">Right</div>
> </div>
> ```
>
> **Required pairings:**
> - `<div class="columns">` → `cols-2`, `cols-3`, `split-2`, `split-3`, `split-asym`, or `split-asym-reverse` in `_class`
> - `<div class="grid">` → `grid-quadrant` or `grid-sharp` in `_class`
> - `<div class="profile-layout">` → `profile` in `_class`

> **🚨 CENTERED LIST PROHIBITION:**
> Do NOT place bullet lists (`-`, `*`, `1.`) on slides with centered-layout classes: `cover`, `cover-wave`, `cover-diagonal`, `cover-noir`, `cover-aurora`, `key-message`, `align-center`. Lists will render centered instead of left-aligned. Move lists to content slides.

**When in doubt, check `slides/sample-slide/` for correct structure, and run `marp-lint.py` to catch these issues automatically.**

## Shared Patterns

### Cover / Title

- Use `<!-- _class: cover subtitle meta -->` for standard covers
- Hide chrome with `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Use `H1` for title, `H2` for subtitle, and a short meta line for author or date

### Table of Contents

- `<!-- _class: toc -->` for many entries
- `<!-- _class: toc-focus -->` for 4-5 high-priority items

### Column Layouts

- `<!-- _class: cols-2 -->` and `<!-- _class: cols-3 -->` for card-style columns
- `<!-- _class: split-2 -->` and `<!-- _class: split-3 -->` for simple split layouts
- Prefer symmetry unless one side is clearly the dominant visual

> **⚠️ `cols-*` / `split-*` must appear in `_class`.**
> When combining with other classes (e.g. `with-header`), the column class must still be present.
> `<!-- _class: with-header -->` alone will NOT activate the column layout.
> Correct: `<!-- _class: cols-2 with-header -->`

### Grids

- `<!-- _class: grid-quadrant -->` for a 2x2 comparison or summary matrix
- `<!-- _class: grid-sharp -->` when you want a cleaner border-only matrix

### Density Control

- `<!-- _class: dense -->` for moderately dense slides
- `<!-- _class: extra-dense -->` for the densest slides that still need to stay readable
- Use `<style scoped>` with `--font-scale` if you need finer control

### Profile / Self-Introduction

- `<!-- _class: profile -->` for photo + bio layouts
- Keep the photo visible and the text short

### Key Message

- `<!-- _class: key-message no-pagination -->` for a section divider or single takeaway slide

### Header / Footer / Pagination

- `no-header`, `no-footer`, `no-pagination`, `pagination-left`, and `with-header` are the main utilities
- Combine them carefully when you need a clean cover or section divider

### Steps and Timeline

- `<!-- _class: steps -->` for process slides
- `<!-- _class: timeline -->` for ordered milestones
- Keep the date and description on the same line for timeline items

### Checklist and Timetable

- `<!-- _class: checklist -->` for action items or review points
- `<!-- _class: timetable -->` for schedule tables

### Callouts

- `callout.info`, `callout.success`, `callout.warning`, and `callout.danger` are available
- Use callouts sparingly and keep contrast strong

### Alignment and Images

- Use `v-top`, `v-center`, `v-bottom`, `text-left`, `text-center`, and `text-right` as needed
- Use `![center shadow width:600px](path)` for emphasis images
- Use `![bg right:45% shadow](path)` for split layouts

## Reading Rule

Only open this file when you need one of the shared patterns above.
If the slide is already covered by a theme-specific rule or by `marp-slide-creator`, avoid loading this file.
