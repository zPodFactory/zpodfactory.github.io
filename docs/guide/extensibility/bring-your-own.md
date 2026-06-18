# Bring your own …

zPodFactory is primarily an **API** for provisioning nested environments. It deploys the Layer 1 stack defined by a [profile](../admin/index.md#manage-profiles) — core appliance, nested hosts, and any baseline components in that profile — and then gets out of the way.

What happens **after** the zPod is `ACTIVE` is up to you. Many teams already treat zPodFactory as infrastructure glue: deploy a known zPod shape, then drive the rest of their lab design with whatever tooling they already use.

## The usual split

| Layer | Who owns it | Examples |
| --- | --- | --- |
| **Provision** | zPodFactory | Pick endpoint + profile, create zPod, wait for deploy |
| **Configure** | You | Terraform, Ansible, Python, bash, product-specific installers |

zPodFactory handles DNS plumbing, passwords, networking, and OVF/OVA deployment. Your automation handles the product-specific or test-specific configuration on top — NSX policy, vSphere clusters, HCX pairing, CI test fixtures, and so on.

## Pattern: profile lab + Terraform or Ansible

A very common workflow today:

1. **Choose a profile** that matches the lab skeleton you need (`base`, a VCF-oriented profile, a custom profile with the right ESXi count, etc.).
2. **Create the zPod** through the [API](../../api/index.md), the [SDK](../../api/index.md#sdk), or [`zcli`](../user/index.md#create-zpods).
3. **Wait until deploy completes** (poll the API, use `--wait` on the CLI, or rely on your orchestrator’s job status).
4. **Run your configuration** — Terraform modules against vCenter/NSX endpoints, Ansible playbooks over SSH/API, or a combination.

Because every component in the zPod shares the same generated password and reachable FQDNs, downstream tools can discover targets from `zcli zpod info <name> -j` or the equivalent API call and feed variables into your modules/playbooks.

This is intentionally **vanilla at L1**: zPodFactory does not need to know your Terraform layout or your Ansible role structure. You keep that logic in your own repo.

## Pattern: shell pipelines with `--wait`

For lighter automation — smoke tests, one-off demos, personal labs — many users chain a single `zcli` command with scripts:

```bash
#!/usr/bin/env bash
set -euo pipefail

ZPOD="team.alpha"

zcli zpod create "$ZPOD" -p base -e sddc-lab -w

# zPod is ACTIVE; run whatever you need next
./scripts/post-deploy-tests.sh "$ZPOD"
python3 ./scripts/tag-esxi-hosts.py "$ZPOD"
```

The `-w` / `--wait` flag blocks until the zPod reaches `ACTIVE` (or fails), so the next command in the pipeline only runs when Layer 1 is ready. No separate polling loop required for simple cases.

Combine with `-j` on info/list commands when you need structured output:

```bash
zcli zpod info "$ZPOD" -j | jq -r '.components[] | select(.component.component_name=="esxi") | .fqdn'
```

## Pattern: direct API / SDK integration

CI systems and internal portals often call the REST API or [zpodsdk](../../api/index.md#sdk) directly instead of shelling out to `zcli`. The flow is the same:

1. `POST /zpods` with `name`, `profile`, `endpoint_id`, optional `features`
2. Poll `GET /zpods/{id}` until `status` is `ACTIVE`
3. Trigger your downstream job (Jenkins, GitHub Actions, Prefect, etc.)

OpenAPI docs are served from your instance at `/docs` — see [API & SDK](../../api/index.md).

## How this relates to other extensibility options

Not everything belongs in external Terraform/Ansible. zPodFactory also supports **in-engine** hooks and **platform-specific** tools:

| Approach | When to use it |
| --- | --- |
| **Bring your own** (this page) | You already have config management or scripts; zPodFactory only provisions the zPod |
| [Config scripts](config-scripts.md) | Python hooks that run *inside* the zPod Engine at deploy/add/destroy time |
| [VCF deployer](vcf-deployer.md) | End-to-end VMware Cloud Foundation on a zPod — an example of “platform installer on top of zPodFactory” |

[VCF deployer](vcf-deployer.md) is a concrete instance of the “bring your own” idea: zPodFactory creates the zPod, then a separate tool runs the Broadcom VCF workflow. Your Terraform or Ansible playbooks follow the same boundary — zPodFactory for L1, your tooling for everything else.

## Related reading

- [User Guide — Create zPods](../user/index.md#create-zpods) — `--wait`, profiles, endpoints
- [User Guide — Accessing the zPod](../user/index.md#accessing-the-zpod) — `zcli zpod info` for URLs and credentials
- [Manage profiles](../admin/index.md#manage-profiles) — define reusable zPod skeletons
- [API & SDK](../../api/index.md) — OpenAPI, SDK, JSON output for scripting
