from __future__ import annotations

from typing import Any


def shadow_filter_def(effects: dict[str, Any]) -> str | None:
    if not effects.get("nodeShadowEnabled"):
        return None
    color = effects.get("nodeShadowColor", "rgba(0, 0, 0, 0.08)")
    blur = effects.get("nodeShadowBlur", 12)
    offset_y = effects.get("nodeShadowOffsetY", 4)
    return (
        f'<filter id="theme-shadow" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="{offset_y}" stdDeviation="{blur / 2:.1f}" flood-color="{color}"/>'
        f"</filter>"
    )


def glow_filter_def(effects: dict[str, Any]) -> str | None:
    if not effects.get("glowEnabled") or not effects.get("glowColor"):
        return None
    color = effects["glowColor"]
    blur = effects.get("glowBlur", 10)
    return (
        f'<filter id="theme-glow" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur stdDeviation="{blur / 2:.1f}" result="blur"/>'
        f'<feFlood flood-color="{color}" flood-opacity="0.55" result="color"/>'
        f'<feComposite in="color" in2="blur" operator="in" result="glow"/>'
        f'<feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f"</filter>"
    )


def build_filter_defs(effects: dict[str, Any]) -> str:
    parts = [part for part in (shadow_filter_def(effects), glow_filter_def(effects)) if part]
    if not parts:
        return ""
    return f"<defs>{''.join(parts)}</defs>"
