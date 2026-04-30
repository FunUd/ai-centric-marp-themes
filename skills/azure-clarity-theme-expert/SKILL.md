---
name: azure-clarity-theme-expert
description: A skill for maximizing the use of the Azure Clarity theme (for Marp) to create and layout professional business presentations. Trigger this skill when the user wants to design, modify, or optimize slides using the Azure Clarity theme, or when they want to beautifully present specific content (TOC, comparisons, schedules, etc.).
---

# Azure Clarity Theme Expert

This skill provides guidelines for appropriately using the classes and layout patterns provided by the custom Marp theme "Azure Clarity" to create beautiful and effective slides.

It assumes you already understand the basics of Marp and slide structure, and focuses specifically on **"how to utilize features unique to this theme."**

## 🎯 Basic Principles

In the Azure Clarity theme, the most important thing is to apply the optimal CSS classes (`<!-- _class: ... -->`) or HTML structures according to the slide's intent (use case). You can easily achieve rich layouts that cannot be expressed with plain Markdown alone.

---

## 📐 Guide by Layout and Use Case

### 1. Cover / Title Slide
The "face" of your presentation. A blue gradient is applied to the background.

- **Classes to use**: `<!-- _class: cover subtitle meta -->`
- **Concurrent directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- **Features**:
  - `#` (H1) becomes the main title.
  - `##` (H2) is emphasized as a subtitle (effect of the `subtitle` class).
  - Paragraph text like presenter info is decorated like a badge (effect of the `meta` class).

### 2. Table of Contents / Agenda
Choose between two designs depending on the number of items.

- **Many items (Standard)**: `<!-- _class: toc -->`
  - Bullet points are automatically arranged in 2 columns.
- **Few items (about 4-5)**: `<!-- _class: toc-focus -->`
  - Becomes a stylish list with large, emphasized numbers in a single column.

### 3. Information Comparison / Parallel Expression (Column Layout)
When placing multiple elements side by side, use different classes depending on whether you want a background/border.

- **Card Type (with background and border)**:
  - **2 Columns**: `<!-- _class: cols-2 -->`
  - **3 Columns**: `<!-- _class: cols-3 -->`
  - **Structure**:
    ```html
    <div class="columns">
      <div class="col">Content 1</div>
      <div class="col">Content 2</div>
    </div>
    ```
- **Simple Type (no background or border)**: Best for placing a table next to text.
  - **2 Columns**: `<!-- _class: split-2 -->`
  - **3 Columns**: `<!-- _class: split-3 -->`
  - **Structure**: Use a simple `<div>` instead of `<div class="col">`.

### 4. 4-Quadrant Matrix
Used for SWOT analysis, priority matrices, etc.

- **Class to use**: `<!-- _class: grid-quadrant -->`
- **Structure**:
  ```html
  <div class="grid">
    <div class="cell">Quadrant 1 content</div>
    <div class="cell">Quadrant 2 content</div>
    <div class="cell">Quadrant 3 content</div>
    <div class="cell">Quadrant 4 content</div>
  </div>
  ```
- **Combining Images and Text**: If you want to split left/right within a quadrant, use `<div class="cell side">`.

### 5. Information Density Control (High-Density Slides)
Used when you need to pack a lot of information into one slide, such as system configurations or requirement definitions.

- **Slightly high (Font size 20px)**: `<!-- _class: dense -->`
- **Very high / Design details (Font size 17px)**: `<!-- _class: extra-dense -->`
  - Ideal for handouts that serve as documentation.

### 6. Profile / Self-Introduction Slide
Used for presenter introductions or team member profiles.

- **Class to use**: `<!-- _class: profile -->`
- **Structure**: Wrap the entire content in `<div class="profile-layout">`, then split into `<div class="profile-image">` (left) and `<div class="profile-content">` (right).
  ```html
  <div class="profile-layout">
    <div class="profile-image">
      ![](path/to/photo.jpg)
      Optional caption
    </div>
    <div class="profile-content">

  # Name
  ## Title / Role

  - Career item 1
  - Career item 2
    </div>
  </div>
  ```
- **Features**:
  - Profile photo is automatically displayed as a circle (200×200px).
  - `h1` renders as a large name (32px, no underline).
  - `h2` renders as a subdued role/title in primary color (18px).
  - `ul` is slightly smaller (19px) for a clean list of career items.

### 7. Appealing with a Strong Message
Used when you want to convey a single message powerfully across the entire slide.

- **Class to use**: `<!-- _class: key-message no-pagination -->`
- **Concurrent directives**: `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- **Structure**: Write the main message in `> blockquote` and supplementary info in a normal paragraph `p`.

---

## 🔧 Header / Footer / Pagination Utilities

Control the visibility of header, footer, and page numbers per slide using these utility classes.

| Class / Directive | Effect |
|---|---|
| `<!-- _class: no-header -->` | Hides the header on that slide |
| `<!-- _class: no-footer -->` | Hides the footer on that slide |
| `<!-- _class: no-pagination -->` | Hides the page number on that slide |
| `<!-- _class: pagination-left -->` | Moves the page number to the bottom-left |
| `<!-- _class: with-header -->` | Adds top padding (85px) to avoid content overlapping the header (use when `header` directive is set but the class isn't auto-detected) |

- These can be combined with other layout classes: `<!-- _class: cover no-pagination no-header no-footer -->`
- `section:has(header)` and `section.with-header` both apply the same top-padding rule, so `with-header` is a fallback for environments that don't support `:has()`.

---

## 🧩 Guide by Component

Simply by adding a class according to the slide's intent, standard Markdown elements are converted into rich components.

### Process and Time-Series Expression
Use ordered lists (`1. `, `2. `).

- **Step Expression**: `<!-- _class: steps -->`
  - Becomes side-by-side cards with badges like "STEP 1", "STEP 2". Ideal for implementation procedures.
- **Timeline**: `<!-- _class: timeline -->`
  - Suitable for expressing project history or roadmaps.

### Presentation of Confirmation Items
- **Checklist**: `<!-- _class: checklist -->`
  - Unordered lists (`- `) are converted into a design with checkmarks.

### Presentation of Schedules
- **Timetable**: `<!-- _class: timetable -->`
  - Standard Markdown tables become an easy-to-read schedule style (e.g., the first column is highlighted).

### Warning and Supplementary Information (Callouts)
Used when you want to emphasize specific information within a slide.

- **Structure**:
  ```html
  <div class="callout info">
    <h4>ℹ️ Information</h4>
    Supplementary info or tips
  </div>
  ```
- **Types**: `info` (Standard), `success` (Success/Completion), `warning` (Caution), `danger` (Warning/Deprecated)

---

## 🎨 Alignment and Image Adjustments

### Alignment within Columns
You can adjust the placement of text and content within columns.

- **Example usage**: `<div class="col v-center text-center">`
- **Vertical**: `v-top` (Top), `v-center` / `v-middle` (Center), `v-bottom` (Bottom)
- **Horizontal**: `text-left` (Left), `text-center` (Center), `text-right` (Right)
*Note: To center all content in the slide, specify `<!-- _class: v-center text-center -->`.

### Image Placement and Shadows
- **Centered + Drop Shadow**: `![center shadow width:600px](path)`
- **Marp Standard Background Split (Coexistence of text and image)**: `![bg right:45% shadow](path)`
  - One of the most frequently used layouts in business presentations. Beautifully place text on the left and an image on the right.
