#!/usr/bin/env python3
"""Run all three map/mashup generation scripts and report results."""
import subprocess
import sys
import os
import time

SCRIPTS = [
    ("Fortnite Creative Maps (40)", "epic/maps/generate_40_maps.py"),
    ("Feature Map World Templates (50)", "marketplace-content/scripts/generate_feature_maps.py"),
    ("Mashup Packs (3)", "marketplace-content/scripts/generate-mashups.py"),
]

ROOT = os.path.dirname(os.path.abspath(__file__))
results = []

for label, rel_path in SCRIPTS:
    script_path = os.path.join(ROOT, rel_path)
    print(f"\n{'='*70}")
    print(f"RUNNING: {label}")
    print(f"  Script: {rel_path}")
    print(f"{'='*70}")
    start = time.time()
    try:
        cp = subprocess.run(
            [sys.executable, script_path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=600,
        )
        elapsed = time.time() - start
        stdout = cp.stdout.strip()
        stderr = cp.stderr.strip()
        ok = cp.returncode == 0
        results.append({
            "label": label,
            "script": rel_path,
            "ok": ok,
            "returncode": cp.returncode,
            "elapsed": elapsed,
            "stdout": stdout,
            "stderr": stderr,
        })
        if ok:
            print(f"  ✓ Success ({elapsed:.1f}s)")
            if stdout:
                for line in stdout.splitlines():
                    print(f"  | {line}")
        else:
            print(f"  ✗ FAILED (exit {cp.returncode}, {elapsed:.1f}s)")
            if stdout:
                print(f"  stdout: {stdout[:500]}")
            if stderr:
                print(f"  stderr: {stderr[:500]}")
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"  ✗ TIMEOUT after {elapsed:.1f}s")
        results.append({
            "label": label,
            "script": rel_path,
            "ok": False,
            "returncode": -1,
            "elapsed": elapsed,
            "stdout": "",
            "stderr": "TIMEOUT",
        })
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ✗ ERROR: {e}")
        results.append({
            "label": label,
            "script": rel_path,
            "ok": False,
            "returncode": -2,
            "elapsed": elapsed,
            "stdout": "",
            "stderr": str(e),
        })

# Generate report
print("\n\n" + "="*70)
print("FINAL REPORT")
print("="*70)
for r in results:
    status = "✓" if r["ok"] else "✗"
    print(f"\n  {status} {r['label']}")
    print(f"     Script: {r['script']}")
    print(f"     Time:   {r['elapsed']:.1f}s")
    print(f"     Exit:   {r['returncode']}")
    if r["stdout"]:
        print(f"     Output: {r['stdout'][:300]}")
    if r["stderr"]:
        print(f"     Errors: {r['stderr'][:300]}")

# Check output files
print("\n\n--- Output File Inventory ---")
base = ROOT

# Script 1: epic/maps/*.json
maps_dir = os.path.join(base, "epic", "maps")
if os.path.isdir(maps_dir):
    jsons = [f for f in os.listdir(maps_dir) if f.endswith(".json")]
    print(f"  epic/maps/ : {len(jsons)} JSON files")
    for f in sorted(jsons)[:5]:
        fpath = os.path.join(maps_dir, f)
        size = os.path.getsize(fpath)
        print(f"    {f} ({size:,} bytes)")
    if len(jsons) > 5:
        print(f"    ... and {len(jsons)-5} more")
else:
    print(f"  epic/maps/ : directory not found")

# Script 2: submission_mcpacks/*.mctemplate
sub_dir = os.path.join(base, "submission_mcpacks")
if os.path.isdir(sub_dir):
    mcts = [f for f in os.listdir(sub_dir) if f.endswith(".mctemplate")]
    print(f"  submission_mcpacks/ : {len(mcts)} .mctemplate files")
    for f in sorted(mcts)[:5]:
        fpath = os.path.join(sub_dir, f)
        size = os.path.getsize(fpath)
        print(f"    {f} ({size:,} bytes)")
    if len(mcts) > 5:
        print(f"    ... and {len(mcts)-5} more")
else:
    print(f"  submission_mcpacks/ : directory not found")

# Script 3: mashup-packs/
mashup_dir = os.path.join(base, "marketplace-content", "mashup-packs")
if os.path.isdir(mashup_dir):
    dirs = [d for d in os.listdir(mashup_dir) if os.path.isdir(os.path.join(mashup_dir, d))]
    print(f"  marketplace-content/mashup-packs/ : {len(dirs)} pack directories")
    for d in sorted(dirs):
        dp = os.path.join(mashup_dir, d)
        items = os.listdir(dp)
        print(f"    {d}/ : {len(items)} files ({', '.join(items)})")
    # Also check description file
    desc_file = os.path.join(mashup_dir, "mashup-packs-description.txt")
    if os.path.isfile(desc_file):
        print(f"    mashup-packs-description.txt ({os.path.getsize(desc_file):,} bytes)")
else:
    print(f"  marketplace-content/mashup-packs/ : directory not found")

print("\nDone.")