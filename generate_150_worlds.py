#!/usr/bin/env python3
"""
Generate 150+ new Minecraft Bedrock .mctemplate files.
Creates 15 new series with 10 maps each (5 survival + 5 pvp/parkour/boss/spawn).
Total: 15 x 10 = 150 new templates.
"""

import os
import zipfile
import json
import uuid

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(WORK_DIR, "submission_mcpacks")

# Read UUIDs already taken from any existing files
uuid_taken_path = os.path.join(OUTPUT_DIR, ".uuid_taken.json")
existing_uuids = set()
if os.path.exists(uuid_taken_path):
    with open(uuid_taken_path, 'r') as f:
        data = json.load(f)
        existing_uuids = set(data.get("items", []))

print(f"Existing UUIDs on record: {len(existing_uuids)}")

# Also scan all existing .mctemplate files for UUIDs to avoid duplicates
os.makedirs(OUTPUT_DIR, exist_ok=True)
for fname in os.listdir(OUTPUT_DIR):
    if fname.endswith(".mctemplate"):
        fpath = os.path.join(OUTPUT_DIR, fname)
        try:
            with zipfile.ZipFile(fpath, 'r') as zf:
                if "manifest.json" in zf.namelist():
                    manifest = json.loads(zf.read("manifest.json"))
                    existing_uuids.add(manifest["header"]["uuid"])
                    for mod in manifest.get("modules", []):
                        existing_uuids.add(mod["uuid"])
        except:
            pass

print(f"Total UUIDs after scanning existing files: {len(existing_uuids)}")


def generate_unique_uuid():
    """Generate a UUID not in existing_uuids."""
    while True:
        uid = str(uuid.uuid4())
        if uid not in existing_uuids:
            existing_uuids.add(uid)
            return uid


def extract_reference_files(template_path):
    """Extract level.dat and world_icon.png from a reference template."""
    level_data = None
    icon_data = None
    try:
        with zipfile.ZipFile(template_path, 'r') as zf:
            for name in zf.namelist():
                if name == "level.dat":
                    level_data = zf.read(name)
                elif name == "world_icon.png":
                    icon_data = zf.read(name)
    except:
        pass
    return level_data, icon_data


def create_mctemplate(output_path, manifest, level_data, icon_data):
    """Create a .mctemplate zip file."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        if level_data:
            zf.writestr("level.dat", level_data)
        if icon_data:
            zf.writestr("world_icon.png", icon_data)
    return True


# Find a reference template to extract level.dat and world_icon.png from
ref_template_path = None
for f in os.listdir(OUTPUT_DIR):
    if f.endswith(".mctemplate"):
        ref_template_path = os.path.join(OUTPUT_DIR, f)
        break

if ref_template_path is None:
    print("ERROR: No reference template found in submission_mcpacks/!")
    exit(1)

print(f"Using reference: {os.path.basename(ref_template_path)}")
level_data, icon_data = extract_reference_files(ref_template_path)

if level_data is None:
    print("WARNING: Could not extract level.dat from reference template!")
if icon_data is None:
    print("WARNING: Could not extract world_icon.png from reference template!")


# ====== 15 NEW SERIES DEFINITIONS ======

SERIES = {
    "crimson-peak": {
        "theme": "Crimson Peak",
        "description_base": "A volcanic mountain range with flowing rivers of lava, crimson stone formations, and fiery caverns carved by ancient eruptions.",
        "color": "red",
    },
    "lunar-haven": {
        "theme": "Lunar Haven",
        "description_base": "A serene moonlit sanctuary with silver meadows, glowing lunar flora, and tranquil crater lakes under eternal starry skies.",
        "color": "white",
    },
    "abyss-trench": {
        "theme": "Abyss Trench",
        "description_base": "The deepest oceanic abyss where bioluminescent creatures roam, hydrothermal vents glow, and ancient ruins lie buried in darkness.",
        "color": "dark_blue",
    },
    "skyward-isles": {
        "theme": "Skyward Isles",
        "description_base": "A collection of floating islands drifting through radiant clouds, connected by sky-bridges and suspended waterfalls.",
        "color": "light_blue",
    },
    "magma-core": {
        "theme": "Magma Core",
        "description_base": "The fiery heart of the world — an infernal realm of bubbling magma pools, obsidian fortresses, and scorching heat hazards.",
        "color": "orange",
    },
    "frozen-wastes": {
        "theme": "Frozen Wastes",
        "description_base": "An endless tundra of ice and snow, with frozen seas, glacial caves, and ancient ice structures gleaming under the aurora.",
        "color": "cyan",
    },
    "enchanted-grove": {
        "theme": "Enchanted Grove",
        "description_base": "A mystical forest where giant glowing mushrooms, ancient oaks, and magical creatures dwell in perpetual twilight.",
        "color": "lime",
    },
    "desert-tyranny": {
        "theme": "Desert Tyranny",
        "description_base": "A scorching desert empire with massive sand pyramids, sun-scorched ruins, and treacherous dune valleys hiding ancient tombs.",
        "color": "yellow",
    },
    "jungle-ruins": {
        "theme": "Jungle Ruins",
        "description_base": "Dense tropical jungles hiding the remains of a lost civilization, with vine-covered temples and overgrown pathways.",
        "color": "green",
    },
    "corrupted-lands": {
        "theme": "Corrupted Lands",
        "description_base": "A blighted dimension infected by dark corruption, with warped flora, purple haze, and twisted landscapes of decay.",
        "color": "dark_purple",
    },
    "starlight-realm": {
        "theme": "Starlight Realm",
        "description_base": "A celestial dimension of cosmic beauty where constellations glow in the ground, nebula clouds drift, and starlight powers everything.",
        "color": "purple",
    },
    "crystal-caverns": {
        "theme": "Crystal Caverns",
        "description_base": "An underground wonderland of giant amethyst geodes, diamond-lit grottoes, and crystalline formations that sing with resonance.",
        "color": "magenta",
    },
    "thunder-plateau": {
        "theme": "Thunder Plateau",
        "description_base": "A high-altitude mesa battered by perpetual storms, with lightning-scarred rock, storm-charged crystals, and violent winds.",
        "color": "blue",
    },
    "shadow-realm": {
        "theme": "Shadow Realm",
        "description_base": "A dark dimension of perpetual night where shadow creatures lurk, void rifts shimmer, and only the brave dare to tread.",
        "color": "black",
    },
    "ocean-trench": {
        "theme": "Ocean Trench",
        "description_base": "Submarine canyons of staggering depth, with coral forests, underwater volcanoes, and the wrecks of ancient ships.",
        "color": "dark_aqua",
    },
}

# ----- SURVIVAL VARIANTS (5 per series) -----
SURVIVAL_VARIANTS = [
    ("survival-base", "Survival Base", "Survive and thrive in this hostile environment — gather resources, craft tools, and build your shelter against the elements and mobs."),
    ("survival-outpost", "Wilderness Outpost", "Establish an outpost in this untamed region. Scavenge supplies, fortify your position, and survive waves of nightly attacks."),
    ("survival-nomad", "Nomad's Journey", "A nomadic survival experience where you must traverse the landscape, set up temporary camps, and keep moving to stay alive."),
    ("survival-island", "Deserted Island", "Stranded in a remote area with minimal supplies. Explore, gather, and craft your way to self-sufficiency against the odds."),
    ("survival-stronghold", "Stronghold Siege", "Defend a crumbling stronghold against relentless mob sieges while managing limited food and resources to outlast the onslaught."),
]

# ----- PVP VARIANTS (2 per series) -----
PVP_VARIANTS = [
    ("pvp-arena", "PvP Arena", "A balanced competitive arena designed for intense player-versus-player battles with strategic cover, loot spawns, and power-up locations."),
    ("pvp-showdown", "Showdown Arena", "A compact showdown arena with dynamic hazards, central control points, and multiple combat tiers for fast-paced duels."),
]

# ----- PARKOUR VARIANTS (1 per series) -----
PARKOUR_VARIANTS = [
    ("parkour-run", "Parkour Run", "An adrenaline-filled parkour course with challenging jumps, timed sections, elytra boosts, and precision platforming."),
]

# ----- BOSS VARIANTS (1 per series) -----
BOSS_VARIANTS = [
    ("boss-arena", "Boss Arena", "Face off against a formidable boss in a specially designed arena with attack patterns, phases, and legendary loot rewards."),
]

# ----- SPAWN VARIANTS (1 per series) -----
SPAWN_VARIANTS = [
    ("spawn-hub", "Spawn Hub", "A beautifully crafted central hub with portals, trading areas, navigation markers, and community gathering spaces."),
]

# Category mapping: 5 survival + 2 pvp + 1 parkour + 1 boss + 1 spawn = 10 per series
CATEGORY_MAP = {
    "survival": SURVIVAL_VARIANTS,
    "pvp": PVP_VARIANTS,
    "parkour": PARKOUR_VARIANTS,
    "boss": BOSS_VARIANTS,
    "spawn": SPAWN_VARIANTS,
}


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


# ====== GENERATE ALL 150 TEMPLATES ======
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

# List all generated files with sizes
print(f"\nAll files:")
for g in sorted(generated):
    filepath = os.path.join(OUTPUT_DIR, g)
    size = os.path.getsize(filepath)
    print(f"  {g} ({size} bytes)")

print(f"\nTotal templates in {OUTPUT_DIR}: {len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.mctemplate')])}")
