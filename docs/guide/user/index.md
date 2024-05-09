# User Guide

Once the zPodFactory framework is deployed and running, and has been configured by an Administrator you can start using the CLI to deploy nested environments.

## Introduction

`zcli` is a command line tool that allows you to manage your zPods and the whole zPodFactory framework.

## CLI Installation

Using `pip`:

``` { data-copy="pip install zpodcli" }
❯ pip install zpodcli
```

Verify that the CLI is now available and working:

``` { data-copy="zcli"}
❯ zcli

 Usage: zcli [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --factory             -f      TEXT  Use specified factory for current commmand.                                       │
│ --output-svg                        Output an SVG file for any list command.                                          │
│ --version             -V            Display version information.                                                      │
│ --install-completion                Install completion for the current shell.                                         │
│ --show-completion                   Show completion for the current shell, to copy it or customize the installation.  │
│ --help                              Show this message and exit.                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ component                          Manage Components                                                                  │
│ endpoint                           Manage Endpoints                                                                   │
│ enet                               Manage ENets                                                                       │
│ factory                            Manage Factories                                                                   │
│ group                              Manage Permission Groups                                                           │
│ library                            Manage Libraries                                                                   │
│ profile                            Manage Profiles                                                                    │
│ setting                            Manage Settings                                                                    │
│ user                               Manage Users                                                                       │
│ zpod                               Manage zPods                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Authentication

The first thing you need to do is to connect to the zPodFactory API with the token an Administrator provided you.

``` {data-copy="zcli factory add myfactory -s http://zpodfactory.domain.lab:8000 -t TOKEN -a}
❯ zcli factory add myfactory -s http://zpodfactory.domain.lab:8000 -t "TOKEN" -a
```

Verify that the connection was successfull and that you are connected to the API:

``` {data-copy="zcli user list"}
❯ zcli user list
```

![img](../../img/zcli_user_list.svg)

## Manage zPods

zPods are the nested environments name in the zPodFactory framework.

### List zPods

``` {data-copy="zcli zpod list"}
❯ zcli zpod list
```

![img](../../img/zcli_zpod_list.svg)

### Create zPods

To create a zPod you will need to provide a few parameters:

- `name`: The name of the zPod
- `profile`: The profile to use to deploy the zPod (use `zcli profile list` to list available profiles)
- `endpoint`: The endpoint to use to deploy the zPod (use `zcli endpoint list` to list available endpoints)

``` {data-copy="zcli zpod create name -p profile -e endpoint"}
❯ zcli zpod create name -p profile -e endpoint
```

For example:

``` {data-copy="zcli zpod create test -p base -e sddc-lab"}
❯ zcli zpod create test -p base -e sddc-lab
```

This will create a zPod with the following attributes:

- `name`: `test` This will be the name of the zPod, that also means it will concatenate this name with the `zpodfactory.domain` to create the FQDN of the zPod. In this case it will be `test.zpodfactory.domain`, and any component, such as `zbox` component will be `zbox.test.zpodfactory.domain`.

!!! info
    The `zpodfactory.domain` is a setting that can ONLY be configured by an Administrator.

    It is configured by the `zpodfactory_default_domain` setting. This setting should be configured at initial setup of this framework and **SHOULD NEVER BE MODIFIED**.

    Check [Manage settings](../admin/index.md#manage-settings) for more information.

- `profile`: `base` This is the profile that will be used to deploy the zPod. It will be used to deploy the `zbox` component, and any other component that is required by the profile. The `base` profile actually entitles to the following components in our current configuration :

    - `zbox-12.4` (mandatory `component` to manage DNS/DHCP, 3 additional zPod /26 subnets on tagged VLAN 64/128/192, and also the NFS datastore for the nested hosts)
    - `esxi-8.0u2` (Host Id: 11, CPU: 4, Mem: 48GB)
    - `esxi-8.0u2` (Host Id: 12, CPU: 4, Mem: 48GB)
    - `vcsa-8.0u2`

!!! info
    The `base` profile is a profile that can ONLY be configured by an Administrator.
    Check [Manage profiles](../admin/index.md#manage-profiles) for more information.

- `endpoint`: `sddc-lab` will reference the endpoint to use to deploy the zPod. In this case it will be the `sddc-lab` endpoint that is configured by an Administrator, and should link to the physical environment that will host this zPod nested environment.

!!! info
    The `sddc-lab` endpoint is an endpoint that can ONLY be configured by an Administrator.
    Check [Manage endpoints](../admin/index.md#manage-endpoints) for more information.


### Accessing the zPod

Once the zPod is deployed, you can access it using the following credentials

for vcsa (VMware vCenter Server):

- `username`: `administrator@name.zpodfactory.domain`
- `password`: Each zPod has its password generated.  Password can be fetched by using the `zcli zpod list` command)

For every other component, the username is the default for that component.  For example, on many VMware products the default administrator account is either `root` or `admin`, such as `nsx-v`, `nsx-t`, `nsx`, `vcda`, `vrops`, `vrli`.  However, for `vcd`, the default administrator account is `administrator`.  The password is **always** the zPod Password.


### Destroy zPods

``` {data-copy="zcli zpod destroy delete name"}
❯ zcli zpod destroy name
```

!!! warning
    This will destroy the zPod and all its components without confirmation, and will not be recoverable.


## Manage components

In the previous section we deployed a zPod with the `base` profile, which does not contain many products, but only the bare minimum to have a functional nested environment.
Here we will show you how to list the available components, and add a new component to a deployed/available zPod.

### List components

``` {data-copy="zcli component list"}
❯ zcli component list
```

![img](../../img/zcli_component_list.svg)


### List components of a zPod

You will need to provide the zpod name parameter so that the CLI knows which zPod to list the components from.

``` {data-copy="zcli zpod component list zpod_name"}
❯ zcli zpod component list zpod_name
```

![img](../../img/zcli_zpod_component_list.svg)

### Add components to a zPod

If you want to add a new component to a zpod, you will need to provide the `component_uid`.  Component UID is a combination of a product name and a version, as many products/versions exist for a given component. (use `zcli component list` to list available components)

``` {data-copy="zcli zpod component add zpod_name -c component_uid"}
❯ zcli zpod component add zpod_name -c component_uid
```

For example in our case:

``` {data-copy="zcli zpod component add team.beta -c vcd-10.5}
❯ zcli zpod component add team.beta -c vcd-10.5
```

This will add the `vcd-10.5` component to the `team.beta` zPod.
