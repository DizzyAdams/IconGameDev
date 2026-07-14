# Afiliação de Agências de Skins — IconMineMods

>Estratégia para acelerar produção e receita **enquanto a aprovação Microsoft (Partner Center) está pendente**.
>Contexto: `README.md` (seção "Agências de Skins Bedrock", rota `/agencias`).

---

## 1. Por que afiliar agências agora

A aprovação Microsoft leva dias/semanas, mas a produção de packs não precisa parar.
Agências especializadas (PixelCraft, BlockSkin) já entregam packs no padrão Marketplace
Bedrock → entram no `dist/` assim que a conta é aprovada, e já geram tráfego de afiliados
hoje. Isso encurta o tempo até a meta de $20k.

---

## 2. Perfil da agência ideal

- Produz **skins/texture/world packs** dentro do padrão oficial Bedrock (manifest válido, UUIDs únicos).
- Entrega em lote (.mcpack) prontos para `submission_mcpacks/` ou via API `/api/submissions`.
- Tem portfólio e capacidade de 50–200 packs/mês.
- Aceita revenue share (não pagamento fixo upfront).

Exemplos alvo: **PixelCraft**, **BlockSkin** (já citados no README).

---

## 3. Modelo de receita compartilhada

| Modelo | Comissão agência | IconMineMods retém |
|--------|------------------|--------------------|
| Revenue share padrão | 30% da receita do pack | 70% (menos 30% Microsoft) |
| Fast-track (volume) | 25% (desconto por volume) | 75% |
| Apenas produção (sem marca) | taxa por pack (ex. R$ 5–15) | 100% da receita |

Recomendado para começar: **revenue share 30%**, descendo para 25% acima de 150 packs/mês.

---

## 4. Fluxo de onboarding + fast-track

1. Agência se cadastra em `/agencias` (POST `/api/agencies`).
2. Recebe **briefing de padrão** (manifest, UUIDs, dimensões PNG 64x64 / 256x256).
3. Deposita packs em `submission_mcpacks/` ou via `POST /api/submissions`.
4. "Escanear inbox" → análise estrutural dep-free (ZIP, manifest, UUIDs, PNG).
5. Reviewer aprova/rejeita → aprovado vira `PROMOTE` para `dist/`.
6. Com **fast_track=on**: prioridade na fila + análise automática + recebimento acelerado.
7. Na aprovação Microsoft: packs da agência já estão no `dist/` prontos para "Submit".

---

## 5. Minuta de contrato (template)

```markdown
# Termo de Parceria — Agência de Skins IconMineMods

**Partes:** IconMineMods (CONTRATANTE) e [NOME DA AGÊNCIA] (PARCEIRA).

1. OBJETO: produção de pacotes .mcpack (skins/texturas/mundos) conforme padrão
   Marketplace Minecraft Bedrock oficial.
2. PADRÃO: manifest.json válido, UUIDs v4 únicos, PNG 64x64 (skins) / 256x256 (ícone),
   zero IP de terceiros.
3. REMUNERAÇÃO: revenue share de [30%]/[25%] sobre a receita líquida do pack, após
   retenção de 30% da Microsoft. Pagamento via PayPal/Wise até o dia 15 do mês seguinte.
4. FAST-TRACK: pacotes aprovados entram com prioridade no pipeline de submissão.
5. PROPRIEDADE: IconMineMods detém a conta de venda (Partner Center); agência detém
   os assets originais entregues.
6. COMPLIANCE: agência responsável por originalidade e ausência de IP infrator.
7. VIGÊNCIA: 12 meses, renovável.
```

---

## 6. Como isso otimiza o caminho para $20k

- **Volume:** +150–300 packs/mês de agências eleva o teto de catálogo Minecraft sem
  contratar headcount interno.
- **Tráfego:** agências trazem seus próprios canais → mais afiliados (comissão 15%) ativos.
- **Speed-to-approval:** quando a Microsoft aprova, o `dist/` já está cheio e pronto para
  submissão em lote → receita Minecraft desbloqueia dias depois, não semanas.
- Soma incremental com Roblox ($2k) + afiliados ($4,8k) + Minecraft net ($1,3k) ≈ $8k/mês
  documentado; agências empurram o resto até $20k.
