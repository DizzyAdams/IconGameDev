# Store Certification — Microsoft Store Policies Mapping

This document maps the **formal Microsoft Store Policies** (the certification
bar every Marketplace offer must clear) to our Bedrock content pipeline. The
other `0x-*.md` docs cover the *Partner Program* and *technical/content*
rules; this one covers the *Store certification* dimensions that are reviewed
per offer before publish.

> Source of truth: Microsoft Store Policies (the "Store Policies" shown in
> Partner Center during submission) and the IARC age-rating system Microsoft
> uses. Treat this as guidance aligned to those policies, not legal advice.

## 1. Product type & declarations

During submission you declare the product type and answer **product
declarations** (e.g. does the product access limited-capability APIs, collect
data, show ads). Our packs are content-only:

| Declaration | Our answer |
|-------------|------------|
| Collects user data? | **No** (the `.mcpack` itself collects nothing) |
| Shows third-party ads? | **No** |
| Uses restricted capabilities? | **No** |
| Account required? | **No** |
| Targets children / COPPA? | **No** (rated E, family-friendly, but not a dedicated child product) |

If the accompanying **website** or **affiliate program** collects data
(emails, referrals), that is covered separately by `templates/privacy-policy.md`
and the Store listing's privacy policy URL field.

## 2. Content rating (IARC)

Microsoft uses the **IARC** age-rating system. You complete a short
questionnaire; a rating certificate is generated automatically.

- Most skin/texture packs → **Everyone (3+)**
- Packs with fantasy combat themes (swords/armor) → **Everyone 10+** if any
  "fantasy violence" descriptors apply; otherwise **Everyone (3+)**
- Worlds with mild scare themes → **Everyone 10+**

See `templates/age-rating-iarc.md` for the questionnaire + certificate template.
Never submit without a rating certificate — uncertified offers are rejected.

## 3. Age-appropriate content (ESRB E / PEGI)

The Store requires content appropriate to the declared rating:

- [ ] No realistic violence, blood, or gore
- [ ] No sexual content or nudity
- [ ] No alcohol, tobacco, or drug references
- [ ] No profanity in names/descriptions
- [ ] No hate speech or discriminatory content
- [ ] Skull/fantasy/skeleton motifs are acceptable (Minecraft canon)

Enforced by `02-content-compliance.md` and `run_compliance.py` (blocklist).

## 4. Metadata accuracy

Store Policies require listings to be accurate and not misleading:

- [ ] Title matches `manifest.json` header name (≤ 60 chars)
- [ ] Description is 100–300 chars, accurate, no false claims
- [ ] Screenshots depict **actual** in-game content
- [ ] No "on sale"/price language in description
- [ ] No external links (Discord, etc.) in description
- [ ] No "please rate 5 stars" manipulation

Template: `templates/store-listing.md`. Validation: `04-submission-pipeline.md`.

## 5. Accessibility

Store certification asks for accessibility info. Our content is inherently
accessible (visual skins/textures, no audio dependence, no input requirements
beyond the game). Declare:

- [ ] No additional hardware required
- [ ] No speech/audio dependency
- [ ] Text in UI is game-rendered (no separate accessibility burden)
- [ ] Color-blind safe: avoid encoding meaning by color alone in icon art

Add an **accessibility note** to the store listing where the field exists.

## 6. Localization

A single EN listing is certifiable; localized listings improve approval across
markets (PT-BR is our priority market). Provide `store_listing.md` per locale
with title + description + 5 search terms. Descriptions must be translated, not
machine-garble.

## 7. System requirements

Declare minimum Bedrock version via `min_engine_version` (≥ 1.20.0, see `01`).
No platform-exclusive assets; packs work on Win10/11, mobile, console.

## 8. Advertising & monetization

- No in-product ads (Minecoin pricing only).
- No "loot box"/gamble mechanics.
- Pricing tiers follow `07-pricing-strategy.md` and valid Minecoin tiers.

## 9. Intellectual property

The hardest certification failure. Microsoft rejects on trademark/copyright.

- [ ] No franchise names in any published pack (`safe-rename.py` + `audit_compliance.py` IP scan)
- [ ] Franchise *inspired* packs live only in `_franchise-archive/` and are never submitted
- [ ] Original theme names only

## 10. Pre-certification gate

Run, in order, before every submission:

```bash
cd marketplace-content
python scripts/safe-rename.py          # ensure safe names (idempotent)
python scripts/build-all.py            # rebuild dist/ from source
python scripts/audit_compliance.py --pack-dir dist   # structural + UUID + IP
cd ..
python compliance/checks/certification_readiness.py   # repo-level readiness
```

Only submit offers when `certification_readiness.py` prints `VERDICT: READY`
and `audit_compliance.py` prints `VERDICT: CLEAN`.
