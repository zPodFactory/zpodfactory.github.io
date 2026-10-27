# Upgrading

zpodcore releases are tagged `vX.Y.Z`; [What's new](../../releases.md) summarises each one, and the [changelog](https://github.com/zPodFactory/zpodcore/blob/main/CHANGELOG.md) has every change, with a **Breaking** section when a release has one. Read it before you upgrade.

## Upgrade the stack

On the appliance, from the zpodcore directory:

``` { data-copy="just zpod-update 0.9.0" }
❯ cd ~/git/zpodcore
❯ just zpod-update 0.9.0
```

`zpod-update` refuses to run on a working tree with uncommitted changes. It fetches the tag, rebuilds the images, restarts the stack, waits for the API, then redeploys the flows. It prints which versions it crosses.

Then update `zcli` on every workstation to the same `major.minor`, since the API refuses any other (see [Set up the zPod CLI (zcli)](../zcli.md#install)):

``` { data-copy="uv tool install zpodcli==0.9.0" }
❯ uv tool install zpodcli==0.9.0
```

## From 0.7.x to 0.8 or later

0.8.0 was the first release after two years. These steps are not automatic:

1. **Back up the database.** The migration drops the `zpod_features` table (features now live as JSON on the zPod), and the Postgres image moved from bullseye to trixie, so every database is reindexed on first start. Neither is reversible.
2. **Host toolchain**: uv replaces pyenv and Poetry.
3. **Prefect 2 → 3**: stop the stack, remove the Prefect volume, start it again, then run `just zpodengine-deploy-all`. Flow-run history is lost.
4. **zbox → zcore**: run `just zcore-transition`; see [zcore migration](zcore-migration.md).
5. **Broadcom downloads**: set the [Broadcom download token](broadcom-download-token.md). Library entries still using the removed `customerconnect` or `avipulse` engines end in `FAILED_UNSUPPORTED_ENGINE`.
6. **Optional**: set `compute.vds` on endpoints whose NSX transport zone spans several VDSs, and review the new [feature flags](feature-flags.md).

The `.env` file does not change; new behaviour comes from settings seeded when the API starts.

## From 0.8 to 0.9

- **zcore 13.7** is the new default core. Profiles still on `zcore-13.5` keep working but miss the storage features and network masquerade; see [zcore migration](zcore-migration.md#profiles-already-on-zcore-135).
- **Datastore floor**: deploys and component adds now stop when the endpoint's datastore has less free space than [`zpodfactory_datastore_min_free_pct`](feature-flags.md#zpodfactory_datastore_min_free_pct) (default 15%).
