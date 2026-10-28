"""Generate the zPodFactory NSX networking overview diagram (SVG)."""
import sys

OUT = sys.argv[1]
FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'JetBrains Mono', monospace"
NAVY, T0RED, GREEN, ORANGE, GREY = "#12455F", "#9B1B30", "#2E7D32", "#E8730C", "#555"
parts = []
add = parts.append


def router(cx, cy, fill, r=26):
    k = r / 27  # same symbol as the layers diagram's routers (r=27), scaled
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


def pill(cx, y, text, fill, w=None, fs=13, color="#fff", bold=False):
    w = w or (len(text) * fs * 0.6 + 18)
    weight = ' font-weight="700"' if bold else ''
    return (f'  <rect x="{cx-w/2:.1f}" y="{y}" width="{w:.1f}" height="{fs+9}" fill="{fill}"/>\n'
            f'  <text x="{cx}" y="{y+fs+3}" text-anchor="middle" font-size="{fs}" fill="{color}"{weight}>{text}</text>')


def badge(cx, cy, n):
    return (f'  <circle cx="{cx}" cy="{cy}" r="11" fill="{T0RED}"/>\n'
            f'  <text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">{n}</text>')


def zpod(x, y, w, name, subnet, uplink_x):
    """A zPod: dotted box, its trunk segment, zcore and three nested ESXi hosts."""
    seg_y = y + 70
    out = [f'  <!-- zPod {name} -->',
           f'  <rect x="{x}" y="{y}" width="{w}" height="300" fill="none" stroke="#777" stroke-width="2" stroke-dasharray="3 4"/>',
           f'  <line x1="{x+14}" y1="{seg_y}" x2="{x+w-14}" y2="{seg_y}" stroke="{NAVY}" stroke-width="3"/>',
           f'  <line x1="{uplink_x}" y1="{y-24}" x2="{uplink_x}" y2="{seg_y}" stroke="{NAVY}" stroke-width="3"/>',
           f'  <text x="{uplink_x+6}" y="{y+18}" font-size="12" font-family="{MONO}" fill="#333">{subnet}</text>',
           f'  <text x="{uplink_x+6}" y="{seg_y-8}" font-size="12" font-weight="700" fill="#333">.1</text>',
           f'  <text x="{x+16}" y="{seg_y-10}" font-size="12" font-weight="700" fill="{NAVY}">zPod-{name}-segment</text>',
           f'  <rect x="{x+w-78}" y="{seg_y-24}" width="62" height="17" rx="3" fill="{NAVY}"/>',
           f'  <text x="{x+w-47}" y="{seg_y-11}" text-anchor="middle" font-size="10" font-weight="700" fill="#fff" letter-spacing="0.5">GENEVE</text>']
    # zcore
    zx = x + 62
    out += [f'  <line x1="{zx}" y1="{seg_y}" x2="{zx}" y2="{seg_y+30}" stroke="{NAVY}" stroke-width="2"/>',
            f'  <text x="{zx+6}" y="{seg_y+20}" font-size="12" fill="#333">.2</text>',
            f'  <rect x="{zx-44}" y="{seg_y+30}" width="88" height="48" rx="4" fill="#FFF3E6" stroke="{ORANGE}" stroke-width="2"/>',
            f'  <text x="{zx}" y="{seg_y+50}" text-anchor="middle" font-size="14" font-weight="700" fill="#C2510F">zcore</text>',
            f'  <text x="{zx}" y="{seg_y+68}" text-anchor="middle" font-size="11" fill="#333">routes VLANs</text>']
    # ESXi hosts
    for i, hid in enumerate((11, 12, 13)):
        ex = x + 140 + i * 52
        out += [f'  <line x1="{ex}" y1="{seg_y}" x2="{ex}" y2="{seg_y+36}" stroke="{NAVY}" stroke-width="2"/>',
                f'  <text x="{ex+4}" y="{seg_y+20}" font-size="11" fill="#333">.{hid}</text>',
                f'  <rect x="{ex-21}" y="{seg_y+36}" width="42" height="30" rx="3" fill="#fff" stroke="#444" stroke-width="1.5"/>',
                f'  <text x="{ex}" y="{seg_y+56}" text-anchor="middle" font-size="11">ESXi</text>']
    # VLANs carried on the trunk
    vy = seg_y + 112
    out += [f'  <text x="{x+16}" y="{vy}" font-size="12" fill="#333">native <tspan font-family="{MONO}">.0/26</tspan> · management, via the T1</text>',
            f'  <text x="{x+16}" y="{vy+18}" font-size="12" fill="#333">VLANs 64 · 128 · 192 <tspan font-family="{MONO}">/26</tspan> · via zcore</text>',
            f'  <text x="{x+16}" y="{vy+36}" font-size="12" fill="#00796B">+ your own VLANs on zcore</text>',
            f'  <text x="{x+w/2}" y="{y+288}" text-anchor="middle" font-size="18" fill="#444">zPod <tspan font-weight="700">{name}</tspan></text>']
    return '\n'.join(out)


W, H = 1600, 800
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" '
    'role="img" aria-label="zPodFactory NSX networking: each zPod gets its own NSX T1 and Geneve segment, '
    'optionally inside an NSX Project, routed to the endpoint T0">')
add('  <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0 0 L10 5 L0 10 z" fill="#666"/></marker></defs>')
add(f'  <rect width="{W}" height="{H}" fill="#fff"/>')

# ---- Management + upstream -----------------------------------------------------
add('  <!-- zPodFactory management -->')
add('  <rect x="330" y="26" width="470" height="168" fill="none" stroke="#777" stroke-width="2" stroke-dasharray="3 4"/>')
add('  <rect x="372" y="64" width="96" height="56" rx="4" fill="#fff" stroke="#444" stroke-width="1.5"/>')
add('  <text x="420" y="88" text-anchor="middle" font-size="12" fill="#666">vm</text>')
add('  <text x="420" y="106" text-anchor="middle" font-size="12" font-weight="700" fill="#222">zPodFactory</text>')
add('  <text x="420" y="138" text-anchor="middle" font-size="12" fill="#444">appliance · zpodweb :8500</text>')
add(f'  <line x1="468" y1="92" x2="664" y2="92" stroke="{ORANGE}" stroke-width="3"/>')
add(f'  <text x="566" y="84" text-anchor="middle" font-size="12" fill="#444">zPodFactory network</text>')
add(f'  <text x="566" y="110" text-anchor="middle" font-size="12" font-family="{MONO}" fill="#333">10.30.1.0/24</text>')
add('  <text x="476" y="110" font-size="12" font-weight="700" fill="#333">.10</text>')
add(router(690, 92, '#F2B705'))
add('  <text x="654" y="110" text-anchor="end" font-size="12" font-weight="700" fill="#333">.1</text>')
add(pill(690, 126, 'T1', '#F2B705', w=60, bold=True))
add('  <text x="565" y="182" text-anchor="middle" font-size="17" fill="#444">zPodFactory management</text>')

add(f'  <line x1="690" y1="148" x2="690" y2="218" stroke="#777" stroke-width="3"/>')
add(f'  <line x1="1176" y1="92" x2="1258" y2="92" stroke="#777" stroke-width="3"/>')
add(f'  <line x1="1362" y1="92" x2="1416" y2="92" stroke="#C62828" stroke-width="3"/>')
add(router(1150, 92, T0RED))
add(pill(1150, 126, 'NSX T0', T0RED, w=86, bold=True))
cx = 1310
add('  <!-- Physical network: spine-leaf fabric -->')
add(f'  <rect x="{cx-52}" y="46" width="104" height="72" rx="8" fill="#F4F4F4" stroke="#444" stroke-width="2"/>')
add('  <path d="' + ' '.join(f'M{sx} 64 L{lx} 96' for sx in (cx-22, cx+22) for lx in (cx-34, cx, cx+34)) + '" stroke="#777" stroke-width="1.5" fill="none"/>')
for sx in (cx-22, cx+22):
    add(f'  <rect x="{sx-12}" y="54" width="24" height="11" rx="2" fill="#444"/>')
for lx in (cx-34, cx, cx+34):
    add(f'  <rect x="{lx-12}" y="96" width="24" height="11" rx="2" fill="#444"/>')
add(pill(1310, 126, 'Physical network', '#444', fs=12))
add('  <rect x="1416" y="66" width="164" height="52" rx="26" fill="#fff" stroke="#C62828" stroke-width="4"/>')
add('  <text x="1498" y="100" text-anchor="middle" font-size="20" font-weight="700" fill="#C62828">INTERNET</text>')

# ---- T0 <-> T1 auto-plumbing ---------------------------------------------------
add(f'  <line x1="1150" y1="148" x2="1150" y2="218" stroke="#777" stroke-width="3"/>')
add('  <rect x="330" y="218" width="1000" height="36" fill="#E9ECEF" stroke="#C5CAD0" stroke-width="1"/>')
add('  <text x="830" y="241" text-anchor="middle" font-size="14" fill="#444">NSX T0 ↔ T1 auto-plumbing · '
    f'<tspan font-family="{MONO}">100.64.0.0/16</tspan> transit</text>')

# ---- NSX Project (ENet): two zPods sharing a T1 ---------------------------------
add('  <!-- NSX Project with a shared T1 (ENet) -->')
add(f'  <rect x="330" y="282" width="636" height="500" fill="none" stroke="{GREEN}" stroke-width="2" stroke-dasharray="4 4"/>')
add(f'  <line x1="648" y1="254" x2="648" y2="302" stroke="#777" stroke-width="3"/>')
add(router(648, 328, '#4CAF50'))
add(pill(648, 360, 'T1 · shared by the ENet', '#4CAF50', fs=12))
# T1 to each zPod segment
add(f'  <path d="M648 382 V398 M490 398 H806" stroke="{NAVY}" stroke-width="3" fill="none"/>')
add(zpod(344, 422, 296, 'a', '10.96.1.0/24', 490))
add(zpod(656, 422, 296, 'b', '10.96.2.0/24', 806))
add(f'  <text x="648" y="774" text-anchor="middle" font-size="16" fill="{GREEN}">NSX Project · ENet <tspan font-size="13" fill="#555">(nsxt_projects endpoint)</tspan></text>')
# static routes from the shared T1 to zPod a's zcore
add(f'  <path d="M622 330 H362 Q350 330 350 342 V546 H353" stroke="#666" stroke-width="2" stroke-dasharray="6 4" fill="none"/>')
add('  <path d="M352 540.5 L361 546 L352 551.5 Z" fill="#666"/>')
add('  <text x="400" y="319" font-size="12" fill="#444">T1 static routes → zcore</text>')
add(badge(382, 314, 1))
add(badge(545, 638, 2))
add(badge(352, 762, 3))

# ---- zPod with its own T1 (nsxt endpoint) ---------------------------------------
add('  <!-- zPod with its own T1 -->')
add(f'  <line x1="1150" y1="254" x2="1150" y2="302" stroke="#777" stroke-width="3"/>')
add(router(1150, 328, NAVY))
add(pill(1150, 360, 'zPod-c-tier1', NAVY, fs=12))
add(zpod(1002, 422, 296, 'c', '10.96.3.0/24', 1150))
add(f'  <line x1="1150" y1="382" x2="1150" y2="398" stroke="{NAVY}" stroke-width="3"/>')
add('  <text x="1150" y="774" text-anchor="middle" font-size="13" fill="#555">nsxt endpoint: one T1 per zPod</text>')

# Trunk explanation (right)
add('  <path d="M1316 486 q10 0 10 10 v16 q0 8 8 8 q-8 0 -8 8 v16 q0 10 -10 10" stroke="#555" stroke-width="2" fill="none"/>')
add('  <g font-size="13" fill="#333">')
add('    <text x="1344" y="508">Geneve segment, 802.1Q trunk:</text>')
add('    <text x="1344" y="527">native VLAN untagged,</text>')
add('    <text x="1344" y="546">VLANs 0–4094 tagged</text>')
add('  </g>')

# ---- Guardrails (left) -------------------------------------------------------------
add('  <g font-size="13" fill="#333">')
add(f'    <text x="22" y="300" font-size="16" font-weight="700" fill="{NAVY}">Routing guardrails</text>')
notes = [
    (1, 340, ["Only each zPod's /24 reaches the T0:",
              "the native /26 lives on the T1, and",
              "VLANs 64, 128 and 192 are routed to",
              "zcore by T1 static routes. zPodFactory",
              "sets them; users cannot change them."]),
    (2, 470, ["Owners add their own VLANs on zcore.",
              "They stay inside the zPod (masquerade",
              "for egress) unless a superadmin",
              "advertises them: zPodFactory checks",
              "the whole fabric for overlaps first,",
              "then adds a T1 static route to zcore."]),
    (3, 630, ["On nsxt_projects endpoints, a zPod",
              "gets its own NSX Project, or shares",
              "one (and its T1) with the other zPods",
              "of an ENet. Needs NSX 4.1.1 or later."]),
]
add('  </g>')
for n, y0, lines in notes:
    add(badge(34, y0 - 5, n))
    for i, l in enumerate(lines):
        add(f'  <text x="54" y="{y0 + i*19}" font-size="13" fill="#333">{l}</text>')

add('</svg>')
open(OUT, 'w').write('\n'.join(parts) + '\n')
print('written', OUT)
