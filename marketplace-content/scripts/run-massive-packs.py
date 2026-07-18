#!/usr/bin/env python
"""Wrapper to run generate-massive-packs.py with timeout and result reporting."""
import sys
import subprocess
import time

SCRIPT = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."
SCRIPT = SCRIPT + "/generate-massive-packs.py"

print("=== Running massive packs generator ===")
print(f"Script: {SCRIPT}")
print()

start = time.time()

try:
    result = subprocess.run(
        [sys.executable, SCRIPT],
        capture_output=True,
        text=True,
        timeout=900,
        cwd=__file__.rsplit("/scripts/", 1)[0] if "/scripts/" in __file__ else "."
    )
    elapsed = time.time() - start

    print(result.stdout)
    if result.stderr:
        print("=== STDERR ===")
        print(result.stderr)
    print(f"\n=== Completed in {elapsed:.1f}s (exit code {result.returncode}) ===")

except subprocess.TimeoutExpired:
    elapsed = time.time() - start
    print(f"\n=== TIMEOUT after {elapsed:.1f}s (900s limit exceeded) ===")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n=== FAILED after {elapsed:.1f}s: {e} ===")