#!/usr/bin/env python3
"""
post-edit-check.py
==================
Run AFTER EVERY edit to a Marp Markdown file (before or together with marp-lint.py).

Why this exists (lessons learned):
  1. A trailing newline loss silently glued a paragraph and its `---` separator
     onto one line. marp-lint.py did NOT catch it: two slides merged, a
     grid-quadrant layout broke, and the deck shrank from 10 slides to 9.
     Detecting it cost 3 extra edit/render round-trips.
  2. Simplified-Chinese characters ("而非", "产出") leaked into Japanese content
     and no existing tool flagged them.

Checks performed:
  - SLIDE_SEPARATOR_GLUED : `---` glued to surrounding text on the same line
  - SLIDE_COUNT_MISMATCH  : rendered/expected slide count != `---` structure count
  - MISSING_EOF_NEWLINE    : file does not end with a newline (the root cause of #1)
  - LANGUAGE_CONTAMINATION : (only with --lang) out-of-language characters/words
  - HTML_SECTION_MISMATCH : (optional, --html) <section> count != slide count

Language check (`--lang`):
  Contamination is RELATIVE to the expected language, so it is opt-in:
    --lang ja : flag simplified-Chinese-only chars/words (they are not valid
                Japanese) — use for Japanese decks
    --lang zh : flag kana (hiragana/katakana) — use for Chinese decks
    (no --lang): language check skipped entirely; structural checks still run
  Do NOT assume Japanese: an English or Chinese deck must never fail the
  ja-contamination rule.

Usage:
  python skills/marp-slide-creator/scripts/post-edit-check.py deck.md --expect 10 --lang ja
  python skills/marp-slide-creator/scripts/post-edit-check.py deck.md --lang zh
  python skills/marp-slide-creator/scripts/post-edit-check.py deck.md --html deck/preview.html

Exit code: 0 = all checks passed, 1 = at least one ERROR.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Console encoding SSoT lives in scripts/diagrams/compat.py; the skill ships
# as a directory, so import the sibling — with the same lines as fallback for
# single-file copies.
try:
    from compat import ensure_utf8_stdio
except ImportError:  # pragma: no cover - single-file copy without compat.py

    def ensure_utf8_stdio() -> None:
        """Force UTF-8 on stdout/stderr; skip streams that cannot be reconfigured."""
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError, ValueError):
                pass


ensure_utf8_stdio()

# Simplified-Chinese-only glyphs that never appear in normal Japanese text.
# Curated to avoid false positives on valid Japanese kanji
# (e.g. 体/学/会/医/团/声/点/后 are shared or JP-standard -> excluded).
ZH_CHARS = set(
    "们这产现发对说时长从众语词计划边还处门题议认让应该图书网络话电脑观权乐欢汉铁银买卖钱轮护实开关样无业个为进义户标"
)

# Word-level patterns (mainly simplified-only compound words).
ZH_WORDS = [
    "而非",
    "产出",
    "我们",
    "这是",
    "因为",
    "所以",
    "但是",
    "然后",
    "确认",
    "实现",
    "进行",
    "通过",
    "数据",
    "用户",
    "视频",
    "这个",
]


def _has_kana(ch: str) -> bool:
    """True for hiragana/katakana (Japanese-only; invalid in Chinese text)."""
    return (
        "\u3040" <= ch <= "\u309f"  # hiragana
        or "\u30a0" <= ch <= "\u30ff"  # katakana
        or "\u31f0" <= ch <= "\u31ff"  # katakana extensions
    )


def _strip_fenced_code(lines: list[str]) -> list[str]:
    """Return lines outside ``` fenced code blocks (blanked out)."""
    out, in_fence = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return out


def check(
    md_path: Path,
    expect: int | None,
    html_path: Path | None,
    lang: str | None,
) -> int:
    raw = md_path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    body_lines = _strip_fenced_code(lines)

    errors: list[str] = []
    warnings: list[str] = []

    # --- 1. Separator count & glued separators -------------------------
    # Structure: line1 `---` (frontmatter open) + closing `---` + (slides - 1)
    # separators  => strict `---` lines == slides + 1.
    strict = [i for i, ln in enumerate(lines, 1) if ln.strip() == "---"]
    slide_count = max(len(strict) - 1, 1)

    for i, ln in enumerate(lines, 1):
        if "---" not in ln or ln.strip() == "---":
            continue
        # Markdown table rows like |---|:---| are valid `---` usage, not glue.
        if "|" in ln:
            continue
        errors.append(
            f"SLIDE_SEPARATOR_GLUED line {i}: `---` is glued to text -> "
            f"the following slide silently merges into this one. "
            f"Put `---` alone on its own line. (content: {ln.strip()[:60]!r})"
        )

    # --- 2. Expected slide count ---------------------------------------
    if expect is not None and slide_count != expect:
        errors.append(
            f"SLIDE_COUNT_MISMATCH: file structure implies {slide_count} slide(s) but --expect {expect} was given."
        )

    # --- 3. EOF newline --------------------------------------------------
    if raw and not raw.endswith("\n"):
        warnings.append(
            "MISSING_EOF_NEWLINE: file does not end with a newline. "
            "This is the root cause of glued `---` separators - fix it now."
        )

    # --- 4. Language contamination (opt-in via --lang) ---------------------
    # Contamination is relative to the deck's expected language.
    if lang == "ja":
        for i, ln in enumerate(body_lines, 1):
            hits = sorted({ch for ch in ln if ch in ZH_CHARS})
            word_hits = [w for w in ZH_WORDS if w in ln]
            found = ", ".join(word_hits + hits)
            if found:
                errors.append(
                    f"LANGUAGE_CONTAMINATION line {i}: simplified-Chinese only "
                    f"({found}) in Japanese content (--lang ja)."
                )
    elif lang == "zh":
        for i, ln in enumerate(body_lines, 1):
            kana = sorted({ch for ch in ln if _has_kana(ch)})
            if kana:
                preview = "".join(kana)
                errors.append(
                    f"LANGUAGE_CONTAMINATION line {i}: Japanese kana ({preview}) in Chinese content (--lang zh)."
                )
    # lang is None -> language check skipped (e.g. English decks)

    # --- 5. Optional: rendered HTML section count -------------------------
    if html_path is not None:
        if not html_path.exists():
            warnings.append(f"HTML_NOT_FOUND: {html_path} (skipped)")
        else:
            html = html_path.read_text(encoding="utf-8", errors="replace")
            sections = len(re.findall(r"<section[\s>]", html))
            if sections != slide_count:
                errors.append(
                    f"HTML_SECTION_MISMATCH: preview.html has {sections} "
                    f"<section> but the Markdown implies {slide_count} slide(s). "
                    f"Re-render before visual inspection."
                )

    # --- Report ------------------------------------------------------------
    print(f"[post-edit-check] {md_path}")
    print(f"  slides detected: {slide_count}")
    print(f"  language check: {lang or 'skipped (pass --lang ja|zh to enable)'}")
    for w in warnings:
        print(f"  [WARN ] {w}")
    for e in errors:
        print(f"  [ERROR] {e}")

    if errors:
        print(f"  RESULT: FAIL ({len(errors)} error(s))")
        return 1
    print("  RESULT: OK" + (" (with warnings)" if warnings else ""))
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Post-edit sanity checks for Marp Markdown.")
    p.add_argument("markdown", type=Path, help="Path to the .md file")
    p.add_argument(
        "--expect", type=int, default=None, help="Expected number of slides (e.g. from the approved outline)"
    )
    p.add_argument(
        "--html", type=Path, default=None, help="Optional rendered preview.html to cross-check <section> count"
    )
    p.add_argument(
        "--lang",
        choices=["ja", "zh"],
        default=None,
        help="Expected deck language; enables the contamination check "
        "(ja: flag simplified-Chinese, zh: flag kana). "
        "Omit to skip language checking (e.g. English decks).",
    )
    args = p.parse_args(argv)

    if not args.markdown.exists():
        print(f"[ERROR] Not found: {args.markdown}")
        return 1
    return check(args.markdown, args.expect, args.html, args.lang)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
