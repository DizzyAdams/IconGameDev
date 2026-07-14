# Runbook Final — Envio para Aprovação (passos humanos)

Tudo que é automatizável já está verde (`python certify.py` → 100%, `python submit/pipeline.py --dry-run` → GO). O que falta abaixo é **ação humana por design** (ToS / KYC / pagamento). Não tem como bot fazer sem banir a conta e estornar pagamentos.

> Nunca cole senhas/CPF/chaves em chat ou em arquivo versionado. `ops/secrets.json` é gitignored.

## 0. Pré-voo (local, seguro)
```bash
python submit/check_secrets_status.py     # só FILLED/PLACEHOLDER, não vaza valor
python certify.py                          # deve dar 100%
python submit/pipeline.py --dry-run        # GO
```
Se `check_secrets_status.py` disser NOT READY, preencha os campos PLACEHOLDER em `ops/secrets.json` (arquivo local, nunca commitado).

## 1. Conta + KYC (você, uma vez)
- [ ] **Microsoft Partner Center** criada e aprovada (leve dias — comece cedo).
- [ ] **Roblox** (pessoa física ok) criada, idade + 2FA verificados.
- [ ] **W-8BEN / W-8BEN-E** preenchido no portal (TIN = CPF ou CNPJ). Sem isso, Microsoft retém 30%.

## 2. Método de pagamento (você — o "manual de pagamentos")
- [ ] **PayPal** ou **Wise** verificado e vinculado no portal de payout de cada plataforma.
- [ ] Confirme e-mail/contas bancárias conforme o portal pedir (2 micro-depósitos ou cartão).
- Isso é o único passo de pagamento; o bot não toca nele.

## 3. Login manual + dirigir a wizard até o gate (bot, Firefox)
```bash
# 3a) LOGIN MANUAL: abre o Firefox, VOCÊ digita usuário/senha/2FA, fecha o browser.
#     Sessão salva em sessions.partner_center_profile (ops/secrets.json).
python submit/browser_use_ai.py --platform ms --capture-login --browser firefox

# 3b) Bot dirige a wizard com a sessão salva e para no gate.
python submit/browser_use_ai.py --platform ms --run --browser firefox
```
O bot preenche título, descrição, termos, categoria, faixa etária, preço, upload do `.mcpack`, declarações (Não×4), IARC e URL de privacy — e **para no gate "Submit for review"**. O bot **nunca** digita sua senha nem faz login/KYC; ele só espera você fechar o browser no passo 3a. Qualquer passo de pagamento/login é recusado pelo filtro de segurança.

## 4. Submit final (você)
- [ ] Revise a oferta preenchida pelo bot.
- [ ] Confirme que o método de pagamento (passo 2) está vinculado.
- [ ] Clique **"Submit for review"**.

## 5. Roblox (catálogo)
```bash
python submit/submit_roblox.py --dry-run   # valida 100 itens
# com a API key em ops/secrets.json:
python submit/submit_roblox.py
```
Publicação da experience IconHub e troca dos IDs placeholder ficam no Roblox Studio (manual).

## Ordem recomendada
1. Conta PayPal/Wise (passo 2) — o que você citou.
2. MEI/CNPJ (se PJ) em paralelo (~5 dias).
3. Partner Center (passo 1) — aprovação leva dias.
4. Quando pronto: W-8BEN → `browser_use_ai.py --run` → você clica Submit.

## Guardrails (não contornar)
- Bot NUNCA: login, 2FA, W-8BEN, pagamento, "Submit for review".
- Filtro `is_blocked_step` recusa esses passos; `submit/test_browser_use_ai.py` valida (17 checks).
- Recebimento depende de vendas reais + ciclo DevEx/Payout (semanas), não da automação.
