#  Roadmap e Versionamento do Ecossistema

> **Arquitetura Bedrock Server Mods** | Documento gerado em 2026-06-25

---

## Ciclo de Vida do BDS e Mod Loaders

O Bedrock Dedicated Server (BDS) segue o versionamento do jogo cliente (ex: 1.26.10). Cada atualização do BDS quebra compatibilidade binária, exigindo rebuild dos mod loaders.

**Estratégia de Versionamento Recomendada:**
- **Semantic Versioning** para plugins: MAJOR.MINOR.PATCH
- **API Version pinning**: Travar versão do @minecraft/server no manifest.json
- **Canary releases**: Testar em branch separada antes de mergear
- **LTS branches**: Manter branches estáveis para versões populares do BDS

## Calendário de Atualizações 2026

| Data | Evento | Impacto |
|------|--------|---------|
| Jan 2026 | BDS 1.26.0 | Custom Dimensions API |
| Mar 2026 | BDS 1.26.10 | LeviLamina v26.10.x, Endstone 0.11 |
| Jun 2026 | BDS 1.26.20 | Script API v2 beta, Chaos Cubed content |
| Sep 2026 | BDS 1.27.0 | Major protocol changes expected |
| Dec 2026 | BDS 1.27.10 | Holiday content update |

---

*Documento parte da Arquitetura Bedrock Server Mods - Zip 01: Fundação Core*
