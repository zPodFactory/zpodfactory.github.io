# Config scripts

Config scripts extend zPodFactory at hook points during the zPod and component lifecycle. They run as Python modules inside the zPod Engine and can automate post-deploy configuration (VDS setup, NSX preparation, custom integrations, etc.).

## Hook points

| Flow | Module path | When it runs |
| --- | --- | --- |
| zPod deploy | `zpodengine/config_scripts/<name>/zpod_deploy.py` | After zPod infrastructure is deployed |
| zPod destroy | `zpodengine/config_scripts/<name>/zpod_destroy.py` | Before zPod teardown |
| Component add | `zpodengine/config_scripts/<name>/zpod_component_add_<component>.py` | After a component is added to a zPod |

Each module must expose `execute_config_script(...)` with the signature expected by the engine (see the [sample scripts](https://github.com/zPodFactory/zpodcore/tree/main/zpodengine/src/zpodengine/config_scripts/sample) in zpodcore).

## Enabling config scripts on a zPod

Config scripts are selected via the zPod **`features`** map, key `config-scripts`, as a list of script names:

```json
{
  "config-scripts": ["vdsnsx"]
}
```

When creating a zPod through the API, pass this in the request body. The CLI does not yet expose a `--config-scripts` flag — use the API or set a global default (below).

### Global default

Apply config scripts to every new zPod automatically:

```bash
zcli setting create -n ff_default_config_scripts -v "vdsnsx" \
  -d "Default config scripts for new zPods"
```

Multiple scripts are comma-separated with no spaces: `script-a,script-b`.

See [Feature flags](../admin/feature-flags.md) for the full flag reference.

## Installing a config script

Place scripts under `zpodengine/src/zpodengine/config_scripts/<name>/` on the zPodFactory host (inside the engine container's source tree in development, or baked into your deployment).

Example — the community **vdsnsx** script (VDS + NSX-T automation):

```bash
cd ~/git/zpodcore
git clone https://github.com/carsso/zPodFactory-vdsnsx.git \
  zpodengine/src/zpodengine/config_scripts/vdsnsx
```

Then set `ff_default_config_scripts` to `vdsnsx` or pass `config-scripts` when creating a zPod via the API.

## Sample script

zpodcore ships a no-op sample at `config_scripts/sample/` showing the expected module layout for `zpod_deploy.py`, `zpod_destroy.py`, and `zpod_component_add_zbox.py`. Use it as a template for custom scripts.

## Related settings

| Setting | Purpose |
| --- | --- |
| `ff_default_config_scripts` | Auto-apply scripts to new zPods |
| `ff_component_wait_for_status` | Wait for component health before running component-add scripts |

## Platform automation on top of zPodFactory

For the general pattern — provision a zPod, then configure it with your own Terraform, Ansible, or scripts — see [Bring your own …](bring-your-own.md).

For products that ship their own installer stack (notably **VMware Cloud Foundation**), see [VCF deployer](vcf-deployer.md) — an external tool that provisions a zPod via zPodFactory, then runs the official Broadcom VCF SDDC workflow on top.
