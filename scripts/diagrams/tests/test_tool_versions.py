"""Tests for the pinned Node tool versions.

Unpinned, `npx -y <pkg>` downloads whatever is newest at that moment. The same
deck then renders differently tomorrow, the golden SVG fixtures start failing
for reasons nobody changed, and a reviewer has no way to tell a real regression
from a dependency bump. Three scripts shell out to npx:

- scripts/diagrams/render-slide-diagram.py  -> @mermaid-js/mermaid-cli
- scripts/take-screenshots.py              -> @marp-team/marp-cli
- skills/…/marp-diagnostics.py             -> @marp-team/marp-cli

`scripts/tool-versions.py` is the single source; `package.json` mirrors it and
is what npx actually reads.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
TOOL_VERSIONS = ROOT / "scripts/diagrams/tool_versions.py"
PACKAGE_JSON = ROOT / "package.json"
RENDERER = ROOT / "scripts/diagrams/render-slide-diagram.py"
TAKE_SHOTS = ROOT / "scripts/take-screenshots.py"
DIAGNOSTICS = ROOT / "skills/marp-slide-creator/scripts/marp-diagnostics.py"

NPM_PACKAGES = ["@mermaid-js/mermaid-cli", "@marp-team/marp-cli"]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


if str(ROOT / "scripts/diagrams") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts/diagrams"))

import tool_versions as tv  # noqa: E402  (import needs the sys.path entry above)


# --- the pin itself ---------------------------------------------------------


def test_package_json_exists() -> None:
    assert PACKAGE_JSON.is_file(), "package.json pins the Node tools npx resolves"


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_package_is_pinned_in_package_json(package: str) -> None:
    data = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    declared = data["devDependencies"][package]
    assert declared in tv.PINNED_VERSIONS.values(), f"{package}@{declared} is not a known pin"
    # Exact version only: ^ or ~ would float again.
    assert not re.match(r"^[\^~><=*]", declared), f"{package} must be an exact version, got {declared!r}"


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_tool_versions_and_package_json_agree(package: str) -> None:
    """The Python pin and the npm pin are two copies of one fact."""
    assert tv.PINNED_VERSIONS[package] == tv.declared_devdependencies()[package]


def test_every_pinned_package_has_an_env_override() -> None:
    assert set(tv.PINNED_VERSIONS) == set(tv.ENV_OVERRIDES)


def test_package_json_pins_nothing_undeclared() -> None:
    assert set(tv.declared_devdependencies()) == set(tv.PINNED_VERSIONS)


# --- spec construction ------------------------------------------------------


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_spec_for_is_exact(package: str) -> None:
    assert tv.spec_for(package) == f"{package}@{tv.PINNED_VERSIONS[package]}"


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_env_override_wins(package: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(tv.ENV_OVERRIDES[package], f"{package}@9.9.9")
    assert tv.spec_for(package) == f"{package}@9.9.9"


def test_no_caret_or_tilde_in_any_pinned_version() -> None:
    for package, version in tv.PINNED_VERSIONS.items():
        assert not re.search(r"[\^~*x]|>=|>", version), f"{package}@{version} floats"


# --- npx command construction ----------------------------------------------


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_npx_command_shape(package: str) -> None:
    import os

    cmd = tv.npx_command(package, "-i", "in.mmd")
    assert os.path.basename(cmd[0]).lower().startswith("npx"), cmd
    assert cmd[1] == "--yes"
    assert cmd[2] == tv.spec_for(package)
    assert cmd[3:] == ["-i", "in.mmd"]


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_npx_executable_resolves_on_this_platform(package: str) -> None:
    """On Windows the binary is npx.CMD; handing plain `npx` to subprocess
    raises FileNotFoundError because CreateProcess ignores PATHEXT."""
    import shutil

    resolved = shutil.which("npx") or shutil.which("npx.cmd")
    if not resolved:
        pytest.skip("npx not installed on this machine")
    assert tv.npx_command(package)[0] == resolved


def test_npx_command_is_a_list_not_a_shell_string() -> None:
    cmd = tv.npx_command("@marp-team/marp-cli", "a.md")
    assert isinstance(cmd, list)
    assert all(isinstance(part, str) for part in cmd)


# --- call sites use the pin -------------------------------------------------


@pytest.mark.parametrize("script", [RENDERER, TAKE_SHOTS, DIAGNOSTICS])
def test_call_site_does_not_hardcode_an_unpinned_npx(script: Path) -> None:
    """No script may invoke `npx -y <bare-package>`; a bare name floats."""
    source = script.read_text(encoding="utf-8")
    offenders = re.findall(r"npx[^\n]*?['\"]@(?:marp-team|mermaid-js)/[a-z-]+['\"](?![^\n]*@)", source)
    assert offenders == [], f"{script.name} has an unpinned npx: {offenders}"


def test_renderer_uses_the_shared_helper() -> None:
    source = RENDERER.read_text(encoding="utf-8")
    assert "from tool_versions import npx_command" in source
    assert "MERMAID_CLI = " in source


def test_take_screenshots_uses_the_shared_helper() -> None:
    source = TAKE_SHOTS.read_text(encoding="utf-8")
    assert "from tool_versions import npx_command" in source
    assert 'MARP_CLI = "@marp-team/marp-cli"' in source


def test_diagnostics_honours_the_env_override() -> None:
    source = DIAGNOSTICS.read_text(encoding="utf-8")
    assert "MARP_CLI_SPEC" in source


def test_diagnostics_default_pin_matches_tool_versions() -> None:
    """Third copy of the pin: MARP_CLI must track PINNED_VERSIONS."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("marp_diag_pin", DIAGNOSTICS)
    module = importlib.util.module_from_spec(spec)
    sys.modules["marp_diag_pin"] = module
    spec.loader.exec_module(module)
    assert module.MARP_CLI == tv.spec_for("@marp-team/marp-cli")


def test_diagnostics_run_command_has_timeout() -> None:
    source = DIAGNOSTICS.read_text(encoding="utf-8")
    assert "timeout=300" in source


# --- no shell=True remains on an interpolated path -------------------------


@pytest.mark.parametrize("script", [RENDERER, TAKE_SHOTS])
def test_npx_invocations_do_not_use_shell_true(script: Path) -> None:
    """`shell=True` with an f-string command is both a quoting hazard and a
    needless injection surface. argv lists need neither."""
    source = script.read_text(encoding="utf-8")
    for call in re.findall(r"subprocess\.run\((.{0,400}?)\)\n", source, re.S):
        if "npx" in call or "cmd" in call or "marp" in call.lower():
            assert "shell=True" not in call, f"{script.name} still uses shell=True: {call[:120]}"


def test_take_screenshots_builds_an_argv_list() -> None:
    source = TAKE_SHOTS.read_text(encoding="utf-8")
    assert "cmd = [" in source
    assert "*npx_command(" in source


# --- npm cache location -----------------------------------------------------


def test_diagnostics_no_longer_hardcodes_the_drive_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """It used C:\\tmp\\npm-cache, creating a directory at the drive root and
    failing outright for a user without write access there."""
    spec = importlib.util.spec_from_file_location("marp_diag_cache", DIAGNOSTICS)
    module = importlib.util.module_from_spec(spec)
    sys.modules["marp_diag_cache"] = module
    spec.loader.exec_module(module)

    monkeypatch.setenv("NPM_CONFIG_CACHE", str(tmp_path / "explicit-cache"))
    env = module.npm_cache_env()
    assert env["npm_config_cache"] == str(tmp_path / "explicit-cache")
    assert "C:\\tmp" not in env["npm_config_cache"]


def test_diagnostics_honours_localappdata(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = importlib.util.spec_from_file_location("marp_diag_lad", DIAGNOSTICS)
    module = importlib.util.module_from_spec(spec)
    sys.modules["marp_diag_lad"] = module
    spec.loader.exec_module(module)

    monkeypatch.delenv("NPM_CONFIG_CACHE", raising=False)
    fake = Path("D:/fake-localappdata")
    monkeypatch.setenv("LOCALAPPDATA", str(fake))
    env = module.npm_cache_env()
    assert "C:\\tmp" not in env["npm_config_cache"]
    assert env["npm_config_cache"].startswith(str(fake))


def test_diagnostics_marp_cli_spec_honours_the_override(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = importlib.util.spec_from_file_location("marp_diag_spec", DIAGNOSTICS)
    module = importlib.util.module_from_spec(spec)
    sys.modules["marp_diag_spec"] = module
    spec.loader.exec_module(module)

    monkeypatch.setenv("MARP_CLI_SPEC", "@marp-team/marp-cli@1.2.3")
    assert module._marp_cli_spec() == "@marp-team/marp-cli@1.2.3"
    monkeypatch.delenv("MARP_CLI_SPEC")
    assert module._marp_cli_spec() == module.MARP_CLI


# --- the vendored copy still works without the pin --------------------------


def test_vendored_renderer_degrades_gracefully_without_tool_versions(tmp_path: Path) -> None:
    """The `try: from tool_versions import ...` must stay optional.

    The vendored copy ships `tool_versions.py` beside it, but a partially
    copied or hand-assembled installation may not have it; the renderer should
    fall back to plain npx rather than fail to import.
    """
    import shutil

    vendor = ROOT / "skills/marp-diagram-creator/vendor"
    isolated = tmp_path / "vendor"
    shutil.copytree(vendor, isolated, ignore=shutil.ignore_patterns("__pycache__"))
    (isolated / "tool_versions.py").unlink()  # simulate a partial install

    result = subprocess.run(
        [
            sys.executable, str(isolated / "render-slide-diagram.py"),
            "-i", str(isolated / "templates/charts/revenue-pie.json"),
            "-o", str(tmp_path / "out.svg"),
            "--theme", "azure-clarity", "--layout", "full",
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(tmp_path),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "out.svg").is_file()


def test_vendored_renderer_is_pinned_in_a_complete_install(tmp_path: Path) -> None:
    import shutil

    vendor = ROOT / "skills/marp-diagram-creator/vendor"
    isolated = tmp_path / "vendor"
    shutil.copytree(vendor, isolated, ignore=shutil.ignore_patterns("__pycache__"))
    assert (isolated / "tool_versions.py").is_file()

    result = subprocess.run(
        [
            sys.executable, "-c",
            f"import sys; sys.path.insert(0, {str(isolated)!r});"
            "import importlib.util as u;"
            f"s = u.spec_from_file_location('r', {str(isolated / 'render-slide-diagram.py')!r});"
            "m = u.module_from_spec(s); s.loader.exec_module(m);"
            "print(m.npx_command('@mermaid-js/mermaid-cli')[2])",
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"@mermaid-js/mermaid-cli@{tv.PINNED_VERSIONS['@mermaid-js/mermaid-cli']}"


def test_repo_renderer_pins_the_mermaid_version(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """End-to-end: the repo renderer must pass an exact `@version` to npx."""
    spec = importlib.util.spec_from_file_location("render_pinned", RENDERER)
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "scripts/diagrams"))
    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules["render_pinned"] = module
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
        sys.path.pop(0)

    captured: list[list[str]] = []
    monkeypatch.setattr(module.subprocess, "run", lambda cmd, **kw: captured.append(cmd) or type(
        "R", (), {"returncode": 0, "stderr": "", "stdout": ""}
    )())

    from design_tokens import load_design_tokens
    module.render_mermaid("flowchart LR; A-->B", tmp_path / "o.svg", load_design_tokens("azure-clarity"), "full")

    assert captured, "npx was never invoked"
    cmd = captured[0]
    assert cmd[2] == f"@mermaid-js/mermaid-cli@{tv.PINNED_VERSIONS['@mermaid-js/mermaid-cli']}", cmd
