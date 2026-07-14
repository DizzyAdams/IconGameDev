# Segurança & Segredos

Última revisão: 2026-07-10

## Arquivos de segredo (NUNCA versionar)

Estes arquivos estão no `.gitignore` e **não devem** ser commitados:

| Arquivo             | Conteúdo                                  | Regra no `.gitignore` |
|---------------------|-------------------------------------------|-----------------------|
| `.env`              | Variáveis locais (Roblox etc.)           | linha `2-3`           |
| `keyroblox.env`     | Config Roblox local                       | linha `38`            |
| `ROBLOX_CONFIG.env` | Config Roblox local                       | linha `34-35`         |
| `ops/secrets.json`  | Segredos reais (template = `ops/secrets.json` é EXEMPLO) | linha `2` |

`ops/secrets.json` no disco é apenas um **template de exemplo** (`_comment` indica isso).
Os arquivos `.env`/`ROBLOX_CONFIG.env`/`keyroblox.env` estão com valores vazios.

## Rotação OBRIGATÓRIA — token Vercel vazado em chat

Um token da Vercel foi exposto em conversa de chat. **Trate como comprometido
imediatamente**, mesmo que "pareça inofensivo". Faça a rotação AGORA:

1. **Revogar o token vazado (prioridade 0)**
   - Dashboard Vercel → **Settings → Tokens** (ou **Account → Tokens**);
   - localize o token exposto e clique em **Delete/Revoke**;
   - alternativa via CLI: `vercel tokens list` e `vercel tokens remove <id>`.
   - Ele não pode ser "girado" in-place: o antigo deve ser **excluído** e um
     novo deve ser criado.

2. **Auditar uso indevido**
   - Em **Settings → Tokens** e no log de atividade da conta, verifique se
     houve deploys, leitura de vars de ambiente ou acessos à API com o token
     vazado;
   - revise **Deployments** e **Project → Settings → Environment Variables**
     de todos os projetros para detectar alterações não autorizadas.

3. **Criar novo token**
   - Gere um token novo com o **menor escopo/permissão** necessário
     (project-scoped em vez de account-scoped quando possível) e expiração
     definida.

4. **Atualizar todos os consumidores (sem commitar)**
   - GitHub Actions: **Settings → Secrets and variables → Actions** — atualize
     `VERCEL_TOKEN` (e quaisquer `VERCEL_*`) usados em `deploy-site.yml`,
     `freedomain.yml`, etc. Nunca cole o token no código.
   - Local: cole apenas em `.env` / `keyroblox.env` (gitignored).
   - Documentação/CI: referencie o secret por nome (`${{ secrets.VERCEL_TOKEN }}`),
     nunca o valor literal.

5. **Verificar limpeza**
   - Rode o scanner: `python scripts/check_secrets.py` (deve retornar `OK`).
   - Garanta que o valor antigo não ficou em nenhum arquivo, histórico ou log.

> Regra: qualquer secret que já foi colado em chat/issue/PR está considerado
> público. Não há "recuperar" — só revogar e trocar.

## Check automático de segredos

`scripts/check_secrets.py` (stdlib, sem dependências) faz:
- validação via `git ls-files` de que os 4 arquivos acima **não** estão trackados;
- grep de padrões de token (Vercel, AWS, GitHub, Slack, Stripe, GCP, GitLab,
  JWT, chaves privadas, assignments genéricos) em arquivos não-ignorados.

Rodar localmente:
```bash
python scripts/check_secrets.py          # scan normal
python scripts/check_secrets.py --strict # também falha se não houver repo git
```

CI: o workflow `.github/workflows/secret-scan.yml` roda esse check em todo
`push`/`pull_request` (branch `main`).
