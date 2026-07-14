# Certification Rollout — Sprints

Phased plan to reach Microsoft Store / Partner Program certification readiness.
Each sprint ends with a green `certification_readiness.py` improvement.

## Sprint 1 — Documentation completeness (done)
- [x] `00`–`07` compliance docs
- [x] `08-store-certification.md` (Store Policies mapping)
- [x] `INDEX.md` master index
- [x] Templates: privacy-policy, terms-of-use, age-rating-iarc, store-listing
- [x] `LICENSE` at repo root
- [x] `checks/certification_readiness.py` + `pre_submission_checklist.md`
- [x] `sprints/certification-rollout.md`

## Sprint 2 — IP hygiene on `dist/`  ✅ DONE
- [x] Moved 15 IP-blocked franchise `.mcpack` from `dist/` into `_franchise-archive/`
      (sources were already archived, so `safe-rename`/`build-all` cannot recreate them)
- [x] `python compliance/checks/certification_readiness.py` → `VERDICT: READY`
- [x] `python compliance/checks/submit_gate.py` → `GO`
- [ ] (Optional) Full structural audit on large dist/ (slow):
      `python marketplace-content/scripts/audit_compliance.py --pack-dir dist`

## Sprint 3 — Asset completeness
- [ ] Generate icons (256x256), thumbnails, 4–6 screenshots (1280x720), hero (1920x1080) for every submitted pack
- [ ] Fill `templates/store-listing.md` per pack (EN + PT-BR)
- [ ] Generate IARC rating certificates (`templates/age-rating-iarc.md`)

## Sprint 4 — Business & legal
- [ ] Finalize `templates/privacy-policy.md` + `templates/terms-of-use.md` (fill placeholders)
- [ ] Confirm CNPJ, W-8BEN, payment method in Partner Center
- [ ] Set privacy policy URL on store listings

## Sprint 5 — Pilot submission
- [ ] Submit first 3–5 safe packs (free/promo) per `04-submission-pipeline.md`
- [ ] Pass content review; capture feedback
- [ ] Scale submission using `audit_compliance.py` + `certification_readiness.py` gates

## Gate
`python compliance/checks/certification_readiness.py` must print `VERDICT: READY`
before any batch submission.
