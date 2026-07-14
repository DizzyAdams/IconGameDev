"""Generate languages.json with translations for all skin packs."""
import json, os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIN_DIR = BASE / 'skin-packs'

LANGUAGES = ['en_US', 'pt_BR', 'es_ES', 'fr_FR', 'de_DE']

def skin_pack_name_to_key(dir_name):
    return dir_name.replace('-', '_')

def generate_for_pack(pack_dir):
    manifest_path = pack_dir / 'manifest.json'
    skins_json_path = pack_dir / 'skins.json'
    if not manifest_path.exists() or not skins_json_path.exists():
        return None

    with open(manifest_path) as f:
        manifest = json.load(f)
    with open(skins_json_path) as f:
        skins_data = json.load(f)

    header_name = manifest.get('header', {}).get('name', pack_dir.name)
    pack_key = f"skinpack.{skin_pack_name_to_key(pack_dir.name)}"

    lang = {}
    for locale in LANGUAGES:
        lang[locale] = {}
        lang[locale][pack_key] = header_name
        for skin in skins_data.get('skins', []):
            lname = skin.get('localization_name', '')
            if lname:
                lang[locale][f"skin.{pack_key}.{lname}"] = lname.replace('_', ' ').title()

    return lang

def main():
    count = 0
    for pack_dir in sorted(SKIN_DIR.iterdir()):
        if not pack_dir.is_dir():
            continue
        lang = generate_for_pack(pack_dir)
        if lang:
            lang_path = pack_dir / 'languages.json'
            # merge with existing if present
            existing = {}
            if lang_path.exists():
                with open(lang_path) as f:
                    existing = json.load(f)
            for loc in LANGUAGES:
                if loc not in existing:
                    existing[loc] = {}
                existing[loc].update(lang.get(loc, {}))
            with open(lang_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            count += 1
            print(f"  {pack_dir.name}/languages.json")

    print(f"\n{count} skin packs updated with languages.json")
    return count

if __name__ == '__main__':
    main()
