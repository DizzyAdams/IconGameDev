import os
import json
import zipfile
import pytest
from PIL import Image
from validators.bedrock_validator import BedrockValidator

# Helpers

def create_valid_manifest(header_uuid="4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e", module_uuid="5c6d7e8f-9a0b-1c2d-3e4f-5a6b7c8d9e0f"):
    return {
        "format_version": 2,
        "header": {
            "name": "Test Name",
            "description": "Test Desc",
            "uuid": header_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "skin_pack",
                "uuid": module_uuid,
                "version": [1, 0, 0]
            }
        ]
    }

def create_valid_skins_json():
    return {
        "skins": [
            {
                "localization_name": "Skin1",
                "geometry": "geometry.humanoid.custom",
                "texture": "Skin1.png",
                "type": "free"
            }
        ],
        "serialize_name": "Test Name",
        "localization_name": "Test Name"
    }

def build_zip(zip_path, files):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for arcname, content in files.items():
            if isinstance(content, str):
                zf.writestr(arcname, content)
            elif isinstance(content, bytes):
                zf.writestr(arcname, content)
            elif isinstance(content, Image.Image):
                # Save PIL Image to bytes
                from io import BytesIO
                out = BytesIO()
                content.save(out, format="PNG")
                zf.writestr(arcname, out.getvalue())

# Tier 1 - Feature Coverage

def test_validator_reports_pass(tmp_path):
    mcpack_path = tmp_path / "valid_pack.mcpack"
    
    icon = Image.new('RGB', (256, 256), color=(255, 0, 0))
    skin_tex = Image.new('RGB', (64, 64), color=(0, 255, 0))
    
    files = {
        "manifest.json": json.dumps(create_valid_manifest()),
        "skins.json": json.dumps(create_valid_skins_json()),
        "pack_icon.png": icon,
        "skins/Skin1.png": skin_tex
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is True
    assert len(result["errors"]) == 0

def test_reports_info_stats(tmp_path):
    mcpack_path = tmp_path / "info_pack.mcpack"
    
    files = {
        "manifest.json": json.dumps(create_valid_manifest()),
        "skins.json": json.dumps(create_valid_skins_json()),
        "skins/Skin1.png": Image.new('RGB', (64, 64))
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert "info" in result
    assert result["info"]["files"] == 3
    assert result["info"]["size_bytes"] > 0
    assert result["info"]["size_kb"] > 0.0

def test_flags_missing_manifest(tmp_path):
    mcpack_path = tmp_path / "no_manifest.mcpack"
    files = {
        "skins.json": json.dumps(create_valid_skins_json()),
        "skins/Skin1.png": Image.new('RGB', (64, 64))
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is False
    assert any("manifest.json missing" in err for err in result["errors"])

def test_flags_wrong_icon_size(tmp_path):
    mcpack_path = tmp_path / "wrong_icon.mcpack"
    
    # 128x128 is not the expected 256x256 size for pack_icon.png
    wrong_icon = Image.new('RGB', (128, 128))
    
    files = {
        "manifest.json": json.dumps(create_valid_manifest()),
        "pack_icon.png": wrong_icon
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    # Size warning should be present, even if valid remains True (since sizes check adds a warning, not an error)
    assert any("expected 256x256" in warn for warn in result["warnings"])

def test_validation_warning_missing_skins_json(tmp_path):
    mcpack_path = tmp_path / "no_skins_json.mcpack"
    files = {
        "manifest.json": json.dumps(create_valid_manifest()),
        "skins/Skin1.png": Image.new('RGB', (64, 64))
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert any("No skins.json found" in warn for warn in result["warnings"])

# Tier 2 - Boundary & Corner Cases

def test_corrupt_zip(tmp_path):
    mcpack_path = tmp_path / "corrupt.mcpack"
    mcpack_path.write_bytes(b"not a zip file at all")
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is False
    assert any("Validation error" in err or "BadZipFile" in err for err in result["errors"])

def test_invalid_manifest_syntax(tmp_path):
    mcpack_path = tmp_path / "invalid_manifest_syntax.mcpack"
    files = {
        "manifest.json": "{invalid json syntax: true,}",
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is False
    assert any("manifest.json JSON error" in err for err in result["errors"])

def test_missing_manifest_keys(tmp_path):
    mcpack_path = tmp_path / "missing_keys.mcpack"
    # manifest missing 'modules' key
    manifest_data = {
        "format_version": 2,
        "header": {
            "name": "Test",
            "uuid": "uuid",
            "version": [1, 0, 0]
        }
    }
    files = {
        "manifest.json": json.dumps(manifest_data)
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is False
    assert any('manifest.json missing "modules"' in err for err in result["errors"])

def test_missing_skin_texture_warnings(tmp_path):
    mcpack_path = tmp_path / "missing_texture.mcpack"
    # skins.json specifies Skin1.png, but it is not in the pack
    files = {
        "manifest.json": json.dumps(create_valid_manifest()),
        "skins.json": json.dumps(create_valid_skins_json())
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert any("skin texture not found: Skin1.png" in warn for warn in result["warnings"])

def test_non_existent_mcpack_path():
    validator = BedrockValidator()
    result = validator.validate_mcpack("does/not/exist/pack.mcpack")
    
    assert result["valid"] is False
    assert result["errors"] == ["File not found"]
