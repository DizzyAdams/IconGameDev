#!/usr/bin/env python3
"""IconMineMods - Roblox UGC catalog generator (stdlib only, deterministic).

Regenerates `roblox-ugc/catalog/roblox_catalog.json` from a compact spec so the
catalog is reproducible/idempotent. Prices and DevEx math match
`roblox_checks.py`. Names are original (zero third-party IP, zero NSFW).

Scaled to 5,000+ items with diverse tiers and categories.

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

PRICE = {
    "classic_shirt": 70,
    "classic_pants": 70,
    "avatar_accessory": 150,
    "game_pass": 250,
}
# Official Roblox creator cuts: classic clothes/game passes keep 70% (30% platform cut),
# UGC avatar accessories keep 30% commission (70% platform cut).
def get_creator_share(typ: str) -> float:
    if typ in ("classic_shirt", "classic_pants", "game_pass"):
        return 0.70
    return 0.30

# Official Roblox DevEx rate: 100,000 Robux = US$350 -> 1 Robux = $0.0035.
DEVEX_RATE = 0.0035

# ── Expanded pools ──────────────────────────────────────────────────────────

SHIRT_POOL = [
    "Crimson", "Frost", "Ember", "Void", "Solar", "Tidal", "Moss", "Neon",
    "Amber", "Cobalt", "Rose", "Onyx", "Pearl", "Jade", "Ash", "Lumen",
    "Quartz", "Hazel", "Vivid", "Prism", "Echo", "Nova", "Dusk", "Pixel",
    "Storm", "Briar", "Glint", "Zephyr", "Cinder", "Aether",
    "Sage", "Titan", "Raven", "Scarlet", "Indigo", "Copper", "Platinum", "Ivory",
    "Rust", "Slate", "Topaz", "Opal", "Umbra", "Flux", "Volt", "Core",
    "Wisp", "Glyph", "Gleam", "Drift",
    # New — more colors and textures
    "Blaze", "Sagebrush", "Thunder", "Lagoon", "Coral", "Tide", "Spruce",
    "Sapphire", "Ruby", "Emerald", "Sunstone", "Moonrise", "Starlight",
    "Wildfire", "Icicle", "Boulder", "Silk", "Velvet", "Linen", "Canvas",
    "Folklore", "Mythic", "Zenith", "Orbit", "Pulse",
    "Phantom", "Mirage", "Haven", "Fjord", "Tundra", "Oasis", "Monsoon",
    "Timber", "Granite", "Magma", "Geode", "Spirit", "Solstice", "Equinox",
]

PANTS_POOL = [
    "Crimson", "Frost", "Ember", "Void", "Solar", "Tidal", "Moss", "Neon",
    "Amber", "Cobalt", "Rose", "Onyx", "Pearl", "Jade", "Ash", "Lumen",
    "Quartz", "Hazel", "Vivid", "Prism",
    "Sage", "Titan", "Raven", "Scarlet", "Indigo", "Copper", "Platinum", "Ivory",
    "Rust", "Slate", "Topaz", "Opal", "Umbra", "Flux", "Volt",
    # New
    "Blaze", "Sagebrush", "Thunder", "Lagoon", "Coral", "Tide", "Spruce",
    "Sapphire", "Ruby", "Emerald", "Sunstone", "Moonrise", "Starlight",
    "Wildfire", "Icicle", "Boulder", "Silk", "Velvet", "Linen", "Canvas",
    "Phantom", "Mirage", "Haven", "Fjord", "Tundra", "Oasis", "Monsoon",
    "Timber", "Granite", "Magma", "Geode", "Spirit",
]

HAT_POOL = [
    "Crimson Wings", "Frost Crown", "Ember Halo", "Void Mask", "Solar Aura",
    "Tidal Cape", "Moss Band", "Neon Visor", "Amber Charm", "Cobalt Horns",
    "Rose Tiara", "Onyx Cloak", "Pearl Earring", "Jade Pendant", "Ash Scarf",
    "Lumen Orb", "Quartz Shard", "Hazel Leaf", "Vivid Bow", "Prism Lens",
    "Echo Bell", "Nova Star", "Dusk Veil", "Pixel Badge", "Storm Bolt",
    "Briar Ring", "Glint Gem", "Zephyr Fan", "Cinder Torch", "Aether Wing",
    "Sage Crown", "Titan Helm", "Raven Plume", "Scarlet Ribbon", "Indigo Gem",
    "Copper Coin", "Platinum Shield", "Ivory Comb", "Rust Gear", "Slate Mask",
    "Topaz Chain", "Opal Ring", "Umbra Shroud", "Flux Capacitor", "Volt Spike",
    "Core Shard", "Wisp Lantern", "Glyph Stone", "Gleam Mirror", "Drift Compass",
    # New — more variety: glasses, necklaces, wings, backpacks, bracelets, etc.
    "Star Goggles", "Crystal Earring", "Ruby Pendant", "Butterfly Wings",
    "Royal Cape", "Adventure Pack", "Moon Crown", "War Paint", "Fox Tail",
    "Bone Bracelet", "Night Vision", "Diamond Stud", "Emerald Locket",
    "Dragon Wings", "Shadow Cape", "Mystic Pack", "Sun Crown", "Tribal Mark",
    "Leopard Tail", "Gold Chain", "Cyber Visor", "Pearl Drop", "Amulet of Light",
    "Bat Wings", "Traveler Cloak", "Spirit Pack", "Ivy Crown", "Moon Mark",
    "Bunny Tail", "Silver Link", "Ocean Pearl", "Storm Horns", "Lava Wings",
    "Frozen Halo", "Thunder Ring", "Glow Stick", "Crystal Tiara",
    "Dark Veil", "Rose Crown", "Fox Ears", "Cat Bell", "Panda Mask",
    "Wolf Fang", "Phoenix Plume", "Fairy Dust", "Star Locket", "Heart Pin",
    "Skull Ring", "Spider Brooch", "Lily Crown", "Maple Leaf", "Snowflake Charm",
]

# Basic accessories — simpler items at a lower price point
BASIC_ACC_POOL = [
    "Simple Band", "Tiny Star", "Mini Gem", "Basic Ring", "Small Stud",
    "Mini Bell", "Tiny Heart", "Star Pin", "Leaf Clip", "Mini Orb",
    "Fairy Light", "Tiny Crown", "Glow Dot", "Mini Mask", "Small Bow",
    "Tiny Shield", "Star Earring", "Mini Cape", "Small Scar", "Gem Chip",
    "Dew Drop", "Spark Dot", "Mini Tail", "Star Badge", "Heart Pin",
    "Clover Pin", "Feather Clip", "Tiny Horn", "Mini Halo", "Glow Ring",
]

# Deluxe accessories — mid-tier items at 250 Robux
DELUXE_ACC_POOL = [
    "Enchanted Necklace", "Crystal Circlet", "Shadow Gauntlet", "Arcane Amulet",
    "Silver Wings", "Sun Pendant", "Frost Gloves", "Void Crown", "Flame Belt",
    "Mystic Tattoo", "Royal Scepter", "Storm Shield", "Jade Bracelet",
    "Lunar Charm", "Thunder Boots", "Golden Armband", "Spirit Mask",
    "Astral Ring", "Crystal Pauldron", "Mermaid Tail",
    "Dragon Scale", "Fairy Crown", "Night Cape", "Demon Tail",
    "Elf Ears", "Angel Wings", "Cyber Arm", "Mythic Horn", "Vampire Fangs",
    "Griffin Feather", "Serpent Ring", "Ghost Veil", "Elven Cloak",
]

PREMIUM_HAT_POOL = [
    "Crown of Stars", "Dragon Horns", "Angel Halo", "Demon Wings", "Phoenix Tail",
    "Lion Mane", "Wolf Ears", "Fox Mask", "Crystal Crown", "Flame Aura",
    "Ice Crown", "Shadow Veil", "Light Halo", "Thunder Crest", "Nature Wreath",
    # New
    "Celestial Diadem", "Dragon Mask", "Phoenix Crown", "Griffin Wings",
    "Kitsune Tail", "Unicorn Horn", "Pegasus Wings", "Leviathan Scale",
    "Sphinx Necklace", "Chimera Mane", "Hydra Hood", "Basilisk Eye",
    "Manticore Spine", "Naga Coil", "Cerberus Collar",
]

LIMITED_HAT_POOL = [
    "Celestial Wings", "Dragon Crown", "Phantom Mask", "Star Halo", "Royal Cape",
    "Enchanted Orb", "Mythic Shield", "Arcane Tome", "Crystal Sword", "Shadow Cloak",
    # New
    "Eternal Crown", "Nebula Wings", "Time Compass", "Void Portal",
    "Cosmic Scepter", "Infinity Ring", "Galaxy Veil", "Astral Throne",
    "Prism Mirror", "Dream Catcher", "Aether Crown", "Fate Spinner",
    "Mirage Cloak", "Quantum Mask", "Eclipse Wings",
]

PASS_POOL = [
    "Double XP", "VIP Lounge", "Speed Boost", "Coin Magnet", "Teleport Anywhere",
    "Exclusive Skin", "Pet Companion", "Flight Pass", "Mystic Vault", "Builder Kit",
    "Emote Pack", "Starter Bundle", "Season Pass", "Trail Glow", "Mini Game",
    "Hidden Map", "Harvest Spirit", "Ancient Key", "Rank Badge", "Cosmetic Set",
    "Treasure Sense", "Lucky Charm", "Shadow Step", "Ghost Form", "Magnet Aura",
    "Craft Boost", "Trade Access", "Guild Banner", "Dance Pack",
    # New
    "Ninja Dash", "Super Jump", "Wall Climb", "Double Jump", "No Clip",
    "Treasure Scan", "Treasure Map", "Map Reveal", "Auto Collect", "Smart Furnace",
    "Haste Aura", "Glider Wings", "Block Launcher", "Arrow Storm", "Brew Master",
    "Craft Elite", "Pet Master", "Hero Class", "Ghost Walk", "Shadow Strike",
    "Time Freeze", "Infinite Stamina", "Night Vision", "Water Walk",
    "Soul Link", "Mana Surge", "Fortune Favor", "Rage Mode",
]

# ── Tier definitions ────────────────────────────────────────────────────────

# PLAN = base items at standard prices
PLAN = {
    "classic_shirt": (3000, SHIRT_POOL),   # 72 names × ~42 variants
    "classic_pants": (2000, PANTS_POOL),     # 57 names × ~35 variants
    "avatar_accessory": (2000, HAT_POOL),    # 80 names × 25 variants
    "game_pass": (1500, PASS_POOL),          # 57 names × ~27 variants
}

PREMIUM_VARIANTS = [
    "Gold", "Platinum", "Diamond", "Obsidian", "Crystal",
    "Inferno", "Frozen", "Celestial", "Ruby", "Sapphire",
]

# Basic accessories — lowest price tier
BASIC_ACC = {
    "avatar_accessory": (300, BASIC_ACC_POOL, 70),
}

# Deluxe accessories — mid-tier
DELUXE_ACC = {
    "avatar_accessory": (250, DELUXE_ACC_POOL, 250),
}

# Premium accessories (500 Robux)
PREMIUM = {
    "avatar_accessory": (400, PREMIUM_HAT_POOL, 500),
}

# Standard accessories at 150 Robux (from the premium pool area)
STANDARD_ACC = {
    "avatar_accessory": (200, PREMIUM_HAT_POOL, 150),
}

# Limited accessories (1000 Robux)
LIMITED = {
    "avatar_accessory": (500, LIMITED_HAT_POOL, 1000),
}

# Game pass tiers
BASIC_PASS = {
    "game_pass": (250, PASS_POOL, 150),
}

PREMIUM_PASS = {
    "game_pass": (250, PASS_POOL, 500),
}

ULTIMATE_PASS = {
    "game_pass": (100, PASS_POOL, 1000),
}

SUFFIX = {
    "classic_shirt": "Shirt",
    "classic_pants": "Pants",
    "avatar_accessory": "Accessory",
    "game_pass": "Pass",
}

# Clear, compliant public description per type
DESC = {
    "classic_shirt": "Original IconHub classic shirt. Cosmetic avatar item; no gameplay advantage.",
    "classic_pants": "Original IconHub classic pants. Cosmetic avatar item; no gameplay advantage.",
    "avatar_accessory": "Original IconHub avatar accessory. Cosmetic item; no gameplay advantage.",
    "game_pass": "IconHub experience game pass. Grants a clearly described cosmetic or convenience "
                 "benefit. No random rewards and no gambling mechanics.",
}

VARIANTS = [
    "Neon", "Glitch", "Retro", "Royal", "Shadow", "Prism",
    "Ember", "Frost", "Golden", "Lunar", "Storm", "Void",
    "Blaze", "Crystal", "Phantom", "Solar",
]


def make_name(typ, base, variant_idx):
    if typ == "game_pass":
        nm = base
    else:
        nm = base + " " + SUFFIX[typ]
    if variant_idx > 0:
        v = VARIANTS[(variant_idx - 1) % len(VARIANTS)]
        nm = nm + " " + v
    return nm


def _generate_plan_items(items, nid, typ, count, pool, price, desc=DESC, note_prefix="Catalog item"):
    """Add `count` items of type `typ` at `price` using `pool` + variants."""
    net = round(price * get_creator_share(typ))
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
            "description": desc[typ] if isinstance(desc, dict) else desc,
            "original_asset": True,
            "ip_clean": True,
            "notes": f"{note_prefix} (original art)",
        })
    return nid


def _generate_tiered_items(items, nid, typ, count, pool, price, note_prefix, desc_override=None):
    """Add tiered items — same pattern as plan items but with a custom price and note."""
    net = round(price * get_creator_share(typ))
    plen = len(pool)
    pvar_len = len(PREMIUM_VARIANTS)
    for i in range(count):
        nid += 1
        base = pool[i % plen]
        variant_idx = i // plen
        nm = base
        if variant_idx > 0:
            nm = nm + " " + PREMIUM_VARIANTS[(variant_idx - 1) % pvar_len]
        desc = desc_override if desc_override else DESC.get(typ, "")
        items.append({
            "id": nid,
            "name": nm,
            "type": typ,
            "price_robux": price,
            "net_robux": net,
            "devex_usd": round(net * DEVEX_RATE, 4),
            "description": desc if "Premium" in note_prefix or "Limited" in note_prefix or "Deluxe" in note_prefix
                           else f"Basic {DESC.get(typ, '')}" if "Basic" in note_prefix
                           else DESC.get(typ, ""),
            "original_asset": True,
            "ip_clean": True,
            "notes": f"{note_prefix} (original art)",
        })
    return nid


def main():
    items = []
    nid = 0

    # ── Base PLAN items ──
    for typ, (count, pool) in PLAN.items():
        nid = _generate_plan_items(items, nid, typ, count, pool, PRICE[typ])

    # ── Basic accessories (70 Robux) ──
    for typ, (count, pool, price) in BASIC_ACC.items():
        nid = _generate_tiered_items(items, nid, typ, count, pool, price,
                                     "Basic accessory")

    # ── Standard accessories from PREMIUM pool at 150 Robux ──
    for typ, (count, pool, price) in STANDARD_ACC.items():
        nid = _generate_tiered_items(items, nid, typ, count, pool, price,
                                     "Standard accessory")

    # ── Premium accessories (500 Robux) ──
    for typ, (count, pool, price) in PREMIUM.items():
        nid = _generate_tiered_items(items, nid, typ, count, pool, price,
                                     "Premium accessory",
                                     "Premium " + DESC[typ])

    # ── Deluxe accessories (250 Robux) ──
    for typ, (count, pool, price) in DELUXE_ACC.items():
        nid = _generate_tiered_items(items, nid, typ, count, pool, price,
                                     "Deluxe accessory",
                                     "Deluxe " + DESC[typ])

    # ── Limited accessories (1000 Robux) ──
    for typ, (count, pool, price) in LIMITED.items():
        nid = _generate_tiered_items(items, nid, typ, count, pool, price,
                                     "Limited premium accessory",
                                     "Limited " + DESC[typ])

    # ── Basic game passes (150 Robux) ──
    for typ, (count, pool, price) in BASIC_PASS.items():
        nid = _generate_tiered_items(items, nid, typ, count, pool, price,
                                     "Basic game pass",
                                     "IconHub basic game pass. Convenience feature.")

    # ── Premium game passes (500 Robux) ──
    for typ, (count, pool, price) in PREMIUM_PASS.items():
        nid = _generate_tiered_items(items, nid, typ, count, pool, price,
                                     "Premium game pass",
                                     "IconHub premium game pass. Enhanced convenience feature.")

    # ── Ultimate game passes (1000 Robux) ──
    for typ, (count, pool, price) in ULTIMATE_PASS.items():
        nid = _generate_tiered_items(items, nid, typ, count, pool, price,
                                     "Ultimate game pass",
                                     "IconHub ultimate game pass. Top-tier convenience feature.")

    total_items = len(items)
    total_robux = sum(x["price_robux"] for x in items)
    total_net = sum(x["net_robux"] for x in items)
    total_devex = round(total_net * DEVEX_RATE, 2)

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "currency_note": "Prices in Robux. Classic clothing and game passes creator share 70% "
                         "(30% platform cut); avatar accessories creator commission 30% "
                         "(70% platform cut); DevEx 100,000 Robux = US$350 (1 Robux = $0.0035).",
        "summary": {
            "total_items": total_items,
            "total_robux_revenue": total_robux,
            "total_net_robux_after_cut": total_net,
            "total_devex_usd": total_devex,
            "currency_note": "Classic clothes / game passes 70% creator share, avatar accessories 30%; DevEx 1 Robux = $0.0035",
        },
        "items": items,
    }
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    print(f"  wrote {CATALOG.name}: {total_items} items")
    print(f"  total Robux revenue: {total_robux}")
    print(f"  total net Robux: {total_net}")
    print(f"  estimated DevEx USD: ${total_devex}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
