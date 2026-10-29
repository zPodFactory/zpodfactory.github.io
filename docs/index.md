---
hide:
  - navigation
  - toc
---

# zPodFactory

![zPodFactory](img/zPodFactory-logo-tr.png){ width="160" align=right }

**Build your own nested VMware labs, on demand.** zPodFactory deploys complete nested environments (zPods) from reusable profiles, onto the vCenter and NSX you already have, and gives each one its own network, DNS and storage. Use it from the Web UI, from `zcli`, or through its API.

!!! tip "Latest releases"
    **zpodcore 0.9.2** and **zpodweb 0.3.0** (2026-10-29) let each component choose [where it is deployed and on which network](guide/user/components.md#placement-and-network), and bring stock cloud images (Ubuntu, Photon OS, Red Hat CoreOS, Talos) up with their zPod address on first boot. They build on 0.9.0's self-service [networks](guide/user/networks.md) and [storage and NFS](guide/user/storage.md). See [What's new](releases.md).

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
