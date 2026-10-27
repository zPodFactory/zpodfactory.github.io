# Administration

Administrators run the factory itself: its settings, who can use it, which products it can deploy, where zPods land, and what a zPod is made of. Most of it is available both in the [Web UI](../user/web-ui.md) and with [zcli](../zcli.md), connected as a `superadmin` user such as the `superuser` created at install.

## Setting up a factory

A new factory needs, in this order:

1. **[Settings](feature-flags.md)**: check `zpodfactory_host` and `zpodfactory_default_domain`, and add an SSH key.
2. **[Broadcom download token](broadcom-download-token.md)**, so VMware products download from the Broadcom depot.
3. **[Endpoints](endpoints.md)**: the vCenter and NSX pair zPods are deployed on.
4. **[Libraries & components](components.md)**: enable the products zPods use, starting with `zcore` and ESXi.
5. **[Profiles](profiles.md)**: the sets of components a zPod is created from.
6. **[Users, groups & permissions](users.md)**: give people access to zPods and endpoints.

## Reference

| Page | What it covers |
| --- | --- |
| [Settings & feature flags](feature-flags.md) | Every `zpodfactory_*` setting and `ff_*` flag, with its default |
| [Users, groups & permissions](users.md) | Users and API tokens, permission groups, zPod and endpoint access |
| [Libraries & components](components.md) | The component library, enabling and uploading products, the download engine |
| [Broadcom download token](broadcom-download-token.md) | Getting and configuring the depot token, and troubleshooting downloads |
| [Endpoints](endpoints.md) | vCenter and NSX targets, the network requirements, ENets |
| [Profiles](profiles.md) | Profile format, per-component overrides, creating a profile |
| [Endpoint OVA staging](endpoint-ova-staging.md) | Staging OVAs as templates on an endpoint to speed up deploys |
| [Upgrading](upgrade.md) | Moving the factory to a new release |
| [zcore migration](zcore-migration.md) | Moving profiles from `zbox` to `zcore` |
| [Troubleshooting](troubleshooting.md) | Logs and the flow engine UI |
