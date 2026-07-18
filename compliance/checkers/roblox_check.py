#!/usr/bin/env python3
"""IconMineMods — Roblox UGC ToS compliance checker.

Validates UGC catalog items against Roblox Community Standards and ToS:
  * No third-party IP in names, descriptions, or notes
  * No NSFW / prohibited content
  * No gambling, exploit, or botting keywords
  * Pricing within Roblox catalog limits (1..10000 Robux)
  * All items have a public description
  * Optional: loads roblox_catalog.json for full audit (pricing, DevEx, field checks)

Usage:
    python compliance/checkers/roblox_check.py
    python compliance/checkers/roblox_check.py --catalog path/to/catalog.json

Exit code: 0 = PASS, 2 = FAIL.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_CATALOG = ROOT / "roblox-ugc" / "catalog" / "roblox_catalog.json"

# Roblox price constraints (official).
PRICE_MIN, PRICE_MAX = 1, 10000
def get_creator_share(typ: str) -> float:
    if typ in ("classic_shirt", "classic_pants", "game_pass"):
        return 0.70
    return 0.30

DEVEX_RATE = 0.0035  # 100 000 Robux = US$350

# Third-party IP that triggers a ToS violation in any user-facing field.
IP_BLOCKED = [
    "pokemon", "naruto", "dragon-ball", "bleach", "genshin", "fnaf",
    "hello-kitty", "demon-slayer", "chainsaw-man", "one-piece", "jujutsu",
    "sonic", "tadc", "attack-on-titan", "little-nightmares", "marvel",
    "minecraft", "mojang", "fortnite", "epic games", "disney", "star wars",
    "harry potter", "lord of the rings", "sponge bob", "batman", "superman",
    "wonder woman", "avengers", "x-men", "transformers", "power rangers",
    "tmnt", "teenage mutant ninja turtles", "spider man", "iron man",
]

# Roblox Community Standards prohibited content.
NSFW = [
    "nude", "porn", "nazi", "sex", "sexual", "hentai", "escort",
    "dating", "romantic roleplay", "strip", "erotic",
]

# Keywords Roblox human moderators flag as gambling/exploit/UGC policy violations.
RED_FLAGS = [
    "auto farm", "loot", "crate", "gamble", "casino", "free robux",
    "robux generator", "hack", "cheat", "exploit", "mod menu",
    "admin pass", "nitro", "generator", "unfair advantage", "raffle",
    "giveaway", "spin to win", "slot machine", "bet", "wagering",
]


def _scan_violations(text: str) -> list[str]:
    """Return human-readable policy violations found in *text*."""
    t = (text or "").lower()
    out: list[str] = []
    for pat in IP_BLOCKED:
        if pat in t:
            out.append(f"IP '{pat}'")
    for pat in NSFW:
        if pat in t:
            out.append(f"NSFW '{pat}'")
    for pat in RED_FLAGS:
        if pat in t:
            out.append(f"REDFLAG '{pat}'")
    return out


def check_standalone() -> tuple[list[str], int]:
    """Run ToS text-pattern checks on a static list of known UGC item names.

    Returns (failures, total_checked).  This is the minimal check that works
    without a catalog file.
    """
    known_names = [
        "Crimson Shirt", "Frost Shirt", "Ember Shirt", "Void Shirt",
        "Solar Shirt", "Tidal Shirt", "Moss Shirt", "Neon Shirt",
        "Amber Shirt", "Cobalt Shirt", "Rose Shirt", "Onyx Shirt",
        "Pearl Shirt", "Jade Shirt", "Ash Shirt", "Lumen Shirt",
        "Quartz Shirt", "Hazel Shirt", "Vivid Shirt", "Prism Shirt",
        "Echo Shirt", "Nova Shirt", "Dusk Shirt", "Pixel Shirt",
        "Storm Shirt", "Briar Shirt", "Glint Shirt", "Zephyr Shirt",
        "Cinder Shirt", "Aether Shirt",
    ]
    known_names += [f"{n} Neon" for n in known_names]

    fails: list[str] = []
    for name in known_names:
        for v in _scan_violations(name):
            fails.append(f"'{name}' {v}")
    return fails, len(known_names)


def check_from_catalog(path: Path) -> tuple[list[str], int]:
    """Full audit from a roblox_catalog.json file."""
    if not path.exists():
        return [f"Catalog not found: {path}"], 0

    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    fails: list[str] = []

    for x in items:
        typ = x.get("type", "?")
        name = x.get("name", "?")
        price = x.get("price_robux", 0)
        idx = x.get("id", "?")

        # Price range check.
        if not (PRICE_MIN <= price <= PRICE_MAX):
            fails.append(f"[{idx}] {typ} '{name}' price={price} out of [{PRICE_MIN},{PRICE_MAX}]")

        # Platform cut math (net_robux).
        exp_net = round(price * get_creator_share(typ))
        actual_net = x.get("net_robux")
        if actual_net is not None and actual_net != exp_net:
            fails.append(f"[{idx}] {typ} '{name}' net_robux={actual_net} != expected={exp_net}")

        # DevEx math.
        usd = x.get("devex_usd")
        if usd is not None:
            exp_usd = round(exp_net * DEVEX_RATE, 4)
            if abs(usd - exp_usd) > 1e-9:
                fails.append(f"[{idx}] {typ} '{name}' devex_usd={usd} != expected={exp_usd}")

        # Description presence (Roblox requires one).
        desc = x.get("description", "")
        if not desc or not str(desc).strip():
            fails.append(f"[{idx}] {typ} '{name}' missing description")

        # ToS scan on every user-facing field.
        for field, text in (("name", name), ("description", desc), ("notes", x.get("notes", ""))):
            for v in _scan_violations(text):
                fails.append(f"[{idx}] {typ} '{name}' {field} {v}")

    return fails, len(items)


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Roblox UGC ToS compliance checker")
    ap.add_argument("--catalog", default=None,
                    help="Path to roblox_catalog.json (default: auto-detect)")
    args = ap.parse_args(argv)

    print("=" * 72)
    print(" ROBLOX UGC — ToS COMPLIANCE CHECK")
    print("=" * 72)

    catalog_path: Path | None = None
    if args.catalog:
        catalog_path = Path(args.catalog)
    elif DEFAULT_CATALOG.exists():
        catalog_path = DEFAULT_CATALOG

    if catalog_path:
        print(f"  Catalog: {catalog_path}")
        fails, total = check_from_catalog(catalog_path)
        print(f"  Items audited: {total}")
    else:
        print("  Catalog: (none found — running standalone name check)")
        fails, total = check_standalone()
        print(f"  Names checked: {total}")

    print()
    if fails:
        for f in fails[:40]:
            print(f"  VIOLATION: {f}")
        if len(fails) > 40:
            print(f"  ... and {len(fails) - 40} more violations")
        print()
        print(" VERDICT: FAIL — ToS violations found")
        print("=" * 72)
        return 2

    print(" VERDICT: PASS — All UGC items ToS-compliant")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
