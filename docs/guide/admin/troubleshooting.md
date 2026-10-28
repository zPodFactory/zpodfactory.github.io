# Troubleshooting

There are two places to look when something goes wrong: the logs of the stack, and the flow engine UI.

## Logs

On the appliance, from the zpodcore directory:

``` { data-copy="cd ~/git/zpodcore && docker compose logs -f" }
❯ cd ~/git/zpodcore
❯ docker compose logs -f
```

To start from a clean slate before reproducing a problem, recreate the stack: `docker compose down` removes the containers and their logs (the database and the flow engine's data stay, in their volumes), and the new containers start with empty logs. Bundle the old logs first if they might matter (see [Getting help](#getting-help)).

``` { data-copy="just zpodcore-stop && just zpodcore-start-background" }
❯ just zpodcore-stop
❯ just zpodcore-start-background
```

Set [`zpodfactory_debug_level`](feature-flags.md#zpodfactory_debug_level) to `DEBUG` for more detail, including every API request and response. It takes effect without a restart.

## Flow engine UI

Deploys, destroys, component adds, disk changes and network routing all run as flows in the zPod Engine (Prefect). The Prefect UI shows each run, its logs and its artifacts:

- `http://<appliance-ip>:8060`

zcli and the Web UI print the name of the run they start, so you can find it there. For day-to-day administration, use the [Web UI](../user/web-ui.md) on port **8500** instead.

## Getting help

Open a [GitHub issue](https://github.com/zPodFactory/zpodcore/issues) with as much detail as you can: the command or action, its output, and the flow run's log.

Attach a log bundle from the appliance, from the zpodcore directory:

``` { data-copy="just zpodcore-logs-dump 24h" }
❯ just zpodcore-logs-dump 24h
```

It writes `zpodcore-logs-<UTC timestamp>.tar.gz`: the log of every stack service, plus the zpodcore release and the containers' state. Leave out the time window (`24h`) for the full logs. Logs can hold tokens or passwords: check the bundle before you share it.
