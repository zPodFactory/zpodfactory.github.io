# Diagram generators

Each script writes one SVG diagram of the documentation site. They use plain Python 3 (no dependencies): every script builds the SVG markup as text and writes it to the path given on the command line.

| Script | Diagram | Used on |
| --- | --- | --- |
| `rackdiagram.py` | `docs/img/zPodFactory-zpod-rack.svg`: a zPod drawn as a physical rack, with the zcore networks and storage panels and the nested workloads | Concepts |
| `instdiagram.py` | `docs/img/zPodFactory-instance-networking.svg`: one zPod's `/24`, its VLANs, the T1 routes and the zcore interfaces | Concepts |
| `nsxdiagram.py` | `docs/img/zPodFactory-networking-nsx-overview.svg`: NSX T0/T1 layout for the `nsxt` and `nsxt_projects` drivers | Concepts |
| `endpointdiagram.py` | `docs/img/zPodFactory-topology-overview-network-endpoints.svg`: the appliance, the lab L3 network and three endpoints | Install, Endpoints |

`docs/img/zPodFactory-overview-layers.svg` and `docs/img/zPodFactory-architecture.svg` have no generator: edit those SVGs directly.

## Regenerate a diagram

From the repository root:

```bash
python3 tools/diagrams/rackdiagram.py docs/img/zPodFactory-zpod-rack.svg
python3 tools/diagrams/instdiagram.py docs/img/zPodFactory-instance-networking.svg
python3 tools/diagrams/nsxdiagram.py docs/img/zPodFactory-networking-nsx-overview.svg
python3 tools/diagrams/endpointdiagram.py docs/img/zPodFactory-topology-overview-network-endpoints.svg
```

Then check the result: open the SVG in a browser, or run `uvx zensical==0.0.67 serve` and look at the page that uses it.

## How a script is laid out

- **Settings at the top**: colours as named constants, fonts, the canvas size, and the main anchor positions (for example `RX, RY` for the rack, `PX` for the zcore networks panel, `WY` for the workloads in `rackdiagram.py`).
- **Helpers** for repeated shapes: `router()` for the round T0/T1 icon, `pill()` for coloured label bars, and in `rackdiagram.py` `unit()` for a rack device sized in rack units.
- **Sections** in drawing order, each adding SVG elements to a list that is written out at the end.

Positions are derived from a few anchors, so most layout changes are one number: moving `WY` moves the whole workloads block, the VLAN lines all end at `LEND`, and the trunk length follows the ESXi positions.

## Conventions

Keep these consistent across all diagrams:

| Element | Colour |
| --- | --- |
| 802.1Q trunk, Geneve segment, T1 to top-of-rack cable (6px) | navy `#12455F` |
| zPod networks: native, VLAN 64, 128, 192 | purples `#4A148C`, `#6A1B9A`, `#8E24AA`, `#AB47BC` |
| zcore VLANs 10, 20, 30 | ambers `#B45309`, `#D97706`, `#F59E0B` |
| User VLANs (examples 111, 200) | teals `#00796B`, `#26A69A` |
| NSX T0 | yellow `#F2B705` (`nsxdiagram.py` draws the endpoint T0 in red `#9B1B30`) |
| zcore | orange `#E8730C` |
| NSX edges | green `#2E7D32` |

- VLAN lines are 2px; workload tiles take their network's colour.
- Examples use the zPod subnet `10.96.42.0/24` and always show full IP addresses.
- Annotations (pointers between a panel and the rack) are dotted curves, so they never look like cables.
