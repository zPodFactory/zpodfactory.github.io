"""Generate the zPodFactory endpoints & network requirements diagram (SVG)."""
import sys

OUT = sys.argv[1]
FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'JetBrains Mono', monospace"
NAVY, ORANGE, T0C, GREY = "#12455F", "#E8730C", "#F2B705", "#777"
P = []
add = P.append


def router(cx, cy, fill, r=22):
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


W, H = 1600, 840
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" '
    'role="img" aria-label="zPodFactory endpoints and network requirements: the appliance reaches the Internet on eth0 '
    'and, on eth1, every endpoint vCenter, NSX Manager and zPod supernet across the lab L3 network">')
add('  <defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
    f'<path d="M0 0 L10 5 L0 10 z" fill="{GREY}"/></marker></defs>')
add(f'  <rect width="{W}" height="{H}" fill="#fff"/>')

# ---- Internet and the appliance ------------------------------------------------------------
AX = 800
add(f'  <rect x="{AX-75}" y="24" width="150" height="40" rx="20" fill="#fff" stroke="#C62828" stroke-width="3"/>')
add(f'  <text x="{AX}" y="50" text-anchor="middle" font-size="16" font-weight="700" fill="#C62828">INTERNET</text>')
# eth0: SNAT out for the download engine, optional DNAT in for WireGuard
add(f'  <line x1="{AX+14}" y1="164" x2="{AX+14}" y2="68" stroke="{GREY}" stroke-width="3" marker-end="url(#ar)"/>')
add(f'  <line x1="{AX-14}" y1="68" x2="{AX-14}" y2="164" stroke="{GREY}" stroke-width="3" stroke-dasharray="3 4" marker-end="url(#ar)"/>')
add(f'  <text x="{AX+30}" y="102" font-size="12" font-weight="700" fill="#C2510F">SNAT / masquerade</text>')
add(f'  <text x="{AX+30}" y="118" font-size="12" fill="#555">to the Internet, for the download engine</text>')
add(f'  <text x="{AX-30}" y="102" text-anchor="end" font-size="12" font-weight="700" fill="#C2510F">DNAT port <tspan font-weight="400" fill="#888">(optional)</tspan></text>')
add(f'  <text x="{AX-30}" y="118" text-anchor="end" font-size="12" fill="#555">for WireGuard access</text>')
add(f'  <text x="{AX+22}" y="160" font-size="11" font-family="{MONO}" fill="#666">eth0 · public</text>')

add(f'  <rect x="{AX-70}" y="168" width="140" height="62" rx="4" fill="#fff" stroke="#444" stroke-width="1.5"/>')
add(f'  <rect x="{AX-70}" y="168" width="6" height="62" fill="{ORANGE}"/>')
add(f'  <text x="{AX+3}" y="192" text-anchor="middle" font-size="12" fill="#666">vm</text>')
add(f'  <text x="{AX+3}" y="212" text-anchor="middle" font-size="14" font-weight="700" fill="#222">zPodFactory</text>')
add(f'  <text x="{AX+3}" y="246" text-anchor="middle" font-size="12" fill="#444">appliance · zpodweb :8500</text>')
add(f'  <line x1="{AX}" y1="254" x2="{AX}" y2="318" stroke="{GREY}" stroke-width="3"/>')
add(f'  <text x="{AX+10}" y="290" font-size="11" font-family="{MONO}" fill="#666">eth1 · lab</text>')

# requirements card, right of the appliance
RX, RY = 1020, 150
add(f'  <rect x="{RX}" y="{RY}" width="520" height="130" rx="6" fill="#FAFAFB" stroke="#DDE1E6"/>')
add(f'  <text x="{RX+18}" y="{RY+26}" font-size="13" font-weight="700" fill="#C2510F">zPodFactory needs L3 access to</text>')
for i, (what, why) in enumerate((('each endpoint vCenter and its ESXi hosts', 'HTTPS API, OVA uploads'),
                                 ('each endpoint NSX Manager', 'HTTPS API'),
                                 ('each endpoint zPod supernet', 'deploy and configure zPods'))):
    y = RY + 54 + i * 24
    add(f'  <circle cx="{RX+24}" cy="{y-4}" r="3" fill="{NAVY}"/>')
    add(f'  <text x="{RX+36}" y="{y}" font-size="12.5" fill="#333"><tspan font-weight="700">{what}</tspan> <tspan fill="#777">· {why}</tspan></text>')
add(f'  <path d="M{AX+70} 199 C{AX+140} 199 {RX-80} {RY+65} {RX} {RY+65}" stroke="#C5CAD0" stroke-width="1.5" stroke-dasharray="3 4" fill="none"/>')

# ---- Lab L3 network: a muted band, spine-leaf icon on the left --------------------------------
BY, BH = 318, 56
add(f'  <rect x="60" y="{BY}" width="{W-120}" height="{BH}" rx="6" fill="#EEF0F2" stroke="#C5CAD0"/>')
ix = 84
add(f'  <rect x="{ix}" y="{BY+8}" width="64" height="40" rx="5" fill="#F8F8F8" stroke="#444" stroke-width="1.5"/>')
add('  <path d="' + ' '.join(f'M{sx} {BY+18} L{lx} {BY+36}' for sx in (ix+20, ix+44) for lx in (ix+12, ix+32, ix+52)) + '" stroke="#888" stroke-width="1.2" fill="none"/>')
for sx in (ix + 20, ix + 44):
    add(f'  <rect x="{sx-8}" y="{BY+13}" width="16" height="6" rx="1.5" fill="#444"/>')
for lx in (ix + 12, ix + 32, ix + 52):
    add(f'  <rect x="{lx-8}" y="{BY+36}" width="16" height="6" rx="1.5" fill="#444"/>')
add(f'  <text x="{ix+82}" y="{BY+25}" font-size="14" font-weight="700" fill="#444">Lab L3 network</text>')
add(f'  <text x="{ix+82}" y="{BY+43}" font-size="12" fill="#666">routed fabric (BGP) · every endpoint supernet must be unique, no overlapping IPs</text>')

# ---- Endpoints --------------------------------------------------------------------------------
EP = [('Endpoint A', 'nsxt', '10.96.0.0/16'),
      ('Endpoint B', 'nsxt', '10.97.0.0/16'),
      ('Endpoint C', 'nsxt', '10.98.0.0/16')]
CW, CH, CY = 440, 350, 450
for k, (name, driver, net) in enumerate(EP):
    x = (W - 3 * CW - 2 * 40) / 2 + k * (CW + 40)
    cx = x + CW / 2
    add(f'  <!-- {name} -->')
    add(f'  <line x1="{cx}" y1="{BY+BH}" x2="{cx}" y2="{CY}" stroke="{GREY}" stroke-width="3"/>')
    add(f'  <rect x="{x}" y="{CY}" width="{CW}" height="{CH}" rx="6" fill="#fff" stroke="#C5CAD0"/>')
    add(f'  <rect x="{x}" y="{CY}" width="6" height="{CH}" rx="2" fill="{NAVY}"/>')
    add(f'  <text x="{x+24}" y="{CY+32}" font-size="16" font-weight="700" fill="{NAVY}">{name}</text>')
    dw = len(driver) * 7 + 52
    add(f'  <rect x="{x+CW-18-dw}" y="{CY+17}" width="{dw}" height="20" rx="10" fill="#EEF4F7" stroke="{NAVY}"/>')
    add(f'  <text x="{x+CW-18-dw/2}" y="{CY+31}" text-anchor="middle" font-size="11" fill="{NAVY}">driver <tspan font-family="{MONO}" font-weight="700">{driver}</tspan></text>')
    # vCenter, NSX Manager, datastore
    tiles = (('vCenter', 'vcsa', 'API · OVA uploads'), ('NSX Manager', 'nsx', 'API'), ('Datastore', 'vSAN', 'zPod VMs'))
    tw, ty = 124, CY + 58
    for j, (t, sub, use) in enumerate(tiles):
        tx = x + 24 + j * (tw + 10)
        if t == 'Datastore':
            add(f'  <rect x="{tx}" y="{ty}" width="{tw}" height="54" rx="4" fill="#fff" stroke="{NAVY}" stroke-width="1.5"/>')
            for e in range(3):
                add(f'  <ellipse cx="{tx+22}" cy="{ty+15+e*10}" rx="10" ry="3.5" fill="#fff" stroke="{NAVY}" stroke-width="1.3"/>')
            add(f'  <text x="{tx+40}" y="{ty+24}" font-size="12" font-weight="700" fill="{NAVY}">{t}</text>')
            add(f'  <text x="{tx+40}" y="{ty+40}" font-size="11" fill="#666">{sub}</text>')
        else:
            add(f'  <rect x="{tx}" y="{ty}" width="{tw}" height="54" rx="4" fill="{NAVY}"/>')
            add(f'  <text x="{tx+tw/2}" y="{ty+24}" text-anchor="middle" font-size="12.5" font-weight="700" fill="#fff">{t}</text>')
            add(f'  <text x="{tx+tw/2}" y="{ty+41}" text-anchor="middle" font-size="11" font-family="{MONO}" fill="#BFD3E0">{sub}</text>')
        add(f'  <text x="{tx+tw/2}" y="{ty+72}" text-anchor="middle" font-size="11" fill="#777">{use}</text>')
    # ESXi cluster
    ey = CY + 158
    add(f'  <text x="{x+24}" y="{ey}" font-size="11.5" font-weight="700" fill="#444">vSphere cluster</text>')
    for j in range(4):
        add(f'  <rect x="{x+24+j*102}" y="{ey+8}" width="94" height="24" rx="3" fill="#C9D1D9" stroke="#8C97A3"/>')
        add(f'  <text x="{x+24+j*102+47}" y="{ey+25}" text-anchor="middle" font-size="11" font-weight="700" fill="#2B3540">ESXi</text>')
    # T0 and the zPod supernet
    t0y = CY + 220
    add(router(x + 50, t0y + 22, T0C))
    add(f'  <text x="{x+82}" y="{t0y+18}" font-size="13" font-weight="700" fill="#8A6A00">NSX T0</text>')
    add(f'  <text x="{x+82}" y="{t0y+35}" font-size="11" fill="#666">one T1 per zPod hangs off it</text>')
    add(f'  <rect x="{x+24}" y="{t0y+58}" width="{CW-48}" height="56" rx="4" fill="#FFFBEA" stroke="{T0C}" stroke-width="1.5"/>')
    add(f'  <text x="{x+38}" y="{t0y+78}" font-size="11.5" font-weight="700" fill="#8A6A00">zPod supernet <tspan font-weight="400" fill="#888">· "networks"</tspan></text>')
    add(f'  <text x="{x+38}" y="{t0y+101}" font-size="16" font-weight="700" font-family="{MONO}" fill="#333">{net}</text>')
    add(f'  <text x="{x+CW-38}" y="{t0y+101}" text-anchor="end" font-size="11" fill="#555">one /24 per zPod</text>')
    add(f'  <line x1="{x+50}" y1="{t0y+44}" x2="{x+50}" y2="{t0y+58}" stroke="{T0C}" stroke-width="1.5" stroke-dasharray="3 3"/>')

add('</svg>')
open(OUT, 'w').write('\n'.join(P) + '\n')
