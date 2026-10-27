---
hide:
  - navigation
  - toc
---

# zPodFactory

![zPodFactory](img/zPodFactory-logo-tr.png){ width="160" align=right }

**Build your own nested VMware labs, on demand.** zPodFactory deploys complete nested environments (zPods) from reusable profiles, onto the vCenter and NSX you already have, and gives each one its own network, DNS and storage. Use it from the Web UI, from `zcli`, or through its API.

!!! tip "Latest releases"
    **zpodcore 0.9.0** and **zpodweb 0.2.0** (2026-10-26) add self-service [networks](guide/user/networks.md) (VLANs, masquerade, NSX fabric routing) and [storage and NFS](guide/user/storage.md) (disks, storages, folders, exports) to every zPod. See [What's new](releases.md).

<div class="grid cards" markdown>

-   :material-rocket-launch-outline:{ .lg .middle } **Getting started**

    ---

    Learn the concepts, install the appliance, and set up `zcli`.

    [:octicons-arrow-right-24:Concepts & architecture](guide/concepts.md)

-   :material-account-outline:{ .lg .middle } **User Guide**

    ---

    Create zPods, add components, and manage their networks, storage and DNS, from the Web UI or `zcli`.

    [:octicons-arrow-right-24:User Guide](guide/user/index.md)

-   :material-shield-account-outline:{ .lg .middle } **Administration**

    ---

    Settings, users and permissions, components, endpoints, profiles and upgrades.

    [:octicons-arrow-right-24:Administration](guide/admin/index.md)

-   :material-puzzle-outline:{ .lg .middle } **Extensibility**

    ---

    Config scripts, Terraform and Ansible on top of zPods, and the VCF deployer.

    [:octicons-arrow-right-24:Extensibility](guide/extensibility/bring-your-own.md)

</div>

## Why zPodFactory

zPodFactory is a rebuild from scratch of an earlier project that was tied to one environment. It is designed around a few principles:

1. **Simplicity**: deploy a nested environment in minutes from a premade or custom profile, without preparing or operating the underlying infrastructure by hand.
2. **Flexibility**: zPodFactory handles the initial deployment only. What you do inside a zPod, and its lifecycle, is up to you.
3. **Extensibility**: everything goes through the zPod API, so new clients and integrations are easy to build.
4. **Maintainability**: day-to-day administration of the factory is kept as simple as possible.

See [Concepts & architecture](guide/concepts.md) for how it is built.
