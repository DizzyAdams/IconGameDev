"""Generate marketing assets (thumbnails, banners) for all packs."""
from PIL import Image, ImageDraw
import os, json, zipfile, tempfile, math
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DIST = BASE / 'dist'
MARKETING = BASE / 'output' / 'marketing'
THUMBS = MARKETING / 'thumbnails'
BANNERS = MARKETING / 'banners'

MARKETING.mkdir(parents=True, exist_ok=True)
THUMBS.mkdir(exist_ok=True)
BANNERS.mkdir(exist_ok=True)

THEME_COLORS = {
    'knight': (70, 130, 180), 'warrior': (180, 30, 30), 'anime': (255, 100, 200),
    'halloween': (255, 140, 0), 'christmas': (255, 0, 0), 'superhero': (0, 0, 200),
    'animal': (50, 200, 50), 'pixel': (100, 200, 100), 'fantasy': (128, 0, 128),
    'summer': (255, 200, 50), 'sonic': (0, 0, 255), 'waifu': (255, 150, 200),
    'kawaii': (255, 200, 220), 'gothic': (50, 0, 50), 'neon': (0, 255, 255),
    'japanese': (200, 50, 50), 'korean': (255, 200, 220), 'egyptian': (255, 215, 0),
    'horror': (0, 0, 0), 'nightmare': (50, 0, 0), 'redstone': (200, 0, 0),
    'pride': (255, 0, 255), 'tadc': (200, 0, 0), 'hive': (255, 200, 0),
    'genshin': (100, 200, 255), 'fnaf': (100, 50, 50), 'kitty': (255, 200, 220),
    'rpg': (200, 150, 50), 'streetwear': (50, 50, 50), 'greek': (200, 200, 200),
    'norse': (100, 100, 150), 'steampunk': (150, 100, 50), 'dragon': (255, 100, 0),
    'pokemon': (255, 200, 0), 'space': (0, 50, 100),
    'faithful': (120, 180, 80), 'natural': (100, 180, 100), 'dark': (20, 20, 30),
    'x64': (100, 150, 200), 'x128': (200, 100, 200), 'pastel': (200, 200, 255),
    'medieval': (180, 120, 60), 'anime_style': (255, 150, 200),
    'skyblock': (135, 206, 235), 'parkour': (255, 140, 0), 'oneblock': (80, 20, 120),
    'survival': (100, 180, 255), 'bedwars': (255, 200, 50), 'skygrid': (80, 20, 120),
    'dragon': (60, 0, 0), 'city': (100, 150, 200),
    'mashup': (200, 150, 50),
}

def guess_color(name):
    name_lower = name.lower()
    for key, color in THEME_COLORS.items():
        if key in name_lower:
            return color
    return (100, 100, 120)

def make_pack_icon(size, primary, secondary):
    img = Image.new('RGBA', (size, size))
    draw = ImageDraw.Draw(img)
    cx = cy = size // 2
    # radial gradient
    for i in range(size):
        for j in range(size):
            dist = ((i - cx) ** 2 + (j - cy) ** 2) ** 0.5
            t = dist / (size * 0.7)
            r = int(primary[0] * (1 - t) + secondary[0] * t)
            g = int(primary[1] * (1 - t) + secondary[1] * t)
            b = int(primary[2] * (1 - t) + secondary[2] * t)
            draw.point((i, j), fill=(min(255, r), min(255, g), min(255, b), 255))
    # inner circle accent
    draw.ellipse([cx-size//4, cy-size//4, cx+size//4, cy+size//4],
                 fill=(*secondary, 180), outline=(*primary, 255), width=3)
    return img

def make_thumbnail(name, primary, secondary):
    w, h = 800, 450
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    # gradient background
    for y in range(h):
        t = y / h
        r = int(primary[0] * (1 - t) + secondary[0] * t)
        g = int(primary[1] * (1 - t) + secondary[1] * t)
        b = int(primary[2] * (1 - t) + secondary[2] * t)
        draw.line([(0, y), (w, y)], fill=(min(255, r), min(255, g), min(255, b)))
    accent = tuple(min(255, int(c * 1.3)) for c in primary)
    # decorative circles
    for cx, cy, r in [(150, 320, 80), (650, 120, 60), (400, 400, 40)]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*accent, 120), outline=None)
    # pack name
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("segoeui.ttf", 42)
        small = ImageFont.truetype("segoeui.ttf", 22)
    except:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    draw.text((40, 30), name.replace('-', ' ').title(), fill=(255, 255, 255), font=font)
    draw.text((40, 80), f"Minecraft Bedrock .mcpack", fill=(220, 220, 220), font=small)
    draw.text((w-200, h-50), f"{round(os.path.getsize(DIST/name) if (DIST/name).exists() else 0)/1024:.0f} KB", fill=(255, 215, 0), font=small)
    return img

def make_banner(name, primary, secondary):
    w, h = 1920, 1080
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(primary[0] * (1 - t*0.7))
        g = int(primary[1] * (1 - t*0.7))
        b = int(primary[2] * (1 - t*0.7))
        draw.line([(0, y), (w, y)], fill=(min(255, r), min(255, g), min(255, b)))
    return img

def main():
    mcpack_files = sorted(DIST.glob('*.mcpack'))
    print(f"=== Generating Marketing Assets for {len(mcpack_files)} packs ===\n")

    for f in mcpack_files:
        name = f.stem
        primary = guess_color(name)
        secondary = tuple(min(255, int(c * 0.6 + 40)) for c in primary)

        # pack icon 256x256
        icon = make_pack_icon(256, primary, secondary)
        icon.save(str(THUMBS / f'{name}_icon.png'))

        # thumbnail 800x450
        thumb = make_thumbnail(f.name, primary, secondary)
        thumb.save(str(THUMBS / f'{name}_thumbnail.jpg'), 'JPEG', quality=88)

        # banner 1920x1080 (just for featured packs - save space)
        banner = make_banner(f.name, primary, secondary)
        banner.save(str(BANNERS / f'{name}_banner.jpg'), 'JPEG', quality=85)

        size_kb = f.stat().st_size / 1024
        print(f"  {f.name} ({size_kb:.0f} KB) -> icon + thumbnail + banner")

    print(f"\n  Output: {MARKETING}")
    print(f"  Icons/Thumbs: {THUMBS}")
    print(f"  Banners: {BANNERS}")

if __name__ == '__main__':
    main()
