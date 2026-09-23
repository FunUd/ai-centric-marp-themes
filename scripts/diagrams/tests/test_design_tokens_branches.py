"""Branch-coverage tests for design_tokens.py (luminance parsing fallbacks,
best_text_on guard clauses, and the missing-file fallback in
load_design_tokens)."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tokens = load_module("design_tokens_branches", "design_tokens.py")


# --- _luminance --------------------------------------------------------------


def test_luminance_expands_shorthand_hex() -> None:
    assert tokens._luminance("#fff") == pytest.approx(tokens._luminance("#ffffff"))
    assert tokens._luminance("#000") == pytest.approx(0.0)


def test_luminance_rejects_malformed_hex() -> None:
    assert tokens._luminance("#12345") is None          # wrong length
    assert tokens._luminance("#zzzzzz") is None          # non-hex digits -> ValueError
    assert tokens._luminance("#1234567") is None


# --- best_text_on ------------------------------------------------------------


def test_best_text_on_guards() -> None:
    # Not a hex color at all -> keep the provided light color.
    assert tokens.best_text_on(None, "light") == "light"
    assert tokens.best_text_on("  ", "light") == "light"
    assert tokens.best_text_on("transparent", "light") == "light"
    # Hex-shaped but unparsable -> luminance None -> light.
    assert tokens.best_text_on("#zzzzzz", "light") == "light"


def test_best_text_on_picks_by_luminance() -> None:
    assert tokens.best_text_on("#FFFFFF", "light", "dark") == "dark"
    assert tokens.best_text_on("#000000", "light", "dark") == "light"


# --- load_design_tokens fallback ---------------------------------------------


def test_load_design_tokens_falls_back_when_theme_file_missing(tmp_path: Path, monkeypatch) -> None:
    """A valid theme name whose JSON is absent falls back to the default file."""
    styles = tmp_path / "theme-styles"
    styles.mkdir()
    shutil.copy(SCRIPT_DIR / "theme-styles" / "azure-clarity.json", styles / "azure-clarity.json")
    monkeypatch.setattr(tokens, "THEME_STYLES_DIR", styles)

    data = tokens.load_design_tokens("prism-edge")  # file missing in this dir

    default = json.loads((styles / "azure-clarity.json").read_text(encoding="utf-8"))
    assert data["theme"] == default["theme"]


def test_load_design_tokens_raises_when_default_also_missing(tmp_path: Path, monkeypatch) -> None:
    styles = tmp_path / "empty-styles"
    styles.mkdir()
    monkeypatch.setattr(tokens, "THEME_STYLES_DIR", styles)

    with pytest.raises(FileNotFoundError):
        tokens.load_design_tokens("azure-clarity")


# --- misc small helpers still unasserted --------------------------------------


def test_node_style_variants_and_filters() -> None:
    ctx = tokens.theme_context(tokens.load_design_tokens("azure-clarity"))

    base = tokens.node_style(ctx, "primary")
    assert "filter" in base  # azure enables shadows
    # azure-clarity ships a zero node radius, so rx/ry are omitted.
    assert "rx" not in base

    unknown = tokens.node_style(ctx, "no-such-variant")
    assert unknown["fill"] == base["fill"]  # falls back to primary variant

    # Non-zero radius themes add rx/ry mirroring the radius.
    rounded = dict(ctx)
    rounded["shapes"] = {**ctx["shapes"], "nodeRadius": 8, "nodeRadiusLg": 14}
    style = tokens.node_style(rounded, "primary")
    assert style["rx"] == 8 and style["ry"] == 8
    assert tokens.node_style(rounded, "primary", large=True)["rx"] == 14

    # Glow takes precedence over shadow for the filter id.
    glowing = dict(ctx)
    glowing["effects"] = {**ctx["effects"], "glowEnabled": True, "nodeShadowEnabled": True}
    assert tokens.node_style(glowing, "primary")["filter"] == "url(#theme-glow)"

    # Zero-radius themes omit rx/ry entirely.
    flat = dict(ctx)
    flat["shapes"] = {**ctx["shapes"], "nodeRadius": 0, "nodeRadiusLg": 0}
    assert "rx" not in tokens.node_style(flat, "primary")


def test_mermaid_postprocess_rules_expose_tokens() -> None:
    theme = tokens.load_design_tokens("nebula-glass")
    rules = tokens.mermaid_postprocess_rules(theme)

    assert rules["fontFamily"] == theme["fontFamily"]
    assert rules["nodeRadius"] == theme["shapes"]["nodeRadius"]
    assert "glowEnabled" in rules


def test_drawio_rect_radius_prefers_swimlane_radius() -> None:
    theme = tokens.load_design_tokens("azure-clarity")

    assert tokens.drawio_rect_radius(theme, {"swimlane": "1"}) == float(theme["shapes"]["nodeRadiusLg"])
    assert tokens.drawio_rect_radius(theme, {"rounded": "1"}) == float(theme["shapes"]["nodeRadius"])
