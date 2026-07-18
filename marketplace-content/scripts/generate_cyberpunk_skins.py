#!/usr/bin/env python3
"""Generate 50 cyberpunk/neon-themed Bedrock skin packs for Marketplace.

Each pack contains 1 original 64x64 skin texture with a mono-dark palette
+ bright neon accents. Output as .mctemplate files (rename to .mcpack for use).

Themes:
  - Neon Cyber (cyan/magenta)
  - Toxic Waste (lime/green)
  - Hologram (cyan/white)
  - Void Walker (purple/black)
  - Ember Punk (orange/red)
  - Arctic Net (blue/white)
  - Shadow Agent (dark grey/cyan)
  - Pink Hacker (pink/magenta)
  - Gold Titan (gold/amber)
  - Plasma Riot (electric blue/purple)

Re-run: safe — skips existing files.
"""

from __future__ import annotations

import io
import json
import uuid
import zipfile
from pathlib import Path

import PIL.Image
import PIL.ImageDraw

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "submission_mcpacks"

# ── 50 cyberpunk skin definitions ──────────────────────────────────────────
# Each entry: (name, mono_dark_base_RGB, neon_accent_RGB, style_variant)
# Style variants affect the pixel-art silhouette and accessories.
# mono_dark_base = the dark base color for the body.
# neon_accent = the bright neon colour for accents (glow lines, visor, trim).

CYBER_SKINS = [
    # ── NEON CYBER (cyan + magenta) ──
    ("Neon Agent",      (10, 12, 20),   (0, 255, 255),   "visor"),       # 1
    ("Cyber Runner",    (12, 10, 24),   (255, 0, 128),   "stripe"),      # 2
    ("Neon Phantom",    (8, 8, 18),     (0, 220, 240),   "visor"),       # 3
    ("Synth Bounty",    (14, 10, 22),   (255, 40, 180),  "stripe"),      # 4
    ("Holo Agent",      (10, 14, 28),   (100, 200, 255), "visor"),       # 5

    # ── TOXIC WASTE (lime + green) ──
    ("Toxic Raider",    (16, 20, 10),   (180, 255, 0),   "visor"),       # 6
    ("Biohazard Drift", (14, 18, 8),    (100, 255, 50),  "stripe"),      # 7
    ("Acid Wraith",     (10, 16, 8),    (200, 255, 80),  "visor"),       # 8
    ("Venom Spitter",   (18, 22, 12),   (80, 220, 0),    "stripe"),      # 9
    ("Toxin Phantom",   (12, 18, 10),   (150, 255, 100), "visor"),       # 10

    # ── HOLOGRAM (cyan + white) ──
    ("Holo Runner",     (8, 10, 20),    (180, 230, 255), "visor"),       # 11
    ("Digital Ghost",   (10, 12, 24),   (140, 210, 255), "stripe"),      # 12
    ("Pixel Shifter",   (6, 10, 22),    (200, 240, 255), "visor"),       # 13
    ("Glitch Walker",   (12, 14, 26),   (160, 200, 255), "stripe"),      # 14
    ("Holo Assassin",   (8, 12, 22),    (220, 250, 255), "visor"),       # 15

    # ── VOID WALKER (purple + magenta) ──
    ("Void Runner",     (12, 8, 22),    (200, 80, 255),  "visor"),       # 16
    ("Shadow Weaver",   (10, 6, 20),    (180, 60, 240),  "stripe"),      # 17
    ("Dark Nexus",      (14, 10, 26),   (220, 100, 255), "visor"),       # 18
    ("Eclipse Agent",   (8, 6, 18),     (160, 40, 220),  "stripe"),      # 19
    ("Twilight Hacker", (16, 10, 24),   (240, 120, 255), "visor"),       # 20

    # ── EMBER PUNK (orange + red) ──
    ("Ember Striker",   (24, 14, 8),    (255, 120, 0),   "visor"),       # 21
    ("Inferno Drift",   (28, 12, 10),   (255, 80, 20),   "stripe"),      # 22
    ("Blaze Phantom",   (22, 10, 6),    (255, 160, 40),  "visor"),       # 23
    ("Cinder Agent",    (26, 16, 12),   (255, 60, 0),    "stripe"),      # 24
    ("Volt Scorch",     (20, 12, 8),    (255, 200, 60),  "visor"),       # 25

    # ── ARCTIC NET (blue + white) ──
    ("Arctic Runner",   (12, 18, 28),   (100, 180, 255), "visor"),       # 26
    ("Frost Drift",     (10, 16, 26),   (60, 160, 240),  "stripe"),      # 27
    ("Glacial Hacker",  (14, 20, 30),   (140, 200, 255), "visor"),       # 28
    ("Ice Phantom",     (8, 14, 24),    (180, 220, 255), "stripe"),      # 29
    ("Snow Net Agent",  (16, 22, 32),   (80, 170, 250),  "visor"),       # 30

    # ── SHADOW AGENT (dark grey + cyan) ──
    ("Shadow Operative",(18, 18, 22),   (0, 255, 200),   "visor"),       # 31
    ("Stealth Runner",  (14, 14, 18),   (0, 230, 180),   "stripe"),      # 32
    ("Umbra Striker",   (20, 20, 26),   (0, 200, 160),   "visor"),       # 33
    ("Darknet Agent",   (16, 16, 20),   (0, 255, 220),   "stripe"),      # 34
    ("Noir Hacker",     (22, 22, 28),   (0, 240, 190),   "visor"),       # 35

    # ── PINK HACKER (pink + magenta) ──
    ("Pink Wraith",     (24, 10, 20),   (255, 80, 200),  "visor"),       # 36
    ("Neon Valkyrie",   (28, 12, 22),   (255, 60, 160),  "stripe"),      # 37
    ("Cyber Bloom",     (22, 8, 18),    (255, 120, 220), "visor"),       # 38
    ("Magenta Striker", (26, 14, 24),   (255, 40, 140),  "stripe"),      # 39
    ("Candy Net Agent", (20, 10, 16),   (255, 160, 240), "visor"),       # 40

    # ── GOLD TITAN (gold + amber) ──
    ("Gold Titan",      (30, 22, 10),   (255, 200, 0),   "visor"),       # 41
    ("Amber Striker",   (28, 20, 8),    (255, 180, 20),  "stripe"),      # 42
    ("Solar Phantom",   (32, 24, 12),   (255, 220, 40),  "visor"),       # 43
    ("Gilded Runner",   (26, 18, 6),    (255, 160, 0),   "stripe"),      # 44
    ("Auric Agent",     (34, 26, 14),   (255, 240, 60),  "visor"),       # 45

    # ── PLASMA RIOT (electric blue + purple) ──
    ("Plasma Striker",  (10, 8, 30),    (60, 120, 255),  "visor"),       # 46
    ("Riot Controller", (14, 10, 34),   (80, 100, 255),  "stripe"),      # 47
    ("Electric Wraith", (8, 6, 28),     (40, 140, 255),  "visor"),       # 48
    ("Bolt Phantom",    (12, 10, 32),   (100, 80, 255),  "stripe"),      # 49
    ("Volt Nexus",      (16, 12, 36),   (20, 160, 255),  "visor"),       # 50
]


def _shade(rgb, f):
    """Scale an RGB tuple by factor f (0..1), clamped to 0-255."""
    return tuple(max(0, min(255, int(c * f))) for c in rgb)


def make_cyber_skin(dark_base, neon_accent, style):
    """Draw a 64×64 cyberpunk humanoid skin.

    The pixel art uses:
      - dark_base as the primary body colour (suit, pants)
      - neon_accent for visor, trim lines, and tech details
      - style controls the accent placement

    Layout (standard Steve skin template, front-facing):
      - 8x8 head at (8, 8)
      - 8x12 body at (20, 20)
      - 4x12 arms at (16, 20) and (28, 20)
      - 4x12 legs at (20, 32) and (24, 32)
    """
    img = PIL.Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = PIL.ImageDraw.Draw(img)

    base = dark_base + (255,)
    dark = _shade(dark_base, 0.7) + (255,)
    darker = _shade(dark_base, 0.5) + (255,)
    neon = neon_accent + (255,)
    neon_dim = _shade(neon_accent, 0.6) + (255,)
    black = (5, 5, 8, 255)

    # ── HEAD (8,8) to (15,15) ──
    d.rectangle([8, 8, 15, 15], fill=base, outline=dark)

    if style == "visor":
        # Full visor across eyes
        d.rectangle([9, 11, 14, 12], fill=neon)
        d.rectangle([10, 10, 13, 10], fill=dark)
        # Small mouth slit
        d.rectangle([11, 14, 12, 14], fill=dark)
        # Headset ear pieces
        d.rectangle([7, 11, 7, 13], fill=neon_dim)
        d.rectangle([16, 11, 16, 13], fill=neon_dim)
        # Antenna
        d.rectangle([11, 6, 12, 7], fill=neon)
    elif style == "stripe":
        # Horizontal stripe across eyes + glowing eyes
        d.rectangle([9, 11, 14, 11], fill=neon)
        d.rectangle([10, 12, 11, 12], fill=neon_dim)
        d.rectangle([12, 12, 13, 12], fill=neon_dim)
        # Cyber crown
        d.rectangle([10, 6, 13, 7], fill=neon)

    # ── BODY (20,20) to (27,31) ──
    d.rectangle([20, 20, 27, 31], fill=base, outline=dark)

    # Center chest emblem
    d.rectangle([23, 23, 24, 24], fill=neon)

    if style == "stripe":
        # Vertical cyber lines on body
        d.rectangle([21, 22, 21, 29], fill=neon_dim)
        d.rectangle([26, 22, 26, 29], fill=neon_dim)
        # Belt
        d.rectangle([20, 29, 27, 30], fill=darker)
        d.rectangle([22, 29, 25, 30], fill=neon)

    # ── ARMS (16,20)-(19,31) and (28,20)-(31,31) ──
    d.rectangle([16, 20, 19, 31], fill=dark)
    d.rectangle([28, 20, 31, 31], fill=dark)

    # Shoulder pads
    d.rectangle([16, 20, 19, 22], fill=darker, outline=neon_dim)
    d.rectangle([28, 20, 31, 22], fill=darker, outline=neon_dim)

    # Glow trim on arms
    if style == "stripe":
        d.rectangle([17, 24, 17, 29], fill=neon_dim)
        d.rectangle([29, 24, 29, 29], fill=neon_dim)
    else:
        d.rectangle([16, 26, 19, 26], fill=neon_dim)
        d.rectangle([28, 26, 31, 26], fill=neon_dim)

    # ── LEGS (20,32)-(23,43) and (24,32)-(27,43) ──
    d.rectangle([20, 32, 23, 43], fill=base)
    d.rectangle([24, 32, 27, 43], fill=darker)

    # Knee pads / boots
    d.rectangle([20, 40, 23, 43], fill=darker, outline=neon_dim)
    d.rectangle([24, 40, 27, 43], fill=darker, outline=neon_dim)

    # Leg neon accents
    if style == "stripe":
        d.rectangle([22, 34, 22, 39], fill=neon_dim)
        d.rectangle([25, 34, 25, 39], fill=neon_dim)
    else:
        d.rectangle([20, 36, 23, 36], fill=neon_dim)
        d.rectangle([24, 36, 27, 36], fill=neon_dim)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def make_skins_json(skin_name):
    """Generate skins.json for a single-skin pack."""
    return {
        "geometry": "geometry.humanoid.custom",
        "skins": [
            {
                "localization_name": skin_name,
                "geometry": "geometry.humanoid.custom",
                "texture": skin_name + ".png",
                "type": "free",
            }
        ],
    }


def make_manifest(pack_name, skin_name, desc, hu, mu):
    """Generate a v4 skin_pack manifest."""
    return {
        "format_version": 1,
        "header": {
            "name": pack_name,
            "description": desc,
            "uuid": hu,
            "version": [1, 0, 0],
        },
        "modules": [
            {"type": "skin_pack", "uuid": mu, "version": [1, 0, 0]}
        ],
        "metadata": {
            "product_type": "skin_pack",
            "price": "$2.99 (440 MC)",
            "price_usd": 2.99,
            "price_mc": 440,
            "authors": ["IconMineMods"],
        },
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    made = skipped = 0

    for idx, (name, dark_base, neon_accent, style) in enumerate(CYBER_SKINS, start=1):
        fname = f"neon-skins-{idx}.mctemplate"
        p = OUT / fname
        if p.exists():
            skipped += 1
            continue

        pack_name = f"Neon Pack {idx}: {name}"
        desc = (
            f"Original IconMineMods cyberpunk skin. {name} features a "
            f"mono-dark exosuit with #{neon_accent[0]:02x}{neon_accent[1]:02x}{neon_accent[2]:02x} "
            f"neon accents. Part of the Neon Cyber collection for Minecraft Bedrock Marketplace."
        )

        png_data = make_cyber_skin(dark_base, neon_accent, style)
        hu = str(uuid.uuid4())
        mu = str(uuid.uuid4())

        data = {
            "manifest.json": json.dumps(
                make_manifest(pack_name, name, desc, hu, mu), indent=2
            ).encode(),
            "skins.json": json.dumps(
                make_skins_json(name), indent=2
            ).encode(),
            name + ".png": png_data,
        }

        with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as zf:
            for k, v in data.items():
                zf.writestr(k, v)

        made += 1
        print(f"  [{made}] {fname} -> {name} "
              f"(#{dark_base[0]:02x}{dark_base[1]:02x}{dark_base[2]:02x} + "
              f"#{neon_accent[0]:02x}{neon_accent[1]:02x}{neon_accent[2]:02x}, {style})")

    print(f"\nDone: generated {made} cyberpunk skin packs into {OUT} (skipped {skipped})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
