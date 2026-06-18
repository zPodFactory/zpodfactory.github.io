# Broadcom download token

Since March 2025, VMware product binaries are distributed through the **Broadcom offline depot** at `dl.broadcom.com`. Downloads require a per-customer **download token** embedded in the URL. zPodFactory stores this token in the `zpodfactory_broadcom_download_token` setting and substitutes it at download time — library JSON files use the placeholder `${BROADCOM_DOWNLOAD_TOKEN}` so tokens never need to be committed to git.

## How it works in zPodFactory

1. A component in the [zPodLibrary](https://github.com/zPodFactory/zPodLibrary) declares an `https` download engine with a depot URL such as (from [`vmware/vmware_nsx/4.2.4.0.json`](https://github.com/zPodFactory/zPodLibrary/blob/main/vmware/vmware_nsx/4.2.4.0.json)):

   ```
   https://dl.broadcom.com/${BROADCOM_DOWNLOAD_TOKEN}/PROD/COMP/NSX_T_MANAGER/nsx-unified-appliance-4.2.4.0.0.25410641.ova
   ```

2. When you run `zcli component enable <uid>`, the download engine reads `zpodfactory_broadcom_download_token` and replaces the placeholder before running `wget`.

3. If the token is missing, invalid, or expired, Broadcom returns **401/403** and the download fails. Use `zcli component upload` as a fallback to provide OVA/ISO files manually.

!!! info "Legacy settings"
    `zpodfactory_customerconnect_username` and `zpodfactory_customerconnect_password` are **no longer used**. The old Customer Connect CLI download engine has been removed.

## Obtaining a download token

You need a [Broadcom Support Portal](https://support.broadcom.com/) account with access to the VMware products you want to download.

### Prerequisites

- A Broadcom Support Portal login linked to your organization's VMware entitlements.
- The **Product Administrator** role for your site. This role is typically assigned by your organization's User Administrator on the portal. Without it, the **Generate Download Token** option will not appear.

Broadcom documents the process in [KB 390098 — VCF authenticated downloads configuration update instructions](https://knowledge.broadcom.com/external/article/390098).

### Steps

1. Log in to [support.broadcom.com](https://support.broadcom.com/).
2. Use the dropdown next to your username and select **VMware Cloud Foundation** (or the product context matching your entitlements).
3. Open **My Dashboard** (top-left pane).
4. Under **Quick Links** (bottom-right), click **Generate Download Token**.
5. Select the correct **Site** for your organization and click **Generate**.
6. Copy the token immediately — it is shown once at generation time.

!!! warning "Token activation delay"
    Broadcom notes that tokens may not be valid for a short period immediately after creation. If a download fails with 401/403 right after generating a token, wait a few minutes and retry.

!!! warning "Entitlements"
    The token authorizes downloads for products your site is entitled to. Enabling a component you are not licensed for will still fail even with a valid token.

## Configuring zPodFactory

Set the token via CLI (superadmin):

```bash
zcli setting update zpodfactory_broadcom_download_token --value "YOUR_TOKEN_HERE"
```

Or via API:

```bash
curl -X PATCH "http://zpodfactory.domain.lab:8000/settings/name=zpodfactory_broadcom_download_token" \
  -H "Content-Type: application/json" \
  -d '{"value": "YOUR_TOKEN_HERE"}'
```

Verify the setting (the token is stored in plain text in the settings table — restrict API access accordingly):

```bash
zcli setting list
```

### Network requirements

The zPodFactory host (or zPod Engine container) must reach **`dl.broadcom.com`** over HTTPS when downloading components. Ensure outbound firewall rules allow this.

## Testing a download

1. Confirm the token is set: `zcli setting list | grep broadcom`
2. Resync the library: `zcli library resync default`
3. Enable a component you are entitled to:

   ```bash
   zcli component enable nsx-4.2.4.0
   ```

4. Watch progress: `zcli component get nsx-4.2.4.0`

On success, download status shows `COMPLETED` and status `ACTIVE`. Check Prefect logs or `docker compose logs zpodengine` if a download stalls or fails.

## Troubleshooting

| Symptom | Likely cause | Action |
| --- | --- | --- |
| 401/403 on download | Missing, invalid, or not-yet-active token | Regenerate token on portal; update setting; wait a few minutes |
| 403 with valid token | Product not entitled for your site | Verify entitlements on Broadcom portal; use `component upload` |
| Wrong file / checksum fail | Library URL out of date | `zcli library resync default`; check zPodLibrary for updated component JSON |
| Non-VMware components (e.g. `zcore`) | Direct HTTPS URL, no token needed | These download without the Broadcom placeholder |

## Manual upload fallback

When depot download is not possible, upload the file directly:

```bash
zcli component upload /path/to/VMware-product.ova
```

zPodFactory matches the file checksum against library metadata and enables the matching component automatically.
