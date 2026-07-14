# Submission Automation — Deploy & Execution Guide

Local: `submit/`

## Pré-requisitos

- Python 3.10+
- Internet (real run only)
- Credenciais em `ops/secrets.json` ou `.env` na raiz:
  - `ROBLOX_API_KEY`
  - `ROBLOX_GROUP_ID`
  - `ROBLOX_EXPERIENCE_ID`

Scripts dependem apenas da stdlib (`urllib`, `json`, `zipfile`, `argparse`).

---

## Pipeline oficial

```bash
# dry-run seguro — valida config, catálogo e assets, SEM uploads
python submit/pipeline.py --dry-run

# real run — Bedrock + Roblox + domains
python submit/pipeline.py
```

## Scripts individuais

### Roblox UGC upload
```bash
# valida catálogo + assets
python submit/submit_roblox.py --dry-run

# upload de 1 item (safe first run)
python submit/submit_roblox.py --test-one

# upload real (idempotente por nome)
python submit/submit_roblox.py
```

Comportamento:
- Pula itens já `status=uploaded` em `submit/state_roblox.json`.
- Gera `submit/last_run_report.json`.
- Hard cap: `MAX_ITEMS=500` por real run.

Resiliência:
- Retry com backoff em erros transitórios de rede (`REQUEST_RETRIES=3`).
- HTTPError retorna imediatamente (não retry).

### Bedrock Marketplace
```bash
python submit/submit_bedrock.py --dry-run
python submit/submit_bedrock.py
```

### Domains claim
```bash
# verifica apenas
python submit/domains/freedomain_claim.py --check
```

---

## Referência rápida

| Flag          | Efeito                                              |
|---------------|-----------------------------------------------------|
| `--dry-run`   | Validação local, nenhuma chamada de rede            |
| `--test-one`  | Executa exatamente 1 item no Roblox                 |
| `--pack-dir`  | Diretório de entrada dos packs (Bedrock audit)      |
| `--resume`    | Continua audit compliance de onde parou             |
| `--fast`      | Auditoria estrutural leve, sem extração PNG         |
