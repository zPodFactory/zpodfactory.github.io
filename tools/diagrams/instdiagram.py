"""Generate the zPod networking diagram (one zPod's /24, its VLANs, T1 and zcore)."""
import sys

OUT = sys.argv[1]
FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'JetBrains Mono', monospace"
NAVY, ORANGE, TEAL, BLUE = "#12455F", "#E8730C", "#00796B", "#1565C0"
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


def chip(x, y, text, fill, w=96):
    return (f'  <rect x="{x}" y="{y}" width="{w}" height="22" fill="{fill}"/>\n'
            f'  <text x="{x+w/2}" y="{y+16}" text-anchor="middle" font-size="13" fill="#fff">{text}</text>')


W, H = 1600, 860
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" '
    'role="img" aria-label="Networking of one zPod: its /24 carved into four /26 networks on a Geneve trunk segment, '
    'routed by the NSX T1 and by zcore, plus zcore VLANs and the owner\'s own VLANs">')
add(f'  <rect width="{W}" height="{H}" fill="#fff"/>')

# ---- T0 / T1 ------------------------------------------------------------------------
TX = 680
add(router(TX, 70, '#F2B705'))
add(pill(TX, 104, 'NSX T0', '#F2B705', w=86, bold=True))
add(f'  <line x1="{TX}" y1="126" x2="{TX}" y2="183" stroke="{NAVY}" stroke-width="3"/>')
add(router(TX, 210, NAVY))
add(f'  <line x1="{TX}" y1="237" x2="{TX}" y2="246" stroke="{NAVY}" stroke-width="3"/>')
add(pill(TX, 246, 'NSX T1 · zPod-test-tier1', NAVY, fs=12))
add(f'  <line x1="{TX}" y1="267" x2="{TX}" y2="378" stroke="{NAVY}" stroke-width="3"/>')
add(f'  <text x="{TX+7}" y="300" font-size="13" font-weight="700" fill="#333">.1</text>')

# T1 routing table
add('  <!-- T1 routing table -->')
add('  <g transform="translate(50 0)">')
add('  <rect x="770" y="150" width="470" height="176" rx="4" fill="#F5F7F9" stroke="#C5CAD0"/>')
add(f'  <text x="786" y="174" font-size="14" font-weight="700" fill="{NAVY}">zPod-test-tier1 routing</text>')
rows = [
    ('connected', f'<tspan font-family="{MONO}">10.96.42.0/26</tspan>  gateway 10.96.42.1 (native VLAN)', '#4A148C'),
    ('static', f'<tspan font-family="{MONO}">10.96.42.64/26</tspan>   → 10.96.42.2 (zcore)', '#6A1B9A'),
    ('static', f'<tspan font-family="{MONO}">10.96.42.128/26</tspan>  → 10.96.42.2 (zcore)', '#8E24AA'),
    ('static', f'<tspan font-family="{MONO}">10.96.42.192/26</tspan>  → 10.96.42.2 (zcore)', '#AB47BC'),
    ('static', f'<tspan font-family="{MONO}">10.42.200.0/24</tspan>   → 10.96.42.2 (advertised user VLAN)', '#26A69A'),
]
for i, (kind, txt, col) in enumerate(rows):
    y = 200 + i * 24
    add(f'  <text x="786" y="{y}" font-size="11" fill="#777">{kind}</text>')
    add(f'  <text x="852" y="{y}" font-size="13" fill="{col}">{txt}</text>')
add('  </g>')
add(f'  <line x1="{TX+30}" y1="210" x2="820" y2="210" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>')

# ---- Segment -----------------------------------------------------------------------
SY = 380
add(f'  <line x1="460" y1="{SY}" x2="1572" y2="{SY}" stroke="{NAVY}" stroke-width="3"/>')
add(f'  <circle cx="1572" cy="{SY}" r="4" fill="{NAVY}"/>')
add(f'  <text x="1490" y="{SY-12}" text-anchor="end" font-size="14" fill="#333"><tspan font-weight="700" fill="{NAVY}">zPod-test-segment</tspan> · 802.1Q trunk</text>')
add(f'  <rect x="1500" y="{SY-29}" width="72" height="20" rx="3" fill="{NAVY}"/>')
add(f'  <text x="1536" y="{SY-14}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff" letter-spacing="0.5">GENEVE</text>')
add(f'  <text x="1572" y="{SY+22}" text-anchor="end" font-size="12" fill="#555">native VLAN untagged · VLANs 1–4094 tagged</text>')

# ---- VLAN ladder (left) ------------------------------------------------------------
LX = 460  # trunk riser
add(f'  <line x1="{LX}" y1="{SY}" x2="{LX}" y2="772" stroke="{NAVY}" stroke-width="6"/>')
add(chip(300, SY - 11, 'native VLAN', '#4A148C', w=110))
add(f'  <text x="300" y="{SY-18}" font-size="12" font-family="{MONO}" fill="#333">10.96.42.0/26</text>')
add(f'  <line x1="410" y1="{SY}" x2="{LX}" y2="{SY}" stroke="{NAVY}" stroke-width="3"/>')

ladder = [  # (y, chip, subnet, colour)
    (450, 'VLAN 64', '10.96.42.64/26', '#6A1B9A'),
    (500, 'VLAN 128', '10.96.42.128/26', '#8E24AA'),
    (550, 'VLAN 192', '10.96.42.192/26', '#AB47BC'),
    (614, 'VLAN 10 · 20 · 30', '172.16.10–30.0/24', '#D97706'),
    (690, 'VLAN 111', '10.42.111.0/24', '#00796B'),
    (760, 'VLAN 200', '10.42.200.0/24', '#26A69A'),
]
for y, name, net, col in ladder:
    w = 140 if '·' in name else 96
    add(chip(LX - 18 - w, y - 11, name, col, w=w))
    add(f'  <text x="{LX-18-w}" y="{y-18}" font-size="12" font-family="{MONO}" fill="#333">{net}</text>')
    add(f'  <line x1="{LX-18}" y1="{y}" x2="{LX}" y2="{y}" stroke="{col}" stroke-width="3"/>')

# Braces and captions
def brace(x, y1, y2, label_lines, col='#555'):
    m = (y1 + y2) / 2
    add(f'  <path d="M{x} {y1} q-10 0 -10 10 V{m-8} q0 8 -8 8 q8 0 8 8 V{y2-10} q0 10 10 10" stroke="{col}" stroke-width="1.6" fill="none"/>')
    for i, l in enumerate(label_lines):
        add(f'  <text x="{x-24}" y="{m - (len(label_lines)-1)*8 + i*17 + 4}" text-anchor="end" font-size="13" fill="{col}">{l}</text>')

brace(296, 424, 562, ['tagged /26s', 'routed by zcore,', 'reached through', 'T1 static routes'], '#8E24AA')
brace(296, 588, 626, ['zcore VLANs', 'for nested VCF'], '#D97706')
# Your own VLANs box
add(f'  <rect x="22" y="650" width="428" height="140" rx="4" fill="none" stroke="{TEAL}" stroke-width="2"/>')
add(f'  <rect x="22" y="650" width="196" height="22" fill="{TEAL}"/>')
add('  <text x="120" y="666" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">YOUR OWN VLANS · 0.9.0</text>')
add(f'  <g font-size="12.5" fill="{TEAL}">')
add('    <text x="34" y="694">local, with masquerade</text>')
add('    <text x="34" y="710">for egress</text>')
add('    <text x="34" y="764">global: advertised by a</text>')
add('    <text x="34" y="780">superadmin (T1 route)</text>')
add('  </g>')

# ---- zcore -----------------------------------------------------------------------------
ZX = 620
add(f'  <line x1="{ZX}" y1="{SY}" x2="{ZX}" y2="416" stroke="{NAVY}" stroke-width="2"/>')
add(f'  <text x="{ZX+6}" y="402" font-size="13" fill="#333">.2</text>')
add(f'  <text x="{ZX-8}" y="402" text-anchor="end" font-size="11" fill="#666">eth0</text>')
add(f'  <rect x="{ZX-86}" y="416" width="172" height="64" rx="4" fill="#FFF3E6" stroke="{ORANGE}" stroke-width="2"/>')
add(f'  <text x="{ZX}" y="440" text-anchor="middle" font-size="16" font-weight="700" fill="#C2510F">zcore</text>')
add(f'  <text x="{ZX}" y="458" text-anchor="middle" font-size="12" fill="#333">DNS · DHCP · NFS</text>')
add(f'  <text x="{ZX}" y="473" text-anchor="middle" font-size="12" fill="#333">zboxapi · VLAN routing</text>')
# eth1 trunk from the riser
add(f'  <line x1="{LX}" y1="448" x2="{ZX-86}" y2="448" stroke="{NAVY}" stroke-width="6"/>')
add(f'  <text x="{LX+8}" y="442" font-size="11" fill="#666">eth1 · trunk</text>')

# zcore interfaces
add('  <!-- zcore interfaces -->')
add('  <rect x="500" y="500" width="250" height="220" rx="4" fill="#FFFAF4" stroke="#F0C9A2"/>')
add('  <text x="514" y="522" font-size="13" font-weight="700" fill="#C2510F">zcore interfaces</text>')
ifs = [('eth0', '10.96.42.2/26', '#4A148C'), ('eth1.64', '10.96.42.65/26', '#6A1B9A'), ('eth1.128', '10.96.42.129/26', '#8E24AA'),
       ('eth1.192', '10.96.42.193/26', '#AB47BC'), ('eth1.10/20/30', '172.16.x.1/24', '#D97706'),
       ('eth1.111', '10.42.111.1/24', '#00796B'), ('eth1.200', '10.42.200.1/24', '#26A69A')]
for i, (n, a, col) in enumerate(ifs):
    y = 546 + i * 24
    add(f'  <text x="514" y="{y}" font-size="12.5" font-family="{MONO}" fill="{col}">{n}</text>')
    add(f'  <text x="736" y="{y}" text-anchor="end" font-size="12.5" font-family="{MONO}" fill="{col}">{a}</text>')

# ---- ESXi hosts ------------------------------------------------------------------------
for i, hid in enumerate((11, 12, 13)):
    ex = 880 + i * 150
    add(f'  <line x1="{ex}" y1="{SY}" x2="{ex}" y2="420" stroke="{NAVY}" stroke-width="2"/>')
    add(f'  <text x="{ex+6}" y="402" font-size="13" fill="#333">.{hid}</text>')
    add(f'  <rect x="{ex-30}" y="420" width="60" height="42" rx="3" fill="#fff" stroke="#444" stroke-width="1.5"/>')
    add(f'  <text x="{ex}" y="446" text-anchor="middle" font-size="12">ESXi</text>')
    add(f'  <text x="{ex}" y="482" text-anchor="middle" font-size="13">esxi{hid}</text>')

# ---- Explanation -------------------------------------------------------------------------
add(f'  <g font-size="14" fill="#333">')
add(f'    <text x="800" y="540" font-size="16" font-weight="700" fill="{NAVY}">One /24 per zPod, carved into four /26</text>')
lines = [
    ('', 576, 'The first /26 is the <tspan font-weight="700">native VLAN</tspan>, routed by the zPod\'s T1 (.1): the management network of the components.'),
    ('', 612, '<tspan font-weight="700">VLANs 64, 128 and 192</tspan> are routed by zcore through T1 static routes: for TEPs, uplinks or workloads.'),
    ('', 648, '<tspan font-weight="700">VLANs 10, 20 and 30</tspan> belong to zcore, for nested VCF, and stay inside the zPod.'),
    (TEAL, 684, '<tspan font-weight="700">Your own VLANs</tspan>: add them on zcore. They stay inside the zPod (masquerade for egress)'),
    (TEAL, 704, 'until a superadmin advertises them, after zPodFactory checks the fabric for overlaps.'),
]
for col, y, t in lines:
    fill = f' fill="{col}"' if col else ''
    add(f'    <text x="800" y="{y}"{fill}>{t}</text>')
add('  </g>')

add('</svg>')
open(OUT, 'w').write('\n'.join(P) + '\n')
print('written', OUT)
