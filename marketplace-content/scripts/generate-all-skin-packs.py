"""Generate all 8 Minecraft Bedrock skin packs with textures."""
from PIL import Image
import os, json, random

random.seed(42)
BASE = os.path.join(os.path.dirname(__file__), '..')
SKIN_PACKS_DIR = os.path.join(BASE, 'skin-packs')

PACK_DEFS = [
    {
        "dir": "warriors-vol2",
        "manifest_name": "Warriors Vol.2",
        "manifest_desc": "10 epic original warrior skins! Includes Blaze, Frost, Storm, and more!",
        "price": "$2.99 (490 MC)",
        "header_uuid": "5a6b7c8d-9e0f-1a2b-3c4d-5e6f7a8b9c0d",
        "module_uuid": "3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d",
        "skins": [
            ("Blaze", (255, 192, 203), (255, 255, 255)),
            ("Frost", (255, 165, 0), (0, 100, 255)),
            ("Dragon", (255, 0, 0), (255, 215, 0)),
            ("Pirate", (255, 255, 0), (0, 0, 0)),
            ("Titan", (0, 100, 255), (255, 255, 255)),
            ("Wizard", (128, 0, 128), (192, 192, 192)),
            ("Hexweaver", (0, 0, 0), (0, 255, 0)),
            ("Cyber", (0, 255, 255), (255, 0, 255)),
            ("MagicalGirl", (255, 192, 203), (255, 215, 0)),
            ("Beast", (139, 69, 19), (255, 0, 0)),
        ]
    },
    {
        "dir": "halloween-2026",
        "manifest_name": "Halloween 2026",
        "manifest_desc": "12 spooky Halloween skins! Zombies, Vampires, Werewolves, and more!",
        "price": "$2.99",
        "header_uuid": "6b7c8d9e-0f1a-2b3c-4d5e-6f7a8b9c0d1e",
        "module_uuid": "4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e",
        "skins": [
            ("Zombie", (0, 128, 0), (128, 128, 128)),
            ("Vampire", (128, 0, 0), (0, 0, 0)),
            ("Werewolf", (128, 128, 128), (139, 90, 43)),
            ("Witch", (128, 0, 128), (0, 128, 0)),
            ("Skeleton", (255, 255, 255), (0, 0, 0)),
            ("Ghost", (255, 255, 255), (0, 100, 255)),
            ("Pumpkin", (255, 165, 0), (0, 0, 0)),
            ("Devil", (255, 0, 0), (255, 215, 0)),
            ("Mummy", (245, 245, 220), (139, 90, 43)),
            ("Clown", (255, 0, 0), (255, 255, 255)),
            ("Reaper", (0, 0, 0), (128, 128, 128)),
            ("BlackCat", (0, 0, 0), (255, 165, 0)),
        ]
    },
    {
        "dir": "christmas-2026",
        "manifest_name": "Christmas 2026",
        "manifest_desc": "12 festive Christmas skins! Santa, Elves, Reindeer, and more!",
        "price": "$2.99",
        "header_uuid": "7c8d9e0f-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
        "module_uuid": "5c6d7e8f-9a0b-1c2d-3e4f-5a6b7c8d9e0f",
        "skins": [
            ("Santa", (255, 0, 0), (255, 255, 255)),
            ("Elf", (0, 128, 0), (255, 0, 0)),
            ("Reindeer", (139, 69, 19), (255, 0, 0)),
            ("Snowman", (255, 255, 255), (0, 100, 255)),
            ("Gingerbread", (205, 133, 63), (255, 255, 255)),
            ("Nutcracker", (255, 0, 0), (255, 215, 0)),
            ("Angel", (255, 255, 255), (255, 215, 0)),
            ("Grinch", (0, 128, 0), (255, 0, 0)),
            ("Penguin", (0, 0, 0), (255, 255, 255)),
            ("PolarBear", (255, 255, 255), (128, 128, 128)),
            ("Caroler", (0, 0, 255), (192, 192, 192)),
            ("Star", (255, 215, 0), (255, 255, 0)),
        ]
    },
    {
        "dir": "superheroes",
        "manifest_name": "Superheroes",
        "manifest_desc": "10 original superhero skins! StarKnight, FlameHero, IceGuardian, and more!",
        "price": "$2.99",
        "header_uuid": "8d9e0f1a-2b3c-4d5e-6f7a-8b9c0d1e2f3a",
        "module_uuid": "6d7e8f9a-0b1c-2d3e-4f5a-6b7c8d9e0f1a",
        "skins": [
            ("StarKnight", (0, 0, 255), (255, 215, 0)),
            ("FlameHero", (255, 0, 0), (255, 255, 0)),
            ("IceGuardian", (0, 255, 255), (255, 255, 255)),
            ("ThunderStrike", (255, 255, 0), (0, 0, 0)),
            ("ShadowViper", (0, 0, 0), (128, 0, 128)),
            ("IronShield", (128, 128, 128), (0, 0, 255)),
            ("CrystalWing", (255, 192, 203), (255, 255, 255)),
            ("StormBreaker", (0, 100, 255), (255, 255, 255)),
            ("NightBlade", (0, 0, 139), (128, 128, 128)),
            ("SunBringer", (255, 165, 0), (255, 0, 0)),
        ]
    },
    {
        "dir": "animals",
        "manifest_name": "Animals",
        "manifest_desc": "12 amazing animal skins! Wolves, Foxes, Pandas, Tigers, and more!",
        "price": "$1.99",
        "header_uuid": "9e0f1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b",
        "module_uuid": "7e8f9a0b-1c2d-3e4f-5a6b-7c8d9e0f1a2b",
        "skins": [
            ("Wolf", (128, 128, 128), (255, 255, 255)),
            ("Fox", (255, 165, 0), (255, 255, 255)),
            ("Panda", (0, 0, 0), (255, 255, 255)),
            ("Tiger", (255, 165, 0), (0, 0, 0)),
            ("Lion", (255, 215, 0), (139, 69, 19)),
            ("Bear", (139, 69, 19), (0, 0, 0)),
            ("Eagle", (139, 69, 19), (255, 255, 255)),
            ("Shark", (0, 100, 255), (128, 128, 128)),
            ("Dragon", (255, 0, 0), (255, 215, 0)),
            ("Phoenix", (255, 0, 0), (255, 165, 0)),
            ("Unicorn", (255, 255, 255), (255, 192, 203)),
            ("Cat", (255, 165, 0), (0, 0, 0)),
        ]
    },
    {
        "dir": "pixel-art",
        "manifest_name": "Pixel Art",
        "manifest_desc": "8 retro 8-bit pixel art skins! Heroes, Mages, Knights, and more!",
        "price": "$1.99",
        "header_uuid": "0f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
        "module_uuid": "8f9a0b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c",
        "skins": [
            ("Hero", (0, 0, 255), (139, 69, 19)),
            ("Mage", (128, 0, 128), (128, 128, 128)),
            ("Knight", (192, 192, 192), (0, 0, 255)),
            ("Rogue", (0, 0, 0), (128, 128, 128)),
            ("Robot", (128, 128, 128), (0, 255, 255)),
            ("Alien", (0, 128, 0), (128, 0, 128)),
            ("Ninja", (0, 0, 139), (255, 0, 0)),
            ("Zombie", (0, 128, 0), (128, 128, 128)),
        ]
    },
    {
        "dir": "fantasy-creatures",
        "manifest_name": "Fantasy Creatures",
        "manifest_desc": "10 mythical fantasy creature skins! Dragons, Phoenixes, Griffins, and more!",
        "price": "$2.99",
        "header_uuid": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
        "module_uuid": "9a0b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c4d",
        "skins": [
            ("Dragon", (255, 0, 0), (255, 215, 0)),
            ("Phoenix", (255, 0, 0), (255, 165, 0)),
            ("Griffin", (139, 69, 19), (255, 255, 255)),
            ("Mermaid", (0, 0, 255), (0, 128, 0)),
            ("Centaur", (139, 69, 19), (0, 128, 0)),
            ("Fairy", (255, 192, 203), (255, 255, 255)),
            ("Golem", (128, 128, 128), (139, 69, 19)),
            ("Hydra", (0, 128, 0), (0, 0, 255)),
            ("Chimera", (128, 0, 128), (0, 128, 0)),
            ("Pegasus", (255, 255, 255), (0, 0, 255)),
        ]
    },
    {
        "dir": "summer-2026",
        "manifest_name": "Summer 2026",
        "manifest_desc": "10 sunny summer skins! Beach Bums, Surfers, Divers, and more!",
        "price": "$1.99",
        "header_uuid": "2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e",
        "module_uuid": "0b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d5e",
        "skins": [
            ("BeachBum", (255, 255, 0), (0, 0, 255)),
            ("Surfer", (0, 0, 255), (255, 255, 255)),
            ("Diver", (0, 0, 255), (0, 128, 128)),
            ("Lifeguard", (255, 0, 0), (255, 255, 255)),
            ("Tourist", (0, 128, 0), (139, 69, 19)),
            ("Sailor", (255, 255, 255), (0, 0, 128)),
            ("Fisher", (0, 0, 255), (139, 69, 19)),
            ("Swimmer", (0, 0, 255), (0, 0, 0)),
            ("Islander", (0, 128, 0), (255, 255, 0)),
            ("Sunset", (255, 165, 0), (255, 192, 203)),
        ]
    },
]



def _valid_color(c):
    """Validate color tuple: must be 3 integers in 0-255 range."""
    if not isinstance(c, (tuple, list)) or len(c) != 3:
        return False
    return all(isinstance(v, int) and 0 <= v <= 255 for v in c)


def generate_texture(primary, secondary, is_8bit=False):
    if not _valid_color(primary) or not _valid_color(secondary):
        raise ValueError(f"Invalid color: {primary} / {secondary}")
    img = Image.new('RGBA', (64, 64), (*primary, 255))
    pixels = img.load()
    if is_8bit:
        block_size = 8
        for bx in range(8):
            for by in range(8):
                if (bx + by) % 3 == 0 or (bx == by) or (bx + by == 7):
                    color = secondary
                else:
                    color = primary
                for dx in range(block_size):
                    for dy in range(block_size):
                        px = bx * block_size + dx
                        py = by * block_size + dy
                        pixels[px, py] = (*color, 255)
        for i in range(64):
            pixels[i, 0] = (0, 0, 0, 255)
            pixels[i, 63] = (0, 0, 0, 255)
            pixels[0, i] = (0, 0, 0, 255)
            pixels[63, i] = (0, 0, 0, 255)
    else:
        pattern = random.choice(['stripe_h', 'stripe_v', 'check', 'diag'])
        for x in range(64):
            for y in range(64):
                r, g, b, a = pixels[x, y]
                use_sec = False
                if pattern == 'stripe_h' and (y // 4) % 2 == 0:
                    use_sec = True
                elif pattern == 'stripe_v' and (x // 4) % 2 == 0:
                    use_sec = True
                elif pattern == 'check' and ((x // 4) + (y // 4)) % 2 == 0:
                    use_sec = True
                elif pattern == 'diag' and ((x + y) // 6) % 2 == 0:
                    use_sec = True
                if use_sec:
                    sr, sg, sb = secondary
                    blend = 0.85
                    pixels[x, y] = (
                        int(r * (1 - blend) + sr * blend),
                        int(g * (1 - blend) + sg * blend),
                        int(b * (1 - blend) + sb * blend),
                        255,
                    )
    return img


def generate_icon(primary, secondary):
    if not _valid_color(primary) or not _valid_color(secondary):
        raise ValueError(f"Invalid color: {primary} / {secondary}")
    icon = Image.new('RGBA', (300, 300), (*primary, 255))
    ipixels = icon.load()
    for x in range(300):
        for y in range(300):
            r, g, b, a = ipixels[x, y]
            cx, cy = 150, 150
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist < 100:
                angle = (x + y) * 0.05
                sr = int(primary[0] * 0.5 + secondary[0] * 0.5 * ((angle * 0.7) % 1))
                sg = int(primary[1] * 0.5 + secondary[1] * 0.5 * ((angle * 0.7) % 1))
                sb = int(primary[2] * 0.5 + secondary[2] * 0.5 * ((angle * 0.7) % 1))
                ipixels[x, y] = (min(sr + 30, 255), min(sg + 30, 255), min(sb + 30, 255), 255)
    return icon


def make_manifest(pack):
    return {
        "format_version": 2,
        "header": {
            "name": pack["manifest_name"],
            "description": pack["manifest_desc"],
            "uuid": pack["header_uuid"],
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {
                "type": "skin_pack",
                "uuid": pack["module_uuid"],
                "version": [1, 0, 0],
            }
        ],
    }


def make_skins_json(pack):
    skins = []
    for name, primary, secondary in pack["skins"]:
        skins.append({
            "localization_name": name,
            "geometry": "geometry.humanoid.custom",
            "texture": f"{name}.png",
            "type": "free",
        })
    return {
        "skins": skins,
        "serialize_name": pack["manifest_name"],
        "localization_name": pack["manifest_name"],
    }


def main():
    for pack in PACK_DEFS:
        pack_dir = os.path.join(SKIN_PACKS_DIR, pack["dir"])
        skins_dir = os.path.join(pack_dir, "textures", "skins")
        os.makedirs(skins_dir, exist_ok=True)

        is_pixel = pack["dir"] == "pixel-art"
        all_colors = [c[1] for c in pack["skins"]] + [c[2] for c in pack["skins"]]

        for name, primary, secondary in pack["skins"]:
            img = generate_texture(primary, secondary, is_8bit=is_pixel)
            img.save(os.path.join(skins_dir, f"{name}.png"))
            print(f"  {pack['dir']}/{name}.png")

        if all_colors:
            icon_primary = all_colors[len(all_colors) // 2]
            icon_secondary = all_colors[-1]
            icon = generate_icon(icon_primary, icon_secondary)
            icon.save(os.path.join(skins_dir, "icon.png"))
            print(f"  {pack['dir']}/icon.png")

        with open(os.path.join(pack_dir, "manifest.json"), "w") as f:
            json.dump(make_manifest(pack), f, indent=2)
        print(f"  {pack['dir']}/manifest.json")

        with open(os.path.join(pack_dir, "skins.json"), "w") as f:
            json.dump(make_skins_json(pack), f, indent=2)
        print(f"  {pack['dir']}/skins.json")

        print(f"  Done: {pack['dir']}")


if __name__ == "__main__":
    main()
