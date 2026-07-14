import os
import json
import zlib
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from src.generators.base_generator import BaseGenerator

# World Icon draw functions
def w_lifesteal(d, sz):
    cx,cy=sz//2,sz//2-20
    d.ellipse([cx-60,cy-35,cx+60,cy+35], fill=(200,50,50))
    d.ellipse([cx-40,cy-25,cx+40,cy+25], fill=(100,0,0))

def w_kitpvp(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-50,cy-60,cx+50,cy+20], fill=(150,150,150))
    d.rectangle([cx-8,cy-75,cx+8,cy-60], fill=(200,150,50))
    d.rectangle([cx-35,cy-35,cx+35,cy-25], fill=(200,150,50))

def w_hunger_games(d, sz):
    cx,cy=sz//2,sz//2-20
    d.ellipse([cx-60,cy-40,cx+60,cy+40], fill=(50,150,50))
    d.ellipse([cx-30,cy-20,cx+30,cy+20], fill=(255,200,0))

def w_hardcore_survival(d, sz):
    cx,cy=sz//2,sz//2-10
    d.ellipse([cx-50,cy-40,cx+50,cy+40], fill=(50,150,50))
    d.rectangle([cx-40,cy+20,cx+40,cy+50], fill=(139,90,43))

def w_maze_runner(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(5):
        for j in range(5):
            if (i+j)%2==0:
                d.rectangle([cx-70+i*35,cy-70+j*35,cx-70+i*35+30,cy-70+j*35+30], fill=(100,150,100), outline=(50,100,50), width=2)

def w_build_battle(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-80,cy+10,cx+80,cy+30], fill=(150,100,50))
    d.rectangle([cx-30,cy-40,cx-10,cy+10], fill=(200,100,100))
    d.rectangle([cx+10,cy-50,cx+30,cy+10], fill=(100,100,200))
    d.rectangle([cx-5,cy-30,cx+5,cy+10], fill=(100,200,100))

def w_spawn_hub(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-70,cy-70,cx+70,cy+70], fill=(150,150,200))
    d.ellipse([cx-50,cy-50,cx+50,cy+50], fill=(200,200,255))

def w_factions(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-80,cy-30,cx+80,cy+30], fill=(100,100,100))
    d.rectangle([cx-60,cy-50,cx-20,cy-30], fill=(200,50,50))
    d.rectangle([cx+20,cy-50,cx+60,cy-30], fill=(50,50,200))

def w_prison(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(3):
        for j in range(3):
            d.rectangle([cx-60+i*42,cy-60+j*42,cx-60+i*42+35,cy-60+j*42+35], fill=(100,100,100), outline=(150,150,150), width=3)

def w_minigames(d, sz):
    cx,cy=sz//2,sz//2
    colors=[(200,50,50),(50,200,50),(50,50,200),(255,200,0),(200,0,200)]
    for i in range(5):
        a=math.radians(i*72-90)
        x=cx+int(65*math.cos(a))
        y=cy+int(65*math.sin(a))
        d.ellipse([x-25,y-25,x+25,y+25], fill=colors[i])

def w_city_roleplay(d, sz):
    cx,cy=sz//2,sz//2
    rng = random.Random(42)
    for i,b in enumerate([(20,70),(35,100),(25,50),(40,120),(30,60)]):
        w,h=b
        x=cx-80+i*30
        c=100+rng.randint(0,40)
        d.rectangle([x,cy+h//2-h,x+w,cy+h//2], fill=(c,c,c))

def w_medieval_smp(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-30,cy-70,cx+30,cy-10], fill=(50,150,50))
    d.rectangle([cx-25,cy-10,cx+25,cy+40], fill=(139,90,43))
    d.rectangle([cx-3,cy-80,cx+3,cy-60], fill=(101,67,33))
    d.ellipse([cx-20,cy-100,cx+20,cy-60], fill=(34,139,34))

def w_ctf(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-80,cy-10,cx-20,cy+10], fill=(200,50,50))
    d.rectangle([cx+20,cy-10,cx+80,cy+10], fill=(50,50,200))

def w_spleef(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(7):
        for j in range(7):
            x=cx-60+i*20; y=cy-60+j*20
            c=(200,200,200) if (i+j)%2==0 else (180,180,180)
            d.rectangle([x,y,x+18,y+18], fill=c, outline=(150,150,150), width=1)

def w_parkour_kingdom(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(6):
        x=cx-60+i*25; y=cy-30+int(20*math.sin(i*1.2))
        d.rectangle([x-10,y-5,x+10,y+5], fill=(200,100,50))

def w_zombie_apoc(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-60,cy-60,cx+60,cy+60], fill=(50,80,50))
    d.ellipse([cx-30,cy-30,cx+30,cy+30], fill=(100,50,50))
    d.rectangle([cx-5,cy-70,cx+5,cy-50], fill=(150,100,50))

def w_raid_boss(d, sz):
    cx,cy=sz//2,sz//2
    d.polygon([(cx,cy-70),(cx-60,cy+30),(cx+60,cy+30)], fill=(200,50,50))
    d.ellipse([cx-20,cy-30,cx+20,cy+10], fill=(255,200,0))

def w_ocean_explore(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-70,cy-70,cx+70,cy+70], fill=(0,50,150))
    d.ellipse([cx-50,cy-50,cx+50,cy+50], fill=(0,100,200))
    d.ellipse([cx-15,cy-15,cx+15,cy+15], fill=(255,200,0))

def w_desert_temple(d, sz):
    cx,cy=sz//2,sz//2
    d.polygon([(cx,cy-70),(cx-60,cy+10),(cx+60,cy+10)], fill=(210,190,140))
    d.rectangle([cx-30,cy+10,cx+30,cy+40], fill=(190,170,120))
    d.ellipse([cx-10,cy-15,cx+10,cy+5], fill=(255,200,0))

def w_ice_spikes(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(5):
        h=30+i*15; w=10+i*3
        x=cx-50+i*25
        d.polygon([(x,cy+30),(x-w//2,cy+30-h),(x+w//2,cy+30-h)], fill=(200,220,255))

def w_void_challenge(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-80,cy-5,cx+80,cy+5], fill=(100,50,150))
    d.rectangle([cx-5,cy-80,cx+5,cy+80], fill=(50,50,50))
    d.ellipse([cx-20,cy-30,cx+20,cy+30], fill=(255,0,0))

def w_tower_defense(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-10,cy-70,cx+10,cy+20], fill=(150,150,150))
    d.rectangle([cx-30,cy-20,cx-10,cy-10], fill=(100,100,200))
    d.rectangle([cx+10,cy-30,cx+30,cy-20], fill=(200,100,100))
    d.ellipse([cx-8,cy-80,cx+8,cy-65], fill=(255,200,0))

def w_anarchy_server(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(8):
        a=math.radians(i*45)
        x=cx+int(50*math.cos(a))
        y=cy+int(50*math.sin(a))
        d.ellipse([x-15,y-15,x+15,y+15], fill=(150,50,50))
    d.text((cx-20,cy-10), "?!", fill=(255,255,255))

DRAW_FUNCTIONS = {
    'lifesteal': w_lifesteal, 'kitpvp': w_kitpvp, 'hunger_games': w_hunger_games,
    'hardcore_survival': w_hardcore_survival, 'maze_runner': w_maze_runner, 'build_battle': w_build_battle,
    'spawn_hub': w_spawn_hub, 'factions': w_factions, 'prison': w_prison, 'minigames': w_minigames,
    'city_roleplay': w_city_roleplay, 'medieval_smp': w_medieval_smp, 'ctf': w_ctf, 'spleef': w_spleef,
    'parkour_kingdom': w_parkour_kingdom, 'zombie_apoc': w_zombie_apoc, 'raid_boss': w_raid_boss,
    'ocean_explore': w_ocean_explore, 'desert_temple': w_desert_temple, 'ice_spikes': w_ice_spikes,
    'void_challenge': w_void_challenge, 'tower_defense': w_tower_defense, 'anarchy_server': w_anarchy_server
}

class WorldTemplateGenerator(BaseGenerator):
    def make_world_icon_bg(self, draw: ImageDraw.ImageDraw, sz: int, color: tuple):
        draw.rectangle([0,0,sz,sz], fill=color)
        for i in range(sz):
            draw.rectangle([0,i,sz,i+1], fill=(0,0,0,int(20*(1-i/sz))))

    def draw_world_text(self, draw: ImageDraw.ImageDraw, sz: int, lines: list, base_y: int, color=(255,255,255)):
        try:
            ft = ImageFont.truetype("segoeui.ttf", sz//10)
            fs = ImageFont.truetype("segoeui.ttf", sz//18)
        except Exception:
            ft = fs = ImageFont.load_default()
        y = base_y
        for i, line in enumerate(lines):
            font = ft if i == 0 else fs
            bbox = draw.textbbox((0,0), line, font=font)
            tw = bbox[2]-bbox[0]
            draw.text(((sz-tw)//2, y), line, fill=color, font=font)
            y += bbox[3]-bbox[1]+8

    def gen_world_icon(self, path: Path, draw_fn, name: str, desc: str, bg: tuple):
        sz = 256
        img = Image.new("RGBA", (sz,sz))
        draw = ImageDraw.Draw(img)
        self.make_world_icon_bg(draw, sz, bg)
        draw_fn(draw, sz)
        self.draw_world_text(draw, sz, [name, desc], sz//2+50)
        img.save(path / "world_icon.png")
        img.resize((300,300), Image.Resampling.LANCZOS).save(path / "thumbnail.png")

    def make_minimal_level_dat(self) -> bytes:
        return zlib.compress(b'\x0a\x00\x00')

    def generate(self, output_dir: Path, pack_dir_name: str, name: str, desc: str, draw_fn, bg: tuple) -> Path:
        """
        Generates a world template pack.
        draw_fn: callable or string matching key in DRAW_FUNCTIONS
        """
        if name is None or not isinstance(name, str):
            raise TypeError("Name must be a string")
        if desc is None or not isinstance(desc, str):
            raise TypeError("Description must be a string")
        if bg is not None:
            if not isinstance(bg, (tuple, list)) or len(bg) != 3:
                raise TypeError("bg must be a tuple/list of 3 elements")
            for c in bg:
                if not isinstance(c, (int, float)) or isinstance(c, bool):
                    raise TypeError("bg color components must be numbers")
                if c < 0 or c > 255:
                    raise ValueError(f"bg color component {c} out of bounds [0, 255]")

        resolved_draw_fn = DRAW_FUNCTIONS.get(draw_fn, draw_fn) if isinstance(draw_fn, str) else draw_fn
        if not callable(resolved_draw_fn):
            resolved_draw_fn = lambda d, sz: None

        pack_dir = Path(output_dir) / pack_dir_name
        pack_dir.mkdir(parents=True, exist_ok=True)

        self.gen_world_icon(pack_dir, resolved_draw_fn, name, desc, bg)

        with open(pack_dir / "level.dat", "wb") as f:
            f.write(self.make_minimal_level_dat())

        uuids = self.get_uuids(f"world_{pack_dir_name}")
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
                    "type": "world_template",
                    "uuid": uuids["module"],
                    "version": [1, 0, 0]
                }
            ],
        }

        with open(pack_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        return pack_dir
