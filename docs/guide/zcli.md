# Set up the zPod CLI (zcli)

`zcli` is the zPodFactory command line. It manages zPods and, for administrators, the whole factory. The appliance has it installed and connected already; this page sets it up on your own workstation.

## Install

Using [uv](https://docs.astral.sh/uv/) (recommended, since it fetches the required Python 3.14 on its own):

``` { data-copy="uv tool install zpodcli" }
❯ uv tool install zpodcli
```

Or with `pip`, on Python 3.14 or later:

``` { data-copy="pip install zpodcli" }
❯ pip install zpodcli
```

!!! info "Match the CLI to the API"
    `zcli X.Y.*` works with zPod API `X.Y.*`, and patch numbers may differ. The API refuses a `zcli` with a different `major.minor` (HTTP `417`), and the error names the version to install, e.g. `uv tool install zpodcli==0.9.0`. Check yours with `zcli --version`.

Check that it runs:

``` { data-copy="zcli --help" }
❯ zcli --help

 Usage: zcli [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --factory             -f      <str>  Use specified factory for current       │
│                                      command.                                │
│ --output-svg                         Output an SVG file for any list         │
│                                      command.                                │
│ --version             -V             Display version information.            │
│ --install-completion                 Install completion for the current      │
│                                      shell.                                  │
│ --show-completion                    Show completion for the current shell,  │
│                                      to copy it or customize the             │
│                                      installation.                           │
│ --help                               Show this message and exit.             │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ component  Manage Components                                                 │
│ endpoint   Manage Endpoints                                                  │
│ enet       Manage ENets                                                      │
│ factory    Manage Factories                                                  │
│ group      Manage Permission Groups                                          │
│ library    Manage Libraries                                                  │
│ profile    Manage Profiles                                                   │
│ setting    Manage Settings                                                   │
│ user       Manage Users                                                      │
│ zpod       Manage zPods                                                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Connect to a factory

Add the factory with your API token. An administrator gives you yours; the first one, the `superuser` token with `superadmin` rights (every permission in the factory), is set up on the appliance at install.

``` {data-copy="zcli factory add myfactory -s http://zpodfactory.domain.lab:8000 -t TOKEN -a"}
❯ zcli factory add myfactory -s http://zpodfactory.domain.lab:8000 -t "TOKEN" -a
```

`-a` makes it the active factory. You can add several factories, switch the active one with `zcli factory update <factory> -a`, or pick one for a single command with `zcli -f <factory> …`.

Check the connection:

``` {data-copy="zcli user list"}
❯ zcli user list
```

![img](../img/zcli_user_list.svg)

The **API Token** column shows your own token (other users' rows are masked unless you're a superadmin), handy if you need it again without running `zcli user reset_api_token`.

## Output for scripts

List, get and info commands take `-j`/`--json` for JSON output, and `--no-color` to strip colours. JSON is plain when piped, so `zcli … -j | jq` works.

## Next steps

- [User Guide](user/index.md): zPods, components, networks, storage and DNS.
- [Administration](admin/index.md): settings, users, components, endpoints and profiles.
