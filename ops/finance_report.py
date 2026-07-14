#!/usr/bin/env python3
"""Consolidated monthly revenue view across channels. Stdlib only, no network."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AVG_NET_PER_PACK_USD = 0.70

BEDROCK_DIR = os.path.join(ROOT, "submission_mcpacks")
ROBLOX_JSON = os.path.join(ROOT, "roblox-ugc", "catalog", "roblox_catalog.json")
AFFILIATE_JSON = os.path.join(ROOT, "affiliates", "payouts.json")
EPIC_JSON = os.path.join(ROOT, "epic", "maps.json")

# Epic takes a 12% cut on Fortnite Creative / Fab; we keep the rest.
EPIC_CUT = 0.12


def bedrock_monthly():
    if not os.path.isdir(BEDROCK_DIR):
        return 0.0
    packs = sum(1 for f in os.listdir(BEDROCK_DIR) if f.lower().endswith(".mcpack"))
    return round(packs * AVG_NET_PER_PACK_USD, 2)


def roblox_monthly():
    try:
        with open(ROBLOX_JSON) as f:
            d = json.load(f)
        return float(d.get("rollup", {}).get("monthly_projection", {}).get("net_usd", 0) or 0)
    except (OSError, ValueError):
        return 0.0


def affiliate_monthly():
    try:
        with open(AFFILIATE_JSON) as f:
            d = json.load(f)
        return float(d.get("total_commission_usd", 0) or 0)
    except (OSError, ValueError):
        return 0.0


def epic_monthly():
    try:
        with open(EPIC_JSON) as f:
            d = json.load(f)
        gross = sum(float(m.get("price_usd", 0) or 0) for m in d.get("maps", []))
        return round(gross * (1 - EPIC_CUT), 2)
    except (OSError, ValueError):
        return 0.0


def main():
    b = bedrock_monthly()
    r = roblox_monthly()
    a = affiliate_monthly()
    e = epic_monthly()
    total = round(b + r + a + e, 2)
    print(f"{'Channel':<12}{'Monthly (USD)':>16}")
    print("-" * 28)
    print(f"{'Bedrock':<12}{b:>16.2f}")
    print(f"{'Roblox':<12}{r:>16.2f}")
    print(f"{'Affiliates':<12}{a:>16.2f}")
    print(f"{'Epic':<12}{e:>16.2f}")
    print("-" * 28)
    print(f"{'TOTAL':<12}{total:>16.2f}")


if __name__ == "__main__":
    main()
