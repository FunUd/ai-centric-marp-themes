---
name: theme-expert-azure-clarity
description: A skill for maximizing the Azure Clarity theme in Marp once the theme has already been chosen. Use when the user wants business-slide layout guidance, theme-specific classes, or structure polish for a deck that is already headed toward Azure Clarity.
---

# Azure Clarity Theme Expert

This skill provides guidelines for using the Azure Clarity theme's classes and layout patterns to create professional business presentations.

Use this skill after the content structure is decided. For outline planning or story shaping, use `slide-content-designer` or the relevant domain skill first.

## Basic Principles

Apply optimal CSS classes (`<!-- _class: ... -->`) according to the slide's intent. The theme enables rich layouts beyond plain Markdown.

## Layout Guide by Use Case

### 1. Cover / Title Slide
- **Classes**: `<!-- _class: cover subtitle meta -->`
- **Directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- **Features**: Blue gradient background, H1 = main title, H2 = subtitle, paragraph = badge-style meta

### 2. Table of Contents
- **Many items**: `<!-- _class: toc -->` (2-column auto-layout)
- **Few items (4-5)**: `<!-- _class: toc-focus -->` (large numbered single column)

### 3. Column Layouts

**Card Type (with background/border)**:
- **2 Columns**: `<!-- _class: cols-2 -->`
- **3 Columns**: `<!-- _class: cols-3 -->`
- **Structure**:
  ```html
  <div class="columns">
    <div class="col">Content 1</div>
    <div class="col">Content 2</div>
  </div>
  ```

**Simple Type (no background)**:
- **2 Columns**: `<!-- _class: split-2 -->`
- **3 Columns**: `<!-- _class: split-3 -->`
- **Structure**: Use plain `<div>` instead of `<div class="col">`

### 4. 4-Quadrant Matrix
- **Class**: `<!-- _class: grid-quadrant -->`
- **Structure**:
  ```html
  <div class="grid">
    <div class="cell">Q1</div>
    <div class="cell">Q2</div>
    <div class="cell">Q3</div>
    <div class="cell">Q4</div>
  </div>
  ```
- **Side-image cell**: `<div class="cell side">` for image + text

### 4-2. Sharp Grid (Border-Only)
- **Class**: `<!-- _class: grid-sharp -->`
- **Structure**: Same as `grid-quadrant`
- **Features**: Transparent background, border-only, minimalist

### 5. Information Density Control
- **Slightly dense (20px)**: `<!-- _class: dense -->`
- **Very dense (17px)**: `<!-- _class: extra-dense -->`

### 5-2. Fine-Grained Font Scale
Use `<style scoped>` with `--font-scale` CSS variable:

```markdown
<style scoped>
section { --font-scale: 0.85; }
</style>
```

**Available range**: `0.7` (very small) to `1.0` (default)
**Common values**: `0.95`, `0.9`, `0.85` (≈dense), `0.75` (≈extra-dense), `0.7`

**⚠️ IMPORTANT**: Do NOT use `<!-- _style: "..." -->` directive — it doesn't work for CSS variables.

### 6. Profile / Self-Introduction
- **Class**: `<!-- _class: profile -->`
- **Structure**:
  ```html
  <div class="profile-layout">
    <div class="profile-image">
      ![](photo.jpg)
    </div>
    <div class="profile-content">
  # Name
  ## Role
  - Career items
    </div>
  </div>
  ```

### 7. Key Message
- **Class**: `<!-- _class: key-message no-pagination -->`
- **Directives**: `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- **Structure**: Main message in `> blockquote`, supplementary in `p`

## Header / Footer / Pagination Utilities

| Class / Directive | Effect |
|-------------------|--------|
| `no-header` | Hide header |
| `no-footer` | Hide footer |
| `no-pagination` | Hide page number |
| `pagination-left` | Move page number to bottom-left |
| `with-header` | Add top padding (85px) for header |

Combine: `<!-- _class: cover no-pagination no-header no-footer -->`

## Component Guide

### Process & Time-Series
- **Steps**: `<!-- _class: steps -->` (ordered list → side-by-side cards with "STEP N" badges)
- **Timeline**: `<!-- _class: timeline -->` (ordered list → vertical timeline)
  - **IMPORTANT**: Bold date and description must be on same line:
    ```markdown
    1. **2024 Q1** Project kickoff
    2. **2024 Q3** Prototype complete
    ```

### Confirmation Items
- **Checklist**: `<!-- _class: checklist -->` (unordered list → checkmarks)

### Schedules
- **Timetable**: `<!-- _class: timetable -->` (table → highlighted first column)

### Callouts
```html
<div class="callout info">
  <h4>ℹ️ Information</h4>
  Content
</div>
```
**Types**: `info`, `success`, `warning`, `danger`

## Alignment & Images

### Alignment
- **Vertical**: `v-top`, `v-center`/`v-middle`, `v-bottom`
- **Horizontal**: `text-left`, `text-center`, `text-right`
- **Example**: `<div class="col v-center text-center">`

### Images
- **Centered + Shadow**: `![center shadow width:600px](path)`
- **Background Split**: `![bg right:45% shadow](path)`
