# Execução atual — rebrand + stack Next.js/NestJS

> Estado atual
- `website/src/app/layout.tsx` já rebrandizado como `IconMyBedrockMods` com header/footer/a11y.
- `website/catalog/pack_index.json` gerado (10 registros) via `tools/build_website.ps1`.
- Tentativa de bootstrap do `website-next` via `create-next-app` travou por timeout no install.
- `marketplace-content` preservado intacto (sem remoção de diretórios/packs).
- Padrão Bedrock: pack dirs como fonte da verdade, scripts em `scripts/`, catálogo em `catalog/PACK_CATALOG.json`.

> Decisões tomadas
- Mantemos `marketplace-content` no path atual.
- Não vamos rodar `npm install` em loop até travar; usar instalação mínima/manual se necessário.
- Rebrand foi aplicado no site atual; reaproveitar para o Next.js.

> Próximos passos (execução ordenada)
1. Verificar se o `website-next` foi parcialmente criado; se não, criar estrutura manualmente.
2. Configurar `website-next/src/app/page.tsx` para consumir `marketplace-content/catalog/PACK_CATALOG.json` (ou `/api/catalog`).
3. Implementar `website-next/src/app/api/catalog/route.ts` com leitura segura do catálogo.
4. Replicar header/footer do layout atual (`IconMyBedrockMods`).
5. Adicionar estilos de catálogo/cards mantendo padrões de usabilidade básica.
6. Planejar NestJS backend em pastas separadas quando parte visual estiver rodando.
