import os
import json
import zipfile
import tempfile
import pytest
from pathlib import Path
from PIL import Image

from src.generators.skin_generator import SkinPackGenerator
from src.generators.texture_generator import TexturePackGenerator
from src.generators.world_generator import WorldTemplateGenerator
from src.generators.mashup_generator import MashupPackGenerator
from src.generators.bulk_ingestor import BulkIngestor
from src.packagers.packager import Packager
from src.validators.bedrock_validator import BedrockValidator
from src.utils.uuid_manager import UUIDManager

# ---------------------------------------------------------
# 1. BEDROCK VALIDATION SCHEMAS & UNHANDLED TYPE EXCEPTIONS
# ---------------------------------------------------------

def test_bedrock_validator_manifest_header_type_error(tmp_path):
    """Test that BedrockValidator handles non-dict 'header' fields gracefully."""
    mcpack_path = tmp_path / "header_string.mcpack"
    manifest_content = {
        "format_version": 2,
        "header": "not-a-dict-but-a-string",  # Invalid type
        "modules": []
    }
    
    with zipfile.ZipFile(mcpack_path, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest_content))
        
    validator = BedrockValidator()
    res = validator.validate_mcpack(str(mcpack_path))
    assert res["valid"] is False
    assert any("Validation error" in err or "TypeError" in err or "attribute" in err for err in res["errors"])


def test_bedrock_validator_manifest_modules_type_error(tmp_path):
    """Test that BedrockValidator handles non-list 'modules' fields gracefully."""
    mcpack_path = tmp_path / "modules_dict.mcpack"
    manifest_content = {
        "format_version": 2,
        "header": {
            "name": "Pack",
            "uuid": "header-uuid",
            "version": [1, 0, 0]
        },
        "modules": {"module": "not-a-list-but-a-dict"}  # Invalid type
    }
    
    with zipfile.ZipFile(mcpack_path, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest_content))
        
    validator = BedrockValidator()
    res = validator.validate_mcpack(str(mcpack_path))
    assert res["valid"] is False
    assert any("Validation error" in err or "TypeError" in err or "attribute" in err for err in res["errors"])


def test_bedrock_validator_manifest_module_element_type_error(tmp_path):
    """Test that BedrockValidator handles non-dict elements in the 'modules' array."""
    mcpack_path = tmp_path / "module_element.mcpack"
    manifest_content = {
        "format_version": 2,
        "header": {
            "name": "Pack",
            "uuid": "header-uuid",
            "version": [1, 0, 0]
        },
        "modules": [12345]  # Invalid element type
    }
    
    with zipfile.ZipFile(mcpack_path, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest_content))
        
    validator = BedrockValidator()
    res = validator.validate_mcpack(str(mcpack_path))
    assert res["valid"] is False
    assert any("Validation error" in err or "TypeError" in err or "attribute" in err for err in res["errors"])


def test_bedrock_validator_skins_json_type_error(tmp_path):
    """Test that BedrockValidator handles non-dict skins.json files gracefully."""
    mcpack_path = tmp_path / "skins_json_list.mcpack"
    manifest_content = {
        "format_version": 2,
        "header": {
            "name": "Skin Pack",
            "uuid": "header-uuid",
            "version": [1, 0, 0]
        },
        "modules": [
            {
                "type": "skin_pack",
                "uuid": "module-uuid",
                "version": [1, 0, 0]
            }
        ]
    }
    skins_content = ["not-a-dict-but-a-list"]  # Invalid type
    
    with zipfile.ZipFile(mcpack_path, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest_content))
        zf.writestr("skins.json", json.dumps(skins_content))
        
    validator = BedrockValidator()
    res = validator.validate_mcpack(str(mcpack_path))
    assert res["valid"] is False
    assert any("Validation error" in err or "TypeError" in err or "attribute" in err or "skins.json" in err for err in res["errors"])


def test_bedrock_validator_skins_array_element_type_error(tmp_path):
    """Test that BedrockValidator handles non-dict elements inside the skins.json skins array."""
    mcpack_path = tmp_path / "skins_array_element.mcpack"
    manifest_content = {
        "format_version": 2,
        "header": {
            "name": "Skin Pack",
            "uuid": "header-uuid",
            "version": [1, 0, 0]
        },
        "modules": [
            {
                "type": "skin_pack",
                "uuid": "module-uuid",
                "version": [1, 0, 0]
            }
        ]
    }
    skins_content = {
        "skins": [12345]  # Invalid element type
    }
    
    with zipfile.ZipFile(mcpack_path, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest_content))
        zf.writestr("skins.json", json.dumps(skins_content))
        
    validator = BedrockValidator()
    res = validator.validate_mcpack(str(mcpack_path))
    assert res["valid"] is False
    assert any("Validation error" in err or "TypeError" in err or "attribute" in err for err in res["errors"])


# ---------------------------------------------------------
# 2. PATH TRAVERSAL (ZIP SLIP & GENERATOR EXPOSURE)
# ---------------------------------------------------------

def test_bedrock_validator_zip_slip_vulnerability(tmp_path, monkeypatch):
    """Test that BedrockValidator detects/prevents Zip Slip path traversal."""
    extract_base = tmp_path / "extract_base"
    extract_base.mkdir()
    
    # Mock mkdtemp to force extraction within a target folder
    def mock_mkdtemp(*args, **kwargs):
        d = extract_base / "target_extract"
        d.mkdir(exist_ok=True)
        return str(d)
        
    monkeypatch.setattr(tempfile, "mkdtemp", mock_mkdtemp)
    
    mcpack_path = tmp_path / "slip_attack.mcpack"
    with zipfile.ZipFile(mcpack_path, "w") as zf:
        # Attempt to write a file one level above target_extract (inside extract_base)
        zf.writestr("../escaped_file.txt", "malicious payload")
        zf.writestr("manifest.json", json.dumps({}))
        
    validator = BedrockValidator()
    validator.validate_mcpack(str(mcpack_path))
    
    escaped_file = extract_base / "escaped_file.txt"
    # Expose vulnerability: if this file exists, Zip Slip path traversal was successful
    assert not escaped_file.exists(), "Vulnerability found: Zip Slip path traversal allowed!"


def test_skin_generator_path_traversal_vulnerability(tmp_path):
    """Test that SkinPackGenerator prevents path traversal via skin names."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    gen = SkinPackGenerator(registry_path=tmp_path / "registry.json")
    
    # Name contains traversal components attempting to write outside skins directory
    skins = [
        ("../../../escaped_skin", (255, 0, 0), (0, 255, 0))
    ]
    
    pack_dir = gen.generate(
        output_dir=output_dir,
        pack_dir_name="skin-pack",
        name="Skin Pack",
        desc="Description",
        skins=skins
    )
    
    escaped_file = output_dir / "escaped_skin.png"
    # Expose vulnerability: if this file exists, SkinPackGenerator is vulnerable
    assert not escaped_file.exists(), "Vulnerability found: SkinPackGenerator allowed path traversal!"


# ---------------------------------------------------------
# 3. TEXTURE GENERATOR DIMENSION BOUNDARIES & TYPE FAILURES
# ---------------------------------------------------------

def test_texture_generator_invalid_dimensions(tmp_path):
    """Test that TexturePackGenerator raises ValueError on zero or negative dimensions."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    gen = TexturePackGenerator(registry_path=tmp_path / "registry.json")
    
    with pytest.raises(ValueError):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="tex-pack-zero",
            name="Texture Pack",
            desc="Description",
            modify="identity",
            sz=0,
            noise=5
        )

    with pytest.raises(ValueError):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="tex-pack-neg",
            name="Texture Pack",
            desc="Description",
            modify="identity",
            sz=-16,
            noise=5
        )


def test_texture_generator_invalid_modify_fallback(tmp_path):
    """Test that TexturePackGenerator falls back to identity when modify is not valid/callable."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    gen = TexturePackGenerator(registry_path=tmp_path / "registry.json")
    
    pack_dir = gen.generate(
        output_dir=output_dir,
        pack_dir_name="tex-pack-modify",
        name="Texture Pack",
        desc="Description",
        modify=12345,  # Invalid modify mapping
        sz=16,
        noise=5
    )
    
    assert pack_dir.exists()
    assert (pack_dir / "textures" / "blocks" / "stone.png").exists()


def test_texture_generator_invalid_noise_type(tmp_path):
    """Test that TexturePackGenerator raises TypeError when noise is not numeric."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    gen = TexturePackGenerator(registry_path=tmp_path / "registry.json")
    
    with pytest.raises(TypeError):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="tex-pack-noise",
            name="Texture Pack",
            desc="Description",
            modify="identity",
            sz=16,
            noise="invalid-noise-string"
        )


# ---------------------------------------------------------
# 4. UUIDMANAGER ROBUSTNESS
# ---------------------------------------------------------

def test_uuid_manager_corrupt_registry(tmp_path):
    """Test that UUIDManager recovers from corrupt registry.json gracefully."""
    registry_file = tmp_path / "corrupt_registry.json"
    registry_file.write_text("invalid json data {", encoding="utf-8")
    
    manager = UUIDManager(registry_path=str(registry_file))
    val = manager.get_or_create("context_1")
    assert val is not None


def test_uuid_manager_missing_directory_auto_create(tmp_path):
    """Test that UUIDManager auto-creates the registry parent directories if missing."""
    registry_file = tmp_path / "nested_dir" / "new_registry.json"
    manager = UUIDManager(registry_path=str(registry_file))
    
    uuid_val = manager.get_or_create("context_1")
    assert uuid_val is not None
    assert registry_file.exists()


# ---------------------------------------------------------
# 5. BULK INGESTOR CHUNK SIZE BOUNDARIES
# ---------------------------------------------------------

def test_bulk_ingestor_invalid_chunk_size(tmp_path):
    """Test that BulkIngestor raises ValueError when skins_per_pack is 0."""
    output_dir = tmp_path / "output"
    dist_dir = tmp_path / "dist"
    registry_path = tmp_path / "registry.json"
    
    ingestor = BulkIngestor(output_dir, dist_dir, registry_path)
    
    with pytest.raises(ValueError) as excinfo:
        ingestor.run(num_skins=10, skins_per_pack=0)
    assert "must not be zero" in str(excinfo.value)


# ---------------------------------------------------------
# 6. PACKAGER PATH LOGIC
# ---------------------------------------------------------

def test_packager_package_file_instead_of_dir(tmp_path):
    """Test that Packager handling of a single file instead of folder doesn't crash."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    some_file = tmp_path / "not_a_directory.txt"
    some_file.write_text("hello", encoding="utf-8")
    
    archive_path = Packager.package(some_file, output_dir)
    assert archive_path.exists()
    with zipfile.ZipFile(archive_path, "r") as zf:
        assert len(zf.namelist()) == 0
