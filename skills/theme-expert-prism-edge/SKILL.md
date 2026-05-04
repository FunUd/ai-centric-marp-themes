---
name: theme-expert-prism-edge
description: A skill for maximizing the use of the Prism Edge theme (for Marp) to create striking, modern, high-impact professional presentations. Trigger this skill when the user wants to design, modify, or optimize slides using the Prism Edge theme, or when they want bold, eye-catching visuals with advanced cover designs and sophisticated layouts.
---

# Prism Edge Theme Expert

This skill provides guidelines for appropriately using the classes and layout patterns provided by the custom Marp theme "Prism Edge". This theme is designed for **high-impact, modern, and professional presentations** that need to stand out — keynotes, investor pitches, product launches, and any scenario where visual memorability matters.

It inherits the layout capabilities of the `azure-clarity` theme but replaces calm blues with **bold indigo-cyan gradients, sharp edges (no excessive rounding), and sophisticated cover designs** featuring waves, diagonal splits, aurora effects, and dark noir backgrounds.

## 🎯 Basic Principles

In the Prism Edge theme, the goal is to create **visually memorable, modern, and professional slides**. Avoid overusing cards and rounded corners. Instead, leverage:
- **Advanced cover designs** (wave, diagonal, noir, aurora)
- **Asymmetric layouts** and bold typography
- **Glass panels, gradient text, and accent borders**
- **Dark slide modes** for dramatic emphasis

---

## 📐 Guide by Layout and Use Case

### 1. Cover / Title Slide — Choose Your Impact
Prism Edge offers **four distinct cover designs** depending on the tone you want.

#### A. Classic Cover (subtle, professional)
- **Classes**: `<!-- _class: cover subtitle meta -->`
- **Directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Features: Clean background with a soft decorative circle. Best for business reports.

#### B. Wave Cover (dynamic, modern)
- **Classes**: `<!-- _class: cover-wave subtitle meta -->`
- **Directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Features: SVG wave layers at the bottom. Great for tech talks and product announcements.

#### C. Diagonal Cover (bold, asymmetric)
- **Classes**: `<!-- _class: cover-diagonal -->`
- **Directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Features: A sharp diagonal split — indigo gradient on the right, white on the left. Text stays left-aligned. Perfect for making a bold first impression.

#### D. Noir Cover (dramatic, high-end)
- **Classes**: `<!-- _class: cover-noir -->`
- **Directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Features: Dark background with complex multi-layer radial gradients (indigo + cyan + magenta glow). White text for maximum contrast. Ideal for keynote-style openings.

#### E. Aurora Cover (ethereal, artistic)
- **Classes**: `<!-- _class: cover-aurora subtitle meta -->`
- **Directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Features: Soft aurora-like rotating gradient blobs on a light background. Best for creative presentations.

### 2. Hero Slide — One Big Message
Use when you want a single, powerful statement to dominate the slide.

- **Class**: `<!-- _class: hero no-pagination -->`
- **Directives**: `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Features: H1 renders at **72px**, centered. H2 and body text are subdued beneath it.
- Example:
  ```markdown
  <!-- _class: hero no-pagination -->
  <!-- _header: "" -->
  <!-- _footer: "" -->

  # 78% Increase

  ## Year-over-year revenue growth
  ```

### 3. Title Only — Minimal & Sharp
A stripped-down slide with only a massive left-aligned title.

- **Class**: `<!-- _class: title-only no-pagination -->`
- Features: H1 at **64px**, no border-bottom, perfectly aligned left. Use for section dividers.

### 4. Table of Contents / Agenda
Choose between two designs depending on the number of items.

- **Many items (Standard)**: `<!-- _class: toc -->`
  - Bullet points are automatically arranged in 2 columns.
- **Few items (about 4-5)**: `<!-- _class: toc-focus -->`
  - Becomes a stylish list with large, emphasized numbers in a single column.

### 5. Information Comparison / Parallel Expression (Column Layout)
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

### 6. Asymmetric Split (65:35)
For editorial-style layouts where one side needs more space.

- **Standard Asym**: `<!-- _class: split-asym -->`
  - Grid ratio: **3fr : 2fr**
- **Reverse Asym**: `<!-- _class: split-asym-reverse -->`
  - Grid ratio: **2fr : 3fr**
- **Structure**: Same as `split-2`, just use `<div>` containers.

### 7. 4-Quadrant Matrix
Used for SWOT analysis, priority matrices, etc.

- **Soft Grid (with backgrounds)**: `<!-- _class: grid-quadrant -->`
  - Cells have pale indigo backgrounds and borders.
  - **Side-image cell**: Add `side` to a cell (`<div class="cell side">`) to place an image beside text with flex layout.
- **Sharp Grid (border-only, no backgrounds)**: `<!-- _class: grid-sharp -->`
  - Cells are separated by **thin borders only**, no backgrounds, no rounded corners. Very modern and editorial.
  - **Structure**:
    ```html
    <div class="grid">
      <div class="cell">Quadrant 1</div>
      <div class="cell">Quadrant 2</div>
      <div class="cell">Quadrant 3</div>
      <div class="cell">Quadrant 4</div>
    </div>
    ```

### 8. Accent Left Border Slide
Adds a striking **gradient border** on the left edge of the slide (indigo → cyan).

- **Class**: `<!-- _class: accent-left -->`
- Use this when you want a subtle but unmistakable visual signature on a content slide.

### 9. Background Pattern Slides
Apply subtle texture to the slide background without adding DOM elements.

- **Grid Pattern**: `<!-- _class: bg-grid -->
  - Fine 40px grid lines. Great for technical/architecture slides.
- **Noise Texture**: `<!-- _class: bg-noise -->`
  - Soft radial speckles in indigo, cyan, and magenta. Adds depth without distraction.

### 11. Glass Panel (Frosted Glass Effect)
Use inside a slide to create a frosted-glass container over complex backgrounds.

- **Structure**:
  ```html
  <div class="glass-panel">
  
  ### Heading Inside Glass
  Content here is readable even over busy backgrounds.
  
  </div>
  ```
- Works beautifully inside `cover-aurora` or `bg-noise` backgrounds.

### 12. Gradient Text
Make headings or numbers pop with a **live gradient fill**.

- **Structure**: `<span class="gradient-text">78% Growth</span>`
- Applies an indigo-to-cyan gradient directly to the text.
- Note: Works best on large text (H1, H2, or hero numbers).

### 13. Underline Accent
Add a **decorative gradient underline** to inline text or headings.

- **Structure**: `<span class="underline-accent">Key Point</span>`
- Produces a 4px tall indigo-to-cyan underline.

### 14. Section Number — Large Decorative Background Number
Add a **giant faded number** behind your slide content for editorial section dividers.

- **Structure**: `<div class="section-number">01</div>` placed before your content.
- The number is rendered at **120px**, semi-transparent, and positioned behind the text.
- Example:
  ```markdown
  <!-- _class: with-header -->

  # Strategy

  <div class="section-number">01</div>

  Content here stays clear of the decorative number.

  </div>
  ```

### 15. Highlight Box — Vivid Emphasis Block
A sharp left-bordered box with a subtle gradient background for key insights.

- **Structure**:
  ```html
  <div class="highlight-box">

  ### Key Insight
  Users engagement hit an all-time high after the new feature launch.

  </div>
  ```
- Features: Indigo left border + pale gradient background. No rounded corners.

### 16. Large Quote — Editorial Blockquote
A large, italic, left-bordered quote style for impactful statements.

- **Structure**:
  ```html
  <div class="quote-large">

  Understanding what customers truly need is our core philosophy.

  </div>
  ```
- Features: 32px italic text, indigo left border, editorial magazine feel.

### 17. Information Density Control (High-Density Slides)
Used when you need to pack a lot of information into one slide.

- **Slightly high (Font size 18px)**: `<!-- _class: dense -->`
- **Very high / Design details (Font size 15px)**: `<!-- _class: extra-dense -->`
  - Ideal for handouts that serve as documentation.

### 17-2. Fine-Grained Font Scale Adjustment
For precise control over font sizes, use the `--font-scale` CSS variable with `<style scoped>` tags.

- **Correct Usage**:
  ```markdown
  <style scoped>
  section {
    --font-scale: 0.85;
  }
  </style>
  ```
- **IMPORTANT**: Do NOT use `<!-- _style: "..." -->` directive — it does not work for CSS variables. Always use `<style scoped>` tags.
- **Available range**: `0.7` (very small) to `1.0` (default)
- **Common values**:
  - `0.95`: Slightly smaller
  - `0.9`: Moderately smaller
  - `0.85`: Equivalent to `dense` class
  - `0.75`: Equivalent to `extra-dense` class
  - `0.7`: Maximum compression
- **Note**: This affects all text elements (headings, paragraphs, lists, tables) proportionally. Use this when predefined `dense` or `extra-dense` classes don't provide the exact size you need.

### 18. Profile / Self-Introduction Slide
Used for presenter introductions or team member profiles.

- **Class**: `<!-- _class: profile -->`
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

### 19. Appealing with a Strong Message
Used when you want to convey a single message powerfully across the entire slide.

- **Class**: `<!-- _class: key-message no-pagination -->`
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
| `<!-- _class: with-header -->` | Adds top padding (85px) to avoid content overlapping the header |

- These can be combined with other layout classes: `<!-- _class: cover-wave no-pagination no-header no-footer -->`
- `with-header` is a fallback for environments that don't support `:has()`.

---

## 🧩 Guide by Component

### Process and Time-Series Expression
Use ordered lists (`1. `, `2. `).

- **Step Expression**: `<!-- _class: steps -->`
  - Becomes side-by-side cards with badges like "STEP 1", "STEP 2".
- **Timeline**: `<!-- _class: timeline -->`
  - Suitable for expressing project history or roadmaps. Gradient vertical line with indigo-to-cyan gradient.
  - **IMPORTANT**: The bold date/period and description text must be on the same line with a space between them.
  - **Correct example**:
    ```markdown
    1. **2024年 Q1** プロジェクト発足、要件定義フェーズ開始
    2. **2024年 Q3** プロトタイプ完成、ユーザーテスト実施
    ```
  - **Incorrect example** (line break after bold):
    ```markdown
    1. **2024年 Q1**
    プロジェクト発足、要件定義フェーズ開始
    2. **2024年 Q3**
    プロトタイプ完成、ユーザーテスト実施
    ```

### Presentation of Confirmation Items
- **Checklist**: `<!-- _class: checklist -->`
  - Unordered lists (`- `) are converted into a design with checkmarks.
  - Can also be applied to a specific list: `<ul class="checklist">`

### Presentation of Schedules
- **Timetable**: `<!-- _class: timetable -->`
  - Standard Markdown tables become an easy-to-read schedule style (first column highlighted).

### Warning and Supplementary Information (Callouts)
Used when you want to emphasize specific information within a slide.

- **Structure**:
  ```html
  <div class="callout info">
    <h4>Information</h4>
    Supplementary info or tips
  </div>
  ```
- **Types**: `info` (Standard), `success` (Success/Completion), `warning` (Caution), `danger` (Warning/Deprecated)

### Badges / Tags
Small inline labels for statuses, categories, or tags.

- **Structure**: `<span class="badge">Tag</span>`
- **Types**:
  - `badge` (Default — pale indigo)
  - `badge primary` (Filled indigo)
  - `badge success` (Filled emerald)
  - `badge warning` (Filled amber)
  - `badge danger` (Filled red)
- Example:
  ```markdown
  <span class="badge primary">New</span>
  <span class="badge success">Completed</span>
  ```

---

## 🎨 Alignment and Image Adjustments

### Alignment within Columns
You can adjust the placement of text and content within columns.

- **Example usage**: `<div class="col v-center text-center">`
- **Vertical**: `v-top` (Top), `v-center` / `v-middle` (Center), `v-bottom` (Bottom)
- **Horizontal**: `text-left` (Left), `text-center` (Center), `text-right` (Right)
  - Aliases also work: `align-left`, `align-center`, `align-right`

*Note: To center all content in the slide, specify `<!-- _class: v-center text-center -->`.

### Image Placement and Shadows
- **Centered + Drop Shadow**: `![center shadow width:600px](path)`
- **Marp Standard Background Split (Coexistence of text and image)**: `![bg right:45% shadow](path)`

---

## 🎨 Text and Background Color Utilities

Apply color accents inline without extra HTML.

| Class | Effect |
|---|---|
| `text-primary` | Indigo (primary color) |
| `text-accent` | Deep slate (accent color) |
| `text-success` | Emerald green |
| `text-warning` | Amber |
| `text-danger` | Red |
| `text-sub` | Muted slate gray |
| `text-cyan` | Cyan accent |
| `text-magenta` | Magenta accent |
| `text-large` | 1.3× font size |
| `text-small` | 0.85× font size |
| `bg-pale` | Soft pale indigo background block |
| `bg-light` | Light indigo background block |
| `bg-dark` | Deep navy background block (light text) |
| `stat-number` | 56px bold metric number (use with `stat-label`) |
| `stat-label` | Uppercase label below a `stat-number` |
| `section-number` | 120px faded decorative background number |
| `highlight-box` | Gradient left-bordered emphasis block |
| `quote-large` | 32px italic editorial blockquote |
| `badge` | Inline status tag (use with `primary`, `success`, `warning`, `danger`) |

- Example: `<span class="text-cyan">highlight</span>` or `<div class="bg-dark">...</div>`
- Example: `<span class="stat-number">2,847</span><span class="stat-label">Users</span>`

---

## 🌟 Design Tips for High-Impact Presentations

- **Choose covers intentionally**: Use `cover-diagonal` for bold pitches, `cover-noir` for dramatic keynotes, `cover-wave` for friendly tech talks, and `cover-aurora` for creative showcases.
- **Embrace Asymmetry**: Use `split-asym` and `grid-sharp` to break away from overly uniform grids. Asymmetry catches the eye.
- **Avoid Rounded Corners**: This theme is intentionally sharp. Do not add custom border-radius in your HTML unless absolutely necessary.
- **Gradient Text for Numbers**: Use `<span class="gradient-text">` for KPIs and percentages in hero slides.
- **Glass Panels for Layering**: When you have a busy background (`bg-noise`, `cover-aurora`), wrap content in `<div class="glass-panel">` to ensure readability.
- **Stat Numbers for KPIs**: Pair `<span class="stat-number">` with `<span class="stat-label">` for clean metric displays in column layouts.
- **Section Numbers for Dividers**: Use `<div class="section-number">` on chapter-break slides for a magazine-like editorial feel.
- **Highlight Boxes for Insights**: Use `<div class="highlight-box">` to make a single key takeaway stand out without card bloat.
- **Sharp > Soft**: If in doubt between a soft card and a sharp border-only layout, choose sharp. That is the Prism Edge aesthetic.
