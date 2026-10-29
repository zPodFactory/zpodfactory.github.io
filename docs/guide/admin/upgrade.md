# Upgrading

zpodcore releases are tagged `vX.Y.Z`; [What's new](../../releases.md) summarises each one, and the [changelog](https://github.com/zPodFactory/zpodcore/blob/main/CHANGELOG.md) has every change, with a **Breaking** section when a release has one. Read it before you upgrade.

## Upgrade the stack

On the appliance, from the zpodcore directory: note where you are, update uv, pull `main` so the justfile has the latest recipes, dump the database, then upgrade:

``` { data-copy="git describe --tags && uv self update && git checkout main && git pull && just zpodcore-db-dump && just zpod-update" }
❯ cd ~/git/zpodcore
❯ git describe --tags      # where a roll back returns to: note it
v0.9.0-2-g3f85190
❯ uv self update
❯ git checkout main && git pull
❯ just zpodcore-db-dump
❯ just zpod-update
```

`zpod-update` follows `main` by default. To run a release instead, give its version: `just zpod-update 0.9.2`.

- zpodcore needs uv 0.9.17 or later: older versions fail on `exclude-newer = "30 days"` (the 30-day supply-chain delay) with a TOML parse error. `uv self update` works when uv came from its standalone installer; otherwise update it the way it was installed (`pip`, `brew`, …). Coming from 0.7.x, see [below](#from-07x-to-08-or-later) first.
- The checkout must be clean: `git status` should list no modified files. Stash or commit local changes (`git stash`), and move away untracked files a pull would overwrite. Ignored files (`.env`, database dumps) are fine. `zpod-update` refuses to run otherwise.
- Pull before dumping: the dump recipe only exists from 0.9.1 on. The running API reloads the pulled code right away, so run the last two commands without waiting; `zpod-update` rebuilds and restarts the stack.

`zpodcore-db-dump` writes `zpodcore-db-<UTC timestamp>.sql` to the zpodcore directory. It holds every secret zpodcore knows (API tokens, passwords, endpoint credentials): keep it safe, off the appliance.

`zpod-update` refuses to run on a working tree with uncommitted changes. It checks out `main` (and pulls it) or the release tag, rebuilds the images, restarts the stack, waits for the API, then redeploys the flows. It prints which versions it crosses.

Then update `zcli` on every workstation to the API's `major.minor`, since the API refuses any other (see [Set up the zPod CLI (zcli)](../zcli.md#install)):

``` { data-copy="uv tool install zpodcli==0.9.2" }
❯ uv tool install zpodcli==0.9.2
```

## Roll back

!!! warning "Last resort"
    A roll back replaces the whole database with the dump: everything done since it was taken is lost from zpodcore, while vSphere and NSX keep it. zPods deployed or destroyed in between, and networks added or removed, no longer match what zpodcore knows. Make sure you understand what you are doing, or [contact a maintainer](troubleshooting.md#getting-help) for additional support before rolling back.

Restore the dump while the new code is still checked out, then go back to what `git describe --tags` printed before the upgrade:

``` { data-copy="just zpodcore-db-restore zpodcore-db-20261028T190840Z.sql && just zpod-update v0.9.0-2-g3f85190" }
❯ just zpodcore-db-restore zpodcore-db-20261028T190840Z.sql
❯ just zpod-update v0.9.0-2-g3f85190
```

`zpodcore-db-restore` asks you to type the database name, dumps the current database first, and leaves the stack stopped so the new code can't migrate the restored database again.

## From 0.7.x to 0.8 or later

0.8.0 was the first release after two years. These steps are not automatic:

1. **Back up the database**, as in [Upgrade the stack](#upgrade-the-stack). The migration drops the `zpod_features` table (features now live as JSON on the zPod), and the Postgres image moved from bullseye to trixie, so every database is reindexed on first start. Neither is reversible.
2. **Host toolchain**: uv replaces pyenv and Poetry.
3. **Prefect 2 → 3**: stop the stack, remove the Prefect volume, start it again, then run `just zpodengine-deploy-all`. Flow-run history is lost.
4. **zbox → zcore**: run `just zcore-transition`; see [zcore migration](zcore-migration.md).
5. **Broadcom downloads**: set the [Broadcom download token](broadcom-download-token.md). Library entries still using the removed `customerconnect` or `avipulse` engines end in `FAILED_UNSUPPORTED_ENGINE`.
6. **Optional**: set `compute.vds` on endpoints whose NSX transport zone spans several VDSs, and review the new [feature flags](feature-flags.md).

The `.env` file does not change; new behaviour comes from settings seeded when the API starts.

## From 0.8 to 0.9

- **Upgrade to 0.9.1 or later.** 0.9.0's migration fails on factories where a zPod deploy was retried; if you are stuck on 0.9.0 (the API answers `500`), run `just zpod-update 0.9.1`.
- **zcore 13.7** is the new default core. Profiles still on `zcore-13.5` keep working but miss the storage features and network masquerade; see [zcore migration](zcore-migration.md#profiles-already-on-zcore-135).
- **Datastore floor**: deploys and component adds now stop when the endpoint's datastore has less free space than [`zpodfactory_datastore_min_free_pct`](feature-flags.md#zpodfactory_datastore_min_free_pct) (default 15%).
