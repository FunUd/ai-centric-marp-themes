---
name: theme-expert-warm-sunnyday
description: A skill for maximizing the use of the Warm Sunnyday theme (for Marp) to create friendly, approachable presentations for self-introductions, icebreakers, and casual chats. Trigger this skill when the user wants to design or modify slides for informal settings using the Warm Sunnyday theme.
---

# Warm Sunnyday Theme Expert

This skill provides guidelines for appropriately using the classes and layout patterns provided by the custom Marp theme "Warm Sunnyday". This theme is designed for self-introductions, icebreakers, casual meetings, and events where a soft, friendly, and warm atmosphere is desired.

It inherits the layout capabilities of the `azure-clarity` theme but replaces the sharp, business-oriented blues with warm oranges, pinks, and rounded fonts (Nunito / Zen Maru Gothic) for a more approachable vibe.

## 🎯 Basic Principles

In the Warm Sunnyday theme, the goal is to foster communication and a friendly atmosphere. The rounded corners, soft colors, and playful fonts help reduce tension, making it perfect for onboarding, team building, or casual lightning talks.

---

## 📐 Guide by Layout and Use Case

### 1. Cover / Title Slide (Self-Introduction Start)
A warm, gradient background that immediately sets a friendly tone.

- **Classes to use**: `<!-- _class: cover subtitle meta -->`
- **Concurrent directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- **Features**:
  - The `#` (H1) title stands out warmly.
  - `##` (H2) is emphasized as a subtitle (effect of the `subtitle` class).
  - Paragraph text looks like a soft badge, great for names and dates (effect of the `meta` class).

### 2. Agenda / Table of Contents
Choose between two designs depending on the number of items.

- **Many items (Standard)**: `<!-- _class: toc -->`
  - Items are automatically arranged in 2 columns with numbered prefixes.
- **Few items (about 4-5, recommended for casual)**: `<!-- _class: toc-focus -->`
  - Creates a stylish list with large, emphasized numbers in a single column. Perfect for a short agenda like "My Background, Hobbies, Q&A".

### 3. Profile / Self-Introduction Slide
Introduce yourself clearly with a photo and bio.

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
  ## Role / Hometown

  - Hobby 1
  - Hobby 2
    </div>
  </div>
  ```
- **Features**:
  - Profile photo is automatically displayed as a circle (200×200px) with a warm border.
  - `h1` renders as a large name (32px, no underline).
  - `h2` renders as a subdued role/title in primary orange (18px).
  - `ul` is slightly smaller (19px) for a clean list of personal details.

### 4. Hobbies / Interests (Column Layout)
Showcase multiple hobbies or topics side-by-side.

- **Card Type (with soft background and border)**:
  - **2 Columns**: `<!-- _class: cols-2 -->`
  - **3 Columns**: `<!-- _class: cols-3 -->`
  - **Structure**:
    ```html
    <div class="columns">
      <div class="col">Content 1</div>
      <div class="col">Content 2</div>
    </div>
    ```
  - Adding `v-center text-center` to columns makes it look like a friendly showcase.
- **Simple Type (no background or border)**:
  - **2 Columns**: `<!-- _class: split-2 -->`
  - **3 Columns**: `<!-- _class: split-3 -->`
  - **Structure**: Use a simple `<div>` instead of `<div class="col">`.

### 5. Icebreaker / Q&A Grid
Perfect for quick questions like "Dogs or Cats?", "Favorite food?".

- **Class to use**: `<!-- _class: grid-quadrant -->`
- **Structure**:
  ```html
  <div class="grid">
    <div class="cell v-center text-center">
      ### 🐕 Dogs or 🐈 Cats?
      I love dogs!
    </div>
    <div class="cell">...</div>
    <div class="cell">...</div>
    <div class="cell">...</div>
  </div>
  ```
- **Combining Images and Text**: Use `<div class="cell side">` to split left/right within a quadrant.

### 5-2. Sharp Grid (Border-Only Grid)
A minimalist grid layout with borders only and no background colors.

- **Class to use**: `<!-- _class: grid-sharp -->`
- **Structure**: Same as `grid-quadrant`
  ```html
  <div class="grid">
    <div class="cell">Cell 1 content</div>
    <div class="cell">Cell 2 content</div>
    <div class="cell">Cell 3 content</div>
    <div class="cell">Cell 4 content</div>
  </div>
  ```
- **Features**:
  - Transparent background with border-only design
  - Clean, minimalist appearance
  - Great for simple comparisons or structured information

### 6. Step-by-Step Process
Show a sequence of steps in a horizontal card layout.

- **Class to use**: `<!-- _class: steps -->`
- Use an ordered list (`1.`, `2.`, `3.`). Each item becomes a card with a "STEP N" badge.
- `**Bold text**` at the top of each item becomes the step title.

### 7. Timeline / History
Great for "My Journey" or career history slides.

- **Class to use**: `<!-- _class: timeline -->`
- Use an ordered list. Each item gets a dot on a vertical line.
- `**Bold text**` within each item renders as the date/label in primary orange.
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

### 8. Motto / Key Message
Share your personal motto or a strong, positive message.

- **Class to use**: `<!-- _class: key-message no-pagination -->`
- **Concurrent directives**: `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- **Structure**: Write the main message in `> blockquote` and supplementary info in a normal paragraph `p`.
- Displays a large, centered blockquote on a warm gradient background.

### 9. Schedule / Timetable
For event programs or session schedules.

- **Class to use**: `<!-- _class: timetable -->`
- Use a standard Markdown table. The first column (time) is automatically highlighted in primary orange.

### 10. Information Density Control
Avoid these in casual presentations unless you really need to pack in content.

- **Slightly compact (font size 18px)**: `<!-- _class: dense -->`
- **Very compact (font size 15px)**: `<!-- _class: extra-dense -->`
  - Better suited for reference/handout slides than casual presentation slides.

### 10-2. Fine-Grained Font Scale Adjustment
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

---

## 🔧 Header / Footer / Pagination Utilities

Control the visibility of header, footer, and page numbers per slide.

| Class / Directive | Effect |
|---|---|
| `<!-- _class: no-header -->` | Hides the header on that slide |
| `<!-- _class: no-footer -->` | Hides the footer on that slide |
| `<!-- _class: no-pagination -->` | Hides the page number on that slide |
| `<!-- _class: pagination-left -->` | Moves the page number to the bottom-left |
| `<!-- _class: with-header -->` | Adds top padding (85px) to avoid content overlapping the header |

- These can be combined with other layout classes: `<!-- _class: cover no-pagination no-header no-footer -->`
- `with-header` is a fallback for environments that don't support `:has()`.

---

## 🧩 Guide by Component

### Checklist
Convert a bullet list into a checkmark-decorated list.

- **Class to use**: `<!-- _class: checklist -->`
- Unordered lists (`- `) get a green rounded checkmark icon automatically.
- Can also be used inline on a single list: `<ul class="checklist">...</ul>`

### Warning and Supplementary Information (Callouts)
Highlight tips, warnings, or important notes within a slide.

- **Structure**:
  ```html
  <div class="callout info">
    <h4>💡 Tip</h4>
    Supplementary info or tips
  </div>
  ```
- **Types**: `info` (default orange), `success` (green), `warning` (amber), `danger` (red)

### Badges / Tags
Add small inline labels to text.

- **Structure**: `<span class="badge">Label</span>`
- **Variants**: `badge` (default pale), `badge primary` (orange), `badge success` (green), `badge warning` (amber), `badge danger` (red)
- Example: `<span class="badge warning">New</span>`

---

## 🎨 Alignment and Image Adjustments

### Alignment within Columns
Adjust placement of text and content within columns or cells.

- **Example usage**: `<div class="col v-center text-center">`
- **Vertical**: `v-top` (Top), `v-center` / `v-middle` (Center), `v-bottom` (Bottom)
- **Horizontal**: `text-left` (Left), `text-center` (Center), `text-right` (Right)
- To center all content in the slide: `<!-- _class: v-center text-center -->`

### Image Placement and Shadows
- **Centered + Drop Shadow**: `![center shadow width:600px](path)`
- **Background Split (text left, image right)**: `![bg right:45% shadow](path)`

### Text and Background Color Utilities
Apply color accents inline without extra HTML.

| Class | Effect |
|---|---|
| `text-primary` | Orange (primary color) |
| `text-accent` | Dark brown (accent color) |
| `text-success` | Green |
| `text-warning` | Amber |
| `text-danger` | Red/pink |
| `text-sub` | Muted warm gray |
| `text-large` | 1.3× font size |
| `text-small` | 0.85× font size |
| `bg-pale` | Soft pale orange background block |
| `bg-light` | Light orange background block |

- Example: `<span class="text-primary">highlight</span>` or `<div class="bg-pale">...</div>`

---

## 🌟 Design Tips for Casual Presentations

- **Use Emojis**: Emojis blend exceptionally well with the `Zen Maru Gothic` font and the warm color palette. Don't hesitate to use them for hobbies or icebreaker questions.
- **Keep it Light**: Avoid `dense` or `extra-dense` unless absolutely necessary. Casual slides should be breathable and easy to read.
- **Rounded Everything**: Unlike Azure Clarity (sharp corners), this theme uses `border-radius: 12px` / `24px` throughout — lean into it with cards and callouts.
- **Friendly Highlights**: Use `<mark>text</mark>` for inline highlights, or badges for small colorful labels.
