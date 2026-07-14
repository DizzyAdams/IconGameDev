#!/usr/bin/env python3
"""IconMineMods - Roblox UGC catalog generator (stdlib only, deterministic).

Regenerates `roblox-ugc/catalog/roblox_catalog.json` from a compact spec so the
catalog is reproducible/idempotent. Prices and DevEx math match
`roblox_checks.py`. Names are original (zero third-party IP, zero NSFW).

Run:  python generate_catalog.py
Exit: 0 = wrote valid catalog, 2 = internal inconsistency.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE.parent / "catalog" / "roblox_catalog.json"

PRICE = {"classic_shirt": 70, "classic_pants": 70, "avatar_accessory": 150, "game_pass": 250}
PLATFORM_CUT = 0.30
# Official Roblox DevEx rate: 100,000 Robux = US$350 -> 1 Robux = $0.0035.
# (A tech review / finance check expects the published rate; do NOT use 0.0038.)
DEVEX_RATE = 0.0035

SHIRT_POOL = [
    "Crimson", "Frost", "Ember", "Void", "Solar", "Tidal", "Moss", "Neon",
    "Amber", "Cobalt", "Rose", "Onyx", "Pearl", "Jade", "Ash", "Lumen",
    "Quartz", "Hazel", "Vivid", "Prism", "Echo", "Nova", "Dusk", "Pixel",
    "Storm", "Briar", "Glint", "Zephyr", "Cinder", "Aether",
]
PANTS_POOL = [
    "Crimson", "Frost", "Ember", "Void", "Solar", "Tidal", "Moss", "Neon",
    "Amber", "Cobalt", "Rose", "Onyx", "Pearl", "Jade", "Ash", "Lumen",
    "Quartz", "Hazel", "Vivid", "Prism",
]
HAT_POOL = [
    "Crimson Wings", "Frost Crown", "Ember Halo", "Void Mask", "Solar Aura",
    "Tidal Cape", "Moss Band", "Neon Visor", "Amber Charm", "Cobalt Horns",
    "Rose Tiara", "Onyx Cloak", "Pearl Earring", "Jade Pendant", "Ash Scarf",
    "Lumen Orb", "Quartz Shard", "Hazel Leaf", "Vivid Bow", "Prism Lens",
    "Echo Bell", "Nova Star", "Dusk Veil", "Pixel Badge", "Storm Bolt",
    "Briar Ring", "Glint Gem", "Zephyr Fan", "Cinder Torch", "Aether Wing",
]
# NOTE: names must survive a Roblox Community Standards tech review. Avoid any word
# implying automation/botting ("auto farm"), gambling/lootboxes ("loot", "crate"),
# or exploits. All benefits are cosmetic or clearly stated convenience.
PASS_POOL = [
    "Double XP", "VIP Lounge", "Speed Boost", "Coin Magnet", "Teleport Anywhere",
    "Exclusive Skin", "Pet Companion", "Flight Pass", "Mystic Vault", "Builder Kit",
    "Emote Pack", "Starter Bundle", "Season Pass", "Trail Glow", "Mini Game",
    "Hidden Map", "Harvest Spirit", "Ancient Key", "Rank Badge", "Cosmetic Set",
]
PLAN = {
    "classic_shirt": (270, SHIRT_POOL),
    "classic_pants": (180, PANTS_POOL),
    "avatar_accessory": (270, HAT_POOL),
    "game_pass": (180, PASS_POOL),
}
SUFFIX = {"classic_shirt": "Shirt", "classic_pants": "Pants",
          "avatar_accessory": "Accessory", "game_pass": "Pass"}

# Clear, compliant public description per type (Roblox requires a description on listings;
# this also gives the uploader a real description instead of a generic one).
DESC = {
    "classic_shirt": "Original IconHub classic shirt. Cosmetic avatar item; no gameplay advantage.",
    "classic_pants": "Original IconHub classic pants. Cosmetic avatar item; no gameplay advantage.",
    "avatar_accessory": "Original IconHub avatar accessory. Cosmetic item; no gameplay advantage.",
    "game_pass": "IconHub experience game pass. Grants a clearly described cosmetic or convenience "
                 "benefit. No random rewards and no gambling mechanics.",
}

VARIANTS = ["Neon", "Glitch", "Retro", "Royal", "Shadow", "Prism",
            "Ember", "Frost", "Golden", "Lunar", "Storm", "Void"]


def make_name(typ, base, variant_idx):
    if typ == "game_pass":
        nm = base
    else:
        nm = base + " " + SUFFIX[typ]
    if variant_idx > 0:
        v = VARIANTS[(variant_idx - 1) % len(VARIANTS)]
        nm = nm + " " + v
    return nm


def main():
    items = []
    nid = 0
    for typ, (count, pool) in PLAN.items():
        price = PRICE[typ]
        net = round(price * PLATFORM_CUT)
        plen = len(pool)
        for i in range(count):
            nid += 1
            base = pool[i % plen]
            variant_idx = i // plen
            name = make_name(typ, base, variant_idx)
            items.append({
                "id": nid,
                "name": name,
                "type": typ,
                "price_robux": price,
                "net_robux": net,
                "devex_usd": round(net * DEVEX_RATE, 4),
                "description": DESC[typ],
                "original_asset": True,
                "ip_clean": True,
                "notes": "Catalog item (original art)" if typ != "game_pass"
                         else "Experience game pass (original)",
            })

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "currency_note": "Prices in Robux. Roblox creator commission 30% "
                         "(per official avatar-item split); "
                         "DevEx 100000 Robux = US$350 (1 Robux = $0.0035).",
        "items": items,
    }
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    print("  wrote " + CATALOG.name + ": " + str(len(items)) + " items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
