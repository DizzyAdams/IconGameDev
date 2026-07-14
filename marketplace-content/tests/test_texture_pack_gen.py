import os
import json
import pytest
import random
from PIL import Image
import texture_pack_gen

# Tier 1 - Feature Coverage

def test_manifest_modules_type(tmp_path, monkeypatch):
    test_pack = {
        'dir': 'test-texture-pack',
        'name': 'Test Texture Pack',
        'desc': 'Test Desc',
        'header_uuid': 'uuid-h',
        'module_uuid': 'uuid-m',
        'modify': lambda c, rng: c,
        'noise_range': 10,
        'icon_label': 'Test',
        'icon_sub': 'Pack',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone'])
    
    texture_pack_gen.generate_pack(test_pack)
    
    manifest_path = tmp_path / 'test-texture-pack' / 'manifest.json'
    assert manifest_path.exists()
    with open(manifest_path) as f:
        data = json.load(f)
        assert data['modules'][0]['type'] == 'resources'

def test_icon_dimensions(tmp_path, monkeypatch):
    test_pack = {
        'dir': 'icon-test-pack',
        'name': 'Icon Test',
        'desc': 'Test',
        'header_uuid': 'h',
        'module_uuid': 'm',
        'modify': lambda c, rng: c,
        'noise_range': 5,
        'icon_label': 'I',
        'icon_sub': 'T',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['dirt'])
    
    texture_pack_gen.generate_pack(test_pack)
    icon_path = tmp_path / 'icon-test-pack' / 'pack_icon.png'
    assert icon_path.exists()
    with Image.open(icon_path) as img:
        assert img.size == (256, 256)

def test_block_texture_dimensions(tmp_path, monkeypatch):
    test_pack = {
        'dir': 'block-test-pack',
        'name': 'Block Test',
        'desc': 'Test',
        'header_uuid': 'h',
        'module_uuid': 'm',
        'modify': lambda c, rng: c,
        'noise_range': 5,
        'icon_label': 'B',
        'icon_sub': 'T',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['granite'])
    
    texture_pack_gen.generate_pack(test_pack)
    block_path = tmp_path / 'block-test-pack' / 'textures' / 'blocks' / 'granite.png'
    assert block_path.exists()
    with Image.open(block_path) as img:
        assert img.size == (32, 32)

def test_standard_blocks_list(tmp_path, monkeypatch):
    test_pack = {
        'dir': 'standard-blocks-pack',
        'name': 'Standard Blocks Test',
        'desc': 'Test',
        'header_uuid': 'h',
        'module_uuid': 'm',
        'modify': lambda c, rng: c,
        'noise_range': 5,
        'icon_label': 'S',
        'icon_sub': 'T',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    # Generate all block names
    texture_pack_gen.generate_pack(test_pack)
    
    blocks_dir = tmp_path / 'standard-blocks-pack' / 'textures' / 'blocks'
    for name in texture_pack_gen.BLOCK_NAMES:
        assert (blocks_dir / f'{name}.png').exists()

def test_folder_structure(tmp_path, monkeypatch):
    test_pack = {
        'dir': 'struct-pack',
        'name': 'Struct Test',
        'desc': 'Test',
        'header_uuid': 'h',
        'module_uuid': 'm',
        'modify': lambda c, rng: c,
        'noise_range': 5,
        'icon_label': 'S',
        'icon_sub': 'T',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone'])
    
    texture_pack_gen.generate_pack(test_pack)
    
    pack_dir = tmp_path / 'struct-pack'
    assert pack_dir.exists()
    assert (pack_dir / 'manifest.json').exists()
    assert (pack_dir / 'pack_icon.png').exists()
    assert (pack_dir / 'textures' / 'blocks').exists()
    assert (pack_dir / 'textures' / 'blocks' / 'stone.png').exists()

# Tier 2 - Boundary & Corner Cases

def test_custom_block_palette(tmp_path, monkeypatch):
    custom_colors = {
        'custom_brick': (200, 100, 50),
        'custom_obsidian': (10, 20, 30)
    }
    test_pack = {
        'dir': 'custom-palette-pack',
        'name': 'Custom Palette',
        'desc': 'Test',
        'header_uuid': 'h',
        'module_uuid': 'm',
        'modify': lambda c, rng: c,
        'noise_range': 5,
        'icon_label': 'C',
        'icon_sub': 'P',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_COLORS", custom_colors)
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", list(custom_colors.keys()))
    
    texture_pack_gen.generate_pack(test_pack)
    
    blocks_dir = tmp_path / 'custom-palette-pack' / 'textures' / 'blocks'
    assert (blocks_dir / 'custom_brick.png').exists()
    assert (blocks_dir / 'custom_obsidian.png').exists()

def test_extreme_darkness_factors():
    color = (100, 150, 200)
    # Factor = 0.0 -> all 0s
    assert texture_pack_gen.darken(color, 0.0) == (0, 0, 0)
    # Factor = 10.0 -> all 255s
    assert texture_pack_gen.darken(color, 10.0) == (255, 255, 255)
    # Factor = -1.0 -> all 0s
    assert texture_pack_gen.darken(color, -1.0) == (0, 0, 0)

def test_custom_noise_ranges():
    rng = random.Random(42)
    # Range = 0 -> output exactly matching base color
    img_no_noise = texture_pack_gen.make_noise_image('stone', (128, 128, 128), 16, rng, noise_range=0)
    assert img_no_noise.size == (16, 16)
    # Verify pixels are very close or identical to (128, 128, 128)
    # Note that make_noise_image has local random seeds, but since range is 0,
    # the noise and rn/gn/bn additions are 0.
    pix = img_no_noise.load()
    assert pix[0, 0] == (128, 128, 128)
    
    # Range = 1000 -> extreme noise, but pixels should remain bounded in 0..255
    img_high_noise = texture_pack_gen.make_noise_image('stone', (128, 128, 128), 16, rng, noise_range=1000)
    pix_high = img_high_noise.load()
    for x in range(16):
        for y in range(16):
            r, g, b = pix_high[x, y]
            assert 0 <= r <= 255
            assert 0 <= g <= 255
            assert 0 <= b <= 255

def test_empty_palettes(tmp_path, monkeypatch):
    test_pack = {
        'dir': 'empty-palette-pack',
        'name': 'Empty Palette',
        'desc': 'Test',
        'header_uuid': 'h',
        'module_uuid': 'm',
        'modify': lambda c, rng: c,
        'noise_range': 5,
        'icon_label': 'E',
        'icon_sub': 'P',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_COLORS", {})
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", [])
    
    # Running should not fail, should write manifest and pack icon
    texture_pack_gen.generate_pack(test_pack)
    
    pack_dir = tmp_path / 'empty-palette-pack'
    assert (pack_dir / 'manifest.json').exists()
    assert (pack_dir / 'pack_icon.png').exists()
    assert len(os.listdir(pack_dir / 'textures' / 'blocks')) == 0

def test_write_locked_directories(tmp_path, monkeypatch):
    # Pass an invalid or uncreatable directory path to test how OS errors are handled
    test_pack = {
        'dir': 'invalid_dir\0_name', # Null byte will raise OSError on Windows/Unix
        'name': 'Invalid Dir Name',
        'desc': 'Test',
        'header_uuid': 'h',
        'module_uuid': 'm',
        'modify': lambda c, rng: c,
        'noise_range': 5,
        'icon_label': 'I',
        'icon_sub': 'D',
    }
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone'])
    
    with pytest.raises((OSError, ValueError)):
        texture_pack_gen.generate_pack(test_pack)
