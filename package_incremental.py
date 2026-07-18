#!/usr/bin/env python3
"""Incremental packager: zip marketplace-content pack dirs that have no
corresponding .mcpack in submission_mcpacks. Idempotent.

world-templates dirs are intentionally skipped: they are manifest-only stubs
(no level.dat), and valid world templates are produced separately as
.mctemplate (see generate_50_templates.py / regen_frostbound.py).
"""
import os
import zipfile
from pathlib import Path

BASE_DIR = Path("marketplace-content")
OUTPUT_DIR = Path("submission_mcpacks")
PACK_TYPES = ["skin-packs", "texture-packs", "mashup-packs", "behavior-packs"]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    existing = {p.stem for p in OUTPUT_DIR.glob("*.mcpack")}
    created = 0
    for pack_type in PACK_TYPES:
        type_dir = BASE_DIR / pack_type
        if not type_dir.is_dir():
            continue
        for pack_path in sorted(type_dir.iterdir()):
            if not pack_path.is_dir() or pack_path.name in existing:
                continue
            if not (pack_path / "manifest.json").is_file():
                continue  # not a pack dir (e.g. shared scripts/ folder)
            out = OUTPUT_DIR / f"{pack_path.name}.mcpack"
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _dirs, files in os.walk(pack_path):
                    for f in files:
                        fp = Path(root) / f
                        zf.write(fp, fp.relative_to(pack_path))
            created += 1
    print(f"created={created}")


if __name__ == "__main__":
    main()
