"""Direct unit tests for `marp-lint.py`'s check functions.

Before this file, no test referenced any `lint_*` function. The linter is the
mandatory first gate in the documented agent workflow, so a false positive makes
an agent "fix" a correct slide and a false negative lets a broken one ship.
Both directions matter, so these tests pin *behaviour* — which markdown is
flagged and which is not — not just the plumbing.

Each `lint_*` function gets:
  - the positive case (must flag),
  - the near-miss cases (must not flag), which is where false positives live,
  - where applicable, the boundary value.

Regression cases already found and fixed are named explicitly.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
LINTER = ROOT / "skills/marp-slide-creator/scripts/marp-lint.py"


def load_module(name: str, path: Path):
    # dataclasses need the module registered in sys.modules before exec.
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


m = load_module("marp_lint_under_test", LINTER)

FM = "---\nmarp: true\ntheme: azure-clarity\n---\n\n"


def deck(body: str) -> str:
    return FM + body


def slides(markdown: str):
    return m.parse_slides(markdown)


def codes_for(markdown: str) -> list[str]:
    """All issue codes across a deck."""
    return [i.code for s in slides(markdown) for i in m.lint_slide(s)]


def first_slide(markdown: str):
    parsed = slides(markdown)
    assert parsed, "deck produced no slides"
    return parsed[0]


def issue_codes(markdown: str) -> list[str]:
    return [i.code for i in m.lint_slide(first_slide(markdown))]


# ============================================================ parse_slides


def test_parse_splits_on_separators_and_skips_frontmatter() -> None:
    parsed = slides(deck("# One\n\n---\n\n# Two\n\n---\n\n# Three\n"))
    assert [s.number for s in parsed] == [1, 2, 3]
    assert [s.headings[0] for s in parsed] == ["One", "Two", "Three"]


def test_parse_works_without_frontmatter() -> None:
    parsed = slides("# One\n\n---\n\n# Two\n")
    assert len(parsed) == 2


def test_slide_numbering_ignores_empty_slides() -> None:
    """Regression: numbering used the split index, so a blank slide between two
    separators shifted every later number (1, 3 instead of 1, 2). Reported
    numbers then disagreed with the section indices Marp and the DOM extractor
    use for the same deck."""
    parsed = slides(deck("# One\n\n---\n\n---\n\n# Two\n"))
    assert [s.number for s in parsed] == [1, 2]


def test_parse_ignores_content_inside_code_fences() -> None:
    """A code example containing `<!-- _class: cover -->` or a `- ` line must
    not be read as slide structure."""
    parsed = slides(deck("# T\n\n```\n<!-- _class: cover -->\n- not a bullet\n```\n"))
    assert parsed[0].classes == set()
    assert parsed[0].list_items == []


def test_parse_collects_classes_images_headings_and_lists() -> None:
    parsed = first_slide(deck(
        "<!-- _class: cols-2 with-header -->\n\n"
        "# Title\n\n"
        "- one\n"
        "2. two\n\n"
        "![width:400px](assets/x.png)\n\n"
        '<div class="columns"><div class="col">a</div></div>\n'
    ))
    assert parsed.classes == {"cols-2", "with-header"}
    assert parsed.list_items == ["one", "two"]
    assert parsed.headings == ["Title"]
    assert parsed.images == [("width:400px", "assets/x.png")]
    assert "columns" in parsed.div_classes and "col" in parsed.div_classes


def test_parse_detects_scoped_list_override() -> None:
    body = "# T\n\n- a\n\n<style scoped>\nsection ul { text-align: left; }\n</style>\n"
    assert first_slide(deck(body)).has_scoped_list_override is True
    assert first_slide(deck("# T\n\n- a\n")).has_scoped_list_override is False


def test_frontmatter_requires_leading_position_zero() -> None:
    """Known and accepted: Marp itself only reads frontmatter at byte 0, so a
    deck with a leading blank line is not a valid Marp deck either. Pinned so
    the behaviour is deliberate rather than accidental."""
    parsed = slides("\n---\nmarp: true\n---\n\n# A\n\n---\n\n# B\n")
    assert len(parsed) == 3


# ==================================================== extract_plain_text


def test_plain_text_excludes_comments_styles_and_tags() -> None:
    text = m.extract_plain_text("<!-- hidden --> <style>.a{}</style><div>x</div> and real")
    assert text == "x and real"


def test_plain_text_unescapes_html_entities() -> None:
    assert "&" in m.extract_plain_text("A &amp; B")


# ============================================ lint_missing_class_directive


@pytest.mark.parametrize("div_class,directive", [
    ("columns", "cols-2"),
    ("columns", "split-2"),
    ("grid", "grid-quadrant"),
    ("profile-layout", "profile"),
])
def test_missing_class_directive_flags_layout_div_without_directive(div_class: str, directive: str) -> None:
    body = f'<div class="{div_class}">x</div>\n'
    assert "MISSING_CLASS_DIRECTIVE" in issue_codes(deck(body))


@pytest.mark.parametrize("div_class,directive", [
    ("columns", "cols-2"),
    ("grid", "grid-sharp"),
])
def test_missing_class_directive_passes_with_directive(div_class: str, directive: str) -> None:
    body = f'<!-- _class: {directive} -->\n\n<div class="{div_class}">x</div>\n'
    assert "MISSING_CLASS_DIRECTIVE" not in issue_codes(deck(body))


def test_missing_class_directive_accepts_any_listed_alternative() -> None:
    """A `grid` div is satisfied by grid-quadrant *or* grid-sharp."""
    body = '<!-- _class: grid-sharp -->\n\n<div class="grid">x</div>\n'
    assert "MISSING_CLASS_DIRECTIVE" not in issue_codes(deck(body))


def test_missing_class_directive_ignores_unrelated_divs() -> None:
    assert issue_codes(deck('<div class="columns-note">x</div>\n')) == []


# ================================================== lint_centered_lists


def test_centered_list_flags_a_list_on_a_cover() -> None:
    assert "CENTERED_LIST" in issue_codes(deck("<!-- _class: cover -->\n\n# T\n\n- a\n- b\n"))


def test_centered_list_respects_scoped_left_align_override() -> None:
    """The documented escape hatch for cover slides that genuinely need a list."""
    body = (
        "<!-- _class: cover -->\n\n# T\n\n- a\n- b\n\n"
        "<style scoped>\nsection ul { text-align: left; }\n</style>\n"
    )
    assert "CENTERED_LIST" not in issue_codes(deck(body))


@pytest.mark.parametrize("cls", [
    "cols-2", "cols-3", "split-2", "split-3", "split-asym",
    "grid-quadrant", "steps", "timeline", "checklist", "dense", "profile",
])
def test_centered_list_passes_on_content_layouts(cls: str) -> None:
    assert "CENTERED_LIST" not in issue_codes(deck(f"<!-- _class: {cls} -->\n\n# T\n\n- a\n- b\n"))


@pytest.mark.parametrize("cls", ["cover", "cover-nebula", "cover-wave", "key-message", "hero", "title-only", "align-center"])
def test_centered_list_flags_every_title_layout(cls: str) -> None:
    assert "CENTERED_LIST" in issue_codes(deck(f"<!-- _class: {cls} -->\n\n# T\n\n- a\n- b\n"))


def test_glass_card_layout_tolerates_a_list() -> None:
    """Regression: `glass-card-layout` centers the slide box but the inner
    `.card` inherits the section's left alignment, so a bulleted feature list
    renders correctly. Flagging it produced a false ERROR on the nebula sample."""
    body = '<!-- _class: glass-card-layout -->\n\n<div class="card">\n\n# T\n\n- a\n- b\n\n</div>\n'
    assert "CENTERED_LIST" not in issue_codes(deck(body))


def test_centered_list_needs_actual_list_items() -> None:
    assert "CENTERED_LIST" not in issue_codes(deck("<!-- _class: cover -->\n\n# T\n"))


# ================================================== lint_oversized_icons


def test_oversized_icon_flags_a_wide_catalog_icon() -> None:
    body = "![width:300px](assets/icons/gear.svg)\n"
    assert "OVERSIZED_ICON" in issue_codes(deck(body))


def test_oversized_icon_boundary_is_inclusive() -> None:
    assert "OVERSIZED_ICON" not in issue_codes(deck("![width:200px](assets/icons/gear.svg)\n"))
    assert "OVERSIZED_ICON" in issue_codes(deck("![width:201px](assets/icons/gear.svg)\n"))


def test_oversized_icon_flags_centred_icon_without_width() -> None:
    assert "OVERSIZED_ICON" in issue_codes(deck("![center](assets/icons/gear.svg)\n"))


def test_oversized_icon_passes_when_alt_says_icon() -> None:
    """`![center icon]` is a deliberate small icon, not a missing constraint."""
    assert "OVERSIZED_ICON" not in issue_codes(deck("![center icon](assets/icons/gear.svg)\n"))


def test_oversized_icon_ignores_background_images() -> None:
    assert "OVERSIZED_ICON" not in issue_codes(deck("![bg right:45%](assets/hero.svg)\n"))


def test_oversized_icon_ignores_raster_images() -> None:
    """Only SVGs are catalog icons; a 900px JPEG photo is legitimate."""
    assert "OVERSIZED_ICON" not in issue_codes(deck("![width:900px](assets/photo.png)\n"))


@pytest.mark.parametrize("src", [
    "assets/flow.svg", "assets/arch.svg", "assets/seq.svg", "assets/state.svg",
    "assets/diagrams/flow.svg", "assets/chart.svg", "assets/drawio/x.svg",
    "assets/render/out.svg", "assets/source.mmd.svg",
])
def test_oversized_icon_does_not_flag_diagrams(src: str) -> None:
    """Regression: the icon check skipped only the hard-coded pair
    ("diagram", "chart") while the embedding check used nine keywords, so a
    diagram named `flow.svg` was an icon to one and a diagram to the other. A
    correct `width:500px` two-column embed got a false ERROR."""
    assert "OVERSIZED_ICON" not in issue_codes(deck("<!-- _class: cols-2 -->\n\n![width:500px](" + src + ")\n"))


def test_icon_and_diagram_checks_agree_on_classification() -> None:
    """Anything the embedding check calls a diagram must never be called an icon.

    This is the invariant that broke: the two checks used different keyword
    sets, so `flow.svg` was a diagram to one and an icon to the other.
    """
    for src in ("assets/flow.svg", "assets/arch.svg", "assets/diagrams/x.svg", "assets/chart.svg"):
        assert m._is_diagram_src(src), src
        assert "OVERSIZED_ICON" not in issue_codes(deck(f"![width:900px]({src})\n")), src


def test_raster_images_are_never_flagged_as_oversized_icons() -> None:
    """Only SVGs can be catalog icons, so the icon check must ignore rasters
    entirely — a 900px photo is legitimate."""
    for src in ("assets/photo.png", "assets/diagrams/x.jpg", "assets/flow.png"):
        assert "OVERSIZED_ICON" not in issue_codes(deck(f"![width:900px]({src})\n")), src


# ================================================ lint_diagram_embedding


def test_diagram_missing_width_is_a_warning() -> None:
    issues = m.lint_diagram_embedding(first_slide(deck("![center](assets/diagrams/x.svg)\n")))
    assert [i.code for i in issues] == ["DIAGRAM_MISSING_WIDTH"]
    assert issues[0].severity == "WARNING"


def test_diagram_overflow_width_is_an_error() -> None:
    issues = m.lint_diagram_embedding(first_slide(deck("![width:1200px](assets/diagrams/x.svg)\n")))
    assert [i.code for i in issues] == ["DIAGRAM_OVERFLOW_WIDTH"]
    assert issues[0].severity == "ERROR"


@pytest.mark.parametrize("cls,width,max_width", [
    ("", 1120, 1120),
    ("cols-2", 520, 520),
    ("split-glass", 520, 520),
    ("split-asym", 710, 710),
    ("cols-3", 340, 340),
])
def test_diagram_width_boundary_is_inclusive(cls: str, width: int, max_width: int) -> None:
    directive = f"<!-- _class: {cls} -->\n\n" if cls else ""
    body = f'{directive}![width:{width}px](assets/diagrams/x.svg)\n'
    assert "DIAGRAM_OVERFLOW_WIDTH" not in issue_codes(deck(body))
    body_over = f'{directive}![width:{max_width + 1}px](assets/diagrams/x.svg)\n'
    assert "DIAGRAM_OVERFLOW_WIDTH" in issue_codes(deck(body_over))


def test_narrowest_layout_class_wins_when_several_are_present() -> None:
    """`asym` is 710px and `col2` is 520px; when both appear the tighter
    constraint is the one that must hold."""
    body = "<!-- _class: split-asym cols-2 -->\n\n![width:600px](assets/diagrams/x.svg)\n"
    assert "DIAGRAM_OVERFLOW_WIDTH" in issue_codes(deck(body))


def test_diagram_ignored_on_non_svg() -> None:
    assert issue_codes(deck("![center](assets/diagrams/x.png)\n")) == []


def test_diagram_embedding_ignores_non_diagram_paths() -> None:
    """A logo is not a diagram, so the *embedding* check ignores it. The icon
    check may still flag it — that is a separate, correct concern."""
    slide = first_slide(deck("![center](assets/logos/mark.svg)\n"))
    assert m.lint_diagram_embedding(slide) == []


def test_diagram_on_title_layout_is_a_warning() -> None:
    body = "<!-- _class: key-message -->\n\n![width:900px](assets/diagrams/x.svg)\n"
    assert "DIAGRAM_ON_CENTERED_LAYOUT" in issue_codes(deck(body))


def test_missing_width_message_names_the_layout_budget() -> None:
    issues = m.lint_diagram_embedding(first_slide(deck("<!-- _class: cols-3 -->\n\n![center](assets/diagrams/x.svg)\n")))
    assert "340px" in issues[0].message
    assert "col3" in issues[0].message


# ======================================================== _slide_layout_key


@pytest.mark.parametrize("classes,expected", [
    (set(), "full"),
    ({"cover"}, "full"),
    ({"cols-2"}, "col2"),
    ({"split-2"}, "col2"),
    ({"split-glass"}, "col2"),
    ({"glass-card-layout"}, "col2"),
    ({"split-asym"}, "asym"),
    ({"split-asym-reverse"}, "asym"),
    ({"cols-3"}, "col3"),
    ({"split-3"}, "col3"),
    ({"split-asym", "cols-2"}, "col2"),
    ({"split-asym", "cols-3"}, "col3"),
])
def test_slide_layout_key(classes: set[str], expected: str) -> None:
    slide = m.SlideInfo(number=1, raw_content="", classes=set(classes))
    assert m._slide_layout_key(slide) == expected


# ======================================================== lint_bullet_hell


def _bullets(n: int) -> str:
    return "".join(f"- item {i}\n" for i in range(n))


@pytest.mark.parametrize("cls,allowed", [
    ("", 4), ("cols-2", 6), ("split-glass", 6), ("split-asym", 6), ("cols-3", 9),
])
def test_bullet_hell_threshold_per_layout(cls: str, allowed: int) -> None:
    directive = f"<!-- _class: {cls} -->\n\n" if cls else ""
    assert "BULLET_HELL" not in issue_codes(deck(f"{directive}# T\n\n" + _bullets(allowed)))
    assert "BULLET_HELL" in issue_codes(deck(f"{directive}# T\n\n" + _bullets(allowed + 1)))


def test_split_glass_gets_the_two_column_budget() -> None:
    """Regression: the bullet threshold used its own class set, which omitted
    `split-glass`, so 5-6 bullets on a legitimate two-column slide were warned
    against a single-column limit of 4."""
    assert "BULLET_HELL" not in issue_codes(deck("<!-- _class: split-glass -->\n\n# T\n\n" + _bullets(5)))


@pytest.mark.parametrize("cls", ["checklist", "steps", "timeline", "timetable", "toc", "toc-focus"])
def test_bullet_hell_exempts_structural_list_layouts(cls: str) -> None:
    assert "BULLET_HELL" not in issue_codes(deck(f"<!-- _class: {cls} -->\n\n# T\n\n" + _bullets(14)))


def test_bullet_hell_message_states_count_and_limit() -> None:
    issues = [i for i in m.lint_slide(first_slide(deck("# T\n\n" + _bullets(6)))) if i.code == "BULLET_HELL"]
    assert issues and "6 bullet points" in issues[0].message
    assert "max is 4" in issues[0].message


# ======================================================== lint_weak_title


@pytest.mark.parametrize("heading", ["概要", "まとめ", "アジェンダ", "背景", "システム構成", "今後の展望"])
def test_weak_title_flags_generic_japanese_headings(heading: str) -> None:
    assert "WEAK_TITLE" in issue_codes(deck(f"# {heading}\n"))


@pytest.mark.parametrize("heading", ["Overview", "Summary", "Agenda", "Background", "Next steps", "Q&A"])
def test_weak_title_flags_generic_english_headings(heading: str) -> None:
    assert "WEAK_TITLE" in issue_codes(deck(f"# {heading}\n"))


def test_weak_title_passes_a_heading_with_a_conclusion() -> None:
    assert "WEAK_TITLE" not in issue_codes(deck("#  microservices cut deploy time by 60%\n"))


@pytest.mark.parametrize("cls", ["cover", "cover-nebula", "key-message", "hero", "title-only", "title-elegant", "toc", "toc-focus"])
def test_weak_title_exempts_title_layouts(cls: str) -> None:
    assert "WEAK_TITLE" not in issue_codes(deck(f"<!-- _class: {cls} -->\n\n# 概要\n"))


def test_weak_title_message_reports_the_cleaned_heading() -> None:
    """Markup is stripped before the heading is quoted back, so the message
    shows the words rather than the tags."""
    body = '# <span class="badge">NEW</span> 概要\n'
    issues = [i for i in m.lint_slide(first_slide(deck(body))) if i.code == "WEAK_TITLE"]
    assert issues == [] or "<span" not in issues[0].message


def test_weak_title_still_flags_markup_wrapped_generic_headings() -> None:
    """`<span>概要</span>` must be caught: the tags are stripped, then the
    pattern is matched against what remains."""
    body = "# <span>概要</span>\n"
    assert "WEAK_TITLE" in issue_codes(deck(body))


def test_weak_title_reports_at_most_one_issue_per_heading() -> None:
    body = "# 概要\n\n## まとめ\n"
    assert issue_codes(deck(body)).count("WEAK_TITLE") == 2


# ==================================================== lint_unlabeled_list


def test_unlabeled_list_flags_unlabelled_long_bullets() -> None:
    body = "# T\n\n" + "".join(f"- {chr(97 + i)}" * 1 + "a very long bullet without a label here\n" for i in range(3))
    assert "UNLABELED_LIST" in issue_codes(deck(body))


@pytest.mark.parametrize("prefix", ["**Label**: detail", "<b>Label</b> detail", "<strong>Label</strong> detail"])
def test_unlabeled_list_accepts_bold_key_labels(prefix: str) -> None:
    body = "# T\n\n" + "".join(f"- {prefix} {'x' * 40}\n" for _ in range(3))
    assert "UNLABELED_LIST" not in issue_codes(deck(body))


def test_unlabeled_list_ignores_short_bullets() -> None:
    body = "# T\n\n" + "".join(f"- short {i}\n" for i in range(4))
    assert "UNLABELED_LIST" not in issue_codes(deck(body))


def test_unlabeled_list_needs_at_least_two_long_bullets() -> None:
    one = "# T\n\n- a single long unlabelled bullet that runs on and on and on\n"
    assert "UNLABELED_LIST" not in issue_codes(deck(one))


# ====================================================== lint_dense_content


def test_dense_content_flags_a_text_wall() -> None:
    body = "# T\n\n" + ("word " * 120)
    assert "DENSE_CONTENT" in issue_codes(deck(body))


def test_dense_content_passes_a_short_slide() -> None:
    assert "DENSE_CONTENT" not in issue_codes(deck("# T\n\nShort.\n"))


@pytest.mark.parametrize("cls", ["dense", "extra-dense"])
def test_dense_content_exempts_density_layouts(cls: str) -> None:
    body = f"<!-- _class: {cls} -->\n\n# T\n\n" + ("word " * 120)
    assert "DENSE_CONTENT" not in issue_codes(deck(body))


def test_dense_content_message_range_matches_the_threshold() -> None:
    """Regression: the message hard-coded "200-350" while MAX_RECOMMENDED_CHARS
    was 400. Both now derive from the constant."""
    expected_low = int(m.MAX_RECOMMENDED_CHARS * 0.5)
    expected_high = int(m.MAX_RECOMMENDED_CHARS * 0.875)
    issues = [i for i in m.lint_slide(first_slide(deck("# T\n\n" + ("word " * 120)))) if i.code == "DENSE_CONTENT"]
    assert f"{expected_low}-{expected_high}" in issues[0].message


def test_thresholds_are_not_left_dead_in_the_module() -> None:
    """Every named threshold must actually be read somewhere."""
    source = LINTER.read_text(encoding="utf-8")
    for const in (
        "MAX_RECOMMENDED_CHARS",
        "MIN_LABELLED_CHARS",
        "UNLABELLED_LIST_MIN",
        "ICON_MAX_WIDTH_PX",
    ):
        uses = source.count(const)
        # 1 definition + at least one use
        assert uses >= 2, f"{const} is defined but never read"


# ============================================================= lint_slide


def test_structural_only_suppresses_readability_warnings() -> None:
    body = "# 概要\n\n" + _bullets(8)
    full = [i.code for i in m.lint_slide(first_slide(deck(body)))]
    structural = [i.code for i in m.lint_slide(first_slide(deck(body)), structural_only=True)]
    assert "BULLET_HELL" in full
    assert "BULLET_HELL" not in structural
    assert "WEAK_TITLE" in full and "WEAK_TITLE" not in structural


def test_structural_only_keeps_errors() -> None:
    body = '<!-- _class: cover -->\n\n# T\n\n- a\n'
    structural = [i.code for i in m.lint_slide(first_slide(deck(body)), structural_only=True)]
    assert "CENTERED_LIST" in structural


def test_clean_deck_produces_no_issues() -> None:
    body = "<!-- _class: cols-2 -->\n\n# Two columns compared\n\n<div class=\"columns\">\n<div class=\"col\">\n- a\n</div>\n</div>\n"
    assert issue_codes(deck(body)) == []


# ================================================================== main


def _run(*args: str) -> subprocess.CompletedProcess:
    return _run_at(LINTER, *args)


def _run_at(linter: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(linter), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_main_exits_zero_for_a_clean_deck(tmp_path: Path) -> None:
    path = tmp_path / "deck.md"
    path.write_text(deck("<!-- _class: cols-2 -->\n\n# Comparison\n\n<div class=\"columns\">\n<div class=\"col\">\n- a\n</div>\n</div>\n"), encoding="utf-8")
    result = _run(str(path))
    assert result.returncode == 0, result.stdout


def test_main_exits_two_on_error(tmp_path: Path) -> None:
    path = tmp_path / "deck.md"
    path.write_text(deck('<!-- _class: cover -->\n\n# T\n\n- a\n- b\n'), encoding="utf-8")
    assert _run(str(path)).returncode == 2


def test_main_exits_zero_for_warnings_unless_strict(tmp_path: Path) -> None:
    path = tmp_path / "deck.md"
    path.write_text(deck("# 概要\n\n" + _bullets(6)), encoding="utf-8")
    assert _run(str(path)).returncode == 0
    assert _run(str(path), "--strict").returncode == 2


def test_main_json_output_is_parseable(tmp_path: Path) -> None:
    import json

    path = tmp_path / "deck.md"
    path.write_text(deck("# 概要\n"), encoding="utf-8")
    result = _run(str(path), "--json")
    payload = json.loads(result.stdout)
    assert isinstance(payload, list) and payload
    assert {"slide", "severity", "code", "message"} <= set(payload[0])


def test_main_reports_a_missing_file() -> None:
    result = _run("definitely-not-here.md")
    assert result.returncode == 1
    assert "not found" in result.stderr.lower()


def test_main_reports_a_clear_error_when_the_manifest_is_missing(tmp_path: Path) -> None:
    """A missing manifest must not silently disable the class-based checks."""
    staged = tmp_path / "scripts"
    staged.mkdir()
    (staged / LINTER.name).write_bytes(LINTER.read_bytes())
    result = _run_at(staged / LINTER.name, "x.md")
    assert result.returncode != 0
    assert "theme class manifest" in result.stderr
    assert "sync-theme-classes.py" in result.stderr
