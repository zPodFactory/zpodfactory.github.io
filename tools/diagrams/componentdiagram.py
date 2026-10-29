"""Generate the component placement use case: a nested zbox on a user VLAN, reached over SSH."""
import sys

OUT = sys.argv[1]
FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'JetBrains Mono', monospace"
NAVY, ORANGE, TEAL, BLUE = "#12455F", "#E8730C", "#00796B", "#1565C0"
MGMT, YELLOW = "#4A148C", "#F2B705"
P = []
add = P.append


def router(cx, cy, fill, r=27):
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


def pill(cx, y, text, fill, fs=13, w=None, bold=False):
    w = w or (len(text) * fs * 0.6 + 18)
    wt = ' font-weight="700"' if bold else ''
    return (f'  <rect x="{cx-w/2:.1f}" y="{y}" width="{w:.1f}" height="{fs+9}" fill="{fill}"/>\n'
            f'  <text x="{cx}" y="{y+fs+3}" text-anchor="middle" font-size="{fs}" fill="#fff"{wt}>{text}</text>')


def badge(cx, cy, n, fill=BLUE, r=13):
    return (f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>\n'
            f'  <text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="{r+2}" font-weight="700" fill="#fff">{n}</text>')


def text(x, y, t, fs=13, fill='#333', anchor='start', mono=False, bold=False):
    fam = f' font-family="{MONO}"' if mono else ''
    wt = ' font-weight="700"' if bold else ''
    return f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{fs}" fill="{fill}"{fam}{wt}>{t}</text>'


W, H = 1600, 1060
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" '
    'role="img" aria-label="A user network on VLAN 42 added on zcore and advertised by the T1, a NETWORK42 portgroup '
    'on VLAN 42 in the zPod vCenter, a nested zbox deployed on it at 192.168.42.10, and the SSH path to it">')
add(f'  <rect width="{W}" height="{H}" fill="#fff"/>')

# ---- Layer bands ------------------------------------------------------------------
BX, BW = 20, 1070  # drawing area; the panel is right of it
bands = [  # (y1, y2, label, fill)
    (20, 150, 'LAB NETWORK', '#F7F9FB'),
    (150, 352, 'NSX · ENDPOINT', '#FFFFFF'),
    (352, 560, 'ENDPOINT VMS · LAYER 1', '#F7F9FB'),
    (560, 960, 'NESTED · LAYER 2', '#FFFFFF'),
]
for y1, y2, label, fill in bands:
    add(f'  <rect x="{BX}" y="{y1}" width="{BW}" height="{y2-y1}" fill="{fill}" stroke="#E3E7EB"/>')
    add(text(BX + 12, y1 + 22, label, fs=11, fill='#8A949E', bold=True))

# ---- Workstation and T0 -------------------------------------------------------------
add(f'  <rect x="160" y="52" width="250" height="74" rx="4" fill="#EEF4FB" stroke="{BLUE}" stroke-width="2"/>')
add(text(285, 78, 'Your workstation', fs=15, fill=BLUE, anchor='middle', bold=True))
add(text(285, 102, 'ssh root@192.168.42.10', fs=13, anchor='middle', mono=True))
add(badge(160, 52, 4))
add(f'  <line x1="410" y1="89" x2="670" y2="89" stroke="#8A949E" stroke-width="3"/>')
add(text(540, 81, 'lab routers learn the T0 routes', fs=11.5, fill='#666', anchor='middle'))

TX = 700
add(router(TX, 89, YELLOW))
add(pill(TX + 84, 78, 'NSX T0', YELLOW, w=78, bold=True))
add(f'  <line x1="{TX}" y1="116" x2="{TX}" y2="203" stroke="{NAVY}" stroke-width="3"/>')

# ---- T1 and its static route --------------------------------------------------------------
add(router(TX, 230, NAVY))
add(pill(TX, 264, 'NSX T1 · zPod-demo-tier1', NAVY, fs=12, w=196))
add(f'  <line x1="{TX}" y1="285" x2="{TX}" y2="330" stroke="{NAVY}" stroke-width="3"/>')
add(text(TX + 7, 304, '.1', bold=True))

add('  <rect x="812" y="174" width="258" height="104" rx="4" fill="#F5F7F9" stroke="#C5CAD0"/>')
add(text(826, 196, 'zPod-demo-tier1 static routes', fs=13, fill=NAVY, bold=True))
add(text(826, 220, '10.96.42.64/26 · 128 · 192', fs=12.5, fill='#8E24AA', mono=True))
add(text(1058, 220, '→ .2', fs=12.5, fill='#8E24AA', anchor='end'))
add(text(826, 246, '192.168.42.0/24', fs=13, fill=TEAL, mono=True, bold=True))
add(text(1058, 246, '→ 10.96.42.2', fs=13, fill=TEAL, anchor='end', mono=True, bold=True))
add(text(826, 266, 'written by routing global', fs=11.5, fill=TEAL))
add(badge(812, 174, 1))
add(f'  <line x1="{TX+28}" y1="230" x2="812" y2="230" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>')

# ---- zPod segment (trunk) ------------------------------------------------------------------
SY = 330
add(f'  <line x1="200" y1="{SY}" x2="1070" y2="{SY}" stroke="{NAVY}" stroke-width="6"/>')
add(text(200, SY - 12, '<tspan font-weight="700" fill="#12455F">zPod-demo-segment</tspan> · 802.1Q trunk', fs=12.5))
add(text(1070, SY - 12, 'VLANs 1–4094: VLAN 42 reaches zcore and every host', fs=12.5, anchor='end'))

# ---- zcore ----------------------------------------------------------------------------------
ZX = 330
add(f'  <line x1="{ZX}" y1="{SY}" x2="{ZX}" y2="392" stroke="{NAVY}" stroke-width="6"/>')
add(text(ZX + 10, 376, 'eth0 · eth1 trunk', fs=11.5, fill='#666'))
add(f'  <rect x="{ZX-150}" y="392" width="300" height="140" rx="4" fill="#FFF3E6" stroke="{ORANGE}" stroke-width="2"/>')
add(text(ZX, 416, 'zcore', fs=16, fill='#C2510F', anchor='middle', bold=True))
add(text(ZX, 434, 'DNS · DHCP · NFS · VLAN routing', fs=12, anchor='middle'))
ifs = [('eth0  mgmt', '10.96.42.2/26', MGMT, False), ('eth1.64  vlan64', '10.96.42.65/26', '#6A1B9A', False),
       ('eth1.42  net42', '192.168.42.1/24', TEAL, True)]
for i, (n, a, col, b) in enumerate(ifs):
    y = 462 + i * 24
    add(text(ZX - 136, y, n, fs=12.5, fill=col, mono=True, bold=b))
    add(text(ZX + 136, y, a, fs=12.5, fill=col, anchor='end', mono=True, bold=b))
add(badge(ZX - 150, 392, 1))

# ---- ESXi hosts --------------------------------------------------------------------------------
HX = [640, 820, 1000]
for i, hx in enumerate(HX):
    hid = 11 + i
    add(f'  <line x1="{hx}" y1="{SY}" x2="{hx}" y2="410" stroke="{NAVY}" stroke-width="4"/>')
    add(text(hx + 8, 376, 'vmnic0 · 1', fs=11.5, fill='#666'))
    add(f'  <rect x="{hx-60}" y="410" width="120" height="58" rx="3" fill="#fff" stroke="#444" stroke-width="1.5"/>')
    add(text(hx, 434, f'esxi{hid}', fs=14, anchor='middle', bold=True))
    add(text(hx, 454, f'10.96.42.{hid}', fs=12, fill=MGMT, anchor='middle', mono=True))

# ---- Nested: the zPod vCenter --------------------------------------------------------------------
VX1, VX2 = 470, 1070
add(f'  <rect x="{VX1}" y="590" width="{VX2-VX1}" height="350" rx="4" fill="none" stroke="#444" stroke-width="1.5" stroke-dasharray="6 4"/>')
for hx in HX:  # host uplinks into the nested switch
    add(f'  <line x1="{hx}" y1="468" x2="{hx}" y2="606" stroke="#444" stroke-width="2" stroke-dasharray="2 4"/>')
add(f'  <rect x="{VX1+20}" y="606" width="{VX2-VX1-40}" height="20" fill="#E9ECEF" stroke="#C5CAD0"/>')
add(text((VX1 + VX2) / 2, 621, 'a VDS, uplinks vmnic0 · vmnic1 (recommended), or the existing vSwitch0', fs=12, fill='#444', anchor='middle', bold=True))
add(text(VX1 + 44, 654, 'zPod vCenter · vcsa.demo.zpod.lab · cluster “Cluster”', fs=14, fill='#333', bold=True))

# Portgroups
PG = [  # (y, name, detail, colour, bold)
    (712, 'VM Network · untagged', 'default → mgmt 10.96.42.0/26', MGMT, False),
    (782, 'NETWORK42 · VLAN 42', 'you create it → net42 192.168.42.0/24', TEAL, True),
]
for y, name, detail, col, b in PG:
    add(f'  <line x1="{VX1+40}" y1="{y}" x2="{VX2-30}" y2="{y}" stroke="{col}" stroke-width="3"/>')
    add(text(VX1 + 70, y - 10, name, fs=13.5, fill=col, bold=True))
    add(text(VX2 - 30, y - 10, detail, fs=12, fill=col, anchor='end'))
    add(f'  <line x1="{VX1+30}" y1="626" x2="{VX1+30}" y2="{y}" stroke="#888" stroke-width="2"/>')
    add(f'  <line x1="{VX1+30}" y1="{y}" x2="{VX1+40}" y2="{y}" stroke="#888" stroke-width="2"/>')
add(badge(VX1 + 54, 767, 2))

# The zbox on NETWORK42
ZBX = 780
add(f'  <line x1="{ZBX}" y1="782" x2="{ZBX}" y2="838" stroke="{TEAL}" stroke-width="3"/>')
add(f'  <rect x="{ZBX-120}" y="838" width="240" height="78" rx="4" fill="{TEAL}"/>')
add(text(ZBX, 862, 'zbox42 · zbox-13.7.1', fs=14, fill='#fff', anchor='middle', bold=True))
add(text(ZBX, 884, '192.168.42.10/24', fs=14, fill='#fff', anchor='middle', mono=True, bold=True))
add(text(ZBX, 904, 'gateway 192.168.42.1 · DNS zcore', fs=12, fill='#E0F2F1', anchor='middle'))
add(badge(ZBX - 120, 838, 3))
add(text(ZBX + 136, 862, 'host id 10 on the', fs=12, fill='#555'))
add(text(ZBX + 136, 878, 'network that the', fs=12, fill='#555'))
add(text(ZBX + 136, 894, 'portgroup’s VLAN', fs=12, fill='#555'))
add(text(ZBX + 136, 910, 'picks: net42', fs=12, fill='#555'))

# Left of the vCenter: what zPodFactory does and doesn't do
add(f'  <g font-size="12.5" fill="#555">')
add(f'    <text x="44" y="610" font-size="13.5" font-weight="700" fill="{NAVY}">Who does what</text>')
who = [('zPodFactory', 'adds net42 on zcore, writes', 'the T1 route, deploys zbox42'),
       ('You', 'create NETWORK42 in the zPod', 'vCenter: zPodFactory never does'),
       ('The VLAN tag', 'is added by the portgroup,', 'so zbox42 sends plain frames')]
for i, (who_, l1, l2) in enumerate(who):
    y = 640 + i * 72
    add(f'    <text x="44" y="{y}" font-weight="700" fill="#333">{who_}</text>')
    add(f'    <text x="44" y="{y+18}">{l1}</text>')
    add(f'    <text x="44" y="{y+35}">{l2}</text>')
add('  </g>')

# ---- SSH path ------------------------------------------------------------------------------------
add(f'  <text x="44" y="996" font-size="13.5" font-weight="700" fill="{BLUE}">SSH path</text>')
hops = ['workstation', 'NSX T0', 'T1 route ①', 'zcore eth1.42', 'trunk · VLAN 42', 'esxi uplink', 'NETWORK42 ②', 'zbox42 ③']
x = 120
for i, h in enumerate(hops):
    w = len(h) * 7.6 + 22
    last = i == len(hops) - 1
    fill = TEAL if last else '#EEF4FB'
    col = '#fff' if last else BLUE
    add(f'  <rect x="{x:.1f}" y="980" width="{w:.1f}" height="24" rx="12" fill="{fill}" stroke="{TEAL if last else BLUE}"/>')
    add(text(x + w / 2, 997, h, fs=12.5, fill=col, anchor='middle', bold=last))
    x += w
    if not last:
        add(f'  <path d="M{x+4:.1f} 992 h12 m-5 -5 l5 5 -5 5" stroke="{BLUE}" stroke-width="2" fill="none"/>')
        x += 20
add(text(44, 1036, 'Every hop is routed: no NAT. With routing local instead of global, only the zPod reaches 192.168.42.0/24.', fs=12.5, fill='#555'))

# ---- Requirements panel ------------------------------------------------------------------------------
PX, PY, PW = 1110, 20, 470
add(f'  <rect x="{PX}" y="{PY}" width="{PW}" height="940" rx="4" fill="#FAFBFC" stroke="#C5CAD0"/>')
add(text(PX + 18, PY + 30, 'What each step needs', fs=16, fill=NAVY, bold=True))

steps = [
    (1, 'Add the network on zcore, then advertise it', [
        ('cmd', 'zcli zpod network add demo --name net42'),
        ('cmd', '\u00a0\u00a0--vlan 42 --gateway 192.168.42.1/24'),
        ('cmd', 'zcli zpod network routing demo net42 global'),
        ('chk', 'VLAN 42 free, not 10, 20, 30, 64, 128, 192'),
        ('chk', 'no overlap with the zPod or its endpoint pool'),
        ('chk', 'global: superadmin only; the flow checks'),
        ('txt', 'the whole fabric for overlaps first'),
    ]),
    (2, 'Create the portgroup in the zPod vCenter', [
        ('txt', 'Build a VDS, uplinks vmnic0 · vmnic1 (recommended),'),
        ('txt', 'or use the existing vSwitch0 of every host;'),
        ('txt', 'then add NETWORK42, VLAN 42, on either one'),
        ('chk', 'it exists: zPodFactory never creates one'),
        ('chk', 'one match for its name'),
        ('chk', 'a standard one is on every host of Cluster'),
    ]),
    (3, 'Add zbox nested, on that portgroup', [
        ('cmd', 'zcli zpod component add demo -c zbox-13.7.1'),
        ('cmd', '\u00a0\u00a0--nested=true --portgroup NETWORK42'),
        ('cmd', '\u00a0\u00a0--hostname zbox42 --host-id 10'),
        ('chk', 'the zPod vCenter exists'),
        ('chk', 'VLAN 42 has a zPod network: net42'),
        ('chk', 'host id 2–254 on it (.1 is zcore)'),
        ('no', 'no --vlan-id: the portgroup tags VLAN 42;'),
        ('txt', '--vlan-id is for trunks and ESXi images'),
        ('no', 'no --vnics: one portgroup for every NIC'),
    ]),
    (4, 'SSH in from your workstation', [
        ('cmd', 'ssh root@192.168.42.10'),
        ('txt', 'root or zadmin, with the zPod password'),
        ('txt', 'or the factory SSH key'),
    ]),
]
y = PY + 68
for n, title, lines in steps:
    add(badge(PX + 30, y - 5, n))
    add(text(PX + 52, y, title, fs=14, fill='#222', bold=True))
    y += 26
    for kind, t in lines:
        if kind == 'cmd':
            add(f'  <rect x="{PX+18}" y="{y-15}" width="{PW-36}" height="21" fill="#EEF1F4"/>')
            add(text(PX + 26, y, t, fs=12.5, fill='#222', mono=True))
            y += 21
            continue
        if kind == 'chk':
            add(f'  <path d="M{PX+24} {y-5} l4 4 8 -9" stroke="{TEAL}" stroke-width="2.2" fill="none"/>')
        elif kind == 'no':
            add(f'  <path d="M{PX+25} {y-12} l9 9 m0 -9 l-9 9" stroke="#B3261E" stroke-width="2.2" fill="none"/>')
        add(text(PX + 44, y, t, fs=13, fill='#333'))
        y += 20
    y += 26

# Why not --vlan-id
add(f'  <rect x="{PX+18}" y="{y-14}" width="{PW-36}" height="128" rx="4" fill="#FFF8E1" stroke="#F2B705"/>')
add(text(PX + 32, y + 10, 'Why not --vlan-id 42?', fs=14, fill='#7A5B00', bold=True))
why = ['--vlan-id makes the guest tag its own frames. It needs',
       'a trunk portgroup, and an image that reads {{zpod_vlan}},',
       'like ESXi. zbox doesn\u2019t: the API refuses it (422).',
       'NETWORK42 already tags VLAN 42, so zbox42 needs',
       'only --portgroup and --host-id.']
for i, l in enumerate(why):
    add(text(PX + 32, y + 34 + i * 18, l, fs=12.5, fill='#5C4600'))

add('</svg>')
open(OUT, 'w').write('\n'.join(P) + '\n')
print('written', OUT)
