# Referencia da Plataforma Roblox (PT-BR) — IconMineMods

> Fonte: `create.roblox.com/docs` (acesso 2026-07-09). O PT-BR esta parcial ("este
> conteudo estara disponivel em breve"); as URLs canonicas sao em `/en-us/`. Para
> PT-BR, troque `/en-us/` por `/pt-br/` onde a pagina existir.
> Indice mestre: https://create.roblox.com/docs/llms.txt

---

## 1. Visao da Plataforma
A Roblox oferece (de graca): Roblox Studio (IDE), Engine (3D), Open Cloud (APIs web
fora da experiencia) e Creator Hub (gestao web). Avatares persistem entre jogos:
bodies, clothing, accessories, animations. O Marketplace e `roblox.com/catalog`.
A plataforma cuida de moderacao, localizacao e processamento de pagamento.

## 2. Itens de Avatar (o que publicamos)
- **Classic shirt** (2D, editor de imagem), **rigid accessory** (3D, Blender+Studio),
  **layered clothing** (3D que veste/camada).
- Ferramentas: Blender, Roblox Studio, Accessory Fitting Tool.
- Politicas: Marketplace policy, Intellectual Property, Moderation.
- Docs: `/docs/en-us/avatar.md` · `classic-clothing` · `layered-accessories` ·
  `rigid-accessories` · `character-bodies` · `dynamic-heads`.

## 3. Open Cloud (como nosso `submit_roblox.py` funciona)
- **Base URL:** `https://apis.roblox.com` · **Auth:** header `x-api-key: <key>`
  (var `ROBLOX_API_KEY`). OAuth 2.0 para escopos delegados.
- **API keys:** https://create.roblox.com/dashboard/credentials
  (correcao: NAO e `/develop` — eh `/dashboard/credentials`)
- **Upload de asset:** `POST /assets/v1/assets` (multipart) — nosso script usa isso.
- **Game pass:** `POST /cloud/v2/universes/{id}/user-game-passes`.
- **Erros:** `401` chave invalida · `403` falta escopo · `404` id errado ·
  `429` rate limit (backoff exponencial) · `500` erro Roblox (retry).
- OpenAPI (p/ MCP): https://create.roblox.com/docs/cloud/openapi.json

## 4. Monetizacao de itens de avatar (comissoes oficiais)
| Cenario | Criador | Afiliado | Plataforma |
|---|---|---|---|
| Compra no Marketplace | **30%** | 40% (Roblox) | 30% |
| Compra in-game | **30%** | 40% (dono do jogo) | 30% |
| Revenda de Limited (comunidade) | 10% | 10% | 30% (revendedor 50%) |

- **Limiteds:** taxa por unidade; revenda so por assinantes Roblox Plus; hold de 30 dias.
- Robux de **revenda/trade de item que voce nao criou NAO e Earned** (inelegivel DevEx).
- **Homestore:** sua loja propria => fatia de comissao maior pra voce.
- Docs: `/docs/en-us/monetize-avatar.md` · `marketplace/marketplace-fees-and-commissions`
  · `marketplace/publish-to-marketplace` · `marketplace/homestore`.

> ⚠️ **CORRECAO NO PROJETO:** `generate_catalog.py` e `roblox_checks.py` usam
> `PLATFORM_CUT = 0.70` (criador fica com 70%). O oficial para itens de avatar e
> **30%**. Isso superestima o ganho em ~2,3x. Sugestao: mudar para `0.30`.

## 5. DevEx / Creator Rewards
- **DevEx:** minimo 30.000 Earned Robux; taxa `0,0038`/Robux (padrao), `0,0054` para
  compras de jogadores EUA 18+ verificados; 1 saque/mes. Portal: `create.roblox.com/dashboard/devex`
- **Creator Rewards:** ganho por engajamento de membros Premium (substituiu
  Engagement-Based Payouts em 24/07/2025).
- Docs: `/docs/en-us/production/monetization/developer-exchange.md` · `/docs/en-us/creator-rewards.md`

## 6. Mapa completo de URLs (relevantes)
| Topico | URL |
|---|---|
| Plataforma (hub PT-BR) | /docs/pt-br/platform |
| Criar itens de avatar | /docs/en-us/avatar |
| Roupas classicas (2D) | /docs/en-us/avatar/classic-clothing |
| Layered clothing | /docs/en-us/avatar/layered-accessories |
| Rigid accessories | /docs/en-us/avatar/rigid-accessories |
| Marketplace policy | /docs/en-us/marketplace/marketplace-policy |
| IP / Moderacao | /docs/en-us/marketplace/intellectual-property · /marketplace/moderation |
| Open Cloud (indice) | /docs/cloud/llms.txt |
| Open Cloud (ref) | /docs/en-us/cloud.md |
| Guia de assets | /docs/en-us/cloud/guides/usage-assets |
| Auth API keys | /docs/en-us/cloud/auth/api-keys |
| Game passes (cloud) | /docs/en-us/cloud/api/game-passes |
| Monetizar avatar | /docs/en-us/monetize-avatar |
| Taxas/comissoes | /docs/en-us/marketplace/marketplace-fees-and-commissions |
| Publicar no Marketplace | /docs/en-us/marketplace/publish-to-marketplace |
| Homestore | /docs/en-us/marketplace/homestore |
| DevEx | /docs/en-us/production/monetization/developer-exchange |
| Creator Rewards | /docs/en-us/creator-rewards |
| Indice mestre | /docs/llms.txt |

## 7. Mapeamento para NOSSO pipeline
```
generate_catalog.py  ->  roblox_catalog.json (900 itens)
roblox_checks.py     ->  VERDICT: PASS  (precos, DevEx math, IP/NSFW)
make_dummy_assets.py ->  PNGs em roblox-ugc/assets/ (placeholders p/ teste)
submit_roblox.py     ->  POST /assets/v1/assets (Open Cloud, idempotente)
Creator Hub          ->  set on sale + analytics (create.roblox.com)
DevEx                ->  saque apos 100k Earned Robux
```

## 8. Links rapidos
- API keys: https://create.roblox.com/dashboard/credentials
- Catalog/Marketplace: https://www.roblox.com/catalog
- Creator Hub: https://create.roblox.com/
- DevEx: https://create.roblox.com/dashboard/devex
- Docs (indice): https://create.roblox.com/docs/llms.txt
