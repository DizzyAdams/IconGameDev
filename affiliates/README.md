# Affiliates

Tracks referral partners and computes their monthly commission payouts.

Commission rate is **15%** of referred revenue (`COMMISSION_RATE = 0.15`).

Run:
1. `python compute_payouts.py --sample` — writes `affiliates.example.csv` (5 sample rows).
2. `python compute_payouts.py` — reads `affiliates.csv` (or the example) and writes `payouts.json`.

Output `payouts.json` includes `total_commission_usd` and per-affiliate `commission_usd`.
