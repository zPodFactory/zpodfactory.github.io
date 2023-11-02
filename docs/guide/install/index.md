# Installation and Configuration

Before you can start using zPodFactory, you need to install it. This section will guide you through the installation and configuration process.

:octicons-alert-fill-24: Requirements are a very important part of the installation process, so please make sure to read them carefully.

## Requirements

As you can imagine, if your plan is to deploy various nested environments you will need quite a bit of resources.

Here are some guidelines for the minimum requirements around the physical environment that will be used to host your nested environments.


### High Level Diagram

![img](../../img/zPodFactory-overview-layers.svg)

VMware SDDC:

- vCenter Server 7.0u3+ or later
    - At least `4 vCPU / 16GB RAM / 250GB Storage` (SSD/NVMe recommended) for the zPodFactory appliance/management VM

    The zPodFactory Appliance will likely have a base 250GB disk, but usage will be much lower depending which products you download/use on your nested environments
    (you will be able to easily extend the disk using LVM if needed)

- NSX-T 3.1+ (for `nsx` basic deployment) or NSX 4.1.1+ (for `nsx-projects` features)

    - T0 & T1 Gateways pre-deployed and configured for proper N/S connectivity (a T1 could be used to host the zPodFactory appliance/management VM)
    - Layer 3 connectivity between the zPodFactory appliance/management VM and the target vCenter Server(ESXi hosts too for OVF/OVA tasks)/NSX Manager, and nested environments (zPodFactory will deploy a T1 linked to a specified T0 for all the nested environments)
    - a network supernet for deploying nested environments (`10.10.0.0/20` for example, as each nested environment will get a global `/24` subnet from this supernet, carved into 4 x `/26` subnets to be used with native vlan and guest vlan tagging within the nested environment)

- Decent Storage performance (SSD/NVMe) for the nested environments if possible (vSAN OSA/ESA is recommended) - 4TB+ of storage is recommended (depending on the number of nested environments you plan to deploy)
    - the zPodFactory Appliance or management vm (if installed manually) should take between 40-300GB of storage (depending how many components will be downloaded/used, and could grow over time)

> Please apply common sense here, as this is a `it depends...` type of answer :-)

Also from a networking perspective, in addition to the minimum requirements above, you will need to have a few things in place:

- if you plan to connect zPodFactory to multiple  `endpoints` (an endpoint is a concept that depicts where you deploy a nested environment(zPod), and consists of a vcsa/nsx pair, and mainly a supernet for zPods)

!!! info
    Please refer to the below [Network Section](./index.md#network-setup) that explains `endpoints` connectivity/requirements:



## Using the zPodFactory Appliance (recommended)

The zPodFactory appliance is a pre-built virtual machine that contains all the required components to run zPodFactory.

It is the recommended way to deploy zPodFactory, as it will simplify the installation process and will ensure that all the required components are installed and pre-configured properly.

## Manual Installation (not recommended)

If you prefer to install zPodFactory manually and potentially set yourself a dev environment for it, you can follow the below instructions.

We recommend starting with a [zBox 12.2](https://cloud.tsugliani.fr/ova/zbox-12.2.ova) appliance, as it is also the Linux distribution used for all our development and testing, and for the zPodFactory Appliance.  This should ensure all the steps we provide are as accurate and informative as possible.

Deploy the appliance and power it on with the correct networking ovf properties.

### Network setup

You can setup any additional specific networking configuration you need for your environment, but here is a quick example of what we use in our lab:

![img](../../img/zPodFactory-topology-overview-network-endpoints.svg)

- `eth0`: interface connected to a public IP (Internet)
- `eth1`: interface connected to the whole lab private network (L3/BGP fabric)

> PS: Remember that for zPodFactory to work correctly you need L3 connectivity to `vCenter Server and ESXi Hosts` (OVA/OVF uploads), and `NSX Manager API Access`.
Those will be necessary for automating the deployment of the Layer 1 nested part of the labs.
> Also required will be `connectivity access to the networks that we provision in NSX-T` for the nested environments (zPods), so that we can deploy the Layer 2 part of the labs. (ovf deploys, connections etc to the nested esxi hosts that will be the foundation for any nested environment)

### Storage setup

Let's update the appliance and install the latest updates:

``` { .sh data-copy="apt update && apt dist-upgrade" }
❯ apt update && apt dist-upgrade
```

Install `cloud-guest-utils` package:

``` { data-copy="apt install cloud-guest-utils" }
❯ apt install cloud-guest-utils
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following additional packages will be installed:
  gdisk
Suggested packages:
  cloud-init
The following NEW packages will be installed:
  cloud-guest-utils gdisk
0 upgraded, 2 newly installed, 0 to remove and 0 not upgraded.
Need to get 249 kB of archives.
After this operation, 979 kB of additional disk space will be used.
Do you want to continue? [Y/n]
Get:1 http://deb.debian.org/debian bookworm/main amd64 cloud-guest-utils all 0.33-1 [27.9 kB]
Get:2 http://deb.debian.org/debian bookworm/main amd64 gdisk amd64 1.0.9-2.1 [221 kB]
Fetched 249 kB in 0s (715 kB/s)
Selecting previously unselected package cloud-guest-utils.
(Reading database ... 42664 files and directories currently installed.)
Preparing to unpack .../cloud-guest-utils_0.33-1_all.deb ...
Unpacking cloud-guest-utils (0.33-1) ...
Selecting previously unselected package gdisk.
Preparing to unpack .../gdisk_1.0.9-2.1_amd64.deb ...
Unpacking gdisk (1.0.9-2.1) ...
Setting up gdisk (1.0.9-2.1) ...
Setting up cloud-guest-utils (0.33-1) ...
Processing triggers for man-db (2.11.2-2) ...
```

Check current partition scheme (we growed the VM disk to 750GB on vCenter):

``` { data-copy="fdisk -l" hl_lines="12 13 22"  }
❯ fdisk -l
Disk /dev/sda: 750 GiB, 805306368000 bytes, 1572864000 sectors
Disk model: Virtual disk
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xb2fbd5f2

Device     Boot   Start       End   Sectors  Size Id Type
/dev/sda1  *       2048    999423    997376  487M 83 Linux
/dev/sda2       1001470 104855551 103854082 49.5G  5 Extended
/dev/sda5       1001472 104855551 103854080 49.5G 8e Linux LVM


Disk /dev/mapper/vg-swap: 7.63 GiB, 8191475712 bytes, 15998976 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/mapper/vg-root: 41.89 GiB, 44979716096 bytes, 87851008 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
```

Grow the extended partition to the new maximum available geometry:

``` { data-copy="growpart /dev/sda 2" }
❯ growpart /dev/sda 2
CHANGED: partition=2 start=1001470 old: size=103854082 end=104855551 new: size=1571862497 end=1572863966
```

Check the changes:

``` { data-copy="fdisk -l" hl_lines="12" }
❯ fdisk -l
Disk /dev/sda: 750 GiB, 805306368000 bytes, 1572864000 sectors
Disk model: Virtual disk
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xb2fbd5f2

Device     Boot   Start        End    Sectors   Size Id Type
/dev/sda1  *       2048     999423     997376   487M 83 Linux
/dev/sda2       1001470 1572863966 1571862497 749.5G  5 Extended
/dev/sda5       1001472  104855551  103854080  49.5G 8e Linux LVM
```

Grow the logical partition used for LVM2:

``` { data-copy="growpart /dev/sda 5" }
❯ growpart /dev/sda 5
CHANGED: partition=5 start=1001472 old: size=103854080 end=104855551 new: size=1571862495 end=1572863966
```

Check the changes:

``` { data-copy="fdisk -l" hl_lines="13" }
❯ fdisk -l
Disk /dev/sda: 750 GiB, 805306368000 bytes, 1572864000 sectors
Disk model: Virtual disk
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xb2fbd5f2

Device     Boot   Start        End    Sectors   Size Id Type
/dev/sda1  *       2048     999423     997376   487M 83 Linux
/dev/sda2       1001470 1572863966 1571862497 749.5G  5 Extended
/dev/sda5       1001472 1572863966 1571862495 749.5G 8e Linux LVM
```

Verify physical volume details:

``` { data-copy="pvdisplay" hl_lines="5" }
❯ pvdisplay
  --- Physical volume ---
  PV Name               /dev/sda5
  VG Name               vg
  PV Size               749.52 GiB / not usable 1.98 MiB
  Allocatable           yes
  PE Size               4.00 MiB
  Total PE              191877
  Free PE               179200
  Allocated PE          12677
  PV UUID               B0U0tY-X3d5-koil-ORim-6F1t-8284-FgWArx
```

Resize the physical volume to the maximum available geometry (if growpart didn't take care of this):

``` { data-copy="pvresize /dev/sda5" }
❯ pvresize /dev/sda5
  Physical volume "/dev/sda5" changed
  1 physical volume(s) resized or updated / 0 physical volume(s) not resized
```

Display the `/dev/vg/root` details:

``` { data-copy="lvdisplay /dev/vg/root" hl_lines="11" }
❯ lvdisplay /dev/vg/root
  --- Logical volume ---
  LV Path                /dev/vg/root
  LV Name                root
  VG Name                vg
  LV UUID                15WYF1-uuTo-Go9v-kVGX-Yokc-CkXY-EMhgYf
  LV Write Access        read/write
  LV Creation host, time zbox, 2023-09-19 13:43:34 +0000
  LV Status              available
  # open                 1
  LV Size                41.89 GiB
  Current LE             10724
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           254:1
```

Now let's extend this to the available space on the PV:

``` { .sh data-copy="lvextend -l +100%FREE /dev/vg/root" }
❯ lvextend -l +100%FREE /dev/vg/root
  Size of logical volume vg/root changed from 41.89 GiB (10724 extents) to 741.89 GiB (189924 extents).
  Logical volume vg/root successfully resized.
```

Verify the current filesystem free space information:

``` { .sh data-copy="duf -only local" hl_lines="7" }
❯ duf -only local
╭────────────────────────────────────────────────────────────────────────────────────────────╮
│ 2 local devices                                                                            │
├────────────┬────────┬───────┬────────┬───────────────────────────────┬──────┬──────────────┤
│ MOUNTED ON │   SIZE │  USED │  AVAIL │              USE%             │ TYPE │ FILESYSTEM   │
├────────────┼────────┼───────┼────────┼───────────────────────────────┼──────┼──────────────┤
│ /          │  40.9G │  1.5G │  37.3G │ [....................]   3.7% │ ext4 │ /dev/vg/root │
│ /boot      │ 446.2M │ 57.7M │ 360.2M │ [##..................]  12.9% │ ext4 │ /dev/sda1    │
╰────────────┴────────┴───────┴────────┴───────────────────────────────┴──────┴──────────────╯
```

We now need to do a filesystem resize to take into account the new geometry and verify the filesystem afterwards:

``` { .sh data-copy="resize2fs /dev/vg/root" }
❯ resize2fs /dev/vg/root
resize2fs 1.47.0 (5-Feb-2023)
Filesystem at /dev/vg/root is mounted on /; on-line resizing required
old_desc_blocks = 6, new_desc_blocks = 93
The filesystem on /dev/vg/root is now 194482176 (4k) blocks long.
```

``` { .sh data-copy="duf -only local" hl_lines="7" }
❯ duf -only local
╭────────────────────────────────────────────────────────────────────────────────────────────╮
│ 2 local devices                                                                            │
├────────────┬────────┬───────┬────────┬───────────────────────────────┬──────┬──────────────┤
│ MOUNTED ON │   SIZE │  USED │  AVAIL │              USE%             │ TYPE │ FILESYSTEM   │
├────────────┼────────┼───────┼────────┼───────────────────────────────┼──────┼──────────────┤
│ /          │ 730.0G │  1.5G │ 698.3G │ [....................]   0.2% │ ext4 │ /dev/vg/root │
│ /boot      │ 446.2M │ 57.7M │ 360.2M │ [##..................]  12.9% │ ext4 │ /dev/sda1    │
╰────────────┴────────┴───────┴────────┴───────────────────────────────┴──────┴──────────────╯
```

We now have a 730GB root filesystem, which will be more than enough for a while if you are using MANY VMware products in your nested labs.

### DNS configuration

zPodFactory does manage the DNS configuration for the nested environments, so you will need to configure a DNS server that will be used by the nested environments.

For this we are using `dnsmasq`, a simple linux daemon that serves as our DNS facility.

It will rely on a watchdog, that will check any modification to the configuration file, and will send a `SIGHUP` signal to the `dnsmasq` process to reload the configuration.

Let's set up the base `dnsmasq` configuration file `/etc/dnsmasq.conf`:

```ini title="/etc/dnsmasq.conf"
listen-address=127.0.0.1,10.96.42.137
interface=lo,eth1
bind-interfaces
expand-hosts
dns-forward-max=1500
cache-size=10000
no-dhcp-interface=lo,eth0,eth1
server=10.96.42.10
domain=nested.lab
local=/nested.lab/
server=/zpod.io/10.96.42.10
server=/zpodfactory.io/10.96.42.11
server=/rax.lab/172.20.0.5
servers-file=/zPod/zPodDnsmasqServers/servers.conf
```

This is obviously tied to my specific configuration so i'll highlight the important parts:

- `listen-address`: the IP address(es) that dnsmasq will listen on
- `interface`: the interface(s) that dnsmasq will listen on
- `no-dhcp-interface`: the interface(s) that dnsmasq will not listen on for DHCP requests (We don't need a DHCP Server on this VM)
- `server`: the DNS server(s) that dnsmasq will use to resolve DNS requests upstream
- `domain` and `local`: the domain name that dnsmasq will use to resolve DNS requests locally for the deployed nested envs:

As an example if you put nested.lab here, every zPod deployed, will have a DNS name like this:

- `zpodname.nested.lab`

and all the DNS requests for this domain will be resolved by another dnsmasq instance on the nested environment itself also through dnsmasq.

- `server=/specificdomain/dnsip`: this is used to forward specific DNS requests to a specific DNS server, in this case we are forwarding all the requests for the `zpod.io` domain to the DNS server
- `servers-file`: this is the file that will be used to store the DNS records for the deployed nested environments

> Every time a nested environment is deployed or destroyed, the `servers-file` configuration file will be updated with the new information, and the watchdog will send a SIGHUP signal to dnsmasq to reload the configuration.

Create the following systemd service file `/etc/systemd/system/zdnsmasqservers.service`:

```ini title="/etc/systemd/system/zdnsmasqservers.service"
[Unit]
Description=zPodFactory dnsmasq watchdog
After=network.target

[Service]
User=root
Type=simple
ExecStart=/usr/bin/python3 -u /usr/local/bin/zdnsmasqservers-watchdog.py
Restart=always

SyslogIdentifier=zdnsmasqservers


[Install]
WantedBy=multi-user.target
```

Create the following python script `/usr/local/bin/zdnsmasqservers-watchdog.py` associated to the systemd service file above:

```python title="/usr/local/bin/zdnsmasqservers-watchdog.py"
#!/usr/bin/env python3
import subprocess
import time

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class Handler(PatternMatchingEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return None

        if event.event_type == "modified":
            print(
                f"{event.src_path} file was {event.event_type} - "
                "Send SIGHUP to dnsmasq..."
            )
            subprocess.call(["pkill", "-SIGHUP", "dnsmasq"])


if __name__ == "__main__":
    event_handler = Handler(patterns=["servers.conf"])
    observer = Observer()
    observer.schedule(
        event_handler,
        "/zPod/zPodDnsmasqServers", # this is the directory where the servers.conf file will be stored
        recursive=False,
    )
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

Install python3-watchdog package used in the script.

``` { data-copy="apt install python3-pip python3-watchdog" }
❯ apt install python3-pip python3-watchdog
```

Change permissions to provide execution permission on the script:

``` { data-copy="chmod +x /usr/local/bin/zdnsmasqservers-watchdog.py" }
❯ chmod +x /usr/local/bin/zdnsmasqservers-watchdog.py
```

Create the `/zPod/zPodDnsmasqServers` directory:

``` { data-copy="mkdir -p /zPod/zPodDnsmasqServers" }
❯ mkdir -p /zPod/zPodDnsmasqServers
```

Reload systemctl daemon:

```  { data-copy="systemctl daemon-reload" }
❯ systemctl daemon-reload
```

Enable the service:

``` { data-copy="systemctl enable zdnsmasqservers.service" }
❯ systemctl enable zdnsmasqservers.service
Created symlink /etc/systemd/system/multi-user.target.wants/zdnsmasqservers.service → /etc/systemd/system/zdnsmasqservers.service.
```

Start the service:

``` { data-copy="systemctl start zdnsmasqservers.service" }
❯ systemctl start zdnsmasqservers.service
```

Verify the service is running:

``` { data-copy="systemctl status zdnsmasqservers.service" }
❯ systemctl status zdnsmasqservers.service
● zdnsmasqservers.service - zPodFactory dnsmasq watchdog
     Loaded: loaded (/etc/systemd/system/zdnsmasqservers.service; enabled; preset: enabled)
     Active: active (running) since Thu 2023-10-05 14:42:19 UTC; 8min ago
   Main PID: 13681 (python3)
      Tasks: 4 (limit: 19135)
     Memory: 8.1M
        CPU: 66ms
     CGroup: /system.slice/zdnsmasqservers.service
             └─13681 /usr/bin/python3 -u /usr/local/bin/zdnsmasqservers-watchdog.py

Oct 05 14:42:19 zpodfactory systemd[1]: Started zdnsmasqservers.service - zPodFactory dnsmasq watchdog.
```

Check the logs (this is an example where I edited the file manually to check the watchdog could detect changes and was sending the `SIGHUP` signal to `dnsmasq`):

You'll have this behavior happen everytime you deploy or destroy a new nested environment.

``` { data-copy="journalctl -u zdnsmasqservers.service" }
❯ journalctl -u zdnsmasqservers.service


Oct 05 14:42:19 zpodfactory systemd[1]: Started zdnsmasqservers.service - zPodFactory dnsmasq watchdog.
Oct 05 14:42:31 zpodfactory zdnsmasqservers[13681]: /zPod/zPodDnsmasqServers/servers.conf file was modified - Send SIGHUP to dnsmasq...
```

### Docker installation

The whole project relies on a [docker compose](https://docs.docker.com/compose) application stack.

``` { data-copy="apt install docker-ce docker-compose-plugin" }
❯ apt install docker-ce docker-compose-plugin
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following additional packages will be installed:
  containerd.io docker-buildx-plugin docker-ce-cli iptables libip6tc2 libltdl7 libslirp0 pigz slirp4netns
Suggested packages:
  aufs-tools cgroupfs-mount | cgroup-lite firewalld
The following NEW packages will be installed:
  containerd.io docker-buildx-plugin docker-ce docker-ce-cli docker-compose-plugin iptables libip6tc2 libltdl7 libslirp0 pigz
  slirp4netns
0 upgraded, 11 newly installed, 0 to remove and 0 not upgraded.
Need to get 108 MB of archives.
After this operation, 403 MB of additional disk space will be used.
Do you want to continue? [Y/n]
```

### zPodCore installation

Clone the zPodCore repository:

``` { data-copy="git clone https://github.com/zPodFactory/zpodcore.git" }
❯ git clone https://github.com/zPodFactory/zpodcore.git

Cloning into 'zpodcore'...
remote: Enumerating objects: 4344, done.
remote: Counting objects: 100% (1543/1543), done.
remote: Compressing objects: 100% (606/606), done.
remote: Total 4344 (delta 941), reused 1317 (delta 819), pack-reused 2801
Receiving objects: 100% (4344/4344), 1.22 MiB | 9.36 MiB/s, done.
Resolving deltas: 100% (2677/2677), done.

```

Install python poetry:

``` { data-copy="apt install python3-poetry" }
❯ apt install python3-poetry
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following additional packages will be installed:
  adwaita-icon-theme at-spi2-common at-spi2-core build-essential cpp cpp-12 dconf-gsettings-backend dconf-service dpkg-dev fakeroot fontconfig g++ g++-12 gcc gcc-12 gcr gnome-keyring
  gnome-keyring-pkcs11 gsettings-desktop-schemas gtk-update-icon-cache hicolor-icon-theme libalgorithm-diff-perl libalgorithm-diff-xs-perl libalgorithm-merge-perl libasan8
  libatk-bridge2.0-0 libatk1.0-0 libatomic1 libatspi2.0-0 libavahi-client3 libavahi-common-data libavahi-common3 libcairo-gobject2 libcairo2 libcc1-0 libcolord2 libcups2 libdatrie1
  libdconf1 libdpkg-perl libepoxy0 libfakeroot libfile-fcntllock-perl libfribidi0 libgcc-12-dev libgck-1-0 libgcr-base-3-1 libgcr-ui-3-1 libgdk-pixbuf-2.0-0 libgdk-pixbuf2.0-bin
  libgdk-pixbuf2.0-common libgomp1 libgraphite2-3 libgtk-3-0 libgtk-3-bin libgtk-3-common libharfbuzz0b libisl23 libitm1 liblcms2-2 liblsan0 libmpc3 libmpfr6 libpam-gnome-keyring
  libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0 libquadmath0 librsvg2-2 librsvg2-common libsecret-1-0 libsecret-common libstdc++-12-dev libthai-data libthai0 libtsan2
  libubsan1 libwayland-client0 libwayland-cursor0 libwayland-egl1 libxcb-render0 libxcb-shm0 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxinerama1 libxkbcommon0 libxrandr2
  libxrender1 libxtst6 make p11-kit p11-kit-modules pinentry-gnome3 python-pkginfo-doc python3-attr python3-cachecontrol python3-cleo python3-crashtest python3-distlib python3-dulwich
  python3-fastimport python3-filelock python3-html5lib python3-importlib-metadata python3-jaraco.classes python3-jeepney python3-json-pointer python3-jsonschema python3-keyring
  python3-lockfile python3-more-itertools python3-msgpack python3-packaging python3-pexpect python3-pip-whl python3-pkginfo python3-platformdirs python3-poetry-core python3-ptyprocess
  python3-pylev python3-pyrsistent python3-rfc3987 python3-secretstorage python3-setuptools-whl python3-shellingham python3-tomlkit python3-uritemplate python3-virtualenv python3-webcolors
  python3-webencodings python3-wheel-whl python3-zipp x11-common
Suggested packages:
  cpp-doc gcc-12-locales cpp-12-doc debian-keyring g++-multilib g++-12-multilib gcc-12-doc gcc-multilib autoconf automake libtool flex bison gdb gcc-doc gcc-12-multilib colord cups-common
  bzr gvfs liblcms2-utils librsvg2-bin libstdc++-12-doc make-doc pinentry-doc python-attr-doc python-cleo-doc python3-gpg python3-genshi python3-lxml python-jsonschema-doc gir1.2-secret-1
  libkf5wallet-bin python3-keyrings.alt python-lockfile-doc python-pexpect-doc python-secretstorage-doc
The following NEW packages will be installed:
  adwaita-icon-theme at-spi2-common at-spi2-core build-essential cpp cpp-12 dconf-gsettings-backend dconf-service dpkg-dev fakeroot fontconfig g++ g++-12 gcc gcc-12 gcr gnome-keyring
  gnome-keyring-pkcs11 gsettings-desktop-schemas gtk-update-icon-cache hicolor-icon-theme libalgorithm-diff-perl libalgorithm-diff-xs-perl libalgorithm-merge-perl libasan8
  libatk-bridge2.0-0 libatk1.0-0 libatomic1 libatspi2.0-0 libavahi-client3 libavahi-common-data libavahi-common3 libcairo-gobject2 libcairo2 libcc1-0 libcolord2 libcups2 libdatrie1
  libdconf1 libdpkg-perl libepoxy0 libfakeroot libfile-fcntllock-perl libfribidi0 libgcc-12-dev libgck-1-0 libgcr-base-3-1 libgcr-ui-3-1 libgdk-pixbuf-2.0-0 libgdk-pixbuf2.0-bin
  libgdk-pixbuf2.0-common libgomp1 libgraphite2-3 libgtk-3-0 libgtk-3-bin libgtk-3-common libharfbuzz0b libisl23 libitm1 liblcms2-2 liblsan0 libmpc3 libmpfr6 libpam-gnome-keyring
  libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0 libquadmath0 librsvg2-2 librsvg2-common libsecret-1-0 libsecret-common libstdc++-12-dev libthai-data libthai0 libtsan2
  libubsan1 libwayland-client0 libwayland-cursor0 libwayland-egl1 libxcb-render0 libxcb-shm0 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxinerama1 libxkbcommon0 libxrandr2
  libxrender1 libxtst6 make p11-kit p11-kit-modules pinentry-gnome3 python-pkginfo-doc python3-attr python3-cachecontrol python3-cleo python3-crashtest python3-distlib python3-dulwich
  python3-fastimport python3-filelock python3-html5lib python3-importlib-metadata python3-jaraco.classes python3-jeepney python3-json-pointer python3-jsonschema python3-keyring
  python3-lockfile python3-more-itertools python3-msgpack python3-packaging python3-pexpect python3-pip-whl python3-pkginfo python3-platformdirs python3-poetry python3-poetry-core
  python3-ptyprocess python3-pylev python3-pyrsistent python3-rfc3987 python3-secretstorage python3-setuptools-whl python3-shellingham python3-tomlkit python3-uritemplate python3-virtualenv
  python3-webcolors python3-webencodings python3-wheel-whl python3-zipp x11-common
0 upgraded, 138 newly installed, 0 to remove and 0 not upgraded.
Need to get 85.3 MB of archives.
After this operation, 331 MB of additional disk space will be used.
Do you want to continue? [Y/n]
```

Disable experimental new installer (poetry)

``` { data-copy="poetry config experimental.new-installer false" }
❯ poetry config experimental.new-installer false
```

Requirement for poetry install on `psycopg2`

``` { data-copy="apt install libpq-dev" }
❯ apt install libpq-dev
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following additional packages will be installed:
  libssl-dev
Suggested packages:
  postgresql-doc-15 libssl-doc
The following NEW packages will be installed:
  libpq-dev libssl-dev
0 upgraded, 2 newly installed, 0 to remove and 0 not upgraded.
Need to get 2,568 kB of archives.
After this operation, 13.2 MB of additional disk space will be used.
Do you want to continue? [Y/n]
Get:1 http://deb.debian.org/debian bookworm/main amd64 libssl-dev amd64 3.0.9-1 [2,428 kB]
Get:2 http://deb.debian.org/debian bookworm/main amd64 libpq-dev amd64 15.3-0+deb12u1 [140 kB]
Fetched 2,568 kB in 0s (18.3 MB/s)
Selecting previously unselected package libssl-dev:amd64.
(Reading database ... 54499 files and directories currently installed.)
Preparing to unpack .../libssl-dev_3.0.9-1_amd64.deb ...
Unpacking libssl-dev:amd64 (3.0.9-1) ...
Selecting previously unselected package libpq-dev.
Preparing to unpack .../libpq-dev_15.3-0+deb12u1_amd64.deb ...
Unpacking libpq-dev (15.3-0+deb12u1) ...
Setting up libssl-dev:amd64 (3.0.9-1) ...
Setting up libpq-dev (15.3-0+deb12u1) ...
Processing triggers for man-db (2.11.2-2) ...
```

Install `pyenv`

``` { data-copy="git clone https://github.com/pyenv/pyenv.git ~/.pyenv" }
❯ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
Cloning into '/root/.pyenv'...
remote: Enumerating objects: 23497, done.
remote: Counting objects: 100% (2072/2072), done.
remote: Compressing objects: 100% (217/217), done.
remote: Total 23497 (delta 1907), reused 1931 (delta 1839), pack-reused 21425
Receiving objects: 100% (23497/23497), 4.69 MiB | 20.86 MiB/s, done.
Resolving deltas: 100% (15988/15988), done.
```

Setup `pyenv` for the currently installed `zsh` shell

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

source ~/.zshrc
```

Python library requirements for compilation

``` { data-copy="apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev libffi-dev liblzma-dev python3-openssl git" }
❯ apt install build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev \
libffi-dev liblzma-dev python3-openssl git
```

Setup an additional apt list for some additional packages

```bash
wget -qO - 'https://proget.makedeb.org/debian-feeds/prebuilt-mpr.pub' | gpg --dearmor | tee /usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg 1> /dev/null
echo "deb [arch=all,$(dpkg --print-architecture) signed-by=/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg] https://proget.makedeb.org prebuilt-mpr $(lsb_release -cs)" |  tee /etc/apt/sources.list.d/prebuilt-mpr.list
apt update
```

``` { data-copy="apt install just bc" }
❯ apt install just bc
```

Here is a facility script called deploy.sh that will help launch the docker compose full application stack with some pre-configured settings through the zPodAPI. (curl is used for this)

``` sh title="/root/git/zpodcore/deploy.sh"
#!/usr/bin/sh

PS4="$(tput setaf 3)>>>$(tput sgr0) "

ZPODAPI_URL=10.96.42.137:8000

set -x

# Shut down docker
docker compose down

# Restart docker
just zpodcore-start-background
sleep 10

# Execute first flow to prep prefect
# This avoids the unique key error "uq_configuration__key" problem when scheduling a lot of deployments to run at the same time
just zpodengine-cmd python src/zpodengine/flow_init.py

# Deploy
just zpodengine-deploy-all


# Set zpodfactory_host (the zPodFactory VM IP listening for API requests)
curl -X PATCH http://$ZPODAPI_URL/settings/name=zpodfactory_host -H "Content-Type: application/json" -d '{
  "value": "10.96.42.137"
}'

# Set zpodfactory_instances_domain
curl -X PATCH http://$ZPODAPI_URL/settings/name=zpodfactory_instances_domain -H "Content-Type: application/json" -d '{
  "value": "mcsa.cloud"
}'

# Set zpodfactory_ssh_key
curl -X PATCH http://$ZPODAPI_URL/settings/name=zpodfactory_ssh_key -H "Content-Type: application/json" -d '{
  "value": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/i56xhpfJKBC9TaL4BlPP3eDY03Csf4aLIM4OkSGDlTwNbadu5doGb8x/Z7650xsxXTuDq22UEVv0fuklc3DCl3NP9yv27LNj54g9WZPrC0wlDZOblvQo52atjkh4SIYZp5Rn9FFY+Vwc5/c3widbZ8OrNynS4QkKWrZHfmrjzWR0ZwGZPgTNxRiD0db6XVfxAxr3MuTKEd2yKlWenS8+ZEKnjR1nhEC6awmkt8p/uNZvyKHcVQ4Goyeo6EKaJf5JtdSV6mnN0lL3URuvDefrJygFzTNqhu1bwiXQl/zG969HaAkNRA4FhM2BIziIjCAzXrmQoaY8+5bWDXJg3kdp root@zPodMaster"
}'

# Set zpodfactory_customerconnect_username
curl -X PATCH http://$ZPODAPI_URL/settings/name=zpodfactory_customerconnect_username -H "Content-Type: application/json" -d '{
  "value": "USERNAME@EMAIL.COM"
}'

# Set zpodfactory_customerconnect_password
curl -X PATCH http://$ZPODAPI_URL/settings/name=zpodfactory_customerconnect_password -H "Content-Type: application/json" -d '{
  "value": "PASSWORD"
}'

# Set some VMware licenses
curl -X POST http://$ZPODAPI_URL/settings -H "Content-Type: application/json" -d '{
  "name": "license_vcsa-8_esxi",
  "description": "vSphere 8 Enterprise Plus with Add-on for Kubernetes",
  "value": "XXXXX-XXXXX-XXXXX-XXXXXX-XXXXX"
}'

curl -X POST http://$ZPODAPI_URL/settings -H "Content-Type: application/json" -d '{
  "name": "license_vcsa-8_vcenter",
  "description": "vCenter Server 8 Standard",
  "value": "XXXXX-XXXXX-XXXXX-XXXXXX-XXXXX"
}'

curl -X POST http://$ZPODAPI_URL/settings -H "Content-Type: application/json" -d '{
  "name": "license_vcsa-8_vsan",
  "description": "vSAN Enterprise Plus",
  "value": "XXXXX-XXXXX-XXXXX-XXXXXX-XXXXX"
}'

curl -X POST http://$ZPODAPI_URL/settings -H "Content-Type: application/json" -d '{
  "name": "license_vcsa-8_tanzu",
  "description": "Tanzu Standard (Subscription)",
  "value": "XXXXX-XXXXX-XXXXX-XXXXXX-XXXXX"
}'

# Set NSX license
curl -X POST http://$ZPODAPI_URL/settings -H "Content-Type: application/json" -d '{
  "name": "license_nsx-4_enterprise",
  "description": "NSX Data Center Enterprise Plus",
  "value": "XXXXX-XXXXX-XXXXX-XXXXXX-XXXXX"
}'


# Create RAX-MCA endpoint
curl -X POST http://$ZPODAPI_URL/endpoints -H "Content-Type: application/json" -d '{
  "name": "rax-mca",
  "description": "MCA Prod Environment",
  "endpoints": {
    "compute": {
      "name": "vcsa.rax.lab",
      "driver": "vsphere",
      "hostname": "vcsa.rax.lab",
      "username": "USERNAME",
      "password": "PASSWORD",
      "datacenter": "Chicago",
      "resource_pool": "SDDC",
      "storage_policy": "zPods",
      "storage_datastore": "vsanDatastore",
      "contentlibrary": "zPodFactory",
      "vmfolder": "zPods-MCA"
    },
    "network": {
      "name": "nsx.rax.lab",
      "driver": "nsxt-projects",
      "hostname": "nsx.rax.lab",
      "username": "USERNAME",
      "password": "PASSWORD",
      "networks": "10.196.128.0/17",
      "transportzone": "nsx-overlay-transportzone",
      "edgecluster": "edgecluster-mca",
      "t0": "T0-MCA",
      "macdiscoveryprofile": "Nested-Mac-Discovery-Profile"
    }
  },
  "enabled": true
}'


# Add libraries
curl -X POST http://$ZPODAPI_URL/libraries -H "Content-Type: application/json" -d '{
  "name": "default",
  "description": "Default zPodFactory library",
  "git_url": "https://github.com/zpodfactory/zpodlibrary"
}'

# Enable component zbox
curl -X PUT http://$ZPODAPI_URL/components/uid=zbox-12.1/enable

# Enable component esxi
curl -X PUT http://$ZPODAPI_URL/components/uid=esxi-8.0u2/enable

# Enable component esxi
curl -X PUT http://$ZPODAPI_URL/components/uid=vcsa-8.0u2/enable

# Enable component nsx
curl -X PUT http://$ZPODAPI_URL/components/uid=nsx-4.1.1.0/enable

# Add zbox profile
curl -X POST http://$ZPODAPI_URL/profiles?force=true -H "Content-Type: application/json" -d '{
  "name": "zbox",
  "profile": [
    {
      "component_uid": "zbox-12.1"
    }
  ]
}'

# Add hosts profile
curl -X POST http://$ZPODAPI_URL/profiles?force=true -H "Content-Type: application/json" -d '{
  "name": "hosts",
  "profile": [
    {
      "component_uid": "zbox-12.1"
    },
    [
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 11,
        "hostname": "esxi11",
        "vcpu": 4,
        "vmem": 12
      },
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 12,
        "hostname": "esxi12",
        "vcpu": 4,
        "vmem": 12
      }
    ]
  ]
}'

# Add 'base' profile
curl -X POST http://$ZPODAPI_URL/profiles?force=true -H "Content-Type: application/json" -d '{
  "name": "base",
  "profile": [
    {
      "component_uid": "zbox-12.1"
    },
    [
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 11,
        "hostname": "esxi11",
        "vcpu": 4,
        "vmem": 48
      },
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 12,
        "hostname": "esxi12",
        "vcpu": 4,
        "vmem": 48
      }
    ],
    {
        "component_uid": "vcsa-8.0u2"
    }
  ]
}'

# Add 'sddc' profile
curl -X POST http://$ZPODAPI_URL/profiles?force=true -H "Content-Type: application/json" -d '{
  "name": "sddc",
  "profile": [
    {
      "component_uid": "zbox-12.1"
    },
    [
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 11,
        "hostname": "esxi11",
        "vcpu": 6,
        "vmem": 48
      },
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 12,
        "hostname": "esxi12",
        "vcpu": 6,
        "vmem": 48
      },
      {
        "component_uid": "esxi-8.0u2",
        "host_id": 13,
        "hostname": "esxi13",
        "vcpu": 6,
        "vmem": 48
      }
    ],
    {
        "component_uid": "vcsa-8.0u2"
    },
    {
        "component_uid": "nsx-4.1.1.0"
    }
  ]
}'

# Add 'sddc-large' profile
curl -X POST http://$ZPODAPI_URL/profiles?force=true -H "Content-Type: application/json" -d '{
  "name": "sddc-large",
  "profile": [
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
        "component_uid": "nsx-4.1.1.0"
    }
  ]
}'

docker compose logs -f
```

Make the script executable

``` { data-copy="chmod +x /root/git/zpodcore/deploy.sh" }
❯ chmod +x /root/git/zpodcore/deploy.sh
```

Then you can build docker compose containers with the following command:

``` { data-copy="docker compose build" }
❯ docker compose build
```

Finally launch the docker compose application stack with our script:

``` { data-copy="./deploy.sh" }
❯ ./deploy.sh
```

This should take a while at first launch, and display everything happening in the background as we are tailing the docker compose logs in the end.

You can now head to the [Administration Guide](../admin/index.md) to learn how to setup/manage zPodFactory.
