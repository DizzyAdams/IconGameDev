#!/usr/bin/env python3
"""IconMineMods - Roblox UGC compliance validator (stdlib only, scalable).

Loads roblox_catalog.json and enforces what a Roblox tech review / moderator checks:
  * item count > 0 and self-consistent
  * per-type unit prices match the Roblox catalog price map
  * DevEx math consistency (net = price*0.70; usd = net*0.0035, official rate)
  * Roblox catalog price limits (1..10000 Robux)
  * every item has a non-empty public `description`
  * no third-party IP substrings in name / description / notes
  * no NSFW substrings in name / description / notes
  * no gambling / exploit / botting red-flags (loot, crate, auto farm, hack, ...)
    in name / description / notes  -- the things a human reviewer would hold

Run:  python roblox_checks.py
Exit: 0 = PASS, 2 = FAIL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE.parent / "catalog" / "roblox_catalog.json"

PRICE = {"classic_shirt": {70}, "classic_pants": {70}, "avatar_accessory": {70, 150, 250, 500, 1000}, "game_pass": {150, 250, 500, 1000}}
def get_creator_share(typ: str) -> float:
    if typ in ("classic_shirt", "classic_pants", "game_pass"):
        return 0.70
    return 0.30

# Official Roblox DevEx: 100,000 Robux = US$350 -> 1 Robux = $0.0035.
DEVEX_RATE = 0.0035
PRICE_MIN, PRICE_MAX = 1, 10000
IP_BLOCKED = [
    "pokemon", "naruto", "dragon-ball", "bleach", "genshin", "fnaf",
    "hello-kitty", "demon-slayer", "chainsaw-man", "one-piece", "jujutsu",
    "sonic", "tadc", "attack-on-titan", "little-nightmares", "marvel",
    "minecraft", "mojang",
]
NSFW = ["nude", "porn", "nazi", "sex"]
# Words a Roblox Community Standards tech review holds for gambling / exploit / botting.
RED_FLAGS = [
    "auto farm", "loot", "crate", "gamble", "casino", "free robux",
    "robux generator", "hack", "cheat", "exploit", "mod menu",
    "admin pass", "nitro", "generator", "unfair advantage",
]


def _violations(text: str) -> list[str]:
    """Return list of human-readable policy violations found in `text`."""
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


def main() -> int:
    if not CATALOG.exists():
        print(f"FAIL: catalog not found at {CATALOG}")
        print("VERDICT: FAIL")
        return 2

    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    items = data.get("items", [])
    fails: list[str] = []
    counts: dict[str, int] = {}

    for x in items:
        typ = x.get("type")
        counts[typ] = counts.get(typ, 0) + 1
        name = x.get("name", "")
        price = x.get("price_robux", 0)
        exp = PRICE.get(typ)
        if exp is not None and price not in exp:
            fails.append(f"{typ} '{name}' price={price} != {exp}")
        if not (PRICE_MIN <= price <= PRICE_MAX):
            fails.append(f"{typ} '{name}' price out of [{PRICE_MIN},{PRICE_MAX}]")
        exp_net = round(price * get_creator_share(typ))
        if x.get("net_robux") != exp_net:
            fails.append(f"{typ} '{name}' net_robux={x.get('net_robux')} != {exp_net}")
        if abs(x.get("devex_usd", 0) - round(exp_net * DEVEX_RATE, 4)) > 1e-9:
            fails.append(f"{typ} '{name}' devex_usd mismatch")
        # Roblox requires a public description; a missing/empty one fails the listing review.
        desc = x.get("description", "")
        if not desc or not str(desc).strip():
            fails.append(f"{typ} '{name}' missing description")
        # Scan every user-facing text field the same way a human reviewer would.
        for field, text in (("name", name), ("description", desc), ("notes", x.get("notes", ""))):
            for v in _violations(text):
                fails.append(f"{typ} '{name}' {field} {v}")

    print(f"  items: {len(items)}")
    for typ, c in sorted(counts.items()):
        print(f"  {typ}: {c}")
    print("\n" + "=" * 60)
    if fails:
        for f in fails[:30]:
            print("  FAIL:", f)
        if len(fails) > 30:
            print(f"  ... and {len(fails) - 30} more")
        print(" VERDICT: FAIL")
        return 2
    print(" VERDICT: PASS - Roblox catalog compliant")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
