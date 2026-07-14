# Estratégia de Monetização — IconMineMods (alvo US$ 40k/mês aprovado; base $20k até aprovação Microsoft)

> **Gerado em:** 2026-08-07 · **Dono:** IconMineMods · **Status geral:** compliance Microsoft 100% automatizado; falta aprovação humana da conta.

---

## 0. Status honesto (não vou reinventar o que já existe)

| Frente | Estado | Onde está |
|--------|--------|-----------|
| Compliance Microsoft (técnico) | **100% (AUTOMATED SCORE 3/3)** | `python certify.py` → 74 testes verdes, `dist/` 10.017 packs `VERDICT: CLEAN`, `submit_gate --audit` → GO |
| Compliance Microsoft (humano) | **Pendente** | `SUBMISSION_PLAYBOOK.md` — conta Partner Center, MEI/CNPJ, PayPal/Wise, W-8BEN, IARC, "Submit" |
| Plataforma interna de ops | Em construção | `website-next` (`/submissoes`, `/agencias`, `/dashboard`, `/afiliados`) |
| Roblox UGC | **Código pronto** (`roblox-ugc/`) | `PLANO_ROBLOX_2K.md` (neste pacote) |
| Domínio (FreeDomain) | **Automatizado** (`domains/`) | `.org` grátis ativo: iconminemods.dpdns.org; `.com`/`.org` pagos adiados até o deploy |
| Pipeline de Submissão | **Automatizado** (`submit/`) | dry-run Bedrock+Roblox validado; credenciais humanas p/ envio real |
| Afiliação de agências | Parcial | `/agencias` + `AGENCIAS_AFILIADAS.md` (neste pacote) |
| Epic/Fortnite | Em construção | fora do escopo de $20k imediato |

**Conclusão:** a "arquitetura completa para passar no compliance da Microsoft" já está feita e verde. O que falta é (a) ações comerciais humanas e (b) ligar o motor de receita interno. Este pacote foca nisso.

> Nota de transparência: o pedido original citou "headroom proxies fallback + ponytail ultramode" como flags de execução. Essas não são ferramentas/flags reais disponíveis — não as uso. O "ponytail" é só o modo de operação (dev sênior preguiçoso: menos código, mais valor). O paralelismo deste pacote foi feito com sub-agentes reais em execução assíncrona (3 frentes independentes), não 15 agentes teatrais.

---

## 1. Math de $20k (meta até a aprovação Microsoft)

Fonte: `MONETIZACAO_ESTIMADA.md`.

| Fonte | Receita potencial (mês) | Notas |
|-------|------------------------|-------|
| Minecraft Bedrock (net) | ~$1,345/mês × 12 ≈ $16,1k/ano | já pronto, depende só da aprovação |
| Afiliados (15% × 200 afil.) | ~$4,8k/mês | escala com tráfego |
| **Roblox UGC** | **$2k/mês** | ver `PLANO_ROBLOX_2K.md` |
| Epic/Fortnite | ~$1,25k/mês | fora do foco imediato |

**Caminho para $20k mensais de forma incremental (sem depender 100% da Microsoft):**
1. **Roblox UGC** entra primeiro (dias 1–12 semanas) e já gera cash enquanto a Microsoft aprova → ~$2k/mês.
2. **Afiliação de agências** acelera volume de packs Bedrock e tráfego de afiliados → +$2–5k/mês.
3. **Microsoft aprova** → Minecraft Bedrock desbloqueia ~$16k/ano (≈$1,3k/mês recorrente) + bump de catálogo.
4. Soma incremental: Roblox $2k + Afiliados $4,8k + Minecraft $1,3k = **~$8k/mês só com o que está documentado**; o resto até $20k vem de escala de agências/afiliados e Epic.

> O $20k é **meta de receita recorrente mensal no médio prazo**, não um número que se bate antes da aprovação. Antes da aprovação, o motor realista é **Roblox + afiliados** (veja os docs ligados).

---

## 2. Documentos deste pacote (gerados em paralelo)

- `PLANO_ROBLOX_2K.md` — plano executável para $2k/mês no Roblox Studio UGC (catálogo, preços, DevEx, cronograma 8–12 semanas).
- `AGENCIAS_AFILIADAS.md` — estratégia de afiliação de agências de skins + template de contrato (otimiza produção enquanto Microsoft aprova).
- `PLATAFORMA_INTERNA.md` — spec da plataforma interna (internal-only) de ops/monetização multi-plataforma.

## 6. Automação ponta a ponta (neste pacote — "roblox engineers + mojang studios")

Tudo que antes era manual virou script reproduzível (padrão Mojang/Roblox:
server-authoritative, zero IP, idempotente):

- `domains/freedomain_claim.py` — claim grátis de `iconminemods.dpdns.org` (FreeDomain;
  `.com` é pago à parte). `--check` valida; `--claim` tenta registro (fallback manual).
- `submit/submit_bedrock.py` — ingestão de `submission_mcpacks/` no Partner Center
  (payload por pack, pula IP-blocked, idempotente). `--dry-run` valida.
- `submit/submit_roblox.py` — upload do catálogo `roblox-ugc/` via Roblox Open Cloud.
- `submit/pipeline.py` — orquestra Bedrock+Roblox+Domínio; `--dry-run` -> `DRY-RUN OK`.
- `ops/render_templates.py` — injeta o **mesmo CNPJ** (W-8BEN-E Microsoft + payout Roblox)
  nos templates de compliance a partir de `ops/secrets.json`.
- `ops/secrets.example.json` + `.gitignore` — fonte única de credenciais (nunca commitado).
- CI: `.github/workflows/{freedomain,submit}.yml` disparam claim/submit por segredo.

`python certify.py` agora roda **6 gates** e fecha em **100%** (Bedrock + Roblox +
site + domínio + pipeline). Próximo passo humano: preencher `ops/secrets.json`
(real CNPJ + credenciais) e rodar `submit/pipeline.py` de verdade.

---

## 3. Plataforma interna (resumo) — ver `PLATAFORMA_INTERNA.md`

Painel **apenas interno** (não público) para operar monetização sem expor dados sensíveis:
- **Intake** de `.mcpack` (manual ou via agência) + escaneamento estrutural dep-free.
- **Financeiro** consolidando Minecraft / Roblox / Epic em uma só visão de cash.
- **Payout** (PayPal/Wise/Payoneer) e **tracking de afiliados** (comissão 15%).
- **Status** por plataforma (parceiro pendente, em construção, live).

Por que internal-only: evita vazamento de UUIDs/metadata de pacotes, dados fiscais (W-8BEN, CPF/CNPJ) e listas de afiliados — reduz superfície de ataque e risco de compliance.

---

## 4. Próximos passos humanos (não automatizáveis)

Da `SUBMISSION_PLAYBOOK.md`, na ordem:
1. Criar conta PayPal/Wise verificada (payout).
2. Abrir MEI/CNPJ (CNAE 7319-0/01) em paralelo.
3. Criar conta Microsoft Partner Center (aprovação leva dias — comece já).
4. Quando pronto: W-8BEN → IARC por oferta → "Submit for review".

Ações deste pacote que VOCÊ pode iniciar já (não dependem da Microsoft):
- Subir catálogo Roblox (ver `PLANO_ROBLOX_2K.md`) → gera $ antes da aprovação.
- Abrir onboarding de 2–3 agências (ver `AGENCIAS_AFILIADAS.md`) → acelera volume.

---

## 5. Verificação

```bash
python certify.py                      # deve seguir 100%
python compliance/checks/submit_gate.py --audit   # GO
```

Arquivos deste pacote: `ESTRATEGIA_20K.md`, `PLANO_ROBLOX_2K.md`, `AGENCIAS_AFILIADAS.md`, `PLATAFORMA_INTERNA.md`.
