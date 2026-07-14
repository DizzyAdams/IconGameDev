# E2E Test Suite Implementation Plan

This plan details the 49+ tests to be implemented in `marketplace-content/tests/` (using pytest).

## Test Case Inventory

### Tier 1: Feature Coverage (20 tests, 5 per feature)

#### Feature 1: Skin Pack Generation
1. `test_skin_pack_manifest_structure`: Verify `manifest.json` contains format_version, header, modules with correct keys.
2. `test_skin_pack_skins_json_structure`: Verify `skins.json` contains skins array and serialize/localization names.
3. `test_skin_pack_icon_dimension`: Verify `icon.png` is generated with 300x300 resolution.
4. `test_skin_pack_texture_dimension`: Verify generated skin textures are 64x64 PNGs.
5. `test_skin_pack_output_files_exist`: Verify all output directories and files are present.

#### Feature 2: Texture Pack Generation
6. `test_texture_pack_manifest_structure`: Verify `manifest.json` modules have type "resources".
7. `test_texture_pack_icon_dimension`: Verify `pack_icon.png` is generated with 256x256 resolution.
8. `test_texture_pack_blocks_dimension`: Verify block textures are generated with 32x32 (or 16x16) resolution.
9. `test_texture_pack_all_blocks_exist`: Verify all 40 standard blocks (e.g. stone, granite) are generated.
10. `test_texture_pack_output_structure`: Verify texture pack output folders (`textures/blocks/`) exist.

#### Feature 3: Bulk Compilation
11. `test_bulk_compile_skin_pack_zip`: Compile a skin pack and verify `.mcpack` is a valid zip.
12. `test_bulk_compile_texture_pack_zip`: Compile a texture pack and verify `.mcpack` is a valid zip.
13. `test_bulk_compile_excludes_hidden`: Verify `.mcpack` does not contain hidden files (`.` prefix) or `__pycache__`.
14. `test_bulk_compile_all_output_in_dist`: Verify compiled packs are placed in the `dist` folder.
15. `test_bulk_compile_multiple_packs`: Verify bulk compilation processes multiple source packs.

#### Feature 4: Output Validation
16. `test_validator_valid_skin_pack_passes`: Verify validator returns `valid=True` for a compiled valid skin pack.
17. `test_validator_valid_texture_pack_passes`: Verify validator returns `valid=True` for a compiled valid texture pack.
18. `test_validator_info_statistics`: Verify validator accurately reports file count and size in KB.
19. `test_validator_missing_manifest_fails`: Verify validator flags missing `manifest.json` as an error.
20. `test_validator_wrong_icon_size_warns`: Verify validator issues warning for icons not matching 256x256.

---

### Tier 2: Boundary & Corner Cases (20 tests, 5 per feature)

#### Feature 1: Skin Pack Generation
21. `test_skin_pack_empty_skins_list`: Verify generation behaves correctly when a pack definition has no skins.
22. `test_skin_pack_invalid_rgb_colors`: Test generator handles RGB colors outside 0-255 bounds.
23. `test_skin_pack_duplicate_skin_names`: Test behavior when a pack has skins with duplicate localization names.
24. `test_skin_pack_long_name_manifest`: Test generator behavior with extremely long pack/skin names.
25. `test_skin_pack_duplicate_uuids`: Test verification when different packs use identical UUIDs.

#### Feature 2: Texture Pack Generation
26. `test_texture_pack_custom_block_palette`: Generate a pack with non-standard blocks and custom colors.
27. `test_texture_pack_darkness_factor_extremes`: Verify color darken factor handles 0.0 and 1.0 safely.
28. `test_texture_pack_custom_noise_range`: Verify texture generation works with zero noise and huge noise bounds.
29. `test_texture_pack_empty_palette`: Test behavior when block color dictionary is empty.
30. `test_texture_pack_write_locked_directory`: Verify elegant failure if target directory is write-protected.

#### Feature 3: Bulk Compilation
31. `test_bulk_compile_empty_source_dir`: Verify behavior when the source directory (e.g., skin-packs) is empty.
32. `test_bulk_compile_overwrites_existing`: Verify compiler successfully overwrites existing `.mcpack` files in `dist/`.
33. `test_bulk_compile_nested_subdirs`: Test zip compilation containing deep nested subdirectories.
34. `test_bulk_compile_locked_destination`: Verify graceful failure when output `.mcpack` is locked/read-only.
35. `test_bulk_compile_mix_valid_invalid`: Test compile with a mix of valid folders and invalid names/files in source.

#### Feature 4: Output Validation
36. `test_validator_corrupt_zip`: Verify validator flags corrupted/empty `.mcpack` zip files as invalid.
37. `test_validator_invalid_manifest_json_syntax`: Verify validator flags manifest with syntax error.
38. `test_validator_missing_manifest_keys`: Verify validator flags manifest missing header or modules.
39. `test_validator_missing_skin_texture_warning`: Verify warning is generated when `skins.json` references a non-existent texture PNG.
40. `test_validator_nonexistent_mcpack_path`: Verify validator returns `valid=False` and error for non-existent path.

---

### Tier 3: Cross-Feature Combinations (4 tests)

41. `test_integration_skin_gen_to_validation`: Generate a skin pack, compile it to `.mcpack`, and validate. Must pass cleanly.
42. `test_integration_texture_gen_to_validation`: Generate a texture pack, compile it to `.mcpack`, and validate. Must pass cleanly.
43. `test_integration_bulk_compile_and_validate_all`: Generate multiple packs, run bulk compile, and use `validate_all()` to assert all outputs are valid.
44. `test_integration_mixed_generation_compilation`: Run skin and texture pack generation and bulk compile together, confirming both formats coexist correctly.

---

### Tier 4: Real-World Workload (5 tests)

45. `test_workload_100_skins`: Mock ingestion and generation of 100 skin inputs, compiling and validating them.
46. `test_workload_500_skins`: Mock ingestion and generation of 500 skin inputs, compiling and validating them.
47. `test_workload_multi_pack_submission`: Process ingestion, compilation, and validation of 10 skin packs and 5 texture packs simultaneously.
48. `test_workload_large_texture_pack`: Modify and compile a large texture pack with 40+ block textures and verify execution time and validator metrics.
49. `test_workload_e2e_full_pipeline`: Generate all 8 standard skin packs and 2 texture packs, bulk compile them, validate all, and check validation report output format.
