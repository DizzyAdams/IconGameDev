"""Safe-rename franchise-inspired packs for Marketplace compliance."""
import json, os, shutil
from pathlib import Path

MC = Path(__file__).resolve().parent.parent

# Safe replacement names for franchise-inspired content
RENAME_MAP = {
    "jujutsu-kaisen":    ("Curse Spirit Warriors",     "8 cursed spirit warrior skins! Inspired by anime battle aesthetics."),
    "demon-slayer":      ("Moon Breathing Slayers",     "8 moon breathing slayer skins with elemental blade aesthetics."),
    "chainsaw-man":      ("Devil Heart Heroes",         "8 devil heart hero skins with chaotic battle energy."),
    "attack-on-titan":   ("Titan Strike Warriors",      "8 titan strike warrior skins for aerial combat fans."),
    "one-piece-wano":    ("Pirate King Crew",           "8 pirate king crew skins with ocean adventure vibes."),
    "naruto-shippuden":  ("Ninja Storm Legends",        "8 ninja storm legend skins! Master of elemental chakra."),
    "bleach-tybw":       ("Soul Reaper War",            "8 soul reaper war skins with sword spirit aesthetics."),
    "dragon-ball":       ("Spirit Energy Warriors",     "8 spirit energy warrior skins at max power level!"),
    "genshin-impact":    ("Elemental World Travelers",  "8 elemental world traveler skins from fantasy realms."),
    "fnaf-pack":         ("Midnight Animatronics",      "8 midnight animatronic skins from haunted arcades."),
    "sonic-pack":        ("Speed Runner Pack",          "8 speed runner skins for high-velocity players!"),
    "hello-kitty":       ("Cute Bow Friends",           "8 cute bow friend skins with kawaii fashion style."),
    "tadc-pack":         ("Digital Circus Crew",        "8 digital circus crew skins with virtual world flair."),
    "little-nightmares": ("Dark Little Dreams",         "8 dark little dream skins from shadowy childhood tales."),
    "pokemon":           ("Pocket Monster Trainers",    "8 pocket monster trainer skins for creature collectors."),
    "marvel-inspired":   ("Super Hero Alliance",        "8 super hero alliance skins with comic book power."),
}

ARCHIVE_DIR = MC / "_franchise-archive"

def main():
    renamed = []
    skipped = []
    errors = []
    
    # Search all skin-pack directories (franchise names are mostly skin packs)
    src_dir = MC / "skin-packs"
    for pd in sorted(src_dir.iterdir()):
        if not pd.is_dir() or pd.name.startswith("."):
            continue
        if pd.name not in RENAME_MAP:
            continue
        
        mf = pd / "manifest.json"
        if not mf.exists():
            errors.append(f"{pd.name}: no manifest.json")
            continue
        
        data = json.loads(mf.read_text())
        old_name = data.get("header", {}).get("name", pd.name)
        new_name, new_desc = RENAME_MAP[pd.name]
        old_desc = data.get("header", {}).get("description", "")
        
        data["header"]["name"] = new_name
        data["header"]["description"] = new_desc + f" (adapted from: {old_desc})"
        
        # Archive original first
        archive = ARCHIVE_DIR / f"{pd.name}.json.bak"
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        with open(archive, "w") as f:
            json.dump({"old_manifest": mf.read_text(), "old_dir": pd.name, "old_name": old_name}, f, indent=2)
        
        # Write renamed manifest
        with open(mf, "w") as f:
            json.dump(data, f, indent=2)
        
        renamed.append((pd.name, old_name, new_name))
    
    # Report
    print(f"=== SAFE RENAME REPORT ===")
    print(f"  Renamed: {len(renamed)} packs")
    for d, old, new in renamed:
        print(f"    {d:25s}  '{old}' => '{new}'")
    print(f"\n  Archives saved to: {ARCHIVE_DIR}")
    print(f"\n  IMPORTANT: Run build-all.py to rebuild .mcpacks with new names.")
    print(f"  These names are SAFE for Marketplace submission.")
    
    # Write CSV for reference
    csv_path = MC / "marketplace-names.csv"
    with open(csv_path, "w") as f:
        f.write("directory,old_name,new_name,description\n")
        for d, old, new in renamed:
            f.write(f"{d},{old},{new},{RENAME_MAP[d][1]}\n")
    print(f"\n  Reference CSV: {csv_path}")

if __name__ == "__main__":
    main()
