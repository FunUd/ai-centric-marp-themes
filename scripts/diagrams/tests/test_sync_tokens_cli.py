"""Tests for sync-tokens-from-css.py — apply_updates() and main().

test_token_sync.py covers parse_root_vars / build_updates / resolve_value.
This file adds the write path (apply_updates) and the CLI entry point
(main), using temp copies of the real CSS/JSON inputs.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

REAL_STYLES_DIR = SCRIPT_DIR / "theme-styles"
REAL_THEMES_DIR = SCRIPT_DIR.parent.parent / "themes"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sync = load_module("sync_tokens_cli", "sync-tokens-from-css.py")


def _real_updates(theme: str) -> dict:
    css_text = (REAL_THEMES_DIR / sync.THEME_FILES[theme]).read_text(encoding="utf-8")
    vars_ = sync.parse_root_vars(css_text)
    existing = json.loads((REAL_STYLES_DIR / f"{theme}.json").read_text(encoding="utf-8"))
    return sync.build_updates(theme, vars_, css_text, existing)


def test_build_updates_keeps_existing_color_when_css_var_missing() -> None:
    """keep() falls back to the curated JSON color when the CSS variable is gone."""
    import re

    css_path = REAL_THEMES_DIR / sync.THEME_FILES["azure-clarity"]
    css = re.sub(r"--ac-primary-dark:\s*[^;]+;\s*", "", css_path.read_text(encoding="utf-8"), count=1)
    vars_ = sync.parse_root_vars(css)
    assert "--ac-primary-dark" not in vars_

    existing = json.loads((REAL_STYLES_DIR / "azure-clarity.json").read_text(encoding="utf-8"))
    updates = sync.build_updates("azure-clarity", vars_, css, existing)

    assert updates["colors"]["primaryDark"] == existing["colors"]["primaryDark"]


def _style_dir(tmp_path: Path, *themes: str) -> Path:
    styles = tmp_path / "theme-styles"
    styles.mkdir()
    for theme in themes or sorted(sync.THEME_FILES):
        shutil.copy(REAL_STYLES_DIR / f"{theme}.json", styles / f"{theme}.json")
    return styles


def _run_main(monkeypatch, *args: str) -> int:
    monkeypatch.setattr(sys, "argv", ["sync-tokens-from-css.py", *args])
    return sync.main()


def test_script_entry_point_check_mode_is_read_only(monkeypatch) -> None:
    """`raise SystemExit(main())` under __main__: --check never writes and the
    real repo is in sync, so the entry point exits 0."""
    import runpy

    monkeypatch.setattr(sys, "argv", ["sync-tokens-from-css.py", "--check"])
    target = REAL_STYLES_DIR / "azure-clarity.json"
    before = target.read_bytes()

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(sync.__file__, run_name="__main__")

    assert exc.value.code == 0
    assert target.read_bytes() == before


# --- apply_updates -----------------------------------------------------------


def test_apply_updates_in_sync_writes_nothing(monkeypatch, tmp_path: Path) -> None:
    styles = _style_dir(tmp_path, "azure-clarity")
    monkeypatch.setattr(sync, "STYLES_DIR", styles)
    target = styles / "azure-clarity.json"
    before = target.read_bytes()

    changed, changes = sync.apply_updates("azure-clarity", _real_updates("azure-clarity"))

    assert changed is False
    assert changes == []
    assert target.read_bytes() == before


def test_apply_updates_reports_and_persists_color_drift(monkeypatch, tmp_path: Path) -> None:
    styles = _style_dir(tmp_path, "azure-clarity")
    monkeypatch.setattr(sync, "STYLES_DIR", styles)
    updates = copy.deepcopy(_real_updates("azure-clarity"))
    original = updates["colors"]["primary"]
    updates["colors"]["primary"] = "#123456"

    changed, changes = sync.apply_updates("azure-clarity", updates)

    assert changed is True
    assert any(line.startswith(f"colors.primary: {original} -> #123456") for line in changes)
    written = json.loads((styles / "azure-clarity.json").read_text(encoding="utf-8"))
    assert written["colors"]["primary"] == "#123456"
    # drawio styles are recomputed from the new palette.
    assert "#123456" in written["drawio"]["accentNodeStyle"]


def test_apply_updates_reports_and_persists_shape_drift(monkeypatch, tmp_path: Path) -> None:
    styles = _style_dir(tmp_path, "azure-clarity")
    monkeypatch.setattr(sync, "STYLES_DIR", styles)
    target = styles / "azure-clarity.json"
    data = json.loads(target.read_text(encoding="utf-8"))
    data["shapes"]["nodeRadius"] = 99
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    updates = _real_updates("azure-clarity")
    changed, changes = sync.apply_updates("azure-clarity", updates)

    assert changed is True
    assert any(line.startswith("shapes.nodeRadius: 99 -> ") for line in changes)
    written = json.loads(target.read_text(encoding="utf-8"))
    assert written["shapes"]["nodeRadius"] == updates["shapes"]["nodeRadius"]


def test_apply_updates_refreshes_signature(monkeypatch, tmp_path: Path) -> None:
    styles = _style_dir(tmp_path, "azure-clarity")
    monkeypatch.setattr(sync, "STYLES_DIR", styles)
    updates = copy.deepcopy(_real_updates("azure-clarity"))
    updates["signature"] = {**updates["signature"], "staleMarker": True}

    changed, changes = sync.apply_updates("azure-clarity", updates)

    assert changed is True
    assert "signature refreshed" in changes
    written = json.loads((styles / "azure-clarity.json").read_text(encoding="utf-8"))
    assert written["signature"]["staleMarker"] is True


def test_apply_updates_syncs_shadow_color(monkeypatch, tmp_path: Path) -> None:
    styles = _style_dir(tmp_path, "azure-clarity")
    monkeypatch.setattr(sync, "STYLES_DIR", styles)
    updates = copy.deepcopy(_real_updates("azure-clarity"))
    updates["effects"]["nodeShadowColor"] = "#010203"

    changed, changes = sync.apply_updates("azure-clarity", updates)

    assert changed is True
    assert "effects.nodeShadowColor -> #010203" in changes
    written = json.loads((styles / "azure-clarity.json").read_text(encoding="utf-8"))
    assert written["effects"]["nodeShadowColor"] == "#010203"


def test_build_updates_nebula_keeps_curated_palette() -> None:
    css_text = (REAL_THEMES_DIR / sync.THEME_FILES["nebula-glass"]).read_text(encoding="utf-8")
    vars_ = sync.parse_root_vars(css_text)
    existing = json.loads((REAL_STYLES_DIR / "nebula-glass.json").read_text(encoding="utf-8"))
    # Nebula's :root lacks derived palette entries (NEBULA_KEEP).
    vars_.pop("--ng-primary-dark", None)

    updates = sync.build_updates("nebula-glass", vars_, css_text, existing)

    assert updates["colors"]["primaryDark"] == existing["colors"]["primaryDark"]


def test_parse_root_vars_without_root_block_returns_empty() -> None:
    assert sync.parse_root_vars("body { color: red; }") == {}


def test_px_to_float_rejects_non_px_values() -> None:
    assert sync.px_to_float("1.5em") is None
    assert sync.px_to_float("wide") is None


# --- main --------------------------------------------------------------------


def test_main_check_passes_for_clean_repo(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(sync, "STYLES_DIR", _style_dir(tmp_path))
    monkeypatch.setattr(sync, "THEMES_DIR", tmp_path / "themes")  # unused in --check? no: css read
    # copy real css files so main() can parse them
    themes = tmp_path / "themes"
    themes.mkdir()
    for css in REAL_THEMES_DIR.glob("*.css"):
        shutil.copy(css, themes / css.name)

    rc = _run_main(monkeypatch, "--check")

    out = capsys.readouterr().out
    assert rc == 0
    assert "[DRIFT]" not in out


def test_main_check_fails_on_signature_drift(monkeypatch, tmp_path: Path, capsys) -> None:
    styles = _style_dir(tmp_path)
    monkeypatch.setattr(sync, "STYLES_DIR", styles)
    themes = tmp_path / "themes"
    themes.mkdir()
    for css in REAL_THEMES_DIR.glob("*.css"):
        shutil.copy(css, themes / css.name)
    monkeypatch.setattr(sync, "THEMES_DIR", themes)

    target = styles / "azure-clarity.json"
    data = json.loads(target.read_text(encoding="utf-8"))
    data["signature"] = {"source": "themes/azure-clarity.css", "stale": True}
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rc = _run_main(monkeypatch, "--check")

    captured = capsys.readouterr()
    assert rc == 1
    assert "[DRIFT] azure-clarity" in captured.out
    assert "FAILED: 1 theme(s) drifted" in captured.err


def test_main_sync_prints_ok_when_already_in_sync(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(sync, "STYLES_DIR", _style_dir(tmp_path))
    themes = tmp_path / "themes"
    themes.mkdir()
    for css in REAL_THEMES_DIR.glob("*.css"):
        shutil.copy(css, themes / css.name)
    monkeypatch.setattr(sync, "THEMES_DIR", themes)

    rc = _run_main(monkeypatch)

    out = capsys.readouterr().out
    assert rc == 0
    assert out.count("[OK]") == len(sync.THEME_FILES)
    assert "[SYNC]" not in out


def test_main_sync_repairs_drifted_color(monkeypatch, tmp_path: Path, capsys) -> None:
    styles = _style_dir(tmp_path, "azure-clarity")
    monkeypatch.setattr(sync, "STYLES_DIR", styles)
    themes = tmp_path / "themes"
    themes.mkdir()
    shutil.copy(REAL_THEMES_DIR / "azure-clarity.css", themes / "azure-clarity.css")
    monkeypatch.setattr(sync, "THEMES_DIR", themes)

    target = styles / "azure-clarity.json"
    data = json.loads(target.read_text(encoding="utf-8"))
    data["colors"]["primary"] = "#000000"
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rc = _run_main(monkeypatch, "--theme", "azure-clarity")

    out = capsys.readouterr().out
    assert rc == 0
    assert "[SYNC] azure-clarity:" in out
    repaired = json.loads(target.read_text(encoding="utf-8"))
    assert repaired["colors"]["primary"] != "#000000"


def test_main_theme_flag_limits_scope(monkeypatch, tmp_path: Path, capsys) -> None:
    styles = _style_dir(tmp_path)
    monkeypatch.setattr(sync, "STYLES_DIR", styles)
    themes = tmp_path / "themes"
    themes.mkdir()
    for css in REAL_THEMES_DIR.glob("*.css"):
        shutil.copy(css, themes / css.name)
    monkeypatch.setattr(sync, "THEMES_DIR", themes)

    # Drift a theme that is NOT selected; it must stay untouched.
    untouched = styles / "slate-minimal.json"
    before = untouched.read_bytes()
    target = styles / "azure-clarity.json"
    data = json.loads(target.read_text(encoding="utf-8"))
    data["colors"]["primary"] = "#000000"
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rc = _run_main(monkeypatch, "--theme", "azure-clarity")

    out = capsys.readouterr().out
    assert rc == 0
    assert "[SYNC] azure-clarity:" in out
    assert "[OK] slate-minimal" not in out
    assert untouched.read_bytes() == before
