import os
import pytest
from pathlib import Path
import skin_pack_gen
import texture_pack_gen
import build_all
from validators.bedrock_validator import BedrockValidator

def test_skin_gen_and_validation(tmp_path, monkeypatch):
    # 1. Skin pack generation
    test_pack = {
        "dir": "cross-skin-pack",
        "manifest_name": "Cross Skin Pack",
        "manifest_desc": "Desc",
        "price": "Free",
        "header_uuid": "11111111-aaaa-bbbb-cccc-111111111111",
        "module_uuid": "22222222-aaaa-bbbb-cccc-222222222222",
        "skins": [
            ("HeroSkin", (0, 0, 0), (255, 255, 255))
        ]
    }
    
    # Configure paths
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path / "skin-packs"))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [test_pack])
    skin_pack_gen.main()
    
    # 2. Compilation
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 1
    
    # 3. Validation
    validator = BedrockValidator()
    mcpack_file = dist_dir / "cross-skin-pack.mcpack"
    result = validator.validate_mcpack(str(mcpack_file))
    
    assert result["valid"] is True
    assert len(result["errors"]) == 0

def test_texture_gen_and_validation(tmp_path, monkeypatch):
    # 1. Texture pack generation
    test_pack = {
        'dir': 'cross-tex-pack',
        'name': 'Cross Texture Pack',
        'desc': 'Desc',
        'header_uuid': '33333333-aaaa-bbbb-cccc-333333333333',
        'module_uuid': '44444444-aaaa-bbbb-cccc-444444444444',
        'modify': lambda c, rng: c,
        'noise_range': 10,
        'seed': 42,
        'tile_size': 16,
        'icon_label': 'C',
        'icon_sub': 'T',
    }
    
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path / "texture-packs"))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone', 'dirt'])
    
    texture_pack_gen.generate_pack(test_pack, 0, 1)
    
    # 2. Compilation
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 1
    
    # 3. Validation
    validator = BedrockValidator()
    mcpack_file = dist_dir / "cross-tex-pack.mcpack"
    result = validator.validate_mcpack(str(mcpack_file))
    
    assert result["valid"] is True
    # It might have resource warnings since skins.json is not expected, which is normal.
    assert len(result["errors"]) == 0

def test_bulk_compile_and_validate_all(tmp_path, monkeypatch):
    # Setup skin pack gen
    s_pack = {
        "dir": "bulk-s-pack",
        "manifest_name": "Bulk Skin Pack",
        "manifest_desc": "Desc",
        "price": "Free",
        "header_uuid": "55555555-aaaa-bbbb-cccc-555555555555",
        "module_uuid": "66666666-aaaa-bbbb-cccc-666666666666",
        "skins": [("SkinA", (0, 0, 0), (255, 255, 255))]
    }
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path / "skin-packs"))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [s_pack])
    skin_pack_gen.main()
    
    # Setup texture pack gen
    t_pack = {
        'dir': 'bulk-t-pack',
        'name': 'Bulk Texture Pack',
        'desc': 'Desc',
        'header_uuid': '77777777-aaaa-bbbb-cccc-777777777777',
        'module_uuid': '88888888-aaaa-bbbb-cccc-888888888888',
        'modify': lambda c, rng: c,
        'noise_range': 10,
        'seed': 42,
        'tile_size': 16,
        'icon_label': 'B',
        'icon_sub': 'T',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path / "texture-packs"))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone'])
    texture_pack_gen.generate_pack(t_pack, 0, 1)
    
    # Compile all
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 2
    
    # Validate all
    validator = BedrockValidator()
    results = validator.validate_all(str(dist_dir))
    
    assert len(results) == 2
    assert results[0]["valid"] is True
    assert results[1]["valid"] is True

def test_mixed_generation_and_compilation(tmp_path, monkeypatch):
    # Verify compilation & validation filters hidden files and validates correctly
    # when both valid and corrupt packs are present.
    
    # 1. Valid skin pack
    s_pack = {
        "dir": "mixed-valid",
        "manifest_name": "Mixed Valid",
        "manifest_desc": "Desc",
        "price": "Free",
        "header_uuid": "99999999-aaaa-bbbb-cccc-999999999999",
        "module_uuid": "00000000-aaaa-bbbb-cccc-000000000000",
        "skins": [("SkinX", (0, 0, 0), (255, 255, 255))]
    }
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path / "skin-packs"))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [s_pack])
    skin_pack_gen.main()
    
    # 2. Semi-invalid pack (we write some extra invalid files in it)
    invalid_pack_dir = tmp_path / "skin-packs" / "mixed-invalid"
    invalid_pack_dir.mkdir(parents=True, exist_ok=True)
    # Missing manifest entirely
    (invalid_pack_dir / "random_file.txt").write_text("some content")
    
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    
    # Both directories mixed-valid and mixed-invalid are folders, so both are zipped
    assert ok == 2
    
    # Run validation
    validator = BedrockValidator()
    results = validator.validate_all(str(dist_dir))
    
    assert len(results) == 2
    valid_results = [r for r in results if r["file"] == "mixed-valid.mcpack"]
    invalid_results = [r for r in results if r["file"] == "mixed-invalid.mcpack"]
    
    assert len(valid_results) == 1
    assert valid_results[0]["valid"] is True
    
    assert len(invalid_results) == 1
    assert invalid_results[0]["valid"] is False
    assert any("manifest.json missing" in err for err in invalid_results[0]["errors"])
