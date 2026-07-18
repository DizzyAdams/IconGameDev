#!/usr/bin/env python3
"""Generate missing Roblox UGC asset PNGs from catalog. 512x512, mono-dark + neon."""
import json, os, hashlib, math, random
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CATALOG = os.path.join(ROOT, "catalog", "roblox_catalog.json")
ASSETS = os.path.join(ROOT, "assets")
ITEMS = os.path.join(ROOT, "items")
SIZE = (512, 512)

COLORS = {
    "classic_shirt": [(10,10,20),(30,30,60),(0,200,255)],
    "classic_pants": [(10,10,20),(30,30,60),(200,0,200)],
    "avatar_accessory": [(15,10,25),(40,20,60),(255,200,0)],
    "game_pass": [(8,8,16),(20,20,40),(0,255,120)],
}

def make_asset_image(item_name, item_type, seed_str):
    rng = random.Random(hashlib.md5(seed_str.encode()).hexdigest())
    palette = COLORS.get(item_type, COLORS["classic_shirt"])
    bg, mid, accent = palette
    img = Image.new("RGBA", SIZE, (*bg, 255))
    draw = ImageDraw.Draw(img)

    # Circuit-pattern background
    for _ in range(rng.randint(30, 60)):
        x = rng.randint(0, SIZE[0])
        y = rng.randint(0, SIZE[1])
        col = tuple(c + rng.randint(-10, 10) for c in mid)
        draw.rectangle([x, y, x+4, y+4], fill=(*col, 60))

    # Neon accent lines
    for _ in range(rng.randint(5, 15)):
        x = rng.randint(0, SIZE[0])
        y = rng.randint(0, SIZE[1])
        w = rng.randint(20, 80)
        h = rng.randint(2, 6)
        col = tuple(c + rng.randint(-20, 20) for c in accent)
        draw.rectangle([x, y, x+w, y+h], fill=(*col, 200))

    # Hex corners
    for cx, cy in [(50,50), (462,50), (50,462), (462,462)]:
        pts = []
        for a in range(6):
            ang = math.radians(a*60)
            pts.append((cx+20*math.cos(ang), cy+20*math.sin(ang)))
        draw.polygon(pts, outline=(*accent, 180), width=2)

    return img

def main():
    with open(CATALOG, encoding='utf-8') as f:
        data = json.load(f)
    items = data['items']
    total = len(items)
    print(f"Catalog: {total} items")

    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(ITEMS, exist_ok=True)

    existing = set(f.replace('.png','') for f in os.listdir(ASSETS) if f.endswith('.png'))

    generated = 0
    for item in items:
        item_name = item['name']
        item_type = item['type']
        # Sanitize filename
        safe = item_name.replace(" ", "_").replace("/","_").replace("\\","_")
        fname = safe + ".png"

        if fname.replace('.png','') in existing:
            continue  # already exists

        out = os.path.join(ASSETS, fname)
        if os.path.isfile(out):
            continue

        img = make_asset_image(item_name, item_type, f"{item['id']}_{item_name}")
        img.save(out)
        generated += 1
        if generated % 500 == 0:
            print(f"  {generated} generated...")

    print(f"\nGenerated: {generated} new assets")
    print(f"Total assets now: {len(os.listdir(ASSETS))}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
