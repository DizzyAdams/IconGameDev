# Domínio — IconMineMods (runbook de aprovação)

Marca canônica para domínio/email: **IconMineMods**. Conforme
`compliance/02-content-compliance.md`, o nome NÃO contém "Minecraft",
"Mojang" ou "Microsoft" — seguro para submissão. (Nota: alguns docs de
compliance usam "IconMyBedrockMods"; padronize a marca para **IconMineMods**
em domínio/email.)

CNPJ: já obtido (preencha `cnpj` em `domains.config.json`).

## Variações de domínio (priorizadas)

| Prioridade | Domínio | Motivo |
|-----------|---------|--------|
| 1 (registrar) | `iconminemods.com` | primário, universal, confiável |
| 1 (registrar) | `iconminemods.org` | proteção de marca / perfil org |
| 1 (registrar) | `iconminemods.com.br` | primário Brasil — **CNPJ habilita .com.br no Registro.br** |
| 1 (registrar) | `www.iconminemods.com/.org/.com.br` | redirect canônico (ver `vercel.json`) |
| 2 (opcional) | `iconminemods.net` | proteção de marca |
| 2 (opcional) | `iconminemods.tech` | combina o email `iconMine.tech` existente |
| 3 (fallback) | `geticonminemods.com`, `playiconminemods.com`, `iconminemods.store` | se os acima estiverem tomados |

Regra de naming (de `domain-name-brainstormer`): curto, sem hífens, pronunciável,
sem números, registrar .com + variação para proteger a marca.

## Registradores

- **.com.br**: Registro.br (exige CNPJ — já temos). ~R$ 40/ano.
- **.com / .org**: Namecheap / Gandi / Porkbun. ~US$ 10–15/ano (.com), ~US$ 10/ano (.org).

## DNS (pronto para importar — ver `operations/dns/iconminemods.zone`)

- Apex `A` → `76.76.21.21` (Vercel anycast)
- `www` `CNAME` → `cname.vercel-dns.com.`
- `MX` → Microsoft 365 (`iconminemods-com.mail.protection.outlook.com.`, prio 10)
- `TXT` → SPF, DKIM (seletor da M365), DMARC, e verificação Microsoft 365 / Search Console

Vercel faz http→https e IPv6 no edge automaticamente; não é preciso AAAA manual.

## Passos para ficar 100% funcional

1. Registrar `iconminemods.com`, `.org`, `.com.br` nos registradores acima.
2. No projeto Vercel: adicionar os domínios (também declarados em `vercel.json`).
3. Apontar DNS conforme a zona (`operations/dns/iconminemods.zone`).
4. Aguardar propagação + certificado HTTPS automático da Vercel.
5. Adicionar registros TXT de verificação (M365, Search Console, Bing).
6. Configurar email corporativo (`admin@iconminemods.com`) na M365.
7. Validar: `https://iconminemods.com` abre o site; `www.` redireciona; HTTPS ativo.

## Checklist de envio p/ aprovação

- [ ] Domínios registrados e DNS propagados
- [ ] HTTPS ativo em todos os domínios
- [ ] `www` → apex (redirect 301)
- [ ] Email corporativo funcionando (M365)
- [ ] TXT de verificação aplicados
- [ ] Privacy Policy + Terms apontando `iconminemods.com` (ver `compliance/templates/`)
- [ ] CNPJ preenchido em `domains.config.json` e documentos legais
