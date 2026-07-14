"""Package generated Behavior Packs into .mcpack files."""
import os
import zipfile

BASE = os.path.join(os.path.dirname(__file__), '..')
SKIN_PACKS_DIR = os.path.join(BASE, 'skin-packs')
BP_DIR = os.path.join(BASE, 'behavior-packs')
OUTPUT_DIR = os.path.join(BASE, 'output')

def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder_path):
            for f in files:
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, folder_path)
                zf.write(abs_path, rel_path)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Package behavior packs
    for addon_name in os.listdir(BP_DIR):
        addon_path = os.path.join(BP_DIR, addon_name)
        if os.path.isdir(addon_path):
            zip_path = os.path.join(OUTPUT_DIR, f"{addon_name}.mcpack")
            zip_folder(addon_path, zip_path)
            print(f"Packaged {addon_name} -> {zip_path}")

    # Package skin packs
    for pack_name in os.listdir(SKIN_PACKS_DIR):
        pack_path = os.path.join(SKIN_PACKS_DIR, pack_name)
        if os.path.isdir(pack_path):
            zip_path = os.path.join(OUTPUT_DIR, f"{pack_name}.mcpack")
            zip_folder(pack_path, zip_path)
            print(f"Packaged {pack_name} -> {zip_path}")


if __name__ == "__main__":
    print("=== Packaging Behavior Packs ===")
    main()
