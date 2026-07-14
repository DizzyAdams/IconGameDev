import os
import json
import pytest
from pathlib import Path
import skin_pack_gen
import texture_pack_gen
import build_all
from validators.bedrock_validator import BedrockValidator

def test_100_skins_workload(tmp_path, monkeypatch):
    # Create 100 skin tuples
    skins = []
    for i in range(100):
        skins.append((f"Skin_{i}", (i % 256, (i * 2) % 256, (i * 3) % 256), (0, 0, 0)))
    
    test_pack = {
        "dir": "skins-100-pack",
        "manifest_name": "100 Skins Pack",
        "manifest_desc": "Workload test for 100 skins",
        "price": "$2.99",
        "header_uuid": "100-header-uuid-uuid",
        "module_uuid": "100-module-uuid-uuid",
        "skins": skins
    }
    
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path / "skin-packs"))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [test_pack])
    
    skin_pack_gen.main()
    
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 1
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(dist_dir / "skins-100-pack.mcpack"))
    assert result["valid"] is True
    assert result["info"]["files"] == 103 # manifest + skins.json + icon + 100 skins

def test_500_skins_workload(tmp_path, monkeypatch):
    # Create 500 skin tuples
    skins = []
    for i in range(500):
        skins.append((f"Skin_{i}", (i % 256, (i * 2) % 256, (i * 3) % 256), (255, 255, 255)))
    
    test_pack = {
        "dir": "skins-500-pack",
        "manifest_name": "500 Skins Pack",
        "manifest_desc": "Workload test for 500 skins",
        "price": "$5.99",
        "header_uuid": "500-header-uuid-uuid",
        "module_uuid": "500-module-uuid-uuid",
        "skins": skins
    }
    
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path / "skin-packs"))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [test_pack])
    
    skin_pack_gen.main()
    
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 1
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(dist_dir / "skins-500-pack.mcpack"))
    assert result["valid"] is True
    assert result["info"]["files"] == 503 # manifest + skins.json + icon + 500 skins

def test_multi_pack_submission_batch(tmp_path, monkeypatch):
    # Setup 3 skin packs
    skin_packs = []
    for i in range(3):
        skin_packs.append({
            "dir": f"skin-pack-{i}",
            "manifest_name": f"Skin Pack {i}",
            "manifest_desc": f"Desc {i}",
            "price": "Free",
            "header_uuid": f"h-skin-{i}",
            "module_uuid": f"m-skin-{i}",
            "skins": [(f"SkinA", (0, 0, 0), (255, 255, 255))]
        })
    
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path / "skin-packs"))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", skin_packs)
    skin_pack_gen.main()
    
    # Setup 3 texture packs
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path / "texture-packs"))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone'])
    
    for i in range(3):
        t_pack = {
            'dir': f'tex-pack-{i}',
            'name': f'Texture Pack {i}',
            'desc': 'Desc',
            'header_uuid': f'h-tex-{i}',
            'module_uuid': f'm-tex-{i}',
            'modify': lambda c, rng: c,
            'noise_range': 5,
            'icon_label': 'T',
            'icon_sub': str(i),
        }
        texture_pack_gen.generate_pack(t_pack)
        
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    # 3 skin packs + 3 texture packs = 6 packs total
    assert ok == 6
    
    validator = BedrockValidator()
    results = validator.validate_all(str(dist_dir))
    assert len(results) == 6
    for r in results:
        assert r["valid"] is True

def test_large_texture_pack_40_blocks(tmp_path, monkeypatch):
    # Ensure we use 40+ block names. We'll populate BLOCK_COLORS with 45 block names
    custom_colors = {}
    for i in range(45):
        custom_colors[f"custom_block_{i}"] = (128, 128, 128)
        
    test_pack = {
        'dir': 'large-texture-pack',
        'name': 'Large Texture Pack',
        'desc': 'Workload test for 45 block textures',
        'header_uuid': 'large-tex-header',
        'module_uuid': 'large-tex-module',
        'modify': lambda c, rng: c,
        'noise_range': 10,
        'icon_label': 'L',
        'icon_sub': 'T',
    }
    
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path / "texture-packs"))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_COLORS", custom_colors)
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", list(custom_colors.keys()))
    
    texture_pack_gen.generate_pack(test_pack)
    
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 1
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(dist_dir / "large-texture-pack.mcpack"))
    assert result["valid"] is True
    # The directory should contain 45 textures, pack_icon.png, and manifest.json
    assert result["info"]["files"] == 47

def test_e2e_full_pipeline_execution(tmp_path, monkeypatch):
    # Run the default generation for 1 skin pack and 1 texture pack using current script definitions
    default_skin_packs = skin_pack_gen.PACK_DEFS[:1]
    default_tex_packs = texture_pack_gen.PACKS[:1]
    
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path / "skin-packs"))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", default_skin_packs)
    
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path / "texture-packs"))
    monkeypatch.setattr(texture_pack_gen, "PACKS", default_tex_packs)
    
    # 1. Skin Gen
    skin_pack_gen.main()
    # 2. Texture Gen
    texture_pack_gen.main()
    
    # 3. Bulk Compile
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 2
    
    # 4. Validator
    validator = BedrockValidator()
    results = validator.validate_all(str(dist_dir))
    assert len(results) == 2
    
    # 5. Report
    rep = validator.report()
    assert "BEDROCK VALIDATION REPORT" in rep
    assert "SUMMARY: 2/2 passed" in rep
