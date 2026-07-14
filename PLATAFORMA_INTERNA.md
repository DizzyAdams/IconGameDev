# Plataforma Interna (internal-only) — IconMineMods

>Painel operacional **NÃO exposto ao público** para gestão de monetização multi-plataforma
>(Minecraft, Roblox, Epic). Contexto: `README.md` (rotas /submissoes, /agencias, /dashboard, /afiliados).

---

## 1. Princípio: apenas interno

- Nada de dados fiscais (W-8BEN, CPF/CNPJ), listas de afiliados ou UUIDs de packs expostos.
- Acesso por allowlist/IP interno + auth (não público).
- Reduz superfície de ataque e risco de compliance (vazamento de IP, dados pessoais).

---

## 2. Módulos

| Módulo | Rota | Função |
|--------|------|--------|
| Intake | `/submissoes` | Recebe `.mcpack` (manual ou agência), escaneia, filtra por status |
| Análise | `/submissoes/[id]` | Validação estrutural dep-free (ZIP, manifest, UUID, PNG) + aprovar/rejeitar/promover |
| Agências | `/agencias` | Cadastro, fast-track, submissões vinculadas |
| Financeiro | `/dashboard` | Visão consolidada de cash por plataforma |
| Afiliados | `/afiliados` | Tracking de comissão 15%, pagamentos |
| Status | — | Minecraft (parceiro pendente) / Roblox (código pronto) / Epic (construindo) |

---

## 3. Modelo de dados mínimo

```
Submission(id, filename, source, status[scan|review|approved|rejected],
           analysis{zip_ok, manifest_ok, uuid_unique, png_dims}, created_at)

Agency(id, name, status[active|paused], fast_track:bool,
       commission_pct, packs_delivered, revenue_share)

Affiliate(id, handle, tier, commission_pct=15, referrals, paid_to_date)

Revenue(platform[minecraft|roblox|epic], gross_usd, platform_cut,
        net_usd, period_month)

Payout(id, method[paypal|wise|payoneer], amount_usd, status, paid_at)
```

---

## 4. Integração com o objetivo de $20k

- O módulo **Financeiro** é a única fonte de verdade de cash: soma Minecraft + Roblox + Epic + Afiliados.
- **Intake + Agências** alimentam o volume de Minecraft (pronto na aprovação Microsoft).
- **Roblox** entra como linha própria assim que os itens do `PLANO_ROBLOX_2K.md` forem publicados.
- **Afiliados** mostra a comissão 15% que