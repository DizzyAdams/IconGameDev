"""Run all three Bedrock content generation scripts in order via subprocess."""
import subprocess
import sys
import os

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'marketplace-content', 'scripts')
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'marketplace-content')

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
        cwd=BASE
    )
    print(result.stdout)
    if result.stderr:
        stderr_lines = result.stderr.strip().splitlines()
        if stderr_lines:
            print("STDERR:", result.stderr)
    if result.returncode != 0:
        print(f"FAILED with code {result.returncode}")
        print(f"STDERR: {result.stderr}")
        sys.exit(result.returncode)
    else:
        print(f"OK (exit code {result.returncode})")

print("\n" + "="*60)
print("ALL DONE")
print("="*60)

# List output
print("\n=== OUTPUT STRUCTURE ===")
for root, dirs, files in os.walk(BASE):
    level = root.replace(BASE, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        fpath = os.path.join(root, file)
        fsize = os.path.getsize(fpath)
        print(f"{subindent}{file}  ({fsize} bytes)")