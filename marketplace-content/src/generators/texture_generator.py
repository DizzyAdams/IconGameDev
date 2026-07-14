import os
import json
import math
import random
from pathlib import Path
from PIL import Image

from src.generators.base_generator import BaseGenerator

BLOCK_COLORS = {
    'stone': (140,140,135), 'granite': (160,130,120), 'diorite': (180,175,170), 'andesite': (135,130,125),
    'grass_top': (90,175,65), 'grass_side': (110,150,75), 'dirt': (130,95,60), 'podzol': (100,75,45),
    'sand': (215,200,150), 'red_sand': (190,120,70), 'gravel': (145,135,125),
    'cobblestone': (120,115,110), 'mossy_cobblestone': (110,125,100), 'brick': (165,85,65), 'stone_brick': (135,130,125),
    'wood_oak': (155,125,75), 'wood_spruce': (85,65,45), 'wood_birch': (195,180,145), 'wood_jungle': (140,100,60),
    'wood_acacia': (160,100,55), 'wood_dark_oak': (60,45,30),
    'planks_oak': (185,155,95), 'planks_spruce': (110,85,55), 'planks_birch': (205,190,155), 'planks_jungle': (165,120,70),
    'planks_acacia': (175,110,60), 'planks_dark_oak': (70,55,40),
    'water_still': (50,80,180), 'water_flow': (45,75,170), 'lava_still': (225,110,25), 'lava_flow': (210,95,20),
    'gold_block': (255,215,0), 'iron_block': (200,200,210), 'diamond_block': (80,200,210), 'emerald_block': (50,205,85),
    'redstone_block': (185,20,20), 'coal_block': (35,35,35), 'obsidian': (20,15,35), 'netherrack': (130,30,30), 'end_stone': (210,200,160),
}

# Modifiers
def _mod_grid(img, sz, _, rng=None):
    pix, div, dark = img.load(), 4, 20
    cell = sz // div
    for x in range(sz):
        for y in range(sz):
            if x % cell == 0 or y % cell == 0:
                r,g,b = pix[x,y]
                pix[x,y] = (max(0,r-dark),max(0,g-dark),max(0,b-dark))

def _mod_stripes(img, sz, _, rng=None):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            if y % 8 == 0 or y % 8 == 1:
                r,g,b = pix[x,y]
                pix[x,y] = (max(0,r-15),max(0,g-15),max(0,b-15))

def _mod_moss(img, sz, _, rng):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'_{x}_{y}')&0xFFFFFFFF)
            if rng.random() < 0.25:
                r,g,b = pix[x,y]
                m=(70,130,60)
                pix[x,y] = tuple(max(0,min(255,int(c*0.6+m[i]*0.4)+rng.randint(-10,10))) for i,c in enumerate((r,g,b)))

def _mod_wave(img, sz, _, rng=None):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            r,g,b = pix[x,y]
            w = int(6*math.sin(x*0.5+y*0.3))
            pix[x,y] = (max(0,min(255,r+w)),max(0,min(255,g+w)),max(0,min(255,b+w)))

def _mod_glow(img, sz, _, rng):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            r,g,b = pix[x,y]
            br = rng.randint(-20,20)
            pix[x,y] = (max(0,min(255,r+br)),max(0,min(255,g+br//2)),max(0,min(255,b+br//3)))

def _mod_sparkle(img, sz, _, rng, amt=40):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'_{x}_{y}')&0xFFFFFFFF)
            if rng.random() < 0.08:
                r,g,b = pix[x,y]
                pix[x,y] = (min(255,r+amt),min(255,g+amt),min(255,b+amt))

def _mod_sheen(img, sz, _, rng):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'_{x}_{y}')&0xFFFFFFFF)
            if rng.random() < 0.1:
                r,g,b = pix[x,y]
                pix[x,y] = (min(255,r+15),min(255,g+15),min(255,b+15))

def _mod_grass(img, sz, _, rng):
    pix, top = img.load(), (90,175,65)
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'_{x}_{y}')&0xFFFFFFFF)
            t = y/sz
            if t < 0.25: c = top
            elif t < 0.4:
                bl = (t-0.25)/0.15
                c = tuple(int(top[i]*(1-bl)+pix[x,y][i]*bl) for i in range(3))
            else: c = pix[x,y]
            n = rng.randint(-15,15)
            pix[x,y] = tuple(max(0,min(255,c[i]+n)) for i in range(3))

def _mod_ember(img, sz, _, rng):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'_{x}_{y}')&0xFFFFFFFF)
            if rng.random() < 0.06:
                r,g,b = pix[x,y]
                pix[x,y] = (min(255,r+50),max(0,g-10),max(0,b-10))

TEX_MODIFIERS = {
    'stone_brick': _mod_grid, 'planks_oak': _mod_stripes, 'planks_spruce': _mod_stripes,
    'planks_birch': _mod_stripes, 'planks_jungle': _mod_stripes, 'planks_acacia': _mod_stripes,
    'planks_dark_oak': _mod_stripes, 'mossy_cobblestone': _mod_moss, 'water_still': _mod_wave,
    'water_flow': _mod_wave, 'lava_still': _mod_glow, 'lava_flow': _mod_glow,
    'gold_block': _mod_sparkle, 'diamond_block': _mod_sparkle, 'emerald_block': _mod_sparkle,
    'obsidian': _mod_sheen, 'netherrack': _mod_ember, 'grass_side': _mod_grass,
}

# Color modification functions
def identity(c, _=None): return c
def pastelize(c, _=None): return tuple(max(0,min(255,int(v*0.7+100))) for v in c)
def neonize(c, _=None): return tuple(max(0,min(255,int(v*1.3+30))) for v in c)
def sepiafy(c, _=None):
    g = int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g*1.1,g*0.95,g*0.8))
def gothify(c, _=None): return tuple(max(0,min(255,int(v*0.5-20))) for v in c)
def animefy(c, _=None): return tuple(max(0,min(255,int(v*0.8+50))) for v in c)
def cartoonify(c, _=None):
    g = int(c[0]*0.299+c[1]*0.587+c[2]*0.114)
    return tuple(max(0,min(255,int(v))) for v in (g+80,g+60,g+40))
def comicfy(c, _=None):
    g = int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g,g//2,g//3))
def watercolor(c, rng):
    return tuple(max(0,min(255,int(v*0.6+80+rng.randint(-10,10)))) for v in c)
def realistic(c, rng):
    return tuple(max(0,min(255,int(v*0.9+rng.randint(-15,15)))) for v in c)
def barebone(c, _=None):
    g = int(c[0]*0.299+c[1]*0.587+c[2]*0.114)
    return (g,g,g)
def default_plus(c, _=None):
    return tuple(max(0,min(255,int(v*1.15))) for v in c)
def pvp_opt(c, _=None):
    g = int(c[0]*0.299+c[1]*0.587+c[2]*0.114)
    return (g*2,g,g-g//3)
def skyify(c, _=None):
    return tuple(max(0,min(255,int(v*0.5+120))) for v in c)

def urban_mod(c, _=None):
    g=int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g+30,g+20,g+10))
def rustic_mod(c, _=None):
    return tuple(max(0,min(255,int(v*0.8+50))) for v in c)
def fantasy_mod(c, _=None):
    g=int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g+50,g+20,g+60))
def faithful_32_mod(c, _=None):
    return tuple(max(0,min(255,int(v*1.1+5))) for v in c)
def smooth_glass_mod(c, _=None):
    return tuple(max(0,min(255,int(v*0.8+50))) for v in c)
def vibrant_mod(c, _=None):
    return tuple(max(0,min(255,int(v*1.3))) for v in c)
def winter_mod(c, _=None):
    g=int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g+40,g+40,g+60))
def nether_mod(c, _=None):
    return tuple(max(0,min(255,int(v*1.2+20))) for v in c)
def end_mod(c, _=None):
    g=int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g-20,g,g+40))
def warm_mod(c, _=None):
    return tuple(max(0,min(255,int(v*1.1+15))) for v in c)

MODIFY_FUNCTIONS = {
    'identity': identity, 'pastelize': pastelize, 'neonize': neonize, 'sepiafy': sepiafy,
    'gothify': gothify, 'animefy': animefy, 'cartoonify': cartoonify, 'comicfy': comicfy,
    'watercolor': watercolor, 'realistic': realistic, 'barebone': barebone, 'default_plus': default_plus,
    'pvp_opt': pvp_opt, 'skyify': skyify, 'urban_mod': urban_mod, 'rustic_mod': rustic_mod,
    'fantasy_mod': fantasy_mod, 'faithful_32_mod': faithful_32_mod, 'smooth_glass_mod': smooth_glass_mod,
    'vibrant_mod': vibrant_mod, 'winter_mod': winter_mod, 'nether_mod': nether_mod,
    'end_mod': end_mod, 'warm_mod': warm_mod
}

class TexturePackGenerator(BaseGenerator):
    def _noise_tex(self, name: str, color: tuple, sz: int, rng: random.Random, noise: int = 18) -> Image.Image:
        img = Image.new('RGB', (sz, sz))
        pix = img.load()
        for x in range(sz):
            for y in range(sz):
                rng.seed(hash(f'{name}_{x}_{y}') & 0xFFFFFFFF)
                pix[x,y] = tuple(max(0,min(255,c+rng.randint(-noise,noise))) for c in color)
        return img

    def generate(self, output_dir: Path, pack_dir_name: str, name: str, desc: str, modify, sz: int, noise: int) -> Path:
        """
        Generates a block texture pack.
        modify: a callable or string name from MODIFY_FUNCTIONS mapping
        """
        if name is None or not isinstance(name, str):
            raise TypeError("Name must be a string")
        if desc is None or not isinstance(desc, str):
            raise TypeError("Description must be a string")
        if not isinstance(sz, int) or isinstance(sz, bool):
            raise TypeError("Texture size (sz) must be an integer")
        if sz <= 0:
            raise ValueError("Texture size (sz) must be a positive integer > 0")
        if not isinstance(noise, (int, float)) or isinstance(noise, bool):
            raise TypeError("Noise must be a numeric value")

        modify_fn = MODIFY_FUNCTIONS.get(modify, modify) if isinstance(modify, str) else modify
        if not callable(modify_fn):
            modify_fn = identity

        pack_dir = Path(output_dir) / pack_dir_name
        blocks_dir = pack_dir / "textures" / "blocks"
        blocks_dir.mkdir(parents=True, exist_ok=True)

        rng = random.Random()
        for bname, color in BLOCK_COLORS.items():
            # Apply modify function
            c = modify_fn(color, rng)
            # Seed and generate noise texture
            rng.seed(hash(bname) & 0xFFFFFFFF)
            img = self._noise_tex(bname, c, sz, rng, noise)
            # Apply modifiers
            if bname in TEX_MODIFIERS:
                TEX_MODIFIERS[bname](img, sz, bname, rng)
            img.save(blocks_dir / f"{bname}.png")

        # Generate pack_icon.png
        sz_icon = 256
        icon = Image.new('RGB', (sz_icon, sz_icon))
        pix = icon.load()
        names = list(BLOCK_COLORS.keys())
        grid = 8
        cs = sz_icon // grid
        for gx in range(grid):
            for gy in range(grid):
                idx = (gy*grid+gx) % len(names)
                c = modify_fn(BLOCK_COLORS[names[idx]], rng)
                for x in range(cs):
                    for y in range(cs):
                        px, py = gx*cs+x, gy*cs+y
                        rng.seed(hash(f'icon_{pack_dir_name}_{px}_{py}')&0xFFFFFFFF)
                        noise_val = rng.randint(-12,12)
                        pix[px,py] = tuple(max(0,min(255,c[i]+noise_val)) for i in range(3))
        
        icon.save(pack_dir / "pack_icon.png")

        # Generate manifest.json
        uuids = self.get_uuids(pack_dir_name)
        manifest = {
            "format_version": 2,
            "header": {
                "name": name,
                "description": desc,
                "uuid": uuids["header"],
                "version": [1, 0, 0],
                "min_engine_version": [1, 20, 0]
            },
            "modules": [
                {
                    "type": "resources",
                    "uuid": uuids["module"],
                    "version": [1, 0, 0]
                }
            ],
        }

        with open(pack_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        return pack_dir
