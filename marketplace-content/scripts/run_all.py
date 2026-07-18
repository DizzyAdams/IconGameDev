"""Run all Bedrock content generation scripts in order."""
import subprocess
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ORDER = [
    "generate-addons.py",
    "generate-mashups.py",
    "package-addons.py",
]

for script in ORDER:
    path = os.path.join(SCRIPTS_DIR, script)
    print(f"\n{'='*60}")
    print(f"RUNNING: {script}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, path],
        capture_output=True, text=True, timeout=300,
        cwd=os.path.dirname(SCRIPTS_DIR)
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    if result.returncode != 0:
        print(f"FAILED with code {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"OK (exit code {result.returncode})")

print("\n" + "="*60)
print("ALL DONE")
print("="*60)