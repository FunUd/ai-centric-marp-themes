"""SKILL.md §2 and diagram-patterns.md §3 must name the same engines.

The patterns table is declared canonical and the SKILL summary "must stay
consistent with it" — by convention only. This gate parses both markdown
tables and requires every diagram keyword to resolve to the same engine
set on both sides, so an insertion, rename, or engine reassignment in one
table fails loudly instead of rotting the other.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills/marp-diagram-creator/SKILL.md"
PATTERNS = ROOT / "skills/marp-diagram-creator/references/diagram-patterns.md"

ENGINES = ("mermaid", "draw.io", "json", "css")


def _table_rows(text: str, header: str) -> list[list[str]]:
    start = text.find(header)
    assert start != -1, f"table header missing: {header}"
    rows: list[list[str]] = []
    for line in text[start:].splitlines()[2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    assert rows, f"no rows under {header}"
    return rows


def _engines_in(cell: str) -> set[str]:
    lowered = cell.lower()
    return {name for name in ENGINES if name in lowered}


def _skill_map() -> dict[str, str]:
    """Normalized engine -> Best-For cell text."""
    mapping: dict[str, str] = {}
    for row in _table_rows(SKILL.read_text(encoding="utf-8"), "| Engine |"):
        names = _engines_in(row[0])
        assert len(names) == 1, f"SKILL engine row names two engines: {row[0]}"
        mapping[next(iter(names))] = row[1]
    assert set(mapping) == set(ENGINES), f"SKILL engine rows changed: {sorted(mapping)}"
    return mapping


def _patterns_rows() -> list[tuple[str, set[str]]]:
    out = []
    for row in _table_rows(PATTERNS.read_text(encoding="utf-8"), "| Diagram Type |"):
        names = _engines_in(row[1])
        assert names, f"patterns row names no known engine: {row[0]}"
        out.append((row[0], names))
    return out


# (keyword regex, expected engine set). The regex must hit the patterns row
# type text; the same match must appear in at least one expected engine's
# SKILL Best-For cell, and the patterns rows mentioning it must jointly
# name exactly the expected engines.
EXPECTATIONS: list[tuple[str, set[str]]] = [
    (r"numeric data", {"json"}),
    (r"scored", {"json"}),
    (r"text-only", {"css"}),
    (r"2-axis", {"css"}),
    (r"flowchart", {"mermaid", "draw.io"}),
    (r"sequence", {"mermaid"}),
    (r"3-tier", {"mermaid", "draw.io"}),
    (r"cloud", {"draw.io"}),
    (r"state machin\w*", {"mermaid"}),
    (r"gantt", {"mermaid"}),
    (r"\bER\b", {"mermaid"}),
    (r"c4", {"mermaid"}),
    (r"mind", {"mermaid"}),
]


def test_engine_tables_agree() -> None:
    skill = _skill_map()
    patterns = _patterns_rows()
    for keyword, expected in EXPECTATIONS:
        mentioning = [(dtype, engines) for dtype, engines in patterns if re.search(keyword, dtype, re.IGNORECASE)]
        assert mentioning, f"patterns table lost keyword {keyword!r}"
        union = set().union(*(engines for _, engines in mentioning))
        assert union == expected, f"patterns engines for {keyword!r}: {sorted(union)} != {sorted(expected)}"
        hits = [name for name in expected if re.search(keyword, skill[name], re.IGNORECASE)]
        assert hits, f"SKILL Best-For lost keyword {keyword!r} (expected in {sorted(expected)})"
