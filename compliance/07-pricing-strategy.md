# Pricing Strategy

## 1. Price Tiers (USD/Minecoins)

| Pack Type    | Price (USD) | Minecoins | Strategy |
|-------------|-------------|-----------|----------|
| Skin Packs  | $1.99       | 160       | Low barrier, high volume |
| Texture Packs | $2.99     | 250       | Mid-tier, good value |
| Worlds      | $3.99       | 350       | Premium content |
| Mashups     | $4.99       | 440       | Bundle pricing |

## 2. Revenue Split

- Microsoft takes 30% cut
- Creator receives 70% of sale price
- Minecoin conversion: 160 coins = $0.99 USD

## 3. Projected Revenue (real portfolio)

Portfolio measured from `marketplace-content/` source dirs: 6,294 skin /
1,737 texture / 1,200 world / 458 mashup = **9,689 packs** (8,521 `.mcpack`
already built in `dist/`). Competitive tiers aligned to valid Minecoin steps
(160/310/440/800). Conservative sales assumption = blended <1 sale/pack/month
after a catalog this size matures.

| Category      | Packs | Price | Sales/mo/pack | Gross/mo | Líquido 70% |
|---------------|-------|-------|---------------|----------|-------------|
| Skin Packs    | 6,294 | $1.99 | 0.5           | $6,263   | $4,384      |
| Texture Packs | 1,737 | $2.99 | 0.4           | $2,078   | $1,454      |
| Worlds        | 1,200 | $3.99 | 0.3           | $1,436   | $1,005      |
| Mashups       | 458   | $4.99 | 0.3           | $686     | $480        |

**Total Marketplace líquido: ~$7,323/mo (~$87,882/yr)**

> These are conservative blended rates (<1 sale/pack/mo). The catalog's size is
> the moat: even thin per-pack velocity compounds across ~9.7k SKUs. See
> `09-receita-50k.md` for the cumulative US$ 50k target and go/no-go gate.

## 4. Pricing Psychology

- 1.99 = impulse buy (less than coffee)
- 2.99 = standard content (lunch)
- 3.99 = premium (sandwich)
- Use .99 endings (charm pricing)
- Bundle discount: mashups save 15-20% vs individual

## 5. Launch Strategy

1. First 10 packs: Free/Promotional ($0.00) to build reviews
2. Next 20 packs: Low price ($0.99) to build catalog
3. Full pricing after 50+ packs published
4. Seasonal limited editions at +$1.00 during holidays

## 6. Minecoin Optimization

- Price in Minecoins must map to real-money tiers
- Valid tiers: 160, 310, 440, 800, 1500, 3500, 7000
- Skin packs at 160 coins = $0.99 (no leftover)
- Texture at 250 coins → 310 tier (must round up)
- Worlds at 350 coins → 440 tier (round up)
- Mashups at 440 coins = $2.99 (exact match)

## 7. Brazilian Market Pricing

- Convert: $1 USD ≈ R$5.00 BRL
- Skin packs: R$4.99 - R$9.99
- Texture packs: R$9.99 - R$14.99
- Worlds: R$14.99 - R$19.99
- Mashups: R$19.99 - R$24.99
- Note: Microsoft sets BRL price based on USD tier

## 8. US$ 50k Revenue Target

Goal: cumulative **US$ 50,000** in creator payouts (see `09-receita-50k.md`).

- At the conservative líquido run-rate above (~$7,323/mo) the target is hit in
  **~6.8 months**.
- The bottleneck is **not** demand or price — it is **submission throughput +
  the compliance gate**. Volume is already sufficient (9,689 packs).
- Sensitivity: at 0.3 sales/pack/mo blended the run-rate is ~$4,394/mo (target
  in ~11.4 months); at 1.0 sale/pack/mo it is hit in ~3.4 months.
- Pricing is already competitive (charm .99 endings, valid Minecoin tiers
  160/310/440/800). Raising prices risks rejection and lower conversion — keep
  tiers as-is. Do not use "temporary discount" language on new submissions.
