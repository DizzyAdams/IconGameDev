# Roblox como Pessoa Física (sem CNAE) — receita antes da Microsoft

> **Resposta curta:** Sim. A Roblox aceita **pessoa física** para criar, vender
> UGC e sacar via DevEx. **CNAE e CNPJ NÃO são exigidos**. Funciona mesmo com o
> CNAE do CNPJ "errado", pois no Roblox você opera como **indivíduo (CPF)**.
>
> **Aviso de realidade:** "receber hoje" não é possível. Precisa de (a) conta
> Roblox pronta, (b) itens publicados, (c) vendas reais, e (d) **100.000 Robux
> ganhos** antes do 1º saque DevEx. Leva semanas. Nenhum agente antecipa isso.

---

## 1. Por que Roblox não precisa de CNAE/CNPJ

- Roblox paga o **criador individual** (CPF como TIN no W-8BEN), não CNPJ.
- Formulário fiscal = **W-8BEN** (PF), **não W-8BEN-E** (PJ, que é o do
  `ops/secrets.example.json` — esse é para a **Microsoft**).
- CNAE é de CNPJ/MEI. Como PF no Roblox, você não declara CNAE nenhum.

> CNAE só importa para **Microsoft / Minecraft Marketplace** (exige empresa).
> Para criação de jogos, `7319-0/01` é válido; alt `6201-5/01`. Confirme com
> contador — não altero inscrição na Receita. Não bloqueia o Roblox.

---

## 2. Requisitos de conta Roblox (pessoa física)

1. Conta Roblox + e-mail confirmado.
2. **Verificação de idade** (doc) e **2FA** — obrigatórios p/ DevEx.
3. **Roblox Premium ativo** — historicamente exigido p/ DevEx (confirme na aba).
4. **Grupo** IconMineMods (opcional; centraliza payout e API).
5. **DevEx habilitado**: Robux precisam ser **ganhos em venda**, não comprados.
6. Perfil fiscal: **W-8BEN**, TIN = seu **CPF**, residência fiscal Brasil.

> Em `PLANO_ROBLOX_2K.md` (seção 4) cita "CNPJ/CPF como TIN". PF usa **só CPF**.

---

## 3. Ciclo de pagamento (por que não é hoje)

| Etapa | O que é | Tempo real |
|-------|---------|------------|
| Publicar itens | `submit/submit_roblox.py` | horas/dias (você) |
| Acumular vendas | compradores pagam Robux | semanas |
| **Mínimo DevEx** | **100.000 Robux ganhos** (≈ US$ 350) | semanas |
| Solicitar saque | portal DevEx → processador | dias úteis |
| Receber | PayPal/banco | dias úteis |

- Taxa DevEx estável: **100.000 Robux = US$ 350** (1 Robux = US$ 0,0035).
  **Confirme mínimo/taxa DENTRO do portal DevEx** — a Roblox muda.
- Corte da plataforma: **30%** sobre venda (você retém 70%).
- Payout via processador do Roblox (Hyperwallet) → PayPal/banco. Não é mesmo dia.

---

## 4. O que JÁ está pronto (e o que falta de verdade)

**Pronto e validado:**
- `roblox-ugc/catalog/roblox_catalog.json` — 100 itens, preços/DevEx consistentes.
- `roblox-ugc/tools/roblox_checks.py` → `VERDICT: PASS`.
- `roblox-ugc/experiences/IconHub/` — kit LuaU (game passes + dev products,
  server-authoritative, sem IP/NSFW/lootbox).
- `submit/submit_roblox.py --dry-run` → 100 itens, payloads OK, sem rede.
- `certify.py` → `roblox_catalog_compliant` = PASS (gate 4/6).

**Falta para publicar de verdade (buracos reais):**
1. **PNGs dos itens.** Camisas/calças/acessórios Roblox exigem o **PNG do asset**
   (template de roupa 585x559). O catálogo tem só metadados. Sem PNGs, o upload
   real não publica a roupa. A API de assets usa two-step: `POST /assets/v1/assets`
   → URL de upload → `PUT` do binário (ajustar `submit_roblox.py`).
2. **Credenciais reais** em `ops/secrets.json`: `roblox.api_key`, `group_id`,
   `experience_id`. Crie a API key no Creator Hub (Open Cloud).
3. **Publicar a experience IconHub** no Roblox Studio (game passes dependem do
   `universeId`).
4. **W-8BEN + CPF** no perfil fiscal do Roblox.
5. **DevEx habilitado** + acúmulo de 100k Robux em vendas antes do 1º saque.

---

## 5. Como rodar (com as credenciais)

```bash
cp ops/secrets.example.json ops/secrets.json   # NUNCA comite secrets.json
$env:ROBLOX_API_KEY="<Open Cloud API key>"
$env:ROBLOX_GROUP_ID="<id do grupo>"
$env:ROBLOX_EXPERIENCE_ID="<universe id>"
python submit/submit_roblox.py --dry-run       # valida sem rede
python submit/submit_roblox.py                 # upload real (idempotente)
```

> `submit_roblox.py` é *best-effort* na chamada real (ver `TODO` no topo). O
> game pass (experience) é o mais próximo de publicável hoje, dependendo só do
> `experience_id`; roupas precisam dos PNGs (item 1).

---

## 6. Resumo para o dono

- **Monetiza no Roblox como PF hoje?** Sim — conta, W-8BEN+CPF, publique. Sem CNAE.
- **Recebe hoje?** Não. Vendas reais + 100k Robux antes do 1º saque.
- **CNAE "errado" atrapalha?** Só na Microsoft. No Roblox, irrelevante.
- **Próximo passo:** gerar PNGs dos itens + preencher `ops/secrets.json` +
  habilitar DevEx. Aí `submit_roblox.py` publica de verdade.
