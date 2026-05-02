---
name: marp-slide-creator
description: Create, edit, and troubleshoot Marp presentation slides with professional quality. Use this skill whenever the user asks to create slides, presentations, or decks in Marp Markdown, or when they want to fix layout issues, preview slides, adjust content overflow, or improve slide design. Also use when the user mentions Marp, slide deck, presentation markdown, or wants to convert slides to PDF/PPTX. This skill enables AI to autonomously preview, evaluate, and iterate on slide quality.
---

# Marp Slide Creator

A comprehensive guide for creating high-quality Marp presentations using AI. This skill covers everything from basic Marp syntax to advanced self-feedback loops for autonomous slide quality improvement.

## Table of Contents

1. [Marp Fundamentals](#1-marp-fundamentals)
2. [Slide Structure & Directives](#2-slide-structure--directives)
3. [Image Syntax](#3-image-syntax)
4. [Preview & Feedback Loop](#4-preview--feedback-loop)
5. [Content Overflow Solutions](#5-content-overflow-solutions)
6. [Quality Checklist](#6-quality-checklist)
7. [Visual Aids & Diagrams](#7-visual-aids--diagrams)
8. [Export & Delivery](#8-export--delivery)

---

## 1. Marp Fundamentals

### What is Marp?

Marp (Markdown Presentation Ecosystem) converts Markdown into slide decks. It consists of:

- **Marpit**: The core framework that transforms Markdown + CSS into slides
- **Marp Core**: Extended Marpit with built-in themes and plugins
- **Marp CLI**: Command-line tool for converting `.md` → HTML / PDF / PPTX / images
- **Marp for VS Code**: Extension for live preview and export within VS Code

### Basic Slide Structure

Every Marp file starts with a YAML front-matter declaring `marp: true`, followed by Markdown content. Slides are separated by `---` (horizontal rule).

### File Organization

To keep the workspace clean and maintainable, always organize your presentation files as follows:

1.  **Base Directory**: All presentations should reside in the `slides/` directory.
2.  **Project Folder**: Create a dedicated subfolder for each individual slide deck (e.g., `slides/project-name/`).
3.  **Files**:
    *   Place the Markdown file (`.md`) directly inside the project folder.
    *   Create an `assets/` subfolder for all images, icons, and diagrams.

**Example Structure:**
```text
slides/
└── marketing-plan/
    ├── marketing-plan.md
    └── assets/
        ├── logo.svg
        └── overview-diagram.drawio.svg
```

---

```markdown
---
marp: true
theme: default
paginate: true
header: "Header Text"
footer: "Footer Text"
---

# Slide 1 Title

Content of the first slide.

---

# Slide 2 Title

Content of the second slide.
```

### Front-matter Directives (Global)

These apply to the entire deck:

| Directive    | Purpose                        | Example                         |
|-------------|-------------------------------|--------------------------------|
| `marp`      | Enable Marp rendering          | `marp: true`                    |
| `theme`     | Specify CSS theme              | `theme: azure-clarity`          |
| `paginate`  | Show page numbers              | `paginate: true`                |
| `header`    | Global header text             | `header: "Project Report"`      |
| `footer`    | Global footer text             | `footer: "© 2026 Company"`     |
| `size`      | Slide dimensions               | `size: 16:9`                    |
| `math`      | Math rendering engine          | `math: mathjax`                 |
| `style`     | Inline CSS for the entire deck | `style: "section { font-size: 20px; }"` |

---

## 2. Slide Structure & Directives

### Local Directives (Per-Slide)

Local directives apply only to the current slide. Prefix with `_` inside an HTML comment:

```markdown
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->

# Title Slide
```

| Directive      | Purpose                              | Example                         |
|---------------|-------------------------------------|--------------------------------|
| `_class`      | Apply CSS class to this slide        | `<!-- _class: cover -->`        |
| `_paginate`   | Override pagination for this slide   | `<!-- _paginate: false -->`     |
| `_header`     | Override header (empty = hide)       | `<!-- _header: "" -->`          |
| `_footer`     | Override footer (empty = hide)       | `<!-- _footer: "" -->`          |
| `_color`      | Override text color                  | `<!-- _color: white -->`        |
| `_backgroundColor` | Override background color       | `<!-- _backgroundColor: #000 -->`|

### Class Combinations

Multiple classes can be combined in a single `_class` directive. The theme CSS determines which classes are available:

```markdown
<!-- _class: cover subtitle meta -->
```

### Presenter Notes

Add notes that appear only in presenter view. Place them after a slide's content using HTML comment syntax:

```markdown
# Slide Content

This is visible on the slide.

<!--
This is a presenter note.
Only visible in presenter view.
-->
```

---

## 3. Image Syntax

Marp extends standard Markdown image syntax with powerful keywords placed in the alt text.

### Inline Images

```markdown
![width:200px](image.jpg)              <!-- Set width -->
![height:150px](image.jpg)             <!-- Set height -->
![w:200 h:150](image.jpg)             <!-- Shorthand -->
![width:100%](image.jpg)              <!-- Percentage width -->
![center](image.jpg)                   <!-- Center align (theme-dependent) -->
![shadow](image.jpg)                   <!-- Drop shadow (theme-dependent) -->
![center shadow width:800px](image.jpg)  <!-- Combine keywords -->
```

### Background Images

Add `bg` keyword to use the image as slide background:

```markdown
![bg](image.jpg)                       <!-- Full background -->
![bg cover](image.jpg)                 <!-- Scale to fill (default) -->
![bg contain](image.jpg)              <!-- Scale to fit -->
![bg fit](image.jpg)                   <!-- Alias for contain -->
![bg auto](image.jpg)                  <!-- Original size -->
![bg 150%](image.jpg)                  <!-- Scale percentage -->
```

### Split Backgrounds

Split the slide into content area + image area:

```markdown
![bg left](image.jpg)                 <!-- Image on left, content on right -->
![bg right](image.jpg)                <!-- Image on right, content on left -->
![bg left:40%](image.jpg)             <!-- Custom split ratio -->
![bg right:45% shadow](image.jpg)     <!-- With shadow effect -->
```

### Multiple Backgrounds

Stack multiple background images:

```markdown
![bg](image1.jpg)
![bg](image2.jpg)
![bg](image3.jpg)
```

Use `vertical` keyword to arrange vertically instead of horizontally:

```markdown
![bg vertical](image1.jpg)
![bg](image2.jpg)
```

### Image Filters

Apply CSS filters via alt text keywords:

```markdown
![blur:10px](image.jpg)
![brightness:1.5](image.jpg)
![contrast:200%](image.jpg)
![grayscale:1](image.jpg)
![sepia:50%](image.jpg)
![opacity:.5](image.jpg)
![brightness:.8 sepia:50%](image.jpg)  <!-- Multiple filters -->
```

---

## 4. Preview & Feedback Loop

> **⚠️ MANDATORY: Preview confirmation is a required step, not optional.**
> Slide creation is NOT complete until every slide has been visually verified. Do NOT skip this step or declare the task done without completing it.

This section is critical for AI-driven slide creation. It enables the AI to see the rendered output and iterate autonomously.

### Prerequisites

- **Marp CLI**: Available via `npx @marp-team/marp-cli`
- **VSCode Extension**: `marp-team.marp-vscode` (for human users' live preview)

### Primary Method: PNG Export (Recommended)

The most reliable approach is to export all slides as PNG images using Marp CLI's `--images png` flag. This requires **no server, no browser tool**, and produces files the AI can read directly.

#### Step 1: Export All Slides as PNG

```powershell
npx -y @marp-team/marp-cli --no-stdin --theme <path-to-theme.css> --images png --image-scale 1 <path-to-slide.md> -o <slides-dir>/assets/preview.png
```

Marp CLI will output one PNG per slide, named sequentially:
`preview.001.png`, `preview.002.png`, `preview.003.png`, ...

**Example:**
```powershell
npx -y @marp-team/marp-cli --no-stdin --theme themes/azure-clarity.css --images png --image-scale 1 slides/my-deck/my-deck.md -o slides/my-deck/assets/preview.png
```

**Key flags:**
- `--images png`: Export every slide as a PNG file
- `--image-scale 1`: Use 1× scale (default 2× is unnecessarily large for review)
- `--no-stdin`: Prevents CLI from waiting for stdin (required in automated environments)
- `--allow-local-files`: Required when the slide references local images or SVGs
- `-o`: Base output path; CLI appends `.001.png`, `.002.png`, etc.

> **Note**: If the slide uses local image files (e.g., `assets/icon.svg`), add `--allow-local-files` to the command. Without it, local assets will be blocked and appear missing in the output.

#### Step 2: Read and Evaluate Each PNG

Use the `readFile` tool (or equivalent image-reading tool) to load each PNG and evaluate it against the Quality Checklist (Section 6). No server or browser required.

```
slides/my-deck/assets/preview.001.png  ← Slide 1
slides/my-deck/assets/preview.002.png  ← Slide 2
...
```

#### Step 3: Fix Issues & Re-Export

After identifying problems:
1. **Refine Content**: Make text more concise first (see Section 5.1).
2. **Adjust Layout**: Apply technical fixes if needed (see Section 5).
3. **Re-export**: Re-run the PNG export command and re-read the updated images.

#### Step 4: Clean Up

After review is complete, delete all preview PNGs:

```powershell
# Delete all preview PNGs (PowerShell)
Remove-Item slides/my-deck/assets/preview.*.png
```

**Important**: Preview PNGs are temporary artifacts. Always delete them before finishing.

### Automated Preview Script

For convenience, a reusable script is available at `skills/marp-slide-creator/scripts/preview.ps1`. Run it from the workspace root:

```powershell
# Usage: .\skills\marp-slide-creator\scripts\preview.ps1 -SlidePath <md-file> -Theme <css-file>
.\skills\marp-slide-creator\scripts\preview.ps1 -SlidePath slides/my-deck/my-deck.md -Theme themes/azure-clarity.css
```

The script exports PNGs, lists them for review, and prompts for cleanup when done.

### Feedback Loop Summary

```
Edit .md → Export PNGs (Marp CLI) → Read PNGs → Evaluate → Fix → Repeat → Clean up
```

No server. No browser. No manual navigation. Just files.

### When PNG Export Fails

If Marp CLI itself fails (missing Node.js, network issues with npx, etc.):

1. **Report to User**: Explain what failed and provide the exact command to run manually.
2. **Text-Based Review**: Perform a thorough Markdown review for syntax, structure, and content organization.
3. **Suggest VSCode Preview**: Ask the user to verify using the Marp for VS Code extension.

**Example Report**:
> "PNG export failed due to [specific reason]. Please run the following command manually and check the output: `npx -y @marp-team/marp-cli --no-stdin --theme themes/azure-clarity.css --images png slides/your-deck/your-deck.md -o slides/your-deck/assets/preview.png`"

### VSCode Integration (For Human Users)

1. Install the "Marp for VS Code" extension (`marp-team.marp-vscode`)
2. Configure `.vscode/settings.json`:
   ```json
   {
     "markdown.marp.themes": [
       "./themes/azure-clarity.css"
     ],
     "markdown.marp.enableHtml": true
   }
   ```
3. Open the `.md` file and use VSCode's built-in Markdown preview (`Ctrl+Shift+V`)
4. The preview updates in real-time as you edit

### Slide Content Overflow Diagnostic

Marp for VS Code has an experimental diagnostic for content overflow:
- Setting: `markdown.marp.diagnostics.slideContentOverflow`
- Warns when slide content overflows the safe area defined by slide padding
- Only available while the Markdown preview is open

---

## 5. Content Overflow Solutions

When content doesn't fit within a slide, use these techniques in order of preference (starting with the most "design-friendly" approach):

### 5.1 Content Refinement (Editing for Conciseness)

Before reaching for technical hacks, always try to "edit down" the content. This is the best way to maintain professional quality and readability.

- **Bulletize**: Convert long paragraphs into short, punchy bullet points.
- **Remove Redundancy**: Eliminate filler words ("In order to", "Basically", "As we can see").
- **Core Message**: Stick to "1 slide = 1 message". If you have too many points, move secondary information to presenter notes or a separate slide.
- **Active Voice**: Use active voice to shorten sentences (e.g., "The team designed the system" vs. "The system was designed by the team").

### 5.2 Use the `style` Directive to Reduce Font Size (Per-Slide)

Apply inline `<style>` scoped to a single slide using the `scoped` attribute. This is the most targeted approach:

```markdown
---

<style scoped>
section { font-size: 20px; }
section li { font-size: 18px; line-height: 1.4; }
</style>

# Dense Content Slide

- Item 1 with lots of text...
- Item 2 with lots of text...
...
```

### 5.3 Use the Front-matter `style` Directive (Global)

For deck-wide font size adjustment:

```markdown
---
marp: true
theme: azure-clarity
style: |
  section { font-size: 22px; }
  section li { font-size: 20px; }
---
```

### 5.4 Use CSS Utility Classes

If the theme provides utility classes like `text-small` or `text-large`:

```markdown
<div class="text-small">

- Dense content here
- More items

</div>
```

### 5.5 Split Content Across Multiple Slides

When content is truly too much for one slide, break it into parts:

```markdown
---

# Topic (1/2)

- First half of points...

---

# Topic (2/2)

- Second half of points...
```

### 5.6 Image Size Adjustments

When images overflow or dominate the slide:

```markdown
<!-- Instead of full-width image: -->
![width:800px](large-image.jpg)

<!-- Reduce to fit: -->
![width:500px](large-image.jpg)

<!-- Or use background with split for text+image layouts: -->
![bg right:45%](large-image.jpg)
```

### 5.7 Table Overflow

For tables with too many columns or rows:

```markdown
<style scoped>
section table { font-size: 16px; }
section table td, section table th { padding: 6px 10px; }
</style>

| Col1 | Col2 | Col3 | Col4 | Col5 |
|------|------|------|------|------|
| ...  | ...  | ...  | ...  | ...  |
```

### 5.8 Code Block Overflow

For long code blocks:

```markdown
<style scoped>
section pre code { font-size: 14px; line-height: 1.3; }
</style>
```

### Decision Matrix for Overflow

| Situation                     | Best Solution                                   |
|------------------------------|------------------------------------------------|
| Text/Bullets overflow        | **1. Refine text (conciseness)**, 2. `<style scoped>`, 3. Split |
| Table too wide               | 1. Abbreviations/Refinement, 2. Reduce font-size |
| Image too large              | Use `width:` keyword to resize                   |
| Code block too long          | Reduce code font-size, or truncate example        |
| Mixed content overflow       | Refine text + combine `<style scoped>` + resize  |
| Content fundamentally too much| Split across 2+ slides                           |

---

## 6. Quality Checklist

Use this checklist when reviewing each slide:

### Layout & Readability
- [ ] All text is fully visible within the slide boundaries (no overflow/cutoff)
- [ ] Images do not overlap with text
- [ ] Consistent margins and padding across slides
- [ ] Slide is not too sparse (wasted space) or too dense (crowded)

### Typography
- [ ] Heading hierarchy is clear (h1 > h2 > h3)
- [ ] Font size is readable (minimum ~16px for body text)
- [ ] Emphasis (bold, italic) is used purposefully
- [ ] Line height provides comfortable readability

### Visual Design
- [ ] Color scheme is consistent across all slides
- [ ] Background images have appropriate contrast with text
- [ ] Tables are properly aligned and styled
- [ ] Code blocks have syntax highlighting
- [ ] No unnatural empty spaces (use visual aids to fill gaps)
- [ ] Diagrams/Icons are used to aid understanding where appropriate

### Structural
- [ ] First slide is a cover/title slide
- [ ] Pagination is hidden on cover and closing slides
- [ ] Headers/footers are hidden where appropriate (cover, key-message)
- [ ] Slide transitions feel logical

### Content
- [ ] Each slide conveys a single main idea
- [ ] Bullet points are concise (not full paragraphs)
- [ ] Text is refined to fit the slide perfectly while maintaining clarity
- [ ] Tables have clear headers
- [ ] Images serve a purpose (not decorative filler)

---

## 7. Visual Aids & Diagrams

To enhance the visual quality and understanding of slides, follow these guidelines for creating and using visual aids:



### 7.2 Editable Diagrams (.drawio.svg)

For complex diagrams (architecture, workflows, flowcharts) that may require manual refinement by the user:

- **Format**: Use `.drawio.svg`. This allows the image to be rendered as an SVG in the slide but remains editable using the Draw.io / diagrams.net editor (or VS Code extension).
- **Benefit**: Users can "Save as" or edit the file directly to fix small details or translations without needing to recreate the diagram from scratch.

### 7.3 Design Best Practices

- **Consistency**: Use colors from the theme (e.g., Azure blue, dark greys) for all generated visual aids.
- **Simplicity**: Prefer clean, flat designs over complex or cluttered images.
- **Alignment**: Use Marp's background image keywords (`bg right`, `bg left`) to integrate diagrams seamlessly with text.

---

## 8. Contrast-Aware Design Principles

Every slide design decision must preserve the visual hierarchy: **the element you want to emphasize must never blend into its surroundings.** This principle applies universally — regardless of whether you use `cols-2`, `cols-3`, `split-2`, `split-3`, background images, cover slides, or any future CSS classes.

### The Core Rule

> **Emphasized elements and their containers must have different background colors (or tones).**

If both the emphasis element and its surrounding area share the same background color, the emphasis disappears. The audience will not perceive what you intended to highlight.

### How It Manifests in Practice

The themes use several classes that add background colors to regions of a slide. When you place another background-colored element inside one of those regions, you must verify contrast.

**Examples:**

- **Column layouts (`cols-2`, `cols-3`)**: Each `.col` receives a **pale primary-color background** (e.g., light blue). If you place a `callout.info` (same pale blue background) inside a column, the callout merges into the card and loses impact. The same risk applies to `callout.success` if the theme ever used a pale green column background.
- **Split layouts (`split-2`, `split-3`)**: Columns have **no background**. They are safe with any callout because the callout is the only colored region.
- **Background images (`bg left`, `bg right`, full `bg`)**: If the image contains tones similar to a callout’s background, the callout gets buried. A `callout.info` (blue) on a blue-tinted photograph is nearly invisible.
- **Cover / dark-background slides**: Light-colored callouts may work, but always verify that the text inside the callout also has sufficient contrast against the callout’s own background.

### Universal Contrast Checklist

Before finalizing any slide, ask yourself:

1. **What is the single most important element on this slide?** Define the emphasis target explicitly.
2. **Does that element have a background color or strong visual treatment?** (`callout.*`, highlighted boxes, badges, color blocks, etc.)
3. **What is directly behind or around that element?** (column cards, background images, full-slide color overlays, other callouts.)
4. **Are the colors (or tones) of the element and its surroundings the same or similar?** If yes, the emphasis is lost.
5. **What is the simplest change that restores contrast?** Options include:
   - Switch to a layout class without background colors (e.g., `split-2` instead of `cols-2`).
   - Move the emphasized element outside the colored container.
   - Change the callout type to one with a contrasting color (e.g., `callout.warning` or `callout.danger` instead of `callout.info`).
   - Add a border, shadow, or opaque overlay between the background and the element.

### Anti-Patterns to Avoid

These are specific instances of the universal rule. Whenever a new class is introduced, evaluate it through the same lens.

- **Do NOT** place a `callout.info` inside a `cols-2` or `cols-3` column. The callout and the column card share the same pale primary background.
- **Do NOT** place any pale-background callout on top of a background image with matching tones without an overlay or border.
- **Do NOT** assume that because two classes are documented separately, they are visually compatible when combined. Always mentally overlay them.

### Decision Guide

Use this reasoning flow for any class combination, now or in the future:

| Situation | Question to Ask | Typical Fix |
|-----------|----------------|-------------|
| Layout with column cards + callout | Do the column and callout share a background color? | Use a split layout (no column background) or choose a callout with a contrasting color. |
| Background image + callout | Does the image contain tones similar to the callout background? | Add a dark overlay, move the callout to a neutral area, or pick a callout with a strongly contrasting color. |
| Multiple callouts on one slide | Do any two callouts have colors that clash or blend? | Space them apart; avoid placing similar-toned callouts adjacent to each other. |
| New class + existing callout | Does the new class apply a background color to the same region as the callout? | Preview and compare the rendered hex codes or visual tones. If they are within ~15% luminance, change one of them. |

---

## 9. Export & Delivery

### Export via Marp CLI

```powershell
# HTML (default)
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md -o output.html

# PDF (requires Chrome/Edge/Firefox installed)
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md -o output.pdf

# PowerPoint
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md -o output.pptx

# PNG images (all slides)
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md --images png

# First slide only (for thumbnails/OGP)
npx -y @marp-team/marp-cli --no-stdin --theme themes/theme.css slides.md --image png
```

### Export via VSCode

1. Open the Markdown file in VSCode
2. Click the Marp icon in the toolbar
3. Select "Export slide deck..."
4. Choose format: HTML / PDF / PPTX / PNG / JPEG

### PDF-Specific Options

```powershell
# Add presenter notes as PDF annotations
npx -y @marp-team/marp-cli --no-stdin --pdf-notes slides.md -o output.pdf

# Add PDF bookmarks/outlines
npx -y @marp-team/marp-cli --no-stdin --pdf-outlines slides.md -o output.pdf
```

---

## Quick Reference: Common Patterns
### 7.1 SVG Icons and Images

After drafting all slides, review every slide for unnatural empty space or text-only layouts. Any such slide MUST have an icon or visual element added before the task is considered complete.

When a slide has unnatural empty space or a concept is better explained visually, use an icon from the `marp-svg-icon-placer` skill catalog, or create a custom SVG and place it in the `assets/` directory.

- **Usage Cases**:
  - Filling large empty areas that make the slide look unbalanced.
  - Representing abstract concepts with simple icons.
  - Creating custom illustrations that match the theme's color palette.
- **Organization**: Always store generated assets in the `assets/` folder relative to the markdown file.
- **Icon Source**: Always check `marp-svg-icon-placer` skill catalog first before generating new SVGs.

### Cover Slide
```markdown
<!-- _class: cover subtitle meta -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->

# Presentation Title

## Subtitle Goes Here

Author Name | Department | Date
```

### Section Divider
```markdown
<!-- _class: key-message no-pagination -->
<!-- _header: "" -->
<!-- _footer: "" -->

> Key Takeaway Statement

Supporting context below the main message.
```

### Two-Column Layout
```markdown
<!-- _class: cols-2 -->

# Comparison

<div class="columns">
<div class="col">

### Option A

- Point 1
- Point 2

</div>
<div class="col">

### Option B

- Point 1
- Point 2

</div>
</div>
```

### Image + Text (Split Background)
```markdown
# Topic Title

![bg right:45%](image.jpg)

- Point 1
- Point 2
- Point 3
```
