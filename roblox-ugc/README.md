# IconMineMods - Roblox UGC Platform Piece

This folder is the **Roblox** half of the unified $20k/month monetization platform
(the other half is the Minecraft Bedrock Marketplace engine in `marketplace-content/`).

## What's here
- `experiences/IconHub/` - a functional, compliant Roblox Studio kit (LuaU):
  - Game-pass ownership check + purchase prompt (server-authoritative)
  - Developer-product `ProcessReceipt` with an idempotent DataStore ledger
  - Original catalog (no IP / NSFW / lootboxes)
  - Rojo `default.project.json` + import README
- `tools/generate_catalog.py` - idempotent generator of the 100-item catalog
- `catalog/roblox_catalog.json` - 100 items (30 shirts / 20 pants / 30 accessories / 20 passes)
- `catalog/DEVEX_REPORT.md` - DevEx math to US$2,000/mo
- `tools/roblox_checks.py` - compliance validator (IP / NSFW / price / DevEx math)

## Run the gates
```
python roblox-ugc/tools/generate_catalog.py --check
python roblox-ugc/tools/roblox_checks.py
```
Both are also wired into the unified `certify.py` (gate 4/4).

## Path to cash (before Microsoft approval)
Roblox pays out on published UGC immediately; it is the first live revenue line.
Follow `PLANO_ROBLOX_2K.md`, then register items in the internal platform
(`PLATAFORMA_INTERNA.md`) alongside Minecraft + affiliates.
