#!/usr/bin/env python3
"""Prepare the Rich/Textual terminal SVGs (`zcli_*.svg`) for static hosting.

These screenshots are Rich terminal exports. The script also recolors `zcli_*.svg` screenshots to the Catppuccin Mocha palette used by the site theme.

Two things make them misbehave when
referenced as plain `<img>` (which is how the docs use them now that the
inline-select-svg MkDocs plugin is gone, since Zensical has no plugin support):

1. Font: they reference Fira Code via an external Cloudflare `@font-face`. An
   `<img>`-loaded SVG is sandboxed and cannot fetch that font, so text falls back
   to a generic monospace and the box-drawing / TUI layout misaligns. We fix this
   by embedding Fira Code (Regular + Bold), subset to the glyphs actually used,
   as `data:` URIs so each SVG renders with the correct font, offline.

2. Size: they carry a `viewBox` but no intrinsic `width`/`height`. Without those,
   the GLightbox lightbox cannot determine their natural size and renders them
   tiny. We add `width`/`height` from the `viewBox` so they size correctly both
   on the page and in the lightbox.

Idempotent: re-running re-embeds a freshly subset font and re-asserts dimensions.

Usage:  python scripts/prepare_zcli_svgs.py
Requires: fonttools, brotli  (pip install fonttools brotli)
"""
from __future__ import annotations

import base64
import glob
import html
import io
import os
import re
import sys
import urllib.request

from fontTools import subset
from fontTools.ttLib import TTFont

from catppuccin_mocha import apply_zcli_theme

SVG_GLOB = os.path.join(os.path.dirname(__file__), "..", "docs", "img", "zcli_*.svg")

FONTS = {
    "FiraCode-Regular": "https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2",
    "FiraCode-Bold": "https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2",
}

# Match a full `src: local("FiraCode-XXX") ... ;` declaration. The src value
# never contains a semicolon, so `[^;]*` safely captures the whole list.
SRC_RE = {
    name: re.compile(r'src:\s*local\("' + re.escape(name) + r'"\)[^;]*;')
    for name in FONTS
}

TEXT_RE = re.compile(r"<text[^>]*>(.*?)</text>", re.S)
TAG_RE = re.compile(r"<[^>]+>")

# Root <svg ...> opening tag and its viewBox.
SVG_TAG_RE = re.compile(r"<svg\b[^>]*>")
VIEWBOX_RE = re.compile(r'viewBox="\s*[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)\s*"')

TERMINAL_TEXT_RE = re.compile(
    r'<text[^>]*class="(terminal-\d+-r(\d))"[^>]*x="([\d.]+)"[^>]*y="([\d.]+)"'
    r'(?:[^>]*textLength="([\d.]+)")?[^>]*>([^<]*)</text>'
)
TERMINAL_LINE_HEIGHT = 24.4
TERMINAL_TRIM_PAD = 18
# Rich terminal chrome layout (matches save_svg output).
TERMINAL_CONTENT_X = 9
TERMINAL_CONTENT_Y = 41
TERMINAL_HORIZONTAL_PAD = 10
TERMINAL_BOTTOM_PAD = 10

WINDOW_FRAME_RE = re.compile(
    r'(<rect fill="#(?:1e1e2e|191919)" stroke="rgba\(255,255,255,0\.35\)" '
    r'stroke-width="1" x="1" y="1" width=")[^"]+(" height=")[^"]+(" rx="8"/>)'
)
CLIP_TERMINAL_RE = re.compile(
    r'(<clipPath id="terminal-\d+-clip-terminal">\s*'
    r'<rect x="0" y="0" width=")[^"]+(" height=")[^"]+(" />)'
)


def content_bounds(svg: str) -> tuple[int, int] | None:
    """Return (width, height) for the terminal table content area."""
    max_x = max_y = 0.0
    min_y = float("inf")
    found = False
    for m in TERMINAL_TEXT_RE.finditer(svg):
        rnum = int(m.group(2))
        if rnum == 1:
            continue  # title padding spans the full terminal width
        text = html.unescape(m.group(6))
        if not text.strip():
            continue
        x = float(m.group(3))
        y = float(m.group(4))
        text_len = float(m.group(5) or 12.2)
        found = True
        max_x = max(max_x, x + text_len)
        min_y = min(min_y, y)
        max_y = max(max_y, y + TERMINAL_LINE_HEIGHT)
    if not found:
        return None
    return round(max_x + TERMINAL_TRIM_PAD), round(max_y + TERMINAL_TRIM_PAD)


def fit_svg_to_content(svg: str) -> str:
    """Crop SVG viewBox (and intrinsic size) to the rendered table bounds."""
    bounds = content_bounds(svg)
    if not bounds:
        return svg
    w, h = bounds
    m = SVG_TAG_RE.search(svg)
    if not m:
        return svg
    tag = m.group(0)
    tag = VIEWBOX_RE.sub(f'viewBox="0 0 {w} {h}"', tag)
    if re.search(r'\bwidth="', tag):
        tag = re.sub(r'\bwidth="[^"]*"', f'width="{w}"', tag)
        tag = re.sub(r'\bheight="[^"]*"', f'height="{h}"', tag)
    else:
        tag = tag[:-1] + f' width="{w}" height="{h}">'
    svg = svg[: m.start()] + tag + svg[m.end():]
    return resize_terminal_chrome(svg, w, h)


def resize_terminal_chrome(svg: str, width: int, height: int) -> str:
    """Shrink the fake terminal window frame to match a trimmed viewBox."""
    frame_w = max(width - 2, 1)
    frame_h = max(height - 2, 1)
    clip_w = max(width - TERMINAL_CONTENT_X - TERMINAL_HORIZONTAL_PAD, 1)
    clip_h = max(height - TERMINAL_CONTENT_Y - TERMINAL_BOTTOM_PAD, 1)

    svg = WINDOW_FRAME_RE.sub(
        rf"\g<1>{frame_w}\g<2>{frame_h}\g<3>",
        svg,
        count=1,
    )
    svg = CLIP_TERMINAL_RE.sub(
        rf"\g<1>{clip_w}\g<2>{clip_h}\g<3>",
        svg,
        count=1,
    )
    return svg


LICENSE_KEY_RE = re.compile(r"[A-Z0-9]{4,5}(?:-[A-Z0-9]{4,5}){4}")
LICENSE_KEY_PARTIAL_RE = re.compile(
    r"XXXXX-XXXXX-XXXXX-XXXXX-XXXXX(?:…)?(?:-[A-Z0-9]{4,5})+"
)
OBFUSCATED_LICENSE = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
OBFUSCATED_SSH = "ssh-rsa XXXXXXXX… root@zPodMaster"
OBFUSCATED_SSH_TEXT_LENGTH = "439.2"  # ~12.2px per glyph in Rich SVG exports
SSH_KEY_VALUE_RE = re.compile(r"ssh-rsa(?:&#160;|\s)+AAA[A-Za-z0-9+/=&#;…]+")


OBFUSCATED_PASSWORD = "************"
ZPOD_PASSWORD_RE = re.compile(r"(?<=>)[A-Za-z0-9!]{14,18}(?=</text>)")


def _redact_zpod_passwords(svg: str) -> str:
    def repl(match: re.Match[str]) -> str:
        value = match.group(0)
        if "!" not in value or value.startswith("*"):
            return value
        return OBFUSCATED_PASSWORD

    return ZPOD_PASSWORD_RE.sub(repl, svg)



RICH_GLYPH_WIDTH = 12.2
TEXT_WITH_LENGTH_RE = re.compile(
    r'(<text\b[^>]*textLength=")([\d.]+)("[^>]*>)([^<]*)(</text>)'
)


def fix_text_lengths(svg: str) -> str:
    """Recompute textLength when redaction shortened visible text."""

    def repl(match: re.Match[str]) -> str:
        prefix, old_length, middle, content, suffix = match.groups()
        visible = html.unescape(content).replace("\u00a0", " ")
        if not visible.strip():
            return match.group(0)
        expected = len(visible) * RICH_GLYPH_WIDTH
        if float(old_length) > expected * 1.05 or float(old_length) < expected * 0.95:
            return f"{prefix}{expected:.1f}{middle}{content}{suffix}"
        return match.group(0)

    return TEXT_WITH_LENGTH_RE.sub(repl, svg)


# Intentionally left as captured from zcli (no redaction).
UNSANITIZED_SVGS = frozenset({
    "zcli_endpoint_list.svg",
    "zcli_user_list.svg",
    "zcli_zpod_list.svg",
})

def sanitize_zcli_svg(svg: str, filename: str) -> str:
    """Redact secrets and lab-specific identifiers from zcli SVG exports."""
    svg = LICENSE_KEY_RE.sub(OBFUSCATED_LICENSE, svg)
    svg = LICENSE_KEY_PARTIAL_RE.sub(OBFUSCATED_LICENSE, svg)
    svg = SSH_KEY_VALUE_RE.sub(OBFUSCATED_SSH, svg)
    svg = _redact_zpod_passwords(svg)

    svg = re.sub(r"pcc-\d+-\d+-\d+-\d+\.ovh\.com", "pcc-example.ovh.com", svg)
    svg = re.sub(r"pcc-\d+-\d+-\d+-\d+_datacenter\d+", "pcc-example_datacenter1", svg)
    svg = re.sub(
        r"zpodfactory@pcc-[^<]+\.ovh\.com",
        "zpodfactory@pcc-example.ovh.com",
        svg,
    )

    svg = svg.replace("tsugliani@z42.sh", "user@example.com")
    svg = svg.replace(">tsugliani<", ">example-user<")
    svg = svg.replace("ff_max_zpods_tsugliani", "ff_max_zpods_example")
    svg = svg.replace("for&#160;tsugliani", "for&#160;example-user")
    svg = svg.replace("french&#160;dude", "example&#160;user")
    svg = svg.replace(">gcarsso<", ">example<")
    svg = svg.replace("172.16.42.12", "10.10.10.10")
    svg = svg.replace("10.60.151.0/24", "10.10.151.0/24")
    svg = svg.replace("10.60.126.2", "10.10.126.2")
    svg = svg.replace("10.60.126.0", "10.10.126.0")
    svg = svg.replace("10.60.0.0/16", "10.10.0.0/16")

    if filename.endswith("zcli_setting_list.svg"):
        svg = re.sub(
            r'(class="[^"]*-r4"[^>]*>license_[^<]+</text>(?:<text[^>]+>[^<]*</text>)*?'
            r'class="[^"]*-r5"[^>]*>)[^<]+(</text>)',
            rf"\1{OBFUSCATED_LICENSE}\2",
            svg,
        )
        svg = re.sub(
            r'(class="[^"]*-r4"[^>]*>zpodfactory_ssh_key</text>(?:<text[^>]+>[^<]*</text>)*?'
            r'class="[^"]*-r5"[^>]*x="[\d.]+"[^>]*y="[\d.]+" )textLength="[\d.]+"'
            rf'([^>]*>)ssh-rsa[^<]*(</text>)',
            rf'\1textLength="{OBFUSCATED_SSH_TEXT_LENGTH}"\2{OBFUSCATED_SSH}\3',
            svg,
            count=1,
        )

    svg = fix_text_lengths(svg)
    return svg


def sanitize_zcli_svgs(svg_paths: list[str]) -> int:
    changed = 0
    for path in svg_paths:
        basename = os.path.basename(path)
        if not basename.startswith("zcli_"):
            continue
        if basename in UNSANITIZED_SVGS:
            continue
        data = open(path, encoding="utf-8").read()
        new = sanitize_zcli_svg(data, basename)
        if path.endswith("zcli_setting_list.svg"):
            new = fit_svg_to_content(new)
        if new != data:
            open(path, "w", encoding="utf-8").write(new)
            changed += 1
    return changed


def used_codepoints(svg_paths: list[str]) -> set[int]:
    """Collect every character that appears inside <text> elements."""
    chars: set[int] = set()
    for path in svg_paths:
        data = open(path, encoding="utf-8").read()
        for chunk in TEXT_RE.findall(data):
            chunk = TAG_RE.sub("", chunk)        # strip nested <tspan> etc.
            chunk = html.unescape(chunk)         # &#160; -> char
            chars.update(ord(c) for c in chunk)
    # Always include printable ASCII and the full box-drawing + block ranges so
    # any terminal art renders, even glyphs not seen in the current screenshots.
    chars.update(range(0x20, 0x7F))
    chars.update(range(0x2500, 0x25A0))
    return chars


def subset_font_b64(url: str, codepoints: set[int]) -> str:
    """Download a woff2 font, subset it to `codepoints`, return base64 woff2."""
    raw = urllib.request.urlopen(url, timeout=60).read()
    font = TTFont(io.BytesIO(raw))
    options = subset.Options()
    options.flavor = "woff2"
    options.desubroutinize = True
    options.layout_features = ["*"]   # keep ligatures/box-drawing features
    options.notdef_outline = True
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=sorted(codepoints))
    subsetter.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def add_dimensions(svg: str) -> str:
    """Crop to table content and set intrinsic width/height for <img> embedding."""
    return fit_svg_to_content(svg)


def main() -> int:
    svg_paths = sorted(glob.glob(SVG_GLOB))
    if not svg_paths:
        print("No zcli_*.svg files found", file=sys.stderr)
        return 1

    codepoints = used_codepoints(svg_paths)
    print(f"{len(svg_paths)} SVGs, subsetting to {len(codepoints)} codepoints")

    embedded: dict[str, str] = {}
    for name, url in FONTS.items():
        b64 = subset_font_b64(url, codepoints)
        embedded[name] = (
            f'src: local("{name}"), '
            f'url("data:font/woff2;base64,{b64}") format("woff2");'
        )
        print(f"  {name}: {len(b64) * 3 // 4} bytes woff2 (subset)")

    fonts_changed = trimmed = dims_changed = 0
    for path in svg_paths:
        data = open(path, encoding="utf-8").read()
        new = data
        for name, replacement in embedded.items():
            new = SRC_RE[name].sub(replacement, new)
        if new != data:
            fonts_changed += 1
        sized = add_dimensions(new)
        if sized != new:
            trimmed += 1
        new = apply_zcli_theme(sized)
        if new != data:
            open(path, "w", encoding="utf-8").write(new)
    sanitized = sanitize_zcli_svgs(svg_paths)
    print(f"Embedded font into {fonts_changed} SVG(s); trimmed to content in {trimmed} SVG(s)")
    if sanitized:
        print(f"Sanitized secrets in {sanitized} zcli SVG(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
