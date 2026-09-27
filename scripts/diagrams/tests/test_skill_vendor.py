"""Tests for the vendored diagram engine in `marp-diagram-creator`.

The defect this exists to prevent: `marp-diagram-creator` shipped 3 files of
prose pointing at `scripts/diagrams/`, which is *outside* the skill. Inside the
repository every command happened to work; copied to `~/.claude/skills/`, every
documented path resolved to nothing and the skill was unusable.

Covered here:

- the vendored copy is byte-identical to `scripts/diagrams/` (the sync gate);
- only the runtime closure is vendored — no repository-only scripts;
- **the vendored engine actually runs with no repository present**;
- vendored render output matches the source engine byte for byte;
- no skill points at a path that only exists in a checkout.
"""
from __future__ import annotations

import filecmp
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
ENGINE_DIR = ROOT / "scripts/diagrams"
SKILL_DIR = ROOT / "skills/marp-diagram-creator"
VENDOR_DIR = SKILL_DIR / "vendor"
SYNC = ROOT / "scripts/sync-skill-vendor.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sync = load_module("sync_skill_vendor", SYNC)


# --- the sync gate ----------------------------------------------------------


def test_vendor_directory_exists() -> None:
    assert VENDOR_DIR.is_dir(), "run: python scripts/sync-skill-vendor.py"


def test_sync_script_check_mode_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(SYNC), "--check"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_vendored_files_are_byte_identical_to_the_source() -> None:
    """The whole point of generating instead of moving: `scripts/diagrams/`
    stays the development source, and drift is a CI failure."""
    expected = sync.expected_files()
    assert expected, "runtime set resolved to nothing"
    for relative in sorted(expected):
        source = sync._source_for(relative)
        vendored = VENDOR_DIR / relative
        assert source.is_file(), f"source missing for {relative}"
        assert vendored.is_file(), f"{relative} not vendored"
        assert filecmp.cmp(source, vendored, shallow=False), f"{relative} differs"


def test_tool_versions_is_vendored_so_installs_stay_pinned() -> None:
    """`tool_versions` is a runtime import of the renderer, not repository
    tooling. Leaving it out made a standalone install silently fall back to
    unpinned `npx -y`, which is the drift this file exists to prevent."""
    assert "tool_versions" in sync.runtime_modules()
    assert (VENDOR_DIR / "tool_versions.py").is_file()
    assert (VENDOR_DIR / "tool_versions.py").read_bytes() == (
        ROOT / "scripts/diagrams/tool_versions.py"
    ).read_bytes()


def test_isolated_skill_resolves_a_pinned_mermaid_version(isolated_skill: Path) -> None:
    """The whole point of vendoring the pin: a copied skill must not float."""
    result = subprocess.run(
        [
            sys.executable, "-c",
            "import sys, importlib.util as u;"
            f"sys.path.insert(0, {str(isolated_skill / 'vendor')!r});"
            f"s = u.spec_from_file_location('r', {str(isolated_skill / 'vendor/render-slide-diagram.py')!r});"
            "m = u.module_from_spec(s); s.loader.exec_module(m);"
            "print(m.npx_command('@mermaid-js/mermaid-cli')[2])",
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stderr
    spec = result.stdout.strip()
    assert spec.startswith("@mermaid-js/mermaid-cli@"), spec

    # Same pin the repository declares.
    expected = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert spec == f"@mermaid-js/mermaid-cli@{expected['devDependencies']['@mermaid-js/mermaid-cli']}"


def test_vendor_has_no_extra_files() -> None:
    actual = {
        p.relative_to(VENDOR_DIR).as_posix()
        for p in VENDOR_DIR.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    assert actual == sync.expected_files()


# --- what is (and is not) vendored ------------------------------------------


def test_both_entry_points_are_vendored() -> None:
    for name in sync.ENTRY_POINTS:
        assert (VENDOR_DIR / f"{name}.py").is_file(), f"{name}.py not vendored"


def test_every_runtime_module_is_vendored() -> None:
    for name in sync.runtime_modules():
        assert (VENDOR_DIR / f"{name}.py").is_file(), f"{name}.py missing from vendor"


@pytest.mark.parametrize("name", sorted(sync.DEV_ONLY))
def test_repository_only_scripts_are_not_vendored(name: str) -> None:
    """These read README.md, themes/*.css or the test suite. Shipping them in a
    standalone skill would advertise tools that cannot work there."""
    assert (ENGINE_DIR / f"{name}.py").is_file(), f"{name}.py moved out of scripts/diagrams"
    assert not (VENDOR_DIR / f"{name}.py").exists(), f"{name}.py must not be vendored"


def test_no_dev_module_leaked_into_the_runtime_closure() -> None:
    assert not (sync.runtime_modules() & sync.DEV_ONLY)


def test_data_directories_are_vendored() -> None:
    for data_dir in sync.DATA_DIRS:
        source = {p.relative_to(ENGINE_DIR).as_posix() for p in (ENGINE_DIR / data_dir).rglob("*") if p.is_file()}
        vendored = {p.relative_to(VENDOR_DIR).as_posix() for p in (VENDOR_DIR / data_dir).rglob("*") if p.is_file()}
        assert source == vendored, data_dir


def test_all_templates_are_vendored() -> None:
    """A template that is not vendored is a template a user of the installed
    skill cannot reach."""
    on_disk = {p.relative_to(ENGINE_DIR).as_posix() for p in (ENGINE_DIR / "templates").rglob("*") if p.is_file()}
    vendored = {p.relative_to(VENDOR_DIR).as_posix() for p in (VENDOR_DIR / "templates").rglob("*") if p.is_file()}
    assert on_disk == vendored
    # SSoT: count follows disk (was 17 before the col2/compact variants).


def test_all_theme_styles_are_vendored() -> None:
    """The renderer resolves themes from theme-styles/*.json, not themes/*.css,
    so this is why no CSS needs to ship with the skill."""
    on_disk = {p.name for p in (ENGINE_DIR / "theme-styles").glob("*.json")}
    vendored = {p.name for p in (VENDOR_DIR / "theme-styles").glob("*.json")}
    assert on_disk == vendored
    assert len(vendored) == 6


def test_vendor_needs_no_theme_css() -> None:
    """If the vendored engine ever started reading `themes/*.css`, the skill
    would break outside a checkout. Assert it does not."""
    for module in sorted(sync.runtime_modules()):
        source = (VENDOR_DIR / f"{module}.py").read_text(encoding="utf-8")
        assert "../themes" not in source, f"{module}.py reads themes/ outside the skill"
        assert "assets/fonts" not in source, f"{module}.py reads assets/fonts"


# --- the vendored engine runs standalone ------------------------------------


@pytest.fixture(scope="module")
def isolated_skill(tmp_path_factory) -> Path:
    """A skill copied out of the repository, with nothing else around it.

    This is the exact scenario that used to be broken: no `scripts/`, no
    `themes/`, no `assets/`, no sibling skills.
    """
    destination = tmp_path_factory.mktemp("standalone") / "marp-diagram-creator"
    shutil.copytree(
        SKILL_DIR,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    return destination


def test_isolated_skill_has_no_repository_paths(isolated_skill: Path) -> None:
    for relative in ("scripts", "themes", "assets", "slides"):
        assert not (isolated_skill.parent / relative).exists()


def _run_isolated(isolated_skill: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(isolated_skill / "vendor" / args[0]), *args[1:]],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd),
    )


@pytest.mark.parametrize("template,theme", [
    ("templates/charts/revenue-pie.json", "azure-clarity"),
    ("templates/concepts/team-pyramid.json", "prism-edge"),
    ("templates/organization/team-org-chart.json", "nebula-glass"),
    ("templates/drawio/system-architecture.drawio", "crimson-clarity"),
])
def test_isolated_engine_renders_json_and_drawio(isolated_skill: Path, tmp_path: Path, template: str, theme: str) -> None:
    """Pure-stdlib engines: no Node, no network, no repository."""
    out = tmp_path / "diagram.svg"
    result = _run_isolated(
        isolated_skill,
        "render-slide-diagram.py",
        "-i", str(isolated_skill / "vendor" / template),
        "-o", str(out),
        "--theme", theme,
        "--layout", "full",
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert out.is_file() and out.stat().st_size > 0
    assert "[SUCCESS]" in result.stdout


def test_isolated_engine_validates_a_rendered_svg(isolated_skill: Path, tmp_path: Path) -> None:
    svg = tmp_path / "pie.svg"
    assert _run_isolated(
        isolated_skill,
        "render-slide-diagram.py",
        "-i", str(isolated_skill / "vendor/templates/charts/revenue-pie.json"),
        "-o", str(svg),
        "--theme", "azure-clarity",
        "--layout", "full",
        cwd=tmp_path,
    ).returncode == 0

    result = _run_isolated(
        isolated_skill,
        "validate-slide-diagram.py",
        str(svg),
        "--layout", "full",
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASSED" in result.stdout


def test_isolated_engine_reports_validation_failure(isolated_skill: Path, tmp_path: Path) -> None:
    """The strict exit-code contract must survive vendoring."""
    svg = tmp_path / "huge.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" width="2000" height="2000">'
        '<rect x="10" y="10" width="1980" height="1980" fill="#fff"/></svg>',
        encoding="utf-8",
    )
    result = _run_isolated(
        isolated_skill,
        "validate-slide-diagram.py",
        str(svg),
        "--layout", "full",
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "FAILED" in result.stdout


def test_print_engine_path_resolves_outside_the_repository(isolated_skill: Path, tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(isolated_skill / "scripts/print-engine-path.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    resolved = Path(result.stdout.strip())
    assert resolved == (isolated_skill / "vendor").resolve()
    assert (resolved / "render-slide-diagram.py").is_file()


def test_print_engine_path_fails_clearly_when_vendor_is_missing(isolated_skill: Path, tmp_path: Path) -> None:
    shutil.rmtree(isolated_skill / "vendor")
    result = subprocess.run(
        [sys.executable, str(isolated_skill / "scripts/print-engine-path.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(tmp_path),
    )
    assert result.returncode == 1
    assert "sync-skills.py" in result.stderr


# --- output parity ----------------------------------------------------------


@pytest.mark.parametrize("template,theme", [
    ("charts/revenue-pie.json", "azure-clarity"),
    ("charts/revenue-donut.json", "nebula-glass"),
    ("concepts/team-radial.json", "slate-minimal"),
    ("drawio/cloud-infrastructure.drawio", "warm-sunnyday"),
])
def test_vendored_output_matches_source_engine(tmp_path: Path, template: str, theme: str) -> None:
    """Vendoring must be a pure copy: no behavioural fork."""
    outputs = {}
    for label, engine in (("source", ENGINE_DIR), ("vendored", VENDOR_DIR)):
        out = tmp_path / f"{label}.svg"
        result = subprocess.run(
            [
                sys.executable,
                str(engine / "render-slide-diagram.py"),
                "-i", str(engine / "templates" / template),
                "-o", str(out),
                "--theme", theme,
                "--layout", "full",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        outputs[label] = out.read_bytes()
    assert outputs["source"] == outputs["vendored"]


def test_vendored_theme_styles_match_the_source() -> None:
    for path in (ENGINE_DIR / "theme-styles").glob("*.json"):
        a = json.loads(path.read_text(encoding="utf-8"))
        b = json.loads((VENDOR_DIR / "theme-styles" / path.name).read_text(encoding="utf-8"))
        assert a == b, path.name


# --- documentation ----------------------------------------------------------

# Paths that only resolve inside a checkout. A skill that is meant to be
# installed elsewhere must not depend on them.
REPO_ONLY_ALLOWED = {
    # explicitly labelled as repository-only maintenance tooling
    "check-catalog-sync", "check-templates", "sync-skill-vendor",
    "ADD_NEW_DIAGRAM_TYPE", "test_", "sync-theme-classes", "sync-tokens-from-css",
    "theme_classes", "check-class-docs", "regenerate-golden",
}


def _skill_docs() -> list[Path]:
    return sorted(SKILL_DIR.rglob("*.md"))


def test_diagram_skill_documents_the_vendored_layout() -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "vendor/render-slide-diagram.py" in text
    assert "print-engine-path.py" in text


def test_slide_expert_skills_point_at_the_skill_not_the_repo() -> None:
    """These nine carry a diagram warning. Pointing them at `scripts/diagrams/`
    sent users to a path that does not exist in an installed skill."""
    stale = []
    for path in sorted((ROOT / "skills").glob("slide-expert-*/SKILL.md")):
        if "scripts/diagrams/render-slide-diagram.py" in path.read_text(encoding="utf-8"):
            stale.append(path.parent.name)
    assert stale == [], f"still pointing at the repo path: {stale}"


def test_no_skill_runs_a_vendored_check_or_sync_script() -> None:
    for path in _skill_docs():
        text = path.read_text(encoding="utf-8")
        for script in ("check-templates.py", "check-catalog-sync.py", "sync-skill-vendor.py"):
            if script in text:
                # Allowed only when the surrounding text marks it repo-only.
                assert "repositor" in text.lower() or "clone" in text.lower(), (
                    f"{path.name} mentions {script} without marking it repository-only"
                )
