"""Generate procedural screenshots for Marketplace packs (no Minecraft needed)."""
from PIL import Image, ImageDraw, ImageFont
import os, json, math, random
from pathlib import Path

MC = Path(__file__).resolve().parent.parent
SKIN_DIR = MC / "skin-packs"
TEX_DIR = MC / "texture-packs"
WORLD_DIR = MC / "world-templates"
MASHUP_DIR = MC / "mashup-packs"
OUT = MC / "screenshots"
OUT.mkdir(exist_ok=True)

W, H = 1280, 720

def darken(c, amt=30):
    return tuple(max(0, v-amt) for v in c[:3])

def lighten(c, amt=30):
    return tuple(min(255, v+amt) for v in c[:3])

def draw_skin_display(d, cx, cy, name, colors):
    # Draw a character silhouette
    # Head
    d.ellipse([cx-30, cy-70, cx+30, cy-10], fill=colors[0] if len(colors) > 0 else (200,150,100), outline=(0,0,0))
    # Body
    body_c = colors[1] if len(colors) > 1 else (50,50,200)
    d.rectangle([cx-25, cy-10, cx+25, cy+40], fill=body_c, outline=(0,0,0))
    # Arms
    d.rectangle([cx-45, cy-5, cx-25, cy+30], fill=body_c, outline=(0,0,0))
    d.rectangle([cx+25, cy-5, cx+45, cy+30], fill=body_c, outline=(0,0,0))
    # Legs
    leg_c = colors[2] if len(colors) > 2 else (50,50,100)
    d.rectangle([cx-20, cy+40, cx-5, cy+70], fill=leg_c, outline=(0,0,0))
    d.rectangle([cx+5, cy+40, cx+20, cy+70], fill=leg_c, outline=(0,0,0))

def draw_mini_block(d, x, y, sz, color, label=""):
    d.rectangle([x, y, x+sz, y+sz], fill=color, outline=(0,0,0))
    if label:
        d.text((x+2, y+2), label, fill=(255,255,255))

def gen_skin_screenshots(pack_dir):
    pack_name = pack_dir.name
    mf = json.loads((pack_dir / "manifest.json").read_text())
    name = mf.get("header", {}).get("name", pack_name)
    
    pack_out = OUT / pack_name
    pack_out.mkdir(exist_ok=True)
    
    for shot_idx in range(4):
        img = Image.new("RGB", (W, H), (30, 30, 45))
        d = ImageDraw.Draw(img)
        
        # Grid background
        for gx in range(0, W, 40):
            d.line([(gx, 0), (gx, H)], fill=(40, 40, 55), width=1)
        for gy in range(0, H, 40):
            d.line([(0, gy), (W, gy)], fill=(40, 40, 55), width=1)
        
        title = f"{name} - Showcase"
        d.text((50, 30), title, fill=(255, 255, 255))
        d.text((50, 60), f"Minecraft Bedrock | Skin Pack | Shot {shot_idx+1}/4", fill=(180, 180, 180))
        
        # Draw 4 skin figures
        colors_pool = [(200,100,100), (100,150,200), (100,200,100), (200,200,100),
                       (200,100,200), (100,200,200), (200,150,100), (150,100,200)]
        for i in range(4):
            cx = 150 + i * 300
            cy = 350
            c1 = colors_pool[(shot_idx + i) % len(colors_pool)]
            c2 = colors_pool[(shot_idx + i + 2) % len(colors_pool)]
            c3 = colors_pool[(shot_idx + i + 4) % len(colors_pool)]
            draw_skin_display(d, cx, cy, f"Skin {i+1}", [c1, c2, c3])
            d.text((cx-30, cy+80), f"Skin {i+1}", fill=(200,200,200))
        
        d.text((W//2-150, H-40), "© Bedrock Minemods", fill=(100,100,120))
        img.save(pack_out / f"screenshot_{shot_idx+1}.png")
    
    return 4

def gen_texture_screenshots(pack_dir):
    pack_name = pack_dir.name
    mf = json.loads((pack_dir / "manifest.json").read_text())
    name = mf.get("header", {}).get("name", pack_name)
    
    pack_out = OUT / pack_name
    pack_out.mkdir(exist_ok=True)
    
    # Check for generated block textures
    block_dir = pack_dir / "textures" / "blocks"
    
    blocks = []
    if block_dir.exists():
        blocks = sorted(block_dir.glob("*.png"))[:24]
    
    for shot_idx in range(4):
        img = Image.new("RGB", (W, H), (25, 30, 35))
        d = ImageDraw.Draw(img)
        
        title = f"{name} - Preview"
        d.text((50, 30), title, fill=(255, 255, 255))
        d.text((50, 60), f"Minecraft Bedrock | Texture Pack | Shot {shot_idx+1}/4", fill=(180, 180, 180))
        
        # Texture grid
        if blocks:
            grid_size = 6 if len(blocks) >= 36 else int(math.sqrt(len(blocks)))
            cell = 80
            start_x = (W - grid_size * cell) // 2
            start_y = 120
            for i, bp in enumerate(blocks[:grid_size*grid_size]):
                gx = i % grid_size
                gy = i // grid_size
                try:
                    tex = Image.open(bp).resize((cell, cell), Image.NEAREST)
                    img.paste(tex, (start_x + gx * cell, start_y + gy * cell))
                except:
                    color = (100 + (i * 30) % 155, 80, 120)
                    d.rectangle([start_x + gx * cell, start_y + gy * cell,
                                 start_x + (gx+1) * cell, start_y + (gy+1) * cell],
                                fill=color, outline=(60,60,60))
                    d.text((start_x + gx * cell + 15, start_y + gy * cell + 30),
                           bp.stem[:8], fill=(255,255,255))
        
        # Color bar at bottom
        colors = [(90,175,65), (130,95,60), (215,200,150), (120,115,110),
                  (155,125,75), (185,155,95), (255,215,0), (80,200,210)]
        bar_y = H - 60
        bar_w = W // len(colors)
        for i, c in enumerate(colors):
            d.rectangle([i*bar_w, bar_y, (i+1)*bar_w, bar_y+30], fill=c, outline=(0,0,0))
        
        d.text((W//2-150, H-30), "© Bedrock Minemods", fill=(100,100,120))
        img.save(pack_out / f"screenshot_{shot_idx+1}.png")
    
    return 4

def gen_world_screenshots(pack_dir):
    pack_name = pack_dir.name
    mf = json.loads((pack_dir / "manifest.json").read_text())
    name = mf.get("header", {}).get("name", pack_name)
    
    pack_out = OUT / pack_name
    pack_out.mkdir(exist_ok=True)
    
    for shot_idx in range(4):
        img = Image.new("RGB", (W, H), (50, 100 + shot_idx * 20, 150 - shot_idx * 10))
        d = ImageDraw.Draw(img)
        
        # Landscape elements
        cx, cy = W // 2, H // 2
        # Ground
        d.rectangle([0, cy+50, W, H], fill=(50, 120 + shot_idx * 20, 50))
        d.rectangle([0, cy+70, W, H], fill=(80, 100, 50))
        # Mountains
        for mx in range(3):
            mcx = cx - 200 + mx * 200
            mh = 150 + shot_idx * 20 + mx * 30
            d.polygon([(mcx-120, cy+50), (mcx, cy-mh), (mcx+120, cy+50)], fill=(100, 130, 100))
        # Sun/moon
        d.ellipse([cx-40, 80, cx+40, 160], fill=(255, 215 + shot_idx * 10, 0))
        # Clouds
        for ci in range(3):
            cdx = 200 + ci * 350 - shot_idx * 50
            d.ellipse([cdx, 120 + ci * 40, cdx+120, 150 + ci * 40], fill=(220, 220, 230, 180))
        
        title = f"{name} - World Preview"
        d.text((50, 30), title, fill=(255, 255, 255))
        d.text((50, 60), f"Minecraft Bedrock | World Template | Shot {shot_idx+1}/4", fill=(200, 200, 200))
        d.text((cx-100, H-40), "© Bedrock Minemods", fill=(150, 150, 150))
        img.save(pack_out / f"screenshot_{shot_idx+1}.png")
    
    return 4

def gen_mashup_screenshots(pack_dir):
    return gen_texture_screenshots(pack_dir)

GENERATORS = {
    "skin-packs": gen_skin_screenshots,
    "texture-packs": gen_texture_screenshots,
    "world-templates": gen_world_screenshots,
    "mashup-packs": gen_mashup_screenshots,
}

def main():
    total = 0
    for sd, gen_fn in GENERATORS.items():
        src = MC / sd
        if not src.exists():
            continue
        count = 0
        for pd in sorted(src.iterdir()):
            if not pd.is_dir() or pd.name.startswith("."):
                continue
            if not (pd / "manifest.json").exists():
                continue
            n = gen_fn(pd)
            count += 1
            total += n
            print(f"  {pd.name:30s} {n} screenshots")
        print(f"  --- {sd}: {count} packs ---")
    print(f"\n=== SCREENSHOTS GENERATED: {total} total ===")
    print(f"  Output: {OUT}")

if __name__ == "__main__":
    main()
