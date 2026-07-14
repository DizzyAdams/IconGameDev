from PIL import Image, ImageDraw, ImageFont
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'world-templates')

def make_icon_bg(draw, size, color):
    draw.rectangle([0, 0, size, size], fill=color)
    # subtle gradient overlay
    for i in range(size):
        alpha = int(20 * (1 - i / size))
        draw.rectangle([0, i, size, i + 1], fill=(0, 0, 0, alpha))

def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_text(draw, size, lines, base_y, color=(255, 255, 255)):
    fs_title = size // 10
    fs_sub = size // 18
    try:
        font_title = ImageFont.truetype("segoeui.ttf", fs_title)
        font_sub = ImageFont.truetype("segoeui.ttf", fs_sub)
    except:
        font_title = font_sub = ImageFont.load_default()

    y = base_y
    for i, line in enumerate(lines):
        font = font_title if i == 0 else font_sub
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((size - tw) // 2, y), line, fill=color, font=font)
        y += bbox[3] - bbox[1] + 8

# ---- Skyblock Pro ----
def gen_skyblock(path):
    size = 256
    img = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(img)
    make_icon_bg(draw, size, (135, 206, 235))

    cx, cy = size // 2, size // 2 - 20
    bw, bh = 80, 30
    # island shape - grass top, dirt below
    # grass layer
    draw.ellipse([cx - bw // 2 - 10, cy - 20, cx + bw // 2 + 10, cy + 10], fill=(87, 168, 47))
    # dirt layer
    draw.rectangle([cx - bw // 2, cy + 5, cx + bw // 2, cy + bh], fill=(139, 90, 43))
    # grass block top detail
    draw.ellipse([cx - bw // 2, cy + 5, cx + bw // 2, cy + 20], fill=(87, 168, 47))
    # bottom dirt
    draw.rectangle([cx - bw // 2 + 5, cy + bh, cx + bw // 2 - 5, cy + bh + 30], fill=(139, 90, 43))

    # tree
    draw.rectangle([cx - 5, cy - bh - 10, cx + 5, cy - 20], fill=(101, 67, 33))
    draw.ellipse([cx - 20, cy - bh - 30, cx + 20, cy - 15], fill=(34, 139, 34))

    # floating islands in bg
    for fx, fy, s in [(40, 40, 20), (210, 60, 15), (180, 180, 12)]:
        draw.ellipse([fx - s, fy - s // 2, fx + s, fy + s // 2], fill=(100, 180, 60))

    draw_text(draw, size, ["Skyblock Pro", "Rise from the void!"], cy + 70)
    img.save(f"{path}\\world_icon.png")
    thumb = img.resize((300, 300), Image.LANCZOS)
    thumb.save(f"{path}\\thumbnail.png")

# ---- Parkour Master ----
def gen_parkour(path):
    size = 256
    img = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(img)
    make_icon_bg(draw, size, (255, 140, 0))

    cx, cy = size // 2, size // 2
    colors = [(255, 215, 0), (255, 69, 0), (50, 205, 50), (0, 191, 255), (255, 20, 147)]
    bw, bh = 40, 40
    for i in range(5):
        x = cx - (2 * bw + 10) + i * (bw + 5)
        y = cy + 40 - i * 20
        draw.rounded_rectangle([x - bw // 2, y - bh // 2, x + bw // 2, y + bh // 2],
                               radius=6, fill=colors[i], outline=(255, 255, 255, 180), width=2)

    # arrow path
    for i in range(4):
        x1 = cx - (2 * bw + 10) + i * (bw + 5) + bw // 2
        y1 = cy + 40 - i * 20
        x2 = cx - (2 * bw + 10) + (i + 1) * (bw + 5) - bw // 2
        y2 = cy + 40 - (i + 1) * 20
        draw.line([x1, y1, x2, y2], fill=(255, 255, 255, 150), width=3)
        # arrowhead
        if i < 4:
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            draw.polygon([(mx, my - 5), (mx + 8, my + 3), (mx - 8, my + 3)], fill=(255, 255, 255, 150))

    draw_text(draw, size, ["Parkour Master", "50 levels of mayhem!"], cy - 60)
    img.save(f"{path}\\world_icon.png")
    thumb = img.resize((300, 300), Image.LANCZOS)
    thumb.save(f"{path}\\thumbnail.png")

# ---- OneBlock ----
def gen_oneblock(path):
    size = 256
    img = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(img)
    make_icon_bg(draw, size, (80, 20, 120))

    cx, cy = size // 2, size // 2 - 10
    bs = 90
    # single block with 3D effect
    # top face
    draw.polygon([(cx, cy - bs // 2), (cx + bs // 2, cy - bs // 2 + 15), (cx, cy - bs // 2 + 30), (cx - bs // 2, cy - bs // 2 + 15)],
                 fill=(120, 180, 80))
    # front face
    draw.rectangle([cx - bs // 2, cy - bs // 2 + 15, cx + bs // 2, cy - bs // 2 + 15 + bs - 30], fill=(87, 168, 47))
    # right face
    draw.polygon([(cx + bs // 2, cy - bs // 2 + 15), (cx + bs // 2, cy - bs // 2 + 15 + bs - 30),
                  (cx, cy - bs // 2 + 15 + bs - 30 + 15), (cx, cy - bs // 2 + 30)],
                 fill=(67, 128, 27))
    # grid lines on front
    gs = bs // 3
    for i in range(1, 3):
        x = cx - bs // 2 + i * gs
        draw.line([(x, cy - bs // 2 + 15), (x, cy - bs // 2 + 15 + bs - 30)], fill=(70, 140, 40), width=1)
    for i in range(1, 3):
        y = cy - bs // 2 + 15 + i * gs
        draw.line([(cx - bs // 2, y), (cx + bs // 2, y)], fill=(70, 140, 40), width=1)

    # sparkles
    for sx, sy in [(30, 30), (220, 40), (40, 200), (210, 210)]:
        draw.polygon([(sx, sy - 6), (sx + 2, sy - 2), (sx + 6, sy), (sx + 2, sy + 2), (sx, sy + 6),
                       (sx - 2, sy + 2), (sx - 6, sy), (sx - 2, sy - 2)], fill=(255, 255, 100, 200))

    draw_text(draw, size, ["OneBlock", "One block. Infinite worlds."], cy + 70)
    img.save(f"{path}\\world_icon.png")
    thumb = img.resize((300, 300), Image.LANCZOS)
    thumb.save(f"{path}\\thumbnail.png")

# ---- Medieval Kingdom ----
def gen_medieval(path):
    size = 256
    img = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(img)
    make_icon_bg(draw, size, (34, 80, 34))

    cx, cy = size // 2, size // 2 - 10
    # castle silhouette
    # main keep
    kw, kh = 100, 120
    draw.rectangle([cx - kw // 2, cy + kh // 2 - kh, cx + kw // 2, cy + kh // 2], fill=(112, 66, 20))
    # towers
    tw, th = 30, 60
    for tx in [cx - kw // 2 - tw // 2 + 10, cx + kw // 2 - tw // 2 - 10]:
        draw.rectangle([tx, cy + kh // 2 - kh - th + 30, tx + tw, cy + kh // 2 - kh + th + 30], fill=(112, 66, 20))
        # turret top
        draw.polygon([(tx - 5, cy + kh // 2 - kh - th + 30), (tx + tw // 2, cy + kh // 2 - kh - th - 10),
                       (tx + tw + 5, cy + kh // 2 - kh - th + 30)], fill=(140, 80, 30))

    # battlements
    bw, bh = 12, 15
    for i in range(7):
        bx = cx - kw // 2 + 5 + i * 15
        draw.rectangle([bx, cy - kh // 2 - bh, bx + bw, cy - kh // 2], fill=(130, 76, 25))

    # gate
    draw.arc([cx - 15, cy + kh // 2 - 40, cx + 15, cy + kh // 2], start=0, end=180, fill=(50, 30, 10), width=4)
    draw.rectangle([cx - 15, cy + kh // 2 - 20, cx + 15, cy + kh // 2], fill=(50, 30, 10))

    # flag on main keep
    draw.line([(cx, cy + kh // 2 - kh - 10), (cx, cy + kh // 2 - kh - 40)], fill=(101, 67, 33), width=3)
    draw.polygon([(cx, cy + kh // 2 - kh - 40), (cx + 20, cy + kh // 2 - kh - 32), (cx, cy + kh // 2 - kh - 24)],
                 fill=(200, 50, 50))

    # background hills
    draw.ellipse([10, cy + kh // 2 - 20, 80, cy + kh // 2 + 30], fill=(50, 100, 50))
    draw.ellipse([170, cy + kh // 2 - 10, 250, cy + kh // 2 + 30], fill=(40, 90, 40))

    draw_text(draw, size, ["Medieval Kingdom", "Build. Defend. Conquer."], cy + 50)
    img.save(f"{path}\\world_icon.png")
    thumb = img.resize((300, 300), Image.LANCZOS)
    thumb.save(f"{path}\\thumbnail.png")


if __name__ == "__main__":
    gen_skyblock(os.path.join(BASE, "skyblock-pro"))
    gen_parkour(os.path.join(BASE, "parkour-master"))
    gen_oneblock(os.path.join(BASE, "oneblock"))
    gen_medieval(os.path.join(BASE, "medieval-kingdom"))
    print("All icons generated successfully.")
