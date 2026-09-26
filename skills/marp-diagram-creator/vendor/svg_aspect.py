"""svg_aspect.py — Canvas aspect-ratio control for slide diagrams.

Three ways to declare a target canvas ratio (width / height):

- JSON source: ``{"aspect": 2.4}`` (resolved in ``diagram_models.parse_diagram_data``).
- Mermaid source: a ``%% aspect: 16:9`` comment directive.
- CLI: ``render-slide-diagram.py --aspect 16:9`` (or ``2.4``; overrides sources).

JSON diagrams reflow directly (``height = width / aspect``). Mermaid and
draw.io engines pick their own geometry, so their finished SVG is *padded*
to the target ratio: the viewBox grows along exactly one axis and its origin
shifts to keep the content centered. Content is never scaled or cropped.
Padding is rejected when the padded canvas would exceed
``layout_spec.VALIDATOR_LIMITS`` for the layout — the feasible ratio range
is part of the error message. The recommended aspect *band* stays a
validator warning (with an actionable hint), not a render error.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from layout_spec import VALIDATOR_LIMITS  # noqa: E402  (path setup above)

# ``%% aspect: 2.4`` / ``%%aspect=16:9`` — first token after the marker.
ASPECT_DIRECTIVE_RE = re.compile(r"^\s*%%\s*aspect\s*[:=]\s*(\S+)", re.MULTILINE)
_SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)
_VIEWBOX_RE = re.compile(r"""viewBox\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
_MAXWIDTH_RE = re.compile(r"(max-width\s*:\s*)[\d.]+")


def parse_aspect(value: object) -> float:
    """Parse ``2.4`` or ``16:9`` into a positive finite width/height ratio."""
    if isinstance(value, bool) or value is None:
        raise ValueError("aspect must be a number or a W:H ratio like '16:9'")
    if isinstance(value, (int, float)):
        ratio = float(value)
    elif isinstance(value, str):
        text = value.strip()
        if ":" in text:
            parts = text.split(":")
            if len(parts) != 2:
                raise ValueError(f"aspect '{value}' must look like 2.4 or 16:9")
            try:
                width_part = float(parts[0].strip())
                height_part = float(parts[1].strip())
            except ValueError as error:
                raise ValueError(f"aspect '{value}' must look like 2.4 or 16:9") from error
            if height_part == 0:
                raise ValueError("aspect ratio denominator must not be zero")
            ratio = width_part / height_part
        else:
            try:
                ratio = float(text)
            except ValueError as error:
                raise ValueError(
                    f"aspect '{value}' must be a number or a W:H ratio like '16:9'"
                ) from error
    else:
        raise ValueError("aspect must be a number or a W:H ratio like '16:9'")
    if not math.isfinite(ratio) or ratio <= 0:
        raise ValueError(f"aspect must be a positive finite number (got {value!r})")
    return ratio


def extract_mermaid_aspect(source: str) -> float | None:
    """Return the ratio from an ``%% aspect: 16:9`` directive, or None.

    Raises ValueError when the directive is present but its value is invalid.
    """
    match = ASPECT_DIRECTIVE_RE.search(source)
    if not match:
        return None
    return parse_aspect(match.group(1))


def feasible_aspect_range(width: float, height: float, layout: str = "full") -> tuple[float, float]:
    """Ratios reachable by padding ``width``×``height`` content in ``layout``.

    Returns ``(min, max)``. Raises ValueError when the content itself already
    exceeds the layout canvas (no ratio can rescue that).
    """
    limits = VALIDATOR_LIMITS.get(layout, VALIDATOR_LIMITS["full"])
    if width <= 0 or height <= 0:
        raise ValueError("SVG canvas dimensions must be positive")
    if width > limits["max_w"] or height > limits["max_h"]:
        raise ValueError(
            f"content ({width:.0f}x{height:.0f}px) already exceeds the '{layout}' canvas "
            f"({limits['max_w']}x{limits['max_h']}px); padding cannot fix it"
        )
    # Taller padding bounded by max_h -> A >= w / max_h; wider padding bounded
    # by max_w -> A <= max_w / h. Content fits, so lo <= hi always holds.
    return width / limits["max_h"], limits["max_w"] / height


def check_aspect_feasible(
    aspect: float, width: float, height: float, layout: str = "full"
) -> str | None:
    """Return an error message when ``aspect`` is unreachable by padding."""
    try:
        low, high = feasible_aspect_range(width, height, layout)
    except ValueError as error:
        return str(error)
    if not (low - 1e-9 <= aspect <= high + 1e-9):
        limits = VALIDATOR_LIMITS.get(layout, VALIDATOR_LIMITS["full"])
        return (
            f"aspect {aspect:.2f} is not reachable by padding {width:.0f}x{height:.0f}px content "
            f"within the '{layout}' canvas ({limits['max_w']}x{limits['max_h']}px); "
            f"feasible range: {low:.2f}-{high:.2f}"
        )
    return None


def _fmt(value: float) -> str:
    # 10 significant digits keeps target ratios exact enough that the padded
    # canvas re-validates without float-rounding aspect-band warnings.
    return f"{value:.10g}"


def _attr_number(tag: str, name: str) -> float | None:
    match = re.search(rf"""(?<![\w-]){name}\s*=\s*(["'])([^"']*)\1""", tag, re.IGNORECASE)
    if not match:
        return None
    number = re.fullmatch(r"\s*([+-]?[\d.]+)\s*(px|pt)?\s*", match.group(2))
    return float(number.group(1)) if number else None


def _set_dim(tag: str, name: str, value: float) -> str:
    """Rewrite a numeric ``width=``/``height=`` attr; leave percentages alone."""
    pattern = re.compile(rf"""(?<![\w-]){name}\s*=\s*(["'])([^"']*)\1""", re.IGNORECASE)

    def replace(match: re.Match[str]) -> str:
        number = re.fullmatch(r"\s*(\d+(?:\.\d+)?)(px|pt)?\s*", match.group(2))
        if not number:  # "100%" and friends keep their intrinsic-scaling meaning
            return match.group(0)
        unit = number.group(2) or ""
        return f"{name}={match.group(1)}{_fmt(value)}{unit}{match.group(1)}"

    return pattern.sub(replace, tag, count=1)


def pad_viewbox(svg_text: str, aspect: object, layout: str = "full") -> str:
    """Pad the root viewBox so the canvas matches ``aspect`` (content centered).

    Only the root ``<svg>`` tag is touched: ``viewBox``, numeric ``width`` /
    ``height`` attributes, and a ``max-width: Npx`` sizing hint. Content markup
    is never scaled or cropped. Raises ValueError when the target ratio is
    not reachable within ``layout_spec.VALIDATOR_LIMITS`` for ``layout``.
    """
    target = parse_aspect(aspect)
    root_match = _SVG_OPEN_RE.search(svg_text)
    if not root_match:
        raise ValueError("SVG root element not found; cannot pad viewBox")
    tag = root_match.group(0)

    view_box: list[float]
    box_match = _VIEWBOX_RE.search(tag)
    if box_match:
        parts = [float(p) for p in box_match.group(1).replace(",", " ").split() if p.strip()]
        if len(parts) != 4:
            raise ValueError(f"malformed viewBox '{box_match.group(1)}'")
        view_box = parts
    else:
        width_attr = _attr_number(tag, "width")
        height_attr = _attr_number(tag, "height")
        if width_attr is None or height_attr is None:
            raise ValueError(
                "SVG has neither a viewBox nor numeric width/height; cannot pad canvas"
            )
        view_box = [0.0, 0.0, width_attr, height_attr]

    min_x, min_y, width, height = view_box
    problem = check_aspect_feasible(target, width, height, layout)
    if problem is not None:
        raise ValueError(problem)

    if abs(width / height - target) <= 1e-9:
        return svg_text  # already at the requested ratio

    if target > width / height:
        new_width, new_height = height * target, height
    else:
        new_width, new_height = width, width / target

    new_min_x = min_x - (new_width - width) / 2
    new_min_y = min_y - (new_height - height) / 2
    new_box = f"{_fmt(new_min_x)} {_fmt(new_min_y)} {_fmt(new_width)} {_fmt(new_height)}"

    if box_match:
        new_tag = _VIEWBOX_RE.sub(lambda _m: f'viewBox="{new_box}"', tag, count=1)
    else:
        new_tag = _SVG_OPEN_RE.sub(
            lambda m: m.group(0)[:-1] + f' viewBox="{new_box}">', tag, count=1
        )
    new_tag = _set_dim(new_tag, "width", new_width)
    new_tag = _set_dim(new_tag, "height", new_height)
    # Mermaid sizes its root via style="max-width: Npx" — keep it in sync.
    new_tag = _MAXWIDTH_RE.sub(lambda m: f"{m.group(1)}{_fmt(new_width)}", new_tag, count=1)

    return svg_text[: root_match.start()] + new_tag + svg_text[root_match.end() :]
