"""Generate all Bedrock content: behavior packs, mashup packs, and .mcpack packages.
Pure standard library — no PIL required (icons are generated as raw PNGs)."""
import os
import json
import struct
import zlib
import io
import zipfile

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'marketplace-content')
BP_DIR = os.path.join(BASE, 'behavior-packs')
MASHUP_DIR = os.path.join(BASE, 'mashup-packs')
OUTPUT_DIR = os.path.join(BASE, 'output')
SKIN_PACKS_DIR = os.path.join(BASE, 'skin-packs')

# ── helpers ──────────────────────────────────────────────────────────────

def make_uuid(seed):
    h = hash(str(seed)) & 0xFFFFFFFFFFFFFFFF
    return (f"f{h>>48:04x}{h>>32&0xFFFF:04x}-{h>>16&0xFFFF:04x}-{h&0xFFFF:04x}-"
            f"{hash(str(seed)+'x')&0xFFFF:04x}-{hash(str(seed)+'y')&0xFFFFFFFFFF:012x}")

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def make_manifest(addon, module_type="data"):
    uid = make_uuid(addon["id"])
    muid = make_uuid(addon["id"] + "_mod")
    manifest = {
        "format_version": 2,
        "header": {
            "name": addon["name"],
            "description": addon["desc"],
            "uuid": uid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [{"type": module_type, "uuid": muid, "version": [1, 0, 0]}],
        "metadata": {
            "authors": ["Bedrock Mass Automation"],
            "product_type": "behavior_pack" if module_type == "data" else "mashup",
            "price": addon.get("price", "$2.99")
        }
    }
    if "dependencies" in addon:
        manifest["dependencies"] = addon["dependencies"]
    return manifest

# ── raw PNG generator (no PIL) ──────────────────────────────────────────

def make_png_raw(width, height, rgba_pixels):
    """Create a PNG from raw RGBA pixel data (bytes)."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    # IHDR
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    # IDAT — raw pixel data, filter byte 0 per row
    raw = b''
    stride = width * 4
    for y in range(height):
        raw += b'\x00' + rgba_pixels[y * stride:(y + 1) * stride]
    compressed = zlib.compress(raw)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

def gen_icon_shield():
    w, h = 256, 256
    pixels = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            cx, cy = x - 128, y - 128
            r, g, b, a = 204, 0, 0, 255  # red bg
            # Shield shape
            if (abs(cx) < 80 and cy < -20 and cy > -90) or \
               (cx < 90 and cx > -90 and cy < 50 and cy > -20 and abs(cx) < 90 - (cy+20)*0.8) or \
               (cy < 90 and cy >= 50 and abs(cx) < 70 - (cy-50)*0.75):
                # Gold shield
                r, g, b = 255, 215, 0
                # Cross
                if abs(cx) < 20 and cy > -60 and cy < 40:
                    r, g, b = 255, 180, 0
                if abs(cy) < 15 and abs(cx) < 50:
                    r, g, b = 255, 180, 0
            idx = (y * w + x) * 4
            pixels[idx:idx+4] = r, g, b, a
    return make_png_raw(w, h, bytes(pixels))

def gen_icon_cherry():
    import math
    w, h = 256, 256
    pixels = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            cx, cy = x - 128, y - 128
            r, g, b, a = 45, 0, 77, 255  # dark purple
            # 5 petals
            for i in range(5):
                angle = math.radians(i * 72 - 90)
                px = int(50 * math.cos(angle))
                py = int(50 * math.sin(angle))
                dx, dy = cx - px, cy - py
                if (dx*dx)/(35*35) + (dy*dy)/(30*30) <= 1:
                    r, g, b = 255, 150, 200
                    if (dx*dx)/(32*32) + (dy*dy)/(27*27) <= 1:
                        r, g, b = 255, 180, 210
            # Center
            if cx*cx + cy*cy <= 12*12:
                r, g, b = 255, 200, 220
            idx = (y * w + x) * 4
            pixels[idx:idx+4] = r, g, b, a
    return make_png_raw(w, h, bytes(pixels))

def gen_icon_pumpkin():
    w, h = 256, 256
    pixels = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            cx, cy = x - 128, y - 128
            r, g, b, a = 26, 26, 26, 255  # black bg
            in_pumpkin = False
            for offset in [-20, 0, 20]:
                ox = cx - offset
                if (ox*ox)/(55*55) + (cy*cy)/(60*60) <= 1:
                    in_pumpkin = True
            if in_pumpkin:
                r, g, b = 255, 140, 0
            # Stem
            if abs(cx) < 8 and cy < -60 and cy > -80:
                r, g, b = 50, 120, 20
            # Carved face (black triangles)
            if cy > -10:
                # Eyes
                if (cx + 35)**2 + (cy+20)**2 < 200 or (cx - 35)**2 + (cy+20)**2 < 200:
                    r, g, b = 26, 26, 26
                # Mouth
                if abs(cx) < 40 and cy > 15 and cy < 35 and abs(cx) > 5:
                    r, g, b = 26, 26, 26
            idx = (y * w + x) * 4
            pixels[idx:idx+4] = r, g, b, a
    return make_png_raw(w, h, bytes(pixels))

ICON_GENS = {
    "gold_shield_on_red": gen_icon_shield,
    "cherry_blossom_on_purple": gen_icon_cherry,
    "pumpkin_on_black": gen_icon_pumpkin,
}

# ── ADD-ONS (Behavior Packs) ────────────────────────────────────────────

ADDONS = [
    {"id": "op_swords", "name": "OP Swords Add-On",
     "desc": "Adds 5 overpowered swords with custom effects to make you unstoppable!",
     "items": ["fire_sword", "ice_sword", "lightning_sword", "earth_sword", "void_sword"]},
    {"id": "lucky_blocks", "name": "Lucky Blocks Add-On",
     "desc": "Break a lucky block for random amazing loot or terrible disasters!",
     "items": ["lucky_block_gold", "lucky_block_diamond", "lucky_block_emerald"]},
    {"id": "pet_dragons", "name": "Pet Dragons Add-On",
     "desc": "Tame and ride 4 different elemental baby dragons!",
     "entities": ["fire_dragon", "water_dragon", "wind_dragon", "earth_dragon"]},
    {"id": "more_tnt", "name": "More TNT Add-On",
     "desc": "Explode your world with 10 new types of TNT!",
     "items": ["tnt_x5", "tnt_x10", "tnt_x50", "nuke", "blackhole_tnt"]},
    {"id": "mutant_mobs", "name": "Mutant Mobs Add-On",
     "desc": "Fight giant mutant versions of classic mobs!",
     "entities": ["mutant_zombie", "mutant_skeleton", "mutant_creeper", "mutant_enderman"]},
]

def generate_addons():
    print("=== Generating Add-Ons (Behavior Packs) ===")
    os.makedirs(BP_DIR, exist_ok=True)
    for addon in ADDONS:
        addon_dir = os.path.join(BP_DIR, addon["id"])
        os.makedirs(addon_dir, exist_ok=True)
        write_json(os.path.join(addon_dir, "manifest.json"), make_manifest(addon))
        ns = addon["id"]
        if "items" in addon:
            items_dir = os.path.join(addon_dir, "items")
            os.makedirs(items_dir, exist_ok=True)
            for item in addon["items"]:
                write_json(os.path.join(items_dir, f"{item}.json"), {
                    "format_version": "1.20.0",
                    "minecraft:item": {
                        "description": {"identifier": f"{ns}:{item}", "category": "equipment"},
                        "components": {
                            "minecraft:icon": {"texture": item},
                            "minecraft:display_name": {"value": item.replace("_", " ").title()},
                            "minecraft:damage": 10,
                            "minecraft:max_stack_size": 1
                        }
                    }
                })
        if "entities" in addon:
            entities_dir = os.path.join(addon_dir, "entities")
            os.makedirs(entities_dir, exist_ok=True)
            for entity in addon["entities"]:
                write_json(os.path.join(entities_dir, f"{entity}.json"), {
                    "format_version": "1.20.0",
                    "minecraft:entity": {
                        "description": {"identifier": f"{ns}:{entity}", "is_spawnable": True, "is_summonable": True},
                        "components": {
                            "minecraft:health": {"value": 100, "max": 100},
                            "minecraft:movement": {"value": 0.3},
                            "minecraft:attack": {"damage": 15},
                            "minecraft:physics": {}
                        }
                    }
                })
        print(f"  Generated: {addon['name']} ({addon['id']})")

# ── MASHUP PACKS ────────────────────────────────────────────────────────

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

def generate_mashups():
    print("\n=== Generating Mashup Packs ===")
    os.makedirs(MASHUP_DIR, exist_ok=True)
    descriptions = []
    for pack in MASHUP_DEFS:
        pack_dir = os.path.join(MASHUP_DIR, pack["dir"])
        os.makedirs(pack_dir, exist_ok=True)
        write_json(os.path.join(pack_dir, "manifest.json"), make_manifest(pack, module_type="resources"))
        # Generate icon (pure Python PNG)
        png_bytes = ICON_GENS[pack["icon"]]()
        with open(os.path.join(pack_dir, "pack_icon.png"), "wb") as f:
            f.write(png_bytes)
        print(f"  {pack['dir']}/manifest.json + pack_icon.png")
        descriptions.append(f"{pack['manifest_name']} ({pack['price']})")
        descriptions.append(f"  {pack['manifest_desc']}")
        descriptions.append(f"  Header UUID: {pack['header_uuid']}")
        descriptions.append(f"  Module UUID: {pack['module_uuid']}")
        descriptions.append("  Dependencies:")
        for dep in pack["dependencies"]:
            descriptions.append(f"    - {dep['uuid']} v{dep['version'][0]}.{dep['version'][1]}.{dep['version'][2]}")
        descriptions.append("")
        print(f"  Done: {pack['dir']}")
    desc_path = os.path.join(MASHUP_DIR, "mashup-packs-description.txt")
    with open(desc_path, "w") as f:
        f.write("Minecraft Bedrock Mashup Packs\n" + "=" * 50 + "\n\n")
        for line in descriptions:
            f.write(line + "\n")
    print(f"  mashup-packs-description.txt")

# ── PACKAGING ────────────────────────────────────────────────────────────

def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder_path):
            for f in files:
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, folder_path)
                zf.write(abs_path, rel_path)

def package_all():
    print("\n=== Packaging .mcpack files ===")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    count = 0
    # Package behavior packs
    for addon_name in os.listdir(BP_DIR):
        addon_path = os.path.join(BP_DIR, addon_name)
        if os.path.isdir(addon_path):
            zip_path = os.path.join(OUTPUT_DIR, f"{addon_name}.mcpack")
            zip_folder(addon_path, zip_path)
            fsize = os.path.getsize(zip_path)
            print(f"  Packaged {addon_name}.mcpack ({fsize} bytes)")
            count += 1
    # Package skin packs if they exist
    if os.path.isdir(SKIN_PACKS_DIR):
        for pack_name in os.listdir(SKIN_PACKS_DIR):
            pack_path = os.path.join(SKIN_PACKS_DIR, pack_name)
            if os.path.isdir(pack_path):
                zip_path = os.path.join(OUTPUT_DIR, f"{pack_name}.mcpack")
                zip_folder(pack_path, zip_path)
                fsize = os.path.getsize(zip_path)
                print(f"  Packaged {pack_name}.mcpack ({fsize} bytes)")
                count += 1
    print(f"  Total: {count} .mcpack files in {OUTPUT_DIR}")

# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    generate_addons()
    generate_mashups()
    package_all()
    print("\n" + "=" * 60)
    print("ALL DONE")
    print("=" * 60)