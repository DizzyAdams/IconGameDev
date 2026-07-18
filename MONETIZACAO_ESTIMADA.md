# Monetizacao Estimada — IconMineMods Multi-Platform

## Minecraft Bedrock (9,985 packs)

| Tier | Preco | Packs | Receita Potencial (100% sell-through) |
|------|-------|-------|---------------------------------------|
| Economy | $0.99 | ~3,000 | $2,970 |
| Standard | $1.99 | ~5,000 | $9,950 |
| Premium | $2.99-$4.99 | ~1,500 | $5,985 |
| Deluxe | $6.99-$9.99 | ~485 | $4,120 |
| **Total** | | **9,985** | **~$23,025** |

*Microsoft 30% cut: ~$6,907 → net ~$16,117*

## Programa de Afiliados

| Comissao | Afiliados | Receita/mes (projecao) |
|----------|-----------|------------------------|
| 15% | 50 | $1,200 |
| 15% | 200 | $4,800 |
| 15% | 500 | $12,000 |

## Roblox UGC (em construcao)
- Target: 100 items @ $0.50-$2.00 avg
- Receita potencial: $5,000-$20,000/mes
- Roblox 30% cut

## Epic Games / Fortnite Creative (em construcao)
- Target: 1000 maps @ $2.99-$9.99
- Receita potencial: ~$324 por mapa (50 vendas médias por mapa/ano)
- Epic 12% cut

## Total Estimado (12 meses)
- Minecraft: $193,404/ano (net)
- Afiliados: $57,600/ano (50 afiliados)
- Roblox: $42,000/ano (estimativa conservadora)
- Epic: $285,322/ano (net, baseada em 1000 mapas)
- **Total: ~$578,326/ano**

## Meta Operacional: US$ 80k/mês (cenário escalado, aprovado com 1000 mapas Epic)

Para bater ~US$ 80k/mês recorrente após aprovação, o motor já construído
(`marketplace-content/` + `roblox-ugc/` + `submit/`) escala por volume:

| Frente | Alvo/mês | Como escala (automatizado) |
|--------|----------|----------------------------|
| Minecraft Bedrock | ~US$ 8k | +tiers Premium/Deluxe, mais packs (motor já gera 10k+), bundles |
| Roblox UGC | ~US$ 10k | 100→500 itens (gerador paramétrico) + 2→5 experiences + passes |
| Afiliados (15%) | ~US$ 12k | 50→500 afiliados (ops/agencias pronto) |
| Epic/Fortnite | ~US$ 50k | 200→1000 maps (catálogo escalado para 1000 mapas) |
| **Total** | **~US$ 80k/mês** | pipeline `submit/pipeline.py` envia os 4 canais |

Teto limitante = aprovação Microsoft (Bedrock) + conta Roblox DevEx + volume de
tráfego/afiliados. Tudo enviável via `submit/pipeline.py --dry-run` (validado)
e `submit/pipeline.py` (real, com credenciais em `ops/secrets.json`).
