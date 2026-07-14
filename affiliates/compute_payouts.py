#!/usr/bin/env python3
"""Compute affiliate commissions (15%) -> payouts.json. Stdlib only."""
import csv
import json
import os
import sys
from datetime import datetime, timezone

COMMISSION_RATE = 0.15
HERE = os.path.dirname(os.path.abspath(__file__))
MAIN_CSV = os.path.join(HERE, "affiliates.csv")
EXAMPLE_CSV = os.path.join(HERE, "affiliates.example.csv")
PAYOUTS = os.path.join(HERE, "payouts.json")


def write_sample():
    rows = [
        ("alice", 12, 340.50),
        ("bob", 5, 120.00),
        ("carol", 30, 980.75),
        ("dave", 8, 255.20),
        ("erin", 3, 75.00),
    ]
    with open(EXAMPLE_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["handle", "referrals", "revenue_usd"])
        for h, r, rev in rows:
            w.writerow([h, r, f"{rev:.2f}"])


def load_rows():
    if os.path.exists(MAIN_CSV):
        path = MAIN_CSV
    elif os.path.exists(EXAMPLE_CSV):
        print(f"hint: {MAIN_CSV} missing; using {EXAMPLE_CSV}")
        path = EXAMPLE_CSV
    else:
        print(f"hint: no affiliates.csv found. Run: python compute_payouts.py --sample")
        return []
    with open(path, newline="") as f:
        return [r for r in csv.DictReader(f)]


def main():
    if "--sample" in sys.argv:
        write_sample()
        print(f"wrote {EXAMPLE_CSV}")
        return
    rows = load_rows()
    out = []
    total = 0.0
    for r in rows:
        rev = float(r["revenue_usd"])
        comm = round(rev * COMMISSION_RATE, 2)
        total += comm
        out.append({
            "handle": r["handle"],
            "referrals": int(r["referrals"]),
            "revenue_usd": round(rev, 2),
            "commission_usd": comm,
        })
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_commission_usd": round(total, 2),
        "affiliates": out,
    }
    with open(PAYOUTS, "w") as f:
        json.dump(data, f, indent=2)
    print(f"total commission: ${round(total, 2):.2f}")


if __name__ == "__main__":
    main()
