# PetSanctuary — Roblox UGC Experience Kit

A minimal, server-authoritative shop kit (GamePasses + Developer Products) for Roblox.

## Files
- `ReplicatedStorage/Config/GamePasses.luau` — 20 GamePass definitions (placeholder ids).
- `ReplicatedStorage/Config/DevProducts.luau` — 10 Developer Product definitions (placeholder ids).
- `ServerScriptService/GamePassService.server.luau` — ownership check + purchase prompt (server-authoritative).
- `ServerScriptService/DevProductService.server.luau` — idempotent `ProcessReceipt` handler with a DataStore ledger.
- `ServerScriptService/CozyCosmetics.server.luau` — server-authoritative "dreamscape" cosmetic applier: turns owned GamePasses into original visual effects (trails, auras, wings, halos, pets, capes, banners). Reads the `GamePass_<id>` attributes set by GamePassService; client never decides.
- `StarterPlayer/StarterPlayerScripts/ShopClient.client.luau` — client prompt trigger only.
- `default.project.json` — Rojo v7 project file.

## Import into Roblox Studio

### Option A — Rojo (recommended)
1. Install [Rojo](https://rojo.space/) and the Rojo Studio plugin.
2. Open this folder in a terminal and run `rojo build -o PetSanctuary.rbxlx` then open the file, or `rojo serve` and connect from the plugin.
3. The tree maps to `ReplicatedStorage`, `ServerScriptService`, and `StarterPlayer` automatically. `RemoteEvents/ShopPurchase` is created as a `RemoteEvent`.

### Option B — Paste manually
1. In Studio, create `ReplicatedStorage/Config`, paste the two config ModuleScripts.
2. Create `ReplicatedStorage/RemoteEvents/ShopPurchase` as a `RemoteEvent`.
3. Paste the two `.server.luau` scripts into `ServerScriptService` and the `.client.luau` into `StarterPlayer/StarterPlayerScripts`.

## Set real IDs (required before publishing)
The `id` values in the configs are placeholders (1..20). After uploading the experience:
1. Create each GamePass / Developer Product in the **Roblox Creator Dashboard**.
2. Copy the real IDs into the config tables.

## Compliance notes
- **No third-party IP**: all names are original (trails, auras, coin boosters, etc.).
- **Server-authoritative**: ownership and grants are resolved server-side via `MarketplaceService` and a DataStore ledger; the client never decides anything.
- **Clear benefits, no lootboxes**: every entry states exactly what the player gets; no random rewards, no gambling.
- **DevEx / monetization**: Roblox takes a ~30% platform fee. At current DevEx rates, 100,000 Robux ≈ $350 USD (rate subject to change; see Roblox DevEx terms).
