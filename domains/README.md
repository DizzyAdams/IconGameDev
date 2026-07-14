# IconMineMods — Free Domain (DigitalPlat FreeDomain)

## Free vs Paid
DigitalPlat **FreeDomain** provides **free** subdomains under these TLDs **only**:

- `.dpdns.org`
- `.us.kg`
- `.qzz.io`
- `.xx.kg`
- `.qd.je`

It does **NOT** offer free `.com` / `.net` / `.org`. Those are **paid** and must be
registered at a registrar (Porkbun / Namecheap / Gandi, or Registro.br with a CNPJ
for `.com.br`). In `../domains.config.json`, `iconminemods.com` is marked
`paid-to-register` for exactly this reason.

Our free primary is **`iconminemods.dpdns.org`** (fallback: `iconminemods.us.kg`).

## Privacy / Contact URL
Lives at: **https://iconminemods.dpdns.org/privacy**

This is wired into `../domains.config.json` as the top-level `privacy_url` and
is served by the Vercel-hosted Next.js app.

## How to claim

### Option A — script (best-effort, stdlib only)
```bash
export DP_EMAIL="you@example.com"
export DP_PASS="yourpassword"
python domains/freedomain_claim.py --claim
python domains/freedomain_claim.py --check   # exits 0 when a free domain exists
```
`--claim` writes `domains/claimed.json` with `status: claimed` if the dashboard
API accepted the request, or `status: planned` (manual: true) if it could not
auto-register. `--check` exits 0 whenever a free domain with status
`claimed`/`planned` is present. It is idempotent: re-running is a no-op.

### Option B — manual (always works)
1. Go to https://dash.domain.digitalplat.org/
2. Register / log in (same `DP_EMAIL` / `DP_PASS`).
3. Claim `iconminemods.dpdns.org` (or `iconminemods.us.kg`).
4. Set DNS — see `domains/dns_records.json`:
   - A `@` → `76.76.21.21`
   - CNAME `www` → `cname.vercel-dns.com`
   - TXT `@` → verification string from the dashboard
5. Run `python domains/freedomain_claim.py --check`.

## Pointing the paid `.com` at the same site later
Once `iconminemods.com` is registered (paid registrar), set the **same** DNS
records as `domains/dns_records.json` in that registrar:
- A `@` → `76.76.21.21`
- CNAME `www` → `cname.vercel-dns.com`

Then add the domain in Vercel and assign it as the production domain for the
Next.js app. The free `.dpdns.org` keeps serving `/privacy` and the contact
pages in the meantime, so the privacy URL never breaks during the transition.
