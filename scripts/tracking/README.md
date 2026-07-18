# IconMineMods — Affiliate Tracking Pipeline
# -----------------------------------------
# Sistema automatizado de tracking de afiliados, comissões e geração de páginas de destino.

## 📁 Estrutura

```
website-next/
├── src/
│   ├── app/
│   │   ├── afiliados/                    # Painel de gerenciamento (já existente)
│   │   │   ├── page.tsx                  #   Lista de afiliados
│   │   │   └── [id]/page.tsx             #   Detalhe do afiliado
│   │   ├── afiliados/landing/[code]/page.tsx  # Página de destino do afiliado (NOVO)
│   │   └── api/
│   │       ├── affiliates/route.ts       # CRUD de afiliados (já existente)
│   │       ├── affiliates/[id]/route.ts  # Detalhe do afiliado (já existente)
│   │       ├── affiliates/track/route.ts         # Click tracking (NOVO)
│   │       ├── affiliates/track/convert/route.ts # Conversion tracking (NOVO)
│   │       └── affiliates/landing/[code]/route.ts # API da landing page (NOVO)
│   └── data/
│       └── affiliates.json               # Base de dados JSON
├── public/
│   └── afiliados/                        # Landing pages estáticas (geradas por script)
└── scripts/
    └── tracking/
        ├── __init__.py
        ├── commission_calculator.py      # Calculadora de comissões
        ├── landing_page_generator.py     # Gerador de landing pages estáticas
        ├── report_generator.py           # Relatórios CSV/JSON
        └── README.md                     # Este arquivo
```

## 🔗 Sistema de Tracking

### 1. Click Tracking
Os afiliados compartilham links no formato:
```
https://iconminemods.com/?ref=IMM_NOME_XXX
```

Quando um usuário clica:
1. O cookie `imm_ref` é definido (30 dias de atribuição)
2. O contador de cliques do link é incrementado
3. O evento é registrado no log de tracking
4. O usuário é redirecionado para a página de destino

**Uso programático (AJAX):**
```javascript
fetch('/api/affiliates/track', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ref: 'IMM_NOME_XXX' })
});
```

### 2. Conversion Tracking
Quando uma venda é concluída, chame o endpoint de conversão:

**POST /api/affiliates/track/convert**
```json
{
  "ref": "IMM_NOME_XXX",
  "sale_id": "sale_abc123",
  "amount": 9.99,
  "product": "Skin Pack — Guerreiros Lendários",
  "platform": "minecraft_bedrock"
}
```

**Tracking Pixel (GET):**
```html
<img src="https://iconminemods.com/api/affiliates/track/convert?ref=IMM_NOME_XXX&sale_id=abc123&amount=9.99" width="1" height="1" />
```

### 3. Landing Pages Dinâmicas
Cada afiliado tem uma página pública automática:
```
https://iconminemods.com/afiliados/landing/IMM_NOME_XXX
```
Mostra: nome, estatísticas, catálogo de packs, link de afiliado.

### 4. Landing Pages Estáticas (geradas por script)
```
python scripts/tracking/landing_page_generator.py
```
Gera páginas HTML estáticas em `website-next/public/afiliados/` para SEO.

## 📊 Scripts de Automação

### commission_calculator.py
```bash
# Relatório completo de comissões
python scripts/tracking/commission_calculator.py

# Marcar pendentes como pagos
python scripts/tracking/commission_calculator.py --pay-pending

# Relatório resumido
python scripts/tracking/commission_calculator.py --report
```

### landing_page_generator.py
```bash
# Gerar landing pages para TODOS os afiliados
python scripts/tracking/landing_page_generator.py

# Gerar landing page para UM afiliado específico
python scripts/tracking/landing_page_generator.py --affiliate-id aff_xxx
```

### report_generator.py
```bash
# Relatório completo (stdout)
python scripts/tracking/report_generator.py

# Exportar CSV
python scripts/tracking/report_generator.py --csv

# Exportar JSON (para dashboards)
python scripts/tracking/report_generator.py --json

# Filtrar por período
python scripts/tracking/report_generator.py --csv --period=2026-07
```

## 🔄 Fluxo Completo

```
1. Afiliado se cadastra → POST /api/affiliates → link gerado automaticamente
2. Afiliado compartilha link → https://iconminemods.com/?ref=IMM_NOME_XXX
3. Usuário clica → GET /api/affiliates/track?ref=IMM_NOME_XXX
   → Cookie setado + clique contado + redirect
4. Usuário compra → POST /api/affiliates/track/convert
   → Comissão calculada (rate%) + registro com status "pending"
5. Mensalmente → commission_calculator.py --report
6. Pagamento → commission_calculator.py --pay-pending
7. Landing pages → landing_page_generator.py
```

## 💰 Modelo de Comissão

| Tipo | Comissão | Descrição |
|------|----------|-----------|
| Padrão | 15% | Comissão base para afiliados |
| Premium | 20-30% | Afiliados com alto volume |
| Agências | 25-30% | Revenue share com agências de skins |

A comissão é calculada automaticamente no momento da conversão:
`commission = sale_amount * (commission_rate / 100)`
