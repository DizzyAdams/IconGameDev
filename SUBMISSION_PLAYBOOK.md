# Submission Playbook — Microsoft Partner Center (passos humanos)

Este é o único documento de **ação manual** que resta. Tudo técnico/compliance
já está em `VERDICT: READY` / `VERDICT: CLEAN` (ver `python certify.py`).

> **Status automatizado: 100%** — dist/ (10.017 packs) audita CLEAN, testes
> verdes, site compila, `submit_gate --audit` → GO.

## 0. Pré-requisitos (já prontos — não mexer)

- [x] `python certify.py` → **AUTOMATED SCORE: 100% (3/3)**
- [x] `dist/` com 10.017 packs, `VERDICT: CLEAN`
- [x] Templates preenchidos em `compliance/templates/`
- [x] Site `website-next` builda (`npm run build`)

## 1. Conta Microsoft Partner Center

1. Acesse https://partner.microsoft.com → **Sign up**.
2. Conta Microsoft (Hotmail/Outlook ou corporativa).
3. Escolha o programa **Microsoft Store / Minecraft Marketplace** (Partner).
4. Aguarde aprovação da conta (pode levar dias — **faça este passo primeiro**).

## 2. CPF e CNPJ (opcional, recomendado: MEI)

- **CPF:** obrigatório para pessoa física (já deve ter o seu).
- **CNPJ via MEI** (recomendado para vender como PJ):
  1. https://www.gov.br/mei → "Formalize-se".
  2. CNAE **7319-0/01** (Criação de jogos eletrônicos).
  3. Nome empresarial: `IconMineMods`.
  4. Custo: grátis; CNPJ em ~5 dias.
  5. Mensalidade MEI: ~R$ 73 (INSS+ISS).
  > Projeção do projeto (~R$ 850k/ano) **ultrapassa** o limite MEI (R$ 81k/ano);
  > após 6–12 meses, faça upgrade para **ME** ou **EPP**. Por enquanto MEI libera
  > o CNPJ para o W-8BEN-E.

## 3. Conta PayPal (ou Wise) — o passo que você citou

> Esta é a ação que **você** precisa fazer; eu não posso criar a conta.

1. https://www.paypal.com/br → **Criar conta** → tipo **Pessoa Física ou
   Empresarial** (se tiver CNPJ, use Empresarial).
2. Confirme e-mail e vincule um **cartão ou conta bancária** (Nubank/PJ ou Inter).
3. Verifique a conta (PayPal pede documento e confirmação de 2 micro-depósitos
   ou cartão).
4. Anote o e-mail da conta — será usado no Partner Center (payout) e no
   programa de afiliados.
5. Alternativa recomendada p/ melhores taxas de câmbio USD→BRL: **Wise**
   (mid-market + 0,5%). O projeto suporta Wise/PayPal/Payoneer.

## 4. W-8BEN (tributário EUA)

- Use `compliance/templates/w8ben.md` (pré-preenchido).
- No Partner Center → **Account → Tax profile** → preencha CPF/CNPJ como TIN.
- Sem isso, Microsoft retém 30%; com ele, 0%–15%.
- Status deve ficar **Approved** antes de submeter ofertas.

## 5. IARC (classificação etária)

- No momento da submissão de cada oferta, o Partner Center abre o questionário
  IARC. Nossas respostas padrão estão em
  `compliance/templates/age-rating-iarc.md`:
  - Violência: Não / só fantasia → **ESRB E** (ou **E10+** p/ combate/fantasia)
  - Linguagem / Nudez / Drogas / Apostas / Ódio: **Não**
  - Medo: leve (alguns mundos)
- Ao concluir, o certificado IARC é gerado **automaticamente**. **Nunca** submeta
  oferta sem o certificado — é rejeitada na certificação.

## 6. URL de Privacy Policy

- Se o site/afiliados coletam dados: publique `compliance/templates/privacy-policy.md`
  em `https://iconmine.tech/privacy` e cole a URL no campo da oferta.
- Os pacotes em si não coletam dados (pode marcar "não coleta" na declaração).

## 7. Submeter a oferta (por pacote / lote)

1. No Partner Center → **Marketplace → Minecraft → Create offer**.
2. Preencha metadata usando `compliance/templates/store-listing.md`
   (título ≤60, descrição 100–300, 5 termos de busca, ícone 256×256, hero
   1920×1080, 4–6 screenshots 1280×720).
3. Faça upload do `.mcpack` de `dist/`.
4. Responda as declarações de produto: coleta de dados = **Não**, anúncios = **Não**,
   recursos restritos = **Não**, conta obrigatória = **Não**.
5. Gere o certificado IARC (passo 5).
6. **Submit for review**.
7. Repita por oferta (automatizar em lote é o próximo passo do pipeline).

## 8. Checklist final antes de clicar "Submit"

- [ ] Conta Partner aprovada
- [ ] CPF (e CNPJ/MEI se PJ) em mãos
- [ ] Conta PayPal/Wise criada e verificada
- [ ] W-8BEN aprovado no Partner Center
- [ ] IARC gerado por oferta
- [ ] Privacy policy URL (se coleta dados)
- [ ] `python certify.py` ainda dá **100%**
- [ ] Preenchido o store listing de cada oferta

## Ordem recomendada para hoje

1. Criar conta PayPal (item 3) — o que você citou.
2. Abrir MEI/CNPJ (item 2) em paralelo (online, ~5 dias).
3. Criar conta Partner Center (item 1) — aprovação leva dias, comece já.
4. Quando tudo acima pronto: W-8BEN (4) → IARC (5) → Submit (7).

## 9. Automação disponível (este pacote)

O envio manual virou pipeline reproduzível (preencha `ops/secrets.json` com os
dados reais — CNPJ, credenciais Microsoft/Roblox/FreeDomain):

1. **Domínio grátis** — `python domains/freedomain_claim.py --claim` registra
   `iconminemods.dpdns.org` (FreeDomain; `.com` é pago à parte). Use a URL
   `https://iconminemods.dpdns.org/privacy` na declaração de privacidade.
   Mantemos o **`.org` grátis até subir o projeto**; o `.com`/`.org` pagos ficam
   para depois do lançamento (estratégia em `domains.config.json`).
2. **Templates com CNPJ** — `python ops/render_templates.py` injeta o CNPJ/razão
   social nos templates de compliance (W-8BEN-E, privacy, terms, store listing).
3. **Submissão** — `python submit/pipeline.py --dry-run` valida tudo (Bedrock +
   Roblox + domínio) e imprime `DRY-RUN OK`; `python submit/pipeline.py` envia de
   verdade (precisa das credenciais nos secrets).
4. **CI** — `.github/workflows/freedomain.yml` e `submit.yml` executam claim/submit
   por segredo (DP_EMAIL/DP_PASS, MS_*, ROBLOX_*).
5. **Certificação** — `python certify.py` roda 6 gates e fecha em 100% automático.
