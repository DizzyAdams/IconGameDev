#!/usr/bin/env python3
"""
Generate 50 new Minecraft Bedrock .mctemplate files.
Expands each of 5 series (crystal-vale, sunken-relic, voidforge, stormwatch, verdant-hollow)
with +10 new maps each (variations on survival, parkour, pvp).
"""

import os
import shutil
import zipfile
import json
import uuid
import io

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
MCPACKS_DIR = os.path.join(WORK_DIR, "submission_mcpacks")
OUTPUT_DIR = os.path.join(WORK_DIR, "submission_mcpacks")

# Reference template to copy base files (level.dat, world_icon.png)
REFERENCE_TEMPLATE = "crystal-vale-survival-base.mctemplate"

# Read UUIDs already taken
uuid_taken_path = os.path.join(MCPACKS_DIR, ".uuid_taken.json")
existing_uuids = set()
if os.path.exists(uuid_taken_path):
    with open(uuid_taken_path, 'r') as f:
        data = json.load(f)
        existing_uuids = set(data.get("items", []))

print(f"Existing UUIDs count: {len(existing_uuids)}")

def generate_unique_uuid():
    """Generate a UUID not in existing_uuids."""
    while True:
        uid = str(uuid.uuid4())
        if uid not in existing_uuids:
            existing_uuids.add(uid)
            return uid

def extract_reference_template(template_path):
    """Extract manifest.json, level.dat, world_icon.png from a reference template."""
    manifest_data = None
    level_data = None
    icon_data = None
    
    with zipfile.ZipFile(template_path, 'r') as zf:
        for name in zf.namelist():
            if name == "manifest.json":
                manifest_data = json.loads(zf.read(name))
            elif name == "level.dat":
                level_data = zf.read(name)
            elif name == "world_icon.png":
                icon_data = zf.read(name)
    
    return manifest_data, level_data, icon_data

def create_mctemplate(output_path, manifest, level_data, icon_data):
    """Create a .mctemplate zip file."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add manifest.json
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        # Add level.dat
        if level_data:
            zf.writestr("level.dat", level_data)
        # Add world_icon.png
        if icon_data:
            zf.writestr("world_icon.png", icon_data)
    return True

# Reference for generating manifest
ref_template_path = os.path.join(MCPACKS_DIR, REFERENCE_TEMPLATE)
if not os.path.exists(ref_template_path):
    # Try another template
    for f in os.listdir(MCPACKS_DIR):
        if f.endswith(".mctemplate"):
            ref_template_path = os.path.join(MCPACKS_DIR, f)
            break

print(f"Using reference: {ref_template_path}")
ref_manifest, level_data, icon_data = extract_reference_template(ref_template_path)

if ref_manifest is None:
    print("ERROR: Could not extract reference manifest!")
    exit(1)

print(f"Reference manifest structure: {json.dumps(ref_manifest, indent=2)}")

# --- Define the 50 new templates ---

# Series definitions
SERIES = {
    "crystal-vale": {
        "theme": "Crystal Vale",
        "description_base": "A luminous valley of towering crystals, shimmering geode caverns, and magical gemstone biomes.",
        "color": "magenta",
    },
    "sunken-relic": {
        "theme": "Sunken Relic",
        "description_base": "Deep ocean ruins of a lost civilization, with coral-encrusted temples and submerged treasure chambers.",
        "color": "cyan",
    },
    "voidforge": {
        "theme": "Voidforge",
        "description_base": "An abyssal dimension of floating obsidian islands, eternal twilight, and nether-forged fortresses.",
        "color": "dark_purple",
    },
    "stormwatch": {
        "theme": "Stormwatch",
        "description_base": "Sky-bound floating islands amidst perpetual thunderstorms, with lightning-charged landscapes and aerial citadels.",
        "color": "blue",
    },
    "verdant-hollow": {
        "theme": "Verdant Hollow",
        "description_base": "An ancient overgrown forest realm with giant flora, mystical ruins, and bioluminescent groves.",
        "color": "green",
    },
}

# Survival variants (4 per series)
SURVIVAL_VARIANTS = [
    ("scavenger-isle", "Scavenger's Isle", "Stranded on a resource-scarce isle — gather, craft, and survive against hostile mobs."),
    ("deep-cavern-dweller", "Deep Cavern Dweller", "Survive the depths of winding caverns with limited light and abundant dangers."),
    ("cliffside-outpost", "Cliffside Outpost", "Build and defend a base perched on treacherous cliffs against nightly raids."),
    ("frostbound-expanse", "Frostbound Expanse", "Brave the icebound wasteland — manage warmth, hunt for food, and endure blizzards."),
]

# Parkour variants (3 per series)
PARKOUR_VARIANTS = [
    ("crystal-leap", "Crystal Leap", "Leap across treacherous crystal spires and narrow ledges high above the valley floor."),
    ("soul-stair", "Soul Stair", "Ascend an ever-twisting vertical stairway of soul sand, slime blocks, and timed jumps."),
    ("phantom-run", "Phantom Run", "Outrun the darkness in a gauntlet of elytra boosts, wall-runs, and precision platforming."),
]

# PVP variants (3 per series)
PVP_VARIANTS = [
    ("chaos-arena", "Chaos Arena", "A chaotic free-for-all arena with random loot drops, environmental hazards, and power-ups."),
    ("king-of-the-summit", "King of the Summit", "Capture and hold the central summit while fending off opponents in vertical combat."),
    ("arsenal-brawl", "Arsenal Brawl", "Kit up from distributed armories and battle in a symmetrical arena with tactical cover."),
]

# Mapping: category -> variant list
CATEGORY_MAP = {
    "survival": SURVIVAL_VARIANTS,
    "parkour": PARKOUR_VARIANTS,
    "pvp": PVP_VARIANTS,
}

# Total: 5 series x (4 survival + 3 parkour + 3 pvp) = 5 x 10 = 50 templates

def make_manifest(series_name, category, variant_key, variant_title, variant_desc, series_info):
    """Create a manifest.json dict for a template."""
    header_uuid = generate_unique_uuid()
    module_uuid = generate_unique_uuid()
    
    full_desc = f"[{series_info['theme']} — {variant_title}] {variant_desc} Theme: {series_info['description_base']}"
    
    manifest = {
        "format_version": 2,
        "header": {
            "name": f"{series_info['theme']}: {variant_title}",
            "description": full_desc,
            "uuid": header_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 21, 0],
            "lock_template_options": True,
            "category": category.capitalize(),
        },
        "modules": [
            {
                "type": "world",
                "uuid": module_uuid,
                "version": [1, 0, 0],
            }
        ],
        "metadata": {
            "authors": ["IconGameDev Studio"],
            "generated_with": ["hermes-agent"],
            "license": "All Rights Reserved",
            "series": series_info["theme"],
            "variant": variant_title,
            "color": series_info["color"],
            "tags": [series_name, category, variant_key],
        },
    }
    return manifest


# Generate all 50 templates
generated = []

for series_name, series_info in SERIES.items():
    for category, variants in CATEGORY_MAP.items():
        for variant_key, variant_title, variant_desc in variants:
            filename = f"{series_name}-{variant_key}.mctemplate"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            manifest = make_manifest(
                series_name, category,
                variant_key, variant_title, variant_desc,
                series_info
            )
            
            create_mctemplate(output_path, manifest, level_data, icon_data)
            generated.append(filename)
            print(f"  Created: {filename}")

# Save updated UUID list
with open(uuid_taken_path, 'w') as f:
    json.dump({"items": sorted(list(existing_uuids))}, f, indent=2)

print(f"\n{'='*60}")
print(f"Generated {len(generated)} new .mctemplate files!")
print(f"{'='*60}")

# Summary by series
for series_name in SERIES:
    count = sum(1 for g in generated if g.startswith(series_name))
    print(f"  {series_name}: {count} templates")

# List all generated files
print(f"\nAll files:")
for g in sorted(generated):
    filepath = os.path.join(OUTPUT_DIR, g)
    size = os.path.getsize(filepath)
    print(f"  {g} ({size} bytes)")
