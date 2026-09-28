"""Committed showcase SVGs must match what the fixed engine produces.

Regression: `mindmap-compact.svg` shipped without the label-bold rule and
with invisible active Gantt bars — the committed artifacts rotted while the
engine moved on, with no gate noticing. This test pins the showcase deck:

- every `assets/diagrams/*.svg` referenced by `new-diagrams-showcase.md`
  resolves to a same-stem template on disk;
- JSON diagrams (deterministic pure-Python renderer) are byte-identical to
  a fresh render;
- Mermaid diagrams carry the postprocessor signals (mindmap bold labels,
  Gantt active boundary in theme ink, theme palette present) — full
  contrast floors for fresh renders live in `test_mermaid_contrast.py`,
  while byte comparison is avoided: Mermaid output can drift by font
  metrics across environments.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SCRIPT_DIR.parent.parent
DECK = ROOT_DIR / "slides/new-diagrams-showcase/new-diagrams-showcase.md"
ASSETS = ROOT_DIR / "slides/new-diagrams-showcase/assets/diagrams"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tokens = load_module("design_tokens_showcase", "design_tokens.py")
render_mod = load_module("render_showcase_check", "render-slide-diagram.py")


def _deck_theme() -> str:
    text = DECK.read_text(encoding="utf-8")
    match = re.search(r"^theme:\s*(\S+)\s*$", text, re.MULTILINE)
    assert match, "deck frontmatter has no theme"
    return match.group(1)


def _pairs() -> list[tuple[str, str]]:
    """(template relpath under templates/, committed svg name) by stem."""
    text = DECK.read_text(encoding="utf-8")
    svgs = re.findall(r"assets/diagrams/([\w-]+\.svg)", text)
    assert svgs, "deck references no diagram SVGs"
    templates = {
        Path(match.group(1)).stem: match.group(1)
        for match in re.finditer(r"`((?:mermaid|charts|concepts|drawio|organization)/[\w.-]+)`", text)
    }
    pairs = []
    for svg in sorted(set(svgs)):
        stem = Path(svg).stem
        assert stem in templates, f"{svg} has no matching template code span in the deck"
        pairs.append((templates[stem], svg))
    return pairs


def test_every_embed_resolves_to_a_template_on_disk() -> None:
    for rel, svg in _pairs():
        assert (SCRIPT_DIR / "templates" / rel).is_file(), f"template missing: {rel}"
        assert (ASSETS / svg).is_file(), f"committed SVG missing: {svg}"


def test_json_showcase_svgs_are_byte_fresh() -> None:
    theme = _deck_theme()
    tdata = tokens.load_design_tokens(theme)
    for rel, svg in _pairs():
        if not rel.endswith(".json"):
            continue
        data = json.loads((SCRIPT_DIR / "templates" / rel).read_text(encoding="utf-8"))
        fresh = render_mod.render_diagram(data, tdata, "full")
        committed = (ASSETS / svg).read_text(encoding="utf-8")
        assert fresh == committed, f"{svg} is stale: re-render {rel} with the fixed engine"


def test_mermaid_showcase_svgs_carry_postprocessor_signals() -> None:
    theme = _deck_theme()
    tdata = tokens.load_design_tokens(theme)
    ctx = tokens.theme_context(tdata)
    for rel, svg in _pairs():
        if not rel.endswith(".mmd"):
            continue
        text = (ASSETS / svg).read_text(encoding="utf-8")
        assert ctx["primary"] in text or ctx["primary"].lower() in text.lower(), (
            f"{svg}: theme primary {ctx['primary']} absent — likely raw CLI output"
        )
        if "mindmap" in rel:
            assert "font-weight:700" in text, f"{svg}: mindmap bold rule missing (stale)"
            for line in re.finditer(r"\.section-(?:-?\d+|root)\s+line\{([^}]*)\}", text):
                body = line.group(1).replace(" ", "")
                assert "stroke:none" in body or "stroke-width:0" in body, (
                    f"{svg}: brown underline alive: {line.group(0)[:60]}"
                )
        if "gantt" in rel:
            match = re.search(r"\.active0[^{]*\{([^}]*)\}", text)
            assert match, f"{svg}: no active-task rule"
            stroke = re.search(r"stroke:([^;!]+)", match.group(1))
            assert stroke, f"{svg}: active task has no stroke"
            assert tokens.contrast_ratio(
                tokens.normalize_color(stroke.group(1)), ctx["background"]
            ) >= 3.0, f"{svg}: active-task boundary invisible again"
