"""Build all packages for Marketplace submission — auto-discovers and builds via Packager."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.packagers.packager import Packager

DIST = ROOT / "dist"
SOURCE_DIRS = ["skin-packs", "texture-packs", "world-templates", "mashup-packs"]

def run_build(root_path=ROOT, dist_path=DIST):
    root_path = Path(root_path)
    dist_path = Path(dist_path)
    dist_path.mkdir(exist_ok=True)
    
    discovered_dirs = []
    for sd in SOURCE_DIRS:
        src_root = root_path / sd
        if not src_root.exists():
            continue
        for pack_dir in sorted(src_root.iterdir()):
            if pack_dir.is_dir() and not pack_dir.name.startswith("."):
                discovered_dirs.append(pack_dir)

    ok_count = 0
    skip_count = 0

    for pack_dir in discovered_dirs:
        try:
            pkg_file = Packager.package(pack_dir, dist_path)
            size_kb = pkg_file.stat().st_size / 1024
            ok_count += 1
            print(f"OK {pkg_file.name} ({size_kb:.0f} KB)")
        except Exception as e:
            print(f"ERROR packaging {pack_dir.name}: {e}")
            skip_count += 1

    print(f"\n=== BUILD COMPLETE ===")
    print(f"  OK: {ok_count}/{len(discovered_dirs)} packages built")
    print(f"  SKIPPED: {skip_count}")
    print(f"  Output: {dist_path}")
    return ok_count, skip_count

if __name__ == "__main__":
    run_build()
