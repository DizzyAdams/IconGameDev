import os
import json
import zipfile
import pytest
import concurrent.futures
from pathlib import Path
from PIL import Image

from src.utils.uuid_manager import UUIDManager
from src.generators.skin_generator import SkinPackGenerator
from src.generators.texture_generator import TexturePackGenerator
from src.generators.world_generator import WorldTemplateGenerator
from src.validators.bedrock_validator import BedrockValidator
from src.packagers.packager import Packager

# Helper function to build a zip
def build_zip(zip_path, files):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for arcname, content in files.items():
            if isinstance(content, str):
                zf.writestr(arcname, content)
            elif isinstance(content, bytes):
                zf.writestr(arcname, content)
            elif isinstance(content, Image.Image):
                from io import BytesIO
                out = BytesIO()
                icon_format = "PNG" if arcname.endswith(".png") else "JPEG"
                content.save(out, format=icon_format)
                zf.writestr(arcname, out.getvalue())

# Helper to create a valid base manifest structure
def make_manifest(header_uuid="4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e", module_uuid="5c6d7e8f-9a0b-1c2d-3e4f-5a6b7c8d9e0f", mtype="skin_pack"):
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
                "type": mtype,
                "uuid": module_uuid,
                "version": [1, 0, 0]
            }
        ]
    }

# Helper to create valid skins.json
def make_skins_json():
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

# 1. Concurrency and Process Safety Stress Testing

def test_uuid_manager_concurrency_race(tmp_path):
    """
    Adversarially tests process/thread safety of UUIDManager under concurrent load.
    Since there is no file-level or memory locking, concurrent calls to get_or_create
    will cause race conditions on reading/writing registry.json, resulting in lost updates,
    key discrepancies, or JSON decode crashes.
    """
    registry_file = tmp_path / "uuid_registry_race.json"
    manager = UUIDManager(registry_path=str(registry_file))
    
    num_threads = 8
    calls_per_thread = 20
    
    def worker(tid):
        local_manager = UUIDManager(registry_path=str(registry_file))
        uuids = []
        for i in range(calls_per_thread):
            context = f"thread_{tid}_uuid_{i}"
            try:
                val = local_manager.get_or_create(context)
                uuids.append(val)
            except Exception as e:
                uuids.append(e)
        return uuids

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker, i) for i in range(num_threads)]
        results = [f.result() for f in futures]
    
    all_results = []
    exceptions = []
    for r in results:
        for item in r:
            if isinstance(item, Exception):
                exceptions.append(item)
            else:
                all_results.append(item)
                
    try:
        with open(registry_file, "r") as f:
            final_registry = json.load(f)
    except Exception:
        final_registry = {}
        
    expected_keys = num_threads * calls_per_thread
    actual_keys = len(final_registry)
    
    # Under concurrent execution with locking, it is expected that
    # no exceptions are raised, all updates are preserved, and all generated uuids are unique.
    concurrency_failed = (
        len(exceptions) > 0 or 
        actual_keys < expected_keys or 
        len(all_results) != len(set(all_results))
    )
    
    assert not concurrency_failed, (
        f"Concurrency race failed!\n"
        f"Exceptions caught: {len(exceptions)}\n"
        f"Expected keys: {expected_keys}, actual keys saved: {actual_keys}\n"
        f"Total generated: {len(all_results)}, unique: {len(set(all_results))}"
    )

# 2. BedrockValidator Unhandled Exception and Input Validation Crashes

def test_bedrock_validator_manifest_null_header(tmp_path):
    """
    Adversarially tests how BedrockValidator handles a manifest.json where 'header' is null.
    We check that the validator catches this gracefully and reports the pack as invalid.
    """
    mcpack_path = tmp_path / "null_header.mcpack"
    manifest_data = {
        "format_version": 2,
        "header": None,
        "modules": []
    }
    build_zip(mcpack_path, {"manifest.json": json.dumps(manifest_data)})
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is False
    assert any("Validation error" in err or "TypeError" in err for err in result["errors"])

def test_bedrock_validator_manifest_null_modules(tmp_path):
    """
    Adversarially tests how BedrockValidator handles a manifest.json where 'modules' is null.
    """
    mcpack_path = tmp_path / "null_modules.mcpack"
    manifest_data = {
        "format_version": 2,
        "header": {
            "name": "Test Name",
            "uuid": "4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e",
            "version": [1, 0, 0]
        },
        "modules": None
    }
    build_zip(mcpack_path, {"manifest.json": json.dumps(manifest_data)})
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is False
    assert any("Validation error" in err or "TypeError" in err or "missing" in err for err in result["errors"])

def test_bedrock_validator_skins_json_invalid_structure(tmp_path):
    """
    Adversarially tests how BedrockValidator handles skins.json containing non-dictionary entries.
    """
    mcpack_path = tmp_path / "invalid_skins_struct.mcpack"
    skins_data = {
        "skins": [None],
        "serialize_name": "Test Name",
        "localization_name": "Test Name"
    }
    files = {
        "manifest.json": json.dumps(make_manifest(mtype="skin_pack")),
        "skins.json": json.dumps(skins_data)
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is False
    assert any("Validation error" in err or "TypeError" in err for err in result["errors"])

# 3. Gaps in BedrockValidator Validation Suite

def test_bedrock_validator_texture_pack_validation_gap(tmp_path):
    """
    Exposes a critical validation gap in BedrockValidator:
    It completely ignores the block textures themselves inside resource/texture packs.
    We verify that the validator still passes the pack as valid (valid = True) even with
    corrupt block textures or wrong size textures.
    """
    mcpack_path = tmp_path / "gap_texture.mcpack"
    icon = Image.new('RGB', (256, 256), color=(255, 0, 0))
    
    files = {
        "manifest.json": json.dumps(make_manifest(mtype="resources")),
        "pack_icon.png": icon,
        "textures/blocks/stone.png": b"corrupt image data",
        "textures/blocks/dirt.png": Image.new('RGB', (1, 1))
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is True
    assert len(result["errors"]) == 0

def test_bedrock_validator_skin_icon_gap(tmp_path):
    """
    Exposes another validation gap: BedrockValidator does not validate the skin pack's internal icon.png
    (located in textures/skins/icon.png).
    We verify that the validator still passes the pack as valid even with a corrupt skin icon.
    """
    mcpack_path = tmp_path / "gap_skin_icon.mcpack"
    files = {
        "manifest.json": json.dumps(make_manifest(mtype="skin_pack")),
        "skins.json": json.dumps(make_skins_json()),
        "textures/skins/Skin1.png": Image.new('RGB', (64, 64)),
        "textures/skins/icon.png": b"corrupt icon data"
    }
    build_zip(mcpack_path, files)
    
    validator = BedrockValidator()
    result = validator.validate_mcpack(str(mcpack_path))
    
    assert result["valid"] is True
    assert len(result["errors"]) == 0

# 4. Generators Parameter and Input Validation Failures

def test_generator_color_out_of_bounds(tmp_path):
    """
    Adversarially tests SkinPackGenerator with out-of-bounds RGB color values.
    Since there is no input validation, passing values > 255 or < 0 raises
    ValueError during pixel math or PIL image creation.
    """
    output_dir = tmp_path / "skin-packs"
    gen = SkinPackGenerator(registry_path=tmp_path / "registry.json")
    
    skins_high = [("Gojo", (1000, 200, 255), (0, 150, 255))]
    with pytest.raises((ValueError, TypeError)):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="color-high",
            name="Color High",
            desc="Desc",
            skins=skins_high
        )
        
    skins_low = [("Yuji", (-50, 200, 150), (200, 50, 50))]
    with pytest.raises((ValueError, TypeError)):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="color-low",
            name="Color Low",
            desc="Desc",
            skins=skins_low
        )

def test_generator_invalid_texture_size(tmp_path):
    """
    Adversarially tests TexturePackGenerator with invalid texture sizes (<= 0).
    Expected to raise ValueError since PIL image cannot have non-positive dimensions.
    """
    output_dir = tmp_path / "texture-packs"
    gen = TexturePackGenerator(registry_path=tmp_path / "registry.json")
    
    with pytest.raises(ValueError):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="size-zero",
            name="Zero Size",
            desc="Desc",
            modify='identity',
            sz=0,
            noise=5
        )
        
    with pytest.raises(ValueError):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="size-negative",
            name="Negative Size",
            desc="Desc",
            modify='identity',
            sz=-16,
            noise=5
        )

def test_generator_none_inputs(tmp_path):
    """
    Adversarially tests WorldTemplateGenerator with None values for name and description.
    Expected to raise TypeError during text drawing.
    """
    output_dir = tmp_path / "world-templates"
    gen = WorldTemplateGenerator(registry_path=tmp_path / "registry.json")
    
    with pytest.raises(TypeError):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="none-test-name",
            name=None,
            desc="Valid description",
            draw_fn="lifesteal",
            bg=(50, 0, 0)
        )
        
    with pytest.raises(TypeError):
        gen.generate(
            output_dir=output_dir,
            pack_dir_name="none-test-desc",
            name="Valid Name",
            desc=None,
            draw_fn="lifesteal",
            bg=(50, 0, 0)
        )
