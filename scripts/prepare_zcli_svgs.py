#!/usr/bin/env python3
"""Prepare the Rich/Textual terminal SVGs (`zcli_*.svg`) for static hosting.

These screenshots are Rich terminal exports. Two things make them misbehave when
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
    """Add intrinsic width/height (from viewBox) to the root <svg> if missing.

    A `<img>`-referenced SVG with only a viewBox has no natural size, which makes
    GLightbox render it tiny. Setting width/height gives it an intrinsic size;
    on the page Material's `max-width: 100%` still scales it to the column.
    """
    m = SVG_TAG_RE.search(svg)
    if not m:
        return svg
    tag = m.group(0)
    if re.search(r'\bwidth="', tag):  # already sized
        return svg
    vb = VIEWBOX_RE.search(tag)
    if not vb:
        return svg
    w = round(float(vb.group(1)))
    h = round(float(vb.group(2)))
    new_tag = tag[:-1] + f' width="{w}" height="{h}">'
    return svg[: m.start()] + new_tag + svg[m.end():]


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

    fonts_changed = dims_changed = 0
    for path in svg_paths:
        data = open(path, encoding="utf-8").read()
        new = data
        for name, replacement in embedded.items():
            new = SRC_RE[name].sub(replacement, new)
        if new != data:
            fonts_changed += 1
        sized = add_dimensions(new)
        if sized != new:
            dims_changed += 1
        new = sized
        if new != data:
            open(path, "w", encoding="utf-8").write(new)
    print(f"Embedded font into {fonts_changed} SVG(s); added dimensions to {dims_changed} SVG(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
