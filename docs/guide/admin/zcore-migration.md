# zcore migration (`zbox` → `zcore`)

The mandatory core component of every zPod has been renamed from **`zbox`** to **`zcore`**. New zPods deploy `zcore`; existing zPods that still use `zbox` as their core continue to work without migration.

## What changed

| Role | Before (`zbox`) | After (`zcore`) |
| --- | --- | --- |
| Subnet IP offset | `.2` | `.2` (unchanged) |
| Hostname / DNS | `zbox.{zpod.domain}` | `zcore.{zpod.domain}` |
| DNS API | `https://zcore.{domain}/zboxapi` | Same mount path (`/zboxapi`) |
| NFS filer | `zbox.{domain}` | `zcore.{domain}` |

The core appliance image is built from [`packer-zcore`](https://github.com/zPodFactory/packer-zcore). The library component is **`zcore-13.7`**. It ships zboxapi 0.2.1, which the zPod [network](../user/networks.md) masquerade/enable/disable and [storage](../user/storage.md) features need. `zcore-13.5` still deploys and works without those features.

!!! info "Legacy zPods"
    zPods deployed before the transition keep their `zbox` core component. DNS, NFS, and API calls resolve against whichever core is actually deployed — no data migration is required.

!!! info "`zbox` is back, as an ordinary component"
    The `zbox` name now belongs to an **ordinary** component: a Debian Linux appliance you can add to any zPod, as many times as you need, for example as a base for Docker or Kubernetes. **`zbox-13.5`** is available now, and **`zbox-13.7`** will follow soon.

    It has nothing to do with the legacy core role: it is never the first component of a profile, and it provides no DNS, DHCP, NFS or routing for the zPod. That is `zcore`'s job. In this guide, "legacy `zbox`" always means the old core component (`zbox-12.x` and earlier).

## Prerequisites

Before migrating profiles or deploying new zPods with `zcore`:

1. **Appliance** — `zcore` OVA published (from `packer-zcore`).
2. **Library** — `zcore-*` component in the [zPodLibrary](https://github.com/zPodFactory/zPodLibrary).
3. **zpodcore** — 0.8.0 or later (0.9.0 for `zcore-13.7` as the default).
4. **`jq`** — required by the migration script.

## Migration steps

Run **after** upgrading zpodcore and confirming the API is healthy:

```bash
just zcore-transition
```

This script:

1. Stops the stack, rebuilds the images with `--no-cache`, starts it again, and waits for zpodapi and the Prefect server to answer.
2. Re-registers every flow (`just zpodengine-deploy-all`).
3. Resyncs the default library, enables `zcore-13.7`, and waits for it to be `ACTIVE`.
4. Rewrites every profile whose **first component** is `zbox-*` to `zcore-13.7` (hostname `zcore`).

Steps 3 and 4 used to break when they ran against a stack that had not been rebuilt yet, so the rebuild now comes first. If the stack is already rebuilt, skip steps 1 and 2:

```bash
SKIP_REBUILD=1 just zcore-transition
```

The script is idempotent, so it is safe to run several times. `ZCORE_UID=zcore-13.5 just zcore-transition` pins another core version.

### Profiles already on `zcore-13.5`

The script only rewrites `zbox-*` profiles, so a profile that already starts with `zcore-13.5` stays on it. To give new zPods the storage and network features, move such a profile to `zcore-13.7` yourself:

```bash
zcli profile info <name> -j > profile.json
# change "zcore-13.5" to "zcore-13.7" in profile.json
zcli profile update <name> -pf profile.json
```

Existing zPods keep the zcore they were deployed with.

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
    "component_uid": "zcore-13.7"
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
