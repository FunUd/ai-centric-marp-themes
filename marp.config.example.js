/**
 * Example Marp CLI config for decks scaffolded by
 * `python skills/marp-slide-creator/scripts/setup-slide-project.py`.
 *
 * Copy this file to `marp.config.js` in your deck directory and adjust.
 * The scaffolded layout is:
 *
 *   slides/<deck>/
 *   ├── <deck>.md          # the deck (frontmatter `theme:` selects the theme)
 *   ├── themes/<theme>.css # theme copy (`themeSet` below points here)
 *   └── assets/fonts/      # bundled fonts so `../assets/fonts/…` resolves
 *
 * Note: `themes/_base.css` in this repository is the shared development
 * source, not a selectable theme — never add it to `themeSet`.
 */
module.exports = {
  // Directory holding the copied theme CSS file(s).
  themeSet: ["./themes/"],
  // Marp decks in this repo use raw HTML (`<div class="columns">` etc.).
  html: true,
  // Local images, diagrams and fonts resolve relative to the deck.
  allowLocalFiles: false,
};
