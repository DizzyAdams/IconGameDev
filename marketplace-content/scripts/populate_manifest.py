# populate_manifest.py
"""Populate submission_manifest.json with info for each .mcpack.
Adds entries:
- name (filename without .mcpack)
- size_bytes
- sha256 checksum
"""
import os, json, hashlib

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(BASE, 'output')
MANIFEST_PATH = os.path.join(OUTPUT_DIR, 'submission_manifest.json')

def file_checksum(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    packs = []
    for fname in os.listdir(OUTPUT_DIR):
        if not fname.lower().endswith('.mcpack'):
            continue
        full_path = os.path.join(OUTPUT_DIR, fname)
        packs.append({
            'name': fname[:-7],
            'size_bytes': os.path.getsize(full_path),
            'sha256': file_checksum(full_path)
        })
    manifest['total_packs'] = len(packs)
    manifest['packs'] = packs
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Updated manifest with {len(packs)} packs")

if __name__ == '__main__':
    main()
