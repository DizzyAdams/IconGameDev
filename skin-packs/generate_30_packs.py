#!/usr/bin/env python3
"""Generate 30 Minecraft Bedrock skin packs: 10 fantasy, 10 animal, 10 pixel-art retro."""

import json
import os
import uuid
import zipfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: PIL not installed. Creating placeholder textures.")
    # Create minimal valid PNG as placeholder
    import struct
    import zlib

    def make_minimal_png(width, height, r, g, b):
        """Create a minimal valid PNG with a solid color."""
        raw = b''
        for y in range(height):
            raw += b'\x00'  # filter byte
            raw += bytes([r, g, b] * width)
        
        def chunk(ctype, data):
            c = ctype + data
            return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        
        ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        return (b'\x89PNG\r\n\x1a\n' +
                chunk(b'IHDR', ihdr) +
                chunk(b'IDAT', zlib.compress(raw)) +
                chunk(b'IEND', b''))

# ─── THEME DEFINITIONS ───────────────────────────────────────────────────────

FANTASY_PACKS = [
    {
        "name": "Dragon Knights",
        "desc": "Fierce dragon-scale armored warriors",
        "colors": ["#8B0000", "#CD5C5C", "#DC143C", "#B22222", "#FF4500", "#A52A2A"],
        "skins": [
            ("Fire Dragon Knight", "dragon_knight_01"),
            ("Ice Dragon Knight", "dragon_knight_02"),
            ("Storm Dragon Knight", "dragon_knight_03"),
            ("Shadow Dragon Knight", "dragon_knight_04"),
            ("Ancient Dragon Knight", "dragon_knight_05"),
            ("Crystal Dragon Knight", "dragon_knight_06"),
        ]
    },
    {
        "name": "Elven Archers",
        "desc": "Mystical forest elves with ancient bows",
        "colors": ["#228B22", "#32CD32", "#006400", "#3CB371", "#2E8B57", "#556B2F"],
        "skins": [
            ("Moon Elf Archer", "elf_archer_01"),
            ("Sun Elf Archer", "elf_archer_02"),
            ("Wood Elf Archer", "elf_archer_03"),
            ("Dark Elf Archer", "elf_archer_04"),
            ("High Elf Archer", "elf_archer_05"),
            ("Wild Elf Archer", "elf_archer_06"),
        ]
    },
    {
        "name": "Dark Wizards",
        "desc": "Masters of forbidden arcane magic",
        "colors": ["#2F004F", "#4B0082", "#800080", "#483D8B", "#6A0DAD", "#301934"],
        "skins": [
            ("Necromancer", "dark_wizard_01"),
            ("Sorcerer", "dark_wizard_02"),
            ("Warlock", "dark_wizard_03"),
            ("Shadow Mage", "dark_wizard_04"),
            ("Void Caller", "dark_wizard_05"),
            ("Arcane Master", "dark_wizard_06"),
        ]
    },
    {
        "name": "Crystal Guardians",
        "desc": "Protectors empowered by living crystals",
        "colors": ["#00CED1", "#20B2AA", "#48D1CC", "#40E0D0", "#7FFFD4", "#66CDAA"],
        "skins": [
            ("Amethyst Guardian", "crystal_guardian_01"),
            ("Sapphire Guardian", "crystal_guardian_02"),
            ("Emerald Guardian", "crystal_guardian_03"),
            ("Ruby Guardian", "crystal_guardian_04"),
            ("Diamond Guardian", "crystal_guardian_05"),
            ("Topaz Guardian", "crystal_guardian_06"),
        ]
    },
    {
        "name": "Valkyrie Warriors",
        "desc": "Legendary shieldmaidens of the north",
        "colors": ["#C0C0C0", "#DAA520", "#B8860B", "#FFD700", "#F0E68C", "#EEE8AA"],
        "skins": [
            ("Battle Valkyrie", "valkyrie_01"),
            ("Storm Valkyrie", "valkyrie_02"),
            ("War Valkyrie", "valkyrie_03"),
            ("Frost Valkyrie", "valkyrie_04"),
            ("Light Valkyrie", "valkyrie_05"),
            ("Twilight Valkyrie", "valkyrie_06"),
        ]
    },
    {
        "name": "Shadow Demons",
        "desc": "Infernal beings from the abyss",
        "colors": ["#1A0033", "#330000", "#2D004B", "#3D002E", "#1C1C1C", "#4A0033"],
        "skins": [
            ("Hellfire Demon", "shadow_demon_01"),
            ("Night Terror", "shadow_demon_02"),
            ("Abyss Wraith", "shadow_demon_03"),
            ("Dark Fiend", "shadow_demon_04"),
            ("Soul Reaper", "shadow_demon_05"),
            ("Chaos Imp", "shadow_demon_06"),
        ]
    },
    {
        "name": "Forest Spirits",
        "desc": "Ancient nature guardians of the woodlands",
        "colors": ["#8FBC8F", "#6B8E23", "#7CCD7C", "#9ACD32", "#A2CD5A", "#698B22"],
        "skins": [
            ("Dryad", "forest_spirit_01"),
            ("Treant Keeper", "forest_spirit_02"),
            ("Moss Sprite", "forest_spirit_03"),
            ("Fern Warden", "forest_spirit_04"),
            ("Bloom Fairy", "forest_spirit_05"),
            ("Vine Shaman", "forest_spirit_06"),
        ]
    },
    {
        "name": "Phoenix Mages",
        "desc": "Fire-born mages wielding solar magic",
        "colors": ["#FF6347", "#FF4500", "#FF8C00", "#FFA500", "#FFD700", "#FF7F50"],
        "skins": [
            ("Flame Weaver", "phoenix_mage_01"),
            ("Solar Priest", "phoenix_mage_02"),
            ("Ember Mage", "phoenix_mage_03"),
            ("Blaze Caller", "phoenix_mage_04"),
            ("Inferno Lord", "phoenix_mage_05"),
            ("Sun Warden", "phoenix_mage_06"),
        ]
    },
    {
        "name": "Dwarven Forge",
        "desc": "Stout crafters of legendary weapons and armor",
        "colors": ["#A0522D", "#D2691E", "#8B4513", "#CD853F", "#B8860B", "#DAA520"],
        "skins": [
            ("Forge Master", "dwarf_forge_01"),
            ("Battle Smith", "dwarf_forge_02"),
            ("Iron Lord", "dwarf_forge_03"),
            ("Runecrafter", "dwarf_forge_04"),
            ("Hammer Warden", "dwarf_forge_05"),
            ("Deep Miner", "dwarf_forge_06"),
        ]
    },
    {
        "name": "Celestial Angels",
        "desc": "Heavenly beings of pure light and justice",
        "colors": ["#FFFFFF", "#FFF8DC", "#F0FFF0", "#F5FFFA", "#FFFAF0", "#FFFFF0"],
        "skins": [
            ("Seraphim", "celestial_angel_01"),
            ("Archangel", "celestial_angel_02"),
            ("Heavenly Guard", "celestial_angel_03"),
            ("Light Bringer", "celestial_angel_04"),
            ("Divine Judge", "celestial_angel_05"),
            ("Star Herald", "celestial_angel_06"),
        ]
    },
]

ANIMAL_PACKS = [
    {
        "name": "Wolf Pack",
        "desc": "Fierce werewolf warriors of the wild",
        "colors": ["#808080", "#A0A0A0", "#696969", "#C0C0C0", "#505050", "#909090"],
        "skins": [
            ("Alpha Wolf", "wolf_01"),
            ("Snow Wolf", "wolf_02"),
            ("Shadow Wolf", "wolf_03"),
            ("Timber Wolf", "wolf_04"),
            ("Dire Wolf", "wolf_05"),
            ("Arctic Wolf", "wolf_06"),
        ]
    },
    {
        "name": "Dragon Pets",
        "desc": "Adorable baby dragon companions",
        "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"],
        "skins": [
            ("Fire Drake", "dragon_pet_01"),
            ("Frost Drake", "dragon_pet_02"),
            ("Storm Drake", "dragon_pet_03"),
            ("Earth Drake", "dragon_pet_04"),
            ("Light Drake", "dragon_pet_05"),
            ("Shadow Drake", "dragon_pet_06"),
        ]
    },
    {
        "name": "Panda Crew",
        "desc": "Playful panda mascots in martial arts gear",
        "colors": ["#1A1A1A", "#FFFFFF", "#333333", "#F5F5F5", "#2D2D2D", "#E8E8E8"],
        "skins": [
            ("Kung Fu Panda", "panda_01"),
            ("Bamboo Panda", "panda_02"),
            ("Red Panda", "panda_03"),
            ("Snow Panda", "panda_04"),
            ("Ninja Panda", "panda_05"),
            ("Party Panda", "panda_06"),
        ]
    },
    {
        "name": "Fox Squad",
        "desc": "Clever fox tricksters in the wilderness",
        "colors": ["#FF7F50", "#FF6347", "#FF4500", "#FF8C69", "#E9967A", "#FA8072"],
        "skins": [
            ("Fire Fox", "fox_01"),
            ("Arctic Fox", "fox_02"),
            ("Shadow Fox", "fox_03"),
            ("Golden Fox", "fox_04"),
            ("Mystic Fox", "fox_05"),
            ("Spirit Fox", "fox_06"),
        ]
    },
    {
        "name": "Bear Clan",
        "desc": "Powerful bear warriors of the northern peaks",
        "colors": ["#8B4513", "#A0522D", "#6B3A2A", "#D2691E", "#CD853F", "#523A28"],
        "skins": [
            ("Grizzly Bear", "bear_01"),
            ("Polar Bear", "bear_02"),
            ("Brown Bear", "bear_03"),
            ("Black Bear", "bear_04"),
            ("Kodiak Bear", "bear_05"),
            ("Sun Bear", "bear_06"),
        ]
    },
    {
        "name": "Eagle Flight",
        "desc": "Soaring bird mascots with feathered armor",
        "colors": ["#8B4513", "#DAA520", "#A0522D", "#FFD700", "#CD853F", "#B8860B"],
        "skins": [
            ("Bald Eagle", "eagle_01"),
            ("Golden Eagle", "eagle_02"),
            ("Hawk Eye", "eagle_03"),
            ("Falcon Dive", "eagle_04"),
            ("Owl Night", "eagle_05"),
            ("Raven Shadow", "eagle_06"),
        ]
    },
    {
        "name": "Cat Kingdom",
        "desc": "Stylish cat mascots with royal flair",
        "colors": ["#FFA500", "#FF8C00", "#FF7F50", "#DAA520", "#CD853F", "#B8860B"],
        "skins": [
            ("Orange Tabby", "cat_01"),
            ("Siamese Cat", "cat_02"),
            ("Black Panther", "cat_03"),
            ("White Persian", "cat_04"),
            ("Calico Cat", "cat_05"),
            ("Bengal Tiger", "cat_06"),
        ]
    },
    {
        "name": "Shark Attack",
        "desc": "Deep-sea shark mascots and ocean predators",
        "colors": ["#4682B4", "#5F9EA0", "#6495ED", "#87CEEB", "#00BFFF", "#1E90FF"],
        "skins": [
            ("Great White Shark", "shark_01"),
            ("Hammerhead Shark", "shark_02"),
            ("Tiger Shark", "shark_03"),
            ("Blue Shark", "shark_04"),
            ("Mako Shark", "shark_05"),
            ("Bull Shark", "shark_06"),
        ]
    },
    {
        "name": "Owl Wisdom",
        "desc": "Wise owl sorcerers and nocturnal guardians",
        "colors": ["#8B6914", "#6B4226", "#A0522D", "#D2B48C", "#DEB887", "#C4A882"],
        "skins": [
            ("Great Horned Owl", "owl_01"),
            ("Snowy Owl", "owl_02"),
            ("Barn Owl", "owl_03"),
            ("Screech Owl", "owl_04"),
            ("Eagle Owl", "owl_05"),
            ("Burrowing Owl", "owl_06"),
        ]
    },
    {
        "name": "Tiger Strike",
        "desc": "Fearsome tiger mascots with striped fury",
        "colors": ["#FF8C00", "#000000", "#FFA500", "#333333", "#FF7F50", "#1A1A1A"],
        "skins": [
            ("Bengal Tiger", "tiger_01"),
            ("Siberian Tiger", "tiger_02"),
            ("White Tiger", "tiger_03"),
            ("Sabertooth Tiger", "tiger_04"),
            ("Golden Tiger", "tiger_05"),
            ("Sumatran Tiger", "tiger_06"),
        ]
    },
]

PIXEL_ART_PACKS = [
    {
        "name": "Arcade Heroes",
        "desc": "Classic 8-bit pixel heroes from the golden age",
        "colors": ["#FF0000", "#FFFF00", "#00FF00", "#00BFFF", "#FF00FF", "#FFFFFF"],
        "skins": [
            ("Jump Hero", "pixel_arcade_01"),
            ("Blast Hero", "pixel_arcade_02"),
            ("Dash Hero", "pixel_arcade_03"),
            ("Mega Hero", "pixel_arcade_04"),
            ("Ultra Hero", "pixel_arcade_05"),
            ("Turbo Hero", "pixel_arcade_06"),
        ]
    },
    {
        "name": "Retro Racers",
        "desc": "High-speed pixel racers from the arcade era",
        "colors": ["#FF4500", "#FFD700", "#00FF7F", "#1E90FF", "#FF1493", "#9400D3"],
        "skins": [
            ("Speed Racer", "pixel_racer_01"),
            ("Turbo Racer", "pixel_racer_02"),
            ("Nitro Racer", "pixel_racer_03"),
            ("Drift Racer", "pixel_racer_04"),
            ("Boost Racer", "pixel_racer_05"),
            ("Circuit Racer", "pixel_racer_06"),
        ]
    },
    {
        "name": "8-Bit Warriors",
        "desc": "Retro pixel warriors from classic RPGs",
        "colors": ["#4169E1", "#DC143C", "#228B22", "#FFD700", "#8B008B", "#FF6347"],
        "skins": [
            ("Pixel Paladin", "pixel_warrior_01"),
            ("Byte Berserker", "pixel_warrior_02"),
            ("Chip Champion", "pixel_warrior_03"),
            ("Bit Blademaster", "pixel_warrior_04"),
            ("Sprite Samurai", "pixel_warrior_05"),
            ("Nes Knight", "pixel_warrior_06"),
        ]
    },
    {
        "name": "NES Legends",
        "desc": "Iconic pixel legends inspired by classic NES games",
        "colors": ["#E60012", "#00A2E8", "#FFD700", "#A0A0A0", "#50B848", "#FF6B6B"],
        "skins": [
            ("Legend Hero", "pixel_nes_01"),
            ("Legend Mage", "pixel_nes_02"),
            ("Legend Knight", "pixel_nes_03"),
            ("Legend Rogue", "pixel_nes_04"),
            ("Legend Sage", "pixel_nes_05"),
            ("Legend Lord", "pixel_nes_06"),
        ]
    },
    {
        "name": "Pixel Samurai",
        "desc": "Retro pixel samurai from feudal game worlds",
        "colors": ["#C41E3A", "#1C1C1C", "#FFD700", "#8B0000", "#FFA500", "#696969"],
        "skins": [
            ("Pixel Shogun", "pixel_samurai_01"),
            ("Pixel Ronin", "pixel_samurai_02"),
            ("Pixel Ninja", "pixel_samurai_03"),
            ("Pixel Daimyo", "pixel_samurai_04"),
            ("Pixel Sensei", "pixel_samurai_05"),
            ("Pixel Ashigaru", "pixel_samurai_06"),
        ]
    },
    {
        "name": "Retro Robots",
        "desc": "Chunky pixel robots with vintage sci-fi charm",
        "colors": ["#C0C0C0", "#FF6347", "#00BFFF", "#FFD700", "#32CD32", "#FF69B4"],
        "skins": [
            ("Mega Bot", "pixel_robot_01"),
            ("Tank Bot", "pixel_robot_02"),
            ("Laser Bot", "pixel_robot_03"),
            ("Boom Bot", "pixel_robot_04"),
            ("Fly Bot", "pixel_robot_05"),
            ("Power Bot", "pixel_robot_06"),
        ]
    },
    {
        "name": "Gameboy Heroes",
        "desc": "Monochrome pixel heroes in classic gameboy green",
        "colors": ["#306230", "#0F380F", "#7BBD5B", "#A0C870", "#4A7A3A", "#1A4A1A"],
        "skins": [
            ("GB Warrior", "pixel_gb_01"),
            ("GB Mage", "pixel_gb_02"),
            ("GB Thief", "pixel_gb_03"),
            ("GB Archer", "pixel_gb_04"),
            ("GB Monk", "pixel_gb_05"),
            ("GB Sage", "pixel_gb_06"),
        ]
    },
    {
        "name": "Vintage Gamers",
        "desc": "Retro gaming fan pixel skins with controller motifs",
        "colors": ["#FF0000", "#0000FF", "#FFFF00", "#00FF00", "#FF00FF", "#00FFFF"],
        "skins": [
            ("Retro Gamer Red", "pixel_vintage_01"),
            ("Retro Gamer Blue", "pixel_vintage_02"),
            ("Retro Gamer Gold", "pixel_vintage_03"),
            ("Retro Gamer Green", "pixel_vintage_04"),
            ("Retro Gamer Pink", "pixel_vintage_05"),
            ("Retro Gamer Cyan", "pixel_vintage_06"),
        ]
    },
    {
        "name": "Retro Space",
        "desc": "Pixel space explorers from classic sci-fi games",
        "colors": ["#000080", "#191970", "#4169E1", "#0000CD", "#483D8B", "#1E90FF"],
        "skins": [
            ("Space Ace", "pixel_space_01"),
            ("Astro Knight", "pixel_space_02"),
            ("Cosmic Scout", "pixel_space_03"),
            ("Star Ranger", "pixel_space_04"),
            ("Nova Pilot", "pixel_space_05"),
            ("Galaxy Guard", "pixel_space_06"),
        ]
    },
    {
        "name": "Old-School Fighters",
        "desc": "Retro pixel fighters from classic beat-em-ups",
        "colors": ["#FF4500", "#1E90FF", "#32CD32", "#FFD700", "#FF1493", "#8A2BE2"],
        "skins": [
            ("Pixel Brawler", "pixel_fighter_01"),
            ("Pixel Slugger", "pixel_fighter_02"),
            ("Pixel Grappler", "pixel_fighter_03"),
            ("Pixel Striker", "pixel_fighter_04"),
            ("Pixel Master", "pixel_fighter_05"),
            ("Pixel Champ", "pixel_fighter_06"),
        ]
    },
]

ALL_THEMES = [
    ("fantasy", FANTASY_PACKS),
    ("animal", ANIMAL_PACKS),
    ("pixel-art", PIXEL_ART_PACKS),
]


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_skin_texture(width, height, base_rgb, accent_rgb, skin_name, pixel_art=False):
    """Create a Minecraft skin-style texture (64x64 or 64x32)."""
    img = Image.new('RGB', (width, height), base_rgb)
    draw = ImageDraw.Draw(img)

    if pixel_art:
        # Pixel art style: large blocks, limited colors, sharp edges
        # Draw a blocky character outline
        bw, bh = width // 8, height // 8  # 8x8 grid of blocks

        # Head area (rows 0-1)
        for y in range(bh * 1, bh * 3):
            for x in range(bw * 2, bw * 6):
                if x == bw*2 or x == bw*5 or y == bh*1 or y == bh*3-1:
                    draw.point((x, y), fill=accent_rgb)
                else:
                    if (x + y) % 4 == 0:
                        draw.point((x, y), fill=accent_rgb)
                    else:
                        draw.point((x, y), fill=base_rgb)

        # Body (rows 2-4)
        for y in range(bh * 3, bh * 6):
            for x in range(bw * 2, bw * 6):
                c = base_rgb
                if y < bh * 3 + 2 and (x < bw * 3 or x > bw * 4):
                    c = accent_rgb
                elif y >= bh * 4 and y < bh * 5 and (x < bw * 3 or x > bw * 4):
                    c = accent_rgb
                draw.point((x, y), fill=c)

        # Legs (rows 5-7)
        for y in range(bh * 6, bh * 8):
            for x in range(bw * 2, bw * 3):
                draw.point((x, y), fill=base_rgb)
            for x in range(bw * 3, bw * 5):
                draw.point((x, y), fill=accent_rgb)
            for x in range(bw * 5, bw * 6):
                draw.point((x, y), fill=base_rgb)
    else:
        # Regular skin style with some shading and detail
        # Head (rows 0-7, centered)
        hat_color = tuple(min(c + 30, 255) for c in base_rgb)
        skin_tone = tuple(max(c - 20, 0) for c in base_rgb)

        # Head area
        for y in range(8, 24):
            for x in range(16, 48):
                img.putpixel((x, y), hat_color)
        # Face area
        for y in range(12, 22):
            for x in range(20, 44):
                img.putpixel((x, y), skin_tone)
        # Eyes
        eye_color = (255, 255, 255)
        for ey in range(14, 17):
            for ex in [23, 24, 38, 39]:
                img.putpixel((ex, ey), eye_color)
        # Pupils
        pupil_color = accent_rgb
        for py in range(15, 16):
            for px in [24, 39]:
                img.putpixel((px, py), pupil_color)

        # Body/torso
        for y in range(24, 48):
            for x in range(16, 48):
                shade = int(10 * (y - 24) / 24)
                c = tuple(max(v - shade, 0) for v in base_rgb)
                img.putpixel((x, y), c)
        # Belt
        belt_color = tuple(max(c - 40, 0) for c in base_rgb)
        for y in range(40, 44):
            for x in range(18, 46):
                img.putpixel((x, y), belt_color)

        # Arms
        arm_color = tuple(max(c - 15, 0) for c in base_rgb)
        for y in range(24, 48):
            for x in range(8, 16):
                img.putpixel((x, y), arm_color)
            for x in range(48, 56):
                img.putpixel((x, y), arm_color)

        # Legs
        leg_color = tuple(max(c - 25, 0) for c in base_rgb)
        for y in range(48, 64):
            for x in range(20, 30):
                img.putpixel((x, y), leg_color)
            for x in range(34, 44):
                img.putpixel((x, y), leg_color)
        # Boots
        boot_color = tuple(max(c - 50, 0) for c in base_rgb)
        for y in range(58, 64):
            for x in range(20, 30):
                img.putpixel((x, y), boot_color)
            for x in range(34, 44):
                img.putpixel((x, y), boot_color)

    return img


def make_uuid_from_name(name, seed=0):
    """Generate a deterministic v4-like UUID from a name."""
    import hashlib
    raw = hashlib.md5(f"{name}-{seed}".encode()).hexdigest()
    return f"{raw[0:8]}-{raw[8:12]}-4{raw[13:16]}-{raw[16:20]}-{raw[20:32]}"


def generate_pack(base_dir, theme, pack_index, pack_def):
    """Generate one skin pack directory with all files."""
    pack_slug = f"{theme}-pack-{pack_index:02d}"
    pack_dir = base_dir / pack_slug
    skins_dir = pack_dir / "textures" / "skins"
    skins_dir.mkdir(parents=True, exist_ok=True)

    skin_count = len(pack_def["skins"])
    print(f"  Creating {pack_slug}: {pack_def['name']} ({skin_count} skins)")

    # ── skins.json ─────────────────────────────────────────────────────────
    skin_entries = []
    for i, (display_name, skin_id) in enumerate(pack_def["skins"]):
        skin_entries.append({
            "localization_name": f"{pack_def['name'].replace(' ', '')}_{i+1:02d}",
            "geometry": "geometry.humanoid.custom",
            "texture": f"{skin_id}.png",
            "type": "free"
        })

    skins_json = {
        "skins": skin_entries,
        "serialize_name": pack_def["name"],
        "localization_name": pack_def["name"]
    }

    with open(skins_dir.parent.parent / "skins.json", "w", encoding="utf-8") as f:
        json.dump(skins_json, f, indent=2)

    # ── manifest.json ──────────────────────────────────────────────────────
    pack_uuid = make_uuid_from_name(f"{theme}-{pack_index}", 1)
    module_uuid = make_uuid_from_name(f"{theme}-{pack_index}-mod", 2)

    manifest = {
        "format_version": 2,
        "header": {
            "name": pack_def["name"],
            "description": pack_def["desc"],
            "uuid": pack_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "skin_pack",
                "uuid": module_uuid,
                "version": [1, 0, 0]
            }
        ]
    }

    with open(pack_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # ── Texture images ─────────────────────────────────────────────────────
    colors = pack_def["colors"]
    for i, (display_name, skin_id) in enumerate(pack_def["skins"]):
        base_color = hex_to_rgb(colors[i % len(colors)])
        accent_color = hex_to_rgb(colors[(i + 3) % len(colors)])

        # Alternate accented accent
        alt_accent = tuple(min(c + 60, 255) for c in base_color)
        if sum(alt_accent) > sum(base_color) + 60:
            accent_color = alt_accent

        is_pixel = (theme == "pixel-art")

        if HAS_PIL:
            img = create_skin_texture(64, 64, base_color, accent_color, skin_id, pixel_art=is_pixel)
            img.save(skins_dir / f"{skin_id}.png")
        else:
            png_data = make_minimal_png(64, 64, *base_color)
            with open(skins_dir / f"{skin_id}.png", "wb") as f:
                f.write(png_data)

    # ── Pack icon (256x256) ────────────────────────────────────────────────
    if HAS_PIL:
        icon_color = hex_to_rgb(pack_def["colors"][0])
        icon = Image.new('RGB', (256, 256), icon_color)
        draw = ImageDraw.Draw(icon)
        # Simple icon: circle with cross
        draw.ellipse([48, 48, 208, 208], outline=icon_color, width=4)
        draw.rectangle([96, 32, 160, 224], fill=None, outline=icon_color, width=4)
        draw.rectangle([32, 96, 224, 160], fill=None, outline=icon_color, width=4)
        icon.save(pack_dir / "pack_icon.png")
    else:
        png_data = make_minimal_png(256, 256, 100, 100, 100)
        with open(pack_dir / "pack_icon.png", "wb") as f:
            f.write(png_data)

    return pack_dir


def package_mcpack(pack_dir, output_dir):
    """Zip a pack directory into a .mcpack file."""
    mcpack_name = pack_dir.name + ".mcpack"
    mcpack_path = output_dir / mcpack_name

    with zipfile.ZipFile(mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(pack_dir.rglob("*")):
            if file_path.is_dir():
                continue
            if any(p.startswith(".") or p == "__pycache__" for p in file_path.relative_to(pack_dir).parts):
                continue
            zf.write(file_path, str(file_path.relative_to(pack_dir)))

    return mcpack_path


def main():
    base_dir = Path(__file__).resolve().parent
    skin_packs_dir = base_dir  # skin-packs/
    output_dir = skin_packs_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}")
    print()

    all_pack_dirs = []
    pack_count = 0

    for theme, packs in ALL_THEMES:
        print(f"\n{'='*60}")
        print(f"  {theme.upper()} PACKS ({len(packs)} packs)")
        print(f"{'='*60}")

        for idx, pack_def in enumerate(packs, start=1):
            pack_dir = generate_pack(skin_packs_dir, theme, idx, pack_def)
            all_pack_dirs.append(pack_dir)
            pack_count += 1

    print(f"\n{'='*60}")
    print(f"  PACKAGING {pack_count} PACKS as .mcpack")
    print(f"{'='*60}")

    mcpack_files = []
    for pack_dir in all_pack_dirs:
        mcpack_path = package_mcpack(pack_dir, output_dir)
        size_kb = mcpack_path.stat().st_size / 1024
        mcpack_files.append(mcpack_path)
        print(f"  ✓ {mcpack_path.name} ({size_kb:.1f} KB)")

    print(f"\n{'='*60}")
    print(f"  COMPLETE: {len(mcpack_files)} .mcpack files created")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}")

    # Summary
    print(f"\n  SUMMARY:")
    for theme, packs in ALL_THEMES:
        theme_packs = [p for p in mcpack_files if p.name.startswith(f"{theme}-")]
        print(f"    {theme}: {len(theme_packs)} packs")
    total_skins = sum(len(p["skins"]) for _, packs in ALL_THEMES for p in packs)
    print(f"    Total skins: {total_skins}")
    print()


if __name__ == "__main__":
    main()
