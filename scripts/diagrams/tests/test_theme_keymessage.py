"""Contract tests for the key-message quote style across all themes.

Regression guard: `section.key-message blockquote p` must never fall back to
the muted subtitle style (`section.key-message p`). Five themes implement the
contract with `font-size: inherit; color: inherit` on the inner ``p``;
`nebula-glass` specifies its own explicit size instead. The computed-style
tests verify the contract in a real browser (skipped when Playwright or its
Chromium build is unavailable); the static tests always run.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
THEMES_DIR = ROOT / "themes"

# Themes whose quote p inherits from `section.key-message blockquote`.
INHERIT_THEMES = ["azure-clarity", "crimson-clarity", "warm-sunnyday", "slate-minimal", "prism-edge"]
ALL_THEMES = INHERIT_THEMES + ["nebula-glass"]

RULE_RE = re.compile(r"section\.key-message\s+blockquote\s+p\s*\{([^}]*)\}")

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
{css}
</style></head><body>
<section class="key-message">
<blockquote><p id="quote">Quote text</p></blockquote>
<p id="caption">Caption</p>
</section></body></html>"""

JS = """() => {
  const g = (el) => { const s = getComputedStyle(el); return {size: s.fontSize, color: s.color}; };
  return {
    quote: g(document.getElementById('quote')),
    blockquote: g(document.querySelector('blockquote')),
    caption: g(document.getElementById('caption')),
  };
}"""


def _rule_body(theme: str) -> str:
    css = (THEMES_DIR / f"{theme}.css").read_text(encoding="utf-8")
    match = RULE_RE.search(css)
    assert match, (
        f"{theme}.css has no `section.key-message blockquote p` rule — "
        "the quote would collapse to the muted subtitle style"
    )
    return match.group(1)


def _px(value: str) -> float:
    return float(value.removesuffix("px"))


# --- static contract (always runs) ------------------------------------------


@pytest.mark.parametrize("theme", ALL_THEMES)
def test_keymessage_quote_rule_declares_font_size(theme: str) -> None:
    assert "font-size" in _rule_body(theme), f"{theme}.css: quote rule lacks an explicit font-size"


@pytest.mark.parametrize("theme", INHERIT_THEMES)
def test_keymessage_quote_rule_inherits_blockquote_size(theme: str) -> None:
    body = _rule_body(theme)
    assert re.search(r"font-size\s*:\s*inherit", body), f"{theme}.css: expected `font-size: inherit`"
    assert re.search(r"color\s*:\s*inherit", body), f"{theme}.css: expected `color: inherit`"


# --- computed styles (Playwright; skipped when unavailable) -----------------


@pytest.fixture(scope="module")
def page():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright not installed")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as error:  # missing browser binary, no sandbox, ...
            pytest.skip(f"chromium unavailable: {error}")
        yield browser.new_page()
        browser.close()


def _computed(page, theme: str) -> dict:
    css = (THEMES_DIR / f"{theme}.css").read_text(encoding="utf-8")
    page.set_content(HTML.format(css=css))
    return page.evaluate(JS)


@pytest.mark.parametrize("theme", INHERIT_THEMES)
def test_keymessage_quote_inherits_blockquote_size_computed(page, theme: str) -> None:
    styles = _computed(page, theme)
    quote, blockquote, caption = styles["quote"], styles["blockquote"], styles["caption"]
    assert _px(quote["size"]) == pytest.approx(_px(blockquote["size"])), (
        f"{theme}: quote {quote['size']} does not inherit blockquote {blockquote['size']}"
    )
    assert (quote["size"], quote["color"]) != (caption["size"], caption["color"]), (
        f"{theme}: quote is styled identically to the subtitle caption (the original bug)"
    )


def test_keymessage_nebula_quote_keeps_explicit_scale_computed(page) -> None:
    styles = _computed(page, "nebula-glass")
    quote, blockquote, caption = styles["quote"], styles["blockquote"], styles["caption"]
    # nebula-glass pins `font-size: 2.2em` (relative to the blockquote) instead of inheriting.
    assert _px(quote["size"]) == pytest.approx(2.2 * _px(blockquote["size"]), rel=1e-3)
    assert (quote["size"], quote["color"]) != (caption["size"], caption["color"])
