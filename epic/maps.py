#!/usr/bin/env python3
"""Generate Epic/Fortnite Creative original map entries -> maps.json. Stdlib only."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "maps.json")
DEFAULT_COUNT = 50

FORBIDDEN = [
    "pokemon", "naruto", "dragon-ball", "bleach", "genshin", "fnaf", "hello-kitty",
    "demon-slayer", "chainsaw-man", "one-piece", "jujutsu", "sonic", "tadc",
    "attack-on-titan", "little-nightmares", "marvel", "minecraft", "mojang",
    "nude", "porn", "nazi", "sex",
]

ADJ = ["Crimson", "Frost", "Ember", "Shadow", "Neon", "Iron", "Solar", "Lunar",
       "Storm", "Toxic", "Golden", "Rapid", "Silent", "Volt", "Azure", "Cobalt"]
NOUN = ["Arena", "Outpost", "Bunker", "Spire", "Circuit", "Citadel", "Harbor",
        "Ridge", "Forge", "Verge", "Nexus", "Drift", "Vault", "Crest", "Hollow", "Beacon"]


def name_for(i):
    return f"{ADJ[i % len(ADJ)]} {NOUN[(i // len(ADJ)) % len(NOUN)]}"


def price_for(i):
    # deterministic, 2.99..9.99 rounded to 2dp
    return round(2.99 + ((i * 131) % 701) / 100, 2)


def build(n):
    maps = []
    for i in range(n):
        name = name_for(i)
        maps.append({
            "id": f"imap-{i:04d}",
            "name": name,
            "price_usd": price_for(i),
            "description": f"Original Fortnite Creative map: {name}.",
            "original": True,
            "ip_clean": True,
        })
    return maps


def write_json(n):
    data = {"count": n, "maps": build(n)}
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    return data


def check(n):
    try:
        with open(OUT) as f:
            data = json.load(f)
    except (OSError, ValueError):
        print("VERDICT FAIL: maps.json missing/unreadable")
        return 2
    maps = data.get("maps", [])
    if len(maps) != n:
        print(f"VERDICT FAIL: count {len(maps)} != {n}")
        return 2
    for m in maps:
        p = m.get("price_usd", 0)
        if not (2.99 <= p <= 9.99):
            print(f"VERDICT FAIL: bad price {p}")
            return 2
        blob = f"{m.get('name','')} {m.get('description','')}".lower()
        for bad in FORBIDDEN:
            if bad in blob:
                print(f"VERDICT FAIL: forbidden substring '{bad}' in {m.get('id')}")
                return 2
    print("VERDICT PASS")
    return 0


def main():
    n = DEFAULT_COUNT
    for a in sys.argv[1:]:
        if a.startswith("--count="):
            n = int(a.split("=", 1)[1])
        elif a == "--count" and sys.argv[-1].isdigit():
            n = int(sys.argv[-1])
    if "--check" in sys.argv:
        sys.exit(check(n))
    write_json(n)
    print(f"wrote {OUT} with {n} maps")


if __name__ == "__main__":
    main()
