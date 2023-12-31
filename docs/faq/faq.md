# FAQ

Frequently asked questions.

## How is DNS configured and how does it work ?

DNS is a hierarchical system that resolves names to IP addresses. In zPodFactory the main domain is set using the `zpodfactory_instance_domain` variable

This domain is used to configure the DNS server running on the zPodFactory VM. The DNS server is configured to resolve all domain set by the `zpodfactory_instance_domain` to the IP address of the zPodFactory VM

Then for EACH zPod/Instance deployed, they get their own unique subdomain

The subdomain is composed of the instance name and the `zpodfactory_instance_domain`

For example, if the `zpodfactory_instance_domain` is set to `zpodfactory.local` and the instance/zPod name is `instance-a`, then the subdomain will be `instance-a.zpodfactory.local`.

!!! warning
    This means every zPod/Instance has a unique name, as it's used to generate the subdomain. If you try to deploy a zPod/Instance with the same name as an existing one, the deployment will fail

Quick representation on how it works:

- The `zpodfactory_instance_domain` is set to `zpod.lab` in this example, and is hosted by the zPodFactory VM.
    - the local dnsmasq service is configured to resolve `zpod.lab`
    - the subdomain `chicago.zpod.lab` is delegated to the zPod Chicago  `zbox`
    - the subdomain `paris.zpod.lab` is delegated to the zPod Paris `zbox`

- The zPod Chicago is deployed with the name `chicago`
    - The local dnsmasq service on the chicago `zbox` is configured to resolve all names ending with `chicago.zpod.lab`

- The zPod Paris is deployed with the name `paris`
    - The local dnsmasq service on the paris  `zbox` is configured to resolve all names ending with `paris.zpod.lab`

``` mermaid

graph TD

    subgraph zpodfactory["zPodFactory VM"]
        setting["setting 'zpodfactory_instance_domain' = 'zpod.lab'"]
        global_domain("zpod.lab")

        setting -- "managed by dnsmasq\n\ndomain=zpod.lab\nlocal=/zpod.lab/" --> global_domain

    end

    subgraph zpod_chicago["zPod Chicago"]
        zpod_chicago_domain("chicago.zpod.lab");


        zpod_chicago_zbox("zbox = 'zbox.chicago.zpod.lab'\n\n10.196.162.2");
        zpod_chicago_vcenter("vcsa = 'vcsa.chicago.zpod.lab'\n\n10.196.162.10");

        zpod_chicago_domain --> zpod_chicago_zbox
        zpod_chicago_zbox -- manages with dnsmasq --> zpod_chicago_domain
        zpod_chicago_domain --> zpod_chicago_vcenter
    end

    subgraph zpod_paris["zPod Paris"]
        zpod_paris_domain("paris.zpod.lab");


        zpod_paris_zbox("zbox = 'zbox.paris.zpod.lab'\n\n10.196.131.2");
        zpod_paris_vcenter("vcsa = 'vcsa.paris.zpod.lab'\n\n10.196.131.10");
        zpod_paris_domain --> zpod_paris_zbox
        zpod_paris_zbox -- manages with dnsmasq --> zpod_paris_domain
        zpod_paris_domain --> zpod_paris_vcenter
    end


    global_domain -- "delegate subdomain\nserver=/chicago.zpod.lab/10.196.162.2" --> zpod_chicago_domain
    global_domain -- "delegates subdomain\nserver=/paris.zpod.lab/10.196.131.2" --> zpod_paris_domain
```

This also means any zPod Admin owns his subdomain and can add some DNS entries to their local zPod DNS server.

For example let's say I'm the admin of the Paris zPod and I want to add the `demo.paris.zpod.lab` A record to point to following IP `192.168.131.100`

Login to the `zbox.paris.zpod.lab` VM using the Paris zPod Password and run edit the following file `/etc/hosts` to add your demo entry (by default the dnsmasq configuration reads this file and advertises it's content as DNS records):

Check the current `reserved` static entries:

``` { data-copy="cat /etc/hosts" }
❯ cat /etc/hosts
127.0.0.1        localhost
10.196.131.2     zbox.paris.zpod.lab    zbox

10.196.131.4     usagemeter
10.196.131.5     nsxt nsx
10.196.131.6     nsxv
10.196.131.7     avi

10.196.131.10    vcsa

10.196.131.11    esxi11
10.196.131.12    esxi12
10.196.131.13    esxi13
10.196.131.14    esxi14
10.196.131.15    esxi15
10.196.131.16    esxi16
10.196.131.17    esxi17
10.196.131.18    esxi18

10.196.131.20    hcx
10.196.131.21    hcx-cgw
10.196.131.22    hcx-l2c

10.196.131.25    cloudbuilder
10.196.131.26    sddcmgr

10.196.131.28    srm
10.196.131.29    vr

10.196.131.30    vrops
10.196.131.31    vrli log
10.196.131.36    vrni
10.196.131.37    vrni-proxy

10.196.131.40    vcd cloud
10.196.131.41    vcda

10.196.131.59    rabbitmq cse voss

10.196.131.62    vyos
```

!!! warning
    **DO NOT REMOVE** the pre-configured entries, they are used for all `components` deployments. (unless you know exactly what you are doing)

    Adding new entries is fine, but removing existing ones is not.

Add the new entry:

```
192.168.131.100    demo
```

Save and exit, and reload the dnsmasq service.

``` { data-copy="systemctl reload dnsmasq" }
❯ systemctl reload dnsmasq
```

## How does the embedded download engine work ?

The download engine has been designed to be as simple as possible for the end user. That said it does have some very specific requirements to work properly.

It relies on a [VMware Customer Connect](https://customerconnect.vmware.com/home) account that needs to be entitled to the products you want to leverage for your nested labs. (If you are not entitled to a product you try to enable/download it will fail)

The download engine is only aware about the products available in the `library`. The library is hosted here:

- [https://github.com/zPodFactory/zPodLibrary](https://github.com/zPodFactory/zPodLibrary)

The default library is a simple collection of JSON files that contains the metadata of all products/versions available for download.

The download engine is then wrapping the [VMware Customer Connect CLI](https://github.com/vmware-labs/vmware-customer-connect-cli) with the `library` metadata for a given `component` to launch the correct download and verify its integrity, then extract it to the correct location on the zPodFactory VM.

!!! info
    Please refer to the following related sections for setting up the download engine correctly and use it:

    Check [Manage settings](../guide/admin/index.md#manage-settings) to setup the customer connect credentials

    Check [Manage library](../guide/admin/index.md#manage-library) for managing the library

    Check [Manage components](../guide/admin/index.md#manage-components) for managing the components

## How to configure product licenses ?

Right now only VMware vCenter licenses are added to a deployed instance, we hope to add more products in the future. (NSX will be next one to be supported)

!!! info
    Please refer to the following related sections for setting up the download engine correctly and use it:

    Check [Manage settings](../guide/admin/index.md#manage-settings) and check the `license_<component>-<version>` variables in the provided screenshot.

## How to access the Prefect Flow engine UI ?

For a visual view of everything executed/launched by the zPodFactory flow engine, you can access the Prefect Flow engine UI here:

- https://manager.zpodfactory.domain:8060 (TBD)

## How to troubleshoot something ?

There are 2 mains ways to troubleshoot something in zPodFactory:

- Docker Compose logs
- The Prefect Flow engine UI

### Docker Compose logs

Change to zPodFactory Project directory:

``` { data-copy="cd ~/git/zpodcore" }
❯ cd ~/git/zpodcore
```

Check the logs:

``` { data-copy="docker-compose logs -f" }
❯ docker-compose logs -f
```

### The Prefect Flow engine UI

- https://manager.zpodfactory.domain:8060 (TBD)


## How to update the project ?

TBD (will likely be git based with a provided update script)

## How to add a new profile ?

Profiles can be created by an admin user, using the zPod API directly or the zPod CLI (`zcli`)

Prepare a `profile.json` file with the content of the `profile`, here is an example.

!!! info

    `zbox` component and `esxi` component are mandatory, all other components are optional.

    Usually you want at least a `zbox`, a few `esxi` hosts and a `vcsa` as the base profile provides

``` json
[
    {
      "component_uid": "zbox-12.1"
    },
    [
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 11,
        "hostname": "esxi11",
        "vcpu": 8,
        "vmem": 64
      },
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 12,
        "hostname": "esxi12",
        "vcpu": 8,
        "vmem": 64
      },
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 13,
        "hostname": "esxi13",
        "vcpu": 8,
        "vmem": 64
      },
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 14,
        "hostname": "esxi14",
        "vcpu": 8,
        "vmem": 64
      }
    ],
    {
        "component_uid": "vcsa-8.0u2"
    },
    {
        "component_uid": "vcd-10.5"
    },
    {
        "component_uid": "nsx-4.1.1.0"
    }
]
```

Next use zcli to create the profile:

``` { data-copy="zcli profile create -n sddc-vcd -pf profile.json" }
❯ zcli profile create -n sddc-vcd -pf profile.json
Profile sddc-vcd has been created.
```

Check the profiles list:

``` { data-copy="zcli profile list" }
❯ zcli profile list
                       List Profile
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Profile    ┃ Components                                  ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ zbox       │ zbox-12.1                                   │
│ hosts      │ zbox-12.1                                   │
│            │ esxi-8.0u2 (Host Id: 11, CPU: 4, Mem: 12GB) │
│            │ esxi-8.0u2 (Host Id: 12, CPU: 4, Mem: 12GB) │
│ base       │ zbox-12.1                                   │
│            │ esxi-8.0u2 (Host Id: 11, CPU: 4, Mem: 48GB) │
│            │ esxi-8.0u2 (Host Id: 12, CPU: 4, Mem: 48GB) │
│            │ vcsa-8.0u2                                  │
│ sddc       │ zbox-12.1                                   │
│            │ esxi-8.0u2 (Host Id: 11, CPU: 6, Mem: 48GB) │
│            │ esxi-8.0u2 (Host Id: 12, CPU: 6, Mem: 48GB) │
│            │ esxi-8.0u2 (Host Id: 13, CPU: 6, Mem: 48GB) │
│            │ vcsa-8.0u2                                  │
│            │ nsx-4.1.1.0                                 │
│ sddc-large │ zbox-12.1                                   │
│            │ esxi-8.0u2 (Host Id: 11, CPU: 8, Mem: 64GB) │
│            │ esxi-8.0u2 (Host Id: 12, CPU: 8, Mem: 64GB) │
│            │ esxi-8.0u2 (Host Id: 13, CPU: 8, Mem: 64GB) │
│            │ esxi-8.0u2 (Host Id: 14, CPU: 8, Mem: 64GB) │
│            │ vcsa-8.0u2                                  │
│            │ nsx-4.1.1.0                                 │
│ sddc-vcd   │ zbox-12.1                                   │
│            │ esxi-8.0u2 (Host Id: 11, CPU: 8, Mem: 64GB) │
│            │ esxi-8.0u2 (Host Id: 12, CPU: 8, Mem: 64GB) │
│            │ esxi-8.0u2 (Host Id: 13, CPU: 8, Mem: 64GB) │
│            │ esxi-8.0u2 (Host Id: 14, CPU: 8, Mem: 64GB) │
│            │ vcsa-8.0u2                                  │
│            │ vcd-10.5                                    │
│            │ nsx-4.1.1.0                                 │
└────────────┴─────────────────────────────────────────────┘
```


## How to add a new product ?

TBD

## Why is x product not available through the download engine ?

There can be multiple reasons for that:

- We just haven't added it yet (time)
    - This could also be because we are missing automation bits around it
    - This could also be because our download engine tooling can't fetch the product from VMware Customer Connect (there are some caveats on some specific Product sections)
- The product is not available on VMware Customer Connect (For example, Pivotal products).

!!! info

    Let us know which products you would like to be supported by zPodFactory and the download engine, and if you can provide any automation bits around it, that would be awesome.

## How to configure the Appliance Wireguard for external access ?

The zPodFactory Appliance will have a docker container ready to be used as a Wireguard VPN server. This will allow you to connect to your zPodFactory Appliance and networks from anywhere in the world.

We are leveraging this simple and efficient WireGuard container:

- [https://hub.docker.com/r/weejewel/wg-easy](https://hub.docker.com/r/weejewel/wg-easy)

This might change in the future, but for now it has been quite good for us and a pretty large teams (80+ VPN accounts accessing to nested labs)

## How to get help ?

- For now probably just create GitHub Issues, and add as much information as you can.
- We will likely add a Slack channel for discussions in the future.
