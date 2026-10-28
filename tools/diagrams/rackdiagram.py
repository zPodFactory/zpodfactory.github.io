"""Generate the 'zPod as a physical rack' diagram (SVG)."""
import sys

OUT = sys.argv[1]
FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'JetBrains Mono', monospace"
NAVY, ORANGE, TEAL, BLUE, T0C = "#12455F", "#E8730C", "#00796B", "#1565C0", "#F2B705"
PURPLE = "#AB47BC"
P = []
add = P.append


def router(cx, cy, fill, r=26):
    k = r / 27
    a, b, c, d, e, f = 18 * k, 11 * k, 5 * k, 6 * k, 12 * k, 13 * k
    return f'''  <g>
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>
    <g stroke="#fff" stroke-width="{3*k:.1f}" stroke-linecap="round" stroke-linejoin="round" fill="none">
      <path d="M{cx-a:.1f} {cy} h{b:.1f} M{cx-a+b-c:.1f} {cy-c:.1f} l{c:.1f} {c:.1f} -{c:.1f} {c:.1f}"/>
      <path d="M{cx+a:.1f} {cy} h-{b:.1f} M{cx+a-b+c:.1f} {cy-c:.1f} l-{c:.1f} {c:.1f} {c:.1f} {c:.1f}"/>
      <path d="M{cx} {cy-d:.1f} v-{e:.1f} M{cx-c:.1f} {cy-f:.1f} l{c:.1f} -{c:.1f} {c:.1f} {c:.1f}"/>
      <path d="M{cx} {cy+d:.1f} v{e:.1f} M{cx-c:.1f} {cy+f:.1f} l{c:.1f} {c:.1f} {c:.1f} -{c:.1f}"/>
    </g>
  </g>'''


def pill(cx, y, text, fill, fs=12, w=None, bold=False):
    w = w or (len(text) * fs * 0.6 + 18)
    wt = ' font-weight="700"' if bold else ''
    return (f'  <rect x="{cx-w/2:.1f}" y="{y}" width="{w:.1f}" height="{fs+9}" fill="{fill}"/>\n'
            f'  <text x="{cx}" y="{y+fs+3}" text-anchor="middle" font-size="{fs}" fill="#fff"{wt}>{text}</text>')


W, H = 1600, 1080
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" '
    'role="img" aria-label="A zPod drawn as a physical rack: a top-of-rack switch for the zPod segment, zcore as the rack '
    'router and NFS filer, four nested ESXi servers, uplinked through the NSX T1 and T0">')
add(f'  <rect width="{W}" height="{H}" fill="#fff"/>')

# ---- Rack cabinet ----------------------------------------------------------------------
RX, RY, RW, RH = 600, 96, 360, 700
IX, IW = RX + 34, RW - 68           # device area between the rails
U = 26                               # height of 1U in the drawing
add('  <!-- rack cabinet -->')
add(f'  <rect x="{RX}" y="{RY}" width="{RW}" height="{RH}" rx="10" fill="#2B2F36"/>')
add(f'  <rect x="{RX+10}" y="{RY+30}" width="{RW-20}" height="{RH-44}" fill="#1E2227"/>')
add(f'  <text x="{RX+RW/2}" y="{RY+21}" text-anchor="middle" font-size="14" font-weight="700" fill="#E6E8EB">zPod “test” rack</text>')
for x in (RX + 14, RX + RW - 30):  # rails with U holes
    add(f'  <rect x="{x}" y="{RY+32}" width="16" height="{RH-48}" fill="#3A3F47"/>')
    for i in range(int((RH - 56) / 13)):
        add(f'  <rect x="{x+6}" y="{RY+38+i*13}" width="4" height="4" fill="#1E2227"/>')
add(f'  <rect x="{RX+18}" y="{RY+RH-14}" width="40" height="14" fill="#2B2F36"/><rect x="{RX+RW-58}" y="{RY+RH-14}" width="40" height="14" fill="#2B2F36"/>')

y = RY + 40


def unit(h, body, label, sub=None, accent=None):
    """Draw a rack device of h U at the current height."""
    global y
    hh = h * U - 4
    out = [f'  <rect x="{IX}" y="{y}" width="{IW}" height="{hh}" rx="2" fill="{body}" stroke="#0F1114"/>']
    if accent:
        out.append(f'  <rect x="{IX}" y="{y}" width="6" height="{hh}" fill="{accent}"/>')
    out.append(('LABEL', label, sub, y, hh))
    y += h * U
    return out, y - h * U, hh


def render(items):
    for it in items:
        if isinstance(it, tuple):
            _, label, sub, yy, hh = it
            continue
        add(it)


# TOR switch (1U)
items, tor_y, tor_h = unit(1, '#30363F', 'TOR')
render(items)
for i in range(16):
    px = IX + 120 + i * 9.5
    add(f'  <rect x="{px:.1f}" y="{tor_y+6}" width="7" height="6" fill="#0F1114"/>')
    add(f'  <rect x="{px+1:.1f}" y="{tor_y+15}" width="5" height="2" fill="{"#7CD992" if i % 5 else "#F2B705"}"/>')
add(f'  <text x="{IX+12}" y="{tor_y+16}" font-size="11.5" font-weight="700" fill="#E6E8EB">TOR switch</text>')
add(f'  <rect x="{IX+IW-58}" y="{tor_y+5}" width="50" height="13" rx="2" fill="{NAVY}"/>')
add(f'  <text x="{IX+IW-33}" y="{tor_y+15}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fff">GENEVE</text>')
TOR_MID = tor_y + tor_h / 2

# zcore: one 3U device, router strip on top, storage below
items, z_y, z_h = unit(3, '#3B2A1E', 'zcore', accent=ORANGE)
render(items)
zr_y, zr_h = z_y, U - 4                     # router strip
add(f'  <line x1="{IX+6}" y1="{z_y+U-2}" x2="{IX+IW}" y2="{z_y+U-2}" stroke="#1E1610" stroke-width="2"/>')
add(f'  <text x="{IX+14}" y="{z_y+16}" font-size="11.5" font-weight="700" fill="#FFD3AD">zcore · router</text>')
add(f'  <text x="{IX+IW-10}" y="{z_y+16}" text-anchor="end" font-size="10" fill="#FFD3AD">10.96.42.2</text>')
ZPORTS = [IX + 120 + i * 9.5 for i in range(10)]
for px in ZPORTS:
    add(f'  <rect x="{px:.1f}" y="{z_y+6}" width="7" height="6" fill="#0F1114"/>')
    add(f'  <rect x="{px+1:.1f}" y="{z_y+15}" width="5" height="2" fill="#7CD992"/>')
sy0 = z_y + U
add(f'  <text x="{IX+14}" y="{sy0+19}" font-size="11.5" font-weight="700" fill="#FFD3AD">zcore · NFS filer</text>')
add(f'  <text x="{IX+14}" y="{sy0+36}" font-size="10.5" fill="#E8C4A4">STORAGE01 + yours · DNS · DHCP</text>')
for i in range(4):
    bx = IX + IW - 82 + i * 18
    add(f'  <rect x="{bx}" y="{sy0+8}" width="14" height="32" rx="1.5" fill="#22262B" stroke="#55493F"/>')
    add(f'  <circle cx="{bx+7}" cy="{sy0+35}" r="1.6" fill="#7CD992"/>')
# patch cables from TOR ports down to zcore ports
CABLES = [(1, NAVY), (3, '#6A1B9A'), (5, '#D97706'), (7, '#00796B'), (9, PURPLE)]
for i, col in CABLES:
    x = IX + 120 + i * 9.5 + 3.5
    y1, y2 = tor_y + 12, z_y + 6
    add(f'  <path d="M{x:.1f} {y1} C{x-5:.1f} {y1+10} {x-5:.1f} {y2-8} {x:.1f} {y2}" stroke="{col}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')


# blank 1U
items, b_y, b_h = unit(1, '#262A30', 'blank')
render(items)

# ESXi servers sit at the bottom of the rack; free units in between show room to grow
free_top = y
y = RY + 40 + int((RY + RH - 20 - 8 * U - (RY + 40)) // U) * U
gy, gh = free_top + 4, y - 8 - free_top
# room to grow: free rack units
add(f'  <rect x="{IX}" y="{gy}" width="{IW}" height="{gh}" rx="3" fill="none" stroke="#5A6170" stroke-width="1.5" stroke-dasharray="6 5"/>')
add(f'  <text x="{IX+IW/2}" y="{gy+gh/2-14}" text-anchor="middle" font-size="30" fill="#5A6170">+</text>')
add(f'  <text x="{IX+IW/2}" y="{gy+gh/2+10}" text-anchor="middle" font-size="13" font-weight="700" fill="#9AA4AF">room to grow</text>')
add(f'  <text x="{IX+IW/2}" y="{gy+gh/2+28}" text-anchor="middle" font-size="11.5" fill="#8A949F">more ESXi hosts, NSX edges, appliances</text>')
add(f'  <text x="{IX+IW/2}" y="{gy+gh/2+44}" text-anchor="middle" font-size="11.5" fill="#8A949F">or extra storage, added to the zPod</text>')

# ESXi servers (2U each)
esx = []
for hid in (11, 12, 13, 14):
    items, sy, sh = unit(2, '#C9D0D8', 'esxi')
    render(items)
    add(f'  <text x="{IX+12}" y="{sy+19}" font-size="12" font-weight="700" fill="#1F2933">ESXi · esxi{hid}</text>')
    add(f'  <text x="{IX+12}" y="{sy+36}" font-size="11" fill="#3E4A56">10.96.42.{hid}</text>')
    for i in range(8):
        bx = IX + IW - 150 + i * 17
        add(f'  <rect x="{bx}" y="{sy+7}" width="13" height="34" rx="1.5" fill="#E9EDF1" stroke="#8A96A3"/>')
        add(f'  <rect x="{bx+3}" y="{sy+32}" width="7" height="2" fill="#62A420"/>')
    add(f'  <circle cx="{IX+IW-12}" cy="{sy+24}" r="3" fill="#62A420"/>')
    esx.append((sy, sh))

# ---- Trunk cabling (right side of the rack) ----------------------------------------------
CX = RX + RW + 18
add('  <!-- 802.1Q trunk patch cables -->')
targets = [zr_y + zr_h / 2] + [sy + sh / 2 for sy, sh in esx]
TE = int((esx[0][0] + esx[-1][0] + esx[-1][1]) / 2 - 78) + 190   # trunk runs down to the VLAN 192 line
add(f'  <path d="M{IX+IW} {TOR_MID} H{CX} V{TE}" stroke="{NAVY}" stroke-width="6" stroke-linejoin="round" fill="none"/>')
for t in targets:
    add(f'  <line x1="{CX}" y1="{t}" x2="{IX+IW}" y2="{t}" stroke="{NAVY}" stroke-width="2"/>')
    add(f'  <circle cx="{CX}" cy="{t}" r="3" fill="{NAVY}"/>')
add(f'  <text x="{CX+8}" y="{(TOR_MID+targets[-1])/2-60}" font-size="12" fill="{NAVY}" transform="rotate(90 {CX+8} {(TOR_MID+targets[-1])/2-60})" text-anchor="middle">802.1Q trunk · native + VLANs 1–4094</text>')

# ---- Upstream (left) -------------------------------------------------------------------------
UX = 330
add('  <!-- upstream -->')
add(f'  <rect x="{UX-150}" y="20" width="130" height="36" rx="18" fill="#fff" stroke="#C62828" stroke-width="3"/>')
add(f'  <text x="{UX-85}" y="44" text-anchor="middle" font-size="15" font-weight="700" fill="#C62828">INTERNET</text>')
add(f'  <rect x="{UX+20}" y="20" width="150" height="36" rx="18" fill="#fff" stroke="#777" stroke-width="3"/>')
add(f'  <text x="{UX+95}" y="36" text-anchor="middle" font-size="12" font-weight="700" fill="#444">Corp network</text>')
add(f'  <text x="{UX+95}" y="50" text-anchor="middle" font-size="11" fill="#666">VPN / BGP</text>')
add(f'  <path d="M{UX-85} 56 V72 H{UX} M{UX+95} 56 V72 H{UX} M{UX} 72 V84" stroke="#777" stroke-width="3" fill="none"/>')
# physical network: spine-leaf fabric
add(f'  <rect x="{UX-52}" y="84" width="104" height="66" rx="8" fill="#F4F4F4" stroke="#444" stroke-width="2"/>')
add('  <path d="' + ' '.join(f'M{sx} 101 L{lx} 130' for sx in (UX-22, UX+22) for lx in (UX-34, UX, UX+34)) + '" stroke="#777" stroke-width="1.5" fill="none"/>')
for sx in (UX-22, UX+22):
    add(f'  <rect x="{sx-12}" y="91" width="24" height="10" rx="2" fill="#444"/>')
for lx in (UX-34, UX, UX+34):
    add(f'  <rect x="{lx-12}" y="130" width="24" height="10" rx="2" fill="#444"/>')
add(f'  <text x="{UX+62}" y="122" font-size="12" font-weight="700" fill="#444">Physical network</text>')
add(f'  <line x1="{UX}" y1="150" x2="{UX}" y2="174" stroke="#777" stroke-width="3"/>')
# supernet reserved for all zPods, routed by the T0
add(f'  <rect x="24" y="166" width="190" height="66" rx="4" fill="#FFFBEA" stroke="{T0C}" stroke-width="1.5"/>')
add(f'  <text x="36" y="185" font-size="11.5" font-weight="700" fill="#8A6A00">zPod pool (all zPods)</text>')
add(f'  <text x="36" y="204" font-size="14" font-weight="700" font-family="{MONO}" fill="#333">10.96.0.0/16</text>')
add(f'  <text x="36" y="222" font-size="11" fill="#555">one /24 each · this one <tspan font-family="{MONO}">.42.0/24</tspan></text>')
add(f'  <line x1="214" y1="200" x2="{UX-28}" y2="200" stroke="{T0C}" stroke-width="1.5" stroke-dasharray="4 3"/>')
add(router(UX, 200, T0C))
add(pill(UX, 232, 'NSX T0 · datacenter core', T0C, bold=True))
add(f'  <line x1="{UX}" y1="253" x2="{UX}" y2="276" stroke="{NAVY}" stroke-width="3"/>')
add(router(UX, 302, NAVY))
add(pill(UX, 334, 'NSX T1 · zPod-test-tier1', NAVY))
# uplink cable from the T1 into the TOR
add(f'  <path d="M{UX+26} 302 H{RX-30} Q{RX-14} 302 {RX-14} {TOR_MID+8} V{TOR_MID} H{IX}" stroke="{NAVY}" stroke-width="6" stroke-linejoin="round" fill="none"/>')
add(f'  <text x="{UX+40}" y="276" font-size="12" font-weight="700" fill="{NAVY}">zPod-test-segment</text>')
add(f'  <text x="{UX+40}" y="292" font-size="11.5" fill="{NAVY}">T1 .1 on the native VLAN</text>')

# T1 static routes, compact, left of the T1
TX, TY, TWD = 24, 254, 206
add(f'  <rect x="{TX}" y="{TY}" width="{TWD}" height="124" rx="4" fill="#F5F7F9" stroke="#C5CAD0"/>')
add(f'  <line x1="{TX+TWD}" y1="302" x2="{UX-28}" y2="302" stroke="{NAVY}" stroke-width="1.5" stroke-dasharray="4 3"/>')
add(f'  <text x="{TX+12}" y="{TY+19}" font-size="12" font-weight="700" fill="{NAVY}">T1 routes</text>')
add(f'  <text x="{TX+TWD-12}" y="{TY+19}" text-anchor="end" font-size="9.5" fill="#888">next hop</text>')
rows = [('10.96.42.0/26', 'gw .1', '#4A148C'),
        ('10.96.42.64/26', '10.96.42.2', '#6A1B9A'),
        ('10.96.42.128/26', '10.96.42.2', '#8E24AA'),
        ('10.96.42.192/26', '10.96.42.2', '#AB47BC'),
        ('10.42.200.0/24', '10.96.42.2', '#26A69A')]
for i, (n, v, col) in enumerate(rows):
    yy = TY + 38 + i * 15
    add(f'  <text x="{TX+12}" y="{yy}" font-size="9.5" font-family="{MONO}" fill="{col}">{n}</text>')
    add(f'  <text x="{TX+TWD-12}" y="{yy}" text-anchor="end" font-size="9.5" font-family="{MONO}" fill="{col}">{v}</text>')
add(f'  <text x="{TX+12}" y="{TY+116}" font-size="8.5" fill="#26A69A">↳ VLAN 200 made global by a superadmin</text>')

# ---- Right: zcore networks (after the zpodweb Topology tab, All networks) ------------------
INDIGO = "#5C6BC0"
PX, PW = 1006, 584
SEG = TOR_MID                      # the panel's segment continues the rack's trunk
PY = SEG - 52
ZB, BUS = SEG + 92, SEG + 150
PORT = BUS + 64
add('  <!-- zcore networks, connected to the rack trunk -->')
add(f'  <rect x="{PX}" y="{PY}" width="{PW}" height="{PORT + 156 - PY}" rx="6" fill="#FAFAFB" stroke="#DDE1E6"/>')
add(f'  <text x="{PX+14}" y="{PY+20}" font-size="13" font-weight="700" fill="#C2510F">zcore networks</text>')
add(f'  <text x="{PX+142}" y="{PY+20}" font-size="11" fill="#888">as in the zpodweb Topology tab, All networks</text>')
# trunk: from the rack bundle into the panel
add(f'  <line x1="{CX}" y1="{SEG}" x2="{PX+PW-24}" y2="{SEG}" stroke="{NAVY}" stroke-width="6" stroke-linecap="round"/>')
add(f'  <text x="{PX+PW-24}" y="{SEG-10}" text-anchor="end" font-size="11.5" font-weight="700" fill="{NAVY}">zPod-test-segment · 802.1Q trunk</text>')
# zcore box
add(f'  <rect x="{PX+14}" y="{ZB}" width="{PW-28}" height="{PORT + 116 - ZB}" rx="4" fill="#FFF7EE" stroke="{ORANGE}" stroke-width="1.5"/>')
add(f'  <text x="{PX+PW-26}" y="{ZB+20}" text-anchor="end" font-size="14" font-weight="700" fill="#C2510F">zcore.test.zpod.io</text>')
add(f'  <text x="{PX+PW-26}" y="{ZB+35}" text-anchor="end" font-size="10" fill="#8A6A4A">zboxapi · network, storage &amp; core services</text>')
# eth0 native (thin) and eth1 trunk (thick)
E0, E1 = PX + 40, PX + 176
add(f'  <line x1="{E0}" y1="{SEG}" x2="{E0}" y2="{ZB}" stroke="#4A148C" stroke-width="2"/>')
add(f'  <circle cx="{E0}" cy="{ZB}" r="6" fill="#fff" stroke="#4A148C" stroke-width="2"/>')
add(f'  <text x="{E0+10}" y="{SEG+28}" font-size="10.5" font-weight="700" font-family="{MONO}" fill="#333">eth0 · native</text>')
add(f'  <text x="{E0+10}" y="{SEG+42}" font-size="10" font-family="{MONO}" fill="#666">10.96.42.2/26</text>')
add(f'  <line x1="{E1}" y1="{SEG}" x2="{E1}" y2="{BUS}" stroke="{NAVY}" stroke-width="6"/>')
add(f'  <text x="{E1+12}" y="{SEG+28}" font-size="10.5" font-weight="700" font-family="{MONO}" fill="{NAVY}">eth1 · 802.1Q trunk</text>')
add(f'  <text x="{E1+12}" y="{SEG+42}" font-size="10" font-family="{MONO}" fill="#666">8 tagged VLANs</text>')
ports = [('eth1.10', '172.16.10.1', 'local', '#B45309'), ('eth1.20', '172.16.20.1', 'local', '#D97706'),
         ('eth1.30', '172.16.30.1', 'local', '#F59E0B'), ('eth1.64', '10.96.42.65', 'global', '#6A1B9A'),
         ('eth1.128', '10.96.42.129', 'global', '#8E24AA'), ('eth1.192', '10.96.42.193', 'global', PURPLE),
         ('eth1.111', '10.42.111.1', 'masquerade', '#00796B'), ('eth1.200', '10.42.200.1', 'global', '#26A69A')]
X0, STEP = PX + 80, 64
xs = [X0 + i * STEP for i in range(len(ports))]
add(f'  <line x1="{xs[0]-12}" y1="{BUS}" x2="{xs[-1]+12}" y2="{BUS}" stroke="{NAVY}" stroke-width="6" stroke-linecap="round"/>')
add(f'  <path d="M{E0} {ZB+6} V{PORT} H{xs[-1]}" stroke="#9AA3AD" stroke-width="1.5" stroke-dasharray="3 3" fill="none"/>')
add(f'  <text x="{E0-6}" y="{(ZB+PORT)/2+6}" transform="rotate(-90 {E0-6} {(ZB+PORT)/2+6})" text-anchor="middle" font-size="10" fill="#777">routing</text>')
for x, (n, ip, mode, col) in zip(xs, ports):
    add(f'  <line x1="{x}" y1="{BUS}" x2="{x}" y2="{PORT-6}" stroke="{col}" stroke-width="2"/>')
    add(f'  <circle cx="{x}" cy="{PORT}" r="6" fill="#fff" stroke="{col}" stroke-width="2"/>')
    add(f'  <text x="{x}" y="{PORT+22}" text-anchor="middle" font-size="9.5" font-weight="700" font-family="{MONO}" fill="#222">{n}</text>')
    add(f'  <text x="{x}" y="{PORT+36}" text-anchor="middle" font-size="8.5" font-family="{MONO}" fill="#555">{ip}</text>')
    add(f'  <text x="{x}" y="{PORT+50}" text-anchor="middle" font-size="9" fill="{col}">{mode}</text>')
def group(i0, i1, label, col):
    a, b = xs[i0] - 28, min(xs[i1] + 28, PX + PW - 22)
    y = PORT + 64
    add(f'  <path d="M{a} {y-6} V{y} H{b} V{y-6}" stroke="{col}" stroke-width="1.5" fill="none"/>')
    add(f'  <text x="{(a+b)/2}" y="{y+16}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{col}">{label}</text>')
group(0, 2, 'zcore VLANs (local) · /24', '#D97706')
group(3, 5, 'zPod networks (global) · /26', '#8E24AA')
group(6, 7, 'your VLANs · /24', TEAL)
# legend for line weights
LY = PORT + 138
add(f'  <line x1="{PX+24}" y1="{LY}" x2="{PX+60}" y2="{LY}" stroke="{NAVY}" stroke-width="6" stroke-linecap="round"/>')
add(f'  <text x="{PX+68}" y="{LY+4}" font-size="11" fill="#555">802.1Q trunk</text>')
add(f'  <line x1="{PX+164}" y1="{LY}" x2="{PX+200}" y2="{LY}" stroke="#4A148C" stroke-width="2"/>')
add(f'  <text x="{PX+208}" y="{LY+4}" font-size="11" fill="#555">native (untagged)</text>')
for k, c in enumerate(('#D97706', '#8E24AA', '#00796B')):
    add(f'  <line x1="{PX+326+k*14}" y1="{LY}" x2="{PX+336+k*14}" y2="{LY}" stroke="{c}" stroke-width="3"/>')
add(f'  <text x="{PX+372}" y="{LY+4}" font-size="11" fill="#555">tagged VLAN, coloured by group</text>')
add(f'  <rect x="{PX+30}" y="{PORT+88}" width="196" height="20" fill="#E8F5EC" stroke="#7DBF95"/>')
add(f'  <text x="{PX+128}" y="{PORT+102}" text-anchor="middle" font-size="9.5" font-family="{MONO}" fill="#2E7D4F">masquerade: 10.42.111.0/24 → eth0</text>')

# cluster bracket and workloads
top, bot = esx[0][0], esx[-1][0] + esx[-1][1]
BX = RX + RW + 52
LB = RX - 12                       # brace on the left of the rack
add(f'  <path d="M{LB} {top} q-10 0 -10 10 V{(top+bot)/2-8} q0 8 -8 8 q8 0 8 8 V{bot-10} q0 10 10 10" stroke="#555" stroke-width="2" fill="none"/>')
add(f'  <text x="{LB-24}" y="{(top+bot)/2}" text-anchor="middle" font-size="13" font-weight="700" fill="#333" transform="rotate(-90 {LB-24} {(top+bot)/2})">vSphere cluster</text>')

# ---- Bottom left: zcore storage (after the zpodweb Storage card), default storage only ---------
SX, SY, SW = 24, 396, 516
c1, c2, c3 = SX + 30, SX + 142, SX + 318
add('  <!-- zcore storage: the default STORAGE01 and its folders, linked to the filer -->')
FY = z_y + U + 22                  # middle of the filer part of zcore

add(f'  <rect x="{SX}" y="{SY}" width="{SW}" height="268" rx="6" fill="#FAFAFB" stroke="#DDE1E6"/>')
add(f'  <text x="{SX+14}" y="{SY+20}" font-size="13" font-weight="700" fill="#C2510F">zcore storage</text>')
add(f'  <rect x="{SX+14}" y="{SY+32}" width="{SW-28}" height="22" rx="3" fill="#fff" stroke="#E3E6EA"/>')
add(f'  <circle cx="{SX+25}" cy="{SY+43}" r="3.5" fill="#43A047"/>')
add(f'  <text x="{SX+34}" y="{SY+47}" font-size="10.5" fill="#333">nfs-server active <tspan fill="#888">· NFS 3 · 4 · 4.1 · 4.2</tspan></text>')
add(f'  <text x="{SX+SW-22}" y="{SY+47}" text-anchor="end" font-size="10" fill="#888">server <tspan font-family="{MONO}" fill="#C2510F">zcore.test.zpod.io</tspan></text>')
hy = SY + 76
for x, h in ((SX + 14, 'Storage · Folder'), (c2, 'Mount · Path'), (c3, 'NFS clients · Access')):
    add(f'  <text x="{x}" y="{hy}" font-size="10" fill="#999">{h}</text>')
add(f'  <text x="{SX+SW-18}" y="{hy}" text-anchor="end" font-size="10" fill="#999">Kind</text>')
add(f'  <line x1="{SX+14}" y1="{hy+7}" x2="{SX+SW-14}" y2="{hy+7}" stroke="#E3E6EA"/>')
def chip(xr, y, label, fg, bg):
    w = len(label) * 5.6 + 12
    add(f'  <rect x="{xr-w}" y="{y-11}" width="{w}" height="16" rx="8" fill="{bg}" stroke="{fg}" stroke-width="1"/>')
    add(f'  <text x="{xr-w/2}" y="{y+1}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{fg}">{label}</text>')
ry = hy + 26
add(f'  <rect x="{SX+14}" y="{ry-9}" width="12" height="9" rx="1.5" fill="none" stroke="#666" stroke-width="1.5"/>')
add(f'  <text x="{c1}" y="{ry}" font-size="11" font-weight="700" font-family="{MONO}" fill="#333">STORAGE01</text>')
add(f'  <text x="{c2}" y="{ry}" font-size="9.5" font-family="{MONO}" fill="#1565C0">/FILER/STORAGE01 <tspan fill="#888">· ext4 · sdb</tspan></text>')
USED = 0.61                        # amber from 60 %, red from 85 %
ucol = '#E53935' if USED >= .85 else '#F59E0B' if USED >= .6 else '#43A047'
add(f'  <rect x="{c3}" y="{ry-7}" width="80" height="6" rx="3" fill="#E3E6EA"/>')
add(f'  <rect x="{c3}" y="{ry-7}" width="{80*USED:.0f}" height="6" rx="3" fill="{ucol}"/>')
add(f'  <text x="{c3+86}" y="{ry}" font-size="10" font-weight="700" font-family="{MONO}" fill="{ucol}">{USED:.0%}</text>')
chip(SX + SW - 18, ry, 'zcore', '#B45309', '#FFF4E5')
rows = [('NFS-01', '10.96.42.0/26', 'rw', ('protected', '#C2510F', '#FFF1E6'), 4),
        ('NFS-VCD', '10.96.42.0/26', 'rw · no_root_squash', ('system', '#666', '#F0F1F3'), 1),
        ('VCF-BACKUPS', None, None, None, 0)]
fy = ry + 28
add(f'  <line x1="{SX+20}" y1="{ry+6}" x2="{SX+20}" y2="{fy+30+44-4}" stroke="#C5CAD0" stroke-width="1.5"/>')
for name, net, acc, kind, mounted in rows:
    add(f'  <line x1="{SX+20}" y1="{fy-4}" x2="{c1-4}" y2="{fy-4}" stroke="#C5CAD0" stroke-width="1.5"/>')
    add(f'  <text x="{c1}" y="{fy}" font-size="10.5" font-family="{MONO}" fill="{"#333" if net else "#888"}">{name}</text>')
    if mounted:                       # NFS clients mounted: 4 ESXi hosts on NFS-01, vcd on NFS-VCD
        mx = c1 + len(name) * 6.4 + 8
        add(f'  <circle cx="{mx+3}" cy="{fy-4}" r="3.5" fill="#43A047"/>')
        add(f'  <text x="{mx+10}" y="{fy}" font-size="10" font-weight="700" fill="#43A047">{mounted}</text>')
    add(f'  <text x="{c2}" y="{fy}" font-size="9.5" font-family="{MONO}" fill="#1565C0">/FILER/STORAGE01/{name}</text>')
    if net:
        add(f'  <rect x="{c3-3}" y="{fy-11}" width="88" height="15" rx="2" fill="#E8F0FB"/>')
        add(f'  <text x="{c3+1}" y="{fy}" font-size="9.5" font-family="{MONO}" fill="#1565C0">{net}</text>')
        if len(acc) > 4:                  # long options go on their own line
            add(f'  <text x="{c3+1}" y="{fy+14}" font-size="9.5" fill="#C2510F">{acc}</text>')
        else:
            add(f'  <text x="{c3+92}" y="{fy}" font-size="9.5" fill="#C2510F">{acc}</text>')
        chip(SX + SW - 18, fy, *kind)
    else:
        add(f'  <text x="{c3}" y="{fy}" font-size="10" font-style="italic" fill="#999">not exported</text>')
    fy += 44 if acc and len(acc) > 4 else 30
add(f'  <line x1="{SX+14}" y1="{fy-14}" x2="{SX+SW-14}" y2="{fy-14}" stroke="#E3E6EA"/>')
add(f'  <rect x="{SX+14}" y="{fy-4}" width="{SW-28}" height="26" rx="4" fill="#F1F8F6" stroke="#26A69A" stroke-dasharray="4 3"/>')
add(f'  <text x="{SX+26}" y="{fy+13}" font-size="10.5" fill="#00796B"><tspan font-weight="700">+ STORAGE02…</tspan> your disks, storages, folders and NFS exports</text>')
WX, WY = 1160, int((top + bot) / 2 - 78)
add(f'  <rect x="{PX}" y="{WY-34}" width="{PW}" height="{(WY+190+122)-(WY-34)}" rx="6" fill="none" stroke="#888" stroke-width="1.5" stroke-dasharray="4 4"/>')
add(f'  <rect x="{PX+10}" y="{WY-44}" width="168" height="18" fill="#fff"/>')
add(f'  <text x="{PX+14}" y="{WY-30}" font-size="13" font-weight="700" fill="#333">zPod nested workloads</text>')
comps = [('vcsa', '.10'), ('nsx', '.20'), ('vrops', '.30'), ('vrli', '.31'), ('vcd', '.40')]
TW, TS = 56, 62
NATIVE = '#4A148C'
LEND = PX + PW - 14             # VLAN lines run the full width of the box
add(f'  <text x="{LEND}" y="{WY-15}" text-anchor="end" font-size="10.5" fill="#4A148C"><tspan font-weight="700">native VLAN</tspan> · <tspan font-family="{MONO}">10.96.42.0/26</tspan></text>')
add(f'  <line x1="{CX}" y1="{WY-10}" x2="{LEND}" y2="{WY-10}" stroke="{NATIVE}" stroke-width="2"/>')
add(f'  <circle cx="{CX}" cy="{WY-10}" r="3.5" fill="{NATIVE}"/>')
for i in range(6):
    add(f'  <line x1="{WX+i*TS+TW/2}" y1="{WY-10}" x2="{WX+i*TS+TW/2}" y2="{WY}" stroke="{NATIVE}" stroke-width="2"/>')
for i, (n, ip) in enumerate(comps):
    x = WX + i * TS
    add(f'  <rect x="{x}" y="{WY}" width="{TW}" height="34" rx="3" fill="{NATIVE}"/>')
    add(f'  <text x="{x+TW/2}" y="{WY+15}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fff">{n}</text>')
    add(f'  <text x="{x+TW/2}" y="{WY+28}" text-anchor="middle" font-size="10" fill="#E1BEE7">{ip}</text>')
x = WX + 5 * TS
add(f'  <rect x="{x}" y="{WY}" width="{TW}" height="34" rx="3" fill="{NATIVE}"/>')
add(f'  <text x="{x+TW/2}" y="{WY+15}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fff">VM</text>')
add(f'  <text x="{x+TW/2}" y="{WY+28}" text-anchor="middle" font-size="10" fill="#E1BEE7">.100</text>')

# workloads on the user VLANs, through the trunk
for ly, col, vlan, net, note, vms in ((WY + 66, '#00796B', 'VLAN 111', '10.42.111.0/24', 'local, masquerade', ((1, '.21'), (3, '.57'))),
                                      (WY + 126, '#26A69A', 'VLAN 200', '10.42.200.0/24', 'global, T1 route', ((0, '.14'), (2, '.88'), (5, '.120')))):
    add(f'  <text x="{LEND}" y="{ly-7}" text-anchor="end" font-size="10.5" fill="{col}"><tspan font-weight="700">{vlan}</tspan> · <tspan font-family="{MONO}">{net}</tspan></text>')
    add(f'  <line x1="{CX}" y1="{ly}" x2="{LEND}" y2="{ly}" stroke="{col}" stroke-width="2"/>')
    add(f'  <circle cx="{CX}" cy="{ly}" r="3" fill="{col}"/>')
    for c, ip in vms:
        x = WX + c * TS
        add(f'  <line x1="{x+TW/2}" y1="{ly}" x2="{x+TW/2}" y2="{ly+6}" stroke="{col}" stroke-width="2"/>')
        add(f'  <rect x="{x}" y="{ly+6}" width="{TW}" height="18" rx="3" fill="{col}"/>')
        add(f'  <text x="{x+TW/2}" y="{ly+19}" text-anchor="middle" font-size="10" fill="#fff">VM <tspan font-weight="700">{ip}</tspan></text>')

# NSX edges on VLAN 192, as in the layers diagram
EB = WY + 190                      # VLAN 192 line
E1X, E2X = WX + TW / 2, WX + 2 * TS + TW / 2
add('  <!-- NSX edges: uplinks on VLAN 192, VIP .250, default route to zcore .193 -->')
add(f'  <line x1="{CX}" y1="{EB}" x2="{LEND}" y2="{EB}" stroke="{PURPLE}" stroke-width="2"/>')
add(f'  <circle cx="{CX}" cy="{EB}" r="3" fill="{PURPLE}"/>')
add(f'  <text x="{LEND}" y="{EB-8}" text-anchor="end" font-size="11" font-weight="700" fill="{PURPLE}">VLAN 192 · <tspan font-family="{MONO}" font-weight="400">10.96.42.192/26</tspan></text>')
add(f'  <text x="{E2X+36}" y="{EB+34}" font-size="10.5" font-weight="700" fill="{PURPLE}">edge uplinks</text>')
for ex, name, state, ip in ((E1X, 'edge-01', 'active', '.251'), (E2X, 'edge-02', 'standby', '.252')):
    add(f'  <line x1="{ex}" y1="{EB}" x2="{ex}" y2="{EB+44}" stroke="{PURPLE}" stroke-width="2"/>')
    add(f'  <text x="{ex+5}" y="{EB+34}" font-size="10.5" fill="{PURPLE}">{ip}</text>')
    add(f'  <rect x="{ex-30}" y="{EB+44}" width="60" height="30" rx="3" fill="#2E7D32"/>')
    add(f'  <text x="{ex}" y="{EB+63}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{name}</text>')
    add(f'  <text x="{ex}" y="{EB+88}" text-anchor="middle" font-size="10.5" fill="{"#2E7D32" if state == "active" else "#777"}">{state}</text>')
add(f'  <rect x="{E1X-46}" y="{EB+39}" width="{E2X-E1X+92}" height="72" fill="none" stroke="#1B5E20" stroke-width="1.5" stroke-dasharray="3 4"/>')
add(f'  <text x="{(E1X+E2X)/2}" y="{EB+105}" text-anchor="middle" font-size="11" fill="#1B5E20">NSX Edge Cluster</text>')
VM_ = (E1X + E2X) / 2
add(f'  <line x1="{E1X}" y1="{EB+14}" x2="{VM_-30}" y2="{EB+14}" stroke="{PURPLE}" stroke-width="1.5" stroke-dasharray="2 2"/>')
add(f'  <line x1="{VM_+30}" y1="{EB+14}" x2="{E2X}" y2="{EB+14}" stroke="{PURPLE}" stroke-width="1.5" stroke-dasharray="2 2"/>')
add(f'  <rect x="{VM_-30}" y="{EB+4}" width="60" height="20" rx="10" fill="#F3E5F5" stroke="{PURPLE}" stroke-width="1.5"/>')
add(f'  <text x="{VM_}" y="{EB+18}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{PURPLE}">VIP .250</text>')
add(f'  <text x="{E2X+54}" y="{EB+52}" font-size="11.5" fill="#333">default route</text>')
add(f'  <text x="{E2X+54}" y="{EB+68}" font-size="11" font-family="{MONO}" font-weight="700" fill="#333">0.0.0.0/0 → <tspan fill="#AB47BC">10.96.42.193</tspan></text>')
add(f'  <text x="{E2X+54}" y="{EB+84}" font-size="11" fill="#555">zcore on VLAN 192</text>')

# ---- Physical <-> zPod mapping ------------------------------------------------------------------
add(f'  <text x="150" y="918" font-size="16" font-weight="700" fill="{NAVY}">How the rack maps to a zPod</text>')
cards = [('Datacenter core', 'NSX T0', T0C),
         ('Rack uplink router', 'NSX T1 (.1, static routes)', NAVY),
         ('Top-of-rack switch', 'Geneve segment (802.1Q trunk)', NAVY),
         ('Rack router + filer', 'zcore: VLANs, DNS, DHCP, NFS', ORANGE),
         ('Rack servers', 'nested ESXi hosts', '#5A6875')]
cw, gap = 272, 14
for i, (phys, zpod, col) in enumerate(cards):
    x = 150 + i * (cw + gap) if i < 4 else None
for i, (phys, zpod, col) in enumerate(cards):
    x = 22 + i * (cw + 40)
    x = 150 + i * ((1580 - 150 - 4 * gap) / 5 + gap)
    w = (1580 - 150 - 4 * gap) / 5
    add(f'  <rect x="{x:.1f}" y="934" width="{w:.1f}" height="76" rx="6" fill="#fff" stroke="#C5CAD0"/>')
    add(f'  <rect x="{x:.1f}" y="934" width="6" height="76" rx="2" fill="{col}"/>')
    add(f'  <text x="{x+18:.1f}" y="960" font-size="13" fill="#666">{phys}</text>')
    add(f'  <text x="{x+18:.1f}" y="982" font-size="12" fill="#999">↓</text>')
    add(f'  <text x="{x+18:.1f}" y="1000" font-size="13.5" font-weight="700" fill="#222">{zpod}</text>')
add('  <text x="150" y="1046" font-size="14" fill="#444">A zPod behaves like a physical rack you own: design its networks, its storage and what runs on its hosts, '
    'without touching the rest of the lab.</text>')

# storage panel link, an annotation drawn over the rack
FBX, FBY = IX + IW / 2, z_y + z_h   # bottom centre of the zcore filer
add(f'  <path d="M{SX+SW} {SY+16} C{SX+SW+110} {SY+16} {FBX} {FBY+130} {FBX} {FBY}" stroke="#F08A3C" stroke-width="2" stroke-dasharray="2 4" stroke-linecap="round" fill="none"/>')
add(f'  <circle cx="{FBX}" cy="{FBY}" r="4" fill="#F08A3C" stroke="#fff" stroke-width="1.5"/>')
add('</svg>')
open(OUT, 'w').write('\n'.join(P) + '\n')
print('written', OUT)
