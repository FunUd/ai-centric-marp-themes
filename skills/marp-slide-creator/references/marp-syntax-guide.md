# Marp Syntax & Reference Guide

This file contains detailed Marp syntax, directives, image formatting, and export commands.
Consult this file only when you need specific syntax details.

## 1. Directives

### Global Directives
| Directive | Purpose | Example |
|-----------|---------|---------|
| `marp` | Enable Marp | `marp: true` |
| `theme` | CSS theme | `theme: azure-clarity` |
| `paginate` | Page numbers | `paginate: true` |
| `header` | Global header | `header: "Report"` |
| `footer` | Global footer | `footer: "© 2026"` |
| `size` | Dimensions | `size: 16:9` |

### Local Directives (Per-Slide)
Apply to current slide only. Prefix with `_`:

```markdown
<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->
```

> **⚠️ CRITICAL ANTI-PATTERN: DO NOT REPEAT GLOBAL DIRECTIVES!**
> Do not use `_paginate: true`, `_header: "..."`, or `_footer: "..."` on every single slide. If you declared `paginate: true` or `header: "..."` in the global frontmatter at the top of the file, it automatically applies to all slides. Only use local directives like `_paginate: false` or `_header: ""` when you want to specifically HIDE them for a single slide (like a cover slide).

## 2. Image Syntax

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

## 3. Export & Delivery

For PDF/PPTX targets, treat the exported file as the source of truth. Re-check any slide that uses dense code, Mermaid, tables, or small text.

```powershell
# HTML
npx -y @marp-team/marp-cli --no-stdin --allow-local-files --theme themes/theme.css slides.md -o output.html

# PDF
npx -y @marp-team/marp-cli --no-stdin --allow-local-files --theme themes/theme.css slides.md -o output.pdf

# PowerPoint
npx -y @marp-team/marp-cli --no-stdin --allow-local-files --theme themes/theme.css slides.md -o output.pptx

# PNG images (all slides)
npx -y @marp-team/marp-cli --no-stdin --allow-local-files --theme themes/theme.css slides.md --images png
```

### PDF Options
```powershell
# With presenter notes
npx -y @marp-team/marp-cli --no-stdin --allow-local-files --pdf-notes slides.md -o output.pdf

# With bookmarks
npx -y @marp-team/marp-cli --no-stdin --allow-local-files --pdf-outlines slides.md -o output.pdf
```

## 4. Quick Reference: Common Patterns

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
