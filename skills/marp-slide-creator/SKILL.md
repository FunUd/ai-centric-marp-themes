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
7. [Export & Delivery](#7-export--delivery)

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

This section is critical for AI-driven slide creation. It enables the AI to see the rendered output and iterate autonomously.

### Prerequisites

- **Marp CLI**: Available via `npx @marp-team/marp-cli`
- **VSCode Extension**: `marp-team.marp-vscode` (for human users' live preview)
- **Browser tool**: For AI to visually inspect rendered slides

### Step-by-Step: AI Self-Review Process

The AI can preview Marp slides by converting them to HTML and opening in a browser. Follow this workflow:

#### Step 1: Generate HTML Preview

```powershell
npx -y @marp-team/marp-cli --no-stdin --theme <path-to-theme.css> <path-to-slide.md> -o <output-path>/preview.html
```

**Example:**
```powershell
npx -y @marp-team/marp-cli --no-stdin --theme themes/azure-clarity.css samples/azure-clarity-sample.md -o preview.html
```

**Important flags:**
- `--no-stdin`: Prevents CLI from waiting for stdin input (required in automated environments)
- `--theme`: Path to custom theme CSS file
- `-o`: Output file path

#### Step 2: Serve and Open in Browser

Start a temporary local server and open the preview:

```powershell
python -m http.server 8080
```

Then use the browser tool to navigate to `http://localhost:8080/preview.html`.

#### Step 3: Capture Screenshots & Evaluate

Use the browser tool to:
1. Navigate through each slide (click navigation arrows or use arrow keys)
2. Capture screenshots of each slide
3. Evaluate against the quality checklist (see Section 6)

#### Step 4: Fix Issues & Re-Preview

After identifying problems:
1. Edit the Markdown file to fix issues
2. Re-run the Marp CLI to regenerate HTML
3. Refresh the browser to verify fixes

#### Step 5: Clean Up

After review is complete:
1. Stop the local server
2. Delete the temporary `preview.html` file

### Automated Preview Workflow (Summary)

```
Edit .md → Run Marp CLI → Start server → Browser screenshot → Evaluate → Fix → Repeat
```

### VSCode Integration (For Human Users)

Instruct users to set up their workspace for live preview:

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
3. Open the `.md` file and use VSCode's built-in Markdown preview (`Ctrl+Shift+V` or `Cmd+Shift+V`)
4. The preview updates in real-time as you edit

### Slide Content Overflow Diagnostic

Marp for VS Code has an experimental diagnostic for content overflow:
- Setting: `markdown.marp.diagnostics.slideContentOverflow`
- Warns when slide content overflows the safe area defined by slide padding
- Only available while the Markdown preview is open

---

## 5. Content Overflow Solutions

When content doesn't fit within a slide, use these techniques in order of preference:

### 5.1 Use the `style` Directive to Reduce Font Size (Per-Slide)

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

### 5.2 Use the Front-matter `style` Directive (Global)

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

### 5.3 Use CSS Utility Classes

If the theme provides utility classes like `text-small` or `text-large`:

```markdown
<div class="text-small">

- Dense content here
- More items

</div>
```

### 5.4 Split Content Across Multiple Slides

When content is truly too much for one slide, break it into parts:

```markdown
---

# Topic (1/2)

- First half of points...

---

# Topic (2/2)

- Second half of points...
```

### 5.5 Image Size Adjustments

When images overflow or dominate the slide:

```markdown
<!-- Instead of full-width image: -->
![width:800px](large-image.jpg)

<!-- Reduce to fit: -->
![width:500px](large-image.jpg)

<!-- Or use background with split for text+image layouts: -->
![bg right:45%](large-image.jpg)
```

### 5.6 Table Overflow

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

### 5.7 Code Block Overflow

For long code blocks:

```markdown
<style scoped>
section pre code { font-size: 14px; line-height: 1.3; }
</style>
```

### Decision Matrix for Overflow

| Situation                     | Best Solution                                   |
|------------------------------|------------------------------------------------|
| Bullet points overflow        | Reduce font-size via `<style scoped>`, or split |
| Table too wide               | Reduce table font-size, or use abbreviations     |
| Image too large              | Use `width:` keyword to resize                   |
| Code block too long          | Reduce code font-size, or truncate example        |
| Mixed content overflow       | Combine `<style scoped>` + image resize           |
| Content fundamentally too much| Split across 2+ slides                           |

---

## 6. Quality Checklist

Use this checklist when reviewing each slide:

### Layout & Readability
- [ ] All text is fully visible within the slide boundaries
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

### Structural
- [ ] First slide is a cover/title slide
- [ ] Pagination is hidden on cover and closing slides
- [ ] Headers/footers are hidden where appropriate (cover, key-message)
- [ ] Slide transitions feel logical

### Content
- [ ] Each slide conveys a single main idea
- [ ] Bullet points are concise (not paragraphs)
- [ ] Tables have clear headers
- [ ] Images serve a purpose (not decorative filler)

---

## 7. Export & Delivery

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
