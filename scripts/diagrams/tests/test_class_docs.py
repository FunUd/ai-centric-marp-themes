"""Tests for check-class-docs.py — the README / class-system gate.

The README claims "All themes share a unified class system". This suite keeps
that claim honest in both directions:

- an implemented class must be documented, or users cannot discover it;
- a class documented as universal must exist in every theme, or users will
  rely on it and get nothing.

Plus the mechanics of the checker itself, since a checker that cannot fail is
worse than no checker.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ROOT = SCRIPT_DIR.parent.parent
README = ROOT / "docs" / "classes.md"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


docs = load_module("check_class_docs", "check-class-docs.py")
classes = load_module("theme_classes_for_docs", "theme_classes.py")


# --- the real repository is clean ------------------------------------------


def test_readme_documents_every_user_facing_class() -> None:
    missing = docs.undocumented(README.read_text(encoding="utf-8"))
    assert missing == {}, f"implemented but undocumented: {sorted(missing)}"


def test_no_unscoped_theme_gaps_in_the_readme() -> None:
    text = README.read_text(encoding="utf-8")
    gaps = docs.missing_per_theme(docs.readme_documented_table_classes(text))
    scoped = docs.theme_specific_markers(text)
    unclaimed = {theme: [c for c in items if c not in scoped] for theme, items in gaps.items()}
    unclaimed = {t: items for t, items in unclaimed.items() if items}
    assert unclaimed == {}, f"documented as universal but theme-specific: {unclaimed}"


def test_script_exits_zero_for_the_real_repository(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["check-class-docs.py"])
    assert docs.main() == 0
    assert "in sync" in capsys.readouterr().out


# --- universal utilities really are universal -------------------------------


@pytest.mark.parametrize(
    "cls",
    [
        "v-center",
        "v-middle",
        "v-top",
        "v-bottom",
        "text-left",
        "text-center",
        "text-right",
        "align-left",
        "align-center",
        "align-right",
        "no-pagination",
        "no-header",
        "no-footer",
        "pagination-left",
        "with-header",
        "text-accent",
        "text-sub",
        "text-blue",
        "text-green",
        "text-orange",
        "text-red",
    ],
)
def test_utility_exists_in_every_theme(cls: str) -> None:
    """Regression guard for the drift this checker was written for.

    `v-middle` was missing from nebula-glass and slate-minimal, `pagination-left`
    from nebula-glass, `align-*` from nebula-glass and slate-minimal, and
    `text-sub` from nebula-glass — all while the README listed them as
    universal.
    """
    missing = [t for t in classes.THEMES if cls not in classes.theme_all_classes(t)]
    assert missing == [], f"{cls} missing from: {missing}"


@pytest.mark.parametrize(
    "cls",
    [
        "cover",
        "toc",
        "toc-focus",
        "cols-2",
        "cols-3",
        "split-2",
        "split-3",
        "grid-quadrant",
        "grid-sharp",
        "steps",
        "timeline",
        "checklist",
        "timetable",
        "key-message",
        "profile",
        "dense",
        "extra-dense",
        "callout",
        "badge",
    ],
)
def test_core_layout_class_exists_in_every_theme(cls: str) -> None:
    missing = [t for t in classes.THEMES if cls not in classes.theme_all_classes(t)]
    assert missing == [], f"{cls} missing from: {missing}"


def test_nebula_cover_alias_matches_cover_nebula() -> None:
    """nebula-glass added `cover` as an alias so a deck can switch themes
    without editing class directives. Both must get identical chrome hiding."""
    css = (classes.THEMES_DIR / "nebula-glass.css").read_text(encoding="utf-8")
    assert "section.cover-nebula,\nsection.cover {" in css
    assert "section.cover-nebula::after,\nsection.cover::after {" in css


# --- checker mechanics ------------------------------------------------------


def test_undocumented_detects_a_new_class(monkeypatch) -> None:
    monkeypatch.setattr(docs, "user_facing_classes", lambda: {"cols-2", "brand-new"})
    result = docs.undocumented("The README documents `cols-2`.")
    assert result == {"brand-new": []}


def test_readme_backticked_classes_reads_html_spans() -> None:
    text = 'Use `<div class="callout blue">` and `cols-2` and `text-accent`.'
    found = docs.readme_backticked_classes(text)
    assert {"callout", "blue", "cols-2", "text-accent"} <= found


def test_readme_backticked_classes_ignores_fenced_blocks() -> None:
    """Regression: ``` fences paired with inline backticks, scrambling every
    span in the document and reporting all 80 classes as undocumented."""
    text = "Documented: `cols-2`.\n```yaml\n---\ntheme: azure-clarity\n```\nAlso `cover`.\n"
    found = docs.readme_backticked_classes(text)
    assert "cols-2" in found
    assert "cover" in found
    assert "theme" not in found
    assert "yaml" not in found


def test_theme_specific_markers_only_reads_marked_rows() -> None:
    text = "\n".join(
        [
            "| `cover-aurora` | *(Prism Edge)* aurora background |",
            "| `cover` | Title slide with gradient background |",
        ]
    )
    scoped = docs.theme_specific_markers(text)
    assert "cover-aurora" in scoped
    assert "cover" not in scoped


def test_missing_per_theme_reports_only_real_classes() -> None:
    text = "| `cols-2` / `cols-3` | card columns |\n"
    documented = docs.readme_documented_table_classes(text)
    gaps = docs.missing_per_theme(documented)
    # cols-2/cols-3 exist everywhere, so no gaps.
    assert gaps == {}


def test_main_fails_on_drift(monkeypatch, capsys) -> None:
    monkeypatch.setattr(docs, "user_facing_classes", lambda: {"totally-unused-class"})
    monkeypatch.setattr(sys, "argv", ["check-class-docs.py"])
    rc = docs.main()
    captured = capsys.readouterr()
    assert rc == 1
    assert "[UNDOCUMENTED]" in captured.out
    assert "totally-unused-class" in captured.out


def test_main_allow_unlisted_downgrades_to_warning(monkeypatch, capsys) -> None:
    monkeypatch.setattr(docs, "user_facing_classes", lambda: {"totally-unused-class"})
    monkeypatch.setattr(sys, "argv", ["check-class-docs.py", "--allow-unlisted"])
    rc = docs.main()
    assert rc == 0
    assert "[WARN]" in capsys.readouterr().out


def test_internal_classes_are_not_user_facing() -> None:
    """hljs-* and structural children must not be demanded in the README."""
    user_facing = docs.user_facing_classes()
    assert not any(c.startswith("hljs-") for c in user_facing)
    for structural in ("columns", "col", "cell", "grid", "card"):
        assert structural not in user_facing
