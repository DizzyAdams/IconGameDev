---
name: mass-monetizer-bot
description: Skill to automatically generate high-profit Bedrock behavior packs (Add-ons) like OP Swords, Lucky Blocks, etc.
---

# Mass Monetizer Bot (Behavior Packs)

Esta skill permite que um sub-agente gere instantaneamente Add-ons (Behavior Packs) de alta conversão para o Minecraft Bedrock.

## Como usar
1. O agente deve garantir que está no diretório raiz do workspace (`C:\Users\forrydev\Desktop\bedrock_minemods`).
2. Executar o script de geração massiva:
   `python marketplace-content/scripts/generate-addons.py`
3. Os pacotes serão gerados na pasta `marketplace-content/behavior-packs`.
4. (Opcional) O agente pode editar o dicionário `ADDONS` dentro de `generate-addons.py` para injetar novos temas que estejam em alta nas trends (trend-jacking).

## Restrições
- Não modifique a estrutura base do `manifest.json`.
- Mantenha sempre um `UUID` único gerado dinamicamente para cada módulo.
