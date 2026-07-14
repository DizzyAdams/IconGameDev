# Business Compliance — CNPJ, Tax, Legal

## 1. Brazil Business Registration (CNPJ)

### Steps to Register MEI (Microempreendedor Individual)
1. Go to https://www.gov.br/mei
2. Click "Formalize-se"
3. Select CNAE: **7319-0/01** (Criação de jogos eletrônicos)
   - Alternative: 6201-5/01 (Desenvolvimento de programas)
4. Choose business name: "IconMyBedrockMods"
5. Provide personal data (CPF, RG, address)
6. Estimated cost: R$ 0 (free for MEI)
7. Time: 30 minutes online, CNPJ in ~5 days
8. Monthly fee: R$ 67,93 (INSS) + R$ 5 (ISS) = ~R$ 73/mo

### After CNPJ Issued
- [ ] Get CNPJ number
- [ ] Get DAS (monthly tax payment slip)
- [ ] Open business bank account (PJ)
- [ ] Register for NFe (nota fiscal eletrônica)
- [ ] Get digital certificate (A1 or A3)

### Tax Responsibilities
- Monthly: Pay DAS (~R$ 73)
- Yearly: Declare IRPF
- Quarterly: Declare Simples Nacional
- Revenue limit: R$ 81.000/year for MEI
- Our projected $157k/yr = ~R$ 850k/yr — **exceeds MEI limit**
- After 6 months: Need to upgrade to ME (Microempresa)

### Upgrade Path
- MEI: up to R$ 81k/yr
- ME (Microempresa): up to R$ 360k/yr
- EPP (Empresa de Pequeno Porte): up to R$ 4.8M/yr
- With $157k/yr = ~R$ 850k/yr → need EPP

## 2. International Tax Compliance

### For Brazil → Microsoft (US)
- Fill **W-8BEN** form (not US citizen)
- This reduces US withholding tax to 0% or 15%
- Microsoft pays gross minus 30% if no W-8BEN
- W-8BEN valid for 3 years

### Required Documents for Microsoft
- [ ] W-8BEN form (signed)
- [ ] CNPJ registration proof
- [ ] Business address proof
- [ ] Bank account for payments (international wire)
- [ ] Partner agreement (provided by Microsoft)

## 3. Payment Setup

### Options for Brazil
| Method | Fee | Time |
|--------|-----|------|
| PayPal | 2.5-4% + fix | 1-3 days |
| Payoneer | 1-2% | 2-5 days |
| Wise (TransferWise) | 0.5-1% | 1-2 days |
| Wire transfer | $15-50 | 3-7 days |

**Recommended**: Wise (best rates for BRL conversion)

### Currency Conversion
- Microsoft pays in USD
- Need to convert to BRL
- Wise offers mid-market rate + 0.5%
- Bank wire: 3-5% above mid-market
- PayPal: 3-4% above mid-market

## 4. Revenue Thresholds

| Level | Monthly Revenue | Annual |
|-------|----------------|--------|
| Survival | $400 | $4,800 |
| Part-time | $2,000 | $24,000 |
| Full-time | $5,000 | $60,000 |
| Studio | $13,000 | $157,000 |

Our projection: $13,153/mo = Studio level

## 5. Legal Agreements

### Need to Create
- [ ] Terms of Service (for website)
- [ ] Privacy Policy (LGPD + GDPR)
- [ ] Refund Policy
- [ ] Cookie Policy
- [ ] Content License Agreement
- [ ] Collaborator Agreement (if hiring)

### LGPD Requirements (Brazil)
- Data processing register
- User consent collection
- Data subject rights (access, delete, port)
- Data breach notification procedure
- DPO (Data Protection Officer) appointment
- Privacy notice in Portuguese

## 6. Business Bank Account

### Options for Brazil
- **Nubank PJ**: Free, digital, no monthly fee
- **Banco do Brasil**: Traditional, has fees
- **Caixa**: Government bank, low fees
- **Inter PJ**: Free, digital, international transfers

### Recommended Setup
1. Nubank PJ (daily operations)
2. Wise (receive USD from Microsoft)
3. Monthly transfer: Wise → Nubank

## 7. Monthly Accounting Checklist

- [ ] Pay DAS (when MEI)
- [ ] Record all Marketplace sales
- [ ] Track expenses (tools, hosting, software)
- [ ] Save 15-20% for taxes
- [ ] Review currency exchange rates
- [ ] Update financial spreadsheet
- [ ] Backup all invoices

## 8. Documents Folder Structure

```
docs/
├── legal/
│   ├── cnpj.pdf
│   ├── w8ben.pdf
│   ├── partner-agreement.pdf
│   ├── terms-of-service.md
│   ├── privacy-policy.md
│   └── refund-policy.md
├── financial/
│   ├── revenue-tracker.csv
│   ├── expense-tracker.csv
│   ├── monthly-das.pdf
│   └── tax-declarations/
├── contracts/
│   ├── collaborator-agreements/
│   └── licensing/
└── identity/
    ├── business-card.pdf
    ├── logo-full.png
    └── brand-guidelines.md
```
