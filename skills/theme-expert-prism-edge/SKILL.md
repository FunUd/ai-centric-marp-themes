---
name: theme-expert-prism-edge
description: A skill for maximizing the Prism Edge theme in Marp once the theme has already been chosen. Use when the user wants bold, high-impact theme-specific layout guidance for an existing deck direction, not for early-stage planning.
---

# Prism Edge Theme Expert

This skill provides guidelines for using the Prism Edge theme — designed for **high-impact, modern, professional presentations** with bold indigo-cyan gradients, sharp edges, and sophisticated cover designs.

Use this skill after the content structure is decided. For outline planning or story shaping, use `slide-content-designer` or the relevant domain skill first.

## Basic Principles

Create **visually memorable, modern, professional slides**. Leverage:
- Advanced cover designs (wave, diagonal, noir, aurora)
- Asymmetric layouts and bold typography
- Glass panels, gradient text, accent borders
- Dark slide modes for dramatic emphasis

## Layout Guide by Use Case

### 1. Cover Slides — Choose Your Impact

#### A. Classic Cover
- **Classes**: `<!-- _class: cover subtitle meta -->`
- Features: Clean with soft decorative circle

#### B. Wave Cover
- **Classes**: `<!-- _class: cover-wave subtitle meta -->`
- Features: SVG wave layers at bottom

#### C. Diagonal Cover
- **Classes**: `<!-- _class: cover-diagonal -->`
- Features: Sharp diagonal split (indigo right, white left)

#### D. Noir Cover
- **Classes**: `<!-- _class: cover-noir -->`
- Features: Dark with multi-layer radial gradients

#### E. Aurora Cover
- **Classes**: `<!-- _class: cover-aurora subtitle meta -->`
- Features: Soft rotating gradient blobs

All covers: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`

### 2. Hero Slide
- **Class**: `<!-- _class: hero no-pagination -->`
- **Directives**: `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Features: H1 at 72px, centered

### 3. Title Only
- **Class**: `<!-- _class: title-only no-pagination -->`
- Features: H1 at 64px, left-aligned, no border

### 4. Table of Contents
- **Many items**: `<!-- _class: toc -->`
- **Few items**: `<!-- _class: toc-focus -->`

### 5. Column Layouts

**Card Type**:
- `<!-- _class: cols-2 -->` or `<!-- _class: cols-3 -->`
- Structure: `<div class="columns"><div class="col">...</div></div>`

**Simple Type**:
- `<!-- _class: split-2 -->` or `<!-- _class: split-3 -->`

### 6. Asymmetric Split (65:35)
- **Standard**: `<!-- _class: split-asym -->` (3fr : 2fr)
- **Reverse**: `<!-- _class: split-asym-reverse -->` (2fr : 3fr)

### 7. 4-Quadrant Matrix
- **Soft Grid**: `<!-- _class: grid-quadrant -->` (with backgrounds)
- **Sharp Grid**: `<!-- _class: grid-sharp -->` (border-only, no backgrounds)
- Structure: `<div class="grid"><div class="cell">...</div></div>`

### 8. Accent Left Border
- **Class**: `<!-- _class: accent-left -->`
- Adds gradient border on left edge

### 9. Background Patterns
- **Grid**: `<!-- _class: bg-grid -->` (40px grid lines)
- **Noise**: `<!-- _class: bg-noise -->` (radial speckles)

### 10. Glass Panel
```html
<div class="glass-panel">
### Heading
Content readable over busy backgrounds
</div>
```

### 11. Gradient Text
`<span class="gradient-text">78% Growth</span>`

### 12. Underline Accent
`<span class="underline-accent">Key Point</span>`

### 13. Section Number
`<div class="section-number">01</div>` (120px faded background number)

### 14. Highlight Box
```html
<div class="highlight-box">
### Key Insight
Content
</div>
```

### 15. Large Quote
```html
<div class="quote-large">
Statement text
</div>
```

### 16. Information Density
- **Slightly dense (18px)**: `<!-- _class: dense -->`
- **Very dense (15px)**: `<!-- _class: extra-dense -->`

### 16-2. Fine-Grained Font Scale
```markdown
<style scoped>
section { --font-scale: 0.85; }
</style>
```
Range: `0.7` to `1.0`. Common: `0.95`, `0.9`, `0.85`, `0.75`, `0.7`

### 17. Profile
- **Class**: `<!-- _class: profile -->`
- Structure: `<div class="profile-layout">` with `profile-image` and `profile-content`

### 18. Key Message
- **Class**: `<!-- _class: key-message no-pagination -->`

## Header / Footer / Pagination

| Class | Effect |
|-------|--------|
| `no-header` | Hide header |
| `no-footer` | Hide footer |
| `no-pagination` | Hide page number |
| `pagination-left` | Move to bottom-left |
| `with-header` | Add top padding |

## Component Guide

### Process & Timeline
- **Steps**: `<!-- _class: steps -->`
- **Timeline**: `<!-- _class: timeline -->`
  - **IMPORTANT**: Bold date and text on same line

### Checklist
- **Class**: `<!-- _class: checklist -->`

### Timetable
- **Class**: `<!-- _class: timetable -->`

### Callouts
```html
<div class="callout info">
  <h4>Information</h4>
  Content
</div>
```
Types: `info`, `success`, `warning`, `danger`

### Badges
`<span class="badge">Label</span>`
Types: `badge`, `badge primary`, `badge success`, `badge warning`, `badge danger`

## Alignment & Images

### Alignment
- Vertical: `v-top`, `v-center`, `v-bottom`
- Horizontal: `text-left`, `text-center`, `text-right`

### Images
- `![center shadow width:600px](path)`
- `![bg right:45% shadow](path)`

## Text & Background Utilities

| Class | Effect |
|-------|--------|
| `text-primary` | Indigo |
| `text-accent` | Deep slate |
| `text-success` | Emerald |
| `text-warning` | Amber |
| `text-danger` | Red |
| `text-cyan` | Cyan |
| `text-magenta` | Magenta |
| `text-large` | 1.3× size |
| `text-small` | 0.85× size |
| `bg-pale` | Pale indigo background |
| `bg-light` | Light indigo background |
| `bg-dark` | Deep navy background |
| `stat-number` | 56px bold metric |
| `stat-label` | Uppercase label |

## Design Tips

- Choose covers intentionally (diagonal for pitches, noir for keynotes, wave for tech talks)
- Embrace asymmetry (`split-asym`, `grid-sharp`)
- Avoid rounded corners (theme is sharp)
- Use `gradient-text` for KPIs
- Use `glass-panel` for busy backgrounds
- Use `stat-number` + `stat-label` for metrics
- Use `section-number` for chapter breaks
- Use `highlight-box` for key insights
- Sharp > Soft
