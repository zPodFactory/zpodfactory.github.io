# zcore migration (`zbox` → `zcore`)

The mandatory core component of every zPod has been renamed from **`zbox`** to **`zcore`**. New zPods deploy `zcore`; existing zPods that still use `zbox` as their core continue to work without migration.

## What changed

| Role | Before (`zbox`) | After (`zcore`) |
| --- | --- | --- |
| Subnet IP offset | `.2` | `.2` (unchanged) |
| Hostname / DNS | `zbox.{zpod.domain}` | `zcore.{zpod.domain}` |
| DNS API | `https://zcore.{domain}/zboxapi` | Same mount path (`/zboxapi`) |
| NFS filer | `zbox.{domain}` | `zcore.{domain}` |

The core appliance image is built from [`packer-zcore`](https://github.com/zPodFactory/packer-zcore). The library component is **`zcore-13.5`** (or newer).

!!! info "Legacy zPods"
    zPods deployed before the transition keep their `zbox` core component. DNS, NFS, and API calls resolve against whichever core is actually deployed — no data migration is required.

!!! info "Future `zbox` component"
    The `zbox` name will eventually return as an **ordinary**, multi-deployable Linux VM (foundation for Docker/Kubernetes), separate from the mandatory core. Do not confuse it with the legacy core role.

## Prerequisites

Before migrating profiles or deploying new zPods with `zcore`:

1. **Appliance** — `zcore` OVA published (from `packer-zcore`).
2. **Library** — `zcore-*` component in the [zPodLibrary](https://github.com/zPodFactory/zPodLibrary).
3. **zpodcore** — running a version that understands `zcore` (current main branch).
4. **`jq`** — required by the migration script.

## Migration steps

Run **after** upgrading zpodcore and confirming the API is healthy:

```bash
just zcore-transition
```

This script:

1. Resyncs the default library (fetches `zcore-*`).
2. Enables `zcore-13.5` (downloads if configured).
3. Rewrites every profile whose **first component** is `zbox-*` to `zcore-13.5` (hostname `zcore`).

The script is idempotent — safe to run multiple times.

### Manual verification

1. `zcli profile list` — profiles should start with `zcore-*`.
2. Deploy a new zPod from a migrated profile.
3. Confirm `zcore.{zpod.domain}` resolves, DNS/NFS are healthy, and nested ESXi mounts `NFS-01` from `zcore.{domain}`.

## Profile requirements

New and updated profiles **must** start with a `zcore-*` component as their first element. Profiles still referencing `zbox-*` as the core will be rejected at create/update/deploy time with a clear error — run `just zcore-transition` first.

Example profile snippet:

```json
[
  {
    "component_uid": "zcore-13.5"
  },
  [
    {
      "component_uid": "esxi-8.0u3i",
      "host_id": 11,
      "hostname": "esxi11",
      "vcpu": 6,
      "vmem": 48
    }
  ],
  {
    "component_uid": "vcsa-8.0u3i"
  }
]
```

## Operator upgrade order

1. Publish the `zcore` appliance OVA.
2. Add `zcore-*` to the zPodLibrary.
3. Upgrade zpodcore: `just zpodcore-stop && git pull && just zpodcore-start-background`
4. Run `just zcore-transition`.
5. Verify a new zPod deployment.
