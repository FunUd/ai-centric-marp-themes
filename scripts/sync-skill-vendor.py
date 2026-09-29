#!/usr/bin/env python3
"""sync-skill-vendor.py — Vendor the diagram runtime into the diagram skill.

`skills/marp-diagram-creator` is the only skill that *executes* the diagram
engine, and it did not ship one. It was 3 files / 20 KB of prose pointing at
`scripts/diagrams/render-slide-diagram.py`, which lives outside the skill. So:

- a deck built with the skill inside this repo worked;
- the same skill copied to `~/.claude/skills/` (or a colleague's machine, or a
  vendored checkout) was **structurally broken** — every documented command
  resolved to a non-existent path.

This script vendors the *runtime* subset of the engine into the skill so it is
self-contained. `scripts/diagrams/` stays the single source of truth for
development and testing; the vendored copy is generated and drift-checked, the
same pattern as `sync-theme-classes.py` and `sync-tokens-from-css.py`.

Only the transitive runtime closure of the two entry points is copied. The
maintenance scripts (`check-*.py`, `sync-*.py`, `theme_classes.py`,
`regenerate-golden.py`) stay behind: they exist to operate on the repository and
are meaningless outside it.

Usage:
    python scripts/sync-skill-vendor.py           # rewrite the vendored copy
    python scripts/sync-skill-vendor.py --check   # fail on drift
"""
from __future__ import annotations

import argparse
import ast
import filecmp
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
ENGINE_DIR = SCRIPT_DIR / "diagrams"
VENDOR_DIR = ROOT_DIR / "skills/marp-diagram-creator/vendor"

sys.path.insert(0, str(ENGINE_DIR))
from compat import ensure_utf8_stdio  # noqa: E402

# Entry points a user invokes. Their transitive local imports are the runtime set.
ENTRY_POINTS = ("render-slide-diagram", "validate-slide-diagram")

# Data directories the runtime reads relative to the engine root.
DATA_DIRS = ("templates", "theme-styles")

# Never vendored: these read the repository (docs/, themes/*.css, the test
# suite) and are meaningless in a standalone skill installation.
DEV_ONLY = {
    "check-catalog-sync",
    "check-class-docs",
    "check-templates",
    "regenerate-golden",
    "sync-theme-classes",
    "sync-tokens-from-css",
    "theme_classes",
}


def _module_names() -> set[str]:
    names = {p.stem for p in ENGINE_DIR.glob("*.py")}
    # Sub-packages (e.g. renderers/) are first-class runtime modules: their
    # __init__.py marks them importable, and the whole directory is vendored.
    names.update(
        p.name
        for p in ENGINE_DIR.iterdir()
        if p.is_dir() and (p / "__init__.py").is_file() and "__pycache__" not in p.parts
    )
    return names


def local_imports(path: Path, known: set[str]) -> set[str]:
    """Names of sibling modules this file imports."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError) as error:
        raise RuntimeError(f"cannot parse {path}: {error}") from error
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Absolute: from X import ... / Relative: from . import X / from .X import ...
            if node.level and node.level > 0:
                for alias in node.names:
                    # from . import foo  -> alias.name == foo
                    # from .foo import bar -> node.module == foo
                    candidate = node.module or alias.name.split(".")[0]
                    if candidate in known:
                        found.add(candidate)
            elif node.module and node.module.split(".")[0] in known:
                found.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in known:
                    found.add(top)
    return found


def _member_paths(name: str) -> list[Path]:
    """Source files implementing a runtime module (single file or package)."""
    single = ENGINE_DIR / f"{name}.py"
    if single.is_file():
        return [single]
    pkg = ENGINE_DIR / name
    if pkg.is_dir() and (pkg / "__init__.py").is_file():
        return sorted(p for p in pkg.rglob("*.py") if "__pycache__" not in p.parts)
    raise RuntimeError(f"runtime module has no source: {name}")


def runtime_modules() -> set[str]:
    """Transitive local-import closure of the entry points."""
    known = _module_names()
    for name in ENTRY_POINTS:
        if not (ENGINE_DIR / f"{name}.py").exists():
            raise RuntimeError(f"entry point missing: {ENGINE_DIR / f'{name}.py'}")
    resolved: set[str] = set()
    stack = list(ENTRY_POINTS)
    while stack:
        name = stack.pop()
        if name in resolved:
            continue
        resolved.add(name)
        for member in _member_paths(name):
            stack.extend(local_imports(member, known))
    missing = sorted(resolved - known)
    if missing:
        raise RuntimeError(f"entry points import missing modules: {missing}")
    return resolved


def _source_for(relative: str) -> Path:
    """Map a vendored path back to the file it is generated from."""
    return ENGINE_DIR / relative


def expected_files() -> set[str]:
    """Vendored paths, relative to VENDOR_DIR, as posix strings."""
    files: set[str] = set()
    for name in sorted(runtime_modules()):
        for member in _member_paths(name):
            files.add(member.relative_to(ENGINE_DIR).as_posix())
    for data_dir in DATA_DIRS:
        data_path = ENGINE_DIR / data_dir
        if not data_path.is_dir():
            raise RuntimeError(f"data dir missing: {data_path}")
        for path in data_path.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                files.add(path.relative_to(ENGINE_DIR).as_posix())
    return files


def _is_stale_vendored_file(relative: str) -> bool:
    """True when VENDOR_DIR holds a file the source no longer produces."""
    vendored = VENDOR_DIR / relative
    source = _source_for(relative)
    if not source.exists():
        return True
    return not filecmp.cmp(vendored, source, shallow=False)


def write_vendor() -> int:
    import tempfile

    files = expected_files()
    # Stage in the same directory as VENDOR_DIR so rename() never crosses
    # volumes/drives (tempfile.gettempdir() may live on another drive).
    staging_parent = VENDOR_DIR.parent
    staging_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".vendor-tmp-", dir=str(staging_parent)))
    try:
        for relative in sorted(files):
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(_source_for(relative), destination)
        # Swap staging into place atomically-ish.
        if VENDOR_DIR.exists():
            backup = VENDOR_DIR.with_name(VENDOR_DIR.name + ".bak")
            if backup.exists():
                shutil.rmtree(backup)
            VENDOR_DIR.rename(backup)
            try:
                staging.rename(VENDOR_DIR)
            except Exception:
                backup.rename(VENDOR_DIR)
                raise
            shutil.rmtree(backup, ignore_errors=True)
        else:
            staging.rename(VENDOR_DIR)
            staging = None  # moved; do not cleanup
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)

    modules = sorted(runtime_modules())
    total = sum((VENDOR_DIR / f).stat().st_size for f in files)
    print(f"[SYNC] vendored {len(files)} files ({total / 1024:.0f} KB) into {VENDOR_DIR.relative_to(ROOT_DIR)}")
    print(f"       runtime modules: {', '.join(modules)}")
    excluded = sorted(_module_names() - set(modules))
    print(f"       dev-only, not vendored: {', '.join(excluded)}")
    return 0


def check_vendor() -> int:
    if not VENDOR_DIR.exists():
        print(
            f"[DRIFT] {VENDOR_DIR.relative_to(ROOT_DIR)} is missing.\n"
            f"        Run: python scripts/sync-skill-vendor.py",
            file=sys.stderr,
        )
        return 1

    expected = expected_files()
    actual = {
        p.relative_to(VENDOR_DIR).as_posix()
        for p in VENDOR_DIR.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }

    problems: list[str] = []
    for missing in sorted(expected - actual):
        problems.append(f"[MISSING] {missing}")
    for extra in sorted(actual - expected):
        problems.append(f"[STALE] {extra} is vendored but the engine no longer produces it")
    for relative in sorted(expected & actual):
        if _is_stale_vendored_file(relative):
            problems.append(f"[STALE] {relative} differs from scripts/diagrams/{relative}")

    if problems:
        for line in problems:
            print(line, file=sys.stderr)
        print(
            f"FAILED: {len(problems)} vendored file problem(s).\n"
            f"       Run: python scripts/sync-skill-vendor.py",
            file=sys.stderr,
        )
        return 1

    print(f"[OK] {len(expected)} vendored files in sync with scripts/diagrams.")
    return 0


def main() -> int:
    ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Vendor the diagram runtime into marp-diagram-creator.")
    parser.add_argument("--check", action="store_true", help="Fail if the vendored copy is stale.")
    args = parser.parse_args()

    missing = [n for n in ENTRY_POINTS if not (ENGINE_DIR / f"{n}.py").exists()]
    if missing:
        print(f"[ERROR] entry points not found in {ENGINE_DIR}: {missing}", file=sys.stderr)
        return 1

    overlap = sorted(runtime_modules() & DEV_ONLY)
    if overlap:
        print(
            f"[ERROR] dev-only modules are in the runtime closure: {overlap}. "
            f"They read the repository and must not be vendored.",
            file=sys.stderr,
        )
        return 1

    return check_vendor() if args.check else write_vendor()


if __name__ == "__main__":
    raise SystemExit(main())
