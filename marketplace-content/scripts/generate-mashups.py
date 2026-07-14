"""Generate 3 Minecraft Bedrock mashup packs (skin + texture + world bundles)."""
from PIL import Image, ImageDraw
import os, json

BASE = os.path.join(os.path.dirname(__file__), '..')
MASHUP_DIR = os.path.join(BASE, 'mashup-packs')
SKIN_PACKS_DIR = os.path.join(BASE, 'skin-packs')
TEXTURE_PACKS_DIR = os.path.join(BASE, 'texture-packs')
WORLD_DIR = os.path.join(BASE, 'world-templates')

MASHUP_DEFS = [
    {
        "dir": "medieval-kingdoms",
        "manifest_name": "Medieval Kingdoms Mashup",
        "manifest_desc": "Everything medieval! Medieval Knights skins + matching texture pack + kingdom world.",
        "price": "$5.99",
        "header_uuid": "9c0d1e2f-3a4b-5c6d-7e8f-9a0b1c2d3e4f",
        "module_uuid": "0d1e2f3a-4b5c-6d7e-8f9a-0b1c2d3e4f5a",
        "dependencies": [
            {"uuid": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d", "version": [1, 0, 0]},
            {"uuid": "3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f", "version": [1, 0, 0]},
            {"uuid": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e", "version": [1, 0, 0]},
        ],
        "icon": "gold_shield_on_red",
    },
    {
        "dir": "anime-world",
        "manifest_name": "Anime World Mashup",
        "manifest_desc": "Full anime experience! Anime skins + dark texture + Japanese-style world.",
        "price": "$5.99",
        "header_uuid": "0d1e2f3a-4b5c-6d7e-8f9a-0b1c2d3e4f5b",
        "module_uuid": "1e2f3a4b-5c6d-7e8f-9a0b-1c2d3e4f5a6b",
        "dependencies": [
            {"uuid": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d", "version": [1, 0, 0]},
            {"uuid": "3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f", "version": [1, 0, 0]},
            {"uuid": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f", "version": [1, 0, 0]},
        ],
        "icon": "cherry_blossom_on_purple",
    },
    {
        "dir": "halloween-night",
        "manifest_name": "Halloween Night Mashup",
        "manifest_desc": "Spookiest Halloween bundle! Halloween skins + dark texture + haunted world.",
        "price": "$6.99",
        "header_uuid": "1e2f3a4b-5c6d-7e8f-9a0b-1c2d3e4f5a6c",
        "module_uuid": "2f3a4b5c-6d7e-8f9a-0b1c-2d3e4f5a6b7c",
        "dependencies": [
            {"uuid": "6b7c8d9e-0f1a-2b3c-4d5e-6f7a8b9c0d1e", "version": [1, 0, 0]},
            {"uuid": "3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f", "version": [1, 0, 0]},
            {"uuid": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a", "version": [1, 0, 0]},
        ],
        "icon": "pumpkin_on_black",
    },
]


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
                "type": "resources",
                "uuid": pack["module_uuid"],
                "version": [1, 0, 0],
            }
        ],
        "dependencies": pack["dependencies"],
        "metadata": {
            "product_type": "mashup",
            "prices": [pack["price"]],
        },
    }


def draw_gold_shield_on_red():
    img = Image.new('RGBA', (256, 256), (204, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = 128, 128
    # Shield shape polygon
    shield = [
        (cx - 80, cy - 90), (cx + 80, cy - 90),
        (cx + 90, cy - 20), (cx + 70, cy + 50),
        (cx + 40, cy + 90), (cx, cy + 100),
        (cx - 40, cy + 90), (cx - 70, cy + 50),
        (cx - 90, cy - 20),
    ]
    draw.polygon(shield, fill=(255, 215, 0, 255), outline=(255, 180, 0, 255), width=4)
    # Inner cross
    draw.rectangle([cx - 20, cy - 60, cx + 20, cy + 40], fill=(255, 180, 0, 255))
    draw.rectangle([cx - 50, cy - 20, cx + 50, cy + 10], fill=(255, 180, 0, 255))
    return img


def draw_cherry_blossom_on_purple():
    img = Image.new('RGBA', (256, 256), (45, 0, 77, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = 128, 128
    # 5 petals around center
    import math
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        px = cx + int(50 * math.cos(angle))
        py = cy + int(50 * math.sin(angle))
        # Ellipse for each petal
        bbox = [px - 35, py - 45, px + 35, py + 15]
        draw.ellipse(bbox, fill=(255, 150, 200, 255), outline=(255, 100, 180, 255), width=2)
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 200, 220, 255))
    return img


def draw_pumpkin_on_black():
    img = Image.new('RGBA', (256, 256), (26, 26, 26, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = 128, 128
    # Pumpkin body - 3 overlapping ellipses
    for offset in [-20, 0, 20]:
        draw.ellipse([cx - 55 + offset, cy - 60, cx + 55 + offset, cy + 60],
                     fill=(255, 140, 0, 255), outline=(200, 100, 0, 255), width=3)
    # Stem
    draw.rectangle([cx - 8, cy - 80, cx + 8, cy - 60], fill=(50, 120, 20, 255))
    # Carved face
    # Eyes
    draw.polygon([(cx - 35, cy - 30), (cx - 20, cy - 10), (cx - 40, cy - 10)], fill=(26, 26, 26, 255))
    draw.polygon([(cx + 35, cy - 30), (cx + 20, cy - 10), (cx + 40, cy - 10)], fill=(26, 26, 26, 255))
    # Nose
    draw.polygon([(cx, cy - 5), (cx - 10, cy + 10), (cx + 10, cy + 10)], fill=(26, 26, 26, 255))
    # Mouth
    draw.polygon([
        (cx - 40, cy + 15), (cx - 25, cy + 35),
        (cx - 10, cy + 20), (cx + 10, cy + 20),
        (cx + 25, cy + 35), (cx + 40, cy + 15),
    ], fill=(26, 26, 26, 255))
    # Glow effect around eyes/mouth
    glow = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - 50, cy - 40, cx + 50, cy + 50], fill=(255, 200, 50, 30))
    img = Image.alpha_composite(img, glow)
    return img


ICON_FUNCS = {
    "gold_shield_on_red": draw_gold_shield_on_red,
    "cherry_blossom_on_purple": draw_cherry_blossom_on_purple,
    "pumpkin_on_black": draw_pumpkin_on_black,
}


def main():
    os.makedirs(MASHUP_DIR, exist_ok=True)

    descriptions = []
    for pack in MASHUP_DEFS:
        pack_dir = os.path.join(MASHUP_DIR, pack["dir"])
        os.makedirs(pack_dir, exist_ok=True)

        # Write manifest
        with open(os.path.join(pack_dir, "manifest.json"), "w") as f:
            json.dump(make_manifest(pack), f, indent=2)
        print(f"  {pack['dir']}/manifest.json")

        # Generate icon
        icon_func = ICON_FUNCS[pack["icon"]]
        icon = icon_func()
        icon.save(os.path.join(pack_dir, "pack_icon.png"))
        print(f"  {pack['dir']}/pack_icon.png")

        # Collect description for combined file
        descriptions.append(f"{pack['manifest_name']} ({pack['price']})")
        descriptions.append(f"  {pack['manifest_desc']}")
        descriptions.append(f"  Header UUID: {pack['header_uuid']}")
        descriptions.append(f"  Module UUID: {pack['module_uuid']}")
        descriptions.append(f"  Dependencies:")
        for dep in pack["dependencies"]:
            descriptions.append(f"    - {dep['uuid']} v{dep['version'][0]}.{dep['version'][1]}.{dep['version'][2]}")
        descriptions.append("")

        print(f"  Done: {pack['dir']}")

    # Write combined description
    desc_path = os.path.join(MASHUP_DIR, "mashup-packs-description.txt")
    with open(desc_path, "w") as f:
        f.write("Minecraft Bedrock Mashup Packs\n")
        f.write("=" * 50 + "\n\n")
        for line in descriptions:
            f.write(line + "\n")
    print(f"  mashup-packs-description.txt")


if __name__ == "__main__":
    main()
