"""Regenerate the zPod component FQDN diagrams.

Writes two self-contained SVGs to docs/img/, embedded from the guides like any
other image:

  zpod_component_fqdn.svg            -- anatomy only: how zPodFactory builds
                                        <hostname>.<zPod name>.<default domain>
  zpodfactory_fqdn_reserved_chars.svg -- the same anatomy plus the 64-character
                                        hostname budget and accept/reject examples

Colors are the Catppuccin Mocha palette on a dark base (same convention as the
zcli terminal screenshots), so they read well on both site schemes. Run after
changing the example FQDN, the limit, or the layout:

    python scripts/gen_fqdn_diagram.py
"""
import html
import pathlib

from catppuccin_mocha import BASE, BLUE, GREEN, MAUVE, PEACH, RED, SUBTEXT0, TEXT

OVERLAY1 = "#7f849c"
SURFACE1 = "#45475a"

HOST, ZPOD, DOM = "very-long-hostname", "very-long-subdomain", "very-long-domain.internal"
FQDN = f"{HOST}.{ZPOD}.{DOM}"
LIMIT, RESERVED = 64, 8
ALLOWED = LIMIT - RESERVED
OK_FQDN = "esxi11.lab01.zpodfactory.io"
assert len(FQDN) == LIMIT

CW = 11  # px per character; textLength pins every run to the grid whatever font renders it
X0 = 34
W = X0 * 2 + LIMIT * CW
MONO = '"Fira Code", "JetBrains Mono", Menlo, Consolas, monospace'
SANS = 'Roboto, "Helvetica Neue", Arial, sans-serif'
SUB, OVL, SURF = SUBTEXT0, OVERLAY1, SURFACE1

IMG = pathlib.Path(__file__).resolve().parent.parent / "docs/img"


def cx(i):
    """x of character index i (left edge)."""
    return X0 + i * CW


def seg(a, n):
    """x-span of n characters starting at index a."""
    return cx(a), cx(a + n)


class Canvas:
    def __init__(self, height, label):
        self.h = height
        self.out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" role="img" '
            f'aria-label="{html.escape(label)}">',
            f'<rect width="{W}" height="{height}" rx="8" fill="{BASE}"/>',
        ]

    def P(self, s):
        self.out.append(s)

    def mono(self, x, y, s, fill=TEXT, size=17, anchor="start", weight="normal", length=None):
        tl = f' textLength="{length}" lengthAdjust="spacingAndGlyphs"' if length else ""
        self.P(f'<text x="{x}" y="{y}" font-family=\'{MONO}\' font-size="{size}" fill="{fill}" '
               f'text-anchor="{anchor}" font-weight="{weight}"{tl}>{html.escape(s)}</text>')

    def sans(self, x, y, s, fill=TEXT, size=12.5, anchor="middle", weight="normal"):
        self.P(f'<text x="{x}" y="{y}" font-family=\'{SANS}\' font-size="{size}" fill="{fill}" '
               f'text-anchor="{anchor}" font-weight="{weight}">{html.escape(s)}</text>')

    def brace(self, x1, x2, y, color, up=False, h=9):
        """Square bracket with a centre tick; opens downwards unless up=True."""
        d = -h if up else h
        mid = (x1 + x2) / 2
        self.P(f'<path d="M{x1},{y} v{d} H{x2} v{-d} M{mid},{y + d} v{d}" fill="none" stroke="{color}" '
               f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')

    def write(self, name):
        self.P("</svg>")
        svg = "\n".join(self.out) + "\n"
        (IMG / name).write_text(svg)
        print(f"wrote docs/img/{name}: {len(svg)} bytes")


def part_anatomy(c, y, title):
    """The FQDN with its three bracketed parts. `y` is the FQDN baseline."""
    c.sans(X0, y - 82, title, SUB, 12, "start", "bold")

    za, zb = seg(len(HOST) + 1, len(ZPOD) + 1 + len(DOM))
    c.brace(za, zb, y - 30, PEACH, up=True)
    c.sans((za + zb) / 2, y - 50,
           f"zPod domain  ·  <zPod name>.<default domain>  ·  {len(ZPOD) + 1 + len(DOM)} chars", PEACH)

    i = 0
    for s, col in [(HOST, BLUE), (".", OVL), (ZPOD, GREEN), (".", OVL), (DOM, MAUVE)]:
        c.mono(cx(i), y, s, col, weight="bold" if s != "." else "normal", length=len(s) * CW)
        i += len(s)

    for a, n, label, col in [(0, len(HOST), "component hostname", BLUE),
                             (len(HOST) + 1, len(ZPOD), "zPod name", GREEN),
                             (len(HOST) + len(ZPOD) + 2, len(DOM), "zpodfactory_default_domain", MAUVE)]:
        x1, x2 = seg(a, n)
        c.brace(x1, x2, y + 10, col)
        m = (x1 + x2) / 2
        c.sans(m, y + 44, label, col, weight="bold")
        c.sans(m, y + 60, f"{n} chars", SUB, 11.5)
    c.sans(cx(LIMIT), y + 82, f"{len(HOST)} + 1 + {len(ZPOD)} + 1 + {len(DOM)}  =  {len(FQDN)} characters",
           TEXT, 12.5, "end")


def part_budget(c, y):
    """The 64-character hostname budget ruler. `y` is the bar's vertical centre."""
    c.sans(X0, y - 32, "2. The hostname length budget checked at POST /zpods", SUB, 12, "start", "bold")
    c.P('<defs><pattern id="fqdn-hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
        f'patternTransform="rotate(45)"><rect width="6" height="6" fill="{RED}" opacity="0.18"/>'
        f'<line x1="0" y1="0" x2="0" y2="6" stroke="{RED}" stroke-width="2" opacity="0.6"/></pattern></defs>')
    ax1, ax2 = seg(0, ALLOWED)
    rx1, rx2 = seg(ALLOWED, RESERVED)
    c.P(f'<rect x="{ax1}" y="{y - 10}" width="{ax2 - ax1}" height="20" rx="4" fill="{GREEN}" opacity="0.22"/>')
    c.P(f'<rect x="{rx1}" y="{y - 10}" width="{rx2 - rx1}" height="20" rx="4" fill="url(#fqdn-hatch)"/>')
    c.P(f'<rect x="{ax1}" y="{y - 10}" width="{rx2 - ax1}" height="20" rx="4" fill="none" stroke="{SURF}" stroke-width="1"/>')
    c.P(f'<line x1="{rx1}" y1="{y - 10}" x2="{rx1}" y2="{y + 10}" stroke="{RED}" stroke-width="1.6"/>')
    c.sans((ax1 + ax2) / 2, y + 4.5, f"allowed  ·  {ALLOWED} characters  ( {LIMIT} − {RESERVED} )", GREEN, 12, weight="bold")
    for n in (0, ALLOWED, LIMIT):
        x = cx(n)
        c.P(f'<line x1="{x}" y1="{y + 10}" x2="{x}" y2="{y + 16}" stroke="{OVL}" stroke-width="1.2"/>')
        c.mono(x, y + 30, str(n), SUB, 11.5, "middle")
    c.sans(rx2, y - 18, f"reserved margin  ·  {RESERVED}", RED, 12, "end", "bold")
    c.mono(rx2, y + 48, f"zpodfactory_fqdn_reserved_chars = {RESERVED}", RED, 11.5, "end")
    c.sans(cx(0), y + 48, f"Linux kernel hostname limit (sethostname / hostnamectl) = {LIMIT}", SUB, 11.5, "start")


def part_result(c, y):
    """Two candidate FQDNs measured against the budget. `y` is the first bar's centre."""
    c.sans(X0, y - 26, "3. Result", SUB, 12, "start", "bold")

    def candidate(y, fqdn, ok):
        n = len(fqdn)
        x1, x2 = seg(0, n)
        col = GREEN if ok else RED
        if ok:
            c.P(f'<rect x="{x1}" y="{y - 9}" width="{x2 - x1}" height="18" rx="3" fill="{GREEN}" opacity="0.28"/>')
        else:
            c.P(f'<rect x="{x1}" y="{y - 9}" width="{cx(ALLOWED) - x1}" height="18" rx="3" fill="{GREEN}" opacity="0.28"/>')
            c.P(f'<rect x="{cx(ALLOWED)}" y="{y - 9}" width="{x2 - cx(ALLOWED)}" height="18" fill="{RED}" opacity="0.45"/>')
        c.P(f'<rect x="{x1}" y="{y - 9}" width="{x2 - x1}" height="18" rx="3" fill="none" stroke="{col}" stroke-width="1.2"/>')
        c.mono(x1 + 6, y + 4, fqdn, TEXT, 11.5)
        if ok:
            c.sans(x2 + 10, y + 4, f"{n} ≤ {ALLOWED}  ✓ accepted", GREEN, 12, "start", "bold")
        else:
            c.P(f'<rect x="{cx(LIMIT) - 232}" y="{y - 9}" width="226" height="18" rx="3" fill="{BASE}" opacity="0.85"/>')
            c.sans(cx(LIMIT) - 6, y + 4, f"{n} > {ALLOWED}  ✗ rejected  (HTTP 400)", RED, 12, "end", "bold")

    candidate(y, OK_FQDN, True)
    candidate(y + 32, FQDN, False)


# --- anatomy only -----------------------------------------------------------
c = Canvas(222, "How zPodFactory builds a zPod component FQDN")
part_anatomy(c, 112, "How zPodFactory builds the FQDN of every zPod component")
c.write("zpod_component_fqdn.svg")

# --- full explainer for zpodfactory_fqdn_reserved_chars ---------------------
c = Canvas(414, "How zpodfactory_fqdn_reserved_chars limits a zPod component FQDN")
part_anatomy(c, 112, "1. The FQDN zPodFactory builds for every component")
part_budget(c, 250)
part_result(c, 352)
c.write("zpodfactory_fqdn_reserved_chars.svg")
