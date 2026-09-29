"""Tests for check-catalog-sync.py — template registry sync checker.

The script compares three sources (templates on disk, template-catalog.md,
docs/diagrams.md table) and fails on any mismatch. Covered here:

- templates_on_disk / mentions_in unit behavior
- main() against the real repository (the CI gate)
- every mismatch branch (CATALOG / DOCS / STALE) against fixtures
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


catalog = load_module("check_catalog_sync", "check-catalog-sync.py")


def test_script_entry_point_runs_main(monkeypatch) -> None:
    """`raise SystemExit(main())` under __main__ exits 0 while the repo is in sync."""
    import runpy

    monkeypatch.setattr(sys, "argv", ["check-catalog-sync.py"])

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(catalog.__file__, run_name="__main__")

    assert exc.value.code == 0


def test_templates_on_disk_returns_expected_names() -> None:
    found = catalog.templates_on_disk()

    assert "flowchart-linear.mmd" in found
    assert "system-architecture.drawio" in found
    assert "revenue-pie.json" in found
    # Only the whitelisted template folders are scanned.
    assert not any(name.startswith(".") for name in found)


def test_templates_on_disk_reads_disk(monkeypatch, tmp_path: Path) -> None:
    templates = tmp_path / "templates"
    (templates / "mermaid").mkdir(parents=True)
    (templates / "charts").mkdir()
    (templates / "mermaid" / "only-here.mmd").write_text("graph LR", encoding="utf-8")
    (templates / "charts" / "only-pie.json").write_text("{}", encoding="utf-8")
    # Non-template folders/extensions are ignored.
    (templates / "mermaid" / "notes.txt").write_text("x", encoding="utf-8")

    monkeypatch.setattr(catalog, "SCRIPT_DIR", tmp_path)

    assert catalog.templates_on_disk() == {"only-here.mmd", "only-pie.json"}


def test_mentions_in_extracts_template_filenames(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "See charts/revenue-pie.json and alpha.mmd plus beta.drawio.\nIgnored: diagrams.md, image.png, script.js\n",
        encoding="utf-8",
    )

    assert catalog.mentions_in(doc) == {"revenue-pie.json", "alpha.mmd", "beta.drawio"}


def test_mentions_in_scopes_docs_to_the_templates_table(tmp_path: Path) -> None:
    """Regression: docs/diagrams.md documents other JSON files (`theme-classes.json`,
    `theme-styles/*.json`). Scanning the whole document reported them as stale
    templates and failed the gate."""
    readme = tmp_path / "diagrams.md"
    readme.write_text(
        "## Project Structure\n"
        "`scripts/theme-classes.json` and `assets/theme-styles/azure.json` are not templates.\n"
        "\n"
        "### Available Templates\n"
        "\n"
        "| Template | Engine |\n"
        "|---|---|\n"
        "| `flowchart-linear.mmd` | Mermaid |\n"
        "\n"
        "## Next Section\n"
        "Mentioning `other.drawio` here must not count.\n",
        encoding="utf-8",
    )

    assert catalog.mentions_in(readme) == {"flowchart-linear.mmd"}


def test_mentions_in_returns_empty_when_docs_has_no_templates_table(tmp_path: Path) -> None:
    readme = tmp_path / "diagrams.md"
    readme.write_text("No table here, just a stray `thing.mmd` mention.\n", encoding="utf-8")

    assert catalog.mentions_in(readme) == set()


def test_mentions_in_reads_table_up_to_the_next_heading(tmp_path: Path) -> None:
    """The table must not bleed into whatever follows it."""
    readme = tmp_path / "diagrams.md"
    readme.write_text(
        "### Available Templates\n\n| a.mmd |\n\n### Lint Integration\n\n`b.mmd` is prose.\n",
        encoding="utf-8",
    )

    assert catalog.mentions_in(readme) == {"a.mmd"}


def test_main_passes_against_real_repository(capsys) -> None:
    """The repo itself must stay in sync (this is the CI gate)."""
    assert catalog.main() == 0
    out = capsys.readouterr().out
    assert "[OK]" in out and "in sync" in out


def _fake_sources(tmp_path: Path, catalog_text: str, docs_text: str) -> Path:
    """Build a fake scripts/diagrams tree holding one on-disk template."""
    script_dir = tmp_path / "scripts" / "diagrams"
    (script_dir / "templates" / "mermaid").mkdir(parents=True)
    (script_dir / "templates" / "mermaid" / "on-disk.mmd").write_text("graph LR", encoding="utf-8")
    # The layout authority the catalog check loads; scoped to the fixture.
    (script_dir / "check-templates.py").write_text(
        'ALLOWED_LAYOUTS = {"mermaid/on-disk.mmd": ("full",)}\n', encoding="utf-8"
    )
    catalog_path = tmp_path / "template-catalog.md"
    catalog_path.write_text(catalog_text, encoding="utf-8")
    docs_path = tmp_path / "diagrams.md"
    # Wrap docs content in the Available Templates table the script scans,
    # so fixtures describe templates rather than prose.
    docs_path.write_text(
        f"{catalog.DOCS_TABLE_HEADING}\n\n{docs_text}\n",
        encoding="utf-8",
    )
    return script_dir, catalog_path, docs_path


def test_main_reports_mismatches(monkeypatch, tmp_path: Path, capsys) -> None:
    script_dir, catalog_path, docs_path = _fake_sources(
        tmp_path,
        catalog_text="stale-entry.mmd is documented\n",
        docs_text="stale-entry.mmd is documented\n",
    )
    monkeypatch.setattr(catalog, "SCRIPT_DIR", script_dir)
    monkeypatch.setattr(catalog, "CATALOG_PATH", catalog_path)
    monkeypatch.setattr(catalog, "DIAGRAMS_DOC_PATH", docs_path)

    rc = catalog.main()

    captured = capsys.readouterr()
    assert rc == 1
    assert "[CATALOG] template on disk but missing in template-catalog.md: on-disk.mmd" in captured.out
    assert "[DOCS] template on disk but missing in docs/diagrams.md Available Templates: on-disk.mmd" in captured.out
    assert "[STALE] documented but file does not exist: stale-entry.mmd" in captured.out
    # The layout columns are verified too: the fixture docs table has no
    # support-matrix header, which the defensive branch reports.
    assert "[LAYOUT] cannot read layout sources" in captured.out
    assert "FAILED: 4 mismatch(es)" in captured.err


def test_main_reports_only_docs_gap(monkeypatch, tmp_path: Path, capsys) -> None:
    script_dir, catalog_path, docs_path = _fake_sources(
        tmp_path,
        catalog_text="on-disk.mmd\n",
        docs_text="no templates listed here\n",
    )
    monkeypatch.setattr(catalog, "SCRIPT_DIR", script_dir)
    monkeypatch.setattr(catalog, "CATALOG_PATH", catalog_path)
    monkeypatch.setattr(catalog, "DIAGRAMS_DOC_PATH", docs_path)

    rc = catalog.main()

    captured = capsys.readouterr()
    assert rc == 1
    assert "[DOCS]" in captured.out
    assert "[CATALOG]" not in captured.out
    assert "[STALE]" not in captured.out


def test_main_passes_when_all_sources_agree(monkeypatch, tmp_path: Path, capsys) -> None:
    script_dir, catalog_path, docs_path = _fake_sources(
        tmp_path,
        catalog_text=(
            "## 1. Mermaid Templates\n\n"
            "| Filename | Type | Verified Layouts | Embed |\n"
            "|---|---|---|---|\n"
            "| `on-disk.mmd` | Mermaid | Full | 1050px |\n"
        ),
        docs_text=(
            "| `on-disk.mmd` | Mermaid |\n"
            "| Template | `full` | `col2` | `asym` | `col3` |\n"
            "|---|:--:|:--:|:--:|:--:|\n"
            "| `on-disk.mmd` | ✅ | | | |\n"
        ),
    )
    monkeypatch.setattr(catalog, "SCRIPT_DIR", script_dir)
    monkeypatch.setattr(catalog, "CATALOG_PATH", catalog_path)
    monkeypatch.setattr(catalog, "DIAGRAMS_DOC_PATH", docs_path)

    rc = catalog.main()

    captured = capsys.readouterr()
    assert rc == 0
    assert "[OK] 1 templates in sync" in captured.out
