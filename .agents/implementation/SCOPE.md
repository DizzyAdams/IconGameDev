# Scope: Implementation Track

## Architecture
- Module structure: `src/generators/`, `src/packagers/`, `src/validators/`
- UUID registry: persistent `output/uuid_registry.json` via `src/utils/uuid_manager.py`

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Generators | Implement/refactor classes for Skin, Texture, World, and Mashup packs, integrating `UUIDManager`. | None | DONE |
| 2 | Packagers | Refactor packaging logic to zip folders and assign correct extensions (`.mcpack`, `.mctemplate`/`.mcworld`). | M1 | DONE |
| 3 | Validators | Refactor validator to support skin sizes, paths, distinct validations, UUID checks. | M2 | DONE |
| 4 | Bulk Ingestor | Implement bulk ingestion/compilation of 500 skin inputs. | M1, M2 | DONE |
| 5 | E2E Integration & Verification | Run E2E tests once `TEST_READY.md` is published; fix bugs until 100% pass. | M1, M2, M3, M4 | DONE |
| 6 | Phase 2: Adversarial Hardening | Invert loop: spawn challengers to analyze code and write tests, fix bugs. | M5 | DONE |

## Interface Contracts
### Generators ↔ UUIDManager
- `BaseGenerator` resolves persistent header/module UUIDs using `UUIDManager.pack_uuids(pack_key)`.
### Generators ↔ Packager
- Generators produce uncompressed folder structure.
- `Packager.package(pack_dir, output_dir)` reads `manifest.json`, determines suffix, and compiles zip archive.
### Validators ↔ Packages
- `BedrockValidator.validate_mcpack(mcpack_path)` parses and validates zip package.
- `BedrockValidator.validate_all(dist_dir)` validates all packages in directory and runs global UUID collision checks.
