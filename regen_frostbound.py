#!/usr/bin/env python3
"""Regenerate the 5 frostbound-expanse .mctemplate files with IP-safe descriptions.

One-off repair: the originals were quarantined because the description contained
"frozen" (Disney IP term blocked by audit_compliance IP scan). Reuses the same
manifest shape as generate_50_templates.py and a reference template's
level.dat / world_icon.png.
"""
import io
import json
import os
import uuid
import zipfile

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
MCPACKS_DIR = os.path.join(WORK_DIR, "submission_mcpacks")

SERIES = {
    "crystal-vale": ("Crystal Vale", "A luminous valley of towering crystals, shimmering geode caverns, and magical gemstone biomes.", "magenta"),
    "sunken-relic": ("Sunken Relic", "Deep ocean ruins of a lost civilization, with coral-encrusted temples and submerged treasure chambers.", "cyan"),
    "voidforge": ("Voidforge", "An abyssal dimension of floating obsidian islands, eternal twilight, and nether-forged fortresses.", "dark_purple"),
    "stormwatch": ("Stormwatch", "Sky-bound floating islands amidst perpetual thunderstorms, with lightning-charged landscapes and aerial citadels.", "blue"),
    "verdant-hollow": ("Verdant Hollow", "An ancient overgrown forest realm with giant flora, mystical ruins, and bioluminescent groves.", "green"),
}

VARIANT_KEY = "frostbound-expanse"
VARIANT_TITLE = "Frostbound Expanse"
VARIANT_DESC = "Brave the icebound wasteland — manage warmth, hunt for food, and endure blizzards."
CATEGORY = "survival"

uuid_taken_path = os.path.join(MCPACKS_DIR, ".uuid_taken.json")
existing_uuids = set()
if os.path.exists(uuid_taken_path):
    with open(uuid_taken_path) as f:
        existing_uuids = set(json.load(f).get("items", []))


def gen_uuid():
    while True:
        u = str(uuid.uuid4())
        if u not in existing_uuids:
            existing_uuids.add(u)
            return u


# Reference level.dat / world_icon.png from any existing mctemplate.
level_data = icon_data = None
for f in sorted(os.listdir(MCPACKS_DIR)):
    if f.endswith(".mctemplate"):
        with zipfile.ZipFile(os.path.join(MCPACKS_DIR, f)) as zf:
            names = zf.namelist()
            if "level.dat" in names:
                level_data = zf.read("level.dat")
            if "world_icon.png" in names:
                icon_data = zf.read("world_icon.png")
        break

assert level_data, "no reference level.dat found"
assert icon_data and icon_data[:8] == b"\x89PNG\r\n\x1a\n", "no valid reference world_icon.png"
# Verify icon is 256x256 (PNG IHDR width/height at bytes 16..24).
w, h = int.from_bytes(icon_data[16:20], "big"), int.from_bytes(icon_data[20:24], "big")
print(f"reference icon: {w}x{h}")
assert (w, h) == (256, 256), f"world_icon must be 256x256, got {w}x{h}"

generated = []
for series_name, (theme, desc_base, color) in SERIES.items():
    manifest = {
        "format_version": 2,
        "header": {
            "name": f"{theme}: {VARIANT_TITLE}",
            "description": f"[{theme} — {VARIANT_TITLE}] {VARIANT_DESC} Theme: {desc_base}",
            "uuid": gen_uuid(),
            "version": [1, 0, 0],
            "min_engine_version": [1, 21, 0],
            "lock_template_options": True,
            "category": CATEGORY.capitalize(),
        },
        "modules": [{"type": "world", "uuid": gen_uuid(), "version": [1, 0, 0]}],
        "metadata": {
            "authors": ["IconGameDev Studio"],
            "generated_with": ["hermes-agent"],
            "license": "All Rights Reserved",
            "series": theme,
            "variant": VARIANT_TITLE,
            "color": color,
            "tags": [series_name, CATEGORY, VARIANT_KEY],
        },
    }
    out = os.path.join(MCPACKS_DIR, f"{series_name}-{VARIANT_KEY}.mctemplate")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("level.dat", level_data)
        zf.writestr("world_icon.png", icon_data)
    generated.append(os.path.basename(out))
    print(f"  Created: {out}")

with open(uuid_taken_path, "w") as f:
    json.dump({"items": sorted(existing_uuids)}, f, indent=2)

# Self-check: no blocked IP substrings anywhere in the new files.
BLOCKED = ["frozen", "pokemon", "naruto", "marvel", "disney", "spongebob"]
for g in generated:
    raw = open(os.path.join(MCPACKS_DIR, g), "rb").read().lower()
    for b in BLOCKED:
        assert b.encode() not in raw, f"IP term {b!r} still present in {g}"
print(f"\nOK: {len(generated)} frostbound templates regenerated, IP self-check clean.")
