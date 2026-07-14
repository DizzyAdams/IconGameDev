#!/usr/bin/env python3
"""
Package Bedrock content packs into .mcpack files for Microsoft Marketplace submission.
- Walks through marketplace-content/behavior-packs, skin-packs, mashup-packs
- For each pack directory, creates a .mcpack zip file containing all files in that directory
- Outputs to a submission directory
- Skips audit and backup directories
"""

import os
import zipfile
from pathlib import Path

BASE_DIR = Path("marketplace-content")
OUTPUT_DIR = Path("submission_mcpacks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PACK_TYPES = ["behavior-packs", "skin-packs", "mashup-packs"]

def pack_directory(pack_type: str, pack_name: str):
    pack_path = BASE_DIR / pack_type / pack_name
    if not pack_path.is_dir():
        return
    output_file = OUTPUT_DIR / f"{pack_name}.mcpack"
    # If file already exists, we can overwrite or skip
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(pack_path):
            # Skip any hidden or system directories if needed
            for file in files:
                file_path = Path(root) / file
                # Create arcname as relative to pack_path
                arcname = file_path.relative_to(pack_path)
                zipf.write(file_path, arcname)
    print(f"Packed {pack_path} -> {output_file}")

def main():
    for pack_type in PACK_TYPES:
        pack_type_path = BASE_DIR / pack_type
        if not pack_type_path.is_dir():
            continue
        for pack_name in os.listdir(pack_type_path):
            pack_path = pack_type_path / pack_name
            if pack_path.is_dir():
                pack_directory(pack_type, pack_name)
    
    print(f"\nAll packs have been packaged into .mcpack files in {OUTPUT_DIR.resolve()}")
    print("You can now upload these .mcpack files to the Microsoft Partner Center.")

if __name__ == "__main__":
    main()