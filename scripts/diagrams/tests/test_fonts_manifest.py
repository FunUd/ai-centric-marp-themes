"""Guard for assets/fonts/ — every bundled font must be referenced by a theme.

Dead weight in a font directory is invisible until someone greps for it: an
unreferenced 9 MB TTF is committed, shipped and never rendered, and the
NOTICE.md attribution quietly rots. This test keeps the directory honest in
both directions.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
THEMES_DIR = ROOT / "themes"
FONTS_DIR = ROOT / "assets/fonts"
NOTICE = FONTS_DIR / "NOTICE.md"

FONT_REF_RE = re.compile(r"url\(['\"]?\.\./assets/fonts/([A-Za-z0-9_.-]+\.ttf)['\"]?\)")
NOTICE_FONT_RE = re.compile(r"`([A-Za-z0-9_.-]+\.ttf)`")

# Faces bundled for completeness rather than wired into a theme.
KNOWN_UNUSED = {"Caladea-BoldItalic.ttf"}


def referenced_fonts() -> set[str]:
    found: set[str] = set()
    for css in THEMES_DIR.glob("*.css"):
        found |= set(FONT_REF_RE.findall(css.read_text(encoding="utf-8")))
    return found


def bundled_fonts() -> set[str]:
    return {p.name for p in FONTS_DIR.iterdir() if p.suffix in (".ttf", ".otf", ".woff", ".woff2")}


def test_fonts_directory_exists() -> None:
    assert FONTS_DIR.is_dir()
    assert (FONTS_DIR / "OFL.txt").is_file()
    assert NOTICE.is_file()


def test_every_bundled_font_exists_on_disk() -> None:
    """Guards a @font-face pointing at a file that was never committed."""
    missing = sorted(referenced_fonts() - bundled_fonts())
    assert missing == [], f"theme CSS references missing font files: {missing}"


def test_no_unreferenced_fonts_are_bundled() -> None:
    """The regression this file exists for: Carlito + Liberation Mono (3.9 MB)
    were committed but no theme ever referenced them."""
    orphans = sorted(bundled_fonts() - referenced_fonts() - KNOWN_UNUSED)
    assert orphans == [], (
        f"unreferenced font files are bundled ({', '.join(orphans)}); "
        f"either wire them into a theme or delete them"
    )


def test_known_unused_fonts_are_still_documented() -> None:
    notice = NOTICE.read_text(encoding="utf-8")
    for name in sorted(KNOWN_UNUSED):
        assert name in notice, f"{name} is unused but undocumented in NOTICE.md"
        section = notice.split(f"`{name}`", 1)
        assert len(section) == 2, f"{name} is mentioned in an unexpected place in NOTICE.md"


def test_notice_documents_every_bundled_font() -> None:
    notice = NOTICE.read_text(encoding="utf-8")
    mentioned = set(NOTICE_FONT_RE.findall(notice))
    for name in sorted(bundled_fonts()):
        assert name in mentioned, f"{name} is bundled but not listed in NOTICE.md"


def test_every_theme_font_family_has_a_license_statement() -> None:
    """Each theme that self-hosts fonts must name them, so attribution travels
    with the theme rather than only in a shared list."""
    notice = NOTICE.read_text(encoding="utf-8")
    for css in sorted(THEMES_DIR.glob("*.css")):
        text = css.read_text(encoding="utf-8")
        if "@font-face" not in text:
            continue
        theme = css.stem
        assert f"## {theme}" in notice, f"{theme} self-hosts fonts but has no NOTICE.md section"


def test_font_face_rules_declare_font_display() -> None:
    """Missing font-display:swap makes text invisible while the font loads."""
    for css in sorted(THEMES_DIR.glob("*.css")):
        text = css.read_text(encoding="utf-8")
        blocks = re.findall(r"@font-face\s*\{(.*?)\}", text, re.S)
        for block in blocks:
            assert "font-display" in block, f"{css.name}: @font-face without font-display"
