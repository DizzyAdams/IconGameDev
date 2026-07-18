"""Generate 800 new mass-skin packs (8 themes x 100 packs) - mono-dark + neon accents."""
import os, json, random, math, argparse, hashlib
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = PROJECT_ROOT / "output" / "mass-skins"
SKINS_PER_PACK = 8
SIZE = (64, 64)

# 16 high-appeal themes — mono-dark background + neon accents (8 original + 8 new)
NEW_THEMES = [
    {
        "suffix": "halloween-spooky",
        "palettes": [
            [(10,5,15),(20,5,40),(255,107,0),(57,255,20),(255,140,0)],
            [(8,8,12),(30,8,45),(255,80,0),(50,255,30),(255,200,0)],
            [(12,4,18),(25,10,50),(255,120,0),(40,255,10),(255,160,50)],
        ],
        "patterns": ["stripe_h","diag","cross","dots","check"],
        "bg_range": ((5,15),(3,10),(10,25)),
    },
    {
        "suffix": "christmas-frost",
        "palettes": [
            [(8,10,20),(10,20,50),(255,0,64),(0,255,64),(170,220,255)],
            [(10,8,25),(15,15,55),(240,0,50),(0,240,60),(190,230,255)],
            [(6,10,18),(12,18,48),(255,20,70),(20,255,50),(150,210,255)],
        ],
        "patterns": ["stripe_v","cross","check","diag","dots"],
        "bg_range": ((5,12),(8,15),(16,30)),
    },
    {
        "suffix": "crypto-bitcoin",
        "palettes": [
            [(8,8,8),(15,15,10),(255,215,0),(255,107,0),(0,255,255)],
            [(10,10,6),(20,18,8),(255,220,20),(255,120,0),(0,240,240)],
            [(6,6,10),(12,12,8),(255,230,30),(240,100,0),(20,255,255)],
        ],
        "patterns": ["check","cross","stripe_h","diag","dots"],
        "bg_range": ((5,12),(5,12),(5,12)),
    },
    {
        "suffix": "anime-kawaii",
        "palettes": [
            [(20,8,20),(35,10,40),(255,20,147),(191,0,255),(0,255,127)],
            [(18,6,22),(30,12,45),(255,40,160),(200,0,240),(0,240,120)],
            [(22,10,18),(38,8,42),(255,30,140),(180,10,255),(10,255,140)],
        ],
        "patterns": ["dots","stripe_v","diag","check","cross"],
        "bg_range": ((15,25),(6,14),(16,25)),
    },
    {
        "suffix": "zombie-apocalypse",
        "palettes": [
            [(8,15,8),(15,18,6),(57,255,20),(204,255,0),(100,180,50)],
            [(6,12,8),(12,16,5),(50,240,15),(190,250,0),(90,170,40)],
            [(10,18,10),(18,20,8),(60,255,25),(210,255,10),(110,190,60)],
        ],
        "patterns": ["diag","cross","stripe_h","dots","check"],
        "bg_range": ((5,12),(12,20),(5,10)),
    },
    {
        "suffix": "galaxy-cosmic",
        "palettes": [
            [(8,8,35),(15,10,50),(0,68,255),(255,0,255),(255,0,128)],
            [(6,8,40),(12,12,55),(20,80,240),(240,0,240),(255,20,140)],
            [(10,6,30),(18,8,48),(0,60,255),(255,10,255),(240,0,100)],
        ],
        "patterns": ["check","dots","diag","cross","stripe_h"],
        "bg_range": ((5,12),(5,12),(30,55)),
    },
    {
        "suffix": "ninja-samurai",
        "palettes": [
            [(8,8,8),(15,15,15),(255,0,34),(255,215,0),(0,212,255)],
            [(10,10,10),(18,18,18),(240,0,30),(230,200,0),(0,200,240)],
            [(6,6,10),(12,12,16),(255,20,50),(255,220,20),(20,220,255)],
        ],
        "patterns": ["stripe_v","cross","diag","check","stripe_h"],
        "bg_range": ((5,12),(5,12),(8,18)),
    },
    {
        "suffix": "pirate-ocean",
        "palettes": [
            [(6,14,14),(10,20,24),(255,215,0),(0,255,136),(255,107,107)],
            [(8,12,16),(12,18,22),(230,200,0),(0,240,130),(240,100,100)],
            [(5,16,12),(10,22,20),(255,220,20),(20,255,140),(255,120,120)],
        ],
        "patterns": ["stripe_h","diag","check","dots","cross"],
        "bg_range": ((4,10),(12,22),(12,25)),
    },
    # === NEW THEMES (Batch 2) ===
    {
        "suffix": "sci-fi-cyborg",
        "palettes": [
            [(5,8,18),(10,12,30),(0,255,255),(255,107,53),(0,180,255)],
            [(8,6,20),(12,10,32),(0,240,240),(255,120,60),(0,160,240)],
            [(4,10,16),(8,14,28),(0,255,230),(255,100,40),(20,200,255)],
        ],
        "patterns": ["cross","diag","stripe_v","check","dots"],
        "bg_range": ((3,10),(6,14),(15,35)),
    },
    {
        "suffix": "nature-spirit",
        "palettes": [
            [(5,15,8),(10,25,12),(57,255,20),(204,255,0),(0,255,136)],
            [(8,12,6),(14,22,10),(50,240,15),(190,250,0),(0,240,130)],
            [(4,18,10),(8,28,14),(60,255,25),(210,255,10),(20,255,140)],
        ],
        "patterns": ["stripe_h","diag","dots","check","cross"],
        "bg_range": ((3,10),(12,25),(5,12)),
    },
    {
        "suffix": "underwater-kingdom",
        "palettes": [
            [(4,12,16),(8,18,26),(0,255,200),(255,0,128),(0,200,255)],
            [(6,10,18),(10,16,28),(0,240,180),(240,0,140),(0,180,240)],
            [(3,14,14),(6,20,24),(0,255,220),(255,20,150),(20,210,255)],
        ],
        "patterns": ["diag","cross","check","stripe_h","dots"],
        "bg_range": ((2,8),(10,22),(14,30)),
    },
    {
        "suffix": "steam-punk",
        "palettes": [
            [(14,10,6),(20,16,10),(255,215,0),(255,183,77),(255,140,0)],
            [(12,8,8),(18,14,12),(240,200,0),(230,170,70),(240,130,0)],
            [(16,12,4),(22,18,8),(255,220,20),(255,190,80),(255,150,20)],
        ],
        "patterns": ["check","cross","stripe_v","diag","stripe_h"],
        "bg_range": ((10,18),(8,16),(4,12)),
    },
    {
        "suffix": "ice-dragon",
        "palettes": [
            [(6,10,20),(10,16,35),(100,200,255),(0,150,255),(200,230,255)],
            [(8,8,22),(12,14,38),(120,210,255),(0,130,240),(180,220,255)],
            [(5,12,18),(8,18,32),(80,190,255),(0,160,255),(220,240,255)],
        ],
        "patterns": ["cross","stripe_v","diag","dots","check"],
        "bg_range": ((4,12),(8,20),(18,40)),
    },
    {
        "suffix": "neon-racer",
        "palettes": [
            [(5,5,5),(10,10,10),(255,0,64),(0,255,64),(0,128,255)],
            [(8,3,8),(12,8,12),(240,0,50),(0,240,50),(0,115,240)],
            [(3,5,7),(8,8,12),(255,20,80),(20,255,80),(20,140,255)],
        ],
        "patterns": ["stripe_h","stripe_v","diag","cross","dots"],
        "bg_range": ((2,10),(2,10),(2,12)),
    },
    {
        "suffix": "tribal-fire",
        "palettes": [
            [(16,6,6),(28,10,8),(255,107,53),(255,215,0),(255,60,0)],
            [(14,8,4),(26,12,6),(255,120,60),(230,200,0),(240,50,0)],
            [(18,4,8),(30,8,10),(255,100,40),(255,220,20),(255,70,10)],
        ],
        "patterns": ["diag","check","cross","dots","stripe_h"],
        "bg_range": ((14,22),(4,12),(4,12)),
    },
    {
        "suffix": "astral-wizard",
        "palettes": [
            [(10,5,22),(18,8,38),(255,0,255),(0,255,255),(180,0,255)],
            [(8,8,20),(16,10,36),(240,0,240),(0,240,240),(160,0,240)],
            [(12,4,24),(20,6,40),(255,20,255),(20,255,255),(200,10,255)],
        ],
        "patterns": ["cross","dots","diag","check","stripe_v"],
        "bg_range": ((8,14),(4,10),(18,40)),
    },
]


def make_uuid(name: str) -> str:
    raw = hashlib.sha256(name.encode()).hexdigest()[:32]
    return "-".join([raw[:8], raw[8:12], raw[12:16], raw[16:20], raw[20:32]])


def blend(a, b, t=0.35):
    return int(a[0]*(1-t) + b[0]*t), int(a[1]*(1-t) + b[1]*t), int(a[2]*(1-t) + b[2]*t)


def skin_pixel_color(rng, x, y, bg, patterns, neons):
    """Mono-dark background with neon accent patterns."""
    p = rng.choice(patterns)
    use_neon = False
    neon_idx = 0

    if p == "stripe_h" and (y // 4) % 2 == 0:
        use_neon = True
        neon_idx = (y // 8) % len(neons)
    elif p == "stripe_v" and (x // 4) % 2 == 0:
        use_neon = True
        neon_idx = (x // 8) % len(neons)
    elif p == "check" and ((x // 4) + (y // 4)) % 2 == 0:
        use_neon = True
        neon_idx = ((x + y) // 12) % len(neons)
    elif p == "diag" and ((x + y) // 6) % 2 == 0:
        use_neon = True
        neon_idx = ((x + y) // 14) % len(neons)
    elif p == "dots" and (x % 8 == 0 and y % 8 == 0):
        use_neon = True
        neon_idx = (x + y) % len(neons)

    # Random sparkle / accent pixel (3% chance)
    if rng.random() < 0.03:
        use_neon = True
        neon_idx = rng.randint(0, len(neons) - 1)

    if use_neon:
        col = neons[neon_idx]
    else:
        # Subtle variation on dark bg
        n = rng.randint(-8, 8)
        col = tuple(max(0, min(255, c + n)) for c in bg)

    return (*col, 255)


def generate_skin(seed, name, bg, neons, patterns, size=SIZE):
    img = Image.new("RGBA", size, (*bg, 255))
    pixels = img.load()
    for x in range(size[0]):
        for y in range(size[1]):
            rng = random.Random(seed + x * 131 + y * 19 + hash(name) % 9999)
            pixels[x, y] = skin_pixel_color(rng, x, y, bg, patterns, neons)
    return img


def generate_icon(seed, palette, patterns, name):
    rng = random.Random(seed + hash(name) % 9999)
    size = 256
    bg = palette[0]
    neons = palette[2:]
    img = Image.new("RGBA", (size, size), (*bg, 255))
    pixels = img.load()

    # Subtle checkerboard background pattern
    for x in range(size):
        for y in range(size):
            if ((x // 16) + (y // 16)) % 2 == 0:
                d = 6
                pixels[x, y] = tuple(min(255, c + d) for c in bg) + (255,)
            if rng.random() < 0.01:
                pixels[x, y] = (*neons[rng.randint(0, len(neons)-1)], 255)

    # Neon circular rings
    cx, cy = size // 2, size // 2
    rings = rng.randint(2, 4)
    for ring in range(rings):
        radius = (ring + 1) * 32
        col = neons[ring % len(neons)]
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            px = cx + int(radius * math.cos(rad))
            py = cy + int(radius * math.sin(rad))
            if 0 <= px < size and 0 <= py < size:
                pixels[px, py] = (*col, 255)
    return img


def make_skins_json(skin_names, pack_title):
    return {
        "skins": [
            {"localization_name": n, "geometry": "geometry.humanoid.custom", "texture": f"{n}.png", "type": "free"}
            for n in skin_names
        ],
        "serialize_name": pack_title,
        "localization_name": pack_title,
    }


def make_manifest(pack_title, pack_dir_name, header_uuid, module_uuid):
    return {
        "format_version": 2,
        "header": {
            "name": pack_title,
            "description": f"Generated pack: {pack_title}",
            "uuid": header_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {"type": "skin_pack", "uuid": module_uuid, "version": [1, 0, 0]},
        ],
    }


def generate_pack(output_root: Path, index: int, theme):
    theme_suffix = theme["suffix"]
    pack_title = f"Mass {theme_suffix.title().replace('-','')} #{index+1}"
    pack_dir_name = f"mass_{theme_suffix}_{index+1:05d}"
    pack_dir = output_root / pack_dir_name
    textures = pack_dir / "textures" / "skins"
    textures.mkdir(parents=True, exist_ok=True)

    rng = random.Random(index * 997 + 31)
    seed = rng.randint(0, 2**31)

    # Pick a palette variant
    pal_var = rng.choice(theme["palettes"])
    bg = pal_var[0]  # mono-dark background
    # Subtle variation on background
    bg = tuple(max(0, min(255, c + rng.randint(-3, 3))) for c in bg)
    neons = pal_var[2:]  # neon accent colors
    patterns = rng.sample(theme["patterns"], k=min(3, len(theme["patterns"])))

    names = []
    for s in range(SKINS_PER_PACK):
        name = f"MassSkin_{index+1:05d}_{s+1:02d}"
        names.append(name)
        img = generate_skin(seed + s * 1009, name, bg, neons, patterns)
        img.save(textures / f"{name}.png")

    icon = generate_icon(seed, pal_var, patterns, pack_title)
    icon.save(textures / "icon.png")

    header_uuid = make_uuid(f"mass_{theme_suffix}_{index}_header")
    module_uuid = make_uuid(f"mass_{theme_suffix}_{index}_module")

    manifest = make_manifest(pack_title, pack_dir_name, header_uuid, module_uuid)
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (pack_dir / "skins.json").write_text(
        json.dumps(make_skins_json(names, pack_title), indent=2), encoding="utf-8"
    )
    return pack_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default=str(DEFAULT_OUT))
    ap.add_argument("--start-index", type=int, default=1600,
                    help="Starting pack index (existing packs go 0-1599)")
    ap.add_argument("--theme-count", type=int, default=100,
                    help="Packs per theme")
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    total = 0
    for ti, theme in enumerate(NEW_THEMES):
        print(f"Generating {theme['suffix']}...")
        for p in range(args.theme_count):
            idx = args.start_index + ti * args.theme_count + p
            generate_pack(out_root, idx, theme)
            total += 1
            if (p + 1) % 25 == 0:
                print(f"  {p+1}/{args.theme_count} packs done")

    # Summary
    pack_dirs = sorted(out_root.glob("mass_*"))
    skin_files = sum(1 for fp in out_root.rglob("*.png") if fp.name != "icon.png")
    invalid = []
    for fp in out_root.rglob("*.png"):
        if fp.name == "icon.png":
            continue
        with Image.open(fp) as img:
            if img.size != SIZE:
                invalid.append((str(fp.relative_to(out_root)), img.size))

    report = {
        "packs_created": total,
        "new_themes": len(NEW_THEMES),
        "skins_generated": skin_files,
        "invalid_skins": invalid[:20],
        "invalid_skin_count": len(invalid),
        "output_dir": str(out_root),
    }
    print(f"\n{'='*50}")
    print(f"DONE! Created {total} packs, {skin_files} skins")
    if invalid:
        print(f"WARNING: {len(invalid)} invalid-sized skins found!")
    print(json.dumps(report, indent=2))

    # Create combined zip
    import zipfile
    zips_dir = PROJECT_ROOT / "output" / "zips"
    zips_dir.mkdir(parents=True, exist_ok=True)
    zip_name = f"mass_skins_v2_{total}_packs_new-themes.zip"
    zip_path = zips_dir / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for pd in pack_dirs:
            for fp in sorted(pd.rglob("*")):
                if fp.is_dir():
                    continue
                zf.write(fp, str(fp.relative_to(out_root)))
    print(f"\nZIP created: {zip_path}")


if __name__ == "__main__":
    raise SystemExit(main())
