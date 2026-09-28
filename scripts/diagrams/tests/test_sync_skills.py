"""Tests for scripts/sync-skills.py — skill directory synchronization.

sync_skills() mutates the real target roots when run as a script; here
SOURCE_DIR / TARGET_ROOTS are redirected into tmp_path so the copy, stale
cleanup, skip, and guard branches are exercised safely.
"""
from __future__ import annotations

import importlib.util
import sys
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


sync_skills_mod = load_module("sync_skills_under_test", SCRIPTS_DIR / "sync-skills.py")


def _make_skill(root: Path, name: str, body: str = "# skill") -> Path:
    skill = root / name
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(body, encoding="utf-8")
    return skill


def test_is_within_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()

    assert sync_skills_mod._is_within_root(root / "a" / "b", root) is True
    assert sync_skills_mod._is_within_root(root, root) is True
    assert sync_skills_mod._is_within_root(tmp_path / "outside", root) is False


def test_sync_refuses_to_write_outside_target_root(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "skills"
    _make_skill(source, "alpha")
    target = tmp_path / "target"
    target.mkdir()
    monkeypatch.setattr(sync_skills_mod, "SOURCE_DIR", source)
    monkeypatch.setattr(sync_skills_mod, "TARGET_ROOTS", [target])
    # _is_within_root's own behavior is covered above; force a refusal here so
    # the guard inside sync_skills() itself is exercised.
    monkeypatch.setattr(sync_skills_mod, "_is_within_root", lambda path, root: False)

    with pytest.raises(RuntimeError, match="Refusing to write outside target root"):
        sync_skills_mod.sync_skills()


def test_script_entry_point_runs_full_sync_without_writing(monkeypatch, capsys) -> None:
    """`if __name__ == "__main__": sync_skills()` executes the whole flow with
    copytree/rmtree stubbed, so the real agent directories stay untouched."""
    import runpy
    import shutil as shutil_mod
    import sys as sys_mod

    copied: list[tuple[Path, Path]] = []
    removed: list[Path] = []
    monkeypatch.setattr(shutil_mod, "copytree", lambda src, dst, **kwargs: copied.append((src, dst)))
    monkeypatch.setattr(shutil_mod, "rmtree", lambda path, **kwargs: removed.append(path))
    monkeypatch.setattr(sys_mod, "argv", ["sync-skills.py"])

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(sync_skills_mod.__file__), run_name="__main__")
    assert exc.value.code == 0

    roots = [t for t in sync_skills_mod.TARGET_ROOTS if t.exists()]
    skills = [d for d in sync_skills_mod.SOURCE_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    assert roots and skills
    out = capsys.readouterr().out
    # Idempotent sync may SKIP byte-identical skills instead of copying.
    processed = len(copied) + out.count("[SKIP]")
    assert processed >= len(roots) * len(skills)
    assert "Done." in out


def test_sync_reports_missing_source(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(sync_skills_mod, "SOURCE_DIR", tmp_path / "no-such-dir")

    assert sync_skills_mod.sync_skills() == 1

    captured = capsys.readouterr()
    assert "[ERROR] Source directory" in (captured.out + captured.err)


def test_sync_reports_when_no_skill_directories(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "skills"
    source.mkdir()
    (source / "notes").mkdir()  # directory without SKILL.md is ignored
    monkeypatch.setattr(sync_skills_mod, "SOURCE_DIR", source)
    monkeypatch.setattr(sync_skills_mod, "TARGET_ROOTS", [])

    sync_skills_mod.sync_skills()

    captured = capsys.readouterr()
    assert "[INFO] No skill directories found" in (captured.out + captured.err)


def test_sync_copies_skills_and_cleans_stale_dirs(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "skills"
    _make_skill(source, "alpha", "# alpha v2")
    _make_skill(source, "beta")

    target = tmp_path / "targets" / "agent"
    target.mkdir(parents=True)
    _make_skill(target, "alpha", "# alpha v1")                # refreshed copy
    (target / "theme-expert-old").mkdir()                     # prefixed stale -> deleted
    (target / "marp-legacy").mkdir()                          # prefixed stale -> deleted
    (target / "theme-creator-old").mkdir()                    # renamed theme-creator -> deleted
    (target / "slide-content-designer-old").mkdir()           # renamed designer -> deleted
    (target / "unrelated").mkdir()                            # not prefixed -> kept
    missing_target = tmp_path / "targets" / "missing"         # -> skip branch

    monkeypatch.setattr(sync_skills_mod, "SOURCE_DIR", source)
    monkeypatch.setattr(sync_skills_mod, "TARGET_ROOTS", [target, missing_target])

    sync_skills_mod.sync_skills()

    out = capsys.readouterr().out
    assert "Found 2 skill(s)" in out
    assert f"[SKIP] '{missing_target}' does not exist" in out
    # Fresh copy contents.
    assert (target / "alpha" / "SKILL.md").read_text(encoding="utf-8") == "# alpha v2"
    assert (target / "beta" / "SKILL.md").exists()
    # Stale prefixed directories removed; unrelated directory untouched.
    assert not (target / "theme-expert-old").exists()
    assert not (target / "marp-legacy").exists()
    assert not (target / "theme-creator-old").exists()
    assert not (target / "slide-content-designer-old").exists()
    assert (target / "unrelated").exists()
    assert "[DEL STALE]" in out and "[COPY]" in out


def test_sync_replaces_existing_skill_directory(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "skills"
    skill = _make_skill(source, "gamma", "# gamma fresh")
    (skill / "extra.md").write_text("new file", encoding="utf-8")

    target = tmp_path / "target"
    stale = target / "gamma"
    stale.mkdir(parents=True)
    (stale / "obsolete.md").write_text("old", encoding="utf-8")

    monkeypatch.setattr(sync_skills_mod, "SOURCE_DIR", source)
    monkeypatch.setattr(sync_skills_mod, "TARGET_ROOTS", [target])

    sync_skills_mod.sync_skills()

    out = capsys.readouterr().out
    assert "[DEL]" in out
    assert not (target / "gamma" / "obsolete.md").exists()
    assert (target / "gamma" / "extra.md").read_text(encoding="utf-8") == "new file"
    assert out.strip().endswith("Done.")
