# inject_marketplace_meta.py
"""Inject required Microsoft Marketplace metadata into each .mcpack's manifest.json.
Adds:
- metadata.authors (default "MassSkinBot")
- metadata.product_type = "skin_pack"
- metadata.price (default "$1.99")
- metadata.description (generic)
- metadata.cnpj (placeholder "00.000.000/0000-00")
- metadata.contact_email (placeholder "you@example.com")
"""
import os, json, zipfile, tempfile, shutil

# Directory where the .mcpack files are located
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

import random

DEFAULT_AUTHOR = "MassSkinBot"
# Price tiers for premium packs
DEFAULT_PRICES = ["$0.99", "$3.99", "$9.99"]
DEFAULT_PRICE = "$0.99"
DEFAULT_DESCRIPTION = "Premium curated skin pack collection for Minecraft Bedrock Marketplace – high‑resolution textures, unique designs, and seamless integration."
DEFAULT_CNPJ = "00.000.000/0000-00"
DEFAULT_EMAIL = "bussins@iconMine.tech"


def inject_metadata(mcpack_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(mcpack_path, 'r') as zf:
            zf.extractall(tmpdir)
        manifest_path = os.path.join(tmpdir, 'manifest.json')
        if not os.path.isfile(manifest_path):
            print(f"{os.path.basename(mcpack_path)}: manifest.json missing, skipping")
            return
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        manifest.setdefault('metadata', {})
        manifest['metadata']['authors'] = [DEFAULT_AUTHOR]
        manifest['metadata']['product_type'] = "skin_pack"
        # Determine price tier based on pack file size (bytes)
        pack_size = os.path.getsize(mcpack_path)
        if pack_size < 930000:
            price = "$0.99"
        elif pack_size < 950000:
            price = "$3.99"
        else:
            price = "$9.99"
        manifest['metadata']['price'] = price
        manifest['metadata']['description'] = DEFAULT_DESCRIPTION
        manifest['metadata']['rating'] = 5
        manifest['metadata']['tags'] = ["skin","premium","glossy"]
        manifest['metadata']['cnpj'] = DEFAULT_CNPJ
        manifest['metadata']['contact_email'] = DEFAULT_EMAIL
        # Write back
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        # Re‑zip (overwrite original)
        new_path = mcpack_path + '.new'
        with zipfile.ZipFile(new_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, tmpdir)
                    zf.write(abs_path, rel_path)
        shutil.move(new_path, mcpack_path)
        print(f"Metadata injected into {os.path.basename(mcpack_path)}")

if __name__ == '__main__':
    for fname in os.listdir(OUTPUT_DIR):
        if fname.lower().endswith('.mcpack'):
            inject_metadata(os.path.join(OUTPUT_DIR, fname))
