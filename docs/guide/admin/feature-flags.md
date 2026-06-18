# Feature flags

zPodFactory stores feature flags in the global `Setting` table. Each flag is a row named with the `ff_` prefix and a string `value`. Operators manage them with the CLI or API:

```bash
zcli setting create  -n <flag> -v <value> [-d "<description>"]
zcli setting update  <flag> --value <value>
zcli setting list
zcli setting delete  <flag>
```

Flags are read at the point of use — changes take effect on the next operation, with no restart required. If a flag is absent, the default behavior applies.

!!! info "Truthiness"
    Most boolean flags require the literal string `"true"` (lowercase). Anything else (`"True"`, `"1"`, `"yes"`) is treated as off. A few flags (noted below) treat any non-empty string as on.

## zPod creation

### `ff_unique_zpod_password`

Forces every new zPod to use this exact password instead of a randomly generated one.

- **Value:** any non-empty string (the literal password)
- **Example:** `zcli setting create -n ff_unique_zpod_password -v "VMware1!"`

!!! warning "VMware password requirements"

    When this flag is unset, zPodFactory generates random 16-character passwords designed to work across all VMware products deployed in a zPod (uppercase, lowercase, digit, and special character).

    Setting a personal or shared password here may break provisioning if a product rejects it — for example VCF now enforces a **15-character minimum**, or policies that disallow passwords that are too short, too simple, or missing required character classes.

### `ff_reuse_zpod_password`

When creating a zPod whose name matches a previously deleted one, reuse that zPod's password.

- **Value:** `"true"` to enable
- **Example:** `zcli setting create -n ff_reuse_zpod_password -v true`

### `ff_restrict_zpod_with_username_prefix`

Non-superadmin users must name their zPods `<username>-<anything>`. Superadmins are exempt.

- **Value:** `"true"` to enable
- **Example:** `zcli setting create -n ff_restrict_zpod_with_username_prefix -v true`

### `ff_default_config_scripts`

Comma-separated list of config-script names auto-applied to new zPods that do not supply their own `config-scripts` feature.

- **Value:** comma-separated string, no spaces (e.g. `vdsnsx,sample`)
- **Example:** `zcli setting create -n ff_default_config_scripts -v "vdsnsx"`
- See [Config scripts](../extensibility/config-scripts.md) for details.

### `ff_zpod_default_profile`

Default profile for `zcli zpod create` when `--profile/-p` is omitted. If unset, the CLI requires a profile.

- **Value:** profile name
- **Example:** `zcli setting create -n ff_zpod_default_profile -v base`

### `ff_max_zpods_per_user`

Cap on how many active zPods a non-superadmin user can own. `0`, missing, or non-numeric means unlimited. Superadmins are exempt. Counts only zPods where the user has `OWNER` permission and status is not `DELETED`.

- **Value:** positive integer
- **Example:** `zcli setting create -n ff_max_zpods_per_user -v 3`

### `ff_max_zpods_<username>`

Per-user override of `ff_max_zpods_per_user`. When set, it fully replaces the global value for that user — including `0`/invalid, which means unlimited for that user. Superadmins are still exempt.

- **Value:** positive integer; `0`/invalid ⇒ unlimited for this user
- **Example:** `zcli setting create -n ff_max_zpods_alice -v 10`

## zPod networking

### `ff_zpod_<zpod_name>_subnet`

Pin a specific zPod to a custom primary `/24` subnet instead of letting the engine allocate one. Must match the configured public-network prefix length (default `/24`).

- **Value:** CIDR string (e.g. `10.96.42.0/24`)
- **Example:** `zcli setting create -n ff_zpod_lab01_subnet -v 10.96.42.0/24`

## Component deployment

### `ff_esxi_hostname_is_fqdn`

For ESXi components, set the hostname to the full FQDN (`<short>.<domain>`) instead of the short name during OVF deploy.

Set this to **`true`** when using [William Lam](https://williamlam.com/) VMware ESXi templates — they expect the deployed hostname to be the FQDN.

- **Value:** any non-empty string is on (no `"true"` requirement)
- **Example:** `zcli setting create -n ff_esxi_hostname_is_fqdn -v true`

### `ff_component_wait_for_status`

During post-script execution, block until the component reports a healthy status before continuing.

- **Value:** `"true"` to enable
- **Example:** `zcli setting create -n ff_component_wait_for_status -v true`

### `ff_endpoint_ova_staging`

Stage L1 OVAs once as VM templates on the endpoint vCenter and clone them for each deployment instead of re-uploading the full OVA every time. Off by default.

- **Value:** `"true"` to enable
- **Example:** `zcli setting create -n ff_endpoint_ova_staging -v true -d "Stage L1 OVAs as templates and clone per deployment"`

See [Endpoint OVA staging](endpoint-ova-staging.md) for architecture and operating notes.
