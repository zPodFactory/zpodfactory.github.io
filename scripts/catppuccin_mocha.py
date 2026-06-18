"""Catppuccin Mocha palette for zcli terminal SVG screenshots.

Used by prepare_zcli_svgs.py to recolor Rich terminal exports so CLI
screenshots match the site's dark (slate) theme.
"""

from __future__ import annotations

# Palette reference: https://catppuccin.com/palette (Mocha)
BASE = "#1e1e2e"
TEXT = "#cdd6f4"
BLUE = "#89b4fa"
SKY = "#89dceb"
TEAL = "#94e2d5"
GREEN = "#a6e3a1"
YELLOW = "#f9e2af"
PEACH = "#fab387"
RED = "#f38ba8"
PINK = "#f5c2e7"
MAUVE = "#cba6f7"
SUBTEXT0 = "#a6adc8"

# Rich DIMMED_MONOKAI (and legacy exports) -> Catppuccin Mocha.
ZCLI_COLOR_REMAP: dict[str, str] = {
    "#191919": BASE,
    "#b9bcba": TEXT,
    "#578fa4": BLUE,
    "#d7d700": YELLOW,
    "#af87ff": MAUVE,
    "#5f87ff": BLUE,
    "#879a3b": SUBTEXT0,
    "#5faf5f": GREEN,
    "#87afff": BLUE,
    "#d7af87": PEACH,
    "#afaf5f": YELLOW,
    "#ffafaf": RED,
    "#afd7d7": TEAL,
    "#855c8d": MAUVE,
    "#d75f5f": RED,
    "#af87af": PINK,
    "#005fff": BLUE,
    "#00afff": SKY,
    "#00ff87": GREEN,
    "#ff5f57": RED,
    "#febc2e": PEACH,
    "#28c840": GREEN,
}

_ZCLI_REMAP: dict[str, str] = {}
for src, dst in ZCLI_COLOR_REMAP.items():
    _ZCLI_REMAP[src.lower()] = dst
    _ZCLI_REMAP[src.upper()] = dst


def apply_zcli_theme(svg: str) -> str:
    """Replace legacy Rich terminal hex colors with Catppuccin Mocha."""
    for src, dst in _ZCLI_REMAP.items():
        svg = svg.replace(src, dst)
    return svg
