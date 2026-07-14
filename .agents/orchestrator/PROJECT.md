# Project: Minecraft Bedrock Skin & Texture Pack Generator Automation

## Architecture
The system is divided into three key packages within `marketplace-content/src/`:
- `generators/`: Standardized classes for pack generation.
  - `BaseGenerator`: Abstract base class handling manifest creation and UUID management.
  - `SkinPackGenerator`: Generates skin PNGs (64x64/128x128), `skins.json`, and manifest.
  - `TexturePackGenerator`: Generates block/item textures, assets directory, and manifest.
  - `WorldTemplateGenerator`: Generates world templates including `level.dat` and `world_icon.png`.
  - `MashupPackGenerator`: Combines skins, textures, and worlds.
- `packagers/`: Standardized packaging tool.
  - `Packager`: Compresses the pack directory. Correctly determines file extensions:
    - Skin, Texture, Mashup packs -> `.mcpack`
    - World templates -> `.mcworld` or `.mctemplate`
- `validators/`: Verification and schema validation.
  - `BedrockValidator`: Parses generated manifests, verifies skin dimensions (64x32, 64x64, 128x128), validates paths (e.g., skin textures under `textures/skins/`), prevents false warnings for world templates, and performs global UUID collision checks.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| 1 | Exploration & Architecture | Analyze existing codebase and design interfaces | None | DONE |
| 2 | E2E Testing Track | Design E2E test harness and Tier 1-4 tests | M1 | DONE |
| 3 | Core Implementation | Refactor generators, packager, and validator | M1 | DONE |
| 4 | Bulk Processing | Implement bulk ingestion/compilation of 500 skin inputs | M3 | DONE |
| 5 | Output Validation | Enhance bedrock validator with strict schema & collision checks | M3 | DONE |
| 6 | Integration & Verification | E2E Testing Track integration and 100% tests pass | M2, M4, M5 | DONE |
| 7 | Adversarial Hardening | Tier 5 white-box coverage hardening | M6 | DONE |

## Interface Contracts
### 1. BaseGenerator & UUIDManager
- UUIDManager:
  - `UUIDManager.get_or_create(context: str) -> str`: Returns persistent, valid UUIDv4.
- Generators:
  - `Generator.generate(config: dict) -> str`: Runs generation and returns the output directory path.

### 2. Packager
- `Packager.package(pack_dir: Path, output_dir: Path) -> Path`: Packages a folder and returns the path to the compressed file. Auto-detects extension based on pack type.

### 3. BedrockValidator
- `BedrockValidator.validate_mcpack(path: str) -> dict`: Returns validation results: `{"valid": bool, "errors": list, "warnings": list, "info": dict}`.
- `BedrockValidator.validate_all(dist_dir: str) -> list`: Validates all generated packages in `dist_dir` and performs global duplicate UUID analysis across all packages.
