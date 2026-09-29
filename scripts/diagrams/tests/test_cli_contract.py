"""CLI contract tests: exit codes and console encoding.

- P0-1: a render that fails layout validation must exit non-zero and must not
  print `[SUCCESS]` (previously it printed `[WARN]` and still exited 0, so
  broken geometry sailed through automation). `--no-validate` remains the
  documented escape hatch.
- P0-2: the CLIs force UTF-8 on stdout/stderr so Japanese file names and text
  survive Windows consoles/pipes that default to cp932.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]


def _run(args: list[str], *, utf8_env: bool = False) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if utf8_env:
        # Simulate a plain cp932 console: strip the shortcuts the docs tell
        # users to set manually — the CLIs must not need them.
        env.pop("PYTHONIOENCODING", None)
        env.pop("PYTHONUTF8", None)
    return subprocess.run([sys.executable, *args], capture_output=True, env=env)


# --- P0-1: validation failures propagate ------------------------------------


def test_render_exits_nonzero_when_validation_fails(tmp_path: Path) -> None:
    source = tmp_path / "too-tall.json"
    output = tmp_path / "too-tall.svg"
    source.write_text(
        json.dumps({"type": "pie", "height": 600, "items": [{"label": "A", "value": 1}]}),
        encoding="utf-8",
    )

    result = _run(
        [
            str(SCRIPT_DIR / "render-slide-diagram.py"),
            "-i",
            str(source),
            "-o",
            str(output),
            "--theme",
            "azure-clarity",
            "--layout",
            "full",
        ]
    )

    stdout = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode != 0, f"expected non-zero exit, got 0 with output:\n{stdout}"
    assert "[SUCCESS]" not in stdout, "must not claim success after failed validation"
    assert "failed layout validation" in result.stderr.decode("utf-8", errors="replace")


def test_render_exits_zero_for_valid_diagram(tmp_path: Path) -> None:
    source = tmp_path / "ok.json"
    output = tmp_path / "ok.svg"
    source.write_text(
        json.dumps({"type": "pie", "aspect": 2.4, "items": [{"label": "A", "value": 1}]}),
        encoding="utf-8",
    )

    result = _run(
        [
            str(SCRIPT_DIR / "render-slide-diagram.py"),
            "-i",
            str(source),
            "-o",
            str(output),
            "--theme",
            "azure-clarity",
            "--layout",
            "full",
        ]
    )

    stdout = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode == 0, f"render failed:\n{stdout}"
    assert "[SUCCESS]" in stdout


def test_no_validate_remains_the_escape_hatch(tmp_path: Path) -> None:
    source = tmp_path / "too-tall.json"
    output = tmp_path / "too-tall.svg"
    source.write_text(
        json.dumps({"type": "pie", "height": 600, "items": [{"label": "A", "value": 1}]}),
        encoding="utf-8",
    )

    result = _run(
        [
            str(SCRIPT_DIR / "render-slide-diagram.py"),
            "-i",
            str(source),
            "-o",
            str(output),
            "--theme",
            "azure-clarity",
            "--layout",
            "full",
            "--no-validate",
        ]
    )

    assert result.returncode == 0
    assert b"[SUCCESS]" in result.stdout


# --- P0-2: UTF-8 console output ---------------------------------------------


def test_validator_cli_emits_utf8_despite_cp932_console(tmp_path: Path) -> None:
    svg = tmp_path / "図式.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 400" width="900" height="400"/>',
        encoding="utf-8",
    )

    result = _run([str(SCRIPT_DIR / "validate-slide-diagram.py"), str(svg)], utf8_env=True)

    # Strict UTF-8 decode: a cp932-encoded 図 (0x96 0x73) is invalid UTF-8 and
    # would raise here if the CLI had not reconfigured its streams.
    stdout = result.stdout.decode("utf-8")
    assert "図式.svg" in stdout
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
