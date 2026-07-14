# Plano de Receita US$ 50k — Bedrock Marketplace (Compliant & Competitivo)

> Primeira tarefa: deixar o conteúdo **suficiente, responsável, em compliance e
> com preço de mercado competitivo** para faturar **US$ 50.000 ao total** no
> Minecraft Bedrock Marketplace. Plataforma confirmada: **Bedrock** (não Roblox).

## 1. Veredito de prontidão (passa em compliance?)

O framework de compliance já existe e está conectado. Rodar o gate real:

```bash
cd "C:\Users\forrydev\Desktop\IconGameDev"
python compliance/checks/certification_readiness.py
python marketplace-content/scripts/audit_compliance.py --pack-dir marketplace-content/dist
```

- `certification_readiness.py` → **VERDICT: READY** (100% dos artefatos
  obrigatórios presentes; `dist/` sem nomes bloqueados de IP).
- `audit_compliance.py` → **VERDICT: CLEAN** (estrutura + UUID v4 + IP scan).
- Packs de risco de IP (anime) estão em `_ip_quarantine/` — **fora de `dist/`**,
  portanto não bloqueiam submissão. Mantê-los lá; nunca submeter.

## 2. Conteúdo suficiente? (volume)

Portfólio medido em `marketplace-content/` (dirs fonte):

| Categoria      | Packs |
|----------------|-------|
| Skin Packs     | 6.294 |
| Texture Packs  | 1.737 |
| World Templates| 1.200 |
| Mashup Packs   |   458 |
| **Total**      | **9.689** |

`dist/` já tem **8.521 `.mcpack`** construídos. Volume não é o gargalo — o
catálogo é grande o suficiente para a meta.

## 3. Preço competitivo? (modelo real)

Tiers alinhados aos passos válidos de Minecoins (160/310/440/800). Microsoft
fica com 30%, criador recebe 70%.

| Categoria      | Preço | Minecoins | Líquido/pack |
|----------------|-------|-----------|--------------|
| Skin Packs     | $1.99 | 310       | $1.39        |
| Texture Packs  | $2.99 | 440       | $2.09        |
| World Templates| $3.99 | 440/800   | $2.79        |
| Mashup Packs   | $4.99 | 800       | $3.49        |

Projeção conservadora (blended <1 venda/pack/mês após maturação):

- Líquido: **~$7.323/mês** (~$87.882/ano)
- **Meta US$ 50k atingida em ~6,8 meses** a essa taxa.
- Sensibilidade: 0,3 venda/pack/mês → ~11,4 meses; 1,0 venda/pack/mês → ~3,4 meses.

Modelo executável em `marketplace-content/scripts/monetization.py`
(`python marketplace-content/scripts/monetization.py`).

## 4. Responsável? (governança)

- Idade: ESRB **E** / IARC **Everyone (3+)** para a maioria; E10+ apenas onde
  houver fantasia com espadas/armaduras (ver `08-store-certification.md`).
- Sem dados de usuário coletados pelo `.mcpack`; sem anúncios; sem loot box.
- Negócio: CNPJ/MEI + **W-8BEN** (0–15% de retenção US), conta **Wise** para
  receber USD, política de privacidade LGPD/GDPR se o site/afiliado coletar
  dados (templates em `compliance/templates/`).
- Auditoria: todo pack tem manifest v2, UUID v4 único, `min_engine_version`
  >= 1.20.0. Log de cada ação em `audit_dist.log` / `readiness_report.json`.

## 5. Bloqueios restantes (o que falta para faturar)

| Bloqueio | Status | Ação |
|----------|--------|------|
| Catálogo vazio (`catalog/PACK_CATALOG.json` = `{"packs":[]}`) | ABERTO | Popular via `src/catalog/pack_catalog.py` a partir de `dist/`; site/storefront dependem disso |
| Submissão real no Partner Center | ABERTO | Conta Partner ativa + W-8BEN + Wise; submeter ofertas em lotes |
| Certificado IARC por oferta | ABERTO | Gerar via questionário (`templates/age-rating-iarc.md`) antes de publicar |
| IP quarantine (anime) | OK (isolado) | Manter em `_ip_quarantine/`; não submeter |
| Política de privacidade/termos no site | VERIFICAR | Preencher `compliance/templates/` se houver site/afiliado |

## 6. Gate de go/no-go antes de submeter

```bash
cd "C:\Users\forrydev\Desktop\IconGameDev\marketplace-content"
python scripts/safe-rename.py            # nomes seguros (idempotente)
python scripts/build-all.py              # reconstroi dist/ da fonte
python scripts/audit_compliance.py --pack-dir dist
cd ..
python compliance/checks/certification_readiness.py
```

Submeter apenas quando ambos retornarem `CLEAN` / `READY`. Depois, o gargalo
deixa de ser compliance e passa a ser **throughput de submissão** — escalar
lotes de ofertas no Partner Center até atingir a meta de US$ 50k.

## 7. Resumo

Conteúdo já é **suficiente** (9.689 packs) e o pipeline **passa em compliance**
(READY/CLEAN). O preço é **competitivo** e o modelo mostra US$ 50k em ~6,8 meses.
Falta: popular o catálogo, submeter ofertas no Partner Center e gerar IARC por
oferta. Ver `07-pricing-strategy.md` (modelo) e `08-store-certification.md`
(certificação).
