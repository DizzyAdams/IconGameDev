# Plano $100k/mês — 14 Agentes · Bedrock Skins Marketplace

```yaml
meta: iconminemods.dpdns.org
target: $100k/mês recorrente (net)
timeframe: 90d (Q3-Q4 2026)
base_actual: ~$8.3k/mês (progress.md 2026-09-07)
multiplier: 12x
principio: yagni + maximum reuse + parallel dispatch
```

## Math $100k (como chegar)

| Fonte | Atual | Target $100k | Multiplicador |
|-------|-------|-------------|---------------|
| Bedrock skins | $1.3k/mês | $35k | 10k→100k packs + premium tiers |
| Roblox UGC | $2k/mês | $20k | 100→2k itens + accessories |
| Afiliados/Agências | $4.8k/mês | $25k | 200→1k afiliados |
| Epic/Fortnite | $1.1k/mês | $20k | 200→1000 maps |
| Bundles cross-plataforma | $0 | $10k | novo canal |

**Breakpoint:** 2.5M downloads/mês @ $0.04 avg net/skin = $100k

## 14 Agentes (Workstreams)

### Batch 1 — Content Engine (3 agentes, ARQUIVOS DIFERENTES)
| # | Agente | Arquivos | Output | Status |
|---|--------|----------|--------|--------|
| A1 | mass-skin-100k | marketplace-content/output/mass-skins-100k/ | 100k packs, 8 skins cada, 7 tiers ($0.99-$9.99) | 🔄 test batch 500 |
| A2 | premium-themes | marketplace-content/output/skin-packs/ | 50 themed collections @ $4.99-$9.99 | 🔄 rodando |
| A3 | texture-packs | texture-packs/ | 500 texture packs @ $1.99-$5.99 | 🔄 rodando |

### Batch 2 — Storefront & SEO (3 agentes, ARQUIVOS DIFERENTES) [aguarda B1]
| # | Agente | Arquivos | Output |
|---|--------|----------|--------|
| A4 | high-end-redesign | website-next/src/ | redesign seguindo Padrão 5 (Geist, bento, dark premium) |
| A5 | seo-content | website-next/ | 200 SEO pages, blog, schema, sitemap |
| A6 | pwa-affiliate | website-next/public/ | PWA push, affiliate dashboard, tracking links |

### Batch 3 — Roblox & Epic Scale (3 agentes, ARQUIVOS DIFERENTES) [aguarda B2]
| # | Agente | Arquivos | Output |
|---|--------|----------|--------|
| A7 | roblox-scale | roblox-ugc/ | 100→2000 items, 10 experiences, premium passes |
| A8 | epic-scale | epic/ | 200→1000 maps, bundles, cross-promo |
| A9 | cross-platform-bundles | submit/ | bundle offers (Bedrock+Roblox+Epic), discount engine |

### Batch 4 — Monetization & Ops (3 agentes, ARQUIVOS DIFERENTES) [aguarda B2]
| # | Agente | Arquivos | Output |
|---|--------|----------|--------|
| A10 | pricing-optimizer | compliance/ | dynamic pricing per tier, A/B test framework, analytics |
| A11 | affiliate-engine | affiliates/ | auto-payout, referral tracking, 3-tier commission system |
| A12 | ops-automation | ops/ | payout automation, finance dashboard, tax reports |

### Batch 5 — Submission & Growth (2 agentes) [aguarda B3+B4]
| # | Agente | Arquivos | Output |
|---|--------|----------|--------|
| A13 | submission-pipeline | submit/ | CI/CD full auto-submit, 100k packs, all platforms |
| A14 | community-growth | website-next/ | Discord bot, Twitter/X scheduler, social proof system |

## Orquestração (Sequência Real)

```
B1 ──→ content ready ──→ B2 (storefront pega o conteúdo)
                           │
                           ├─→ B3 (cross-platform depois da storefront)
                           │
                           └─→ B4 (pricing/ops roda em paralelo com B3)
                                │
                                └─→ B5 (submission só após pricing + content)
```

## Status Gates

- [ ] Batch 1 (A1-A3): dispatched (A1 test batch, A2+A3 running)
- [ ] Batch 1 full: 100k cron job setup
- [ ] Batch 2 (A4-A6): aguarda B1
- [ ] Batch 3 (A7-A9): aguarda B2
- [ ] Batch 4 (A10-A12): aguarda B2
- [ ] Batch 5 (A13-A14): aguarda B4
- [ ] Integração + Build + Deploy
- [ ] Revenue tracking ativo

## Verificação Final

```bash
python certify.py  # 100%
python compliance/checks/submit_gate.py --audit  # GO
npm run build  # website-next
git add . && git commit -m "feat: 100k pipeline"
npx vercel deploy --prod --yes
```
