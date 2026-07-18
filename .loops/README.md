# Loop Ecosystem — IconMineMods Affiliation & Platform Engine

Bounded, observable loops that compound toward:
"largest Roblox + Minecraft Bedrock skin/affiliate platform, best Roblox client, $1M skins."

Every loop is local + reversible. None sends external messages, pays out, or
submits to a platform without explicit user approval (gated inside each prompt).

## Operational loops (cron jobs)
| loop | schedule | reads / acts on | stop rule |
|------|----------|-----------------|-----------|
| roblox-approval-hardening | every 6h | certify.py --all | 100% green or stagnant |
| roblox-catalog-compliance-growth | daily 06:00 | roblox-ugc tools | clean + no new issue or stagnant |
| affiliate-payout-integrity | daily 07:00 | compute_payouts.py | ledger correct |
| affiliate-funnel-recruitment | daily 08:00 | /partner page | no gap or stagnant |
| affiliate-revenue-tracker | daily 09:00 | affiliates.csv | $1M reached or no-op |
| pipeline-volume-scaling | every 12h | ops/run_daily.py | batch cap (2000) or stagnant |
| bedrock-roblox-submission-readiness | daily 05:00 | roblox_checks + submit_gate --audit | gates green or stagnant |
| ip-compliance-watchdog | every 3h | audit_compliance.py IP scan | clean (silent) or match reported |
| affiliate-agency-growth | daily 10:00 | /agencias + /api/agencies | no gap or stagnant |
| catalog-seo-discovery | daily 11:00 | SEO/GEO crawl of /catalog /roblox /partner /agencias | no high-impact gap or stagnant |
| submission-lifecycle-tracker | daily 12:00 | submission state | all approved or no-op |

## State files (agent-written)
- certify.md, catalog.md, payout.md, funnel.md, revenue.md
- volume.md, submission.md, ip-watch.md, agency.md, seo.md, submissions.md

## Hard guardrails (non-negotiable)
- IP_BLOCKED themes (anime/kawaii/franchises) are quarantined — never add.
- No payout, no external message, no platform submission without user approval.
- A FAIL/timeout is never reported as approved.
- Source of truth for inventory: out/inventory_report.json (per run_daily).

## How to become "the biggest"
The $1M and the platform lead come from THROUGHPUT + COMPLIANCE + RECRUITMENT:
1. pipeline-volume-scaling raises batch only while certify stays green.
2. ip-compliance-watchdog keeps the catalog submission-safe 24/7.
3. affiliate-funnel-recruitment + affiliate-agency-growth widen demand.
4. submission-lifecycle-tracker shows what is actually live on Roblox/Bedrock.
5. affiliate-revenue-tracker is the only number that proves $1M progress.

To accelerate revenue for real, the user must authorize: affiliate/agency
outreach (external messages) and real platform submission. Both are gated.
