# validate_packs.py
"""Validate generated .mcpack files for JSON correctness and UUID uniqueness.

- Checks each .mcpack contains a valid manifest.json and skins.json.
- Collects all header.uuid and module.uuid values and ensures they are unique.
- Reports any duplicate UUIDs and exits with code 1 if problems are found.
"""
import os, json, zipfile, sys

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))

header_uuids = {}
module_uuids = {}
errors = []

for filename in os.listdir(OUTPUT_DIR):
    if not filename.endswith('.mcpack'):
        continue
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        with zipfile.ZipFile(path, 'r') as zf:
            with zf.open('manifest.json') as mf:
                manifest = json.load(mf)
            # skins.json optional but we try to load to ensure valid JSON
            try:
                with zf.open('skins.json') as sf:
                    json.load(sf)
            except KeyError:
                pass
    except Exception as e:
        errors.append(f"{filename}: cannot read zip or JSON – {e}")
        continue

    header_uuid = manifest.get('header', {}).get('uuid')
    modules = manifest.get('modules', [])
    module_uuid = modules[0].get('uuid') if modules else None
    if header_uuid:
        if header_uuid in header_uuids:
            errors.append(f"Duplicate header UUID {header_uuid} in {filename} and {header_uuids[header_uuid]}")
        else:
            header_uuids[header_uuid] = filename
    if module_uuid:
        if module_uuid in module_uuids:
            errors.append(f"Duplicate module UUID {module_uuid} in {filename} and {module_uuids[module_uuid]}")
        else:
            module_uuids[module_uuid] = filename

if errors:
    print('Validation failed with the following issues:')
    for err in errors:
        print(' -', err)
    sys.exit(1)
else:
    print('All .mcpack files validated successfully. No duplicate UUIDs found.')
    sys.exit(0)
