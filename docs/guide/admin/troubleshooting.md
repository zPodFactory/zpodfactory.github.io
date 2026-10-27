# Troubleshooting

There are two places to look when something goes wrong: the logs of the stack, and the flow engine UI.

## Logs

On the appliance, from the zpodcore directory:

``` { data-copy="cd ~/git/zpodcore && docker compose logs -f" }
❯ cd ~/git/zpodcore
❯ docker compose logs -f
```

Set [`zpodfactory_debug_level`](feature-flags.md#zpodfactory_debug_level) to `DEBUG` for more detail, including every API request and response. It takes effect without a restart.

## Flow engine UI

Deploys, destroys, component adds, disk changes and network routing all run as flows in the zPod Engine (Prefect). The Prefect UI shows each run, its logs and its artifacts:

- `http://<appliance-ip>:8060`

zcli and the Web UI print the name of the run they start, so you can find it there. For day-to-day administration, use the [Web UI](../user/web-ui.md) on port **8500** instead.

## Getting help

Open a [GitHub issue](https://github.com/zPodFactory/zpodcore/issues) with as much detail as you can: the command or action, its output, and the flow run's log.
