from PIL import Image, ImageDraw
import os, math

textures_dir = 'textures/blocks'
os.makedirs(textures_dir, exist_ok=True)

# Generate simple 16x16 block textures
blocks = {
    'stone.png': (100, 100, 100),
    'grass_top.png': (80, 160, 60),
    'grass_side.png': (100, 120, 70),
    'dirt.png': (120, 90, 50),
    'wood_oak.png': (150, 120, 70),
    'planks_oak.png': (180, 150, 90),
    'sand.png': (210, 190, 140),
    'cobblestone.png': (110, 110, 110),
    'brick.png': (160, 80, 60),
    'water_still.png': (50, 80, 180),
    'lava_still.png': (220, 100, 20),
    'gold_block.png': (255, 215, 0),
    'iron_block.png': (200, 200, 210),
    'diamond_block.png': (80, 200, 200),
    'emerald_block.png': (50, 200, 80),
    'redstone_block.png': (180, 20, 20),
    'coal_block.png': (30, 30, 30),
    'obsidian.png': (20, 15, 30),
    'netherrack.png': (120, 30, 30),
    'end_stone.png': (200, 190, 150),
}

for name, color in blocks.items():
    img = Image.new('RGB', (16, 16), color)
    draw = ImageDraw.Draw(img)
    # Add noise/texture
    for x in range(16):
        for y in range(16):
            r, g, b = color
            noise = (hash(f"{name}{x}{y}") % 30) - 15
            draw.point((x, y), fill=(
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise)),
            ))
    img.save(f'{textures_dir}/{name}')
    print(f"Generated {name}")

# Generate pack icon
icon = Image.new('RGB', (256, 256), (80, 160, 60))
draw = ImageDraw.Draw(icon)
draw.rectangle((30, 30, 226, 226), outline=(255, 255, 255), width=3)
draw.text((60, 110), "16x", fill=(255, 255, 255))
draw.text((60, 130), "Faithful", fill=(200, 200, 200))
icon.save('pack_icon.png')
print("Generated pack_icon.png")
