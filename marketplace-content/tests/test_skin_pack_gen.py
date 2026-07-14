import os
import json
import pytest
from PIL import Image
import skin_pack_gen

# Tier 1 - Feature Coverage

def test_manifest_structure():
    pack = {
        "manifest_name": "Test Pack",
        "manifest_desc": "Test Description",
        "header_uuid": "11111111-2222-3333-4444-555555555555",
        "module_uuid": "66666666-7777-8888-9999-000000000000",
        "skins": []
    }
    manifest = skin_pack_gen.make_manifest(pack)
    assert manifest["format_version"] == 2
    assert manifest["header"]["name"] == "Test Pack"
    assert manifest["header"]["description"] == "Test Description"
    assert manifest["header"]["uuid"] == "11111111-2222-3333-4444-555555555555"
    assert manifest["modules"][0]["type"] == "skin_pack"
    assert manifest["modules"][0]["uuid"] == "66666666-7777-8888-9999-000000000000"

def test_skins_json_format():
    pack = {
        "manifest_name": "Test Pack",
        "skins": [
            ("Skin1", (255, 0, 0), (0, 255, 0)),
            ("Skin2", (0, 0, 255), (255, 255, 255))
        ]
    }
    skins_json = skin_pack_gen.make_skins_json(pack)
    assert skins_json["serialize_name"] == "Test Pack"
    assert len(skins_json["skins"]) == 2
    assert skins_json["skins"][0]["localization_name"] == "Skin1"
    assert skins_json["skins"][0]["geometry"] == "geometry.humanoid.custom"
    assert skins_json["skins"][0]["texture"] == "Skin1.png"
    assert skins_json["skins"][1]["localization_name"] == "Skin2"

def test_icon_dimensions():
    icon = skin_pack_gen.generate_icon((255, 0, 0), (0, 255, 0))
    assert icon.size == (300, 300)
    assert icon.mode == 'RGBA'

def test_texture_dimensions():
    tex = skin_pack_gen.generate_texture((100, 150, 200), (50, 50, 50), is_8bit=False)
    assert tex.size == (64, 64)
    assert tex.mode == 'RGBA'
    
    tex_8bit = skin_pack_gen.generate_texture((100, 150, 200), (50, 50, 50), is_8bit=True)
    assert tex_8bit.size == (64, 64)
    assert tex_8bit.mode == 'RGBA'

def test_folder_structure(tmp_path, monkeypatch):
    test_pack = {
        "dir": "test-pack-dir",
        "manifest_name": "Test Pack E2E",
        "manifest_desc": "Test E2E Pack Description",
        "price": "$1.99",
        "header_uuid": "aaaa-bbbb",
        "module_uuid": "cccc-dddd",
        "skins": [
            ("TestSkin", (10, 20, 30), (40, 50, 60))
        ]
    }
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [test_pack])
    
    skin_pack_gen.main()
    
    pack_dir = tmp_path / "test-pack-dir"
    assert pack_dir.exists()
    assert (pack_dir / "manifest.json").exists()
    assert (pack_dir / "skins.json").exists()
    
    skins_dir = pack_dir / "textures" / "skins"
    assert skins_dir.exists()
    assert (skins_dir / "TestSkin.png").exists()
    assert (skins_dir / "icon.png").exists()

# Tier 2 - Boundary & Corner Cases

def test_empty_skins_list(tmp_path, monkeypatch):
    test_pack = {
        "dir": "empty-skin-pack",
        "manifest_name": "Empty Skins Pack",
        "manifest_desc": "No skins in this pack",
        "price": "Free",
        "header_uuid": "h-uuid",
        "module_uuid": "m-uuid",
        "skins": []
    }
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [test_pack])
    
    # We should be able to run main without errors, even with empty skins
    skin_pack_gen.main()
    
    pack_dir = tmp_path / "empty-skin-pack"
    assert pack_dir.exists()
    assert (pack_dir / "manifest.json").exists()
    
    with open(pack_dir / "skins.json") as f:
        data = json.load(f)
        assert data["skins"] == []

def test_invalid_color_ranges():
    # PIL should raise ValueError for invalid color values or incorrect tuple sizes
    with pytest.raises(ValueError):
        skin_pack_gen.generate_texture((300, 100, 100), (0, 0, 0))
    with pytest.raises(ValueError):
        skin_pack_gen.generate_texture((100, 100), (0, 0, 0))
    with pytest.raises(ValueError):
        skin_pack_gen.generate_icon((-5, 100, 100), (0, 0, 0))

def test_duplicate_skin_names(tmp_path, monkeypatch):
    test_pack = {
        "dir": "dup-skin-pack",
        "manifest_name": "Dup Skins Pack",
        "manifest_desc": "Contains duplicate skin names",
        "price": "Free",
        "header_uuid": "h-uuid",
        "module_uuid": "m-uuid",
        "skins": [
            ("DupSkin", (10, 20, 30), (40, 50, 60)),
            ("DupSkin", (100, 110, 120), (130, 140, 150))
        ]
    }
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [test_pack])
    
    skin_pack_gen.main()
    
    pack_dir = tmp_path / "dup-skin-pack"
    skins_dir = pack_dir / "textures" / "skins"
    # File should exist, but only one is saved (overwritten)
    assert (skins_dir / "DupSkin.png").exists()
    
    with open(pack_dir / "skins.json") as f:
        data = json.load(f)
        # Verify both entries are in the skins.json array
        assert len(data["skins"]) == 2
        assert data["skins"][0]["localization_name"] == "DupSkin"
        assert data["skins"][1]["localization_name"] == "DupSkin"

def test_long_skin_names(tmp_path, monkeypatch):
    long_name = "A" * 100
    test_pack = {
        "dir": "long-skin-pack",
        "manifest_name": "Long Skins Pack",
        "manifest_desc": "Contains long skin name",
        "price": "Free",
        "header_uuid": "h-uuid",
        "module_uuid": "m-uuid",
        "skins": [
            (long_name, (10, 20, 30), (40, 50, 60))
        ]
    }
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [test_pack])
    
    skin_pack_gen.main()
    
    pack_dir = tmp_path / "long-skin-pack"
    skins_dir = pack_dir / "textures" / "skins"
    assert (skins_dir / f"{long_name}.png").exists()

def test_duplicate_uuids(tmp_path, monkeypatch):
    # Tests behavior when header and module UUIDs are the same
    dup_uuid = "same-uuid-for-both-header-and-module"
    test_pack = {
        "dir": "dup-uuid-pack",
        "manifest_name": "Dup UUID Pack",
        "manifest_desc": "Contains duplicate UUIDs",
        "price": "Free",
        "header_uuid": dup_uuid,
        "module_uuid": dup_uuid,
        "skins": [
            ("Skin1", (10, 20, 30), (40, 50, 60))
        ]
    }
    monkeypatch.setattr(skin_pack_gen, "SKIN_PACKS_DIR", str(tmp_path))
    monkeypatch.setattr(skin_pack_gen, "PACK_DEFS", [test_pack])
    
    skin_pack_gen.main()
    
    pack_dir = tmp_path / "dup-uuid-pack"
    with open(pack_dir / "manifest.json") as f:
        data = json.load(f)
        assert data["header"]["uuid"] == dup_uuid
        assert data["modules"][0]["uuid"] == dup_uuid
