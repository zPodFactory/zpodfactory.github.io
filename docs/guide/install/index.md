# Install zPodFactory

zPodFactory is installed as a pre-built appliance (OVA) on the vSphere environment that will host your zPods. Read the requirements first: nested environments need a fair amount of compute, storage and network plumbing on the physical side.

See [Concepts & architecture](../concepts.md) for how the layers fit together.

## Requirements

### Physical environment

- **vCenter Server 7.0u3 or later.**
    - At least `4 vCPU / 16GB RAM / 250GB storage` (SSD/NVMe recommended) for the zPodFactory appliance.
    - The appliance starts with a 50GB disk. Usage grows with the products you download; the disk can be extended with LVM, and 500GB+ is recommended if you plan to use many products.
- **NSX-T 3.1 or later** for an `nsxt` endpoint, the recommended driver. The optional `nsxt_projects` driver needs **NSX 4.1.1 or later**, and is not recommended for new endpoints (see [NSX networking](../concepts.md#nsx-networking)).
    - T0 and T1 gateways deployed and configured for north/south connectivity (a T1 can host the appliance).
    - A supernet for zPods, for example `10.10.0.0/20`: each zPod gets a `/24` from it, carved into four `/26` networks (see [zPod networks](../concepts.md#zpod-networks)).
    - Change the NSX default DLR MAC address first; see [this FAQ entry](../../faq/faq.md#why-does-preparing-nsx-hosts-break-my-zpod).
- **Fast storage** (SSD/NVMe; vSAN OSA/ESA recommended), 4TB or more depending on how many zPods you plan to run. On a vSAN physical environment, see [this FAQ entry](../../faq/faq.md#why-does-creating-a-vsan-datastore-fails-in-my-zpod).

> Sizing is an "it depends" answer: scale it to the number and size of the zPods you expect.

### Network requirements

Here is an example of the networking we use in our lab, with one or more [endpoints](../admin/endpoints.md) (a vCenter and NSX pair with a zPod supernet):

![zPodFactory endpoints and network connectivity](../../img/zPodFactory-topology-overview-network-endpoints.svg)

- `eth0`: interface connected to a public IP (internet).
- `eth1`: interface connected to the whole lab private network (L3/BGP fabric).

The appliance needs L3 connectivity to:

- **vCenter Server and the ESXi hosts**, for the API and for OVA/OVF uploads;
- **NSX Manager**, for its API;
- **the networks NSX provisions for the zPods**, to deploy and configure the nested components (OVF deploys, connections to the nested ESXi hosts, and so on).

## Deploy the appliance

The appliance is a pre-built VM with everything zPodFactory needs, installed and configured at first boot.

!!! warning
    Set the OVF properties correctly, and make sure the appliance's network gives it internet access: the installation stops if it cannot reach the internet.

- :material-calendar: 06/2026 - zPodFactory Appliance latest:
    - :material-download: [Download OVA](https://cloud.tsugliani.fr/ova/zpodfactory.ova)
    - :simple-github: [Git Commit Log](https://github.com/zPodFactory/zpodcore/commits/main/)

The appliance runs the full stack (**zPod API**, **zPod Engine**, **zcli**) plus **[zpodweb](https://github.com/zPodFactory/zpodweb)**, the Web UI, on port **8500**.

## Next steps

1. Browse to `http://<appliance-ip>:8500` and open the [Web UI](../user/web-ui.md).
2. [Set up the zPod CLI (zcli)](../zcli.md) on your workstation, if you prefer the command line.
3. As an administrator, review the [settings](../admin/feature-flags.md), set the [Broadcom download token](../admin/broadcom-download-token.md), create an [endpoint](../admin/endpoints.md), enable [components](../admin/components.md) and build [profiles](../admin/profiles.md).
4. To keep the factory up to date, see [Upgrading](../admin/upgrade.md).
