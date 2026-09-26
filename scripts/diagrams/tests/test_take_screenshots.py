"""Tests for scripts/take-screenshots.py.

Playwright and Marp CLI are fully faked: no browser, no npx. Covers
parse_args, build_html's exit contract, hide_controls, slide advancement in
take_screenshots, ad-hoc slide selection (all / out-of-range / no valid),
list_slide_count cleanup, and process_theme's unknown-theme guard.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


shots = load_module("take_screenshots_under_test", SCRIPTS_DIR / "take-screenshots.py")


# --- fakes -------------------------------------------------------------------


class FakeKeyboard:
    def __init__(self) -> None:
        self.pressed: list[str] = []

    def press(self, key: str) -> None:
        self.pressed.append(key)


class FakeMouse:
    def __init__(self) -> None:
        self.moves: list[tuple[int, int]] = []

    def move(self, x: int, y: int) -> None:
        self.moves.append((x, y))


class FakePage:
    def __init__(self, slide_count: int) -> None:
        self.slide_count = slide_count
        self.keyboard = FakeKeyboard()
        self.mouse = FakeMouse()
        self.screenshots: list[Path] = []
        self.styles: list[str] = []
        self.urls: list[str] = []
        self.clicks: list[str] = []
        self.waits: list[int] = []

    def goto(self, url: str, wait_until: str | None = None) -> None:
        self.urls.append(url)

    def wait_for_timeout(self, ms: int) -> None:
        self.waits.append(ms)

    def evaluate(self, script: str) -> int:
        return self.slide_count

    def click(self, selector: str) -> None:
        self.clicks.append(selector)

    def add_style_tag(self, content: str | None = None) -> None:
        self.styles.append(content or "")

    def screenshot(self, path: str | None = None) -> None:
        self.screenshots.append(Path(path))


class FakeBrowser:
    def __init__(self, page: FakePage) -> None:
        self.page = page
        self.closed = False

    def new_page(self, viewport: dict | None = None) -> FakePage:
        assert viewport == {"width": 1280, "height": 720}
        return self.page

    def close(self) -> None:
        self.closed = True


def install_playwright(monkeypatch, page: FakePage) -> FakeBrowser:
    browser = FakeBrowser(page)

    class _Chromium:
        def launch(self, headless: bool = True):
            assert headless is True
            return browser

    class _P:
        chromium = _Chromium()

    @contextmanager
    def fake_sync_playwright():
        yield _P()

    monkeypatch.setattr(shots, "sync_playwright", fake_sync_playwright)
    # __main__ re-imports the symbol from the source module (runpy tests).
    monkeypatch.setattr(sys.modules["playwright.sync_api"], "sync_playwright", fake_sync_playwright)
    return browser


def install_build_html(monkeypatch, created: list[Path] | None = None) -> list[tuple[Path, Path]]:
    calls: list[tuple[Path, Path]] = []

    def fake_build_html(slide_md: Path, output_html: Path) -> None:
        calls.append((slide_md, output_html))
        output_html.write_text("<html></html>", encoding="utf-8")
        if created is not None:
            created.append(output_html)

    monkeypatch.setattr(shots, "build_html", fake_build_html)
    return calls


# --- parse_args --------------------------------------------------------------


def test_parse_args_theme_mode(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["take-screenshots.py", "nebula-glass"])
    _, args = shots.parse_args()

    assert args.theme == "nebula-glass"
    assert args.slide is None
    assert args.slide_numbers == []


def test_parse_args_slide_mode_with_numbers(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["take-screenshots.py", "--slide", "deck.md", "1", "5", "all"])
    _, args = shots.parse_args()

    assert args.slide == "deck.md"
    # The first token is pulled back out of `theme` into slide_numbers.
    assert args.theme is None
    assert args.slide_numbers == ["1", "5", "all"]


def test_parse_args_slide_mode_single_token(monkeypatch) -> None:
    # Before the fix, both of these lost their only token to `theme`.
    monkeypatch.setattr(sys, "argv", ["take-screenshots.py", "--slide", "deck.md", "3"])
    _, args = shots.parse_args()
    assert args.theme is None
    assert args.slide_numbers == ["3"]

    monkeypatch.setattr(sys, "argv", ["take-screenshots.py", "--slide", "deck.md", "all"])
    _, args = shots.parse_args()
    assert args.theme is None
    assert args.slide_numbers == ["all"]

    monkeypatch.setattr(sys, "argv", ["take-screenshots.py", "--slide", "deck.md"])
    _, args = shots.parse_args()
    assert args.theme is None
    assert args.slide_numbers == []


def test_parse_args_list_and_output(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["take-screenshots.py", "--list", "deck.md", "-o", "shots"])
    _, args = shots.parse_args()

    assert args.list == "deck.md"
    assert args.output == "shots"


def test_parse_args_defaults(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["take-screenshots.py"])
    # Wide terminal so argparse does not wrap the long default-path line.
    monkeypatch.setenv("COLUMNS", "500")
    parser, args = shots.parse_args()

    assert args.theme is None
    assert args.list is None
    assert args.slide_numbers == []
    help_text = parser.format_help()
    assert "Output directory (default:" in help_text
    assert str(shots.OUTPUT_DIR) in help_text


# --- __main__ dispatch (runpy) ------------------------------------------------

_SCRIPT = str(shots.__file__)


def _runpy_main(monkeypatch, *args: str):
    """Execute the script's __main__ block in-process.

    Returns the SystemExit code, or None when the block falls off the end.
    """
    import runpy

    monkeypatch.setattr(sys, "argv", [_SCRIPT, *args])
    try:
        runpy.run_path(_SCRIPT, run_name="__main__")
    except SystemExit as exc:
        return exc.code
    return None


def _install_marp_cli(monkeypatch) -> None:
    # build_html only checks the subprocess exit status.
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(shots.subprocess, "run", fake_run)


def test_main_without_args_prints_help(monkeypatch, capsys) -> None:
    assert _runpy_main(monkeypatch) == 1

    assert "usage:" in capsys.readouterr().out


def test_main_list_mode_prints_count_and_exits_zero(monkeypatch, capsys) -> None:
    _install_marp_cli(monkeypatch)
    install_playwright(monkeypatch, FakePage(slide_count=7))

    assert _runpy_main(monkeypatch, "--list", "README.md") == 0

    assert "README.md: 7 slides" in capsys.readouterr().out
    assert not (shots.WORKSPACE / "_list_temp.html").exists()


def test_main_slide_mode_requires_numbers_or_all(monkeypatch, capsys) -> None:
    # A relative --output is resolved against the workspace root before the
    # guard fires; capture never starts, so nothing is written.
    assert _runpy_main(monkeypatch, "--slide", "README.md", "-o", "rel-shots") == 1

    assert "Specify slide numbers" in capsys.readouterr().out
    assert not (shots.WORKSPACE / "rel-shots").exists()


def test_main_slide_mode_rejects_non_numeric_numbers(monkeypatch, capsys) -> None:
    # slide_numbers keeps every token after FILE; int("x") raises and the
    # guard reports the offending list.
    assert _runpy_main(monkeypatch, "--slide", "README.md", "1", "5", "x") == 1

    assert "Slide numbers must be integers or 'all'" in capsys.readouterr().out


def test_main_slide_mode_captures_all(monkeypatch, tmp_path: Path, capsys) -> None:
    _install_marp_cli(monkeypatch)
    page = FakePage(slide_count=40)
    browser = install_playwright(monkeypatch, page)

    assert _runpy_main(monkeypatch, "--slide", "README.md", "all", "-o", str(tmp_path)) == 0

    out = capsys.readouterr().out
    assert "Total slides: 40" in out
    assert "✅ Done!" in out
    assert browser.closed is True
    assert len(page.screenshots) == 40


def test_main_slide_mode_captures_selected_numbers(monkeypatch, tmp_path: Path, capsys) -> None:
    _install_marp_cli(monkeypatch)
    page = FakePage(slide_count=40)
    install_playwright(monkeypatch, page)

    # Both tokens after FILE become slide numbers (1-based slides 1 and 5).
    assert _runpy_main(monkeypatch, "--slide", "README.md", "1", "5", "-o", str(tmp_path)) == 0

    assert [p.name for p in page.screenshots] == ["README-slide-001.png", "README-slide-005.png"]
    assert "✅ Done!" in capsys.readouterr().out


def test_main_theme_mode_single_theme(monkeypatch, tmp_path: Path, capsys) -> None:
    _install_marp_cli(monkeypatch)
    page = FakePage(slide_count=40)
    install_playwright(monkeypatch, page)

    # Falls off the end of the block: no SystemExit.
    assert _runpy_main(monkeypatch, "azure-clarity", "-o", str(tmp_path)) is None

    out = capsys.readouterr().out
    assert "Theme: azure-clarity" in out
    assert "✅ Done!" in out
    assert len(page.screenshots) == len(shots.THEME_CONFIG["azure-clarity"]["screenshots"])


def test_main_theme_mode_all_iterates_every_theme(monkeypatch, tmp_path: Path, capsys) -> None:
    _install_marp_cli(monkeypatch)
    page = FakePage(slide_count=40)
    install_playwright(monkeypatch, page)

    assert _runpy_main(monkeypatch, "all", "-o", str(tmp_path)) is None

    out = capsys.readouterr().out
    for theme in shots.THEME_CONFIG:
        assert f"Theme: {theme}" in out
    assert "✅ Done!" in out
    expected = sum(len(cfg["screenshots"]) for cfg in shots.THEME_CONFIG.values())
    assert len(page.screenshots) == expected


# --- build_html / hide_controls ----------------------------------------------


def test_build_html_success_invokes_marp_cli(monkeypatch) -> None:
    """`build_html` must build an argv list, not a shell string.

    A shell string meant deck paths were re-parsed by the shell, and it is a
    needless injection surface. The list also lets the Marp CLI version be
    pinned.
    """
    captured: dict = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["cwd"] = kwargs.get("cwd")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(shots.subprocess, "run", fake_run)

    shots.build_html(Path("deck.md"), Path("out.html"))

    cmd = captured["cmd"]
    assert isinstance(cmd, list), f"expected an argv list, got {type(cmd).__name__}"
    assert all(isinstance(part, str) for part in cmd)
    assert any(part.startswith("@marp-team/marp-cli@") for part in cmd), cmd
    assert str(shots.THEME_DIR) in cmd
    assert "--allow-local-files" in cmd
    assert captured["cwd"] == str(shots.WORKSPACE)
    assert "shell" not in captured.get("kwargs", {})


def test_build_html_uses_the_pinned_marp_cli(monkeypatch) -> None:
    """Regression guard against reintroducing an unpinned `npx -y <pkg>`."""
    captured: dict = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(shots.subprocess, "run", fake_run)
    shots.build_html(Path("deck.md"), Path("out.html"))

    spec = next(p for p in captured["cmd"] if p.startswith("@marp-team/marp-cli"))
    version = spec.rsplit("@", 1)[1]
    assert version and version[0].isdigit(), f"unpinned spec: {spec}"
    assert not version.startswith(("^", "~"))


def test_build_html_preserves_paths_containing_spaces(monkeypatch) -> None:
    """A deck path with a space must arrive as one argv element.

    This is what the shell string used to get wrong: quoting happened to cover
    it, but nothing in the code guaranteed it.
    """
    captured: dict = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(shots.subprocess, "run", fake_run)
    spaced = Path("my deck/some deck.md")
    shots.build_html(spaced, Path("out dir/out.html"))

    assert str(spaced) in captured["cmd"]
    assert str(Path("out dir/out.html")) in captured["cmd"]


def test_build_html_exits_on_failure(monkeypatch, capsys) -> None:
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 1, "", "marp exploded")

    monkeypatch.setattr(shots.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="marp exploded"):
        shots.build_html(Path("deck.md"), Path("out.html"))


def test_hide_controls_applies_css_and_parks_mouse() -> None:
    page = FakePage(slide_count=1)

    shots.hide_controls(page)

    assert page.styles == [shots.HIDE_CONTROLS_CSS]
    assert page.mouse.moves == [(-100, -100)]
    assert page.waits == [300]


# --- take_screenshots --------------------------------------------------------


def test_take_screenshots_sorts_advances_and_skips_missing_slides(monkeypatch, tmp_path: Path) -> None:
    page = FakePage(slide_count=10)
    browser = install_playwright(monkeypatch, page)
    html = tmp_path / "deck.html"
    html.write_text("<html></html>", encoding="utf-8")
    out_dir = tmp_path / "shots"

    shots.take_screenshots(
        "deck",
        html,
        [("late.png", 5), ("first.png", 0), ("missing.png", 12)],
        out_dir,
    )

    # Sorted ascending: no presses for slide 0, then 5 ArrowRight presses.
    assert page.keyboard.pressed == ["ArrowRight"] * 5
    assert page.screenshots == [out_dir / "first.png", out_dir / "late.png"]
    assert page.urls and page.urls[0].startswith("file://")
    assert page.clicks == ["body"]
    # Control hiding re-applied after every transition.
    assert page.styles.count(shots.HIDE_CONTROLS_CSS) >= 3
    assert browser.closed is True
    assert "missing.png" not in {p.name for p in page.screenshots}


def test_take_screenshots_default_output_dir(monkeypatch, tmp_path: Path, monkeypatch_workspace: None = None) -> None:
    page = FakePage(slide_count=3)
    install_playwright(monkeypatch, page)
    html = tmp_path / "deck.html"
    html.write_text("<html></html>", encoding="utf-8")

    shots.take_screenshots("deck", html, [("only.png", 0)])

    # No output_dir -> module default.
    assert shots.OUTPUT_DIR in {p.parent for p in page.screenshots}


# --- list_slide_count --------------------------------------------------------


def test_list_slide_count_missing_file(capsys) -> None:
    with pytest.raises(RuntimeError, match="File not found"):
        shots.list_slide_count(Path("does-not-exist.md"))


def test_list_slide_count_prints_and_cleans_up(monkeypatch, tmp_path: Path, capsys) -> None:
    page = FakePage(slide_count=4)
    install_playwright(monkeypatch, page)
    install_build_html(monkeypatch)
    slide = tmp_path / "deck.md"
    slide.write_text("# hi", encoding="utf-8")

    shots.list_slide_count(slide)

    out = capsys.readouterr().out
    assert "deck.md: 4 slides" in out
    temp_html = shots.WORKSPACE / "_list_temp.html"
    assert not temp_html.exists()


# --- take_ad_hoc_screenshots -------------------------------------------------


def test_ad_hoc_missing_file_exits(capsys) -> None:
    with pytest.raises(RuntimeError, match="File not found"):
        shots.take_ad_hoc_screenshots(Path("missing.md"), [1], Path("/tmp/out"))


def test_ad_hoc_all_selects_every_slide(monkeypatch, tmp_path: Path) -> None:
    page = FakePage(slide_count=3)
    install_playwright(monkeypatch, page)
    build_calls = install_build_html(monkeypatch)
    captured: list = []
    monkeypatch.setattr(shots, "take_screenshots", lambda *a: captured.append(a))
    slide = tmp_path / "deck.md"
    slide.write_text("# hi", encoding="utf-8")
    out_dir = tmp_path / "out"

    shots.take_ad_hoc_screenshots(slide, "all", out_dir)

    assert build_calls and build_calls[0][0] == slide
    assert len(captured) == 1
    _, _, screenshots, target_dir = captured[0]
    assert [idx for _, idx in screenshots] == [0, 1, 2]
    assert [name for name, _ in screenshots] == [
        "deck-slide-001.png", "deck-slide-002.png", "deck-slide-003.png"
    ]
    assert target_dir == out_dir
    # Temp html removed in the finally block.
    assert not (shots.WORKSPACE / "_adhoc_temp.html").exists()


def test_ad_hoc_skips_out_of_range_numbers(monkeypatch, tmp_path: Path, capsys) -> None:
    page = FakePage(slide_count=3)
    install_playwright(monkeypatch, page)
    install_build_html(monkeypatch)
    captured: list = []
    monkeypatch.setattr(shots, "take_screenshots", lambda *a: captured.append(a))
    slide = tmp_path / "deck.md"
    slide.write_text("# hi", encoding="utf-8")

    shots.take_ad_hoc_screenshots(slide, [0, 2, 99], tmp_path / "out")

    out = capsys.readouterr().out
    _, _, screenshots, _ = captured[0]
    assert [idx for _, idx in screenshots] == [1]  # only 1-based slide 2 exists
    assert "Slide 99 is out of range" in out
    assert "Slide 0 is out of range" in out


def test_ad_hoc_returns_when_no_valid_slides(monkeypatch, tmp_path: Path, capsys) -> None:
    page = FakePage(slide_count=2)
    install_playwright(monkeypatch, page)
    install_build_html(monkeypatch)
    captured: list = []
    monkeypatch.setattr(shots, "take_screenshots", lambda *a: captured.append(a))
    slide = tmp_path / "deck.md"
    slide.write_text("# hi", encoding="utf-8")

    shots.take_ad_hoc_screenshots(slide, [42], tmp_path / "out")

    out = capsys.readouterr().out
    assert "No valid slides to capture" in out
    assert captured == []
    assert not (shots.WORKSPACE / "_adhoc_temp.html").exists()


# --- process_theme -----------------------------------------------------------


def test_process_theme_unknown_theme_exits(capsys) -> None:
    with pytest.raises(RuntimeError, match="Unknown theme: not-a-theme"):
        shots.process_theme("not-a-theme")


def test_process_theme_runs_pipeline_and_cleans_temp(monkeypatch, tmp_path: Path) -> None:
    page = FakePage(slide_count=30)
    install_playwright(monkeypatch, page)
    build_calls = install_build_html(monkeypatch)
    captured: list = []
    monkeypatch.setattr(shots, "take_screenshots", lambda *a: captured.append(a))

    shots.process_theme("azure-clarity", tmp_path / "out")

    config = shots.THEME_CONFIG["azure-clarity"]
    assert build_calls[0][0] == config["slide"]
    assert len(captured) == 1
    _, _, screenshots, target_dir = captured[0]
    assert screenshots == config["screenshots"]
    assert target_dir == tmp_path / "out"
    assert not (shots.WORKSPACE / "_azure-clarity_temp.html").exists()


def test_cli_help_exits_zero() -> None:
    """The script's __main__ entry answers --help without touching Marp."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "take-screenshots.py"), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode == 0
    assert "Capture screenshots of Marp slides" in result.stdout


def test_cli_help_lists_every_configured_theme() -> None:
    """The help text must not go stale as themes are added to THEME_CONFIG."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "take-screenshots.py"), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    for theme in shots.THEME_CONFIG:
        assert theme in result.stdout, f"{theme} missing from --help"


# --- screenshot registry integrity ------------------------------------------
#
# The registry maps (filename, 0-based slide index) pairs into sample decks.
# Nothing stops a sample deck from gaining or losing a slide, which would
# silently shift every index after it and produce mislabelled PNGs. These
# tests read the real sample decks, so they fail the moment the registry drifts.


def test_every_screenshot_index_is_within_its_deck() -> None:
    for theme, config in shots.THEME_CONFIG.items():
        slide_count = shots.count_markdown_slides(Path(config["slide"]))
        for filename, index in config["screenshots"]:
            assert 0 <= index < slide_count, (
                f"{theme}/{filename}: index {index} out of range "
                f"(deck has {slide_count} slides) — the sample deck changed; "
                f"update THEME_CONFIG"
            )


def test_every_configured_theme_has_a_sample_deck_on_disk() -> None:
    for theme, config in shots.THEME_CONFIG.items():
        assert Path(config["slide"]).is_file(), f"{theme}: missing sample deck"


def test_report_theme_registry_finds_no_problems(capsys) -> None:
    problems = shots.report_theme_registry()

    out = capsys.readouterr().out
    assert problems == [], out
    assert "All screenshot indices are in range" in out


def test_report_theme_registry_flags_an_out_of_range_index(monkeypatch, capsys) -> None:
    config = {
        "broken": {
            "slide": shots.THEME_CONFIG["azure-clarity"]["slide"],
            "screenshots": [("broken.png", 9999)],
        }
    }
    monkeypatch.setattr(shots, "THEME_CONFIG", config)

    problems = shots.report_theme_registry()

    out = capsys.readouterr().out
    assert len(problems) == 1
    assert "broken.png" in problems[0]
    assert "Problems:" in out


def test_report_theme_registry_flags_a_missing_deck(monkeypatch, capsys) -> None:
    config = {"gone": {"slide": shots.WORKSPACE / "nope.md", "screenshots": []}}
    monkeypatch.setattr(shots, "THEME_CONFIG", config)

    problems = shots.report_theme_registry()

    assert len(problems) == 1
    assert "sample deck not found" in problems[0]
    assert "sample deck not found" in capsys.readouterr().out


def test_main_list_themes_mode_exits_zero(monkeypatch, capsys) -> None:
    """--list-themes must work without Marp CLI or a browser."""
    assert _runpy_main(monkeypatch, "--list-themes") == 0

    out = capsys.readouterr().out
    assert "screenshots across" in out
    assert "All screenshot indices are in range" in out


def test_list_themes_reports_drift_as_a_failure(monkeypatch, capsys) -> None:
    """A drifted registry must be reported as a failure so it can gate CI.

    Called directly rather than through runpy: run_path re-executes the module
    in a fresh namespace, so monkeypatching the already-imported copy's
    THEME_CONFIG would not be visible to it.
    """
    config = {
        "broken": {
            "slide": shots.THEME_CONFIG["azure-clarity"]["slide"],
            "screenshots": [("broken.png", 9999)],
        }
    }
    monkeypatch.setattr(shots, "THEME_CONFIG", config)

    assert shots.report_theme_registry() != []
    assert "Problems:" in capsys.readouterr().out


def test_count_markdown_slides_matches_the_real_sample_deck() -> None:
    # 30 slides at the time of writing: 31 `---` separators (2 frontmatter + 29 slide breaks).
    # Assert a lower bound so appending a slide does not break the contract;
    # index drift itself is guarded by test_every_screenshot_index_is_within_its_deck.
    deck = shots.THEME_CONFIG["azure-clarity"]["slide"]
    assert shots.count_markdown_slides(Path(deck)) >= 30
