---
name: marp-slide-creator
description: Activate this skill when writing or editing Marp Markdown files after the outline is approved, or when the user wants to fix layout issues, resolve content overflow, preview slides, or export to PDF/PPTX. This skill handles the implementation phase: Marp syntax, directives, image placement, diagnostics, and the preview feedback loop. For content planning and outline creation, use slide-content-designer first.
---

# Marp Slide Creator

A comprehensive guide for creating high-quality Marp presentations using AI.

## 1. Marp Fundamentals

### What is Marp?

Marp (Markdown Presentation Ecosystem) converts Markdown into slide decks:
- **Marpit**: Core framework (Markdown + CSS → slides)
- **Marp Core**: Extended Marpit with built-in themes
- **Marp CLI**: Command-line tool for export (HTML/PDF/PPTX/PNG)
- **Marp for VS Code**: Extension for live preview

### File Organization

**Required Structure:**
```
slides/
└── project-name/
    ├── project-name.md
    └── assets/
        ├── images/
        └── icons/
```

### Creating a New Project

> **⚠️ IMPORTANT: Never use shell commands** (PowerShell/Bash) to create directories. Use the Python setup script for cross-platform compatibility.

```python
python skills/marp-slide-creator/scripts/setup-slide-project.py my-presentation
```

### Basic Slide Structure

```markdown
---
marp: true
theme: azure-clarity
paginate: true
header: "Header Text"
footer: "Footer Text"
---

# Slide 1 Title

Content here.

---

# Slide 2 Title

More content.
```

### Front-matter Directives (Global)

| Directive | Purpose | Example |
|-----------|---------|---------|
| `marp` | Enable Marp | `marp: true` |
| `theme` | CSS theme | `theme: azure-clarity` |
| `paginate` | Page numbers | `paginate: true` |
| `header` | Global header | `header: "Report"` |
| `footer` | Global footer | `footer: "© 2026"` |
| `size` | Dimensions | `size: 16:9` |

## 2. Slide Structure & Directives

### Local Directives (Per-Slide)

Apply to current slide only. Prefix with `_`:

```markdown
<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->
```

| Directive | Purpose | Example |
|-----------|---------|---------|
| `_class` | Apply CSS class | `<!-- _class: cover -->` |
| `_paginate` | Override pagination | `<!-- _paginate: false -->` |
| `_header` | Override header | `<!-- _header: "" -->` |
| `_footer` | Override footer | `<!-- _footer: "" -->` |

### Presenter Notes

```markdown
# Slide Content

Visible content here.

<!--
Presenter notes (only in presenter view)
-->
```

## 3. Image Syntax

### Inline Images

```markdown
![width:200px](image.jpg)
![height:150px](image.jpg)
![w:200 h:150](image.jpg)
![center shadow width:800px](image.jpg)
```

### Background Images

```markdown
![bg](image.jpg)                      <!-- Full background -->
![bg cover](image.jpg)                <!-- Scale to fill -->
![bg contain](image.jpg)              <!-- Scale to fit -->
![bg left:40%](image.jpg)             <!-- Split layout -->
![bg right:45% shadow](image.jpg)     <!-- With shadow -->
```

### Multiple Backgrounds

```markdown
![bg](image1.jpg)
![bg](image2.jpg)
![bg vertical](image3.jpg)            <!-- Vertical stack -->
```

### Image Filters

```markdown
![blur:10px](image.jpg)
![brightness:1.5](image.jpg)
![grayscale:1](image.jpg)
![opacity:.5](image.jpg)
```

## 4. Preview & Feedback Loop

> **⚠️ MANDATORY: Preview confirmation is required, not optional.**
> Slide creation is NOT complete until every slide has been visually verified.

### Stage 1: Editor Diagnostic

Marp for VS Code includes an experimental `slide-content-overflow` diagnostic. Enable `markdown.marp.diagnostics.slideContentOverflow` and keep the Markdown preview open to surface overflow warnings directly in the editor.

### Stage 2: Batch Diagnostic Helper

If you want the same overflow check from the terminal, use the helper script:

```powershell
python skills/marp-slide-creator/scripts/marp-diagnostics.py slides/my-deck/my-deck.md
```

This helper exports `slides/my-deck/preview.html`, runs the DOM extractor, and writes `slides/my-deck/assets/dom-metrics.json`.

### Workflow

```
1. Edit Markdown
2. Run the editor diagnostic or `marp-diagnostics.py`
3. If issues -> fix -> repeat
4. If clean -> export HTML and run the DOM extractor for a deeper pass
5. Analyze metrics
6. If issues -> fix -> repeat
7. Complete
```

### Stage 3: DOM Metrics Extraction

If you already have a rendered HTML file, skip the export step and run the extractor directly.

**Step 1: Export HTML**
```powershell
npx -y @marp-team/marp-cli --no-stdin --theme themes/azure-clarity.css slides/my-deck/my-deck.md -o slides/my-deck/preview.html
```

**Step 2: Run DOM Extractor**
```powershell
python skills/marp-slide-creator/scripts/marp-dom-extractor.py slides/my-deck/preview.html -o slides/my-deck/assets/dom-metrics.json
```

**Step 3: Analyze JSON**

Auto-detected risk flags:
- `CONTENT_OVERFLOW`: Content past slide bottom
- `DENSE_TEXT`: >600 characters
- `MANY_LINES`: >20 lines
- `IMAGE_NO_SRC`: Missing image source
- `IMAGE_BROKEN`: Failed to load

Manual checks from `elements` array:
- Element overlap
- Text truncation (`clipped: true`)
- Unbalanced layout
- Missing expected images

## 5. Content Overflow Solutions

Priority order (most design-friendly first):

### 5.1 Content Refinement
- Bulletize paragraphs
- Remove redundancy
- Stick to "1 slide = 1 message"
- Use active voice

### 5.2 Per-Slide Font Size
```markdown
<style scoped>
section { font-size: 20px; }
section li { font-size: 18px; }
</style>
```

### 5.3 Global Font Size
```markdown
---
style: |
  section { font-size: 22px; }
---
```

### 5.4 CSS Utility Classes
```markdown
<div class="text-small">
Content here
</div>
```

### 5.5 Split Slides
```markdown
# Topic (1/2)
- First half

---

# Topic (2/2)
- Second half
```

### 5.6 Image Resize
```markdown
![width:500px](image.jpg)
![bg right:45%](image.jpg)
```

### 5.7 Table Overflow
```markdown
<style scoped>
section table { font-size: 16px; }
</style>
```

## 6. Quality Checklist

Layout:
- [ ] No text overflow/cutoff
- [ ] Images don't overlap text
- [ ] Consistent margins
- [ ] Lists are left-aligned (not centered)

Typography:
- [ ] Clear heading hierarchy
- [ ] Readable font size (≥16px)
- [ ] Purposeful emphasis

Visual:
- [ ] Consistent color scheme
- [ ] Good text/background contrast
- [ ] Aligned tables
- [ ] Diagrams/icons where appropriate

Content:
- [ ] One idea per slide
- [ ] Concise bullet points
- [ ] Images serve a purpose

## 7. Visual Aids & Icons

### SVG Icons

After drafting, review for empty space. Add icons from `marp-svg-icon-placer` skill catalog.

**Always activate `marp-svg-icon-placer` skill before selecting icons.**

### Diagram Choice

Use the simplest visual that communicates the idea clearly:

1. Start with SVG icons for small accents, status markers, and lightweight labels.
2. Use Mermaid when the slide needs a sequence, flow, state, or relationship diagram that can be expressed cleanly in code.
3. Use `.drawio.svg` when Mermaid is too limited, when precise layout matters, or when the diagram needs richer shape control.
4. If drawio still cannot represent it cleanly, or the quality is not good enough, ask the user to provide a source image.

### Mermaid Diagrams

Use Mermaid-style code blocks when a diagram is easier to read as structured text than as a hand-built graphic.

```markdown
<pre class="mermaid">
sequenceDiagram
    participant A as Client
    participant B as Server

    A->>B: HTTP request (GET /data)
    B->>A: HTTP response (200 OK + JSON)
</pre>
```

Good Mermaid use cases:
- Sequence diagrams
- Flowcharts
- Simple state transitions
- Dependency or relationship diagrams

Prefer `.drawio.svg` instead when:
- The diagram needs precise positioning or many cross-links
- The slide must match a specific visual style
- The diagram is too dense to read comfortably in Mermaid

### Editable Diagrams

Use `.drawio.svg` format for complex diagrams (architecture, workflows).

## 8. Contrast-Aware Design

**Core Rule:** Emphasized elements and their containers must have different background colors.

### Universal Checklist

1. What is the most important element on this slide?
2. Does it have a background color?
3. What is directly behind it?
4. Are the colors similar? If yes, emphasis is lost.
5. Fix: Change layout, move element, or change color.

### Anti-Patterns

- **DO NOT** place `callout.info` inside `cols-2`/`cols-3` (same pale background)
- **DO NOT** place pale callouts on matching-tone background images
- **DO NOT** assume documented classes are visually compatible

## 9. Export & Delivery

### Export via Marp CLI

```powershell
# HTML
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md -o output.html

# PDF
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md -o output.pdf

# PowerPoint
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md -o output.pptx

# PNG images (all slides)
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md --images png
```

### PDF Options

```powershell
# With presenter notes
npx -y @marp-team/marp-cli --no-stdin --pdf-notes slides.md -o output.pdf

# With bookmarks
npx -y @marp-team/marp-cli --no-stdin --pdf-outlines slides.md -o output.pdf
```

## Quick Reference: Common Patterns

### Cover Slide
```markdown
<!-- _class: cover subtitle meta -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->

# Title
## Subtitle
Author | Date
```

### Section Divider
```markdown
<!-- _class: key-message no-pagination -->
<!-- _header: "" -->
<!-- _footer: "" -->

> Key Takeaway
```

### Two-Column Layout
```markdown
<!-- _class: cols-2 -->

<div class="columns">
<div class="col">

### Left
Content

</div>
<div class="col">

### Right
Content

</div>
</div>
```

### Image + Text Split
```markdown
![bg right:45%](image.jpg)

# Title
- Point 1
- Point 2
```
