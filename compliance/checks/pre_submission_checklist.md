# Pre-Submission Checklist (Final Gate)

Run this human checklist for **every** offer before clicking "Submit for
review" in Partner Center. Automated gates live in `certification_readiness.py`
and `scripts/audit_compliance.py`.

## A. Package integrity
- [ ] `manifest.json` present, valid JSON, `format_version: 2`
- [ ] Header + module UUIDs are valid v4 and unique across all packs
- [ ] `min_engine_version` >= [1, 20, 0]
- [ ] `skins.json` present for skin packs; `level.dat` for worlds
- [ ] All referenced PNGs exist and are RGBA, correct dimensions
- [ ] Pack file size < 10 MB (ideally < 5 MB)

## B. IP & content
- [ ] No trademarked/franchise names in pack name or description
- [ ] No IP-blocked names in `dist/` (see `audit_compliance.py` IP scan)
- [ ] ESRB E / PEGI 3 (or E10+ / PEGI 7 where applicable)
- [ ] No profanity, violence, drugs, hate speech
- [ ] Screenshots match actual content

## C. Store metadata
- [ ] Title ≤ 60 chars, matches manifest name
- [ ] Description 100–300 chars, accurate, no false claims
- [ ] 5 search terms; category set
- [ ] Icon 256x256, hero 1920x1080, 4–6 screenshots 1280x720
- [ ] IARC rating certificate generated
- [ ] Accessibility note provided

## D. Business & legal
- [ ] Partner account active; W-8BEN on file
- [ ] Payment method (Wise/PayPal) configured
- [ ] Privacy policy URL set (if website/affiliate collects data)
- [ ] Pricing within valid Minecoin tiers (`07`)

## E. Automation verdict
- [ ] `python scripts/audit_compliance.py --pack-dir dist` → `VERDICT: CLEAN`
- [ ] `python compliance/checks/certification_readiness.py` → `VERDICT: READY`

Only submit when **all** boxes are checked.
