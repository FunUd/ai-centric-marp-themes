"""Tests for regenerate-golden.py — golden fixture regeneration driver.

The script shells out to render-slide-diagram.py for 6 themes x 3 engines.
subprocess.run is mocked so no npx/Mermaid CLI is required.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


regen = load_module("regenerate_golden", "regenerate-golden.py")


def _install_runner(monkeypatch, out_dir: Path, returncode: int = 0, stderr: str = ""):
    """Replace subprocess.run with a fake that writes each requested output."""
    commands: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        commands.append(list(cmd))
        dest = Path(cmd[cmd.index("-o") + 1])
        if returncode == 0:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f"<svg><!-- {dest.name} --></svg>", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, returncode, "", stderr)

    monkeypatch.setattr(regen, "ROOT", out_dir.parent)
    monkeypatch.setattr(regen, "OUT", out_dir)
    monkeypatch.setattr(regen.subprocess, "run", fake_run)
    return commands


def test_main_renders_all_theme_kind_combinations(monkeypatch, tmp_path: Path, capsys) -> None:
    out_dir = tmp_path / "golden"
    commands = _install_runner(monkeypatch, out_dir)

    rc = regen.main()

    assert rc == 0
    assert len(commands) == len(regen.THEMES) * len(regen.SOURCES) == 18
    # Every command targets the renderer with an explicit theme + layout.
    assert commands[0][1].endswith("render-slide-diagram.py")
    assert "--theme" in commands[0] and "--layout" in commands[0]
    # All 18 SVGs exist on disk.
    for theme in regen.THEMES:
        for kind in regen.SOURCES:
            assert (out_dir / f"{theme}-{kind}.svg").exists()
    out = capsys.readouterr().out
    assert out.count("[OK]") == 18
    assert "[FAIL]" not in out


def test_main_returns_nonzero_and_reports_failures(monkeypatch, tmp_path: Path, capsys) -> None:
    out_dir = tmp_path / "golden"
    commands = _install_runner(monkeypatch, out_dir, returncode=1, stderr="mermaid exploded")

    rc = regen.main()

    captured = capsys.readouterr()
    assert rc == 1
    assert len(commands) == 18  # failures do not abort the loop early
    assert captured.out.count("[FAIL]") == 18
    assert "mermaid exploded" in captured.out
    # Failed renders leave no output behind.
    assert not any(out_dir.glob("*.svg")) if out_dir.exists() else True


def test_source_templates_referenced_by_the_driver_exist() -> None:
    """The golden driver must point at real template files."""
    for kind, src in regen.SOURCES.items():
        assert src.exists(), f"{kind}: missing {src}"
