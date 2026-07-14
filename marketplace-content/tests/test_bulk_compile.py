import os
import zipfile
import pytest
from pathlib import Path
import build_all

# Tier 1 - Feature Coverage

def test_valid_skin_pack_zip(tmp_path):
    # Setup mock structure
    skin_packs_dir = tmp_path / "skin-packs"
    skin_packs_dir.mkdir()
    pack_dir = skin_packs_dir / "my-skin-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (pack_dir / "skins.json").write_text("{}", encoding="utf-8")
    
    dist_dir = tmp_path / "dist"
    
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 1
    assert skipped == 0
    
    mcpack_file = dist_dir / "my-skin-pack.mcpack"
    assert mcpack_file.exists()
    
    with zipfile.ZipFile(mcpack_file, "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist
        assert "skins.json" in namelist

def test_valid_texture_pack_zip(tmp_path):
    texture_packs_dir = tmp_path / "texture-packs"
    texture_packs_dir.mkdir()
    pack_dir = texture_packs_dir / "my-texture-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (pack_dir / "pack_icon.png").write_text("icon", encoding="utf-8")
    
    dist_dir = tmp_path / "dist"
    
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 1
    
    mcpack_file = dist_dir / "my-texture-pack.mcpack"
    assert mcpack_file.exists()
    
    with zipfile.ZipFile(mcpack_file, "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist
        assert "pack_icon.png" in namelist

def test_hidden_file_exclusion(tmp_path):
    skin_packs_dir = tmp_path / "skin-packs"
    skin_packs_dir.mkdir()
    pack_dir = skin_packs_dir / "exclude-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (pack_dir / ".DS_Store").write_text("garbage", encoding="utf-8")
    (pack_dir / "__pycache__").mkdir()
    (pack_dir / "__pycache__" / "cached.pyc").write_text("cache", encoding="utf-8")
    
    dist_dir = tmp_path / "dist"
    build_all.run_build(tmp_path, dist_dir)
    
    mcpack_file = dist_dir / "exclude-pack.mcpack"
    with zipfile.ZipFile(mcpack_file, "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist
        assert ".DS_Store" not in namelist
        assert "__pycache__" not in namelist
        assert "__pycache__/cached.pyc" not in namelist

def test_dist_output_location(tmp_path):
    skin_packs_dir = tmp_path / "skin-packs"
    skin_packs_dir.mkdir()
    pack_dir = skin_packs_dir / "loc-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("{}", encoding="utf-8")
    
    dist_dir = tmp_path / "my-custom-dist"
    build_all.run_build(tmp_path, dist_dir)
    
    assert dist_dir.exists()
    assert (dist_dir / "loc-pack.mcpack").exists()

def test_multiple_packs_compilation(tmp_path):
    # Setup skin pack
    skin_packs_dir = tmp_path / "skin-packs"
    skin_packs_dir.mkdir()
    s_pack = skin_packs_dir / "s-pack"
    s_pack.mkdir()
    (s_pack / "manifest.json").write_text("{}", encoding="utf-8")
    
    # Setup texture pack
    texture_packs_dir = tmp_path / "texture-packs"
    texture_packs_dir.mkdir()
    t_pack = texture_packs_dir / "t-pack"
    t_pack.mkdir()
    (t_pack / "manifest.json").write_text("{}", encoding="utf-8")
    
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 2
    assert (dist_dir / "s-pack.mcpack").exists()
    assert (dist_dir / "t-pack.mcpack").exists()

# Tier 2 - Boundary & Corner Cases

def test_empty_source(tmp_path):
    # Source folders exist but have no packs
    (tmp_path / "skin-packs").mkdir()
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 0
    assert len(os.listdir(dist_dir)) == 0

def test_overwrite_existing(tmp_path):
    skin_packs_dir = tmp_path / "skin-packs"
    skin_packs_dir.mkdir()
    pack_dir = skin_packs_dir / "overwrite-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("new content", encoding="utf-8")
    
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    existing_file = dist_dir / "overwrite-pack.mcpack"
    existing_file.write_text("old zipped content", encoding="utf-8")
    
    # Run compiler
    build_all.run_build(tmp_path, dist_dir)
    
    # Verify it is overwritten with a valid zip instead of the plain text
    assert existing_file.exists()
    with zipfile.ZipFile(existing_file, "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist

def test_nested_subdirectories(tmp_path):
    skin_packs_dir = tmp_path / "skin-packs"
    skin_packs_dir.mkdir()
    pack_dir = skin_packs_dir / "nested-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("{}", encoding="utf-8")
    
    sub = pack_dir / "textures" / "skins"
    sub.mkdir(parents=True)
    (sub / "skin1.png").write_text("png", encoding="utf-8")
    
    dist_dir = tmp_path / "dist"
    build_all.run_build(tmp_path, dist_dir)
    
    mcpack_file = dist_dir / "nested-pack.mcpack"
    with zipfile.ZipFile(mcpack_file, "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist
        # Note standard zip separators are always forward slash
        assert "textures/skins/skin1.png" in namelist or "textures\\skins\\skin1.png" in namelist

def test_locked_destination(tmp_path, monkeypatch):
    # Try compiling when dist is unwriteable or zipfile raises an error
    skin_packs_dir = tmp_path / "skin-packs"
    skin_packs_dir.mkdir()
    pack_dir = skin_packs_dir / "lock-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("{}", encoding="utf-8")
    
    dist_dir = tmp_path / "dist"
    
    # We can mock ZipFile to throw PermissionError on write to simulate locked destination
    orig_zipfile = zipfile.ZipFile
    def mock_zipfile(*args, **kwargs):
        raise PermissionError("Destination locked")
        
    monkeypatch.setattr(zipfile, "ZipFile", mock_zipfile)
    
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    assert ok == 0
    assert skipped == 1

def test_mixed_valid_invalid_folders(tmp_path):
    skin_packs_dir = tmp_path / "skin-packs"
    skin_packs_dir.mkdir()
    
    # Valid pack
    pack_dir = skin_packs_dir / "valid-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("{}", encoding="utf-8")
    
    # Invalid folder (starts with dot)
    invalid_dir = skin_packs_dir / ".invalid-pack"
    invalid_dir.mkdir()
    (invalid_dir / "manifest.json").write_text("{}", encoding="utf-8")
    
    # Non-directory file inside skin-packs folder
    (skin_packs_dir / "readme.txt").write_text("documentation", encoding="utf-8")
    
    dist_dir = tmp_path / "dist"
    ok, skipped = build_all.run_build(tmp_path, dist_dir)
    
    # Only valid-pack should compile
    assert ok == 1
    assert (dist_dir / "valid-pack.mcpack").exists()
    assert not (dist_dir / ".invalid-pack.mcpack").exists()
    assert not (dist_dir / "readme.txt.mcpack").exists()
