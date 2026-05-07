# Layout Snippets

Use these exact HTML snippets to ensure correct structure and avoid layout breaks.

> **🚨 Every snippet below includes the `<!-- _class: ... -->` directive. This directive is NOT optional — it is an inseparable part of the pattern. Without it, the layout does NOT activate.**

## Two-Column Layout (cols-2)
```html
<!-- _class: cols-2 -->

<div class="columns">
  <div class="col">
    <h3>Left Column</h3>
    <p>Content goes here.</p>
  </div>
  <div class="col">
    <h3>Right Column</h3>
    <p>Content goes here.</p>
  </div>
</div>
```

## Three-Column Layout (cols-3)
```html
<!-- _class: cols-3 -->

<div class="columns">
  <div class="col">
    <h3>Column 1</h3>
    <p>Content goes here.</p>
  </div>
  <div class="col">
    <h3>Column 2</h3>
    <p>Content goes here.</p>
  </div>
  <div class="col">
    <h3>Column 3</h3>
    <p>Content goes here.</p>
  </div>
</div>
```

## 2x2 Grid (grid-quadrant or grid-sharp)
```html
<!-- _class: grid-quadrant -->

<div class="grid">
  <div class="cell">
    <h3>Top Left</h3>
    <p>Content</p>
  </div>
  <div class="cell">
    <h3>Top Right</h3>
    <p>Content</p>
  </div>
  <div class="cell">
    <h3>Bottom Left</h3>
    <p>Content</p>
  </div>
  <div class="cell">
    <h3>Bottom Right</h3>
    <p>Content</p>
  </div>
</div>
```

## Profile Layout (profile)
```html
<!-- _class: profile -->

<div class="profile-layout">
  <div class="profile-image">
    <img src="assets/profile.jpg" alt="Profile Name">
  </div>
  <div class="profile-content">
    <h2>Name</h2>
    <h3>Role / Title</h3>
    <p>Bio or description goes here.</p>
  </div>
</div>
```

## Callouts (callout.info / success / warning / danger)
```html
<div class="callout info">
  <p><strong>Note:</strong> This is an info callout.</p>
</div>
```

## Custom Font Scaling (font-scale)

Use this when you need finer control over content density than `dense` or `extra-dense` provide.

```html
<style scoped>
section {
  --font-scale: 0.85; /* Scale factor (default is 1.0) */
}
</style>
```
