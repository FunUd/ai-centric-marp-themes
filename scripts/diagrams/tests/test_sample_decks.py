"""Lint the repository's own sample decks.

The samples are the reference decks: agents read them to learn the layout
system, and the README tells users to copy from them. If a sample drifts out of
compliance, the guidance it gives is wrong.

This runs the real `marp-lint.py` and `post-edit-check.py` against
`slides/sample-slide/*.md` so CI fails when a sample breaks a rule the toolkit
itself enforces.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SAMPLES = ROOT / "slides/sample-slide"
DECKS = sorted(SAMPLES.glob("*.md"))
LINT = ROOT / "skills/marp-slide-creator/scripts/marp-lint.py"
POST_EDIT = ROOT / "skills/marp-slide-creator/scripts/post-edit-check.py"


def test_samples_exist() -> None:
    assert DECKS, f"no sample decks found in {SAMPLES}"


def test_every_theme_has_a_sample_deck() -> None:
    # `_*.css` files are SSoT sources (e.g. `_base.css`), not selectable themes.
    themes = {p.stem for p in (ROOT / "themes").glob("*.css") if not p.stem.startswith("_")}
    covered = {d.stem.removesuffix("-sample") for d in DECKS if d.stem.endswith("-sample")}
    assert themes <= covered, f"themes without a sample deck: {sorted(themes - covered)}"


def test_deck_names_match_their_theme() -> None:
    """`*_sample.md` with a `theme:` frontmatter pointing elsewhere is a
    copy-paste error that would silently showcase the wrong design."""
    import re

    for deck in DECKS:
        text = deck.read_text(encoding="utf-8")
        match = re.search(r"^theme:\s*(\S+)\s*$", text, re.M)
        assert match, f"{deck.name}: no `theme:` in frontmatter"
        if deck.stem.endswith("-sample"):
            assert match.group(1) == deck.stem.removesuffix("-sample"), (
                f"{deck.name}: frontmatter theme is '{match.group(1)}'"
            )


@pytest.mark.parametrize("deck", DECKS, ids=lambda p: p.name)
def test_sample_passes_structural_lint(deck: Path) -> None:
    """Structural errors (ERROR severity) are defects, not style opinions.

    `--structural-only` is deliberate: readability WARNINGs are advisory and
    several samples intentionally demonstrate dense layouts.
    """
    result = subprocess.run(
        [sys.executable, str(LINT), str(deck), "--structural-only"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("deck", DECKS, ids=lambda p: p.name)
def test_sample_passes_post_edit_check(deck: Path) -> None:
    """Catches glued `---`, wrong slide counts and language contamination."""
    result = subprocess.run(
        [sys.executable, str(POST_EDIT), str(deck), "--lang", "ja"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("deck", DECKS, ids=lambda p: p.name)
def test_sample_only_uses_classes_its_theme_implements(deck: Path) -> None:
    """The failure mode this catches: a class copied from another theme's
    sample that silently does nothing here."""
    import re
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts/diagrams"))
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "tc_for_samples", ROOT / "scripts/diagrams/theme_classes.py"
        )
        module = importlib.util.module_from_spec(spec)
        _sys.modules["tc_for_samples"] = module
        spec.loader.exec_module(module)
    finally:
        _sys.path.pop(0)

    theme_match = re.search(r"^theme:\s*(\S+)\s*$", deck.read_text(encoding="utf-8"), re.M)
    if not theme_match:
        pytest.skip(f"{deck.name}: no theme frontmatter")
    theme = theme_match.group(1)
    available = module.theme_all_classes(theme)

    text = deck.read_text(encoding="utf-8")
    used: set[str] = set()
    for match in re.finditer(r"_class:\s*(.+?)\s*-->", text):
        used |= set(match.group(1).split())
    for match in re.finditer(r'class="([^"]+)"', text):
        used |= set(match.group(1).split())

    unknown = sorted(
        c for c in used
        if c not in available and not c.startswith("section-") and c not in {"columns", "col", "cell", "grid", "content", "card"}
    )
    assert unknown == [], f"{deck.name} uses classes {theme}.css does not implement: {unknown}"
