#!/usr/bin/env python3
"""IconMineMods - Generate 30 Roblox UGC shirt+pants item templates (mono-dark cyber/tech)."""

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "items"
OUT.mkdir(parents=True, exist_ok=True)

SIZE = 512

# ── Colour palette: mono-dark premium ──────────────────────────────────────
DARK_BG    = (6, 6, 10)      # near-black
DARK_MID   = (12, 12, 20)    # slightly lifted
DARK_PANEL = (18, 18, 30)    # panel card
ACCENTS = [
    ("#00ffff", "#0088aa"),  # cyan
    ("#ff00ff", "#880088"),  # magenta
    ("#00ff88", "#006644"),  # mint
    ("#ff6600", "#883300"),  # orange
    ("#8888ff", "#444488"),  # periwinkle
    ("#ff4488", "#882244"),  # pink
    ("#44ff88", "#228844"),  # spring
    ("#ffaa00", "#885500"),  # amber
    ("#aa44ff", "#552288"),  # purple
    ("#00ccff", "#006688"),  # sky
    ("#ff3366", "#881133"),  # rose
    ("#33ffcc", "#118866"),  # teal
    ("#ff4444", "#882222"),  # red
    ("#44ff44", "#228822"),  # lime
    ("#4488ff", "#224488"),  # blue
    ("#ff8800", "#884400"),  # gold
    ("#ff66aa", "#883355"),  # coral
    ("#66ffaa", "#338855"),  # emerald
    ("#aa66ff", "#553388"),  # violet
    ("#ff9966", "#884c33"),  # peach
    ("#66ccff", "#336688"),  # ice
    ("#ff5588", "#882a44"),  # berry
    ("#55ff88", "#2a8844"),  # jungle
    ("#cc66ff", "#663388"),  # orchid
    ("#ffbb33", "#885d19"),  # sun
    ("#33ffbb", "#19885d"),  # aqua
    ("#ff3377", "#88193b"),  # cherry
    ("#77ff33", "#3b8819"),  # neon green
    ("#3377ff", "#193b88"),  # royal
    ("#ff7733", "#883b19"),  # rust
]
SEED = 42
random.seed(SEED)


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return tuple(int(ac + (bc - ac) * t) for ac, bc in zip(a, b))


def draw_circuit(draw, x, y, w, h, accent, step=32):
    """Draw a subtle circuit-board trace pattern in a zone."""
    pts: list[tuple[int, int]] = []
    cx = x + random.randint(4, w - 4)
    cy = y + random.randint(4, h - 4)
    pts.append((cx, cy))
    for _ in range(random.randint(3, 6)):
        dx = random.choice([-step, 0, step])
        dy = random.choice([-step, 0, step])
        if dx == 0 and dy == 0:
            continue
        cx = max(x + 2, min(x + w - 2, cx + dx))
        cy = max(y + 2, min(y + h - 2, cy + dy))
        pts.append((cx, cy))
    if len(pts) >= 2:
        for i in range(len(pts) - 1):
            draw.line((*pts[i], *pts[i+1]), fill=accent, width=1)


def draw_hex_grid(draw, x0, y0, w, h, accent, radius=8, spacing=28):
    """Draw a honeycomb/hex pattern zone."""
    r = radius
    dx = r * 1.5
    dy = r * math.sqrt(3)
    cols = int(w / dx) + 1
    rows = int(h / dy) + 2
    for row in range(rows):
        for col in range(cols):
            cx = x0 + col * dx + (0 if row % 2 == 0 else dx * 0.5)
            cy = y0 + row * dy
            if cx - r < x0 or cx + r > x0 + w or cy - r < y0 or cy + r > y0 + h:
                continue
            pts = []
            for i in range(6):
                a = math.radians(60 * i - 30)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            draw.polygon(pts, outline=accent, width=1)


def draw_grid_lines(draw, x0, y0, w, h, accent, step=32):
    """Draw a subtle dot-grid or crosshair pattern."""
    for rx in range(x0, x0 + w, step):
        for ry in range(y0, y0 + h, step):
            draw.point((rx, ry), fill=accent)


def draw_angled_lines(draw, x0, y0, w, h, accent, angle_deg=45, spacing=24):
    """Draw angled parallel lines."""
    rad = math.radians(angle_deg)
    diag = int(math.hypot(w, h)) + spacing
    for d in range(-diag, diag, spacing):
        start = (x0 + d * math.cos(rad), y0 + d * math.sin(rad))
        end = (x0 + d * math.cos(rad) + diag * math.cos(rad + math.pi/2),
               y0 + d * math.sin(rad) + diag * math.sin(rad + math.pi/2))
        draw.line((start[0], start[1], end[0], end[1]), fill=accent, width=1)


def draw_data_row(draw, x0, y0, w, accent, num_bars=8):
    """Draw a row of 'data bars' like a terminal readout."""
    bw = (w - (num_bars - 1) * 2) // num_bars
    for i in range(num_bars):
        bh = random.randint(4, 16)
        bx = x0 + i * (bw + 2)
        draw.rectangle((bx, y0 - bh, bx + bw, y0), fill=accent)


def make_shirt(n: int) -> Image.Image:
    """Generate a single 512×512 Roblox shirt template."""
    img = Image.new("RGBA", (SIZE, SIZE), DARK_BG)
    draw = ImageDraw.Draw(img)

    accent_hi = hex_to_rgb(ACCENTS[n % len(ACCENTS)][0])
    accent_lo = hex_to_rgb(ACCENTS[n % len(ACCENTS)][1])

    # Fill base with a subtle gradient (vertical)
    for y in range(SIZE):
        t = y / SIZE
        col = lerp(DARK_BG, (12, 12, 22), t * 0.5)
        draw.line((0, y, SIZE, y), fill=col)

    # Torso zones for shirt: roughly
    # Front torso: ~256-512 x ~0-256
    # Back torso: ~0-256 x ~0-256
    # Left sleeve front: ~256-512 x ~256-384
    # Right sleeve front: ~256-512 x ~384-512
    # Left sleeve back: ~0-128 x ~256-384
    # Right sleeve back: ~128-256 x ~256-384
    # Lower extensions: ~0-256 x ~384-512

    zones = [
        (256, 0, 512, 256, "front_torso"),
        (0, 0, 256, 256, "back_torso"),
        (256, 256, 384, 384, "ls_front"),
        (384, 256, 512, 384, "rs_front"),
        (0, 256, 128, 384, "ls_back"),
        (128, 256, 256, 384, "rs_back"),
        (0, 384, 128, 512, "lower_l"),
        (128, 384, 256, 512, "lower_r"),
        (256, 384, 384, 512, "lower_lf"),
        (384, 384, 512, 512, "lower_rf"),
    ]

    # Draw panel backgrounds in each zone
    for (x0, y0, x1, y1, _name) in zones:
        draw.rectangle((x0 + 4, y0 + 4, x1 - 4, y1 - 4), fill=DARK_PANEL, outline=accent_lo, width=1)

    # Apply patterned decorations based on item index
    pattern_type = n % 5

    if pattern_type == 0:
        # Circuit traces on front torso
        z = (256, 0, 512, 256)
        for _ in range(random.randint(8, 16)):
            draw_circuit(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_hi, step=24)
        # Hex grid on back
        z = (0, 0, 256, 256)
        draw_hex_grid(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_lo, radius=6, spacing=24)

    elif pattern_type == 1:
        # Angled lines on front torso
        z = (256, 0, 512, 256)
        draw_angled_lines(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_hi, angle_deg=-45, spacing=20)
        # Grid dots on back
        z = (0, 0, 256, 256)
        draw_grid_lines(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_lo, step=24)

    elif pattern_type == 2:
        # Data rows on front + back
        z = (256, 0, 512, 256)
        for row_y in range(z[1] + 20, z[3], 20):
            draw_data_row(draw, z[0] + 10, row_y, z[2]-z[0]-20, accent_hi, num_bars=6)
        # Hex on sleeves
        for z in [(256, 256, 384, 384), (384, 256, 512, 384)]:
            draw_hex_grid(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_lo, radius=5, spacing=20)

    elif pattern_type == 3:
        # Angled lines both ways on front
        z = (256, 0, 512, 256)
        draw_angled_lines(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_hi, angle_deg=45, spacing=24)
        draw_angled_lines(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_lo, angle_deg=-45, spacing=24)
        # Circuit on sleeves
        for z in [(256, 256, 384, 384), (384, 256, 512, 384)]:
            draw_circuit(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_hi, step=16)

    elif pattern_type == 4:
        # Large hex grid across front torso
        z = (256, 0, 512, 256)
        draw_hex_grid(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_hi, radius=12, spacing=40)
        # Circuit on back
        z = (0, 0, 256, 256)
        for _ in range(random.randint(6, 12)):
            draw_circuit(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_lo, step=24)

    # Draw central accent element on front torso (a diamond/chevron)
    cx, cy = 384, 128
    pts = [
        (cx, cy - 30),
        (cx + 20, cy),
        (cx, cy + 30),
        (cx - 20, cy),
    ]
    draw.polygon(pts, outline=accent_hi, width=2)

    # Small accent dots at corners
    for z in zones:
        draw.point((z[0] + 6, z[1] + 6), fill=accent_hi)
        draw.point((z[2] - 6, z[1] + 6), fill=accent_hi)
        draw.point((z[0] + 6, z[3] - 6), fill=accent_hi)
        draw.point((z[2] - 6, z[3] - 6), fill=accent_hi)

    return img


def make_pants(n: int) -> Image.Image:
    """Generate a single 512×512 Roblox pants template."""
    img = Image.new("RGBA", (SIZE, SIZE), DARK_BG)
    draw = ImageDraw.Draw(img)

    accent_hi = hex_to_rgb(ACCENTS[n % len(ACCENTS)][0])
    accent_lo = hex_to_rgb(ACCENTS[n % len(ACCENTS)][1])

    # Vertical gradient
    for y in range(SIZE):
        t = y / SIZE
        col = lerp(DARK_BG, (10, 10, 18), t * 0.4)
        draw.line((0, y, SIZE, y), fill=col)

    # Pants zones: front legs (left), back legs (right)
    # Standard Roblox pants template:
    # Left half (0-256): Left leg
    # Right half (256-512): Right leg
    # Upper part: Waist/hip area
    # Lower part: Leg
    zones = [
        (4, 4, 252, 128, "waist_lf"),
        (260, 4, 508, 128, "waist_rf"),
        (4, 132, 252, 256, "leg_lf_front"),
        (260, 132, 508, 256, "leg_rf_front"),
        (4, 260, 252, 384, "leg_lf_back"),
        (260, 260, 508, 384, "leg_rf_back"),
        (4, 388, 252, 508, "leg_lf_lower"),
        (260, 388, 508, 508, "leg_rf_lower"),
    ]

    for (x0, y0, x1, y1, _name) in zones:
        draw.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), fill=DARK_PANEL, outline=accent_lo, width=1)

    # Apply patterns
    ptype = n % 4

    if ptype == 0:
        # Vertical data lines
        for (x0, y0, x1, y1, _) in zones:
            for rx in range(x0 + 8, x1, 16):
                draw_data_row(draw, rx, y1 - 10, y1 - y0 - 20, accent_hi, num_bars=4)

    elif ptype == 1:
        # Angled lines on each leg
        z = (4, 132, 252, 384)
        draw_angled_lines(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_hi, angle_deg=45, spacing=20)
        z = (260, 132, 508, 384)
        draw_angled_lines(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_lo, angle_deg=-45, spacing=20)

    elif ptype == 2:
        # Circuits on upper, dot grid on lower
        for z in [(4, 4, 252, 128), (260, 4, 508, 128)]:
            draw_circuit(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_hi, step=20)
        for z in [(4, 132, 252, 384), (260, 132, 508, 384)]:
            draw_grid_lines(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_lo, step=20)

    elif ptype == 3:
        # Hex pattern down the legs
        for z in [(4, 132, 252, 384), (260, 132, 508, 384)]:
            draw_hex_grid(draw, z[0], z[1], z[2]-z[0], z[3]-z[1], accent_hi, radius=7, spacing=28)

    # Vertical accent line down each leg
    draw.line((128, 132, 128, 508), fill=accent_hi, width=2)
    draw.line((384, 132, 384, 508), fill=accent_lo, width=2)

    # Waist accent band
    draw.line((4, 66, 252, 66), fill=accent_hi, width=2)
    draw.line((260, 66, 508, 66), fill=accent_hi, width=2)

    return img


def main():
    COUNT = 30
    for n in range(1, COUNT + 1):
        shirt = make_shirt(n)
        shirt_path = OUT / f"shirt-{n}.png"
        shirt.save(shirt_path, "PNG")
        print(f"  wrote {shirt_path.name}  ({n}/{COUNT})")

        pants = make_pants(n)
        pants_path = OUT / f"pants-{n}.png"
        pants.save(pants_path, "PNG")
        print(f"  wrote {pants_path.name}  ({n}/{COUNT})")

    print(f"\nDone — {COUNT} shirts + {COUNT} pants = {COUNT*2} PNGs in {OUT}")
    # Show a quick summary
    names = [
        "Neon Pulse", "Cyber Blaze", "Digital Phantom", "Void Walker", "Synth Surge",
        "Pixel Storm", "Circuit Breaker", "Holo Drift", "Quantum Shift", "Binary Split",
        "Shadow Mesh", "Glitch Core", "Data Stream", "Volt Runner", "Signal Void",
        "Nano Veil", "Transient Flux", "System Crash", "Matrix Fold", "Echo Frame",
        "Cipher Gate", "Warp Field", "Photon Edge", "Dark Relay", "Omega Trace",
        "Rift Signal", "Flux Pulse", "Core Fragment", "Ghost Protocol", "Nexus Point",
    ]
    print("\nItem naming (for catalog):")
    for i, nm in enumerate(names, 1):
        print(f"  {i:2d}. {nm} Shirt + {nm} Pants")


if __name__ == "__main__":
    main()
