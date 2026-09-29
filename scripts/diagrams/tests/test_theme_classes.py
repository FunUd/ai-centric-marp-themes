"""Tests for theme_classes.py and the generated manifest.

Two jobs:

1. Keep the semantic sets honest against the CSS. A class may only be declared
   centered / title-exempt if some theme actually implements it, so the linter
   cannot accumulate entries for layouts that were renamed or removed.
2. Keep the generated `theme-classes.json` in sync. `marp-lint.py` is copied
   standalone into agent directories and reads that file; if it drifts, the
   installed linter disagrees with the repo.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ROOT = SCRIPT_DIR.parent.parent
MANIFEST = ROOT / "skills/marp-slide-creator/scripts/theme-classes.json"
LINTER = ROOT / "skills/marp-slide-creator/scripts/marp-lint.py"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


classes = load_module("theme_classes", "theme_classes.py")


# --- semantic sets vs the CSS ----------------------------------------------


@pytest.mark.parametrize("name", ["LIST_UNSUITABLE_CLASSES", "TITLE_EXEMPT_CLASSES", "LIST_EXEMPT_CLASSES"])
def test_declared_classes_exist_in_some_theme(name: str) -> None:
    """No phantom entries: every declared class must be implemented."""
    declared = set(getattr(classes, name))
    implemented = classes.all_section_classes()
    missing = sorted(declared - implemented)
    assert missing == [], f"{name} references classes no theme implements: {missing}"


def _rule_bodies(theme: str, cls: str) -> str:
    """Declarations of every rule whose selector list mentions `section.<cls>`.

    Handles grouped selectors such as:
        section.align-center,
        section .align-center { text-align: center; }
    where a naive `section.<cls> {` search finds nothing.
    """
    import re

    css = re.sub(r"/\*.*?\*/", "", (classes.THEMES_DIR / f"{theme}.css").read_text(encoding="utf-8"), flags=re.S)
    bodies: list[str] = []
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        selectors = [s.strip() for s in match.group(1).split(",")]
        # The class may appear anywhere in a selector group, e.g.
        #   section.align-center,
        #   section .align-center { text-align: center; }
        if f"section.{cls}" in selectors:
            bodies.append(match.group(2))
    return " ".join(bodies)


def _centers(declarations: str) -> bool:
    squashed = re.sub(r"\s+", " ", declarations)
    return bool(re.search(r"text-align:\s*center", squashed) or re.search(r"align-items:\s*center", squashed))


def test_list_unsuitable_covers_every_title_and_message_layout() -> None:
    """The set must include every cover, title and message layout.

    Keying on layout *purpose* rather than a CSS property is deliberate: several
    themes left-align their covers (`slate-minimal`, `cover-diagonal`,
    `nebula-glass` `key-message`), so a "does it centre?" test would either
    produce false positives or force those themes to be under-protected.
    """
    implemented = classes.all_section_classes()
    expected = {
        c for c in implemented if c.startswith(("cover", "title-", "hero")) or c in {"key-message", "align-center"}
    }
    missing = sorted(expected - classes.LIST_UNSUITABLE_CLASSES)
    assert missing == [], f"title/message layouts missing from LIST_UNSUITABLE_CLASSES: {missing}"


def test_glass_card_layout_is_correctly_excluded() -> None:
    """Documents the one deliberate exclusion.

    `glass-card-layout` centers the slide box, but the inner `.card` inherits
    the section's left alignment, so a bulleted feature list renders correctly.
    Flagging it produced a false positive on the nebula-glass sample deck.
    """
    assert "glass-card-layout" not in classes.LIST_UNSUITABLE_CLASSES
    css = (classes.THEMES_DIR / "nebula-glass.css").read_text(encoding="utf-8")
    # The card rule must not force centre alignment on its content.
    assert "section.glass-card-layout .card {" in css


def test_list_unsuitable_excludes_content_layouts() -> None:
    """A list is the point of these layouts, so they must not be flagged."""
    content = {
        "cols-2",
        "cols-3",
        "split-2",
        "split-3",
        "split-asym",
        "split-asym-reverse",
        "split-glass",
        "grid-quadrant",
        "grid-sharp",
        "steps",
        "timeline",
        "checklist",
        "timetable",
        "profile",
        "dense",
        "extra-dense",
        "with-header",
        "toc",
        "toc-focus",
    }
    assert not (content & classes.LIST_UNSUITABLE_CLASSES)


def test_align_center_is_included_because_it_explicitly_centers() -> None:
    """`align-center` is the manual opt-in and always centers."""
    assert "align-center" in classes.LIST_UNSUITABLE_CLASSES
    assert _centers(_rule_bodies("azure-clarity", "align-center"))


def test_title_exempt_includes_every_cover_variant() -> None:
    """A cover exists to carry a deck or product name, so a generic heading is
    correct there. This is the regression: `cover-nebula` was missing and the
    skill's own quick start produced a false WEAK_TITLE."""
    covers = {c for c in classes.all_section_classes() if c.startswith("cover")}
    missing = sorted(covers - classes.TITLE_EXEMPT_CLASSES)
    assert missing == [], f"cover layouts not exempt from WEAK_TITLE: {missing}"


def test_title_exempt_includes_title_layouts() -> None:
    title_layouts = {c for c in classes.all_section_classes() if c.startswith(("title-", "hero"))}
    missing = sorted(title_layouts - classes.TITLE_EXEMPT_CLASSES)
    assert missing == [], f"title layouts not exempt from WEAK_TITLE: {missing}"


def test_list_exempt_covers_structural_list_layouts() -> None:
    structural = {"checklist", "steps", "timeline", "timetable", "toc", "toc-focus"}
    assert structural <= classes.LIST_EXEMPT_CLASSES


def test_toc_is_exempt_from_title_check() -> None:
    """A TOC heading is a label, not a claim, so "Agenda" must not be flagged."""
    assert {"toc", "toc-focus"} <= classes.TITLE_EXEMPT_CLASSES


# --- diagram layout mapping -------------------------------------------------


def test_diagram_layout_classes_source_from_layout_spec() -> None:
    layout_spec = load_module("layout_spec", "layout_spec.py")
    assert classes.DIAGRAM_LAYOUT_CLASSES == layout_spec.CLASS_TO_LAYOUT


def test_diagram_layout_classes_all_exist_in_css() -> None:
    implemented = classes.all_section_classes()
    missing = sorted(set(classes.DIAGRAM_LAYOUT_CLASSES) - implemented)
    assert missing == [], f"layout mapping references unimplemented classes: {missing}"


def test_diagram_layout_profiles_are_canonical() -> None:
    layout_spec = load_module("layout_spec", "layout_spec.py")
    profiles = set(classes.DIAGRAM_LAYOUT_CLASSES.values())
    assert profiles <= set(layout_spec.LAYOUTS)


def test_asym_layouts_are_not_mapped_to_col2() -> None:
    for cls in ("split-asym", "split-asym-reverse"):
        assert classes.DIAGRAM_LAYOUT_CLASSES[cls] == "asym"


# --- generated manifest -----------------------------------------------------


def test_manifest_exists() -> None:
    assert MANIFEST.is_file(), f"{MANIFEST.name} is missing — run python scripts/diagrams/sync-theme-classes.py"


def test_manifest_is_in_sync() -> None:
    expected = json.dumps(classes.build_manifest(), indent=2, ensure_ascii=False) + "\n"
    assert MANIFEST.read_text(encoding="utf-8") == expected, (
        f"{MANIFEST.name} is stale — run python scripts/diagrams/sync-theme-classes.py"
    )


def test_sync_script_check_mode_passes_for_the_real_repo() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "sync-theme-classes.py"), "--check"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_manifest_section_classes_match_the_css() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert set(data["section_classes"]) == set(classes.THEMES)
    for theme, listed in data["section_classes"].items():
        assert set(listed) == classes.theme_section_classes(theme), theme


def test_linter_reads_the_manifest_rather_than_hardcoding() -> None:
    """The linter must source its class sets from the manifest, otherwise the
    single source of truth is decorative."""
    source = LINTER.read_text(encoding="utf-8")
    assert "theme-classes.json" in source
    assert "_THEME_CLASSES[" in source
    # The old duplicated literals must be gone.
    assert '"cover-aurora", "cover-diagonal"' not in source
    assert "_COL2_CLASSES" not in source
    assert "_ASYM_CLASSES" not in source


def test_linter_fails_loudly_when_the_manifest_is_missing(tmp_path: Path) -> None:
    """A missing manifest must not silently disable the class-based checks."""
    import shutil

    staged = tmp_path / "scripts"
    staged.mkdir()
    shutil.copy(LINTER, staged / LINTER.name)
    result = subprocess.run(
        [sys.executable, str(staged / LINTER.name), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode != 0
    assert "theme class manifest" in result.stderr
    assert "sync-theme-classes.py" in result.stderr
