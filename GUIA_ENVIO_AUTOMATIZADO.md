# Guia de Envio Automatizado — IconMineMods

Como deixar todo o **envio** (Bedrock + Roblox + domínio) automatizado, e o que
continua sendo ação humana (e por quê).

---

## 0. O que é automatizado vs. humano (leia antes)

| Etapa | Quem faz | Por quê |
|-------|----------|---------|
| Gerar conteúdo (packs, catálogo) | Código | script `marketplace-content/scripts/*` |
| Validar compliance | Código | `certify.py`, `audit_compliance.py` |
| Build do site | Código | `website-next` / `npm run build` |
| **Criar conta Roblox / Microsoft** | **Você (humano)** | ToS proíbe conta por bot; KYC/tributário é pessoal |
| Verificar idade / 2FA / W-8BEN / PayPal | **Você (humano)** | verificação de identidade não é automatizável |
| **Enviar** packs/catálogo | Código | `submit/pipeline.py` (1 comando) |
| Pagar/DevEx | Plataforma | ciclo da Roblox/Microsoft após vendas reais |

> **Criação de conta NÃO é automatizada de propósito.** Conta feita por script
> com e-mail/telefone viola os Termos de Uso e é banida na primeira revisão; a
> plataforma ainda estorna (clawback) pagamentos de conta irregular. O KYC
> (W-8BEN com seu CPF, idade, 2FA, PayPal) só pode ser feito por você, logado,
> com seus documentos. Automatizar isso destruiria o projeto.

---

## 1. Pré-requisitos humanos (uma vez)

1. **Roblox** (pessoa física ok, sem CNAE): criar conta com seu e-mail → verificar
   idade + 2FA → habilitar **DevEx** (perfil fiscal W-8BEN, TIN = seu CPF) →
   vincular **PayPal** no portal de payout.
2. **Microsoft Partner Center** (exige CNPJ/empresa): criar conta → aprovação →
   IARC → W-8BEN-E. Leva dias; comece cedo.
3. **Roblox Open Cloud API key**: Creator Hub → `Develop` → `API keys` → crie uma
   chave com permissão de upload. Guarde a chave.
4. Anote o **Group ID** e o **Universe ID** da sua experience IconHub.

---

## 2. Preencher `ops/secrets.json` (credenciais reais)

```bash
cp ops/secrets.example.json ops/secrets.json   # NUNCA comite secrets.json (.gitignore já cobre)
```

Preencha (campos em `ops/secrets.example.json`):
- `roblox.api_key`, `roblox.group_id`, `roblox.experience_id`
- `microsoft_partner.*` (só para Bedrock real)
- `freedomain.*` (opcional, domínio free)
- `payments.*` (só referência; PayPal é vinculado no portal, não aqui)

---

## 3. Validar sem enviar (dry-run, seguro)

```bash
python certify.py                  # deve dar 100% (6/6)
python submit/pipeline.py --dry-run   # deve imprimir GO/NO-GO: GO  e  DRY-RUN OK
```

Se `certify.py` < 100% ou o dry-run der FAIL, **não envie** — corrija primeiro.

---

## 4. Enviar de verdade (1 comando)

```bash
python submit/pipeline.py
```

O orquestrador roda 3 estágios idempotentes:
- **Bedrock**: envia packs de `marketplace-content/dist/` (pula IP bloqueado).
- **Roblox**: sobe os 100 itens do catálogo + prepara a experience.
- **Domínio**: claim/`--check` do FreeDomain.

Cada estágio captura falha e continua; o resumo final mostra `stages passed: 3/3`.
Rodar de novo é seguro (idempotente por nome/ID).

---

## 5. Automação total via GitHub Actions (CI)

Os workflows já existem em `.github/workflows/`. Para envio 100% automatizado
em nuvem, cadastre os **secrets do repositório** (Settings → Secrets):

| Secret | De onde vem |
|--------|-------------|
| `ROBLOX_API_KEY` | Open Cloud API key (passo 1.3) |
| `ROBLOX_GROUP_ID` | ID do grupo Roblox |
| `ROBLOX_EXPERIENCE_ID` | Universe ID da experience |
| `MS_TENANT_ID` / `MS_CLIENT_ID` / `MS_CLIENT_SECRET` / `MS_PARTNER_ID` | Partner Center (Bedrock) |
| `DP_EMAIL` / `DP_PASS` | DigitalPlat (domínio free) |

- `submit.yml` já traz o bloco "Real submission" **comentado**. Descomente-o e o
  envio real dispara por `workflow_dispatch` (botão "Run workflow") ou agenda.
- `freedomain.yml` roda o claim mensalmente (cron `0 6 1 * *`).
- `test.yml` / `build-mcpacks.yml` / `deploy-site.yml` cuidam de testes, build e site.

Com os secrets preenchidos, o envio roda sem você tocar no terminal.

---

## 6. Gate de qualidade

`python certify.py` executa 6 gates (testes, Bedrock, site, Roblox, domínio,
pipeline) e só deve chegar a **100%** antes do envio real. Ele é o "trava" que
impede submeter conteúdo não-compliant.

---

## 7. Realidade do recebimento (sem ilusão)

Envio automatizado **não é** pagamento. O dinheiro vem de **vendas reais**:
-publicar → compradores compram (Robux) → acumular **100.000 Robux ganhos**
(≈ US$ 350) → pedir saque DevEx → processador (Hyperwallet) → PayPal em dias
úteis. Leva semanas. Nenhuma automação antecipa esse prazo.

---

## 7b. Automação da wizard de envio com browser-use-ai

Tudo que é **repetitivo dentro da tela de submissão** (depois de logado) agora é
dirigido por `submit/browser_use_ai.py` (Playwright + decisor opcional via LLM do
`config.yaml`). Ele preenche título, descrição, termos de busca, categoria, faixa
etária, preço, faz upload do `.mcpack`, responde as declarações de produto
(Não/Não/Não/Não), responde o IARC e cola a URL de privacy — e **para antes do
"Submit for review"**.

```bash
python submit/browser_use_ai.py --dry-run        # gera + valida o plano (sem browser)
# 1) LOGIN MANUAL (você digita, bot só espera):
python submit/browser_use_ai.py --platform ms --capture-login --browser firefox
# 2) dirige a wizard com a sessão salva (para no gate):
python submit/browser_use_ai.py --platform ms --run --browser firefox
python submit/browser_use_ai.py --platform roblox --run --browser firefox --llm   # igual, com LLM
```

Pré-requisito para `--run`: uma sessão autenticada — gerada via `--capture-login`
(você loga à mão no Firefox aberto, fecha o browser, sessão salva em
`BROWSER_PROFILE_MS` / `sessions.partner_center_profile`) **ou** um arquivo de
cookies (`BROWSER_COOKIES_MS` / `sessions.cookies_file`). O script **nunca** faz
login/2FA/KYC — isso é ação humana. Sem sessão, ele recusa.

### Fluxo de UM comando (recomendado para uso diário)

Se quiser **abrir o navegador, colocar só os dados (login) e deixar o script
rodar o resto**, use `--auto`. Ele junta o login manual e a direção da wizard
num único comando — sem segundo passo:

```bash
# defina o perfil uma vez (pasta gravável; a sessão é salva aqui):
set BROWSER_PROFILE_MS=C:\Users\forrydev\AppData\Local\firefox-ms-profile
# abre o navegador -> você loga à mão -> aperta ENTER -> bot dirige a wizard:
python submit/browser_use_ai.py --platform ms --auto --browser firefox
# com LLM (preenche seletores dinâmicos do React):
python submit/browser_use_ai.py --platform roblox --auto --browser firefox --llm
```

O que acontece: o Firefox abre na tela de login → **você** digita e-mail/senha/2FA
(o bot nunca digita credenciais) → quando o portal estiver aberto, volte no
terminal e aperte **ENTER** → o bot dirige a wizard na MESMA sessão (título,
descrição, busca, categoria, faixa etária, preço, upload do `.mcpack`,
declarações, IARC, URL de privacidade) → **para antes do "Submit for review"** e
deixa o navegador aberto para você configurar o pagamento e clicar enviar.

Filtro de segurança (`is_blocked_step`): qualquer passo cujo rótulo mencione
pagamento/checkout/payout/PayPal/Wise/cartão/banco/2FA/verify/login/W-8BEN/CPF/CNPJ/
identidade/KYC/**submit for review** é **recusado e logado**. O plano só é válido se
termina num `human_gate`. Teste offline: `python submit/test_browser_use_ai.py`.

> O que continua 100% manual: criação de conta, KYC (W-8BEN), configuração do
> **método de pagamento** (PayPal/Wise/Payoneer) e o clique final "Submit for
> review" — exatamente como pedido ("deixar só configuração manual para pagamentos").



- [ ] Conta Roblox criada e verificada (você)
- [ ] DevEx habilitado + W-8BEN (CPF) + PayPal vinculado (você)
- [ ] API key Open Cloud criada; `ops/secrets.json` preenchido
- [ ] `python certify.py` → 100%
- [ ] `python submit/pipeline.py --dry-run` → GO
- [ ] Secrets do repo GitHub cadastrados (para CI)
- [ ] `submit.yml`: bloco "Real submission" descomentado
- [ ] Clicar "Run workflow" → envio automatizado completo
