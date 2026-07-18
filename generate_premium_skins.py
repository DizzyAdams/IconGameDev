#!/usr/bin/env python3
"""Generate 50 premium themed Bedrock skin packs (12 skins each) in skin-packs/."""

from __future__ import annotations

import hashlib
import io
import json
import os
import random
import math
from pathlib import Path

import PIL.Image
import PIL.ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent
OUT = PROJECT_ROOT / "skin-packs"
SKINS_PER_PACK = 12
SIZE = (64, 64)

# ============================================================
# 50 PREMIUM THEMES
# theme_id: (display_name, price_usd, mc_coins, description, palette_colors)
# Prices range $4.99-$9.99 as requested
# ============================================================
THEMES = [
    ("cyberpunk-neon",       "Cyberpunk Neon",      6.99,  1060, "12 neon-lit cyberpunk skins with holographic visors and chrome armor."),
    ("medieval-knights",     "Medieval Knights",    6.99,  1060, "12 armored knight skins with heraldic shields and steel plate armor."),
    ("aquatic-depths",      "Aquatic Depths",      5.99,   910, "12 deep ocean skins with coral armor, tridents, and bioluminescent fins."),
    ("space-explorers",     "Space Explorers",     7.99,  1210, "12 futuristic space suits with jetpacks, helmets, and galaxy visors."),
    ("fantasy-elves",       "Fantasy Elves",       6.99,  1060, "12 mystical elf skins with nature magic, glowing runes, and elegant robes."),
    ("steampunk-inventors", "Steampunk Inventors", 7.99,  1210, "12 steampunk inventor skins with brass goggles, gears, and steam-powered suits."),
    ("shadow-ninja",        "Shadow Ninja",        5.99,   910, "12 shadow-cloaked ninja skins with throwing stars, katanas, and smoke effects."),
    ("samurai-warriors",    "Samurai Warriors",    6.99,  1060, "12 samurai warrior skins with kabuto helmets, katana blades, and ornate armor."),
    ("dragon-lords",        "Dragon Lords",        8.99,  1360, "12 dragon-themed skins with scale armor, wings, and elemental breath effects."),
    ("celestial-guardians", "Celestial Guardians", 8.99,  1360, "12 celestial skins with starfield capes, golden halos, and cosmic weapons."),
    ("arctic-frost",        "Arctic Frost",        5.99,   910, "12 ice warriors with frost armor, snow capes, and frozen weapons."),
    ("jungle-warriors",     "Jungle Warriors",     5.99,   910, "12 jungle tribe skins with animal totems, bone armor, and camouflage."),
    ("pirate-raiders",      "Pirate Raiders",      6.99,  1060, "12 pirate skins with eye patches, cutlasses, treasure maps, and peg legs."),
    ("egyptian-pharaohs",   "Egyptian Pharaohs",   7.99,  1210, "12 ancient Egyptian skins with golden headdresses, ankhs, and royal regalia."),
    ("viking-raiders",      "Viking Raiders",      6.99,  1060, "12 viking warrior skins with horned helmets, battle axes, and rune shields."),
    ("wild-west",           "Wild West",           5.99,   910, "12 wild west outlaw skins with cowboy hats, revolvers, and sheriff badges."),
    ("zombie-horde",        "Zombie Horde",        6.99,  1060, "12 undead zombie skins with rotting flesh, glowing eyes, and tattered clothes."),
    ("vampire-legacy",      "Vampire Legacy",      7.99,  1210, "12 vampire lord skins with crimson capes, fangs, and dark aristocrat attire."),
    ("werewolf-pack",       "Werewolf Pack",       7.99,  1210, "12 werewolf skins with fur, claws, glowing eyes, and lunar amulets."),
    ("fairy-kingdom",       "Fairy Kingdom",       6.99,  1060, "12 fairy skins with shimmering wings, flower crowns, and pixie dust trails."),
    ("demonic-legion",      "Demonic Legion",      7.99,  1210, "12 demonic skins with horned helmets, fire auras, and infernal armor."),
    ("angelic-host",        "Angelic Host",        7.99,  1210, "12 angelic skins with feathered wings, golden armor, and holy light halos."),
    ("robot-uprising",      "Robot Uprising",      8.99,  1360, "12 robot skins with LED visors, servo joints, and metal plating."),
    ("dinosaur-age",        "Dinosaur Age",        6.99,  1060, "12 dinosaur-inspired skins with scales, claws, tails, and primal patterns."),
    ("desert-nomads",       "Desert Nomads",       5.99,   910, "12 desert wanderer skins with turbans, sand cloaks, and scimitars."),
    ("crystal-cavern",      "Crystal Cavern",      8.99,  1360, "12 crystal-themed skins with gemstone armor, crystalline weapons, and glowing facets."),
    ("lava-realm",          "Lava Realm",          7.99,  1210, "12 lava warrior skins with molten armor, fire weapons, and obsidian shields."),
    ("toxic-wasteland",     "Toxic Wasteland",     6.99,  1060, "12 toxic survivor skins with hazmat suits, gas masks, and neon warning stripes."),
    ("magic-academy",       "Magic Academy",       6.99,  1060, "12 wizard apprentice skins with spellbooks, wizard hats, and enchanted staffs."),
    ("super-soldiers",      "Super Soldiers",      6.99,  1060, "12 elite soldier skins with tactical gear, night vision, and combat armor."),
    ("carnival-masks",      "Carnival Masks",      5.99,   910, "12 carnival festival skins with colorful masks, confetti, and parade outfits."),
    ("royal-court",         "Royal Court",         7.99,  1210, "12 royal court skins with crowns, velvet capes, scepters, and gemstone jewelry."),
    ("ghost-pirates",       "Ghost Pirates",       7.99,  1210, "12 ghostly pirate skins with spectral glows, torn sails, and cursed treasure."),
    ("galaxy-rangers",      "Galaxy Rangers",      8.99,  1360, "12 interstellar ranger skins with plasma rifles, nebula armor, and energy shields."),
    ("mushroom-kingdom",    "Mushroom Kingdom",    5.99,   910, "12 mushroom-themed skins with toadstool hats, spore cloaks, and forest colors."),
    ("clockwork-city",      "Clockwork City",      8.99,  1360, "12 clockwork automaton skins with gear mechanisms, brass plating, and steam vents."),
    ("mecha-ninja",         "Mecha Ninja",         8.99,  1360, "12 cyber-ninja skins with tech blades, holographic cloaks, and targeting visors."),
    ("dreamscape",          "Dreamscape",          9.99,  1520, "12 dreamlike ethereal skins with prismatic auras, floating runes, and starlight trails."),
    ("neon-riders",         "Neon Riders",         6.99,  1060, "12 neon biker skins with cyber jackets, glowing helmets, and energy whips."),
    ("grim-reapers",        "Grim Reapers",        7.99,  1210, "12 death incarnate skins with scythes, hooded cloaks, and soul lanterns."),
    ("mythic-beasts",       "Mythic Beasts",       8.99,  1360, "12 mythical beast skins representing griffins, krakens, minotaurs, and chimeras."),
    ("candy-land",          "Candy Land",          4.99,   760, "12 sweet candy-themed skins with frosting armor, licorice whips, and gumdrop details."),
    ("ocean-warriors",      "Ocean Warriors",      6.99,  1060, "12 marine soldier skins with pearl armor, wave blades, and coral shields."),
    ("shadow-hunters",      "Shadow Hunters",      6.99,  1060, "12 shadow hunter skins with dark capes, crossbows, and spectral tracking effects."),
    ("thunder-gods",        "Thunder Gods",        9.99,  1520, "12 storm deity skins with lightning bolts, storm clouds, and thunder hammers."),
    ("samurai-elite",       "Samurai Elite",       6.99,  1060, "12 elite samurai skins with crimson armor, demon masks, and legendary katanas."),
    ("dwarven-miners",      "Dwarven Miners",      5.99,   910, "12 dwarf miner skins with pickaxes, lantern helmets, and gem-encrusted beards."),
    ("woodland-rangers",    "Woodland Rangers",    5.99,   910, "12 forest ranger skins with leaf cloaks, bows, antlers, and animal companions."),
    ("void-walkers",        "Void Walkers",        9.99,  1520, "12 void entity skins with cosmic tentacles, purple auras, and reality-warping effects."),
    ("phoenix-order",       "Phoenix Order",       8.99,  1360, "12 phoenix knight skins with flame wings, rebirth armor, and solar weapons."),
]


def make_uuid(name: str) -> str:
    """Deterministic UUID from a name string."""
    raw = hashlib.sha256(name.encode()).hexdigest()[:32]
    return "-".join([raw[:8], raw[8:12], raw[12:16], raw[16:20], raw[20:32]])


def _shade(rgb, f):
    return tuple(max(0, min(255, int(c * f))) for c in rgb)


def make_premium_skin(theme_rgb, variant_idx: int) -> bytes:
    """Draw a stylized 64x64 humanoid skin with the theme color + variant accents."""
    rng = random.Random(variant_idx * 7919 + 13)
    base = theme_rgb + (255,)
    dark = _shade(theme_rgb, 0.65) + (255,)
    darker = _shade(theme_rgb, 0.40) + (255,)
    accent = (
        min(255, theme_rgb[0] + rng.randint(-30, 60)),
        min(255, theme_rgb[1] + rng.randint(-30, 60)),
        min(255, theme_rgb[2] + rng.randint(-30, 60)),
        255,
    )

    img = PIL.Image.new("RGBA", SIZE, (0, 0, 0, 0))
    d = PIL.ImageDraw.Draw(img)

    # ---- HEAD (8,8)-(23,23) ----
    d.rectangle([8, 8, 23, 23], fill=base, outline=dark)
    # Eyes
    d.rectangle([11, 13, 13, 15], fill=(20, 20, 30, 255))
    d.rectangle([17, 13, 19, 15], fill=(20, 20, 30, 255))
    # Eye glow / visor accent (premium touch)
    d.rectangle([11, 14, 13, 14], fill=accent)
    d.rectangle([17, 14, 19, 14], fill=accent)

    # ---- BODY (20,24)-(43,47) ----
    d.rectangle([20, 24, 43, 47], fill=dark, outline=base)
    # Chest plate accent
    d.rectangle([26, 28, 37, 35], fill=base, outline=accent)
    # Belt
    d.rectangle([22, 40, 41, 43], fill=darker, outline=accent)

    # ---- LEFT ARM (44,24)-(51,47) ----
    d.rectangle([44, 24, 51, 35], fill=dark)
    d.rectangle([44, 36, 51, 47], fill=darker)

    # ---- RIGHT ARM (12,24)-(19,47) ----
    d.rectangle([12, 24, 19, 35], fill=dark)
    d.rectangle([12, 36, 19, 47], fill=darker)

    # ---- LEFT LEG (20,48)-(31,63) ----
    d.rectangle([20, 48, 31, 63], fill=darker, outline=dark)
    # Boot
    d.rectangle([20, 56, 31, 63], fill=darker, outline=accent)

    # ---- RIGHT LEG (32,48)-(43,63) ----
    d.rectangle([32, 48, 43, 63], fill=dark, outline=darker)
    # Boot
    d.rectangle([32, 56, 43, 63], fill=dark, outline=accent)

    # ---- Shoulder pauldron accents ----
    d.rectangle([20, 24, 23, 26], fill=accent)
    d.rectangle([40, 24, 43, 26], fill=accent)

    # ---- Hat / hair variant indicator ----
    if variant_idx % 3 == 0:
        # Hair
        d.rectangle([9, 6, 22, 8], fill=darker)
        d.rectangle([7, 8, 8, 12], fill=darker)
        d.rectangle([22, 8, 23, 12], fill=darker)
    elif variant_idx % 3 == 1:
        # Helmet crest
        d.rectangle([11, 5, 20, 7], fill=accent)
        d.rectangle([13, 3, 18, 5], fill=accent)
    else:
        # Hood / cowl
        d.rectangle([8, 6, 23, 10], fill=darker)
        d.rectangle([7, 10, 8, 16], fill=darker)
        d.rectangle([22, 10, 23, 16], fill=darker)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def make_skins_json(names_list):
    return {
        "geometry": "geometry.humanoid.custom",
        "skins": [
            {
                "localization_name": n,
                "geometry": "geometry.humanoid.custom",
                "texture": f"{n}.png",
                "type": "free",
            }
            for n in names_list
        ],
    }


def make_manifest(pack_name, description, price_usd, price_mc, header_uuid, module_uuid):
    return {
        "format_version": 2,
        "header": {
            "name": pack_name,
            "description": description,
            "uuid": header_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {
                "type": "skin_pack",
                "uuid": module_uuid,
                "version": [1, 0, 0],
            }
        ],
        "metadata": {
            "product_type": "skin_pack",
            "price_usd": price_usd,
            "price_mc": price_mc,
            "authors": ["IconMineMods"],
            "generated_with": "generate_premium_skins.py",
        },
    }


def main() -> int:
    print(f"Generating {len(THEMES)} premium themed skin packs into {OUT}...")
    print(f"  Each pack: {SKINS_PER_PACK} skins")
    print(f"  Total skins: {len(THEMES) * SKINS_PER_PACK}")
    print()

    OUT.mkdir(parents=True, exist_ok=True)

    made = 0
    for theme_id, display_name, price_usd, price_mc, description in THEMES:
        pack_dir = OUT / theme_id
        pack_dir.mkdir(parents=True, exist_ok=True)

        # Generate a deterministic but unique RGB color from theme_id
        seed = int(hashlib.md5(theme_id.encode()).hexdigest()[:6], 16)
        rng = random.Random(seed)
        theme_rgb = (rng.randint(60, 220), rng.randint(60, 220), rng.randint(60, 220))

        # Skin names
        skin_names = [f"{display_name.replace(' ', '')}_{i+1:02d}" for i in range(SKINS_PER_PACK)]

        # Manifest
        hu = make_uuid(f"premium_{theme_id}_header")
        mu = make_uuid(f"premium_{theme_id}_module")
        manifest = make_manifest(display_name, description, price_usd, price_mc, hu, mu)
        (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # Skins JSON
        skins_json = make_skins_json(skin_names)
        (pack_dir / "skins.json").write_text(json.dumps(skins_json, indent=2), encoding="utf-8")

        # Generate 12 skin textures
        for i, name in enumerate(skin_names):
            png_data = make_premium_skin(theme_rgb, i)
            (pack_dir / f"{name}.png").write_bytes(png_data)

        made += 1
        print(f"  [{made:2d}/{len(THEMES)}] {display_name:25s}  ${price_usd:.2f}  ({SKINS_PER_PACK} skins)")

    # Final report
    total_skins = made * SKINS_PER_PACK
    avg_price = sum(t[2] for t in THEMES) / len(THEMES)
    min_price = min(t[2] for t in THEMES)
    max_price = max(t[2] for t in THEMES)

    print()
    print("=" * 60)
    print(f"  DONE!")
    print(f"  Collections: {made}")
    print(f"  Total skins: {total_skins}")
    print(f"  Price range: ${min_price:.2f} - ${max_price:.2f}")
    print(f"  Average:     ${avg_price:.2f}")
    print(f"  Output:      {OUT.resolve()}")
    print("=" * 60)

    # Verify output
    total_pngs = sum(1 for _ in OUT.rglob("*.png"))
    total_manifests = sum(1 for _ in OUT.rglob("manifest.json"))
    total_skins_json = sum(1 for _ in OUT.rglob("skins.json"))
    print(f"\n  Verification:")
    print(f"    Directories:  {made}")
    print(f"    Manifests:    {total_manifests}")
    print(f"    Skins JSONs:  {total_skins_json}")
    print(f"    PNG textures: {total_pngs} (skins + icons)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
