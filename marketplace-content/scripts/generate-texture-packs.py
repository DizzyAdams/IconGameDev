from PIL import Image
import os, math, random, json

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

def darken(c, factor=0.6):
    return tuple(max(0, min(255, int(v * factor))) for v in c)

def make_noise_image(name, color, size, rng, noise_range=18):
    img = Image.new('RGB', (size, size))
    pix = img.load()
    for x in range(size):
        for y in range(size):
            rng.seed(hash(f'{name}_{x}_{y}') & 0xFFFFFFFF)
            r, g, b = color
            noise = rng.randint(-noise_range, noise_range)
            rn = rng.randint(-noise_range, noise_range)
            gn = rng.randint(-noise_range, noise_range)
            bn = rng.randint(-noise_range, noise_range)
            pix[x, y] = (
                max(0, min(255, r + noise + rn)),
                max(0, min(255, g + noise + gn)),
                max(0, min(255, b + noise + bn)),
            )
    return img

def make_stone_brick(name, color, size, rng):
    """Stone brick with subtle grid pattern."""
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
    """Gem/mineral blocks with subtle sparkle."""
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

PACKS = [
    {
        'dir': '32x-natural',
        'name': '32x Natural',
        'desc': 'Enhanced 32x32 textures that make your world look stunning while keeping the vanilla feel.',
        'header_uuid': '3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f',
        'module_uuid': '4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a',
        'modify': lambda c, rng: c,
        'noise_range': 18,
        'icon_label': '32x',
        'icon_sub': 'Natural',
    },
    {
        'dir': 'dark-mode',
        'name': 'Dark Mode',
        'desc': 'A moody dark texture pack. Everything is darker, edgier, and more atmospheric.',
        'header_uuid': '4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9b',
        'module_uuid': '5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b',
        'modify': lambda c, rng: darken(c, 0.55),
        'noise_range': 22,
        'icon_label': 'Dark',
        'icon_sub': 'Mode',
    },
]

BLOCK_NAMES = list(BLOCK_COLORS.keys())

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

def generate_pack(pack):
    pack_dir = os.path.join(BASE, pack['dir'])
    tex_dir = os.path.join(pack_dir, TEX_DIR)
    os.makedirs(tex_dir, exist_ok=True)

    rng = random.Random()

    # Generate textures
    for name in BLOCK_NAMES:
        base_color = BLOCK_COLORS[name]
        color = pack['modify'](base_color, rng)
        rng.seed(hash(name) & 0xFFFFFFFF)

        maker = SPECIAL.get(name, make_noise_image)
        if maker == make_noise_image:
            img = make_noise_image(name, color, SIZE, rng, noise_range=pack['noise_range'])
        else:
            img = maker(name, color, SIZE, rng)

        filepath = os.path.join(tex_dir, f'{name}.png')
        img.save(filepath)
        print(f'  {os.path.join(pack["dir"], TEX_DIR, name)}.png')

    # Generate pack icon
    rng.seed(hash(pack['dir']) & 0xFFFFFFFF)
    icon_colors = [pack['modify'](BLOCK_COLORS[n], rng) for n in BLOCK_NAMES]
    icon = make_pack_icon(pack['dir'], ICON_SIZE, icon_colors, rng)
    icon_path = os.path.join(pack_dir, 'pack_icon.png')
    icon.save(icon_path)
    print(f'  {os.path.join(pack["dir"], "pack_icon.png")}')

    # Write manifest.json
    manifest = {
        'format_version': 2,
        'header': {
            'name': pack['name'],
            'description': pack['desc'],
            'uuid': pack['header_uuid'],
            'version': [1, 0, 0],
            'min_engine_version': [1, 20, 0],
        },
        'modules': [
            {
                'type': 'resources',
                'uuid': pack['module_uuid'],
                'version': [1, 0, 0],
            }
        ],
    }
    manifest_path = os.path.join(pack_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f'  {os.path.join(pack["dir"], "manifest.json")}')

def main():
    for pack in PACKS:
        print(f'\nGenerating {pack["name"]}...')
        generate_pack(pack)
    print('\nDone!')

if __name__ == '__main__':
    main()
