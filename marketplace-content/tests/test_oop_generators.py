import json
import zipfile
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

def test_skin_pack_generator_oop(tmp_path):
    output_dir = tmp_path / "skin-packs"
    gen = SkinPackGenerator(registry_path=tmp_path / "registry.json")
    
    skins = [
        ("Gojo", (200, 200, 255), (0, 150, 255)),
        ("Yuji", (255, 200, 150), (200, 50, 50))
    ]
    pack_dir = gen.generate(
        output_dir=output_dir,
        pack_dir_name="jujutsu-test",
        name="Jujutsu Test Pack",
        desc="Description here",
        skins=skins
    )
    
    assert pack_dir.exists()
    assert (pack_dir / "manifest.json").exists()
    assert (pack_dir / "skins.json").exists()
    
    # Check skin texture dimensions
    skin_file = pack_dir / "textures" / "skins" / "Gojo.png"
    assert skin_file.exists()
    with Image.open(skin_file) as img:
        assert img.size == (64, 64)
        
    icon_file = pack_dir / "textures" / "skins" / "icon.png"
    assert icon_file.exists()
    with Image.open(icon_file) as img:
        assert img.size == (300, 300)

def test_texture_pack_generator_oop(tmp_path):
    output_dir = tmp_path / "texture-packs"
    gen = TexturePackGenerator(registry_path=tmp_path / "registry.json")
    
    pack_dir = gen.generate(
        output_dir=output_dir,
        pack_dir_name="retro-test",
        name="Retro Test Pack",
        desc="Description here",
        modify='identity',
        sz=16,
        noise=5
    )
    
    assert pack_dir.exists()
    assert (pack_dir / "manifest.json").exists()
    assert (pack_dir / "pack_icon.png").exists()
    
    with Image.open(pack_dir / "pack_icon.png") as img:
        assert img.size == (256, 256)
        
    # Check a block texture dimensions
    stone_file = pack_dir / "textures" / "blocks" / "stone.png"
    assert stone_file.exists()
    with Image.open(stone_file) as img:
        assert img.size == (16, 16)

def test_world_template_generator_oop(tmp_path):
    output_dir = tmp_path / "world-templates"
    gen = WorldTemplateGenerator(registry_path=tmp_path / "registry.json")
    
    pack_dir = gen.generate(
        output_dir=output_dir,
        pack_dir_name="lifesteal-test",
        name="Lifesteal SMP",
        desc="Lifesteal description",
        draw_fn="lifesteal",
        bg=(50, 0, 0)
    )
    
    assert pack_dir.exists()
    assert (pack_dir / "manifest.json").exists()
    assert (pack_dir / "level.dat").exists()
    assert (pack_dir / "world_icon.png").exists()
    assert (pack_dir / "thumbnail.png").exists()
    
    with Image.open(pack_dir / "world_icon.png") as img:
        assert img.size == (256, 256)
        
    with Image.open(pack_dir / "thumbnail.png") as img:
        assert img.size == (300, 300)

def test_mashup_pack_generator_oop(tmp_path):
    output_dir = tmp_path / "mashup-packs"
    gen = MashupPackGenerator(registry_path=tmp_path / "registry.json")
    
    skins = [("Skin1", (255, 0, 0), (0, 255, 0))]
    pack_dir = gen.generate(
        output_dir=output_dir,
        pack_dir_name="mashup-test",
        name="Mashup Test",
        desc="Mashup desc",
        world_draw_fn="spawn_hub",
        world_bg=(50, 50, 100),
        skins=skins,
        texture_modify="identity",
        texture_sz=32,
        texture_noise=10
    )
    
    assert pack_dir.exists()
    assert (pack_dir / "manifest.json").exists()
    assert (pack_dir / "level.dat").exists()
    assert (pack_dir / "world_icon.png").exists()
    assert (pack_dir / "pack_icon.png").exists()
    assert (pack_dir / "skins.json").exists()
    assert (pack_dir / "textures" / "skins" / "Skin1.png").exists()
    assert (pack_dir / "textures" / "blocks" / "stone.png").exists()
    
    with open(pack_dir / "manifest.json") as f:
        m = json.load(f)
        assert m.get("metadata", {}).get("product_type") == "mashup"

def test_packager_and_bedrock_validator(tmp_path):
    output_dir = tmp_path / "builds"
    dist_dir = tmp_path / "dist"
    
    # 1. World Template pack
    w_gen = WorldTemplateGenerator(registry_path=tmp_path / "registry.json")
    w_dir = w_gen.generate(output_dir, "my-world", "My World", "Desc", "kitpvp", (50,50,50))
    
    # 2. Mashup Pack
    m_gen = MashupPackGenerator(registry_path=tmp_path / "registry.json")
    m_dir = m_gen.generate(
        output_dir, "my-mashup", "My Mashup", "Desc", "kitpvp", (50,50,50),
        [("Skin1", (0,0,0), (255,255,255))], "identity", 32, 10
    )
    
    # Package using Packager
    w_zip = Packager.package(w_dir, dist_dir)
    m_zip = Packager.package(m_dir, dist_dir)
    
    assert w_zip.suffix == ".mctemplate"
    assert m_zip.suffix == ".mcpack"
    
    # Validate
    validator = BedrockValidator()
    results = validator.validate_all(dist_dir)
    
    assert len(results) == 2
    for r in results:
        assert r["valid"] is True
        assert len(r["errors"]) == 0

def test_uuid_local_and_global_collisions(tmp_path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    
    # Create two zip files with the same UUID in manifest
    manifest_data = {
        "format_version": 2,
        "header": {
            "name": "Pack 1",
            "description": "Desc",
            "uuid": "colliding-uuid-value",
            "version": [1, 0, 0]
        },
        "modules": [
            {
                "type": "resources",
                "uuid": "module-uuid-1",
                "version": [1, 0, 0]
            }
        ]
    }
    
    # Write pack 1
    p1 = tmp_path / "p1"
    p1.mkdir()
    with open(p1 / "manifest.json", "w") as f:
        json.dump(manifest_data, f)
    (p1 / "pack_icon.png").write_text("icon")
    
    # Write pack 2 (same header UUID)
    manifest_data_2 = manifest_data.copy()
    manifest_data_2["header"] = manifest_data["header"].copy()
    manifest_data_2["header"]["name"] = "Pack 2"
    p2 = tmp_path / "p2"
    p2.mkdir()
    with open(p2 / "manifest.json", "w") as f:
        json.dump(manifest_data_2, f)
    (p2 / "pack_icon.png").write_text("icon")
    
    # Package
    zip1 = Packager.package(p1, dist_dir)
    zip2 = Packager.package(p2, dist_dir)
    
    validator = BedrockValidator()
    results = validator.validate_all(dist_dir)
    
    # Check that they both fail due to global collision
    assert len(results) == 2
    for r in results:
        assert r["valid"] is False
        assert any("Global UUID collision" in err for err in r["errors"])

def test_bulk_ingestor_parallel(tmp_path):
    output_dir = tmp_path / "output"
    dist_dir = tmp_path / "dist"
    registry_path = tmp_path / "registry.json"
    
    ingestor = BulkIngestor(output_dir, dist_dir, registry_path)
    # Generate a small bulk workload of 20 skins, 10 skins per pack -> 2 volumes
    results, val_results = ingestor.run(num_skins=20, skins_per_pack=10)
    
    assert len(results) == 2
    assert (dist_dir / "skin-pack-vol-1.mcpack").exists()
    assert (dist_dir / "skin-pack-vol-2.mcpack").exists()
    
    assert len(val_results) == 2
    for r in val_results:
        assert r["valid"] is True
