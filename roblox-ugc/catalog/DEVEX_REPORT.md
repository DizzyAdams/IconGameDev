# Roblox UGC - DevEx & Monetization Report (IconMineMods)

## DevEx constants (Roblox official)
- Platform cut on sales: **30%** (creator keeps 70%)
- DevEx rate: **100,000 Robux = US$350**  ->  **1 Robux = US$0.0035**
- Minimum balance to DevEx: **100,000 Robux** (earned, not bought)
- Payout: Hyperwallet, monthly, processor fees apply

## Reverse math to US$ 2,000 / month (net, via DevEx)
```
Target net (DevEx)........: US$ 2,000.00
/ DevEx rate (0.0035).....: 571,429 Robux (creator keeps)
/ 70% (after 30% cut).....: 816,327 Robux (required gross monthly sales)
```

## Catalog (100 items, roblox_catalog.json)
| Type             | Items | Unit (Robux) | Share | Gross Robux/mo | Net Robux/mo | Net US$/mo |
|------------------|-------|--------------|-------|---------------|--------------|------------|
| classic_shirt    | 30    | 70           | 30%   | 244,898       | 171,429      | ~$600      |
| classic_pants    | 20    | 70           | 20%   | 163,265       | 114,286      | ~$400      |
| avatar_accessory | 30    | 150          | 35%   | 285,714       | 200,000      | ~$700      |
| game_pass        | 20    | 250          | 15%   | 122,450       | 85,714       | ~$300      |
| **Total**        | **100** | ~111 blend | 100%  | **816,327**   | **571,429**  | **~$2,000**|

\* Net US$ = net Robux x 0.0035. Shirts/pants are the discovery funnel; accessories + passes are revenue.

## Compliance
- All 100 names are original (no third-party IP).
- Server-authoritative grants (see IconHub kit); no lootboxes/gambling.
- Validated by `python roblox-ugc/tools/roblox_checks.py` -> VERDICT: PASS.
