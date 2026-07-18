#!/usr/bin/env python3
"""
Generate 256x256 pack_icon.png for every skin pack that's missing one.
Uses theme-derived gradient colors + centered "IMM" text + decorative border.
"""

import os
import hashlib
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

SKIN_PACKS_DIR = Path(r"C:\Users\forrydev\Desktop\IconGameDev\skin-packs")

# Theme to gradient color pairs: mapping of keyword -> (primary_hex, secondary_hex)
THEME_COLORS = {
    "zombie":    ("#2d5a27", "#1a3a15"),
    "woodland":  ("#3d5a2e", "#2a4020"),
    "west":      ("#8b6914", "#6b4f10"),
    "werewolf":  ("#4a2e2e", "#3a1e1e"),
    "void":      ("#2d1b4e", "#1a0e30"),
    "viking":    ("#3a4a5a", "#2a3a48"),
    "vampire":   ("#5c1a1a", "#3e1010"),
    "toxic":     ("#3a5a1a", "#2a4010"),
    "thunder":   ("#4a4a1a", "#3a3a12"),
    "soldier":   ("#1a3a5a", "#102a48"),
    "steampunk": ("#5a4a2e", "#483a20"),
    "explorer":  ("#1a1a3e", "#10102e"),
    "ninja":     ("#1a1a1a", "#0e0e0e"),
    "shadow":    ("#1a1a2e", "#101020"),
    "samurai":   ("#5a1a1a", "#401212"),
    "elite":     ("#4a1a4a", "#3a123a"),
    "royal":     ("#4a1a4a", "#3a123a"),
    "robot":     ("#3a3a4a", "#2a2a3a"),
    "pirate":    ("#3a2a1a", "#2a1e12"),
    "phoenix":   ("#5a2a1a", "#401e12"),
    "ocean":     ("#1a2e5a", "#102048"),
    "neon":      ("#1a1a3e", "#10102e"),
    "mythic":    ("#2e1a4a", "#1e103a"),
    "mushroom":  ("#5a3a1a", "#4a2a12"),
    "medieval":  ("#4a3a2e", "#3a2a20"),
    "mecha":     ("#2e3a4a", "#1e2a3a"),
    "magic":     ("#2e1a3e", "#1e102e"),
    "lava":      ("#5a1a0e", "#401206"),
    "jungle":    ("#1a4a1a", "#123a12"),
    "grim":      ("#2e2e2e", "#1e1e1e"),
    "ghost":     ("#2e304e", "#202040"),
    "galaxy":    ("#1a1a4a", "#10103a"),
    "fairy":     ("#4a1a4a", "#3a123a"),
    "fantasy":   ("#2e3e4a", "#1e2e3a"),
    "egyptian":  ("#8a6e1a", "#725812"),
    "dwarven":   ("#5a4a2e", "#483a20"),
    "dream":     ("#2e1a4e", "#1e103e"),
    "dragon":    ("#5a1a1a", "#401212"),
    "dinosaur":  ("#2e5a1a", "#1e4a12"),
    "desert":    ("#8a7a1a", "#726212"),
    "demonic":   ("#5a0e0e", "#400808"),
    "cyberpunk": ("#1a0e2e", "#0e081e"),
    "crystal":   ("#2e4e5a", "#1e3e4a"),
    "clockwork": ("#3a3a2e", "#2a2a20"),
    "celestial": ("#1a1a5a", "#10104a"),
    "carnival":  ("#5a1a3e", "#4a122e"),
    "candy":     ("#5a2e3e", "#4a1e2e"),
    "arctic":    ("#2e4a5a", "#1e3a4a"),
    "aquatic":   ("#0e2e5a", "#081e4a"),
    "anime":     ("#2e1a3e", "#1e102e"),
    "angelic":   ("#2e2e5a", "#1e1e4a"),
}

# Fallback brand colors
BRAND_EMERALD = "#10b981"


def hash_color(theme_name: str):
    """Derive a color pair from theme name via hash."""
    h = hashlib.md5(theme_name.encode()).hexdigest()
    r1 = int(h[0:2], 16) % 200 + 30
    g1 = int(h[2:4], 16) % 200 + 30
    b1 = int(h[4:6], 16) % 200 + 30
    r2 = max(0, r1 - 40)
    g2 = max(0, g1 - 40)
    b2 = max(0, b1 - 40)
    return (f"#{r1:02x}{g1:02x}{b1:02x}", f"#{r2:02x}{g2:02x}{b2:02x}")


def get_theme_colors(pack_name: str):
    """Get primary and secondary colors for a pack theme."""
    name_lower = pack_name.lower().replace("-", " ").replace("_", " ")
    
    for key, colors in THEME_COLORS.items():
        if key in name_lower:
            return colors
    
    # Fallback to hash
    return hash_color(pack_name)


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_gradient(width, height, color1, color2):
    """Generate a vertical gradient image from color1 to color2."""
    img = Image.new("RGBA", (width, height))
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    pixels = []
    for y in range(height):
        ratio = y / height
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        row = [(r, g, b, 255)] * width
        pixels.extend(row)
    img.putdata(pixels)
    return img


def generate_pack_icon(pack_name, output_path):
    """Generate a 256x256 pack_icon.png for the given pack."""
    try:
        size = 256
        primary_hex, secondary_hex = get_theme_colors(pack_name)
        c1 = hex_to_rgb(primary_hex)
        c2 = hex_to_rgb(secondary_hex)
        
        # Create gradient background
        img = generate_gradient(size, size, c1, c2)
        draw = ImageDraw.Draw(img)
        
        # Decorative border - 4 concentric rings
        for i in range(4):
            alpha = 40 + i * 15
            draw.rectangle([i, i, size - 1 - i, size - 1 - i],
                          outline=(255, 255, 255, alpha), width=2)
        
        # Inner glow band
        inner_margin = 20
        draw.rectangle([inner_margin, inner_margin, 
                        size - inner_margin, size - inner_margin],
                       outline=(255, 255, 255, 30), width=1)
        
        # Try to load a bold font
        font = None
        font_size = 80
        font_paths = [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, font_size)
                    break
                except Exception:
                    continue
        
        # Draw "IMM" centered
        text = "IMM"
        text_color = (255, 255, 255, 220)
        
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
        else:
            bbox = draw.textbbox((0, 0), text)
        
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (size - tw) // 2
        ty = (size - th) // 2 - 10
        
        if font:
            draw.text((tx + 2, ty + 2), text, font=font, fill=(0, 0, 0, 100))
            draw.text((tx, ty), text, font=font, fill=text_color)
        else:
            draw.text((tx + 2, ty + 2), text, fill=(0, 0, 0, 100))
            draw.text((tx, ty), text, fill=text_color)
        
        # Save
        img.save(output_path, "PNG")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("pack_icon.png Generator for IconMineMods Skin Packs")
    print("=" * 60)
    
    if not SKIN_PACKS_DIR.exists():
        print(f"ERROR: Directory not found: {SKIN_PACKS_DIR}")
        sys.exit(1)
    
    # Find all subdirectories
    pack_dirs = sorted([d for d in SKIN_PACKS_DIR.iterdir() if d.is_dir()])
    print(f"\nFound {len(pack_dirs)} pack directories.\n")
    
    generated = 0
    skipped = 0
    failed = 0
    regenerated = 0
    
    for pack_dir in pack_dirs:
        pack_name = pack_dir.name
        icon_path = pack_dir / "pack_icon.png"
        
        if icon_path.exists():
            # Check if it's a valid 256x256 PNG
            try:
                with Image.open(icon_path) as img:
                    w, h = img.size
                    if w == 256 and h == 256:
                        print(f"  [SKIP] {pack_name}: already valid 256x256")
                        skipped += 1
                        continue
                    else:
                        print(f"  [REGEN] {pack_name}: wrong dims ({w}x{h})")
                        regenerated += 1
            except Exception:
                print(f"  [REGEN] {pack_name}: corrupt PNG")
                regenerated += 1
        else:
            print(f"  [GEN] {pack_name}: MISSING pack_icon.png")
        
        if generate_pack_icon(pack_name, icon_path):
            # Verify
            try:
                with Image.open(icon_path) as img:
                    w, h = img.size
                    if w == 256 and h == 256:
                        size_kb = os.path.getsize(icon_path) / 1024
                        print(f"    -> OK: 256x256, {size_kb:.1f} KB")
                        generated += 1
                    else:
                        print(f"    -> FAIL: wrong size {w}x{h}")
                        failed += 1
            except Exception as e:
                print(f"    -> FAIL: {e}")
                failed += 1
        else:
            print(f"    -> FAIL: generation error")
            failed += 1
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total packs:  {len(pack_dirs)}")
    print(f"  Valid (skip): {skipped}")
    print(f"  Generated:    {generated}")
    print(f"  Regenerated:  {regenerated}")
    print(f"  Failed:       {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
