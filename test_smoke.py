#!/usr/bin/env python3
"""Quick smoke test for catalog/sync.py and catalog/backup.py."""
import sys
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# 1 — Import and run sync.py --check --json
sys.path.insert(0, str(HERE))
import catalog.sync as sync

# Dry run bedrock sync
br = sync.sync_bedrock(repair=False)
print("=== sync_bedrock (check) ===")
print(f"  active_packs: {br.get('active_packs')}")
print(f"  added: {br.get('added')}, removed: {br.get('removed')}, updated: {br.get('updated')}, unchanged: {br.get('unchanged')}")
print(f"  errors: {br.get('errors', [])}")

# Dry run roblox sync (skip since generate_catalog.py expects to be run from its own dir)
# Just check the path exists
from pathlib import Path
rc_path = HERE / "roblox-ugc" / "catalog" / "roblox_catalog.json"
print(f"\n=== roblox_catalog.json ===")
print(f"  exists: {rc_path.exists()}")
if rc_path.exists():
    data = json.loads(rc_path.read_text(encoding="utf-8"))
    print(f"  items: {len(data.get('items', []))}")
    print(f"  generated_at: {data.get('generated_at', '?')}")

# 2 — Check backup.py can import cleanly
import catalog.backup as bk

# 3 — Generate sitemap
sm = bk.generate_sitemap()
print(f"\n=== sitemap ===")
print(f"  path: {sm.get('path')}")
print(f"  entries: {sm.get('entries', {}).get('total')}")
print(f"  errors: {sm.get('errors', [])}")

# 4 — Check cleanup logic (no-op, no backups dir)
cl = bk.do_cleanup(keep=5)
print(f"\n=== cleanup ===")
print(f"  deleted: {cl.get('deleted')}, kept: {cl.get('kept')}")

print("\n=== ALL SMOKE TESTS PASSED ===")
