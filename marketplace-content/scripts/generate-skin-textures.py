from PIL import Image
import os

base_dir = os.path.join(os.path.dirname(__file__), '..', 'skin-packs', 'medieval-knights')
skins_dir = os.path.join(base_dir, 'textures', 'skins')
os.makedirs(skins_dir, exist_ok=True)

# (name, primary_color, secondary_color)
skins_data = [
    ("knight", (70, 130, 180), (200, 200, 210)),
    ("archer", (34, 139, 34), (210, 180, 140)),
    ("mage", (128, 0, 128), (180, 130, 200)),
    ("paladin", (255, 215, 0), (255, 255, 255)),
    ("necromancer", (20, 20, 30), (80, 0, 80)),
    ("berserker", (139, 0, 0), (80, 80, 80)),
    ("rogue", (30, 30, 30), (100, 100, 100)),
    ("druid", (139, 69, 19), (60, 179, 113)),
]

for name, primary, secondary in skins_data:
    img = Image.new('RGBA', (64, 64), (*primary, 255))
    pixels = img.load()
    for x in range(64):
        for y in range(64):
            r, g, b, a = pixels[x, y]
            if (x + y) % 8 < 3:
                pixels[x, y] = (*secondary, 255)
    img.save(os.path.join(skins_dir, f'{name}.png'))
    print(f"Generated {name}.png")

icon = Image.new('RGBA', (300, 300), (50, 50, 70, 255))
ipixels = icon.load()
for x in range(300):
    for y in range(300):
        r, g, b, a = ipixels[x, y]
        cx, cy = 150, 150
        dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if dist < 100:
            angle = (x + y) * 0.05
            sr = int(50 + 30 * (angle % 1))
            sg = int(50 + 20 * ((angle * 0.7) % 1))
            sb = int(70 + 40 * ((angle * 1.3) % 1))
            ipixels[x, y] = (min(sr, 255), min(sg, 255), min(sb, 255), 255)
icon.save(os.path.join(skins_dir, 'icon.png'))
print("Generated icon.png")
