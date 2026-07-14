# Cross-Platform Submission Automation

Stdlib + `urllib` only. Minimal, idempotent, safe dry-runs. No `pip` installs.

## What it does

| Script | Target | Source |
|--------|--------|--------|
| `submit/submit_bedrock.py` | Microsoft Partner Center / Microsoft Store (Minecraft Bedrock Marketplace) | `submission_mcpacks/*.mcpack` (one offer per pack) |
| `submit/submit_roblox.py` | Roblox Open Cloud (catalog items + IconHub experience) | `roblox-ugc/catalog/roblox_catalog.json` (100 items) |
| `submit/pipeline.py` | Orchestrates a safe pass: bedrock + roblox + domains claim check | calls the two above + `domains/freedomain_claim.py --check` |

Hard compliance rule: any pack whose filename contains a blocked IP term
(`pokemon, naruto, dragon-ball, bleach, genshin, fnaf, hello-kitty, demon-slayer,
chainsaw-man, one-piece, jujutsu, sonic, tadc, attack-on-titan, little-nightmares,
marvel, minecraft, mojang`) is skipped and the skipped count is printed.

## Environment secrets

### Microsoft (Bedrock / Partner Center)
- `MS_TENANT_ID`        – Azure AD tenant id
- `MS_CLIENT_ID`        – app registration client id
- `MS_CLIENT_SECRET`    – app registration client secret
- `MS_PARTNER_ID`       – Microsoft Partner / publisher id

If any of these are missing, the real run **skips all network calls** (safe no-op).

### Roblox (Open Cloud)
- `ROBLOX_API_KEY`         – Open Cloud API key
- `ROBLOX_GROUP_ID`        – group that owns the assets
- `ROBLOX_EXPERIENCE_ID`   – IconHub universe id (for game passes)

If `ROBLOX_API_KEY` is missing, the real run **skips all uploads**.

### Domains (FreeDomain)
- `DP_EMAIL` / `DP_PASS`   – used by `domains/freedomain_claim.py --claim`
  (the pipeline only runs `--check`, which reads `domains/claimed.json` and exits 0
  when a free domain with status `claimed`/`planned` is present).

## How to run

Dry-run (no network writes; validates config + prints sample payloads; exits 0):

```bash
python submit/pipeline.py --dry-run
# or individually:
python submit/submit_bedrock.py --dry-run
python submit/submit_roblox.py --dry-run
```

Real submission (needs the matching secrets above; idempotent by pack/item name):

```bash
python submit/pipeline.py
# or individually:
python submit/submit_bedrock.py
python submit/submit_roblox.py
```

## Idempotency / state

- `submit/state_bedrock.json` – tracks submitted pack offer names.
- `submit/state_roblox.json`  – tracks uploaded item names.

Re-running skips anything already recorded as `submitted` / `uploaded`.

## TODO (human)

The Microsoft Store and Roblox Open Cloud request endpoints/schemas are best-effort
placeholders. Confirm the exact APIs and update `SUBMIT_URL` / `ASSETS_URL` /
`GAMEPASS_URL` (and the upload-destination handling for binary asset content) before
the first real run.
