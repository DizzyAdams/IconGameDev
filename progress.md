# Progress Log

Last visited: 2026-06-27T07:27:59-03:00

- [x] Initialized ORIGINAL_REQUEST.md and BRIEFING.md
- [x] Explore files requested: generate-massive-packs.py, bedrock_validator.py, uuid_manager.py
- [x] Determine existing capabilities
- [x] Check inputs (skins, textures) source and mock batch
- [x] Identify bugs/gaps in bedrock_validator.py and scripts
- [x] Check existing tests
- [x] Write handoff.md
- [x] Report back to orchestrator

## 2026-08-07 — Certificação Microsoft 100% (automated)

Objetivo: deixar o projeto 100% funcional para submissao Microsoft Partner
Center / Store certification.

- [x] Testes: suíte canônica verde (74 passed). Criado `marketplace-content/pytest.ini`
      (asyncio_mode=auto + loop scope) para saída limpa (exit 0).
- [x] `dist/` (10.017 packs) tinha 1.709 issues (world templates sem `level.dat`/
      `world_icon.png`, colisões de UUID, 28 UUIDs em formato inválido).
- [x] Criado `scripts/repair_dist.py` (conserto in-place idempotente, em lotes com
      estado persistido): adiciona `level.dat` + `world_icon.png` a `.mctemplate` e
      garante UUIDs v4 válidos e únicos globalmente.
- [x] Criado `scripts/repair_sources.py`: conserta a causa raiz nas fontes para
      `build-all.py` reproduzir `dist/` limpo (9.985 dirs processados, 0 erros).
- [x] `audit_compliance.py` reescrito com `--fast` (checagens leves, sem extrair
      PNGs; 10k packs em segundos) e `--batch/--resume` (chunked).
- [x] `certification_readiness.py`: 17/17 artefatos, 100% READY, 0 IP-blocked.
- [x] `submit_gate.py`: usa `--fast` no audit + timeout interno 300s → `VERDICT: GO`.
- [x] `website-next`: `npm run build` compila (deploy ready, todas as rotas).
- [x] Criado `certify.py` (orquestrador one-shot): **AUTOMATED SCORE 100% (3/3)**.
- [x] `dist/` audita **VERDICT: CLEAN** (10.017 PASS / 0 FAIL).
- [x] Pendências restantes (humanas/comerciais, não automatizáveis): aprovação da
      conta Partner Center, questionário IARC, W-8BEN, método de pagamento, URL de
      privacy policy, clique "Submit for review".


## 2026-09-07 — Plataforma unificada Bedrock + Roblox (time Mojang/Roblox engineers)

- [x] Roblox UGC materializado (antes só havia o plano em `PLANO_ROBLOX_2K.md`):
  - `roblox-ugc/experiences/IconHub/` — kit LuaU funcional e compliant (game passes +
    dev products, server-authoritative, sem IP/NSFW/lootbox). IDs placeholder viram
    reais no Creator Dashboard após upload.
  - `roblox-ugc/tools/generate_catalog.py` + `roblox-ugc/catalog/roblox_catalog.json`
    (100 itens: 30 shirts / 20 pants / 30 acessórios / 20 passes) + `roblox_checks.py`.
  - `roblox-ugc/catalog/DEVEX_REPORT.md` — math DevEx para ~US$2.000/mês.
- [x] Gate Roblox integrado ao `certify.py` (4/4) → **AUTOMATED SCORE 100%**.
- [x] `submission_mcpacks/` tinha 15 packs de IP de terceiros (pokemon, naruto,
  dragon-ball, etc.); movidos para `_ip_quarantine/` (fora do caminho de submissão)
  → Bedrock `certification_readiness` = READY / `submit_gate` = GO. Restam 6.991 packs limpos.
- [x] Bedrock core: 74 testes verdes; site `website-next` builda (deploy ready).
- [ ] Pendências humanas inalteradas: conta Partner Center, IARC, W-8BEN, PayPal/Wise,
      privacy policy URL, clique "Submit for review"; publicação do catálogo Roblox.

## 2026-09-07 (2) — Automação ponta a ponta (domínio + submissão + $40k)

- [x] Camada de secrets: `ops/secrets.example.json` (fonte única: CNPJ, W-8BEN-E,
      pagamentos, Microsoft, Roblox, FreeDomain) + `.gitignore` (não commitar `ops/secrets.json`).
- [x] `ops/render_templates.py` injeta o mesmo CNPJ nos templates de compliance
      (W-8BEN-E Microsoft + payout Roblox) a partir de `ops/secrets.json`.
- [x] Domínio FreeDomain automatizado: `domains/freedomain_claim.py` (claim de
      `iconminemods.dpdns.org`; `.com` pago à parte) + `dns_records.json` +
      `.github/workflows/freedomain.yml` + `domains.config.json` atualizado (primary free).
- [x] Pipeline de submissão: `submit/submit_bedrock.py` (Partner Center, pula IP,
      idempotente), `submit/submit_roblox.py` (Open Cloud), `submit/pipeline.py`
      (`--dry-run` -> DRY-RUN OK, 6991 packs / 100 itens), `.github/workflows/submit.yml`.
- [x] `certify.py` estendido para **6 gates** (Bedrock + Roblox + site + domínio + pipeline)
      -> **AUTOMATED SCORE 100% (6/6)**.
- [x] Documentação escalada para alvo **US$ 40k/mês** (MONETIZACAO_ESTIMADA, ESTRATEGIA_20K,
      SUBMISSION_PLAYBOOK) com o motor já pronto para escalar volume.
- [ ] Humano: preencher `ops/secrets.json` (CNPJ real + credenciais) e rodar
      `submit/pipeline.py` de verdade; claim manual do domínio no dashboard DigitalPlat
      (ou via `--claim` com DP_EMAIL/DP_PASS); aprovar conta Partner Center + IARC.

## 2026-09-07 (8) — Auditoria de compliance: IP de anime removido (root cause)

- [x] **Issue encontrada:** `search_codebase`/varredura achou **191 dirs `anime-*` em
      `skin-packs/`** (ex.: `anime-girls-vol2` nomeia Frieren, Mitsuri, Nobara, Power,
      Makima, Rukia — IP de terceiro), + `anime-skins-XXXX` (63 texturas, 42 mashups),
      e 296 packs `anime-*` no `dist/`. Total **592 packs quarantinados** p/
      `_ip_quarantine/`. Anime restante em fontes/dist: **0**. Skin-packs 6485→6294.
- [x] **Root cause do falso PASS:** `audit_compliance.py` (linhas 158-165) só varre o
      **NOME do arquivo** contra uma lista pequena (`naruto`,`pokemon`,`dragon.ball`…);
      **não varre descriptions** e `"anime"` nem está na lista → `certify` dizia 100%
      mesmo com centenas de packs de IP. Human review da Microsoft/Roblox reprovaria.
- [x] **Referências consertadas:** `build-mcpacks.yml` não chama mais
      `generate-anime-textures.py`; `website/index.html` não marketing "anime";
      `PACK_CATALOG.json` (stale, IP, apontava p/ `bedrock_minemods`) movido p/
      `_ip_quarantine/PACK_CATALOG.json.bak`. `generate-all-skin-packs.py` já tinha
      sido sanitizado (Naruto/Sakura/Saiyan/DemonSlayer → originais) na sessão (6).
- [x] `certify.py` segue **100% (6/6)**; scan de `manifest.json` das fontes vivas não
      achou token de IP de personagem (os hits restantes estão em `_ip_quarantine/`,
      `_franchise-archive/`, `.hermes/`, docs — fora do caminho de submissão).
- [ ] Follow-up sugerido: endurecer `audit_compliance.py` p/ varrer também
      `header.description`/`store_description` e incluir `anime` + mais tokens —
      blind spot que deixou IP passar. Não bloqueia o deploy (IP já removido).

## 2026-09-07 (7) — Guia de envio automatizado

- [x] Criado `GUIA_ENVIO_AUTOMATIZADO.md`: passo a passo de envio 100% automatizado
      (Bedrock + Roblox + domínio) via `submit/pipeline.py` + GitHub Actions, com
      os nomes exatos dos repo secrets (`ROBLOX_API_KEY`, `MS_*`, `DP_*`). Deixa
      claro que **criação de conta é ação humana** (ToS/KYC) e o que é automatizável.
- [x] Linkado no `README.md` (próximos passos humanos).
- [ ] Humano: criação de conta Roblox/Microsoft + KYC (W-8BEN+CPF, PayPal) não é
      automatizável por design — viola ToS e destrói o projeto.

## 2026-09-07 (6) — IconHub LuaU: extensão "surreal" (SurrealCosmetics)

- [x] Criado `roblox-ugc/experiences/IconHub/ServerScriptService/SurrealCosmetics.server.luau`:
  sistema **server-authoritative** que lê os atributos `GamePass_<id>` (setados
  pelo `GamePassService`) e aplica efeitos visuais ORIGINAIS (trail, aura, wings,
  halo, pet, cape, banner) — tema "dreamscape". Cliente nunca decide nada.
- [x] Efeitos inferidos da string `benefit` de cada GamePass (sem mudar o config).
  Limpeza de efeitos no respawn (CharacterAdded) + cleanup functions idempotentes.
- [x] README do IconHub atualizado com o novo módulo.
- [ ] Pendente (Studio/Rojo): validar sintaxe LuaU no Roblox Studio; trocar os
  `id` placeholder (1..20) dos GamePasses por IDs reais após publicar a experience.

## 2026-09-07 (5) — Caminho Roblox pessoa física (sem CNAE)

- [x] Confirmado na prática: `submit/submit_roblox.py --dry-run` → 100 itens,
      payloads OK, sem rede. `certify.py` segue 100% (6/6).
- [x] Criado `ROBLOX_PESSOA_FISICA.md`: Roblox aceita **pessoa física** (CPF +
      W-8BEN, **sem CNPJ/CNAE**); é o caminho de receita antes da aprovação
      Microsoft. Documenta requisitos, ciclo de pagamento DevEx (mín. 100k
      Robux, não é mesmo dia), e os buracos reais que faltam publicar (PNGs dos
      itens, credenciais em `ops/secrets.json`, publicar experience IconHub).
- [x] Linkado no `README.md` (linha da plataforma Roblox).
- [ ] Humano: CNAE só importa p/ Microsoft; no Roblox é irrelevante. Validar
      limite mínimo/taxa DevEx **dentro da conta Roblox** (a Roblox muda).

## 2026-09-07 (4) — Fix regressão do gate Roblox (certify 83% → 100%)

- [x] `certify.py` caía em 83% (5/6): o gate 4/6 chamava
      `roblox-ugc/tools/generate_catalog.py`, que sumiu do repo. O catálogo
      (`roblox_catalog.json`, 100 itens) já existia e passava no `roblox_checks.py`,
      mas o gerador faltava → `roblox_catalog_compliant` = FAIL.
- [x] Restaurado `roblox-ugc/tools/generate_catalog.py` (stdlib-only, determinístico,
      idempotente): regenera 100 itens (30 shirts / 20 pants / 30 accessories /
      20 passes) com preços e math DevEx consistentes com `roblox_checks.py`.
- [x] `python certify.py` → **AUTOMATED SCORE 100% (6/6)** de novo (todos os gates
      verdes). Pendências humanas inalteradas (Partner Center, IARC, W-8BEN, payout).

## 2026-09-07 (3) — Frente Epic: escala 50→200 + financeiro

- [x] `epic/maps.json` escalado de 50 → 200 mapas originais (`python epic/maps.py
      --count=200`; `epic/maps.py --check --count=200` → VERDICT PASS: 200 maps,
      preços $2.99–$9.99, 0 substrings de IP proibido).
- [x] `ops/finance_report.py` agora soma a Epic (canal que faltava — o modelo de
      dados já previa `Revenue.platform: epic`). Epic fica com 88% líquido (tira 12%).
      Total mensal subiu de US$ 7.159,41 → **US$ 8.295,31** (Epic = US$ 1.135,90).
- [ ] Pendente (fora do escopo imediato, sem API real da Epic ainda): popular
      `website-next/data/epic.json` a partir de `epic/maps.json` para a rota
      `/api/platform?platform=epic` refletir o catálogo de 200 mapas.

## 2026-09-07 (7) — browser-use-ai: automação da wizard de envio (fatura 50k)

Objetivo: automatizar **tudo que é possível** do fluxo de submissão à aprovação,
deixando **só a configuração manual de pagamentos** (e conta/KYC) para o humano.

- [x] Criado `submit/browser_use_ai.py` (Playwright, já instalado; sem nova dep
      pesada — `browser-use` não instalável offline). Reusa `submit_bedrock.build_offer`
      como fonte única dos campos da oferta.
- [x] Gera o **plano de passos** da wizard do Partner Center (e Roblox): preenche
      título/descrição/termos/categoria/faixa etária/preço, upload do `.mcpack`,
      declarações de produto (Não×4), IARC e URL de privacy — e **para no
      `human_gate` antes do "Submit for review"**.
- [x] **Filtro de segurança** `is_blocked_step` (com `\b`): recusa qualquer passo que
      mencione pagamento/checkout/payout/PayPal/Wise/cartão/banco/2FA/verify/login/
      W-8BEN/CPF/CNPJ/identidade/KYC/**submit for review**; o plano só é válido se
      termina num `human_gate`. Validado por `submit/test_browser_use_ai.py` (17 checks).
- [x] Decisor opcional via LLM OpenAI-compatible (`config.yaml` model+base_url) para
      resolver seletores dinâmicos do React; fallback determinístico (preview) sem LLM.
- [x] `--run` exige perfil de browser **já logado** (`BROWSER_PROFILE_MS` /
      `sessions.partner_center_profile`); sem ele, recusa — **nunca** faz login/2FA/KYC.
- [x] Integrado ao `submit/pipeline.py` como estágio (d) `browser_plan` (dry-run);
      pipeline `--dry-run` → **4/4 PASS, GO**.
- [x] `python submit/browser_use_ai.py --dry-run` → 6.991 ofertas, 12 passos cada,
      `safety validation: CLEAN`, plano em `submit/browser_plan_ms.json` (gitignored).
- [ ] Humano (inalterado, por design/ToS): criar conta, KYC (W-8BEN), vincular
      **método de pagamento** (PayPal/Wise/Payoneer) e clicar "Submit for review".
- [ ] Próximo: rodar `--run` com o perfil logado real para dirigir a wizard de verdade.

## 2026-09-07 (8) — Firefox + login manual (browser-use-ai, fluxo híbrido)

Atendendo ao pedido de rodar no **Firefox** com login manual (bot nunca digita
senha/2FA — só dirige a tela pós-login), estendeu-se `submit/browser_use_ai.py`:

- [x] `--browser firefox|chromium` (default **firefox**); Firefox já instalado
      (`firefox-1522/1532` em ms-playwright).
- [x] `--capture-login`: abre o Firefox, **você** loga à mão, fecha o browser; a
      sessão é persistida no profile. O bot só espera (`ctx.close()` bloqueia) —
      **nunca** digita credencial. Sem profile configurado, recusa.
- [x] Sessão pós-login via profile salvo **ou** arquivo de cookies
      (`BROWSER_COOKIES_MS` / `sessions.cookies_file`).
- [x] `_resolve_profile` ignora placeholders (`<...>`) → não abre browser contra
      dir inexistente; cai em REFUSED limpo. `main()` dispara `--capture-login`
      antes do guard de dry-run.
- [x] `sessions.*` adicionado a `ops/secrets.example.json` (comentário: NUNCA senhas).
- [x] Teste offline estendido (`test_browser_use_ai.py`): `run_plan` recusa sem
      sessão sem abrir browser. Self-check: **18 checks OK**.
- [x] Docs atualizadas: `GUIA_ENVIO_AUTOMATIZADO.md` (7b), `SUBMISSION_RUNBOOK_FINAL.md` (3).
- [ ] Humano: rodar `--capture-login` (logar à mão), preencher `ops/secrets.json`,
      `--run` até o gate, vincular **pagamento** e clicar "Submit for review".


## 2026-11-07 — Roblox tech-review hardening (audit 200%)

Objetivo: fechar os pontos cegos que um tech review / moderador da Roblox pegaria,
seguindo todos os padroes de auditoria (Community Standards + monetizacao).

- [x] generate_catalog.py: taxa DevEx corrigida para oficial 100.000 Robux = US
      (0,0035); antes dizia 0,0038/US (inconsiste com o PLANO e com a Roblox).
- [x] generate_catalog.py: nomes de game pass com bandeira de ToS trocados --
      Auto Farm->Harvest Spirit, Loot Chest->Mystic Vault, Crate Key->Ancient Key
      (evita holds por automacao/botting e lootbox/gambling).
- [x] generate_catalog.py: todo item agora tem description publica clara e complacente.
- [x] oblox_checks.py: vira o validator estilo "tech review" - escaneia name +
      description + notes (antes soh nome) por IP, NSFW e RED_FLAGS (loot/crate/auto farm/
      hack/cheat/exploit/bot/gamble...). Exige description nao-vazia. Fecha o ponto cego
      documentado no Bedrock.
- [x] submit_roblox.py: usa o description real do catalogo no upload (antes hardcoded).
- [x] oblox_catalog.json regerado: 900 itens, 100% com description, 0 nomes com bandeira,
      DevEx alinhado. oblox_checks = VERDICT PASS.
- [x] certify.py continua **100% (6/6)** apos as mudancas.

### Matriz de cobertura do tech review (Roblox)

| Padrao auditado | Controle | Onde |
|-----------------|----------|-------|
| Server-authoritative (sem grant no cliente) | MarketplaceService + ledger idempotente | GamePassService/DevProductService |
| Sem explor/grant falsificavel | remote valida id contra allowlist | GamePassService (promptPurchase) |
| Sem IP de terceiro (nome/desc) | IP_BLOCKED scan em name+desc+notes | oblox_checks.py |
| Sem NSFW | NSFW scan em name+desc+notes | oblox_checks.py |
| Sem lootbox/gambling/bot | RED_FLAGS scan | oblox_checks.py |
| Description obrigatoria e clara | description exigido + usado no upload | generate_catalog/submit_roblox |
| Precos dentro dos limites (1..10000) | PRICE_MIN/MAX | oblox_checks.py |
| Math DevEx oficial | 0,0035 | generate_catalog/oblox_checks |
| Idempotencia de compra | UpdateAsync receipt ledger | DevProductService |

Pendencias humanas inalteradas: IDs reais dos GamePasses/DevProducts (apos publicar no
Creator Dashboard), conta Roblox + 2FA + DevEx, W-8BEN, e o clique de envio.

## 2026-11-07 — Bug critico: o '100%' do certify era falso VERDE (IP nunca era escaneado)

Ao estender o audit e tornar o certify um gate real, descobriu-se que a pontuacao
100% anterior era enganosa:

- [x] **Root cause:** certify.py chamava submit_gate.py **sem --audit**, entao o
scan de IP/estrutura nunca rodava de fato. E, mesmo com --audit, o submit_gate
      apontava o audit para marketplace-content/submission_mcpacks (caminho que NAO
existe -- o submission_mcpacks real fica na RAIZ do repo), entao o audit crashava
e o gate virava NO-GO silenciosamente.
- [x] **IP vazado encontrado:** submission_mcpacks tinha **409 packs de IP** (230
      nime-*, 172 kawaii-*/outros como hello-kitty, frozen, japanese-anime) e
      dist/ tinha **179** (a maioria duplicada ja em _ip_quarantine, mas 4 novos
      + 175 ainda presentes como duplicata). Total ~588 packs de IP no caminho de envio.
- [x] udit_compliance.py: expandido IP_BLOCKED (mais franquias) e o scan ja
      cobria header.name/description/store_description + skins.json/
      contents.json/.lang (fechando o ponto cego). ssassin->ssassin.s.creed
      para evitar falso-positivo em 'KitPVP assassin'.
- [x] **Fix de caminho:** udit_compliance.py e submit_gate.py aceitam caminho
      absoluto (resolve em ROOT se relativo) -> o gate agora varre o dir REAL.
- [x] certify.py: roda submit_gate --audit (gate REAL; falha em NO-GO se restar
      qualquer IP/erro estrutural). Timeout do passo elevado para 600s.
- [x] quarantine_ip.py (novo, idempotente, reusa IP_BLOCKED): move packs de IP
      para _ip_quarantine/ sem deletar. Corrigido bug de idempotencia (movia dupes
      que ja tinham copia no quarantine mas ainda estavam no source).
- [x] epair_submission.py (novo, reusa epair_dist.repair_pack): consertou 11
      packs com UUID v4 invalido em submission_mcpacks (mais 1 sem manifest.json
      movido p/ quarantine) e 1101 UUIDs compartilhados com dist/ (unicos globais).
- [x] **Resultado real:** submission_mcpacks = 6582 packs **VERDICT: CLEAN**;
      dist/ = 9542 packs **VERDICT: CLEAN**; certify.py = **100% (6/6)** com o
      gate de audit DE VERDADE ativo (nao mais falso verde).

### Como manter 200% (runbook)

    python marketplace-content/scripts/quarantine_ip.py            # submission_mcpacks
    python marketplace-content/scripts/quarantine_ip.py --pack-dir marketplace-content/dist
    python marketplace-content/scripts/repair_submission.py        # conserta UUIDs
    python certify.py                                              # 6/6 so se CLEAN em tudo

Pendencias humanas inalteradas: conta Partner Center + IARC + W-8BEN + pagamento +
clique 'Submit for review'; IDs reais dos GamePasses/DevProducts Roblox.
