"""Generate the zPodFactory architecture diagram (SVG): clients, the appliance's Docker Compose
services (zpodweb, zPod API, PostgreSQL, zPod Engine), the library volumes and the endpoints.

    python3 archdiagram.py OUT.svg            # today: every service publishes its own port
    python3 archdiagram.py OUT.svg traefik    # proposal: Traefik as the single entry point
"""
import sys

OUT = sys.argv[1]
TRAEFIK = len(sys.argv) > 2 and sys.argv[2] == 'traefik'
FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'JetBrains Mono', monospace"
NAVY, GREY, LINE, MUTED = "#12455F", "#777", "#C5CAD0", "#888"
DOMAIN = 'zpodfactory.fqdn.com'
P = []
add = P.append


def card(x, y, w, h, title, sub=None, accent=NAVY):
    """White card with a coloured accent bar on the left, a bold title and an optional subtitle."""
    add(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff" stroke="{LINE}"/>')
    add(f'  <rect x="{x}" y="{y}" width="6" height="{h}" rx="2" fill="{accent}"/>')
    add(f'  <text x="{x+22}" y="{y+30}" font-size="16" font-weight="700" fill="{NAVY}">{title}</text>')
    if sub:
        add(f'  <text x="{x+22}" y="{y+49}" font-size="12" fill="#666">{sub}</text>')


def port(x, y, text, internal=False):
    """Rounded pill on a card's top-right corner (x is the pill's right edge).
    A published port is solid navy; an internal one (behind Traefik) is grey and dashed."""
    w = len(text) * 7.5 + 20
    if internal:
        add(f'  <rect x="{x-w}" y="{y}" width="{w}" height="20" rx="10" fill="#fff" stroke="#9AA4AE" stroke-dasharray="3 2"/>')
        color = MUTED
    else:
        add(f'  <rect x="{x-w}" y="{y}" width="{w}" height="20" rx="10" fill="#EEF4F7" stroke="{NAVY}"/>')
        color = NAVY
    add(f'  <text x="{x-w/2}" y="{y+14}" text-anchor="middle" font-size="11.5" font-weight="700" font-family="{MONO}" fill="{color}">{text}</text>')


def tile(x, y, w, h, title, sub):
    """Solid navy tile: a service or a library inside a card."""
    add(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{NAVY}"/>')
    add(f'  <text x="{x+w/2}" y="{y+h/2-3}" text-anchor="middle" font-size="12.5" font-weight="700" fill="#fff">{title}</text>')
    add(f'  <text x="{x+w/2}" y="{y+h/2+14}" text-anchor="middle" font-size="11" font-family="{MONO}" fill="#BFD3E0">{sub}</text>')


def cylinder(cx, top, rx, ry, h, fill=NAVY, lid="#2E6E8C"):
    """Database drum: a solid body, a lighter lid and two white bands."""
    add(f'  <path d="M{cx-rx} {top} V{top+h} A{rx} {ry} 0 0 0 {cx+rx} {top+h} V{top} Z" fill="{fill}"/>')
    for k in (1, 2):
        yb = top + h * k / 3
        add(f'  <path d="M{cx-rx} {yb:.1f} A{rx} {ry} 0 0 0 {cx+rx} {yb:.1f}" stroke="#fff" stroke-width="1.5" fill="none"/>')
    add(f'  <ellipse cx="{cx}" cy="{top}" rx="{rx}" ry="{ry}" fill="{lid}" stroke="{fill}" stroke-width="1.5"/>')


def arrow(d, label=None, lx=0, ly=0, anchor="middle", both=False, dashed=False):
    dash = ' stroke-dasharray="3 4"' if dashed else ''
    start = ' marker-start="url(#ar)"' if both else ''
    add(f'  <path d="{d}" stroke="{GREY}" stroke-width="2.5" fill="none"{dash}{start} marker-end="url(#ar)"/>')
    if label:
        add(f'  <text x="{lx}" y="{ly}" text-anchor="{anchor}" font-size="11.5" fill="#555">{label}</text>')


def band_label(x, y, text):
    add(f'  <text x="{x}" y="{y}" font-size="11" font-weight="700" letter-spacing="0.5" fill="{MUTED}">{text}</text>')


def stack(x, y, w, h, name):
    """Dashed frame around the services of one Docker Compose project, its name as a legend."""
    add(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="#B9C0C8" stroke-width="1.5" stroke-dasharray="6 5"/>')
    lw = len(name) * 7 + 16
    add(f'  <rect x="{x+12}" y="{y-8}" width="{lw}" height="16" fill="#F7F8FA"/>')
    add(f'  <text x="{x+20}" y="{y+4}" font-size="10.5" font-weight="700" letter-spacing="0.4" fill="{MUTED}">{name}</text>')


# With Traefik, everything below the panel titles moves down by TY to free a band for Traefik and
# its routes, and the two routing options are drawn under the panels.
TY = 100 if TRAEFIK else 0
PANEL_H = 700 + TY
OPT_Y = 20 + PANEL_H + 40
W = 1600
H = OPT_Y + 240 if TRAEFIK else 20 + PANEL_H + 40
label = ('zPodFactory architecture with Traefik as the single entry point: the browser and zcli reach zpodweb, '
         'the zPod API and the Prefect UI through Traefik on port 443, by path or by host name'
         if TRAEFIK else
         'zPodFactory architecture: zcli and the browser call the zPod API; the API stores its data in PostgreSQL '
         'and schedules flows on the zPod Engine, whose worker runs each flow in its own container that reads the '
         'library volumes and deploys to the endpoints')
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" '
    f'role="img" aria-label="{label}">')
add('  <defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
    f'<path d="M0 0 L10 5 L0 10 z" fill="{GREY}"/></marker></defs>')
add(f'  <rect width="{W}" height="{H}" fill="#fff"/>')

# ---- Panels: your workstation and the appliance --------------------------------------------------
WX, WW = 30, 270
AX, AY, AW = 340, 20, 940
add(f'  <rect x="{WX}" y="20" width="{WW}" height="{PANEL_H}" rx="6" fill="#F7F8FA" stroke="#E3E6EA"/>')
band_label(WX + 16, 44, 'YOUR WORKSTATION')
add(f'  <rect x="{AX}" y="{AY}" width="{AW}" height="{PANEL_H}" rx="6" fill="#F7F8FA" stroke="#E3E6EA"/>')
band_label(AX + 16, AY + 24, 'ZPODFACTORY APPLIANCE')

if TY:
    add(f'  <g transform="translate(0 {TY})">')

# ---- Your workstation: browser and zcli --------------------------------------------------------
card(WX + 16, 90, WW - 32, 76, 'Web browser',
     f'https://{DOMAIN}' if TRAEFIK else 'zpodweb :8500 · Prefect UI :8060')
card(WX + 16, 300, WW - 32, 200, 'zcli', 'command line · Typer · Rich')
add(f'  <rect x="{WX+38}" y="362" width="{WW-76}" height="28" rx="4" fill="#F0F2F4"/>')
add(f'  <text x="{WX+48}" y="381" font-size="12.5" font-family="{MONO}" fill="#333">$ zcli zpod list</text>')
add(f'  <rect x="{WX+38}" y="408" width="{WW-76}" height="72" rx="4" fill="#fff" stroke="{NAVY}" stroke-width="1.5"/>')
add(f'  <text x="{WX+52}" y="430" font-size="12.5" font-weight="700" fill="{NAVY}">zPod SDK</text>')
add(f'  <text x="{WX+52}" y="448" font-size="11" fill="#666">Python client generated</text>')
add(f'  <text x="{WX+52}" y="464" font-size="11" fill="#666">from the API\'s <tspan font-family="{MONO}">openapi.json</tspan></text>')

# ---- The appliance's services ------------------------------------------------------------------
# zpodweb
ZX, ZY, ZW, ZH = AX + 22, 90, 240, 118
card(ZX, ZY, ZW, ZH, 'zpodweb', 'Web UI · React · Node server')
port(ZX + ZW - 14, ZY + 14, ':80' if TRAEFIK else ':8500', internal=TRAEFIK)
if TRAEFIK:
    add(f'  <text x="{ZX+22}" y="{ZY+80}" font-size="11.5" fill="#555">keeps its <tspan font-family="{MONO}" font-weight="700">/api/</tspan> proxy, to reach</text>')
    add(f'  <text x="{ZX+22}" y="{ZY+97}" font-size="11.5" fill="#555">any zPodFactory API it targets</text>')
else:
    add(f'  <text x="{ZX+22}" y="{ZY+80}" font-size="11.5" fill="#555">proxies <tspan font-family="{MONO}" font-weight="700">/api/</tspan> to the zPod API,</text>')
    add(f'  <text x="{ZX+22}" y="{ZY+97}" font-size="11.5" fill="#555">so the browser needs no CORS</text>')

# zPod API
PX, PY, PW, PH = AX + 326, 90, 290, 250
card(PX, PY, PW, PH, 'zPod API', 'core service · zpodapi')
port(PX + PW - 14, PY + 14, ':8000', internal=TRAEFIK)
tile(PX + 22, PY + 70, 117, 64, 'REST API', 'FastAPI')
tile(PX + 151, PY + 70, 117, 64, 'ORM', 'SQLModel')
add(f'  <text x="{PX+22}" y="{PY+162}" font-size="11.5" fill="#555">users, zPods, components, profiles,</text>')
add(f'  <text x="{PX+22}" y="{PY+179}" font-size="11.5" fill="#555">endpoints, settings; schedules flows</text>')
add(f'  <rect x="{PX+22}" y="{PY+196}" width="{PW-44}" height="34" rx="4" fill="#F0F2F4"/>')
add(f'  <text x="{PX+34}" y="{PY+217}" font-size="11.5" fill="#555">publishes <tspan font-family="{MONO}" font-weight="700" fill="#333">openapi.json</tspan> · Rich logs</text>')

# PostgreSQL: one server, two databases
DX, DY, DW, DH = PX + 50, 410, PW - 70, 112
add(f'  <rect x="{DX}" y="{DY}" width="{DW}" height="{DH}" rx="6" fill="#fff" stroke="{LINE}"/>')
add(f'  <rect x="{DX}" y="{DY}" width="6" height="{DH}" rx="2" fill="{NAVY}"/>')
cylinder(DX + 42, DY + 24, 18, 6, 46)
add(f'  <text x="{DX+76}" y="{DY+32}" font-size="16" font-weight="700" fill="{NAVY}">PostgreSQL</text>')
add(f'  <text x="{DX+76}" y="{DY+50}" font-size="11" font-family="{MONO}" fill="#666">zpodpostgres</text>')
dbx = DX + 76
for name, what in (('zpod', 'zPodFactory'), ('prefect', 'Prefect')):
    w = len(name) * 7.5 + 20
    add(f'  <rect x="{dbx}" y="{DY+64}" width="{w}" height="20" rx="10" fill="#EEF4F7" stroke="{NAVY}"/>')
    add(f'  <text x="{dbx+w/2}" y="{DY+78}" text-anchor="middle" font-size="11.5" font-weight="700" font-family="{MONO}" fill="{NAVY}">{name}</text>')
    add(f'  <text x="{dbx+w/2}" y="{DY+100}" text-anchor="middle" font-size="10.5" fill="#777">{what}</text>')
    dbx += w + 10

# zPod Engine
EX, EY, EW, EH = AX + 680, 90, 240, 466
card(EX, EY, EW, EH, 'zPod Engine', 'Prefect workflows · Prefect UI')
tile(EX + 20, EY + 66, EW - 40, 56, 'Prefect server', 'API and UI')
port(EX + EW - 14, EY + 14, ':4200' if TRAEFIK else ':8060', internal=TRAEFIK)
tile(EX + 20, EY + 156, EW - 40, 56, 'Prefect worker', 'zpodengine-pool')
arrow(f'M{EX+EW/2} {EY+124} V{EY+154}')
arrow(f'M{EX+EW/2} {EY+214} V{EY+246}')
add(f'  <text x="{EX+EW/2+8}" y="{EY+236}" font-size="11" fill="#555">starts · docker</text>')
# the flow run container and its tools
FX, FY, FW, FH = EX + 20, EY + 250, EW - 40, 200
add(f'  <rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" rx="4" fill="#fff" stroke="{NAVY}" stroke-width="1.5" stroke-dasharray="5 4"/>')
add(f'  <text x="{FX+FW/2}" y="{FY+20}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{NAVY}">flow run container</text>')
add(f'  <text x="{FX+FW/2}" y="{FY+36}" text-anchor="middle" font-size="11" fill="#666">one per run, <tspan font-family="{MONO}">zpodengine</tspan> image</text>')
TOOLS = (('Python', True), ('PowerShell · PowerCLI', True), ('Shell · govc', True),
         ('Terraform (available)', True), ('Ansible (not implemented)', False))
for i, (t, ok) in enumerate(TOOLS):
    ty = FY + 48 + i * 29
    if ok:
        add(f'  <rect x="{FX+12}" y="{ty}" width="{FW-24}" height="23" rx="11.5" fill="#EEF4F7" stroke="{NAVY}"/>')
        add(f'  <text x="{FX+FW/2}" y="{ty+16}" text-anchor="middle" font-size="11.5" fill="{NAVY}">{t}</text>')
    else:
        add(f'  <rect x="{FX+12}" y="{ty}" width="{FW-24}" height="23" rx="11.5" fill="#fff" stroke="#B9C0C8" stroke-dasharray="3 3"/>')
        add(f'  <text x="{FX+FW/2}" y="{ty+16}" text-anchor="middle" font-size="11.5" fill="{MUTED}">{t}</text>')

# the two Compose projects: zpodweb runs on its own, next to zpodcore
stack(ZX - 12, 74, ZW + 24, ZH + 32, 'COMPOSE · ZPODWEB')
stack(PX - 12, 74, EX + EW - PX + 24, EY + EH - 74 + 14, 'COMPOSE · ZPODCORE')

# zPod Library: host directories mounted into the API and every flow run
LX, LY, LW, LH = AX + 22, 590, EX + EW - AX - 22, 92
card(LX, LY, LW, LH, 'zPod Library', 'host volumes')
for i, (path, what) in enumerate((('/library', 'component definitions · zPodLibrary git repositories'),
                                  ('/products', 'downloaded templates and binaries · OVA, ISO'))):
    lx = LX + 200 + i * 354
    add(f'  <rect x="{lx}" y="{LY+18}" width="320" height="56" rx="4" fill="#fff" stroke="{NAVY}" stroke-width="1.5"/>')
    add(f'  <text x="{lx+14}" y="{LY+41}" font-size="13" font-weight="700" font-family="{MONO}" fill="{NAVY}">{path}</text>')
    add(f'  <text x="{lx+14}" y="{LY+60}" font-size="11" fill="#666">{what}</text>')

# ---- Endpoints ----------------------------------------------------------------------------------
NX, NY, NW, NH = AX + AW + 30, FY, W - (AX + AW + 30) - 30, FH
add(f'  <rect x="{NX}" y="{NY}" width="{NW}" height="{NH}" rx="6" fill="#fff" stroke="{LINE}"/>')
add(f'  <rect x="{NX}" y="{NY}" width="6" height="{NH}" rx="2" fill="{NAVY}"/>')
add(f'  <text x="{NX+22}" y="{NY+30}" font-size="16" font-weight="700" fill="{NAVY}">Endpoints</text>')
add(f'  <text x="{NX+22}" y="{NY+49}" font-size="12" fill="#666">where zPods are deployed</text>')
tile(NX + 22, NY + 66, NW - 44, 50, 'vCenter', 'vcsa · ESXi hosts')
tile(NX + 22, NY + 126, NW - 44, 50, 'NSX Manager', 'nsx')

# ---- Flows between the boxes ----------------------------------------------------------------------
if not TRAEFIK:
    # browser → zpodweb → API
    arrow(f'M{WX+WW-16} 128 H{ZX-2}', 'HTTP :8500', (WX + WW - 16 + ZX) / 2, 120)
    arrow(f'M{ZX+ZW} 149 H{PX-2}', '/api/', (ZX + ZW + PX) / 2, 141)
    # browser → Prefect UI, over the top of both stacks, onto the engine's :8060 pill
    arrow(f'M{WX+WW-60} 88 V58 H{EX+EW-46} V{EY-2}', 'HTTP :8060 · Prefect UI', (PX + PW + EX) / 2, 52)
    # zcli → API, through the SDK
    arrow(f'M{WX+WW-38} 444 C{AX+120} 444 {PX-120} 300 {PX-2} 300', 'HTTP :8000 · zPod SDK', AX + 150, 410, 'start')
# API ↔ PostgreSQL, API → engine, engine ↔ PostgreSQL
arrow(f'M{DX+DW/2} {PY+PH+2} V{DY-2}', 'read / write', DX + DW / 2 + 8, (PY + PH + DY) / 2 + 4, 'start', both=True)
arrow(f'M{PX+PW} 180 H{EX-2}', 'flows', (PX + PW + EX) / 2, 172)
arrow(f'M{DX+DW} {DY+DH/2} H{EX-2}', 'read / write', (DX + DW + EX) / 2, DY + DH / 2 - 8, both=True)
# both mount the library
arrow(f'M{PX+30} {LY-2} V{PY+PH+2}', 'mounts', PX + 22, LY - 5, 'end', dashed=True)
arrow(f'M{EX+EW/2} {LY-2} V{EY+EH+2}', 'mounts', EX + EW / 2 + 8, LY - 5, 'start', dashed=True)
# flow runs deploy to the endpoints
arrow(f'M{FX+FW+2} {FY+FH/2} H{NX-2}')
add(f'  <text x="{NX+NW/2}" y="{NY+NH+24}" text-anchor="middle" font-size="11.5" fill="#555">flows call the vCenter and NSX APIs</text>')
add(f'  <text x="{NX+NW/2}" y="{NY+NH+40}" text-anchor="middle" font-size="11.5" fill="#555">and upload OVAs to deploy zPods</text>')

if TY:
    add('  </g>')

# ---- Traefik: the single entry point (proposal) ----------------------------------------------------
if TRAEFIK:
    # the band, above both stacks; coordinates are absolute (the services are TY lower than above)
    BX, BY, BW, BH = AX + 10, 56, EX + EW + 12 - (AX + 10), 92
    add(f'  <rect x="{BX}" y="{BY}" width="{BW}" height="{BH}" rx="6" fill="#fff" stroke="{LINE}"/>')
    add(f'  <rect x="{BX}" y="{BY}" width="6" height="{BH}" rx="2" fill="{NAVY}"/>')
    add(f'  <text x="{BX+22}" y="{BY+28}" font-size="16" font-weight="700" fill="{NAVY}">Traefik</text>')
    add(f'  <text x="{BX+22}" y="{BY+46}" font-size="12" fill="#666">reverse proxy · TLS · the only published port</text>')
    port(BX + BW - 14, BY + 12, ':443')
    add(f'  <text x="{BX+BW-80}" y="{BY+26}" text-anchor="end" font-size="11" fill="#777">:80 redirects to :443</text>')
    add(f'  <text x="{BX+BW-14}" y="{BY+50}" text-anchor="end" font-size="11" fill="#777">dashed ports: internal only, no longer published</text>')
    # one route per service: a chip in the band, an arrow down to the service
    # arrows land right of the stack names, which sit on the stacks' top-left borders
    routes = ((ZX + ZW - 75, ZY + TY, '/ui', 'ui.*'),
              (PX + PW / 2 + 30, PY + TY, '/api', 'api.*'),
              (EX + EW / 2, EY + TY, '/prefect', 'prefect.*'))
    for cx, top, path, host in routes:
        w = (len(path) + len(host) + 6) * 7.2 + 24
        add(f'  <rect x="{cx-w/2}" y="{BY+60}" width="{w}" height="22" rx="11" fill="#EEF4F7" stroke="{NAVY}"/>')
        add(f'  <text x="{cx}" y="{BY+75}" text-anchor="middle" font-size="11.5" font-family="{MONO}" fill="{NAVY}" xml:space="preserve">'
            f'<tspan font-weight="700">{path}</tspan>  or  <tspan font-weight="700">{host}</tspan></text>')
        arrow(f'M{cx} {BY+BH} V{top-2}')
    # browser and zcli both come in on :443
    # right-angle paths with rounded corners, ending on a straight run into the band
    def elbow(x0, y0, xv, y1, r=8):
        return f'M{x0} {y0} H{xv-r} Q{xv} {y0} {xv} {y0-r} V{y1+r} Q{xv} {y1} {xv+r} {y1} H{BX-2}'
    arrow(elbow(WX + WW - 16, 128 + TY, WX + WW + 10, BY + 30))
    arrow(elbow(WX + WW - 38, 444 + TY, WX + WW + 22, BY + 66))
    add(f'  <text x="{WX+WW-16}" y="{BY+56}" text-anchor="end" font-size="11.5" fill="#555">both to Traefik, HTTPS <tspan font-family="{MONO}" font-weight="700">:443</tspan></text>')

    # ---- the two ways to route -------------------------------------------------------------------
    band_label(WX, OPT_Y - 12, 'TWO WAYS TO ROUTE · BOTH WORK AT THE SAME TIME')
    OW = (W - 2 * WX - 30) / 2
    options = (
        ('Option A · by path', 'recommended for labs',
         'one name, or just the appliance IP: no DNS records, one certificate',
         ((f'https://{DOMAIN}/ui', 'zpodweb'),
          (f'https://{DOMAIN}/api', 'zPod API, zcli -s …/api'),
          (f'https://{DOMAIN}/prefect', 'Prefect UI and its API'),
          ('https://&lt;appliance-ip&gt;/ui', 'the same routes by IP')),
         'apps read their prefix from X-Forwarded-Prefix; the Prefect UI is built for /prefect'),
        ('Option B · by host name', None,
         f'a wildcard DNS record and certificate: *.{DOMAIN}',
         ((f'https://ui.{DOMAIN}', 'zpodweb'),
          (f'https://api.{DOMAIN}', 'zPod API, zcli -s https://api.…'),
          (f'https://prefect.{DOMAIN}', 'Prefect UI and its API')),
         'same routers as option A: ui.* and api.* serve at /, prefect.* opens /prefect/'),
    )
    for k, (title, tag, sub, rows, note) in enumerate(options):
        ox = WX + k * (OW + 30)
        card(ox, OPT_Y, OW, 210, title, sub)
        if tag:
            tw = len(tag) * 6.8 + 20
            add(f'  <rect x="{ox+OW-18-tw}" y="{OPT_Y+14}" width="{tw}" height="22" rx="11" fill="{NAVY}"/>')
            add(f'  <text x="{ox+OW-18-tw/2}" y="{OPT_Y+29}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fff">{tag}</text>')
        for i, (url, target) in enumerate(rows):
            ry = OPT_Y + 82 + i * 26
            add(f'  <text x="{ox+22}" y="{ry}" font-size="13" font-family="{MONO}" fill="#333">{url}</text>')
            add(f'  <text x="{ox+400}" y="{ry}" font-size="12.5" fill="#999">→</text>')
            add(f'  <text x="{ox+422}" y="{ry}" font-size="12.5" fill="{NAVY}">{target}</text>')
        add(f'  <text x="{ox+22}" y="{OPT_Y+194}" font-size="11.5" fill="#777">{note}</text>')

add('</svg>')
open(OUT, 'w').write('\n'.join(P) + '\n')
