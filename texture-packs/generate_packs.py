#!/usr/bin/env python3
"""
Generate 500 Minecraft Bedrock texture packs across 7 categories.
Categories: natural, medieval, modern, fantasy, sci-fi, cartoon, realistic
Resolutions: 256x ($1.99), 512x ($3.99), 1024x ($5.99)
Manifest v2 format.
All textures are procedural (original) - no IP used.
"""

import os
import json
import uuid
import hashlib
import struct
import zlib
from math import sin, cos, floor, pi
import random

random.seed(42)

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(WORKSPACE, "bedrock_packs")

# ─── 7 Categories ──────────────────────────────────────────
CATEGORIES = {
    "natural": {
        "prefix": "NAT",
        "description": "Nature-inspired block textures",
        "color_theme": [(34,139,34), (139,90,43), (100,149,237), (218,165,32)],
    },
    "medieval": {
        "prefix": "MED",
        "description": "Castle & medieval-themed textures",
        "color_theme": [(105,105,105), (139,119,72), (160,82,45), (210,180,140)],
    },
    "modern": {
        "prefix": "MOD",
        "description": "Sleek modern building textures",
        "color_theme": [(200,200,210), (169,169,169), (112,128,144), (245,245,245)],
    },
    "fantasy": {
        "prefix": "FAN",
        "description": "Magical fantasy-themed textures",
        "color_theme": [(147,112,219), (255,20,147), (0,191,255), (255,215,0)],
    },
    "sci-fi": {
        "prefix": "SFI",
        "description": "Science fiction digital textures",
        "color_theme": [(0,150,200), (50,205,50), (255,69,0), (0,255,255)],
    },
    "cartoon": {
        "prefix": "CAR",
        "description": "Vibrant cartoon-style textures",
        "color_theme": [(255,99,71), (255,215,0), (60,179,113), (30,144,255)],
    },
    "realistic": {
        "prefix": "REA",
        "description": "Photorealistic block textures",
        "color_theme": [(101,67,33), (139,137,137), (70,130,180), (128,128,0)],
    },
}

# ─── Procedural Texture Generators ────────────────────────

def _fbm(x, y, seed_val, octaves=4):
    """Simple value noise / fractal Brownian motion."""
    total = 0.0
    amp = 1.0
    freq = 1.0
    for _ in range(octaves):
        n = sin(x * freq + seed_val) * cos(y * freq * 1.3 + seed_val * 0.7)
        total += amp * (n * 0.5 + 0.5)
        amp *= 0.5
        freq *= 2.0
    return max(0.0, min(1.0, total))

def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def _hash_color(x, y, seed_val):
    """Deterministic hash-based color variation."""
    h = hashlib.md5(f"{x}_{y}_{seed_val}".encode()).hexdigest()
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b)

def gen_organic(size, base_color, seed_val):
    """Organic noise pattern (natural, realistic)."""
    img = []
    for y in range(size):
        row = []
        for x in range(size):
            n = _fbm(x / size, y / size, seed_val, 5)
            n2 = _fbm(x / size * 3, y / size * 3, seed_val + 100, 3)
            r = _clamp(base_color[0] * (0.5 + n) + n2 * 30)
            g = _clamp(base_color[1] * (0.5 + n) + n2 * 20)
            b = _clamp(base_color[2] * (0.5 + n) + n2 * 15)
            row.extend([r, g, b, 255])
        img.append(row)
    return img

def gen_brick(size, base_color, seed_val):
    """Brick / stone pattern (medieval, realistic)."""
    brick_h = max(4, size // 8)
    img = []
    for y in range(size):
        row = []
        brick_row = y // brick_h
        offset = (brick_row % 2) * (size // 14)
        for x in range(size):
            bx = (x + offset) % size
            in_mortar = (y % brick_h) < max(1, size // 64) or (bx % (size // 7)) < max(1, size // 64)
            if in_mortar:
                c = (60, 55, 50)
            else:
                n = _fbm(bx / size, y / size, seed_val, 3)
                r = _clamp(base_color[0] * (0.6 + n * 0.4) + _hash_color(bx, y, seed_val)[0] * 0.2)
                g = _clamp(base_color[1] * (0.6 + n * 0.4) + _hash_color(bx, y, seed_val)[1] * 0.2)
                b = _clamp(base_color[2] * (0.6 + n * 0.4) + _hash_color(bx, y, seed_val)[2] * 0.2)
                c = (r, g, b)
            row.extend([*c, 255])
        img.append(row)
    return img

def gen_planks(size, base_color, seed_val):
    """Wood plank pattern."""
    board_w = max(4, size // 16)
    img = []
    for y in range(size):
        row = []
        for x in range(size):
            board = x // board_w
            n = _fbm(x / size, y / size, seed_val, 3)
            grain = sin(y * 0.3 + board * 1.5 + seed_val) * 0.15 + 0.5
            r = _clamp(base_color[0] * (0.5 + n * 0.3 + grain * 0.3))
            g = _clamp(base_color[1] * (0.5 + n * 0.3 + grain * 0.3))
            b = _clamp(base_color[2] * (0.5 + n * 0.3 + grain * 0.2))
            row.extend([r, g, b, 255])
        img.append(row)
    return img

def gen_tech(size, base_color, seed_val):
    """Tech / sci-fi panel pattern."""
    panel_size = max(8, size // 8)
    img = []
    for y in range(size):
        row = []
        for x in range(size):
            panel_x = x // panel_size
            panel_y = y // panel_size
            inside = (x % panel_size) > 1 and (y % panel_size) > 1
            if inside:
                n = _fbm(x / size * 4, y / size * 4, seed_val, 3)
                glow = sin(x * 0.5 + seed_val) * 0.5 + 0.5 if inside and panel_x % 2 == 0 else 0
                r = _clamp(base_color[0] * (0.6 + n * 0.4) + glow * 40)
                g = _clamp(base_color[1] * (0.6 + n * 0.4) + glow * 20)
                b = _clamp(base_color[2] * (0.6 + n * 0.4) + glow * 50)
            else:
                r, g, b = (30, 30, 35)
            row.extend([r, g, b, 255])
        img.append(row)
    return img

def gen_fantasy_scale(size, base_color, seed_val):
    """Fantasy scaly / magical pattern."""
    img = []
    for y in range(size):
        row = []
        for x in range(size):
            sx = x / size * 8
            sy = y / size * 8
            d = sin(sx * 1.5 + seed_val) * cos(sy * 1.5 + seed_val * 0.8)
            n = _fbm(x / size * 4, y / size * 4, seed_val, 4)
            shimmer = sin(x * 0.3 + y * 0.3 + seed_val) * 0.5 + 0.5
            r = _clamp(base_color[0] * (0.4 + n * 0.4 + shimmer * 0.2) + shimmer * 30)
            g = _clamp(base_color[1] * (0.4 + n * 0.3 + d * 0.2) + shimmer * 20)
            b = _clamp(base_color[2] * (0.4 + n * 0.3 + (1-d) * 0.2) + shimmer * 40)
            row.extend([r, g, b, 255])
        img.append(row)
    return img

def gen_cartoon(size, base_color, seed_val):
    """Flat-color cartoon style with sharp outlines."""
    cell_size = max(4, size // 12)
    img = []
    for y in range(size):
        row = []
        for x in range(size):
            cx = x // cell_size
            cy = y // cell_size
            is_edge = (x % cell_size) < 2 or (y % cell_size) < 2
            hc = _hash_color(cx, cy, seed_val)
            r = _clamp(base_color[0] * 0.3 + hc[0] * 0.7) if not is_edge else 20
            g = _clamp(base_color[1] * 0.3 + hc[1] * 0.7) if not is_edge else 20
            b = _clamp(base_color[2] * 0.3 + hc[2] * 0.7) if not is_edge else 20
            row.extend([r, g, b, 255])
        img.append(row)
    return img

TEXTURE_GENERATORS = {
    "natural": [gen_organic, gen_planks, gen_brick],
    "medieval": [gen_brick, gen_planks, gen_organic],
    "modern": [gen_tech, gen_planks, gen_organic],
    "fantasy": [gen_fantasy_scale, gen_organic, gen_brick],
    "sci-fi": [gen_tech, gen_organic, gen_fantasy_scale],
    "cartoon": [gen_cartoon, gen_organic, gen_planks],
    "realistic": [gen_organic, gen_brick, gen_planks],
}

TEXTURE_SLOTS = [
    "dirt", "grass_block_top", "grass_block_side", "stone",
    "cobblestone", "planks_oak", "planks_spruce", "planks_birch",
    "sand", "gravel", "log_oak_top", "log_oak",
    "log_spruce_top", "log_spruce", "log_birch_top", "log_birch",
    "bricks", "stone_bricks", "mossy_stone_bricks",
    "netherrack", "soul_sand", "obsidian",
    "iron_block", "gold_block", "diamond_block",
    "emerald_block", "redstone_block", "lapis_block",
    "coal_block", "quartz_block_side", "quartz_block_top",
    "purpur_block", "end_stone", "prismarine",
    "sea_lantern", "glowstone", "magma",
    "bone_block_side", "bone_block_top", "terracotta",
    "white_wool", "orange_wool", "magenta_wool", "light_blue_wool",
    "yellow_wool", "lime_wool", "pink_wool", "gray_wool",
    "cyan_wool", "purple_wool", "blue_wool", "brown_wool",
    "green_wool", "red_wool", "black_wool",
    "water_still", "water_flow", "lava_still", "lava_flow",
    "ice", "packed_ice", "snow",
]

# ─── Pack Name Generation ─────────────────────────────────

PACK_SUFFIXES = [
    "Pack", "Set", "Collection", "Edition", "Series",
    "Bundle", "Craft", "Vault", "Crate", "World",
]

PACK_THEMES = {
    "natural": ["Verdant", "Terra", "Evergreen", "Wildwood", "Natura", "Flora", "Groves", "Thicket",
                 "Meadow", "Pine", "Cedar", "Briar", "Fern", "Moss", "Dew", "Rain", "Sunstone",
                 "Clay", "Riverstone", "Basalt", "Oasis", "Willow", "Hazel", "Rowan", "Aspen",
                 "Laurel", "Myrtle", "Bramble", "Heath", "Marl"],
    "medieval": ["Castle", "Knight", "Keep", "Fortress", "Citadel", "Crown", "Ironhold", "Stonewall",
                  "Shield", "Crusade", "Longbow", "Tower", "Dungeon", "Rampart", "Throne",
                  "Halberd", "Chainmail", "Battleaxe", "Plate", "Kingdom", "Realm", "Squire",
                  "Steed", "Banner", "Scepter", "Gauntlet", "Armory", "Garrison", "Palisade"],
    "modern": ["Urban", "Metro", "Concrete", "Steel", "Glass", "Loft", "Sleek", "Blueprint",
                "Pulse", "Grid", "Atrium", "Fusion", "Nexus", "Vertex", "Apex",
                "Zenith", "Core", "Facet", "Prism", "Vector", "Radius", "Pivot",
                "Linear", "Flux", "Gear", "Pulse", "Cubic", "Moda", "Trend"],
    "fantasy": ["Mystic", "Arcane", "Enchanted", "Sorcery", "Rune", "Crystal", "Ethereal", "Spellbound",
                 "Mythic", "Astral", "Phantom", "Celestial", "Twilight", "Nebula", "Oracle",
                 "Glimmer", "Aether", "Lunar", "Solaris", "Stardust", "Nova", "Cosmos",
                 "Hex", "Talisman", "Vortex", "Elixir", "Charm", "Enigma", "Aura"],
    "sci-fi": ["Neon", "Cyber", "Digital", "Circuit", "Holo", "Matrix", "Pixel", "Byte",
                "Plasma", "Quantum", "Orbit", "Solar", "Nova", "Starforge", "Data",
                "Hyper", "Volt", "Rocket", "Astro", "Comet", "Photon", "Warp",
                "Drift", "Flux", "Pod", "Signal", "Relay", "Beacon", "Transmit"],
    "cartoon": ["Bubble", "Pop", "Fun", "Jolly", "Cheer", "Zest", "Happy", "Sunny",
                 "Bouncy", "Glee", "Sprinkle", "Candy", "Gummy", "Jelly", "Sugar",
                 "Zing", "Peppy", "Perky", "Lively", "Frisky", "Breezy", "Spry",
                 "Vivid", "Glossy", "Zany", "Goofy", "Bliss", "Zippy", "Mirth"],
    "realistic": ["Photo", "Real", "True", "Vivid", "Ultra", "Detail", "Shade", "Texture",
                   "Nature", "Earth", "Stone", "Woodgrain", "Rustic", "Raw", "Fine",
                   "Prism", "Lens", "Focus", "Depth", "Shadow", "Grain", "Pigment",
                   "Palette", "Render", "Chroma", "Tone", "Value", "Hue", "Spectrum"],
}

PACK_ADJECTIVES = [
    "Ultimate", "Premium", "Elite", "Pro", "Classic",
    "Deluxe", "Supreme", "Vibrant", "Dynamic", "Epic",
    "Pristine", "Artisan", "Master", "Signature", "Exclusive",
    "Heritage", "Legacy", "Essential", "Elemental", "Primal",
]

# ─── PNG Writer (no PIL needed) ───────────────────────────

def _png_chunk(chunk_type, data):
    c = chunk_type + data
    crc = struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    return struct.pack(">I", len(data)) + c + crc

def write_png(path, rgba_pixels, width, height):
    """Write a PNG from a list-of-lists RGBA pixel matrix."""
    raw = b""
    for row in rgba_pixels:
        raw += b"\x00"  # filter byte
        for p in row:
            raw += bytes(p)
    compressed = zlib.compress(raw)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = _png_chunk(b"IDAT", compressed)
    iend = _png_chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(sig)
        f.write(_png_chunk(b"IHDR", ihdr))
        f.write(idat)
        f.write(iend)


# ─── Manifest v2 Generator ───────────────────────────────

def make_manifest(pack_name, description, resolution, category):
    prices = {256: 1.99, 512: 3.99, 1024: 5.99}
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"texturepack.{category}.{pack_name}.{resolution}"))

    manifest = {
        "format_version": 2,
        "header": {
            "name": pack_name,
            "description": f"{description} - {resolution}x Resolution",
            "uuid": uid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
            "pack_category": "texture",
            "price": prices[resolution],
        },
        "modules": [
            {
                "type": "data",
                "uuid": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"data.{uid}")),
                "version": [1, 0, 0],
            }
        ],
        "capabilities": ["texture_packs"],
        "metadata": {
            "authors": ["IconGameDev Studios"],
            "generated_with": "procedural_generator_v2",
            "category": category,
            "resolution": f"{resolution}x",
            "license": "All Rights Reserved - IconGameDev",
        },
    }
    return manifest


# ─── Pack Icon Generator ─────────────────────────────────

def make_pack_icon(size, category, pack_idx):
    """Generate a simple colored icon with a pattern representing the category."""
    cat = CATEGORIES[category]
    base = cat["color_theme"][pack_idx % len(cat["color_theme"])]
    seed = hash(f"{category}_{pack_idx}") & 0x7fffffff

    if category == "natural":
        icon = gen_organic(size, base, seed)
    elif category == "medieval":
        icon = gen_brick(size, base, seed)
    elif category == "modern":
        icon = gen_tech(size, base, seed)
    elif category == "fantasy":
        icon = gen_fantasy_scale(size, base, seed)
    elif category == "sci-fi":
        icon = gen_tech(size, base, seed + 99)
    elif category == "cartoon":
        icon = gen_cartoon(size, base, seed)
    else:  # realistic
        icon = gen_organic(size, base, seed)

    # Overlay a letter indicator
    letter = CATEGORIES[category]["prefix"][0]
    lx = size // 3
    ly = size // 3
    for dy in range(size // 3):
        for dx in range(size // 4):
            px, py = lx + dx, ly + dy
            if px < size and py < size:
                icon[py][px*4+0] = _clamp(icon[py][px*4+0] * 0.3 + 255 * 0.7)
                icon[py][px*4+1] = _clamp(icon[py][px*4+1] * 0.3 + 255 * 0.7)
                icon[py][px*4+2] = _clamp(icon[py][px*4+2] * 0.3 + 255 * 0.7)
    return icon


# ─── Main Generator ──────────────────────────────────────

def generate_all():
    total = 0
    resolutions = [256, 512, 1024]
    price_tiers = {256: [], 512: [], 1024: []}

    packs_per_cat = 500 // len(CATEGORIES)  # ~71 per category
    remainder = 500 - (packs_per_cat * len(CATEGORIES))

    for cat_idx, (category, cat_info) in enumerate(CATEGORIES.items()):
        num_packs = packs_per_cat + (1 if cat_idx < remainder else 0)
        themes = PACK_THEMES[category]
        generators = TEXTURE_GENERATORS[category]

        for p_idx in range(num_packs):
            total += 1
            pack_num = p_idx + 1

            # Pick name
            theme = themes[p_idx % len(themes)]
            adjective = PACK_ADJECTIVES[(p_idx + cat_idx) % len(PACK_ADJECTIVES)]
            suffix = PACK_SUFFIXES[(p_idx + cat_idx * 3) % len(PACK_SUFFIXES)]
            pack_name = f"{adjective} {theme} {suffix}"
            if cat_idx % 2 == 0:
                pack_name = f"{theme} {suffix}"
            if p_idx % 5 == 0:
                pack_name = f"{cat_info['prefix']}{pack_num:03d} - {theme}"

            for res_idx, resolution in enumerate(resolutions):
                price = {256: 1.99, 512: 3.99, 1024: 5.99}[resolution]

                # Create pack directory
                pack_dir = os.path.join(OUTPUT_DIR, f"{cat_info['prefix']}{pack_num:03d}_{resolution}x")
                textures_dir = os.path.join(pack_dir, "textures", "blocks")

                # Store in price tier
                price_tiers[resolution].append(pack_name)

                # Write manifest
                desc = f"A {resolution}x {category} texture pack - {cat_info['description']}"
                manifest = make_manifest(pack_name, desc, resolution, category)
                with open(os.path.join(pack_dir, "manifest.json"), "w") as f:
                    json.dump(manifest, f, indent=2)

                # Write pack icon
                icon_size = min(256, resolution)
                icon = make_pack_icon(icon_size, category, pack_num)
                write_png(os.path.join(pack_dir, "pack_icon.png"), icon, icon_size, icon_size)

                # Write block textures (procedural)
                textures_per_pack = random.randint(15, 25)
                for t_idx in range(textures_per_pack):
                    slot = TEXTURE_SLOTS[(t_idx + pack_num) % len(TEXTURE_SLOTS)]
                    gen = generators[(t_idx + p_idx * 2) % len(generators)]
                    base = cat_info["color_theme"][(t_idx + pack_num) % len(cat_info["color_theme"])]
                    seed = hash(f"{category}_{pack_num}_{t_idx}_{resolution}") & 0x7fffffff
                    pixels = gen(resolution, base, seed)
                    write_png(os.path.join(textures_dir, f"{slot}.png"), pixels, resolution, resolution)

                # Also do ui/ and environment/ textures
                env_dir = os.path.join(pack_dir, "textures", "environment")
                ui_dir = os.path.join(pack_dir, "textures", "ui")
                os.makedirs(env_dir, exist_ok=True)
                os.makedirs(ui_dir, exist_ok=True)

                # Environment textures (sky, clouds, moon, sun)
                env_slots = ["sun", "moon", "moon_phases", "clouds", "rain"]
                for es in env_slots:
                    base = cat_info["color_theme"][0]
                    seed = hash(f"env_{category}_{pack_num}_{es}_{resolution}") & 0x7fffffff
                    pixels = gen_organic(resolution // 2, base, seed)
                    write_png(os.path.join(env_dir, f"{es}.png"), pixels, resolution // 2, resolution // 2)

                # UI textures (blur, vignette)
                ui_size = min(64, resolution // 4)
                pixels = gen_organic(ui_size, (50, 50, 50), seed=pack_num)
                write_png(os.path.join(ui_dir, "blur.png"), pixels, ui_size, ui_size)

    return total, price_tiers


if __name__ == "__main__":
    print("=" * 60)
    print("IconGameDev - Bedrock Texture Pack Generator")
    print("=" * 60)
    print(f"Output: {OUTPUT_DIR}")
    print()

    total, price_tiers = generate_all()

    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total texture packs generated: {total}")
    print()
    print("Price Breakdown:")
    for res, packs in price_tiers.items():
        price = {256: 1.99, 512: 3.99, 1024: 5.99}[res]
        print(f"  {res}x - ${price:.2f} - {len(packs)} packs")
    print()
    print(f"Total estimated value: ${sum(len(v) * {256: 1.99, 512: 3.99, 1024: 5.99}[k] for k, v in price_tiers.items()):.2f}")
    print()
    print("Categories:")
    for cat in CATEGORIES:
        print(f"  - {cat}: {CATEGORIES[cat]['description']}")

    # Write summary file
    summary = {
        "total_packs": total,
        "price_tiers": {str(k): {"count": len(v), "price": {256: 1.99, 512: 3.99, 1024: 5.99}[k]} for k, v in price_tiers.items()},
        "categories": list(CATEGORIES.keys()),
        "estimated_total_value": sum(len(v) * {256: 1.99, 512: 3.99, 1024: 5.99}[k] for k, v in price_tiers.items()),
    }
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to: {os.path.join(OUTPUT_DIR, 'summary.json')}")
