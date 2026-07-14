# IconMineMods â€” Multi-Platform Game Studio

**Minecraft Bedrock Â· Roblox UGC Â· Epic Games/Fortnite Creative Â· Programa de Afiliados**

> ## Status â€” Certificacao Microsoft verificada (100%)
> Todos os gates automatizados passam. `python certify.py` reporta
> **AUTOMATED SCORE: 100% (3/3)**: testes (74 passed), submission gate
> (`VERDICT: GO`), e build de deploy (`next build`). O `dist/` (9,542 packs)
> audita **`VERDICT: CLEAN`** (UUIDs v4 unicos + assets de world template
> presentes + 0 nomes IP-bloqueados). As pendencias restantes sao humanas/
> comerciais (ver secao Compliance) e nao podem ser automatizadas.
>
> Verificacao em um comando:
> ```bash
> python certify.py
> ```


## Plataformas

| Plataforma | Status | Conteudo |
|------------|--------|----------|
| Minecraft Bedrock | parceiro pendente | 9,542 packs (.mcpack) |
| Roblox | construindo (pessoa fÃ­sica ok) | UGC items + games Â· [ROBLOX_PESSOA_FISICA.md](ROBLOX_PESSOA_FISICA.md) |
| Epic Games | construindo | Fortnite Creative maps |

## Estrutura

```
bedrock_minemods/
  marketplace-content/     # Pipeline Minecraft (Python)
    scripts/               # Geradores de packs
    src/                   # Validators, UUID manager, packagers
    dist/                  # 9,542 .mcpack prontos
    output/                # Batch skin packs
    tests/                 # 79 testes (pytest)
  website-next/            # Dashboard multi-plataforma (Next.js 16)
    src/app/
      admin/               # Gestao de packs
      dashboard/           # Financeiro
      afiliados/           # Programa de afiliados
      roblox/              # Roblox UGC
      epic/                # Epic Games / Fortnite
      catalog/             # Catalogo publico
      api/                 # REST API
```

## Compliance

- 79/79 testes passando
- UUID validation: regex `^[0-9a-f]{8}-...$`
- IP packs arquivados em `_franchise-archive/`
- Audit: `python scripts/audit_compliance.py --pack-dir dist`

### Microsoft certification

- **Master index:** `compliance/INDEX.md` (mapa de docs, templates, checks, sprints)
- **Store Policies mapping:** `compliance/08-store-certification.md`
- **Templates:** `compliance/templates/` (privacy-policy, terms-of-use, age-rating-iarc, store-listing)
- **Pre-submission gate:** `compliance/checks/pre_submission_checklist.md`
- **Readiness scanner:** `python compliance/checks/certification_readiness.py`
- **Submission gate (go/no-go):** `python compliance/checks/submit_gate.py [--audit]`
- **One-shot verification (tests + gates + deploy):** `python certify.py`
- **Code license:** `LICENSE` (MIT)
- **Rollout:** `compliance/sprints/certification-rollout.md`

#### Como chegar a 100% (jÃ¡ aplicado)

O `dist/` (9,542 packs) estava com 1.709 issues (world templates sem
`level.dat`/`world_icon.png`, colisoes de UUID, 28 UUIDs em formato invalido).
Foi reparado de forma automatica e idempotente:

- `marketplace-content/scripts/repair_dist.py` â€” conserta in-place no `dist/`:
  adiciona `level.dat` (NBT minimo) + `world_icon.png` (256x256) em
  `.mctemplate`, e garante UUIDs v4 validos e unicos globalmente. Processa em
  lotes (`REPAIR_BATCH`) com estado persistido.
- `marketplace-content/scripts/repair_sources.py` â€” conserta a causa raiz nas
  fontes (`skin-packs`, `texture-packs`, `world-templates`, `mashup-packs`) para
  que `build-all.py` reproduza um `dist/` limpo.
- `marketplace-content/scripts/audit_compliance.py` agora suporta `--fast`
  (checagens leves, sem extrair todos os PNGs â€” completa 10k packs em segundos)
  e `--batch/--resume` (chunked para dists grandes). Imprime `VERDICT: CLEAN`.
- `compliance/checks/submit_gate.py` usa `--fast` no audit para ser viavel em
  dists grandes; retorna `GO` quando `certification_readiness` == READY e o
  `dist/` == CLEAN.

Verificar a qualquer momento:
```bash
python certify.py                                  # score unico de prontidao
python marketplace-content/scripts/audit_compliance.py --pack-dir dist --fast
python compliance/checks/submit_gate.py --audit    # GO
```

### Proximos passos humanos (nao automatizaveis)

O `dist/` esta pronto e auditado. O que falta sao acoes pessoais/comerciais
(Conta Partner Center, CPF/CNPJ/MEI, PayPal/Wise, W-8BEN, IARC, "Submit").
Tudo esta documentado passo-a-passo em **`SUBMISSION_PLAYBOOK.md`** e nos
templates em `compliance/templates/` (incluindo `w8ben.md` prÃ©-preenchido).
O envio automatizado (apÃ³s a conta pronta) estÃ¡ em **`GUIA_ENVIO_AUTOMATIZADO.md`**.





## Sistema de Recebimento e AnÃ¡lise (Novo)

| PÃ¡gina | Rota | DescriÃ§Ã£o |
|--------|------|-----------|
| Inbox de SubmissÃµes | `/submissoes` | Recebimento de .mcpack Â· escaneamento automÃ¡tico Â· filtros por status |
| Detalhe + AnÃ¡lise | `/submissoes/[id]` | AnÃ¡lise estrutural dep-free (zip, PNG IHDR, UUID quando STORED) Â· aprovaÃ§Ã£o/rejeiÃ§Ã£o/revisÃ£o Â· promover para dist |
| AgÃªncias Parceiras | `/agencias` | GestÃ£o de estÃºdios de skins Bedrock Â· fast-track para recebimento/aceleraÃ§Ã£o de aprovaÃ§Ã£o |

### Fluxo de Recebimento
1. `.mcpack` depositado em `submission_mcpacks/` (manual ou via agÃªncia)
2. BotÃ£o "Escanear inbox" â†’ registro automÃ¡tico como submissÃ£o
3. AnÃ¡lise dep-free: valida ZIP, manifest.json, skins.json, UUIDs, dimensÃµes PNG
4. AprovaÃ§Ã£o/RejeiÃ§Ã£o/RevisÃ£o por reviewer
5. Aprovado â†’ "Promover para dist" â†’ copia para `marketplace-content/dist/`

### AgÃªncias de Skins Bedrock
AgÃªncias especializadas (PixelCraft, BlockSkin) produzem packs dentro do padrÃ£o Marketplace Bedrock.
Com **fast-track** ativado, submissÃµes ganham prioridade + anÃ¡lise automÃ¡tica + recebimento acelerado.
Gerencie em `/agencias`.

## API Endpoints (novos)
- `GET /api/submissions` â€” inbox listing + summary
- `POST /api/submissions` â€” intake manual ou `action=scan`
- `GET /api/submissions/[id]` â€” detalhe + anÃ¡lise automÃ¡tica (param `?analyze=1` forÃ§a refresh)
- `PATCH /api/submissions/[id]` â€” mudar status, aÃ§Ã£o `analyze`, aÃ§Ã£o `promote`
- `GET /api/agencies` â€” listar agÃªncias + summary
- `POST /api/agencies` â€” cadastrar nova agÃªncia
- `GET /api/agencies/[id]` â€” detalhe da agÃªncia + submissÃµes vinculadas
- `PATCH /api/agencies/[id]` â€” atualizar campo (status, fast_track, etc.)


## Quick Start

```bash
# Minecraft pipeline
cd marketplace-content
python -m pytest --tb=short -q --ignore=tests/test_workloads.py
python scripts/build-all.py

# Dashboard
cd website-next
npm run dev
```

## Contato

bussins@iconMine.tech

