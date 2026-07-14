# Project Context and Findings

## Initial Discoveries
- We are operating in the workspace `C:\Users\forrydev\Desktop\bedrock_minemods`.
- The workspace contains two main codebases/folders:
  - `bedrock-economy-rpg`: A Python-based RPG economy addon/plugin structure.
  - `marketplace-content`: A Node/Python project containing generator scripts, pack templates, and validators.
- Compliance guidelines exist in `C:\Users\forrydev\Desktop\bedrock_minemods\compliance`:
  - `01-technical-compliance.md` outlines `manifest.json` schemas, PNG specifications, and `skins.json` formats.
  - References to helper scripts:
    - UUID manager: `marketplace-content/src/utils/uuid_manager.py`
    - Validator: `marketplace-content/src/validators/bedrock_validator.py`
- Pre-existing scripts are located in `marketplace-content/scripts/`, including:
  - `generate-massive-packs.py` (58 KB)
  - `generate-all-skin-packs.py` (12.5 KB)
  - `generate-texture-packs.py` (11 KB)
  - `generate-bbmodel.py` (7 KB)
  - `generate-skin-textures.py` (1.6 KB)
  - `generate-texture-pack.py` (1.7 KB)

## Requirements Checklist
1. **R1. Mass Compilation Engine**: Bulk ingest skins/textures, output valid `.mcpack` files.
2. **R2. Output Validation & Verification**: Enforce schemas, validate JSONs, unique UUIDs, check texture sizes.
3. **Acceptance Criteria**:
   - Programmatically ingest 500 skin inputs to generate `.mcpack` files.
   - Validation test confirms JSON validity of 100% of `manifest.json` and `skins.json` files.
   - Validator confirms no two `.mcpack` files share the same UUIDs.
