from PIL import Image
import os, math, random, json, hashlib

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'texture-packs'))
TEX_DIR = 'textures/blocks'
SIZE = 32
ICON_SIZE = 256

# 40 block color palettes (base RGB)
BLOCK_COLORS = {
    'stone': (140, 140, 135), 'granite': (160, 130, 120), 'diorite': (180, 175, 170), 'andesite': (135, 130, 125),
    'grass_top': (90, 175, 65), 'grass_side': (110, 150, 75), 'dirt': (130, 95, 60), 'podzol': (100, 75, 45),
    'sand': (215, 200, 150), 'red_sand': (190, 120, 70), 'gravel': (145, 135, 125),
    'cobblestone': (120, 115, 110), 'mossy_cobblestone': (110, 125, 100), 'brick': (165, 85, 65), 'stone_brick': (135, 130, 125),
    'wood_oak': (155, 125, 75), 'wood_spruce': (85, 65, 45), 'wood_birch': (195, 180, 145), 'wood_jungle': (140, 100, 60),
    'wood_acacia': (160, 100, 55), 'wood_dark_oak': (60, 45, 30),
    'planks_oak': (185, 155, 95), 'planks_spruce': (110, 85, 55), 'planks_birch': (205, 190, 155), 'planks_jungle': (165, 120, 70),
    'planks_acacia': (175, 110, 60), 'planks_dark_oak': (70, 55, 40),
    'water_still': (50, 80, 180), 'water_flow': (45, 75, 170), 'lava_still': (225, 110, 25), 'lava_flow': (210, 95, 20),
    'gold_block': (255, 215, 0), 'iron_block': (200, 200, 210), 'diamond_block': (80, 200, 210), 'emerald_block': (50, 205, 85),
    'redstone_block': (185, 20, 20), 'coal_block': (35, 35, 35), 'obsidian': (20, 15, 35), 'netherrack': (130, 30, 30), 'end_stone': (210, 200, 160),
}

BLOCK_NAMES = list(BLOCK_COLORS.keys())


# ── Color modifiers ──────────────────────────────────────────────────

def mod_normal(c, rng):
    return c

def mod_darken(c, rng):
    factor = rng.uniform(0.4, 0.65)
    return tuple(max(0, min(255, int(v * factor))) for v in c)

def mod_lighten(c, rng):
    factor = rng.uniform(1.2, 1.6)
    return tuple(max(0, min(255, int(v * factor))) for v in c)

def mod_warm(c, rng):
    return (min(255, c[0] + 25), max(0, c[1] - 10), max(0, c[2] - 20))

def mod_cool(c, rng):
    return (max(0, c[0] - 20), max(0, c[1] - 5), min(255, c[2] + 30))

def mod_sepia(c, rng):
    gray = int(c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11)
    return (min(255, gray + 25), min(255, gray + 10), max(0, gray - 10))

def mod_neon(c, rng):
    return tuple(max(0, min(255, int(v * 1.4 + 30))) for v in c)

def mod_desaturated(c, rng):
    gray = int(c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11)
    return (gray, gray, gray)

def mod_vibrant(c, rng):
    mx = max(c) / 255.0
    if mx < 0.01:
        return c
    return tuple(min(255, int(v / mx)) for v in c)

def mod_vintage(c, rng):
    return (max(0, c[0] - 15), max(0, c[1] - 5), max(0, c[2] - 25))

def mod_nocturnal(c, rng):
    return tuple(max(0, min(255, int(v * 0.35 + 20))) for v in c)

def mod_high_contrast(c, rng):
    mx, mn = max(c), min(c)
    return (mx if c[0] > mn + 20 else mn, mx if c[1] > mn + 20 else mn, mx if c[2] > mn + 20 else mn)

def mod_soft(c, rng):
    return tuple(int(v * 0.8 + 40) for v in c)

MODIFIERS = [
    ('natural', mod_normal),
    ('dark', mod_darken),
    ('light', mod_lighten),
    ('warm', mod_warm),
    ('cool', mod_cool),
    ('sepia', mod_sepia),
    ('neon', mod_neon),
    ('monochrome', mod_desaturated),
    ('vibrant', mod_vibrant),
    ('vintage', mod_vintage),
    ('nocturnal', mod_nocturnal),
    ('high-contrast', mod_high_contrast),
    ('soft', mod_soft),
]

# Resolution labels and corresponding base tile sizes
RESOLUTIONS = [
    ('16x', 16, 1.99),
    ('32x', 32, 3.99),
    ('64x', 64, 5.99),
]


def make_uuid(name: str) -> str:
    raw = hashlib.sha256(name.encode()).hexdigest()[:32]
    return "-".join([raw[:8], raw[8:12], raw[12:16], raw[16:20], raw[20:32]])


def darken(c, factor=0.6):
    return tuple(max(0, min(255, int(v * factor))) for v in c)


def make_noise_image(name, color, size, rng, noise_range=18):
    img = Image.new('RGB', (size, size))
    pix = img.load()
    for x in range(size):
        for y in range(size):
            rng.seed(hash(f'{name}_{x}_{y}') & 0xFFFFFFFF)
            r, g, b = color
            rn = rng.randint(-noise_range, noise_range)
            gn = rng.randint(-noise_range, noise_range)
            bn = rng.randint(-noise_range, noise_range)
            pix[x, y] = (
                max(0, min(255, r + rn)),
                max(0, min(255, g + gn)),
                max(0, min(255, b + bn)),
            )
    return img


def make_stone_brick(name, color, size, rng):
    img = make_noise_image(name, color, size, rng)
    pix = img.load()
    cell = size // 4
    for x in range(size):
        for y in range(size):
            cx, cy = x % cell, y % cell
            if cx == 0 or cy == 0:
                r, g, b = pix[x, y]
                pix[x, y] = (max(0, r - 20), max(0, g - 20), max(0, b - 20))
    return img


def make_mossy(name, color, size, rng):
    img = make_noise_image(name, color, size, rng)
    pix = img.load()
    moss_green = (70, 130, 60)
    for x in range(size):
        for y in range(size):
            rng.seed(hash(f'{name}_moss_{x}_{y}') & 0xFFFFFFFF)
            if rng.random() < 0.25:
                r, g, b = pix[x, y]
                pix[x, y] = (
                    max(0, min(255, int(r * 0.6 + moss_green[0] * 0.4) + rng.randint(-10, 10))),
                    max(0, min(255, int(g * 0.6 + moss_green[1] * 0.4) + rng.randint(-10, 10))),
                    max(0, min(255, int(b * 0.6 + moss_green[2] * 0.4) + rng.randint(-10, 10))),
                )
    return img


def make_water(name, color, size, rng):
    img = make_noise_image(name, color, size, rng, noise_range=12)
    pix = img.load()
    for x in range(size):
        for y in range(size):
            r, g, b = pix[x, y]
            wave = int(6 * math.sin(x * 0.5 + y * 0.3))
            pix[x, y] = (max(0, min(255, r + wave)), max(0, min(255, g + wave)), max(0, min(255, b + wave)))
    return img


def make_lava(name, color, size, rng):
    img = make_noise_image(name, color, size, rng, noise_range=20)
    pix = img.load()
    for x in range(size):
        for y in range(size):
            r, g, b = pix[x, y]
            bright = rng.randint(-15, 15)
            pix[x, y] = (max(0, min(255, r + bright)), max(0, min(255, g + bright // 2)), max(0, min(255, b + bright // 3)))
    return img


def make_grass_side(name, color, size, rng):
    img = Image.new('RGB', (size, size))
    pix = img.load()
    top_color = BLOCK_COLORS['grass_top']
    for x in range(size):
        for y in range(size):
            rng.seed(hash(f'{name}_{x}_{y}') & 0xFFFFFFFF)
            t = y / size
            if t < 0.3:
                c = top_color
            elif t < 0.45:
                blend = (t - 0.3) / 0.15
                c = tuple(int(top_color[i] * (1 - blend) + color[i] * blend) for i in range(3))
            else:
                c = color
            noise = rng.randint(-15, 15)
            pix[x, y] = (max(0, min(255, c[0] + noise)), max(0, min(255, c[1] + noise)), max(0, min(255, c[2] + noise)))
    return img


def make_planks(name, color, size, rng):
    img = make_noise_image(name, color, size, rng)
    pix = img.load()
    strip = size // 8
    for x in range(size):
        for y in range(size):
            if y % strip == 0 or y % strip == 1:
                r, g, b = pix[x, y]
                pix[x, y] = (max(0, r - 15), max(0, g - 15), max(0, b - 15))
    return img


def make_wood(name, color, size, rng):
    img = make_noise_image(name, color, size, rng)
    pix = img.load()
    cx, cy = size // 2, size // 2
    for x in range(size):
        for y in range(size):
            rng.seed(hash(f'{name}_ring_{x}_{y}') & 0xFFFFFFFF)
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            ring = int(dist * 1.5) % 4
            if ring == 0 or ring == 1:
                r, g, b = pix[x, y]
                pix[x, y] = (max(0, r - 12), max(0, g - 12), max(0, b - 12))
    return img


def make_ore_block(name, color, size, rng):
    img = make_noise_image(name, color, size, rng)
    pix = img.load()
    for x in range(size):
        for y in range(size):
            rng.seed(hash(f'{name}_sparkle_{x}_{y}') & 0xFFFFFFFF)
            if rng.random() < 0.08:
                r, g, b = pix[x, y]
                pix[x, y] = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
    return img


def make_netherrack(name, color, size, rng):
    img = make_noise_image(name, color, size, rng, noise_range=25)
    pix = img.load()
    for x in range(size):
        for y in range(size):
            rng.seed(hash(f'{name}_ember_{x}_{y}') & 0xFFFFFFFF)
            if rng.random() < 0.06:
                r, g, b = pix[x, y]
                pix[x, y] = (min(255, r + 50), max(0, g - 10), max(0, b - 10))
    return img


def make_obsidian(name, color, size, rng):
    img = make_noise_image(name, color, size, rng, noise_range=8)
    pix = img.load()
    for x in range(size):
        for y in range(size):
            rng.seed(hash(f'{name}_sheen_{x}_{y}') & 0xFFFFFFFF)
            if rng.random() < 0.1:
                r, g, b = pix[x, y]
                pix[x, y] = (min(255, r + 15), min(255, g + 15), min(255, b + 15))
    return img


def make_pack_icon(name, size, colors, rng):
    """Generate a pack icon with a grid of block colors."""
    if not colors:
        return Image.new('RGB', (size, size), (128, 128, 128))
    img = Image.new('RGB', (size, size))
    pix = img.load()
    grid = 8
    cs = size // grid
    for gx in range(grid):
        for gy in range(grid):
            idx = (gy * grid + gx) % len(colors)
            c = colors[idx]
            for x in range(cs):
                for y in range(cs):
                    px = gx * cs + x
                    py = gy * cs + y
                    rng.seed(hash(f'icon_{name}_{px}_{py}') & 0xFFFFFFFF)
                    noise = rng.randint(-12, 12)
                    pix[px, py] = (max(0, min(255, c[0] + noise)), max(0, min(255, c[1] + noise)), max(0, min(255, c[2] + noise)))
    return img


SPECIAL = {
    'stone_brick': make_stone_brick,
    'mossy_cobblestone': make_mossy,
    'water_still': make_water,
    'water_flow': make_water,
    'lava_still': make_lava,
    'lava_flow': make_lava,
    'grass_side': make_grass_side,
    'planks_oak': make_planks,
    'planks_spruce': make_planks,
    'planks_birch': make_planks,
    'planks_jungle': make_planks,
    'planks_acacia': make_planks,
    'planks_dark_oak': make_planks,
    'wood_oak': make_wood,
    'wood_spruce': make_wood,
    'wood_birch': make_wood,
    'wood_jungle': make_wood,
    'wood_acacia': make_wood,
    'wood_dark_oak': make_wood,
    'gold_block': make_ore_block,
    'iron_block': make_ore_block,
    'diamond_block': make_ore_block,
    'emerald_block': make_ore_block,
    'redstone_block': make_ore_block,
    'coal_block': make_ore_block,
    'netherrack': make_netherrack,
    'obsidian': make_obsidian,
}


def build_pack_configs():
    """Build 500 texture pack configurations programmatically."""
    configs = []
    pack_index = 0

    for res_label, tile_size, price in RESOLUTIONS:
        for mod_label, mod_fn in MODIFIERS:
            for variant in range(13):  # 13 variants per modifier = 13×39×3 = 507 total
                pack_index += 1
                theme_seed = f'tp{pack_index:04d}_{mod_label}_{res_label}_v{variant}'

                noise_range = random.Random(theme_seed + '_nr').randint(10, 30)

                dir_name = f'{mod_label}-{res_label}-v{variant:02d}'
                pack_name = f'{mod_label.title()} {res_label} Pack v{variant + 1}'
                desc = (
                    f'A {mod_label} {res_label} texture pack variant {variant + 1}. '
                    f'Procedurally generated with unique noise profile.'
                )

                configs.append({
                    'dir': dir_name,
                    'name': pack_name,
                    'desc': desc,
                    'modify': mod_fn,
                    'noise_range': noise_range,
                    'seed': theme_seed,
                    'tile_size': tile_size,
                    'res_label': res_label,
                    'price': price,
                })

    return configs


def generate_pack(pack, pack_index, total):
    dir_name = pack['dir']
    pack_dir = os.path.join(BASE, dir_name)
    tex_dir = os.path.join(pack_dir, TEX_DIR)
    os.makedirs(tex_dir, exist_ok=True)

    seed = pack['seed']
    rng = random.Random()
    mod_fn = pack['modify']
    noise_range = pack['noise_range']
    tile_size = pack['tile_size']

    # Generate textures
    for name in BLOCK_NAMES:
        base_color = BLOCK_COLORS[name]
        color = mod_fn(base_color, rng)
        rng.seed(hash(f'{seed}_{name}') & 0xFFFFFFFF)

        maker = SPECIAL.get(name, make_noise_image)
        if maker == make_noise_image:
            img = make_noise_image(f'{seed}_{name}', color, tile_size, rng, noise_range=noise_range)
        else:
            img = maker(f'{seed}_{name}', color, tile_size, rng)

        filepath = os.path.join(tex_dir, f'{name}.png')
        img.save(filepath)

    # Generate pack icon
    rng.seed(hash(f'{seed}_icon') & 0xFFFFFFFF)
    icon_colors = [mod_fn(BLOCK_COLORS[n], rng) for n in BLOCK_NAMES]
    icon = make_pack_icon(seed, ICON_SIZE, icon_colors, rng)
    icon.save(os.path.join(pack_dir, 'pack_icon.png'))

    # Write manifest.json
    name_with_res = f'{pack["name"]}'
    # Strip price for manifest; it's metadata
    manifest = {
        'format_version': 2,
        'header': {
            'name': name_with_res,
            'description': pack['desc'],
            'uuid': make_uuid(f'header_{seed}'),
            'version': [1, 0, 0],
            'min_engine_version': [1, 20, 0],
        },
        'modules': [
            {
                'type': 'resources',
                'uuid': make_uuid(f'module_{seed}'),
                'version': [1, 0, 0],
            }
        ],
    }
    with open(os.path.join(pack_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)


def main():
    configs = build_pack_configs()
    total = len(configs)
    print(f'Generating {total} texture packs...')

    for i, pack in enumerate(configs, 1):
        print(f'[{i}/{total}] {pack["name"]} ({pack["dir"]})...', end=' ', flush=True)
        generate_pack(pack, i, total)
        print('OK')

    print(f'\nDone! Generated {total} packs to {BASE}')


if __name__ == '__main__':
    main()
