# What's new

These are the highlights of recent zpodcore and zpodweb releases, for people who run or use a factory. The full notes are the GitHub releases and the changelogs of [zpodcore](https://github.com/zPodFactory/zpodcore/blob/main/CHANGELOG.md) and [zpodweb](https://github.com/zPodFactory/zpodweb/blob/main/CHANGELOG.md).

zpodcore ships four packages under one version: the zPod API, the zPod Engine, `zcli` and `zpodsdk`. A `zcli X.Y.*` only works with an API `X.Y.*`, so upgrade the CLI with the factory (`uv tool install zpodcli==<version>`).

## zpodcore 0.9.0 — 2026-10-26

[Release notes](https://github.com/zPodFactory/zpodcore/releases/tag/v0.9.0)

!!! warning "Breaking"
    - **`GET /zpods/{id}/networks` needs read access to the zPod.** It had no permission check before. A caller with no permission on the zPod now gets `404`.
    - **zPod deploys and L1 component adds stop when the endpoint's datastore is low.** They check [`zpodfactory_datastore_min_free_pct`](guide/admin/feature-flags.md#zpodfactory_datastore_min_free_pct) (default `15`) first. Lower the setting to get the 0.8 behavior back.

**zPod networks**: [guide](guide/user/networks.md)

- Add VLAN networks with their own subnet to a zPod's zcore, with optional masquerade (egress). You can also enable, disable and remove them.
- Superadmins can advertise a network to the NSX fabric through a T1 static route. An audited flow checks the whole fabric for overlaps first, supports a dry run, and keeps an artifact of the evidence.
- The list shows all three kinds of network: the deploy-time ones (`zpod`), zcore's own VLANs 10/20/30 (`zcore`) and your own (`user`), with live status.
- New CLI group: `zcli zpod network list|add|remove|masquerade|enable|disable|routing`.

**zPod storage and NFS**: [guide](guide/user/storage.md)

- Add, grow and remove thin virtual disks on the zcore VM. Each change runs as a zPod Engine flow.
- Create storages on those disks (raw or LVM), grow them online, delete or adopt them again, and manage their folders.
- Export folders over NFS to the clients you choose, and see who has each export mounted.
- New CLI groups: `zcli zpod disk`, `zcli zpod storage` (including `folder`) and `zcli zpod nfs` (including `client`).
- `zcli zpod info` has a new Storage panel (`-f s`).
- New seeded settings: [`zpodfactory_zpod_disk_max_gb`](guide/admin/feature-flags.md#zpodfactory_zpod_disk_max_gb) (`2048`) and [`zpodfactory_datastore_min_free_pct`](guide/admin/feature-flags.md#zpodfactory_datastore_min_free_pct) (`15`).

**Stack and operations**

- The appliance bootstrap enables **`zcore-13.7`** (zboxapi 0.2.1), which the storage features and network masquerade/enable/disable need.
- `just zcore-transition` rebuilds the stack before it touches profiles. `SKIP_REBUILD=1` skips the rebuild. See [zcore migration](guide/admin/zcore-migration.md).
- Prefect 3.8.3 → 3.8.8. The flow image puts the Python environment in its last layer, so a dependency bump no longer re-downloads the PowerShell modules.

## zpodweb 0.2.0 — 2026-10-26

[Release notes](https://github.com/zPodFactory/zpodweb/releases/tag/v0.2.0) · [Web UI guide](guide/user/web-ui.md)

- **Users** and **Groups** pages, and an **Access** section on each endpoint card for granting users and groups.
- A **Networks** card on the zPod detail page:
    - add, enable/disable, masquerade and remove networks;
    - advertise a network to the NSX fabric, with a dry run, and follow the run to its verdict;
    - a **Topology** tab that animates a network's paths to the internet, from the fabric and to management, and explains why each one works or is blocked.
- A **Storage** card:
    - a storage and folder tree with usage bars and mount indicators;
    - NFS exports with ready-to-copy ESXi and Linux mount commands;
    - a **Layout** tab per disk;
    - every maintainer action, with protected items shown disabled and the reason.
- The Network Topology card shows every zcore interface by kind, with a live status. The zPods list's Networks column shows only the zPod's own subnets.

## zpodcore 0.8.0 — 2026-10-08

[Release notes](https://github.com/zPodFactory/zpodcore/releases/tag/v0.8.0)

!!! warning "Breaking"
    - **`zcore` replaces `zbox` as the mandatory core component.** A profile must start with `zcore-*`. Run `just zcore-transition` once after upgrading. See [zcore migration](guide/admin/zcore-migration.md).
    - **zPod features are a JSON object on the zPod.** `GET /zpods/{id}/features` and the `zpod_features` table are gone.
    - **zPod names and FQDNs are validated up front.** Names must be ASCII and start with a letter, and the longest component FQDN must fit in `64 - zpodfactory_fqdn_reserved_chars` characters.
    - **Settings are readable by every authenticated user.** Only the Broadcom token is masked.
    - **`https` is the only download engine.** `customerconnect` and `avipulse` are removed. See [Broadcom download token](guide/admin/broadcom-download-token.md).
    - **zpodcli and zpodsdk require Python 3.14.**
    - **Prefect 2 → 3.** Wipe the Prefect volume and re-register the flows (`just zpodengine-deploy-all`).
    - **`zcli` uses `--watch/-w`** for auto-refresh on `zpod list` and `zpod component list` (it was `--wait`).

Highlights:

- [Feature flags](guide/admin/feature-flags.md) for passwords, username prefixes, per-user zPod quotas, default profile and config scripts, subnet pinning, ESXi FQDN hostnames and NSX status waits. Missing settings are seeded on every start.
- [Config scripts](guide/extensibility/config-scripts.md) run on zPod deploy, destroy and component add.
- [Endpoint OVA staging](guide/admin/endpoint-ova-staging.md) (`ff_endpoint_ova_staging`), NSX orphan port cleanup on destroy (`ff_nsx_clean_orphan_ports`), and an optional VDS name on endpoints.
- New components: Proxmox VE, Proxmox Datacenter Manager, Proxmox Backup Server, `vcfinstaller` (VCF 9), `hcx-cloud` and `hcx-connector`.
- Per-component `vcpu`, `vmem`, `vnics` and `vdisks`. Broadcom depot downloads through `zpodfactory_broadcom_download_token`. The log level (`zpodfactory_debug_level`) changes live.
- `zcli zpod info`, `zpod create --wait`, `--json` and `--no-color` everywhere, `user delete`, `setting create|delete`.

## zpodweb 0.1.0 — 2026-10-04

[Release notes](https://github.com/zPodFactory/zpodweb/releases/tag/v0.1.0)

This was the first tagged release of the web UI:

- dashboard, zPods and zPod detail pages;
- components, libraries, profiles (import and export), endpoints (CRUD with VDS), and factory settings;
- several saved API targets;
- zPod permissions;
- chunked, resumable component uploads;
- the Catppuccin Mocha theme.
