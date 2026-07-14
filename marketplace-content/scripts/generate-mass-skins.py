"""Generate +1500 Bedrock skins bundled into compliant zip deliverable packs."""
import os, json, random, math, argparse, zipfile, hashlib
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = PROJECT_ROOT / "output" / "mass-skins"
DEFAULT_SKINS_PER_PACK = 8
VALID_SKIN_SIZES = {(64, 32), (64, 64), (128, 128)}

THEME_PRESETS = [
    {"suffix": "neon-streets", "palette": [(0,255,255),(255,0,255),(32,0,64),(192,255,0)], "patterns": ["stripe_h","diag","cross"]},
    {"suffix": "sunset-safari", "palette": [(255,120,0),(255,200,50),(90,40,10),(255,160,120)], "patterns": ["stripe_v","check","dots"]},
    {"suffix": "deep-space", "palette": [(8,4,48),(80,90,240),(180,140,255),(12,20,90)], "patterns": ["diag","cross","stripe_h"]},
    {"suffix": "toxic-waste", "palette": [(120,220,40),(20,80,10),(210,255,140),(10,30,5)], "patterns": ["dots","stripe_v","diag"]},
    {"suffix": "candy-summers", "palette": [(255,105,180),(120,220,255),(255,255,120),(255,160,220)], "patterns": ["check","cross","stripe_h"]},
    {"suffix": "ocean-depths", "palette": [(0,80,120),(0,180,220),(160,230,255),(10,30,50)], "patterns": ["stripe_v","dots","diag"]},
    {"suffix": "ember-ash", "palette": [(190,40,10),(90,10,10),(255,140,60),(20,20,20)], "patterns": ["cross","check","stripe_h"]},
    {"suffix": "neon-mint", "palette": [(0,255,160),(0,120,90),(180,255,230),(10,40,35)], "patterns": ["stripe_v","diag","dots"]},
    {"suffix": "royal-gold", "palette": [(60,20,110),(220,180,30),(120,80,180),(30,10,60)], "patterns": ["cross","stripe_h","check"]},
    {"suffix": "clay-bakery", "palette": [(210,120,80),(245,200,150),(160,75,45),(255,235,210)], "patterns": ["dots","stripe_v","diag"]},
    {"suffix": "retro-arcade", "palette": [(16,24,48),(0,255,60),(255,0,80),(210,215,220)], "patterns": ["stripe_h","cross","check"]},
    {"suffix": "sakura-garden", "palette": [(255,183,197),(180,80,110),(255,240,245),(255,120,150)], "patterns": ["diag","dots","stripe_v"]},
    {"suffix": "slime-caves", "palette": [(0,160,90),(10,60,40),(110,240,160),(20,20,20)], "patterns": ["cross","dots","stripe_h"]},
    {"suffix": "midnight-jazz", "palette": [(18,16,40),(40,30,80),(210,180,130),(12,10,30)], "patterns": ["check","stripe_v","diag"]},
    {"suffix": "safari-dust", "palette": [(175,140,95),(90,65,40),(220,200,160),(50,35,20)], "patterns": ["stripe_h","cross","dots"]},
]


def deterministic(_): return 0.20
def make_uuid(name: str) -> str:
    raw = hashlib.sha256(name.encode()).hexdigest()[:32]
    return "-".join([raw[:8], raw[8:12], raw[12:16], raw[16:20], raw[20:32]])


def blend(a, b, t=0.35):
    return int(a[0]*(1-t) + b[0]*t), int(a[1]*(1-t) + b[1]*t), int(a[2]*(1-t) + b[2]*t)


def skin_pixel_color(seed, x, y, palette, patterns):
    rng = random.Random(seed + x * 131 + y * 19)
    primary, secondary = palette[0], palette[1]
    accent = palette[min(2, len(palette)-1)]
    p = rng.choice(patterns)
    use_sec = False
    use_acc = False
    if p == "stripe_h" and (y // 4) % 2 == 0:
        use_sec = True
    elif p == "stripe_v" and (x // 4) % 2 == 0:
        use_sec = True
    elif p == "check" and ((x // 4) + (y // 4)) % 2 == 0:
        use_sec = True
    elif p == "diag" and ((x + y) // 6) % 2 == 0:
        use_sec = True
    elif p == "dots" and (x % 8 == 0) and (y % 8 == 0):
        use_acc = True
    elif p == "cross" and ((x // 4) % 2 == 0 or (y // 4) % 2 == 0):
        use_sec = True

    if rng.random() < 0.03:
        base = accent
    else:
        base = secondary if (use_sec or use_acc) else primary
    return (*base, 255)


def noise_color(seed, x, y, base):
    rng = random.Random(seed + x * 53 + y * 97)
    n = rng.randint(-18, 18)
    return max(0, min(255, base[0]+n)), max(0, min(255, base[1]+n)), max(0, min(255, base[2]+n)), 255


def generate_skin(seed, name, palette, patterns, size=(64, 64), noise=True):
    img = Image.new("RGBA", size, (*palette[0], 255))
    pixels = img.load()
    for x in range(size[0]):
        for y in range(size[1]):
            c = skin_pixel_color(seed, x, y, palette, patterns)
            if noise:
                c = noise_color(seed, x, y, c)
            pixels[x, y] = c
    return img


def generate_icon(seed, palette, name):
    rng = random.Random(seed + hash(name))
    size = 256
    img = Image.new("RGBA", (size, size), (*palette[-1 if len(palette) > 1 else 0], 255))
    pixels = img.load()
    for x in range(size):
        for y in range(size):
            if ((x // 16) + (y // 16)) % 2 == 0:
                pixels[x, y] = (*blend(palette[0], palette[1], rng.uniform(0.05, 0.25)), 255)
    cx, cy = size // 2, size // 2
    rings = rng.randint(2, 4)
    for ring in range(rings, 0, -1):
        radius = ring * 36
        col = palette[ring % len(palette)]
        for angle in range(0, 360, 3):
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


def generate_pack(output_root: Path, index: int, theme, skins_per_pack, size):
    theme_suffix = theme["suffix"]
    pack_title = f"Mass {theme_suffix.title().replace('-','')} #{index+1}"
    pack_dir_name = f"mass_{theme_suffix}_{index+1:05d}"
    pack_dir = output_root / pack_dir_name
    textures = pack_dir / "textures" / "skins"
    textures.mkdir(parents=True, exist_ok=True)

    rng = random.Random(index * 997 + 31)
    seed = rng.randint(0, 2**31)
    palette = rng.choice(theme["palette"])
    secondary = theme["palette"][1]
    accent = theme["palette"][2 if len(theme["palette"]) > 2 else 1]
    pack_palette = [palette, secondary, accent, rng.choice(theme["palette"])]
    patterns = rng.sample(theme["patterns"], k=min(3, len(theme["patterns"])))

    names = []
    for s in range(skins_per_pack):
        name = f"MassSkin_{index+1:05d}_{s+1:02d}"
        names.append(name)
        img = generate_skin(seed + s * 1009, name, pack_palette, patterns, size=size)
        img.save(textures / f"{name}.png")

    icon = generate_icon(seed, pack_palette, pack_title)
    icon.save(textures / "icon.png")

    header_uuid = make_uuid(f"mass_{theme_suffix}_{index}_header")
    module_uuid = make_uuid(f"mass_{theme_suffix}_{index}_module")

    manifest = make_manifest(pack_title, pack_dir_name, header_uuid, module_uuid)
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (pack_dir / "skins.json").write_text(
        json.dumps(make_skins_json(names, pack_title), indent=2), encoding="utf-8"
    )
    return pack_dir, header_uuid, module_uuid, names


def build_final_zip(output_root: Path, zips_dir: Path, total_packs: int, pack_meta: list):
    zips_dir.mkdir(parents=True, exist_ok=True)
    zip_name = f"mass_skins_{total_packs}_packs_{output_root.name}.zip"
    zip_path = zips_dir / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for pack_dir, *_ in pack_meta:
            for fp in sorted(pack_dir.rglob("*")):
                if fp.is_dir():
                    continue
                zf.write(fp, str(fp.relative_to(output_root)))
    return zip_path


def summarize(output_root: Path, total_packs: int, skins_per_pack: int, size):
    packs = sorted(output_root.glob("mass_*"))
    skin_files = sum(1 for fp in output_root.rglob("*.png") if fp.name != "icon.png")
    bad = []
    for fp in output_root.rglob("*.png"):
        if fp.name == "icon.png":
            continue
        with Image.open(fp) as img:
            if img.size not in VALID_SKIN_SIZES:
                bad.append((str(fp.relative_to(output_root)), img.size))
    return {
        "packs": len(packs),
        "skins": skin_files,
        "invalid_skins": bad[:20],
        "invalid_skin_count": len(bad),
        "target_packs": total_packs,
        "size": size,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1600)
    ap.add_argument("--skins-per-pack", type=int, default=8)
    ap.add_argument("--size", choices=["64x64", "64x32", "128x128", "mix"], default="64x64")
    ap.add_argument("--out", type=str, default=str(DEFAULT_OUT))
    args = ap.parse_args()
    size_map = {"64x64": (64,64), "64x32": (64,32), "128x128": (128,128), "mix": None}
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    metadata = []
    for i in range(args.count):
        theme = THEME_PRESETS[i % len(THEME_PRESETS)]
        size = size_map[args.size]
        if size is None:
            size = (64,64) if (i % 3) else (128,128) if (i % 5) else (64,32)
        metadata.append(generate_pack(out_root, i, theme, args.skins_per_pack, size))
    zips_dir = PROJECT_ROOT / "output" / "zips"
    zip_path = build_final_zip(out_root, zips_dir, args.count, metadata)
    report = summarize(out_root, args.count, args.skins_per_pack, None)
    if size_map[args.size] is None:
        report["size_mode"] = "mix"
    report["zip"] = str(zip_path)
    report["output_dir"] = str(out_root)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
