# W-8BEN — Template pré-preenchido (Microsoft Partner Center)

> A Microsoft (EUA) paga via Marketplace. Sem este formulário, retém **30%** de
> imposto na fonte; com ele, a alíquota cai para **0%–15%** (tratado Brasil–EUA).
> Válido por **3 anos**. Preencha no Partner Center (ou envie PDF assinado).

## Qual formulário usar

| Situação | Formulário | TIN (Brasil) |
|-----------|-----------|---------------|
| Pessoa física (sem CNPJ) | **W-8BEN** | CPF |
| MEI / CNPJ (pessoa jurídica) | **W-8BEN-E** | CNPJ |

> Recomendado: abra MEI/CNPJ (ver `03-business-compliance.md`) e use **W-8BEN-E**
> com o CNPJ. Abaixo o modelo W-8BEN (PF). Para W-8BEN-E, os campos de entidade
> substituem os pessoais.

## W-8BEN — campos (modelo)

```
Parte I — Identificação do beneficiário
  Nome completo (conforme CPF): <SEU NOME COMPLETO>
  Nacionalidade: Brazilian
  Endereço residencial: <RUA, NÚMERO, CIDADE, ESTADO, CEP, BRASIL>
  E-mail: bussins@iconMine.tech
  Data de nascimento: <AAAA-MM-DD>
  TIN (Brazil): CPF <XXX.XXX.XXX-XX>        <-- obrigatório p/ reduzir retenção
  Tipo de beneficiário: Individual

Parte II — Reivindicação de tratado (Brasil–EUA)
  País de residência fiscal: Brazil
  Artigo do tratado: Article 7 (Business Profits) / Article 12 (Royalties)
  Percentual de redução reivindicado: 0%–15% sobre royalties

Parte III — Certificação
  Assinatura: ___________________________
  Data: <AAAA-MM-DD>
  Nome impresso: <SEU NOME COMPLETO>
```

## Como enviar

1. No Partner Center → **Account → Tax profile → New tax form**.
2. Selecione **W-8BEN** (ou W-8BEN-E).
3. Preencha os campos acima (use CPF/CNPJ como TIN).
4. Assine eletronicamente e envie.
5. Status deve ficar **"Approved"** antes da primeira submissão de oferta.

## Notas

- O CPF é exigido pela Receita Federal e usado aqui como TIN perante o IRS.
- Guarde cópia PDF em `docs/legal/w8ben.pdf`.
- Renove a cada 3 anos (o Partner Center avisa quando expirar).
