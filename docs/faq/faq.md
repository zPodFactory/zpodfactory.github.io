# FAQ

Answers that moved to the guides:

- How zPod DNS works: [DNS records](../guide/user/dns.md#how-zpod-dns-works)
- The download engine, and why a product may be missing: [Libraries & components](../guide/admin/components.md#download-engine)
- Product licenses: [`license_<component>-<version>`](../guide/admin/feature-flags.md#license_component-version)
- Creating a profile: [Profiles](../guide/admin/profiles.md#create-a-profile)
- Logs and the Prefect UI: [Troubleshooting](../guide/admin/troubleshooting.md)
- Updating zPodFactory: [Upgrading](../guide/admin/upgrade.md)

## Why does preparing NSX hosts break my zPod ?

The DLR feature in NSX will setup a very specific/hardcoded mac address `02:50:56:56:44:52` for the DLR interface. This mac address is also configured in *any new NSX host preparation step* by the nested environment, which makes any L3 forwarding impossible with the physical environment and creates a routing network blackhole between the physical environment and nested ESXi hosts.

It will seem as if your zPod went down (vcsa,nsx,esxi unresponsive from routed networks).

That said if you try to ping/connect/access the **`zcore`** VM of that zPod (legacy: `zbox`), it will have no networking issues as it isn't hosted by one of the nested zPod ESXi hosts.

You will need to change this hardcoded mac address to a different one, as it will conflict with any new nested environment when prepared by NSX.

You can also fix a broken zPod with the same steps from the core VM as L2 connectivity will work properly:

- [Change the MAC Address of NSX Virtual Distributed Router](https://techdocs.broadcom.com/us/en/vmware-cis/nsx/vmware-nsx/4-2/migration-guide/preparing-layer-2-bridging-for-lift-and-shift-migration/change-the-mac-address-of-nsx-t-virtual-distributed-router.html)

!!! info

    We recommend that you apply this new mac address to the physical environment layer, so that all new nested labs will be ready to go with no extra steps.

## Why does creating a vSAN datastore fails in my zPod ?

If you are trying to setup/run nested vSAN over a physical vSAN, you might encounter some issues with the vSAN datastore creation.

You will need to enable the `FakeSCSIReservations` setting on each host part of your physical vSphere vSAN cluster.

Leverage `esxcli` on *every* vSAN physical host:

``` { .sh data-copy="esxcli system settings advanced set -o /VSAN/FakeSCSIReservations -i 1" }
❯ esxcli system settings advanced set -o /VSAN/FakeSCSIReservations -i 1
```

[William Lam](https://twitter.com/lamw) explains the issue and the workaround in one of his blog articles:

- [How to run Nested ESXi on top of a VSAN datastore?](https://williamlam.com/2013/11/how-to-run-nested-esxi-on-top-of-vsan.html)
- [PowerCLI Script](https://developer.vmware.com/samples/5388/set-fakescsi-reservations-on-vsan-to-allow-nested-esxi-vms-to-run-vsan) to set the FakeSCSIReservations on all hosts in a vSAN cluster

## How to configure the Appliance WireGuard for external access ?

The zPodFactory Appliance will have a docker container ready to be used as a WireGuard VPN server. This will allow you to connect to your zPodFactory Appliance and networks from anywhere in the world.

We are leveraging this simple and efficient WireGuard container:

- [https://github.com/wg-easy/wg-easy](https://github.com/wg-easy/wg-easy)

This might change in the future, but for now it has been quite good for us with pretty large teams (80+ VPN accounts accessing the nested labs)

## How to get help ?

Open a [GitHub issue](https://github.com/zPodFactory/zpodcore/issues) with as much detail as you can.
