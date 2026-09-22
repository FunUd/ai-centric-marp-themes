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


tokens = load_module("design_tokens", "design_tokens.py")


@pytest.mark.parametrize("theme", sorted(tokens.VALID_THEMES))
def test_all_themes_expose_required_token_sections(theme: str) -> None:
    data = tokens.load_design_tokens(theme)
    assert data["shapes"]["nodeRadius"] >= 0
    assert data["typography"]["titleSize"] > 0
    assert "colors" in data
    assert "effects" in data


def test_unknown_theme_falls_back_to_default() -> None:
    data = tokens.load_design_tokens("unknown-theme")
    assert data["theme"] == tokens.DEFAULT_THEME


def test_node_style_uses_theme_radius() -> None:
    warm = tokens.theme_context(tokens.load_design_tokens("warm-sunnyday"))
    sharp = tokens.theme_context(tokens.load_design_tokens("azure-clarity"))
    assert warm["shapes"]["nodeRadius"] == 12
    assert sharp["shapes"]["nodeRadius"] == 0
    assert tokens.node_style(warm)["rx"] == 12
    assert "rx" not in tokens.node_style(sharp)


def test_nebula_glass_enables_glow() -> None:
    ctx = tokens.theme_context(tokens.load_design_tokens("nebula-glass"))
    style = tokens.node_style(ctx)
    assert ctx["effects"]["glowEnabled"] is True
    assert style["filter"] == "url(#theme-glow)"
