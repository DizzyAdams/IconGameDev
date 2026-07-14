from PIL import Image
import os

skins_data = [
    ("samurai", (180, 20, 20), (50, 50, 50)),         # crimson / dark
    ("ninja", (10, 10, 50), (20, 20, 20)),             # dark blue / black
    ("monk", (255, 165, 0), (255, 200, 50)),           # orange / gold
    ("ronin", (160, 160, 160), (200, 200, 200)),       # gray / white
    ("shrine_maiden", (255, 255, 255), (220, 50, 50)), # white / red
    ("oni_slayer", (100, 30, 120), (200, 170, 0)),     # purple / gold
    ("sensei", (100, 70, 40), (80, 140, 70)),          # brown / green
    ("shadow_blade", (10, 10, 10), (0, 100, 100)),     # black / cyan
]

out_dir = os.path.join('skin-packs', 'anime-warriors', 'textures', 'skins')
os.makedirs(out_dir, exist_ok=True)

for name, primary, secondary in skins_data:
    img = Image.new('RGBA', (64, 64), (*primary, 255))
    pixels = img.load()
    for x in range(64):
        for y in range(64):
            r, g, b, a = pixels[x, y]
            if (x // 4 + y // 4) % 3 == 0:
                pixels[x, y] = (*secondary, 255)
    img.save(os.path.join(out_dir, f'{name}.png'))
    print(f"Generated {name}.png")

icon = Image.new('RGBA', (300, 300), (140, 20, 20, 255))
icon.save(os.path.join(out_dir, 'icon.png'))
print("Generated icon.png")
