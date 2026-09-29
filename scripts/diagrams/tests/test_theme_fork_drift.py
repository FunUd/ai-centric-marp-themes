"""Fork-drift guard for the near-identical themes.

`azure-clarity.css` and `crimson-clarity.css` are 99% identical forks that
differ only in colour. That is a deliberate trade-off (each theme ships as a
single self-contained file with no @import), but it silently produced real
divergence: crimson-clarity had a `callout.blue h4` rule that azure-clarity
lacked, and crimson-clarity hard-coded the blue callout colours instead of
using its own tokens, so editing `:root` did not change them.

These tests compare the two files with colours and token names normalised, so
any *structural* difference shows up as a failure.

`warm-sunnyday` is deliberately excluded: it is a colour fork *plus* genuine
design divergence (larger radii, looser letter-spacing, a different step-badge
treatment), so a structural comparison would be noise.
"""
from __future__ import annotations

import difflib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
THEMES = ROOT / "themes"

# Pure colour forks: any structural difference is unintended.
PAIRED_THEMES = [
    ("azure-clarity", "crimson-clarity"),
]

# Forks with intentional design differences; component rules must still match.
SEMI_FORKED_THEMES = [
    ("azure-clarity", "warm-sunnyday"),
]

_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
_HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
_RGBA_RE = re.compile(r"rgba?\([^)]*\)")
_VAR_RE = re.compile(r"--[\w-]+")
_FONT_STACK_RE = re.compile(r"font-family:[^;]+;")
# Font loading is an intentional per-theme difference: azure-clarity and
# crimson-clarity rely on the OS font stack, warm-sunnyday bundles its own.
_FONT_FACE_RE = re.compile(r"@font-face\s*\{[^}]*\}", re.S)


def _normalise(path: Path) -> list[str]:
    """Strip everything theme-specific: comments, colours, token names, fonts."""
    css = _COMMENT_RE.sub("", path.read_text(encoding="utf-8"))
    css = _FONT_FACE_RE.sub("", css)
    css = _HEX_RE.sub("COLOR", css)
    css = _RGBA_RE.sub("COLOR", css)
    css = _VAR_RE.sub("VAR", css)
    css = _FONT_STACK_RE.sub("font-family:STACK;", css)
    return [line.strip() for line in css.splitlines() if line.strip()]


@pytest.mark.parametrize("left,right", PAIRED_THEMES)
def test_paired_themes_have_no_structural_drift(left: str, right: str) -> None:
    """Any non-colour difference between pure colour forks is unintended."""
    a = _normalise(THEMES / f"{left}.css")
    b = _normalise(THEMES / f"{right}.css")
    diff = [
        line
        for line in difflib.unified_diff(a, b, lineterm="", n=0)
        if line[:1] in "+-" and not line.startswith(("---", "+++"))
    ]
    assert diff == [], (
        f"{left}.css and {right}.css differ structurally (colours normalised).\n"
        + "\n".join(diff[:40])
        + "\n\nIf this change is intentional, update PAIRED_THEMES in this file."
    )


@pytest.mark.parametrize("left,right", SEMI_FORKED_THEMES)
@pytest.mark.parametrize("component", [
    "callout.blue",
    "callout.green",
    "callout.orange",
    "callout.red",
    "callout.blue h4",
    "callout.green h4",
    "callout.orange h4",
    "callout.red h4",
    "badge",
    "badge.blue",
    "badge.green",
    "badge.orange",
    "badge.red",
])
def test_semi_forked_themes_agree_on_components(left: str, right: str, component: str) -> None:
    """warm-sunnyday diverges on radii and step badges by design, but the
    alert and badge components must stay in sync — they carry meaning, not
    personality, and are documented as such."""
    rule = f"section .{component} "
    present = {}
    for theme in (left, right):
        css = (THEMES / f"{theme}.css").read_text(encoding="utf-8")
        present[theme] = bool(re.search(re.escape(rule) + r"\{", css))
    assert present[left] == present[right], (
        f"`{component}` exists in {left}: {present[left]} but {right}: {present[right]}"
    )


@pytest.mark.parametrize("theme,prefix", [
    ("azure-clarity", "--ac-"),
    ("crimson-clarity", "--cc-"),
    ("warm-sunnyday", "--ws-"),
])
def test_callout_blue_uses_theme_tokens(theme: str, prefix: str) -> None:
    """The regression: crimson's blue callout was three hard-coded hex values,
    so the documented "edit :root to retheme" workflow silently did nothing."""
    css = (THEMES / f"{theme}.css").read_text(encoding="utf-8")
    match = re.search(r"section \.callout\.blue\s*\{(.*?)\}", css, re.S)
    assert match, f"{theme}: no .callout.blue rule"
    body = match.group(1)
    assert not _HEX_RE.search(body), f"{theme}: .callout.blue hard-codes colours:\n{body}"
    assert f"var({prefix}" in body, f"{theme}: .callout.blue does not use {prefix}* tokens"


@pytest.mark.parametrize("theme", ["azure-clarity", "crimson-clarity", "warm-sunnyday"])
def test_callout_blue_heading_rule_exists(theme: str) -> None:
    """azure-clarity was missing the rule crimson-clarity had, so a blue
    callout heading rendered in the body colour there."""
    css = (THEMES / f"{theme}.css").read_text(encoding="utf-8")
    assert re.search(r"section \.callout\.blue h4\s*\{", css), f"{theme}: missing `.callout.blue h4` rule"


@pytest.mark.parametrize(
    "theme,prefix",
    [
        ("azure-clarity", "--ac-"),
        ("crimson-clarity", "--cc-"),
        ("warm-sunnyday", "--ws-"),
    ],
)
def test_info_tokens_are_declared(theme: str, prefix: str) -> None:
    css = (THEMES / f"{theme}.css").read_text(encoding="utf-8")
    assert f"{prefix}info:" in css, f"{theme}: {prefix}info not declared"
    assert f"{prefix}info-pale:" in css, f"{theme}: {prefix}info-pale not declared"


ALL_THEMES = [
    "azure-clarity",
    "crimson-clarity",
    "prism-edge",
    "nebula-glass",
    "warm-sunnyday",
    "slate-minimal",
]


@pytest.mark.parametrize("theme", ALL_THEMES)
@pytest.mark.parametrize(
    "utility_pattern,desc",
    [
        (r"section\.no-header\s+header", "no-header utility"),
        (r"section\.no-footer\s+footer", "no-footer utility"),
        (r"section\.no-pagination(?:::after|\s*\{)", "no-pagination utility"),
        (r"section\.pagination-left(?:::after|\s*\{)", "pagination-left utility"),
        (r"section\.align-center", "align-center utility"),
        (r"section\.dense", "dense layout class"),
        (r"section\.extra-dense", "extra-dense layout class"),
    ],
)
def test_all_themes_declare_core_utility_classes(theme: str, utility_pattern: str, desc: str) -> None:
    """Core display and density utilities must be implemented across all 6 themes,
    including structural forks (nebula-glass, slate-minimal) that do not use _base.css sync."""
    css = (THEMES / f"{theme}.css").read_text(encoding="utf-8")
    assert re.search(utility_pattern, css), f"{theme}.css is missing {desc} ({utility_pattern})"
