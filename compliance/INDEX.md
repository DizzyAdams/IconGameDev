# Compliance Index — Microsoft Partner Program & Store Certification

Single source of truth that ties together every compliance document, template,
check and automation script in this repo.

## Document map

| Doc | Covers |
|-----|--------|
| `00-microsoft-partner-requirements.md` | Partner Program eligibility, portfolio, business, technical, content, submission, ongoing compliance |
| `01-technical-compliance.md` | manifest v2 schema, UUIDs, file structure, PNG specs, skins.json, versioning |
| `02-content-compliance.md` | EULA/IP risk, age rating (ESRB), description rules, screenshots, pricing, cultural sensitivity |
| `03-business-compliance.md` | CNPJ/MEI, W-8BEN, payments, LGPD/GDPR, legal agreements, accounting |
| `04-submission-pipeline.md` | Pre-submission checklist, build pipeline, Partner Center flow, review |
| `05-marketing-assets-guide.md` | Icons, thumbnails, screenshots, hero art, SEO, branding, seasonal |
| `06-qa-guide.md` | Automated + manual QA, content review, performance, device testing |
| `07-pricing-strategy.md` | Price tiers, revenue split, Minecoin tiers, BR pricing |
| `08-store-certification.md` | **Formal Microsoft Store Policies mapping** (content rating/IARC, accessibility, metadata accuracy, product declarations, localizations, advertising) |
| `09-receita-50k.md` | Consolidated US$ 50k revenue plan: readiness verdict, volume, competitive pricing, governance, remaining blockers, go/no-go gate |

## Templates (`compliance/templates/`)

- `privacy-policy.md` — LGPD + GDPR + Microsoft Store privacy policy (fill-in)
- `terms-of-use.md` — Terms of Use / EULA for the store page and website
- `age-rating-iarc.md` — IARC questionnaire guidance + rating certificate template
- `store-listing.md` — Store listing metadata template (EN/PT) for Partner Center

## Checks (`compliance/checks/`)

- `pre_submission_checklist.md` — Final human-run gate before every submission
- `certification_readiness.py` — Dependency-free readiness scanner (artifacts + IP scan)
- `submit_gate.py` — Single go/no-go for first-try approval (`[--audit]` runs heavy structural check)
- `readiness_report.json` — Generated output of the readiness scanner
- `audit_dist.log` / `audit_dist.err` — Output of the full structural audit over `dist/`

## Sprints (`compliance/sprints/`)

- `certification-rollout.md` — Phased plan to reach certification readiness

## Automation (reuse, do not duplicate)

These scripts already enforce pack-level compliance — the docs above describe
the *policy*, the scripts enforce the *structure*:

- `marketplace-content/scripts/audit_compliance.py` — structural + UUID v4 + IP scan on `dist/`
- `marketplace-content/scripts/run_compliance.py` — validator + QA agent + blocklist + product-type allowlist
- `marketplace-content/scripts/safe-rename.py` — renames franchise-inspired packs to safe names
- `marketplace-content/scripts/build-all.py` — rebuilds `.mcpack` from source after renames

## Microsoft Store certification checklist

Each certification requirement maps to where it is satisfied:

| Certification requirement | Satisfied by |
|---------------------------|--------------|
| Valid package & manifest (format_version 2) | `01`, `audit_compliance.py`, `run_compliance.py` |
| Unique, valid v4 UUIDs | `01`, `audit_compliance.py` |
| No IP / trademark infringement | `02`, `safe-rename.py`, `audit_compliance.py` (IP scan) |
| Age rating assigned (ESRB E / IARC) | `02`, `08`, `templates/age-rating-iarc.md` |
| Content rating certificate (IARC) | `08`, `templates/age-rating-iarc.md` |
| Accessibility declarations | `08` |
| Accurate metadata (title/desc/keywords) | `04`, `05`, `templates/store-listing.md` |
| Required assets (icon/thumb/screenshots/hero) | `01`, `05` |
| Privacy policy (if data collected) | `03`, `templates/privacy-policy.md` |
| Terms of use | `03`, `templates/terms-of-use.md` |
| Localized listings | `04`, `templates/store-listing.md` |
| Pricing within policy | `07` |
| US$ 50k revenue target | `07`, `09` |
| Code license present | `LICENSE` |

## How to verify readiness

```bash
# 1. Pack-level structural + IP audit
cd marketplace-content
python scripts/audit_compliance.py --pack-dir dist

# 2. Policy + QA orchestration
python scripts/run_compliance.py --pack-dir <dir> --require-thumbnails --require-screenshots

# 3. Repo-level certification readiness (artifacts + IP scan)
cd ..
python compliance/checks/certification_readiness.py
```

Verdict is `READY` only when all required artifacts exist and `dist/` contains
no IP-blocked pack names.
