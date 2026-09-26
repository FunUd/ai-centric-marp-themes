"""Tests for check-templates.py — the template validation gate.

The gate's most important property is not "templates render" (that needs npx and
is covered by running the script) but "**no template can escape validation**".
A template that is on disk but missing from ALLOWED_LAYOUTS would be silently
skipped, which is exactly the defect that let 3 broken Mermaid templates ship
under a CI step that only echoed their filenames.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

VALID_LAYOUTS = {"full", "col2", "asym", "col3"}


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker = load_module("check_templates", "check-templates.py")


def test_manifest_covers_every_template_on_disk() -> None:
    assert checker.undeclared(checker.templates_on_disk()) == []


def test_manifest_has_no_entries_for_missing_files() -> None:
    assert checker.stale_entries(checker.templates_on_disk()) == []


def test_manifest_matches_the_documented_template_count() -> None:
    # 5 mermaid + 2 drawio + 5 charts + 4 concepts + 1 organization
    assert len(checker.templates_on_disk()) == 17
    assert len(checker.ALLOWED_LAYOUTS) == 17


@pytest.mark.parametrize("rel,layouts", sorted(checker.ALLOWED_LAYOUTS.items()))
def test_every_declared_layout_is_canonical(rel: str, layouts: tuple[str, ...]) -> None:
    assert layouts, f"{rel}: at least one layout must be declared"
    assert set(layouts) <= VALID_LAYOUTS, f"{rel}: unknown layout in {layouts}"
    assert len(set(layouts)) == len(layouts), f"{rel}: duplicate layout in {layouts}"


@pytest.mark.parametrize("rel,layouts", sorted(checker.ALLOWED_LAYOUTS.items()))
def test_declared_templates_exist_with_the_right_extension(rel: str, layouts: tuple[str, ...]) -> None:
    path = checker.TEMPLATES_DIR / rel
    assert path.is_file(), f"{rel}: declared in the manifest but missing on disk"
    engine = rel.split("/", 1)[0]
    assert checker._engine_of(rel) == engine
    expected_suffix = {"mermaid": ".mmd", "drawio": ".drawio"}.get(engine, ".json")
    assert path.suffix == expected_suffix, f"{rel}: expected {expected_suffix}"


def test_every_template_declares_the_full_layout() -> None:
    """`full` is the layout the README documents for all templates; a template
    that cannot render at `full` is unusable as shipped."""
    missing = [rel for rel, layouts in checker.ALLOWED_LAYOUTS.items() if checker.FULL not in layouts]
    assert missing == []


def test_undeclared_detects_a_new_template(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(checker, "TEMPLATES_DIR", tmp_path)
    (tmp_path / "charts").mkdir()
    (tmp_path / "charts" / "brand-new.json").write_text("{}", encoding="utf-8")
    assert checker.undeclared(checker.templates_on_disk()) == ["charts/brand-new.json"]


def test_stale_entries_detects_a_removed_template(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(checker, "TEMPLATES_DIR", tmp_path)
    (tmp_path / "charts").mkdir()
    assert "charts/revenue-pie.json" in checker.stale_entries(checker.templates_on_disk())


def test_main_fails_when_a_template_is_undeclared(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(checker, "TEMPLATES_DIR", tmp_path)
    monkeypatch.setattr(sys, "argv", ["check-templates.py"])
    (tmp_path / "charts").mkdir()
    (tmp_path / "charts" / "undeclared.json").write_text("{}", encoding="utf-8")

    rc = checker.main()

    captured = capsys.readouterr()
    assert rc == 1
    assert "[UNDECLARED]" in captured.err
    assert "charts/undeclared.json" in captured.err


def test_main_validates_a_single_engine_against_the_real_manifest(monkeypatch, capsys) -> None:
    """End-to-end on the real repo, restricted to the stdlib-only org chart so
    the test needs neither npx nor a network."""
    monkeypatch.setattr(sys, "argv", ["check-templates.py", "--engine", "organization"])

    rc = checker.main()

    out = capsys.readouterr().out
    assert rc == 0, out
    assert "[OK] organization/team-org-chart.json @ full" in out
    assert "mermaid" not in out


def test_relevant_lines_keeps_only_errors_and_warnings() -> None:
    output = "\n".join(
        [
            "Rendering Mermaid diagram...",
            "[OK] something",
            "[WARN] aspect ratio 0.63 < 1.2",
            "[ERROR] Height (587.0px) exceeds max allowed height (470.0px)",
            "[SUCCESS] ready",
        ]
    )
    lines = checker._relevant_lines(output)
    assert len(lines) == 2
    assert lines[0].startswith("[WARN]")
    assert lines[1].startswith("[ERROR]")


def test_relevant_lines_is_capped() -> None:
    output = "\n".join(f"[ERROR] problem {i}" for i in range(50))
    assert len(checker._relevant_lines(output)) == 6


def test_engine_filter_selects_only_that_engine() -> None:
    targets = sorted(checker.templates_on_disk())
    json_only = [t for t in targets if checker._engine_of(t) == "organization"]
    assert json_only == ["organization/team-org-chart.json"]
