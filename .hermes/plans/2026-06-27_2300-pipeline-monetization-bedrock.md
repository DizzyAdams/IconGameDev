# Pipeline + Monetização Bedrock: Plano Execução

**Goal:**
1) Finalizar o pipeline de metadata/compliance/catálogo/site.
2) Levantar referências e padrões de monetização/qualidade do ecossistema Bedrock/Microsoft e gerar uma arquitetura rentável.

**Context/Assumptions:**
- O projeto atual está em `C:\Users\forrydev\Desktop\bedrock_minemods\marketplace-content`.
- Packs fonte: `dist/*.mcpack` (171 itens). Estrutura organizada: `descriptions/`, `skin-packs/`, `texture-packs/`, `world-templates/`, `mashup-packs/`, `screenshots/`.
- Já existem `scripts/upgrade-manifests.py`, módulos `src/catalog/`, e 5 agents em `agents/`.
- O retorno passado mostrou bloqueios de path/Windows (diretório `out/dist_audit_sample.json`, `mc_dir` errado no script).
- Usuário confirmou usar `continue` + permissão total para execução real.

**Proposed approach:**
1. Corrigir bloqueios do Windows antes de qualquer “mass run”.
2. Gerar um sample auditável confiável em `out/dist_audit_sample_10.json`.
3. Revisar se um item cutuca QA/compliance com dados corretos.
4. Refinar agentes para considerar `dist/*.mcpack` como fonte canônica e manter compatibilidade com manifests locais.
5. Gerar relatório de curadoria (sample first) e só depois propor integração no site.
6. Fechar este plano (tarefas sequenciais), e depois iniciar o plano de arquitetura de monetização.

## Tarefas

### Task 1: Limpar trava de path no Windows
- Excluir o arquivo/diretório corrompido `out/dist_audit_sample.json`
  - `rmdir out/dist_audit_sample.json` (se existir como diretório)

### Task 2: Ajustar script para evitar nome conflitante
- Alterar `scripts/audit_from_dist.py` para salvar como `out/dist_audit_sample_10.json`
- Garantir `Path(__file__)` absoluto e criação de diretório com `mkdir(parents=True, exist_ok=True)`
- Usar cwd real em vez de caminho base incompatível

### Task 3: Rodar sample auditável
- Executar: `cd C:\Users\forrydev\Desktop\bedrock_minemods\marketplace-content`
- `PYTHONPATH=. python scripts/audit_from_dist.py --sample-size 10`
- Ler o JSON e verificar: preço/tier/descrição/header_description

### Task 4: Validar pack `anime-world` com regras reais
- Rodar `agents/pricing_compliance_agent.py --pack-dir anime-world --subdir-hint mashup-packs`
- Rodar `agents/compliance_qa_agent.py --pack-dir anime-world`
- Confirmar que `anime-world` aponta para `mashup-packs/anime-world/manifest.json`
- Verificar preço, tipo, tier, e description correta

### Task 5: Corrigir detector de subdiretório nos agents (se necessário)
- `agents/catalog_site_agent.py` e `agents/sales_deploy_agent.py` devem procurar em:
  1) `mashup-packs/<pack_dir>`
  2) `world-templates/<pack_dir>`
  3) `texture-packs/<pack_dir>`
  4) `skin-packs/<pack_dir>`
- Em vez de assumir uma ordem fixa

### Task 6: Revisar QA/compliance
- Garantir que `compliance_qa_agent.py` usa `descriptions/<pack_dir>` para extrair texto
- Garantir que `assets_agent.py` não cria conflitos com nomes de pasta

### Task 7: Gerar primeiro relatório executável
- Usar sample de 10 packs da pasta `dist/`
- Estrutura: `out/first_batch_report.json`
- Campos: `pack_dir`, `type`, `price`, `tier`, `description`, `store_description`, `qa_decision`

### Task 8: Apresentar arquitetura de monetização Bedrock
- Mapear padrões Microsoft/Bedrock: pricing tiers, asset specs, compliance, SEO de marketplace
- Gerar documento: `docs/bedrock-monetization-architecture.md`
- Cobrir:
  - Sources of truth: `descriptions/`, `screenshots/`, `dist/*.mcpack`
  - Regras de metadata premium
  - Pricing strategy por tier
  - Pipelines de assets (icon, thumbnail, banner)
  - Compliance checklist por pack
  - Views/site: catálogo, SEO, search keywords

## Tests/Verification
- `ls out/dist_audit_sample_10.json` existe e contém 10 itens
- `grep 'anime-world' out/dist_audit_sample_10.json`
- Ações dos agents retornam JSON válido e sem erro de diretório inexistente

## Risks/Tradeoffs
- Windows/MSYS pode continuar quebrando paths absolutos; mitigar com cwd/env.
- `audit_from_dist.py` reescreve conteúdo sem tocar em arquivos locais — sem risco de corromper manifests, mas pode espelhar preços “default”. Validar pricing ranges antes.

## Open Questions
- Definir se quer validação agora no `anime-world` ou primeiro gerar o relatório de 10 packs?
- Site atual usa `generate-site.py`? Depois de finalizar metadata, integrar novo catálogo neste gerador ou criar endpoint separado?
