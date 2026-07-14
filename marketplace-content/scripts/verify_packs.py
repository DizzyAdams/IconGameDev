# verify_packs.py
"""Validate all generated .mcpack files for required Marketplace metadata.
Checks performed for each .mcpack:
- manifest.json exists
- metadata fields: authors, product_type, price, description, cnpj, contact_email
- price is "$0.99"
- contact_email is "bussins@iconMine.tech"
Any missing/incorrect entries are reported.
"""
import os, json, zipfile, tempfile, sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(BASE, 'output')

REQUIRED_FIELDS = {
    'authors': lambda v: isinstance(v, list) and len(v) > 0,
    'product_type': lambda v: v == 'skin_pack' or v == 'behavior_pack',
    'price': lambda v: v in ['$0.99', '$3.99', '$9.99'],
    'description': lambda v: isinstance(v, str) and len(v) > 0,
    'cnpj': lambda v: isinstance(v, str) and len(v) > 0,
    'contact_email': lambda v: v == 'bussins@iconMine.tech',
}

issues = []

for fname in os.listdir(OUTPUT_DIR):
    if not fname.lower().endswith('.mcpack'):
        continue
    pack_path = os.path.join(OUTPUT_DIR, fname)
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(pack_path, 'r') as zf:
            try:
                zf.extractall(tmpdir)
            except Exception as e:
                issues.append(f"{fname}: extraction error {e}")
                continue
        manifest_path = os.path.join(tmpdir, 'manifest.json')
        if not os.path.isfile(manifest_path):
            issues.append(f"{fname}: manifest.json missing")
            continue
        with open(manifest_path, 'r', encoding='utf-8') as f:
            try:
                manifest = json.load(f)
            except Exception as e:
                issues.append(f"{fname}: manifest.json invalid JSON {e}")
                continue
        metadata = manifest.get('metadata', {})
        for field, validator in REQUIRED_FIELDS.items():
            if field not in metadata:
                issues.append(f"{fname}: missing metadata field '{field}'")
            else:
                if not validator(metadata[field]):
                    issues.append(f"{fname}: invalid value for '{field}' (found '{metadata[field]}')")

if issues:
    print('Validation completed: issues found')
    for line in issues:
        print('- ' + line)
    sys.exit(1)
else:
    print('All packs passed validation – required metadata present and correct.')
    sys.exit(0)
