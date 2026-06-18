# Endpoint OVA staging

**Feature flag:** `ff_endpoint_ova_staging` (off by default)

## Problem

Every L1 component deployment runs `govc import.ova` against the endpoint vCenter, streaming the full OVA from the zPodFactory host on **every** deployment. Deploying multiple zPods (or a profile with several nested-ESXi hosts) that share the same template re-uploads the same multi-GB OVA repeatedly — slow and network-intensive.

## Solution

When enabled, each OVA is uploaded to the endpoint vCenter **once**, converted into a **VM template** in a `components-staging` folder, and **cloned** for subsequent L1 deployments. Per-zPod OVF properties and portgroup assignment happen at clone time.

### Scope

- **L1 only** — components with `component_isnested: false` (e.g. `esxi`, `zcore`, `vcfinstaller`, `proxmox`). L2 nested components keep the direct import path. `vcsa` uses its own deployer and is excluded.
- **Templates are never powered on** — booting a template would consume one-shot OVF customization and break later clones.
- **Fallback** — if staging or cloning fails, the engine falls back to the direct `govc import.ova` path.

### Inventory layout

Under the endpoint's configured `vmfolder`:

```
/<datacenter>/vm/<vmfolder>/
└── components-staging/
    ├── esxi-8.0u3g        (VM Template)
    ├── zcore-13.5         (VM Template)
    └── vcfinstaller-...   (VM Template)
```

Template names match the component UID. Cloned VMs land in the zPod vApp with the usual FQDN name.

## Enable / disable

```bash
# Enable
zcli setting create --name ff_endpoint_ova_staging --value true \
  --description "Stage L1 OVAs as templates and clone per deployment"

# Disable (reverts immediately to direct import)
zcli setting update --name ff_endpoint_ova_staging --value false
# or
zcli setting delete --name ff_endpoint_ova_staging
```

Existing staged templates are harmless and are reused if the flag is re-enabled.

## Operating notes

### Inspect staged templates

```bash
govc ls '/<datacenter>/vm/<vmfolder>/components-staging'
govc object.collect -s '/.../components-staging/esxi-8.0u3g' customValue
```

A template is ready when it exists and its `zpodfactory_staging_status` custom attribute is `staged`.

### Manual template cleanup

When a component is disabled and you want its template removed:

```bash
govc vm.destroy '/<datacenter>/vm/<vmfolder>/components-staging/<component_uid>'
```

The next deployment for that UID will re-stage automatically.

### Stale lock rows

Staging uses atomic claim rows named `_ova_staging_lock_<endpoint_id>_<uid>` in the settings table. A leftover lock after a crash can be cleared manually:

```bash
zcli setting list | grep _ova_staging_lock_
zcli setting delete --name _ova_staging_lock_<endpoint_id>_<component_uid>
```
