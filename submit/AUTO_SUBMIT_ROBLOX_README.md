# Auto-Submissão Roblox UGC — Pipeline de Batch Upload

## Visão Geral

`auto_submit_roblox.py` é a pipeline automatizada de submissão de itens UGC
da IconMineMods para o Roblox Marketplace. Ela escaneia diretórios de imagens
PNG, faz match com o catálogo (`roblox_catalog.json`) e faz upload via
**Roblox Open Cloud API** (Assets API v1).

---

## Fluxo

```
                      ┌──────────────────┐
                      │ roblox_catalog.json│
                      │ (900+ items)      │
                      └────────┬─────────┘
                               │
roblox-ugc/items/*.png ────────┤
roblox-ugc/assets/*.png ───────┤
                               ▼
                    ┌─────────────────────┐
                    │ auto_submit_roblox.py │
                    │                     │
                    │ 1. Load catalog     │
                    │ 2. Scan PNGs        │
                    │ 3. Match by name    │
                    │ 4. Filter state     │
                    │ 5. Upload batch     │
                    │ 6. Save report      │
                    └─────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Roblox Assets API v1 │
                    │ apis.roblox.com      │
                    └──────────────────────┘
```

---

## Modos de Execução

| Comando | Efeito |
|---------|--------|
| `python auto_submit_roblox.py --dry-run` | Valida catálogo + imagens, **sem enviar** |
| `python auto_submit_roblox.py --test-one` | Envia **1 item** e para (teste seguro) |
| `python auto_submit_roblox.py` | Upload batch completo (idempotente) |
| `python auto_submit_roblox.py --force` | Re-envia itens já marcados como enviados |
| `python auto_submit_roblox.py --unmatched-only` | Só processa PNGs **sem** match no catálogo |
| `python auto_submit_roblox.py --items-dir ../outros_pngs` | Diretório customizado |

---

## Credenciais

A pipeline carrega credenciais na seguinte ordem de prioridade:

1. **Variáveis de ambiente**: `ROBLOX_API_KEY`, `ROBLOX_GROUP_ID`, `ROBLOX_EXPERIENCE_ID`
2. **Arquivo `.env`** na raiz do projeto
3. **`ops/secrets.json`** → `{"roblox": {"api_key": "...", "group_id": "...", "experience_id": "..."}}`

### Onde obter:

| Variável | Onde encontrar |
|----------|---------------|
| `ROBLOX_API_KEY` | [Roblox Creator Hub → Open Cloud → API Keys](https://create.roblox.com/dashboard/credentials) |
| `ROBLOX_GROUP_ID` | Dashboard do grupo → URL `/groups/<GROUP_ID>/` |
| `ROBLOX_EXPERIENCE_ID` | Creator Hub → Experience → Configurações → Universe ID (para game passes) |

---

## Estrutura de Diretórios

```
IconGameDev/
├── roblox-ugc/
│   ├── assets/           # PNGs dos itens (fallback)
│   │   ├── Crimson Shirt.png
│   │   ├── Crimson Shirt Neon.png
│   │   ├── Crimson Wings Accessory Frost.png
│   │   └── ...
│   ├── items/            # Diretório preferencial para PNGs
│   ├── catalog/
│   │   └── roblox_catalog.json   # 900+ itens catalogados
│   └── tools/
│       ├── generate_catalog.py   # Gera catálogo
│       └── roblox_checks.py      # Valida catálogo
└── submit/
    ├── submit_roblox.py           # Uploader original (manual)
    ├── auto_submit_roblox.py      # Uploader automático (batch)
    ├── state_roblox.json          # Estado dos uploads (auto-gerado)
    └── last_run_report.json       # Relatório da última execução
```

---

## Nomenclatura de Arquivos

O script faz **match automático** entre PNGs e itens do catálogo pelo nome do arquivo:

| Nome do PNG | Item do Catálogo | Tipo |
|-------------|------------------|------|
| `Crimson Shirt.png` | `"Crimson Shirt"` | `classic_shirt` |
| `Crimson Shirt Neon.png` | `"Crimson Shirt Neon"` | `classic_shirt` (variante) |
| `Crimson Wings Accessory.png` | `"Crimson Wings Accessory"` | `avatar_accessory` |
| `Crimson Wings Accessory Frost.png` | `"Crimson Wings Accessory"` + variante Frost | `avatar_accessory` |

Se um PNG **não** tiver correspondência no catálogo, o script:
1. Tenta inferir o tipo pelo sufixo no nome (`Shirt`, `Pants`, `Accessory`)
2. Usa `classic_shirt` como fallback
3. Se `--unmatched-only`, processa apenas esses

---

## Rate Limiting e Budget

| Parâmetro | Default | Descrição |
|-----------|---------|-----------|
| `--rate-limit` | 1.0s | Delay entre uploads (evita rate limit da API) |
| `--max-items` | 500 | Cap máximo de itens por execução |
| `UPLOAD_BUDGET_BYTES` | 250 MB | Budget total de bytes (segurança) |
| Tamanho máx. imagem | 10 MB | Validação por imagem |

---

## Estado e Idempotência

O script mantém `state_roblox.json` para **não re-enviar** itens já publicados:

```json
{
  "Crimson Shirt": {"status": "uploaded", "type": "classic_shirt"},
  "Crimson Wings Accessory Frost": {"status": "error", "msg": "HTTP 400 ..."}
}
```

- Itens com `status: "uploaded"` são pulados em execuções subsequentes
- Use `--force` para re-enviar itens mesmo que já marcados

---

## Relatórios

Após cada execução, `last_run_report.json` é gerado:

```json
{
  "uploaded": 45,
  "skipped": 312,
  "errors": 2,
  "budget_bytes": 8723456,
  "budget_max_bytes": 262144000,
  "items_remaining": 0,
  "catalog_total": 900
}
```

---

## Integração com a Pipeline

### Fluxo recomendado de lançamento de itens:

```bash
# 1. Gerar catálogo
python roblox-ugc/tools/generate_catalog.py

# 2. Validar catálogo
python roblox-ugc/tools/roblox_checks.py

# 3. Dry-run do auto-submit
python submit/auto_submit_roblox.py --dry-run

# 4. Testar com 1 item
python submit/auto_submit_roblox.py --test-one

# 5. Execução completa
python submit/auto_submit_roblox.py

# 6. Ver relatório
cat submit/last_run_report.json
```

---

## API Utilizada

### Assets API v1 (para ClassicShirt, ClassicPants, Hat)

```
POST https://apis.roblox.com/assets/v1/assets
Headers: x-api-key: <ROBLOX_API_KEY>
Body: multipart/form-data
  - request: JSON com assetType, displayName, description, creationContext
  - file: imagem PNG
```

### Cloud v2 Game Passes (para GamePass)

```
POST https://apis.roblox.com/cloud/v2/universes/{universe}/user-game-passes
Headers: x-api-key: <ROBLOX_API_KEY>
Body: JSON com displayName, description
```

> **Nota sobre Game Passes:** a API do game pass cria o item, mas o **ícone**
> deve ser adicionado manualmente no Creator Hub após a criação.

---

## Solução de Problemas

| Erro | Causa Provável | Solução |
|------|---------------|---------|
| `HTTP 401` | API key inválida/expirada | Regenerar em [Open Cloud](https://create.roblox.com/dashboard/credentials) |
| `HTTP 403` | API key sem permissão UGC | Verificar scopes da API key |
| `HTTP 429` | Rate limit excedido | Aumentar `--rate-limit` |
| `HTTP 400` | Imagem inválida ou metadados incorretos | Verificar formato/dimensões da imagem |
| `IMAGE_SIZE_OUT_OF_RANGE` | PNG > 10 MB | Comprimir imagem |
| `NO IMAGE for ...` | PNG não encontrado | Verificar nome do arquivo em `assets/` ou `items/` |
| `UNSUPPORTED_TYPE` | Tipo desconhecido no catálogo | Verificar `type` no `roblox_catalog.json` |
