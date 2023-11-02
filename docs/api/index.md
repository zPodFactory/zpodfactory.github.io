# API & SDK

## API

zPodFactory exposes it's own API through [FastAPI](https://fastapi.tiangolo.com/) which leverages the open standards for APIs:

- [OpenAPI](https://github.com/OAI/OpenAPI-Specification) (previously known as Swagger)
- [JSON Schema](https://json-schema.org/)

It can be accessed on your zPodFactory instance at the following address:

- `https://manager.zpodfactory.domain/openjson.json`

If you want to access the Swagger/docs UI, you can access it at the following address:

- `https://manager.zpodfactory.domain/docs`

That said, the API is not usually meant to be used directly, but rather through the SDK that is generated from the OpenAPI JSON schema.

SDK and CLI updates will be pushed to PyPi, but if you wanted to set up a developer environment and generate the SDK, you can always generate it yourself using the following `just` command.

[just](https://just.systems/man/en/) is basically a next-gen `Makefile` like command line tool, that allows to define tasks in a `justfile` and run them from the command line (as shown in the sample below screenshot)

![img](https://raw.githubusercontent.com/casey/just/master/screenshot.png)

Generate updated Python SDK binding from the running zPodFactory Project.

```bash
just zcli zpodsdk-update
```

We currently support a few just commands for this project and simplify some actions/tasks:

```bash
❯ just
Available recipes:
    alembic *args              # Run alembic command in zpodapi container
    alembic-downgrade rev="-1" # Downgrade database schema -1
    alembic-revision message='update' # Generate alembic revision
    alembic-upgrade rev="head" # Upgrade database schema to head
    docker-fullclean           # Docker prune everything
    zcli *args                 # Run zcli command
    zpodapi-coverage           # Generate coverage docs
    zpodapi-exec *args="bash"  # Connect to zpodapi container and run command
    zpodapi-generate-openapi   # Generate openapi json
    zpodapi-pytest *args       # Run pytest in zpodapi
    zpodcore-start $COLUMNS=rich_cols # Start Docker Environment
    zpodcore-start-background $COLUMNS=rich_cols # Start Docker Env in BG
    zpodcore-stop              # Stop Docker Environment
    zpodengine-deploy-all      # Deploy all Flows
    zpodengine-prefect *args   # Manually Run Prefect Command
    zpodsdk-update             # Update zpodsdk
```

## SDK

SDK is available on pypi:

- [https://pypi.org/project/zpodsdk/](https://pypi.org/project/zpodsdk/)

``` { data-copy="pip install zpodsdk"}
❯ pip install zpodsdk
```

## CLI

CLI is available on pypi:

- [https://pypi.org/project/zpodcli/](https://pypi.org/project/zpodcli/)

``` { data-copy="pip install zpodcli"}
❯ pip install zpodcli
```
