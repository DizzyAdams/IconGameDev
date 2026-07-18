#!/usr/bin/env python3
"""IconMineMods — Fortnite (Epic Games) UGC / Creative map ToS compliance checker.

Validates Fortnite Creative maps against Epic Games Content Guidelines:
  * No third-party IP in map names, descriptions, or metadata
  * No NSFW / mature / prohibited content
  * No gambling / loot-box / exploit keywords
  * Pricing sanity checks (Epic's Support-a-Creator / published price ranges)
  * All maps have a public description
  * Author-asserted originality (original asset flag)

Usage:
    python compliance/checkers/epic_check.py
    python compliance/checkers/epic_check.py --maps path/to/epic.json

Exit code: 0 = PASS, 2 = FAIL.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_MAPS = ROOT / "website-next" / "data" / "epic.json"

# Epic Games Content Guidelines — prohibited / restricted words in user-facing
# fields.  In-game map names, descriptions, tags, and thumbnails are moderated.
IP_BLOCKED = [
    "pokemon", "naruto", "dragon-ball", "bleach", "genshin", "fnaf",
    "hello-kitty", "demon-slayer", "chainsaw-man", "one-piece", "jujutsu",
    "sonic", "tadc", "attack-on-titan", "little-nightmares", "marvel",
    "minecraft", "mojang", "roblox", "disney", "star wars",
    "harry potter", "lord of the rings", "sponge bob", "batman", "superman",
    "wonder woman", "avengers", "x-men", "transformers", "power rangers",
    "tmnt", "fortnite (as map name part)", "epic games (as map name)",
    "call of duty", "grand theft auto", "gta", "halo", "mario", "zelda",
]

# Epic Content Rating / Community Rules — prohibited content types.
NSFW = [
    "nude", "porn", "nazi", "sex", "sexual", "hentai", "escort",
    "strip", "erotic", "dating sim",
]

# Keywords flagged by Epic human review for gambling / exploit / policy violation.
RED_FLAGS = [
    "loot box", "gamble", "casino", "free v bucks", "v buck generator",
    "hack", "cheat", "exploit", "mod menu", "auto win", "aimbot",
    "wallhack", "unfair advantage", "raffle", "giveaway",
    "spin to win", "slot machine", "bet", "wagering",
]

# Recommended price range for Epic Creative maps in USD (free up to ~$9.99).
PRICE_MIN = 0.0
PRICE_MAX = 19.99
TYPICAL_MAX = 9.99  # softer ceiling for "typical" maps


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


def check_from_maps(path: Path) -> tuple[list[str], int]:
    """Full audit from an epic.json maps file."""
    if not path.exists():
        return [f"Maps file not found: {path}"], 0

    raw = json.loads(path.read_text(encoding="utf-8"))
    # epic.json may have {brand, platform, status, maps: [...]} or be a flat array.
    if isinstance(raw, dict):
        maps = raw.get("maps", raw.get("data", raw.get("games", [])))
    elif isinstance(raw, list):
        maps = raw
    else:
        return [f"Unknown data shape in {path}"], 0

    if not maps:
        return ["No maps found in data file"], 0

    fails: list[str] = []
    for m in maps:
        mid = m.get("id", "?")
        name = m.get("name", "?")
        price = m.get("price_usd", 0.0)
        desc = m.get("description", "")

        # Price range check.
        try:
            fp = float(price)
        except (TypeError, ValueError):
            fails.append(f"[{mid}] '{name}' price_usd={price!r} is not a number")
            continue

        if not (PRICE_MIN <= fp <= PRICE_MAX):
            fails.append(f"[{mid}] '{name}' price_usd={fp} out of [{PRICE_MIN},{PRICE_MAX}]")
        elif fp > TYPICAL_MAX:
            fails.append(f"[{mid}] '{name}' price_usd={fp} exceeds typical ceiling ${TYPICAL_MAX}")

        # Description presence.
        if not desc or not str(desc).strip():
            fails.append(f"[{mid}] '{name}' missing description")

        # Author-originality flag.
        if not m.get("ip_clean", True):
            fails.append(f"[{mid}] '{name}' flagged as not ip_clean")

        # ToS scan on user-facing fields.
        for field, text in (("name", name), ("description", desc), ("notes", m.get("notes", ""))):
            for v in _scan_violations(text):
                fails.append(f"[{mid}] '{name}' {field} {v}")

    return fails, len(maps)


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Fortnite Creative map ToS compliance checker")
    ap.add_argument("--maps", default=None,
                    help="Path to epic.json (default: auto-detect)")
    args = ap.parse_args(argv)

    print("=" * 72)
    print(" FORTNITE CREATIVE (EPIC GAMES) — ToS COMPLIANCE CHECK")
    print("=" * 72)

    maps_path: Path | None = None
    if args.maps:
        maps_path = Path(args.maps)
    elif DEFAULT_MAPS.exists():
        maps_path = DEFAULT_MAPS

    if maps_path:
        print(f"  Maps file: {maps_path}")
        fails, total = check_from_maps(maps_path)
        print(f"  Maps audited: {total}")
    else:
        print("  Maps file: (none found — cannot check)")
        print()
        print(" VERDICT: SKIP — no map data available")
        print("=" * 72)
        return 0  # Not a hard fail — data may not be generated yet.

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

    print(" VERDICT: PASS — All Fortnite Creative maps ToS-compliant")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
