"""tool-versions.py — Pinned Node tool versions, single source of truth.

Three scripts shell out to `npx`:

- ``scripts/diagrams/render-slide-diagram.py`` → ``@mermaid-js/mermaid-cli``
- ``scripts/take-screenshots.py``             → ``@marp-team/marp-cli``
- ``skills/…/marp-diagnostics.py``            → ``@marp-team/marp-cli``

Unpinned, ``npx -y <pkg>`` downloads *whatever is newest at that moment*, so the
same deck can render differently tomorrow and the golden SVG fixtures start
failing for reasons nobody changed. Versions are pinned here and mirrored into
``package.json`` (which is what actually makes ``npx`` pick them up locally and
in CI). ``test_tool_versions.py`` fails if the two disagree.

The specs are also exported as environment-variable defaults so a caller can
override without editing code::

    MARP_CLI_SPEC=@marp-team/marp-cli@4.2.3 python render-slide-diagram.py …
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
# The repository root is the parent of scripts/, i.e. two levels up from here
# (scripts/diagrams/). A vendored copy under a skill has neither, which is why
# declared_devdependencies() tolerates a missing package.json.
REPO_ROOT = SCRIPT_DIR.parent.parent

# npm package name -> pinned exact version (no ^ or ~).
PINNED_VERSIONS: dict[str, str] = {
    "@mermaid-js/mermaid-cli": "12.0.0",
    "@marp-team/marp-cli": "4.2.3",
}

# npm package -> environment variable a caller can set to override the spec.
ENV_OVERRIDES: dict[str, str] = {
    "@mermaid-js/mermaid-cli": "MERMAID_CLI_SPEC",
    "@marp-team/marp-cli": "MARP_CLI_SPEC",
}

PACKAGE_JSON = REPO_ROOT / "package.json"


def spec_for(package: str) -> str:
    """`@scope/name@1.2.3`, honouring an environment override."""
    override = ENV_OVERRIDES.get(package)
    if override and os.environ.get(override):
        return os.environ[override]
    return f"{package}@{PINNED_VERSIONS[package]}"


def declared_devdependencies() -> dict[str, str]:
    if not PACKAGE_JSON.is_file():
        return {}
    import json

    data = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    return dict(data.get("devDependencies", {}))


def npx_command(package: str, *args: str) -> list[str]:
    """`npx` invocation for a pinned package, resolved for the host platform.

    On Windows the executable is ``npx.CMD``; handing ``npx`` straight to
    ``subprocess`` raises ``FileNotFoundError`` because CreateProcess does not
    consult PATHEXT.
    """
    npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
    return [npx, "--yes", spec_for(package), *args]


def installed_version(package: str) -> str | None:
    """Version ``npx`` currently resolves, or None if it cannot be determined."""
    npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
    try:
        result = subprocess.run(
            [npx, "--yes", spec_for(package), "--version"],
            capture_output=True,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    for token in result.stdout.split():
        if token and token[0].isdigit():
            return token.lstrip("v")
    return None
