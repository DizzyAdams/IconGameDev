import os
import json
import pytest
import random
from PIL import Image
import texture_pack_gen

# Helper: build a valid test pack dict with the fields the current generate_pack needs.
def _make_test_pack(dir_name, name='Test', desc='Test', **overrides):
    pack = {
        'dir': dir_name,
        'name': name,
        'desc': desc,
        'header_uuid': 'h',
        'module_uuid': 'm',
        'modify': lambda c, rng: c,
        'noise_range': 5,
        'icon_label': name[0],
        'icon_sub': 'T',
        'seed': 42,
        'tile_size': 32,
    }
    pack.update(overrides)
    return pack

# Tier 1 - Feature Coverage

def test_manifest_modules_type(tmp_path, monkeypatch):
    test_pack = _make_test_pack('test-texture-pack', 'Test Texture Pack', 'Test Desc', noise_range=10)
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone'])
    
    texture_pack_gen.generate_pack(test_pack, 0, 1)
    
    manifest_path = tmp_path / 'test-texture-pack' / 'manifest.json'
    assert manifest_path.exists()
    with open(manifest_path) as f:
        data = json.load(f)
        assert data['modules'][0]['type'] == 'resources'

def test_icon_dimensions(tmp_path, monkeypatch):
    test_pack = _make_test_pack('icon-test-pack', 'Icon Test')
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['dirt'])
    
    texture_pack_gen.generate_pack(test_pack, 0, 1)
    icon_path = tmp_path / 'icon-test-pack' / 'pack_icon.png'
    assert icon_path.exists()
    with Image.open(icon_path) as img:
        assert img.size == (256, 256)

def test_block_texture_dimensions(tmp_path, monkeypatch):
    test_pack = _make_test_pack('block-test-pack', 'Block Test')
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['granite'])
    
    texture_pack_gen.generate_pack(test_pack, 0, 1)
    block_path = tmp_path / 'block-test-pack' / 'textures' / 'blocks' / 'granite.png'
    assert block_path.exists()
    with Image.open(block_path) as img:
        assert img.size == (32, 32)

def test_standard_blocks_list(tmp_path, monkeypatch):
    test_pack = _make_test_pack('standard-blocks-pack', 'Standard Blocks Test')
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    # Generate all block names
    texture_pack_gen.generate_pack(test_pack, 0, 1)
    
    blocks_dir = tmp_path / 'standard-blocks-pack' / 'textures' / 'blocks'
    for name in texture_pack_gen.BLOCK_NAMES:
        assert (blocks_dir / f'{name}.png').exists()

def test_folder_structure(tmp_path, monkeypatch):
    test_pack = _make_test_pack('struct-pack', 'Struct Test')
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone'])
    
    texture_pack_gen.generate_pack(test_pack, 0, 1)
    
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
    test_pack = _make_test_pack('custom-palette-pack', 'Custom Palette')
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_COLORS", custom_colors)
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", list(custom_colors.keys()))
    
    texture_pack_gen.generate_pack(test_pack, 0, 1)
    
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
    test_pack = _make_test_pack('empty-palette-pack', 'Empty Palette')
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_COLORS", {})
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", [])
    
    # Running should not fail, should write manifest and pack icon
    texture_pack_gen.generate_pack(test_pack, 0, 1)
    
    pack_dir = tmp_path / 'empty-palette-pack'
    assert (pack_dir / 'manifest.json').exists()
    assert (pack_dir / 'pack_icon.png').exists()
    assert len(os.listdir(pack_dir / 'textures' / 'blocks')) == 0

def test_write_locked_directories(tmp_path, monkeypatch):
    # Pass an invalid or uncreatable directory path to test how OS errors are handled
    test_pack = _make_test_pack('invalid_dir\0_name', 'Invalid Dir Name')
    monkeypatch.setattr(texture_pack_gen, "BASE", str(tmp_path))
    monkeypatch.setattr(texture_pack_gen, "BLOCK_NAMES", ['stone'])
    
    with pytest.raises((OSError, ValueError)):
        texture_pack_gen.generate_pack(test_pack, 0, 1)
