# Compliance Audit Script — run before Partner Center submission

import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from pathlib import Path
from validators.bedrock_validator import BedrockValidator

ROOT = Path(__file__).resolve().parent.parent
UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

# Known franchise names that trigger IP rejection
IP_BLOCKED = [
    'pokemon', 'naruto', 'dragon.ball', 'bleach', 'genshin', 'fnaf', 'hello.kitty',
    'demon.slayer', 'chainsaw.man', 'one.piece', 'jujutsu', 'sonic', 'tadc',
    'attack.on.titan', 'little.nightmares',
    # Anime / manga franchise signals (the blind spot that let IP through).
    # Word-boundary patterns avoid false hits inside unrelated words.
    r'\banime\b', r'\bmanga\b', r'\bshonen\b', r'\bshounen\b',
    r'\botaku\b', r'\bwaifu\b', r'\bkawaii\b', r'\bsenpai\b',
]

def audit_packs(pack_dir='dist'):
    """Three-pass audit: structural, UUID format, IP scan."""
    pack_dir = ROOT / pack_dir
    mcpacks = sorted([f for f in os.listdir(str(pack_dir)) if f.endswith(('.mcpack', '.mctemplate', '.mcworld'))])
    
    print(f"=== COMPLIANCE AUDIT: {pack_dir} ===\n")
    print(f"Total packs: {len(mcpacks)}\n")
    
    # Pass 1: Structural (BedrockValidator)
    validator = BedrockValidator()
    results = validator.validate_all(str(pack_dir))
    structural_fail = [r for r in results if not r['valid']]
    structural_pass = len(results) - len(structural_fail)
    
    print(f"--- Pass 1: Structural ---")
    print(f"PASS={structural_pass} FAIL={len(structural_fail)}")
    
    # Pass 2: UUID format
    uuid_bad = []
    for f in mcpacks:
        path = pack_dir / f
        with zipfile.ZipFile(path, 'r') as zf:
            if 'manifest.json' in zf.namelist():
                m = json.loads(zf.read('manifest.json'))
                header = m.get('header', {})
                header_uuid = header.get('uuid', '')
                if not UUID_RE.match(str(header_uuid)):
                    uuid_bad.append((f, f"header: {header_uuid}"))
                for mod in m.get('modules', []):
                    mod_uuid = mod.get('uuid', '')
                    if not UUID_RE.match(str(mod_uuid)):
                        uuid_bad.append((f, f"module: {mod_uuid}"))
    
    uuid_good = len(mcpacks) - len(set(name for name, _ in uuid_bad))
    print(f"\n--- Pass 2: UUID Format ---")
    print(f"PASS={uuid_good} FAIL={len(set(name for name, _ in uuid_bad))}")
    
    # Pass 3: IP scan (filename + manifest header.description/store_description)
    ip_bad = []
    for f in mcpacks:
        name_lower = f.lower().replace('_', '-').replace('.mcpack', '')
        haystack = name_lower
        try:
            with zipfile.ZipFile(pack_dir / f, 'r') as zf:
                if 'manifest.json' in zf.namelist():
                    try:
                        m = json.loads(zf.read('manifest.json'))
                    except Exception:
                        m = {}
                    if isinstance(m, dict):
                        h = m.get('header', {})
                        if isinstance(h, dict):
                            haystack += ' ' + str(h.get('description', '')).lower()
                        haystack += ' ' + str(m.get('store_description', '')).lower()
        except Exception:
            pass
        for pattern in IP_BLOCKED:
            if re.search(pattern, haystack):
                ip_bad.append(f)
                break
    
    ip_good = len(mcpacks) - len(ip_bad)
    print(f"\n--- Pass 3: IP Scan ---")
    print(f"PASS={ip_good} FAIL={len(ip_bad)}")
    
    # Summary
    total_issues = len(structural_fail) + len(set(name for name, _ in uuid_bad)) + len(ip_bad)
    if total_issues == 0:
        print(f"\n=== VERDICT: CLEAN — {len(mcpacks)} packs ready for Partner Center ===")
    else:
        print(f"\n=== VERDICT: {total_issues} issues across {len(mcpacks)} packs ===")
        if structural_fail:
            print(f"\nStructural failures (sample):")
            for r in structural_fail[:5]:
                print(f"  {r['file']}: {r['errors']}")
        if uuid_bad:
            print(f"\nUUID format issues (sample):")
            for name, issue in uuid_bad[:5]:
                print(f"  {name}: {issue}")
        if ip_bad:
            print(f"\nIP violations:")
            for name in ip_bad:
                print(f"  {name}")

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--pack-dir', default='dist')
    args = p.parse_args()
    audit_packs(args.pack_dir)
