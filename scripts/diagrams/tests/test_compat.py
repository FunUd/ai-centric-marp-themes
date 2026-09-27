"""Tests for the console-encoding SSoT (`compat.ensure_utf8_stdio`).

Windows consoles default to cp932, so every CLI funnels through one guard
instead of carrying its own try/except. These tests pin the consolidation:

- the canonical `scripts/diagrams/compat.py`, its shipped twin in the skill,
  and the three single-file-copy fallbacks define byte-identical behaviour
  (compared as AST, so comments may differ);
- no script outside those five touches `.reconfigure(` directly.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ROOT_DIR = SCRIPT_DIR.parent.parent

CANONICAL = SCRIPT_DIR / "compat.py"
SHIPPED = ROOT_DIR / "skills/marp-slide-creator/scripts/compat.py"
FALLBACKS = [
    ROOT_DIR / "skills/marp-slide-creator/scripts/marp-lint.py",
    ROOT_DIR / "skills/marp-slide-creator/scripts/marp-diagnostics.py",
    ROOT_DIR / "skills/marp-slide-creator/scripts/post-edit-check.py",
]

import compat as compat_module  # noqa: E402


def _function_ast(path: Path) -> ast.FunctionDef:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "ensure_utf8_stdio":
            return node
    raise AssertionError(f"{path} defines no ensure_utf8_stdio")


def _fallback_ast(path: Path) -> ast.FunctionDef:
    """The `def ensure_utf8_stdio` nested in `except ImportError`."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "ensure_utf8_stdio":
                    return child
    raise AssertionError(f"{path} has no ImportError fallback for ensure_utf8_stdio")


def test_shipped_copy_matches_canonical() -> None:
    assert ast.dump(_function_ast(CANONICAL)) == ast.dump(_function_ast(SHIPPED))


@pytest.mark.parametrize("path", FALLBACKS, ids=[p.name for p in FALLBACKS])
def test_fallback_matches_canonical(path: Path) -> None:
    assert ast.dump(_function_ast(CANONICAL)) == ast.dump(_fallback_ast(path))


def _reconfigure_calls_outside_guard(path: Path) -> list[int]:
    """Line numbers of `.reconfigure(` calls not covered by the guard.

    Allowed: the guard definition itself (`compat.py`), or a call nested in
    an `except ImportError` fallback. Anything else is a new copy-paste that
    must go through `ensure_utf8_stdio` instead.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    bad: list[int] = []

    def visit(node: ast.AST, in_fallback: bool, in_guard_def: bool) -> None:
        nonlocal bad
        if isinstance(node, ast.FunctionDef) and node.name == "ensure_utf8_stdio":
            in_guard_def = True
        if isinstance(node, ast.ExceptHandler):
            in_fallback = True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "reconfigure"
            and not (in_fallback or in_guard_def)
        ):
            bad.append(node.lineno)
        for child in ast.iter_child_nodes(node):
            visit(child, in_fallback, in_guard_def)

    visit(tree, False, path.name == "compat.py")
    return bad


def test_no_direct_reconfigure_outside_the_guard() -> None:
    roots = [SCRIPT_DIR, ROOT_DIR / "scripts", ROOT_DIR / "skills"]
    offenders: list[str] = []
    seen: set[Path] = set()
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts or path in seen:
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if ".reconfigure(" not in text:
                continue
            for lineno in _reconfigure_calls_outside_guard(path):
                offenders.append(f"{path.relative_to(ROOT_DIR)}:{lineno}")
    assert offenders == []


def test_guard_forces_utf8() -> None:
    calls: list[dict] = []

    class Stream:
        def reconfigure(self, **kwargs: object) -> None:
            calls.append(kwargs)

    import sys as _sys

    real_out, real_err = _sys.stdout, _sys.stderr
    _sys.stdout, _sys.stderr = Stream(), Stream()  # type: ignore[misc]
    try:
        compat_module.ensure_utf8_stdio()
    finally:
        _sys.stdout, _sys.stderr = real_out, real_err
    assert calls == [
        {"encoding": "utf-8", "errors": "replace"},
        {"encoding": "utf-8", "errors": "replace"},
    ]


def test_guard_tolerates_streams_without_reconfigure() -> None:
    class Bare:
        pass

    import sys as _sys

    real_out, real_err = _sys.stdout, _sys.stderr
    _sys.stdout, _sys.stderr = Bare(), Bare()  # type: ignore[misc]
    try:
        compat_module.ensure_utf8_stdio()  # must not raise
    finally:
        _sys.stdout, _sys.stderr = real_out, real_err
