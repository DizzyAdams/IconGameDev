"""Generate 100k Minecraft Bedrock skin packs (8 skins/pack, 7 price tiers).
Combines 15 v1 themes + 8 v2 themes = 23 total. Deterministic (seed=42).
Output: marketplace-content/output/mass-skins/ alongside existing 1600 packs."""

import os, json, random, math, argparse, hashlib, time
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = PROJECT_ROOT / "output" / "mass-skins"
SKINS_PER_PACK = 8
SIZE = (64, 64)

# ── 15 v1 themes (colorful palettes) ──────────────────────────────
V1_THEMES = [
    {"suffix": "neon-streets",   "palette": [(0,255,255),(255,0,255),(32,0,64),(192,255,0)],   "patterns": ["stripe_h","diag","cross"]},
    {"suffix": "sunset-safari",  "palette": [(255,120,0),(255,200,50),(90,40,10),(255,160,120)], "patterns": ["stripe_v","check","dots"]},
    {"suffix": "deep-space",     "palette": [(8,4,48),(80,90,240),(180,140,255),(12,20,90)],    "patterns": ["diag","cross","stripe_h"]},
    {"suffix": "toxic-waste",    "palette": [(120,220,40),(20,80,10),(210,255,140),(10,30,5)],  "patterns": ["dots","stripe_v","diag"]},
    {"suffix": "candy-summers",  "palette": [(255,105,180),(120,220,255),(255,255,120),(255,160,220)], "patterns": ["check","cross","stripe_h"]},
    {"suffix": "ocean-depths",   "palette": [(0,80,120),(0,180,220),(160,230,255),(10,30,50)],  "patterns": ["stripe_v","dots","diag"]},
    {"suffix": "ember-ash",      "palette": [(190,40,10),(90,10,10),(255,140,60),(20,20,20)],   "patterns": ["cross","check","stripe_h"]},
    {"suffix": "neon-mint",      "palette": [(0,255,160),(0,120,90),(180,255,230),(10,40,35)],  "patterns": ["stripe_v","diag","dots"]},
    {"suffix": "royal-gold",     "palette": [(60,20,110),(220,180,30),(120,80,180),(30,10,60)], "patterns": ["cross","stripe_h","check"]},
    {"suffix": "clay-bakery",    "palette": [(210,120,80),(245,200,150),(160,75,45),(255,235,210)], "patterns": ["dots","stripe_v","diag"]},
    {"suffix": "retro-arcade",   "palette": [(16,24,48),(0,255,60),(255,0,80),(210,215,220)],   "patterns": ["stripe_h","cross","check"]},
    {"suffix": "sakura-garden",  "palette": [(255,183,197),(180,80,110),(255,240,245),(255,120,150)], "patterns": ["diag","dots","stripe_v"]},
    {"suffix": "slime-caves",    "palette": [(0,160,90),(10,60,40),(110,240,160),(20,20,20)],   "patterns": ["cross","dots","stripe_h"]},
    {"suffix": "midnight-jazz",  "palette": [(18,16,40),(40,30,80),(210,180,130),(12,10,30)],   "patterns": ["check","stripe_v","diag"]},
    {"suffix": "safari-dust",    "palette": [(175,140,95),(90,65,40),(220,200,160),(50,35,20)],  "patterns": ["stripe_h","cross","dots"]},
]

# ── 8 v2 themes (mono-dark bg + neon accents) ─────────────────────
V2_THEMES = [
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
]

ALL_THEMES = V1_THEMES + V2_THEMES

# ── Price Tiers (7 tiers, evenly distributed across 100k) ──────────
PRICE_TIERS = [
    ("$0.99",  760,    0,  14284),
    ("$1.99",  1510, 14285, 28570),
    ("$2.99",  2450, 28571, 42856),
    ("$3.99",  3410, 42857, 57142),
    ("$4.99",  4400, 57143, 71428),
    ("$6.99",  6400, 71429, 85714),
    ("$9.99",  9500, 85715, 99999),
]

# ── Utility Functions ──────────────────────────────────────────────

def make_uuid(name: str) -> str:
    raw = hashlib.sha256(name.encode()).hexdigest()[:32]
    return "-".join([raw[:8], raw[8:12], raw[12:16], raw[16:20], raw[20:32]])

def blend(a, b, t=0.35):
    return int(a[0]*(1-t) + b[0]*t), int(a[1]*(1-t) + b[1]*t), int(a[2]*(1-t) + b[2]*t)

def get_price_tier(index: int):
    """Return (price_label, price_mc) for a pack index (0-99999)."""
    for label, mc, lo, hi in PRICE_TIERS:
        if lo <= index <= hi:
            return label, mc
    return ("$9.99", 9500)

# ── V1 Skin Generation ────────────────────────────────────────────

def v1_skin_pixel_color(rng, x, y, palette, patterns):
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

def v1_noise_color(rng, x, y, base):
    n = rng.randint(-18, 18)
    return max(0, min(255, base[0]+n)), max(0, min(255, base[1]+n)), max(0, min(255, base[2]+n)), 255

def generate_v1_skin(rng, seed, name, palette, patterns, size=SIZE):
    img = Image.new("RGBA", size, (*palette[0], 255))
    pixels = img.load()
    for x in range(size[0]):
        for y in range(size[1]):
            c = v1_skin_pixel_color(rng, x, y, palette, patterns)
            c = v1_noise_color(rng, x, y, c)
            pixels[x, y] = c
    return img

# ── V2 Skin Generation ────────────────────────────────────────────

def v2_skin_pixel_color(rng, x, y, bg, patterns, neons):
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
    if rng.random() < 0.03:
        use_neon = True
        neon_idx = rng.randint(0, len(neons) - 1)
    if use_neon:
        col = neons[neon_idx]
    else:
        n = rng.randint(-8, 8)
        col = tuple(max(0, min(255, c + n)) for c in bg)
    return (*col, 255)

def generate_v2_skin(rng, seed, name, bg, neons, patterns, size=SIZE):
    img = Image.new("RGBA", size, (*bg, 255))
    pixels = img.load()
    for x in range(size[0]):
        for y in range(size[1]):
            pixels[x, y] = v2_skin_pixel_color(rng, x, y, bg, patterns, neons)
    return img

# ── Icon Generation ────────────────────────────────────────────────

def generate_icon(rng, seed, palette, name):
    """Generate 256x256 pack icon at pack root."""
    size = 256
    bg = palette[0]
    img = Image.new("RGBA", (size, size), (*bg, 255))
    pixels = img.load()
    for x in range(size):
        for y in range(size):
            if ((x // 16) + (y // 16)) % 2 == 0:
                d = 6
                pixels[x, y] = tuple(min(255, c + d) for c in bg) + (255,)
    # Determine accent colors
    if len(palette) > 3:
        accents = palette[2:]
    else:
        accents = palette[1:3]
    # Concentric rings
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
    # Occasional sparkle
    for _ in range(20):
        sx = rng.randint(0, size-1)
        sy = rng.randint(0, size-1)
        if accents:
            pixels[sx, sy] = (*accents[rng.randint(0, len(accents)-1)], 255)
    return img

# ── JSON Generators ───────────────────────────────────────────────

def make_skins_json(skin_names, pack_title):
    return {
        "skins": [
            {"localization_name": n, "geometry": "geometry.humanoid.custom", "texture": f"{n}.png", "type": "free"}
            for n in skin_names
        ],
        "serialize_name": pack_title,
        "localization_name": pack_title,
    }

def make_manifest(pack_title, pack_dir_name, header_uuid, module_uuid, price_label, price_mc):
    return {
        "format_version": 2,
        "header": {
            "name": pack_title,
            "description": f"Generated pack: {pack_title} | Tier: {price_label} ({price_mc} MC)",
            "uuid": header_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {"type": "skin_pack", "uuid": module_uuid, "version": [1, 0, 0]},
        ],
    }

# ── Pack Generator ────────────────────────────────────────────────

def generate_pack(output_root: Path, index: int):
    """Generate one skin pack at a given absolute index (0-99999)."""
    # Theme selection: alternate between v1 and v2 style based on theme cycle
    theme_idx = index % len(ALL_THEMES)
    theme = ALL_THEMES[theme_idx]
    is_v1 = theme_idx < len(V1_THEMES)

    theme_suffix = theme["suffix"]
    pack_title = f"Mass {theme_suffix.title().replace('-','')} #{index+1}"
    pack_dir_name = f"mass_{theme_suffix}_{index+1:05d}"
    pack_dir = output_root / pack_dir_name
    textures = pack_dir / "textures" / "skins"
    textures.mkdir(parents=True, exist_ok=True)

    rng = random.Random(index * 997 + 31)
    seed = rng.randint(0, 2**31)

    price_label, price_mc = get_price_tier(index)

    names = []
    if is_v1:
        # ── V1 generation ──
        palette = rng.choice(theme["palette"])
        secondary = theme["palette"][1]
        accent = theme["palette"][2 if len(theme["palette"]) > 2 else 1]
        pack_palette = [palette, secondary, accent, rng.choice(theme["palette"])]
        patterns = rng.sample(theme["patterns"], k=min(3, len(theme["patterns"])))

        for s in range(SKINS_PER_PACK):
            name = f"MassSkin_{index+1:05d}_{s+1:02d}"
            names.append(name)
            sk_rng = random.Random(seed + s * 1009 + 17)
            img = generate_v1_skin(sk_rng, seed + s * 1009, name, pack_palette, patterns)
            img.save(textures / f"{name}.png")

        icon = generate_icon(rng, seed, pack_palette, pack_title)
        # pack_icon.png at pack ROOT per bedrock spec
        icon.save(pack_dir / "pack_icon.png")
    else:
        # ── V2 generation ──
        pal_var = rng.choice(theme["palettes"])
        bg = pal_var[0]
        bg = tuple(max(0, min(255, c + rng.randint(-3, 3))) for c in bg)
        neons = pal_var[2:]
        patterns = rng.sample(theme["patterns"], k=min(3, len(theme["patterns"])))

        for s in range(SKINS_PER_PACK):
            name = f"MassSkin_{index+1:05d}_{s+1:02d}"
            names.append(name)
            sk_rng = random.Random(seed + s * 1009 + 17)
            img = generate_v2_skin(sk_rng, seed + s * 1009, name, bg, neons, patterns)
            img.save(textures / f"{name}.png")

        icon = generate_icon(rng, seed, pal_var, pack_title)
        icon.save(pack_dir / "pack_icon.png")

    # UUIDs (SHA256-based, deterministic)
    header_uuid = make_uuid(f"mass100k_{theme_suffix}_{index}_header")
    module_uuid = make_uuid(f"mass100k_{theme_suffix}_{index}_module")

    # Write manifest and skins.json
    manifest = make_manifest(pack_title, pack_dir_name, header_uuid, module_uuid, price_label, price_mc)
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (pack_dir / "skins.json").write_text(
        json.dumps(make_skins_json(names, pack_title), indent=2), encoding="utf-8"
    )

    return pack_dir, header_uuid, module_uuid, names

def find_highest_index(output_root: Path) -> int:
    """Scan existing output dir for the highest pack index. Returns -1 if empty."""
    highest = -1
    for d in output_root.glob("mass_*_[0-9][0-9][0-9][0-9][0-9]"):
        try:
            idx = int(d.name.split("_")[-1])
            if idx > highest:
                highest = idx
        except (ValueError, IndexError):
            continue
    return highest

def dry_run_report(output_root: Path, target_total: int):
    """Show stats without generating anything."""
    existing = sum(1 for _ in output_root.glob("mass_*_[0-9][0-9][0-9][0-9][0-9]"))
    need = max(0, target_total - existing)
    print(f"{'='*60}")
    print(f"DRY RUN — 100k Skin Pack Generator")
    print(f"{'='*60}")
    print(f"Output directory: {output_root}")
    print(f"Existing packs:   {existing}")
    print(f"Target total:     {target_total}")
    print(f"Packs to create:  {need}")
    print(f"")
    print(f"Price Tier Distribution (100k packs):")
    for label, mc, lo, hi in PRICE_TIERS:
        count = hi - lo + 1
        pct = count / 100000 * 100
        print(f"  {label:>8s} ({mc} MC)  indices {lo:>5d}-{hi:<5d}  {count:>6d} packs ({pct:.1f}%)")
    print(f"")
    print(f"Themes: {len(V1_THEMES)} v1 + {len(V2_THEMES)} v2 = {len(ALL_THEMES)} total")
    print(f"Skins per pack: {SKINS_PER_PACK}")
    print(f"Skins total:    {target_total * SKINS_PER_PACK}")
    print(f"Seed: 42 (deterministic)")
    print(f"Disk estimate: ~{target_total * 8 * 4 // 1024 // 1024:.1f} GB (PNGs)")
    print(f"{'='*60}")
    return need

def main():
    ap = argparse.ArgumentParser(
        description="Generate 100k Minecraft Bedrock skin packs deterministically."
    )
    ap.add_argument("--count", type=int, default=100000,
                    help="Target total pack count (default: 100000)")
    ap.add_argument("--out", type=str, default=str(DEFAULT_OUT))
    ap.add_argument("--dry-run", action="store_true",
                    help="Show stats and exit without generating")
    ap.add_argument("--resume", action="store_true",
                    help="Resume from highest existing pack index")
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        dry_run_report(out_root, args.count)
        return

    # Determine starting index
    if args.resume:
        highest = find_highest_index(out_root)
        start_idx = highest + 1
        existing = highest + 1
        if highest < 0:
            existing = 0
            start_idx = 0
    else:
        existing = sum(1 for _ in out_root.glob("mass_*_[0-9][0-9][0-9][0-9][0-9]"))
        start_idx = existing

    total_needed = max(0, args.count - existing)

    if total_needed == 0:
        print(f"Already have {existing} packs — nothing to generate. Target: {args.count}")
        return

    print(f"{'='*60}")
    print(f"100k Skin Pack Generator")
    print(f"{'='*60}")
    print(f"Output:    {out_root}")
    print(f"Existing:  {existing} packs")
    print(f"Generating {total_needed} packs (indices {start_idx}-{args.count-1})")
    print(f"{'='*60}")

    start_time = time.time()
    packs_created = 0
    bad_sizes = []

    for i in range(start_idx, args.count):
        pack_dir, *_ = generate_pack(out_root, i)
        packs_created += 1

        if packs_created % 100 == 0:
            elapsed = time.time() - start_time
            rate = packs_created / elapsed if elapsed > 0 else 0
            remaining = total_needed - packs_created
            eta = remaining / rate if rate > 0 else 0
            print(f"  [{packs_created}/{total_needed}] index {i} — "
                  f"{rate:.1f} packs/s — ETA {eta/60:.1f} min")

    # ── Final Verification ──
    elapsed = time.time() - start_time
    total_packs = sum(1 for _ in out_root.glob("mass_*_[0-9][0-9][0-9][0-9][0-9]"))
    skin_files = sum(1 for fp in out_root.rglob("*.png") if fp.name != "pack_icon.png" and fp.name != "icon.png")
    icon_files = sum(1 for fp in out_root.rglob("pack_icon.png"))

    # Validate skin sizes
    invalid_skins = []
    for fp in sorted(out_root.rglob("*.png")):
        if fp.name == "pack_icon.png" or fp.name == "icon.png":
            continue
        try:
            with Image.open(fp) as img:
                if img.size != SIZE:
                    invalid_skins.append((str(fp.relative_to(out_root)), img.size))
        except Exception as e:
            invalid_skins.append((str(fp.relative_to(out_root)), str(e)))

    # Check manifest integrity (first 5 and random sample)
    manifest_issues = []
    all_manifests = sorted(out_root.glob("**/manifest.json"))
    sample_indices = list(range(min(5, len(all_manifests))))
    if len(all_manifests) > 5:
        sample_indices += [len(all_manifests) // 2 - 1, len(all_manifests) - 1]
    for idx in sample_indices:
        fp = all_manifests[idx]
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            if "header" not in data or "modules" not in data:
                manifest_issues.append(f"{fp.name}: missing header/modules")
        except Exception as e:
            manifest_issues.append(f"{fp.name}: {e}")

    report = {
        "target_total": args.count,
        "packs_created_this_run": packs_created,
        "total_packs_in_output": total_packs,
        "skins_generated": skin_files,
        "pack_icons": icon_files,
        "invalid_skins": invalid_skins[:10],
        "invalid_skin_count": len(invalid_skins),
        "manifest_issues": manifest_issues,
        "runtime_seconds": round(elapsed, 1),
        "avg_packs_per_second": round(packs_created / elapsed, 2) if elapsed > 0 else 0,
        "output_dir": str(out_root),
    }

    print(f"\n{'='*60}")
    print(f"GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Packs created this run: {packs_created}")
    print(f"  Total packs in output:  {total_packs}")
    print(f"  Total skins:            {skin_files}")
    print(f"  Pack icons:             {icon_files}")
    print(f"  Runtime:                {elapsed:.1f}s ({elapsed/60:.1f} min)")
    if invalid_skins:
        print(f"  WARNING: {len(invalid_skins)} invalid-sized skins!")
    if manifest_issues:
        print(f"  WARNING: {len(manifest_issues)} manifest issues!")
    print(f"  Output:                 {out_root}")
    print(f"{'='*60}")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    raise SystemExit(main())
