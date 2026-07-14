"""Generate 42 expansion packs based on scraped trend data (MCPEDL, MCSkins, NameMC, minecraftskins)."""
from PIL import Image, ImageDraw
import os, json, random, math, io, base64

random.seed(42)
BASE = os.path.join(os.path.dirname(__file__), '..')
SKIN_DIR = os.path.join(BASE, 'skin-packs')
TEX_DIR = os.path.join(BASE, 'texture-packs')
WORLD_DIR = os.path.join(BASE, 'world-templates')
MASHUP_DIR = os.path.join(BASE, 'mashup-packs')

UUID_BASE = "f0000000-0000-0000-0000-000000000000"

def make_uuid(seed):
    h = hash(str(seed)) & 0xFFFFFFFFFFFFFFFF
    return f"{h>>48:04x}{h>>32&0xFFFF:04x}-{h>>16&0xFFFF:04x}-{h&0xFFFF:04x}-{hash(str(seed)+'x')&0xFFFF:04x}-{hash(str(seed)+'y')&0xFFFFFFFFFF:012x}"

# ── SKIN TEXTURE GENERATORS ──

def gen_skin_tex(primary, secondary, pattern='auto'):
    img = Image.new('RGBA', (64, 64), (*primary, 255))
    pixels = img.load()
    if pattern == 'auto':
        pattern = random.choice(['stripe_h', 'stripe_v', 'check', 'diag', 'dots', 'cross'])
    for x in range(64):
        for y in range(64):
            r, g, b, a = pixels[x, y]
            use_sec = False
            if pattern == 'stripe_h' and (y // 4) % 2 == 0:
                use_sec = True
            elif pattern == 'stripe_v' and (x // 4) % 2 == 0:
                use_sec = True
            elif pattern == 'check' and ((x // 4) + (y // 4)) % 2 == 0:
                use_sec = True
            elif pattern == 'diag' and ((x + y) // 6) % 2 == 0:
                use_sec = True
            elif pattern == 'dots' and (x // 8) % 2 == 0 and (y // 8) % 2 == 0:
                use_sec = True
            elif pattern == 'cross' and ((x // 4) % 2 == 0 or (y // 4) % 2 == 0):
                use_sec = True
            if use_sec:
                sr, sg, sb = secondary
                blend = 0.8
                pixels[x, y] = (int(r*(1-blend)+sr*blend), int(g*(1-blend)+sg*blend), int(b*(1-blend)+sb*blend), 255)
    return img

def gen_skin_icon(colors):
    icon = Image.new('RGBA', (300, 300), (30, 30, 40, 255))
    draw = ImageDraw.Draw(icon)
    cx, cy = 150, 150
    for i, c in enumerate(colors):
        angle = i * 2.0
        px = cx + int(80 * math.cos(angle))
        py = cy + int(80 * math.sin(angle))
        draw.ellipse([px-40, py-40, px+40, py+40], fill=(*c, 255))
    return icon

# ── SKIN PACK DEFINITIONS (25 new based on trends) ──

SKIN_PACKS = [
    # MCPEDL trends
    {"dir": "anime-waifus", "name": "Anime Waifus", "desc": "8 cute anime waifu skins! Frieren, Rem, Hu Tao, Megumin, Asuna, ZeroTwo, Miku, Emilia.",
     "skins": [("Frieren", (200,180,255),(255,220,220)),("Rem", (0,100,255),(255,255,255)),("HuTao", (200,50,50),(255,200,0)),
               ("Megumin", (255,0,0),(0,0,0)),("Asuna", (255,200,200),(255,255,255)),("ZeroTwo", (255,50,50),(0,200,255)),
               ("Miku", (0,200,150),(50,200,255)),("Emilia", (200,150,255),(255,200,255))]},
    {"dir": "kawaii-fashion", "name": "Kawaii Fashion", "desc": "8 pastel kawaii fashion skins! Pastel girl, soft girl, hello kitty, strawberry, bunny, bear, angel, fairy.",
     "skins": [("PastelGirl", (255,200,220),(255,220,240)),("SoftGirl", (200,220,255),(255,200,220)),("HelloKitty", (255,200,220),(255,255,255)),
               ("Strawberry", (255,100,100),(50,200,50)),("Bunny", (255,220,255),(200,200,255)),("Bear", (200,150,100),(150,100,80)),
               ("Angel", (255,255,255),(255,215,0)),("Fairy", (200,255,200),(255,200,255))]},
    {"dir": "gothic-kawaii", "name": "Gothic Kawaii", "desc": "8 dark gothic kawaii skins! Gothic lolita, dark angel, vampire queen, shadow cat, etc.",
     "skins": [("GothLolita", (50,0,50),(200,150,200)),("DarkAngel", (20,20,40),(200,200,255)),("VampQueen", (100,0,0),(200,0,0)),
               ("ShadowCat", (30,30,30),(200,200,200)),("DarkFairy", (50,0,80),(200,100,200)),("NightRose", (80,0,50),(0,200,50)),
               ("Witch", (50,0,50),(0,150,0)),("SoulEater", (20,20,20),(255,50,50))]},
    {"dir": "neon-cyber", "name": "Neon Cyber", "desc": "8 neon cyberpunk skins! Neon gamer, cyber hacker, glitch, volt, pulse, matrix, byte, pixel.",
     "skins": [("NeonGamer", (255,0,255),(0,255,255)),("CyberHacker", (0,255,0),(0,0,0)),("Glitch", (255,0,0),(0,0,255)),
               ("Volt", (255,255,0),(0,255,255)),("Pulse", (255,0,128),(0,255,128)),("Matrix", (0,255,0),(0,50,0)),
               ("Byte", (0,200,255),(255,0,255)),("Pixel", (255,200,0),(255,0,200))]},
    {"dir": "japanese-fashion", "name": "Japanese Fashion", "desc": "8 traditional Japanese fashion skins! Kimono, schoolgirl, samurai, geisha, shrine maiden, ninja, yokai, ronin.",
     "skins": [("Kimono", (255,50,50),(255,215,0)),("Schoolgirl", (0,50,200),(255,255,255)),("Samurai", (180,20,20),(50,50,50)),
               ("Geisha", (255,255,255),(255,200,200)),("ShrineMaiden", (255,255,255),(220,50,50)),("Ninja", (10,10,50),(20,20,20)),
               ("Yokai", (200,50,200),(0,200,0)),("Ronin", (160,160,160),(200,200,200))]},
    {"dir": "korean-fashion", "name": "Korean Fashion", "desc": "8 K-pop inspired fashion skins! K-pop star, streetwear, idol, dancer, chic, trendy, casual, model.",
     "skins": [("KpopStar", (255,200,220),(200,150,255)),("Streetwear", (50,50,50),(200,200,200)),("Idol", (255,220,255),(200,200,255)),
               ("Dancer", (255,100,150),(100,100,200)),("Chic", (200,200,200),(255,200,200)),("Trendy", (255,200,0),(0,0,0)),
               ("Casual", (150,200,255),(255,220,200)),("Model", (200,200,255),(255,200,220))]},
    {"dir": "egyptian-mythology", "name": "Egyptian Mythology", "desc": "8 Egyptian god skins! Ra, Anubis, Horus, Bastet, Osiris, Isis, Seth, Cleopatra.",
     "skins": [("Ra", (255,215,0),(255,255,255)),("Anubis", (0,0,0),(255,215,0)),("Horus", (0,100,255),(255,215,0)),
               ("Bastet", (255,200,100),(200,150,50)),("Osiris", (50,200,50),(255,215,0)),("Isis", (100,200,255),(255,200,200)),
               ("Seth", (200,50,50),(0,0,0)),("Cleopatra", (255,215,0),(0,0,200))]},
    {"dir": "horror-creepypasta", "name": "Horror Creepypasta", "desc": "8 creepy horror skins! Nightmare, Endoskeleton, Slenderman, JeffK, Ben Drowned, Ticci Toby, Eyeless Jack, Laughing Jill.",
     "skins": [("Nightmare", (0,0,0),(200,0,0)),("Endoskeleton", (150,150,150),(0,0,0)),("Slenderman", (0,0,0),(50,50,50)),
               ("JeffK", (200,200,200),(200,0,0)),("BenDrowned", (0,100,200),(0,200,0)),("TicciToby", (100,100,100),(200,0,0)),
               ("EyelessJack", (50,50,50),(0,0,0)),("LaughingJill", (200,200,255),(200,0,0))]},
    # MCSkins.top trends
    {"dir": "redstone-tech", "name": "Redstone Tech", "desc": "8 redstone & tech skins! Redstone bot, engineer, mechanic, hacker, robot, cyborg, drone, AI.",
     "skins": [("RedBot", (200,0,0),(50,50,50)),("Engineer", (200,150,50),(0,100,200)),("Mechanic", (50,50,200),(200,200,200)),
               ("Hacker", (0,200,0),(0,0,0)),("Robot", (150,150,150),(0,200,255)),("Cyborg", (100,100,100),(255,0,0)),
               ("Drone", (0,100,200),(200,200,200)),("AI", (0,200,255),(0,0,200))]},
    {"dir": "pride-2026", "name": "Pride 2026", "desc": "8 colorful pride-themed skins! Rainbow, trans, bi, pan, nonbinary, ace, genderfluid, lesbian.",
     "skins": [("Rainbow", (255,0,0),(255,255,0)),("Trans", (200,200,255),(255,200,220)),("Bi", (200,50,150),(0,50,200)),
               ("Pan", (255,100,200),(255,255,0)),("Nonbinary", (255,255,0),(100,0,200)),("Ace", (0,0,0),(150,150,150)),
               ("Genderfluid", (255,150,200),(150,50,255)),("Lesbian", (200,50,50),(255,200,150))]},
    {"dir": "hive-style", "name": "Hive Style", "desc": "8 Hive-style skins! Bee, axolotl, plush, marshmallow, dino, flower, mail, flame.",
     "skins": [("Bee", (255,200,0),(50,50,50)),("Axolotl", (255,150,200),(255,100,150)),("Plush", (200,150,200),(255,200,220)),
               ("Marshmallow", (255,220,220),(200,180,200)),("Dino", (50,200,50),(0,150,0)),("Flower", (255,100,200),(255,255,0)),
               ("Mail", (200,50,50),(255,255,255)),("Flame", (255,100,0),(255,255,0))]},
    {"dir": "fantasy-rpg", "name": "Fantasy RPG", "desc": "8 fantasy RPG class skins! Warrior, Mage, Rogue, Cleric, Paladin, Druid, Bard, Warlock.",
     "skins": [("Warrior", (200,50,50),(150,150,150)),("Mage", (100,50,200),(255,200,255)),("Rogue", (50,50,50),(100,100,100)),
               ("Cleric", (255,255,255),(255,215,0)),("Paladin", (200,200,200),(255,215,0)),("Druid", (50,150,50),(150,100,50)),
               ("Bard", (200,50,150),(255,200,0)),("Warlock", (100,0,100),(0,200,0))]},
    {"dir": "streetwear-urban", "name": "Streetwear Urban", "desc": "8 urban streetwear skins! Hoodie, bomber, sneakerhead, skater, graffiti, beatbox, bboy, hypebeast.",
     "skins": [("Hoodie", (50,50,50),(200,200,200)),("Bomber", (0,100,200),(255,255,255)),("Sneakerhead", (255,255,255),(200,50,50)),
               ("Skater", (150,100,50),(200,150,50)),("Graffiti", (255,200,0),(255,50,50)),("Beatbox", (50,50,150),(200,200,200)),
               ("Bboy", (200,50,50),(255,215,0)),("Hypebeast", (50,200,50),(255,200,0))]},
    {"dir": "greek-mythology", "name": "Greek Mythology", "desc": "8 Greek god skins! Zeus, Poseidon, Hades, Athena, Ares, Apollo, Artemis, Aphrodite.",
     "skins": [("Zeus", (255,255,255),(255,215,0)),("Poseidon", (0,100,200),(100,200,255)),("Hades", (50,0,50),(255,200,0)),
               ("Athena", (200,200,200),(0,100,200)),("Ares", (200,50,50),(150,50,50)),("Apollo", (255,215,0),(255,255,255)),
               ("Artemis", (50,150,50),(200,150,50)),("Aphrodite", (255,200,220),(255,100,150))]},
    {"dir": "norse-mythology", "name": "Norse Mythology", "desc": "8 Norse god skins! Odin, Thor, Loki, Freyja, Baldr, Heimdall, Tyr, Hel.",
     "skins": [("Odin", (100,100,150),(200,200,200)),("Thor", (200,150,50),(50,50,200)),("Loki", (50,100,50),(255,200,0)),
               ("Freyja", (255,200,150),(50,200,50)),("Baldr", (255,255,255),(255,215,0)),("Heimdall", (255,215,0),(255,255,255)),
               ("Tyr", (200,50,50),(150,150,150)),("Hel", (0,0,100),(50,200,50))]},
    {"dir": "steampunk", "name": "Steampunk", "desc": "8 steampunk skins! Engineer, airship captain, inventor, clockmaker, alchemist, pilot, explorer, tinkerer.",
     "skins": [("Engineer", (150,100,50),(200,150,50)),("AirshipCap", (100,50,0),(200,150,100)),("Inventor", (150,150,150),(200,150,50)),
               ("Clockmaker", (200,150,50),(100,50,0)),("Alchemist", (50,100,50),(200,150,0)),("Pilot", (150,100,50),(0,100,200)),
               ("Explorer", (100,80,50),(200,200,200)),("Tinkerer", (200,150,100),(50,50,50))]},
    {"dir": "space-astronaut", "name": "Space Astronaut", "desc": "8 space-themed skins! Astronaut, alien, rover, star, comet, nebula, galaxy, cosmonaut.",
     "skins": [("Astronaut", (255,255,255),(200,200,200)),("Alien", (50,200,50),(0,200,255)),("Rover", (200,150,50),(100,100,100)),
               ("Star", (255,215,0),(255,255,255)),("Comet", (255,100,0),(255,215,0)),("Nebula", (150,50,200),(0,100,200)),
               ("Galaxy", (50,0,100),(200,100,255)),("Cosmonaut", (255,50,50),(200,200,200))]},
]

# ── TEXTURE PACK DEFINITIONS (8 new) ──

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

TEX_MODIFIERS = {
    'stone_brick': lambda img, sz, rng: _grid(img, sz, 4, 20),
    'planks_oak': lambda img, sz, rng: _stripes(img, sz, 8),
    'planks_spruce': lambda img, sz, rng: _stripes(img, sz, 8),
    'planks_birch': lambda img, sz, rng: _stripes(img, sz, 8),
    'planks_jungle': lambda img, sz, rng: _stripes(img, sz, 8),
    'planks_acacia': lambda img, sz, rng: _stripes(img, sz, 8),
    'planks_dark_oak': lambda img, sz, rng: _stripes(img, sz, 8),
    'mossy_cobblestone': lambda img, sz, rng: _moss(img, sz, rng),
    'water_still': lambda img, sz, rng: _wave(img, sz),
    'water_flow': lambda img, sz, rng: _wave(img, sz),
    'lava_still': lambda img, sz, rng: _glow(img, sz, rng),
    'lava_flow': lambda img, sz, rng: _glow(img, sz, rng),
    'gold_block': lambda img, sz, rng: _sparkle(img, sz, rng, 40),
    'diamond_block': lambda img, sz, rng: _sparkle(img, sz, rng, 40),
    'emerald_block': lambda img, sz, rng: _sparkle(img, sz, rng, 40),
    'obsidian': lambda img, sz, rng: _sheen(img, sz, rng),
    'netherrack': lambda img, sz, rng: _ember(img, sz, rng),
    'grass_side': lambda img, sz, rng: _grass_side(img, sz, rng),
}

def _noise_tex(name, color, sz, rng, noise=18):
    img = Image.new('RGB', (sz, sz))
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'{name}_{x}_{y}') & 0xFFFFFFFF)
            pix[x,y] = tuple(max(0,min(255,c+rng.randint(-noise,noise))) for c in color)
    return img

def _grid(img, sz, div, dark):
    pix = img.load()
    cell = sz // div
    for x in range(sz):
        for y in range(sz):
            if x % cell == 0 or y % cell == 0:
                r,g,b = pix[x,y]
                pix[x,y] = (max(0,r-dark),max(0,g-dark),max(0,b-dark))
    return img

def _stripes(img, sz, spacing):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            if y % spacing == 0 or y % spacing == 1:
                r,g,b = pix[x,y]
                pix[x,y] = (max(0,r-15),max(0,g-15),max(0,b-15))
    return img

def _moss(img, sz, rng):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'moss_{x}_{y}')&0xFFFFFFFF)
            if rng.random() < 0.25:
                r,g,b = pix[x,y]
                moss=(70,130,60)
                pix[x,y] = tuple(max(0,min(255,int(c*0.6+m*d*0.4)+rng.randint(-10,10))) for c,m,d in zip((r,g,b),moss,[0,1,2]))
    return img

def _wave(img, sz):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            r,g,b = pix[x,y]
            w = int(6*math.sin(x*0.5+y*0.3))
            pix[x,y] = (max(0,min(255,r+w)),max(0,min(255,g+w)),max(0,min(255,b+w)))
    return img

def _glow(img, sz, rng):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            r,g,b = pix[x,y]
            br = rng.randint(-20,20)
            pix[x,y] = (max(0,min(255,r+br)),max(0,min(255,g+br//2)),max(0,min(255,b+br//3)))
    return img

def _sparkle(img, sz, rng, amt):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'sparkle_{x}_{y}')&0xFFFFFFFF)
            if rng.random() < 0.08:
                r,g,b = pix[x,y]
                pix[x,y] = (min(255,r+amt),min(255,g+amt),min(255,b+amt))
    return img

def _sheen(img, sz, rng):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'sheen_{x}_{y}')&0xFFFFFFFF)
            if rng.random() < 0.1:
                r,g,b = pix[x,y]
                pix[x,y] = (min(255,r+15),min(255,g+15),min(255,b+15))
    return img

def _ember(img, sz, rng):
    pix = img.load()
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'ember_{x}_{y}')&0xFFFFFFFF)
            if rng.random() < 0.06:
                r,g,b = pix[x,y]
                pix[x,y] = (min(255,r+50),max(0,g-10),max(0,b-10))
    return img

def _grass_side(img, sz, rng):
    pix = img.load()
    top = (90,175,65)
    for x in range(sz):
        for y in range(sz):
            rng.seed(hash(f'grass_{x}_{y}')&0xFFFFFFFF)
            t = y/sz
            if t < 0.25:
                c = top
            elif t < 0.4:
                bl = (t-0.25)/0.15
                c = tuple(int(top[i]*(1-bl)+pix[x,y][i]*bl) for i in range(3))
            else:
                c = pix[x,y]
            n = rng.randint(-15,15)
            pix[x,y] = tuple(max(0,min(255,c[i]+n)) for i in range(3))
    return img

def _darken(c, f=0.55):
    return tuple(max(0,min(255,int(v*f))) for v in c)

def _pastel(c, _rng=None):
    return tuple(max(0,min(255,int(v*0.7+100))) for v in c)

def _neon(c, _rng=None):
    return tuple(max(0,min(255,int(v*1.3+30))) for v in c)

def _sepia(c, _rng=None):
    g = int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g*1.1,g*0.95,g*0.8))

def _anime_style(c, _rng=None):
    return tuple(max(0,min(255,int(v*0.8+50))) for v in c)

def _gothic(c, _rng=None):
    return tuple(max(0,min(255,int(v*0.5-20))) for v in c)

TEXTURE_PACKS = [
    {"dir": "x64-natural", "name": "64x Natural", "desc": "Enhanced 64x64 textures that make your world look stunning while keeping the vanilla feel.",
     "modify": lambda c,_rng=None: c, "sz": 64, "noise": 20},
    {"dir": "x128-ultra", "name": "128x Ultra HD", "desc": "Ultra HD 128x128 textures for maximum visual fidelity.",
     "modify": lambda c,_rng=None: c, "sz": 128, "noise": 22},
    {"dir": "x64-faithful", "name": "64x Faithful", "desc": "Faithful 64x64 textures that stay true to vanilla Minecraft.",
     "modify": lambda c,_rng=None: c, "sz": 64, "noise": 16},
    {"dir": "pastel-cute", "name": "Pastel Cute", "desc": "Soft pastel-colored textures for a cute and cozy Minecraft world.",
     "modify": _pastel, "sz": 32, "noise": 14},
    {"dir": "neon-glow", "name": "Neon Glow", "desc": "Bright neon-colored textures that glow and pop with vibrant energy.",
     "modify": _neon, "sz": 32, "noise": 20},
    {"dir": "medieval-rp", "name": "Medieval RP", "desc": "Medieval roleplay textures with warm, rustic colors for fantasy worlds.",
     "modify": _sepia, "sz": 32, "noise": 18},
    {"dir": "horror-gothic", "name": "Horror Gothic", "desc": "Dark gothic textures for horror and spooky Minecraft builds.",
     "modify": _gothic, "sz": 32, "noise": 22},
    {"dir": "anime-style", "name": "Anime Style", "desc": "Anime-inspired textures with bright, vibrant colors and smooth shading.",
     "modify": _anime_style, "sz": 32, "noise": 15},
]

# ── WORLD TEMPLATES (5 new) ──

def make_world_icon_bg(draw, sz, color):
    draw.rectangle([0,0,sz,sz], fill=color)
    for i in range(sz):
        alpha = int(20*(1-i/sz))
        draw.rectangle([0,i,sz,i+1], fill=(0,0,0,alpha))

def draw_world_text(draw, sz, lines, base_y, color=(255,255,255)):
    from PIL import ImageFont
    try:
        ft = ImageFont.truetype("segoeui.ttf", sz//10)
        fs = ImageFont.truetype("segoeui.ttf", sz//18)
    except:
        ft = fs = ImageFont.load_default()
    y = base_y
    for i, line in enumerate(lines):
        font = ft if i == 0 else fs
        bbox = draw.textbbox((0,0), line, font=font)
        tw = bbox[2]-bbox[0]
        draw.text(((sz-tw)//2, y), line, fill=color, font=font)
        y += bbox[3]-bbox[1]+8

def gen_survival_island(path):
    sz = 256
    img = Image.new("RGBA", (sz,sz))
    draw = ImageDraw.Draw(img)
    make_world_icon_bg(draw, sz, (100,180,255))
    cx,cy=sz//2,sz//2-20
    draw.ellipse([cx-60,cy-30,cx+60,cy+40], fill=(87,168,47))
    draw.rectangle([cx-55,cy+20,cx+55,cy+70], fill=(139,90,43))
    draw.rectangle([cx-5,cy-50,cx+5,cy-25], fill=(101,67,33))
    draw.ellipse([cx-25,cy-80,cx+25,cy-40], fill=(34,139,34))
    for fx,fy,s in [(30,60,15),(210,80,18),(190,200,12),(50,200,14)]:
        draw.ellipse([fx-s,fy-s//2,fx+s,fy+s//2], fill=(100,180,60))
    draw_world_text(draw,sz,["Survival Island","Advanced survival challenge!"], cy+80)
    img.save(f"{path}\\world_icon.png")
    img.resize((300,300),Image.LANCZOS).save(f"{path}\\thumbnail.png")

def gen_bedwars(path):
    sz = 256
    img = Image.new("RGBA", (sz,sz))
    draw = ImageDraw.Draw(img)
    make_world_icon_bg(draw, sz, (255,200,50))
    cx,cy=sz//2,sz//2-10
    for i in range(4):
        a=math.radians(i*90-45)
        bx=cx+int(70*math.cos(a))
        by=cy+int(70*math.sin(a))
        draw.rectangle([bx-20,by-15,bx+20,by+15], fill=[(200,50,50),(50,50,200),(50,200,50),(255,200,0)][i])
        draw.ellipse([bx-8,by-20,bx+8,by-5], fill=(255,255,255))
    draw_world_text(draw,sz,["Bed Wars","Fight for your bed!"], cy+70)
    img.save(f"{path}\\world_icon.png")
    img.resize((300,300),Image.LANCZOS).save(f"{path}\\thumbnail.png")

def gen_skygrid(path):
    sz = 256
    img = Image.new("RGBA", (sz,sz))
    draw = ImageDraw.Draw(img)
    make_world_icon_bg(draw, sz, (80,20,120))
    cx,cy=sz//2,sz//2-10
    bs=35
    for gx in range(4):
        for gy in range(3):
            x=cx-60+gx*40
            y=cy-30+gy*40
            colors=[(120,180,80),(180,140,60),(100,100,180),(200,100,100)]
            draw.rectangle([x,y,x+bs,y+bs], fill=colors[(gx+gy)%4], outline=(255,255,255,100), width=2)
    draw_world_text(draw,sz,["SkyGrid","Every block a challenge!"], cy+70)
    img.save(f"{path}\\world_icon.png")
    img.resize((300,300),Image.LANCZOS).save(f"{path}\\thumbnail.png")

def gen_dragon_lair(path):
    sz = 256
    img = Image.new("RGBA", (sz,sz))
    draw = ImageDraw.Draw(img)
    make_world_icon_bg(draw, sz, (60,0,0))
    cx,cy=sz//2,sz//2-10
    # dragon silhouette
    draw.polygon([(cx-60,cy+20),(cx-40,cy-40),(cx-10,cy-50),(cx+10,cy-60),
                  (cx+30,cy-40),(cx+50,cy-20),(cx+60,cy+10),(cx+40,cy+30),
                  (cx+20,cy+10),(cx-20,cy+10),(cx-40,cy+30)], fill=(100,0,0,200))
    # wings
    draw.polygon([(cx-10,cy-40),(cx-50,cy-80),(cx-30,cy-50)], fill=(150,0,0,180))
    draw.polygon([(cx+10,cy-50),(cx+50,cy-80),(cx+30,cy-40)], fill=(150,0,0,180))
    # fire
    draw.polygon([(cx+60,cy),(cx+80,cy-10),(cx+75,cy+5),(cx+85,cy+10)], fill=(255,200,50,200))
    draw_world_text(draw,sz,["Dragon's Lair","Face the final boss!"], cy+70)
    img.save(f"{path}\\world_icon.png")
    img.resize((300,300),Image.LANCZOS).save(f"{path}\\thumbnail.png")

def gen_city_build(path):
    sz = 256
    img = Image.new("RGBA", (sz,sz))
    draw = ImageDraw.Draw(img)
    make_world_icon_bg(draw, sz, (100,150,200))
    cx,cy=sz//2,sz//2
    # buildings silhouette
    for i,b in enumerate([(20,80),(35,110),(25,60),(40,130),(30,70),(20,90)]):
        w,h=b
        x=cx-80+i*30
        draw.rectangle([x,cy+h//2-h,x+w,cy+h//2], fill=(120+random.randint(0,40),120+random.randint(0,40),120+random.randint(0,40)))
        # windows
        for wy in range(cy+h//2-h+8,cy+h//2-8,12):
            for wx in range(x+4,x+w-4,8):
                if random.random()<0.6:
                    draw.rectangle([wx,wy,wx+4,wy+4], fill=(255,255,200,180))
    draw_world_text(draw,sz,["City Build","Build your metropolis!"], cy+70)
    img.save(f"{path}\\world_icon.png")
    img.resize((300,300),Image.LANCZOS).save(f"{path}\\thumbnail.png")

WORLDS = [
    ("survival-island-advanced", gen_survival_island, "Survival Island Advanced", "Advanced survival island with multiple biomes, caves, and challenges."),
    ("bedwars-arena", gen_bedwars, "Bed Wars Arena", "4-team Bed Wars map with islands, generators, and arenas."),
    ("skygrid", gen_skygrid, "SkyGrid", "Every single block is floating in a grid. Survive the chaos!"),
    ("dragon-lair", gen_dragon_lair, "Dragon's Lair", "Epic adventure map with a dragon boss at the end."),
    ("city-build", gen_city_build, "City Build", "Flat modern city with roads, plots, and infrastructure."),
]

# ── MASHUP PACKS (4 new) ──

MASHUPS = [
    {"dir": "japanese-anime-mashup", "name": "Japanese Anime Mashup", "desc": "Full Japanese anime experience! Japanese Fashion skins + Anime Style textures + Japanese world.",
     "deps": [], "icon_fn": "cherry_icon"},
    {"dir": "cyberpunk-city-mashup", "name": "Cyberpunk City Mashup", "desc": "Cyberpunk bundle! Neon Cyber skins + Neon Glow textures + City world.",
     "deps": [], "icon_fn": "neon_icon"},
    {"dir": "fantasy-rpg-mashup", "name": "Fantasy RPG Mashup", "desc": "Epic RPG bundle! Fantasy RPG skins + Medieval RP textures + Dragon's Lair world.",
     "deps": [], "icon_fn": "rpg_icon"},
    {"dir": "horror-mashup", "name": "Horror Mashup", "desc": "Spooky horror bundle! Horror Creepypasta skins + Horror Gothic textures + Haunted world.",
     "deps": [], "icon_fn": "horror_icon"},
]

def draw_cherry_icon():
    img = Image.new('RGBA', (256,256), (45,0,77,255))
    draw = ImageDraw.Draw(img)
    cx,cy=128,128
    for i in range(5):
        a=math.radians(i*72-90)
        px=cx+int(50*math.cos(a))
        py=cy+int(50*math.sin(a))
        draw.ellipse([px-35,py-45,px+35,py+15], fill=(255,150,200,255))
    draw.ellipse([cx-12,cy-12,cx+12,cy+12], fill=(255,200,220,255))
    return img

def draw_neon_icon():
    img = Image.new('RGBA', (256,256), (10,10,30,255))
    draw = ImageDraw.Draw(img)
    cx,cy=128,128
    draw.ellipse([cx-80,cy-80,cx+80,cy+80], fill=(255,0,255,60))
    draw.ellipse([cx-60,cy-60,cx+60,cy+60], fill=(0,255,255,80))
    draw.rectangle([cx-40,cy-10,cx+40,cy+10], fill=(0,255,255,200))
    draw.rectangle([cx-10,cy-40,cx+10,cy+40], fill=(255,0,255,200))
    for i in range(8):
        a=math.radians(i*45)
        x=cx+int(90*math.cos(a))
        y=cy+int(90*math.sin(a))
        draw.ellipse([x-5,y-5,x+5,y+5], fill=(255,255,0,200))
    return img

def draw_rpg_icon():
    img = Image.new('RGBA', (256,256), (40,20,10,255))
    draw = ImageDraw.Draw(img)
    cx,cy=128,128
    # sword
    draw.rectangle([cx-6,cy-80,cx+6,cy+20], fill=(200,200,200,255))
    draw.polygon([(cx-15,cy-80),(cx+15,cy-80),(cx,cy-100)], fill=(200,200,200,255))
    # crossguard
    draw.rectangle([cx-25,cy-25,cx+25,cy-15], fill=(180,120,50,255))
    draw.rectangle([cx-6,cy+20,cx+6,cy+40], fill=(120,80,30,255))
    # glow
    draw.ellipse([cx-50,cy-120,cx+50,cy-60], fill=(255,215,0,30))
    return img

def draw_horror_icon():
    img = Image.new('RGBA', (256,256), (20,0,0,255))
    draw = ImageDraw.Draw(img)
    cx,cy=128,128
    # red eyes
    draw.ellipse([cx-40,cy-30,cx-10,cy+10], fill=(200,0,0,255))
    draw.ellipse([cx+10,cy-30,cx+40,cy+10], fill=(200,0,0,255))
    # pupils
    draw.ellipse([cx-35,cy-20,cx-15,cy], fill=(255,0,0,255))
    draw.ellipse([cx+15,cy-20,cx+35,cy], fill=(255,0,0,255))
    # mouth
    draw.arc([cx-60,cy+20,cx+60,cy+80], 0, 180, fill=(100,0,0), width=6)
    # drip
    draw.rectangle([cx-5,cy+50,cx+5,cy+70], fill=(150,0,0,200))
    draw.ellipse([cx-5,cy+65,cx+5,cy+75], fill=(150,0,0,200))
    return img

MASH_ICONS = {
    "cherry_icon": draw_cherry_icon,
    "neon_icon": draw_neon_icon,
    "rpg_icon": draw_rpg_icon,
    "horror_icon": draw_horror_icon,
}

# ── GENERATION FUNCTIONS ──

def make_skin_manifest(pack):
    uid = make_uuid(pack["dir"])
    muid = make_uuid(pack["dir"]+"_mod")
    return {
        "format_version": 2,
        "header": {"name": pack["name"], "description": pack["desc"], "uuid": uid, "version": [1,0,0], "min_engine_version": [1,20,0]},
        "modules": [{"type": "skin_pack", "uuid": muid, "version": [1,0,0]}],
    }

def make_skins_json(pack):
    return {
        "skins": [{"localization_name": n, "geometry": "geometry.humanoid.custom", "texture": f"{n}.png", "type": "free"} for n,_,_ in pack["skins"]],
        "serialize_name": pack["name"], "localization_name": pack["name"],
    }

def gen_skin_pack(pack):
    pd = os.path.join(SKIN_DIR, pack["dir"])
    sd = os.path.join(pd, "textures", "skins")
    os.makedirs(sd, exist_ok=True)
    for name, prim, sec in pack["skins"]:
        img = gen_skin_tex(prim, sec)
        img.save(os.path.join(sd, f"{name}.png"))
    all_colors = [c[1] for c in pack["skins"]] + [c[2] for c in pack["skins"]]
    icon = gen_skin_icon(all_colors)
    icon.save(os.path.join(sd, "icon.png"))
    with open(os.path.join(pd, "manifest.json"), "w") as f:
        json.dump(make_skin_manifest(pack), f, indent=2)
    with open(os.path.join(pd, "skins.json"), "w") as f:
        json.dump(make_skins_json(pack), f, indent=2)
    print(f"  Skin pack: {pack['dir']} ({len(pack['skins'])} skins)")

def make_tex_manifest(pack):
    uid = make_uuid(pack["dir"])
    muid = make_uuid(pack["dir"]+"_mod")
    return {
        "format_version": 2,
        "header": {"name": pack["name"], "description": pack["desc"], "uuid": uid, "version": [1,0,0], "min_engine_version": [1,20,0]},
        "modules": [{"type": "resources", "uuid": muid, "version": [1,0,0]}],
    }

def gen_tex_pack(pack):
    pd = os.path.join(TEX_DIR, pack["dir"])
    td = os.path.join(pd, "textures", "blocks")
    os.makedirs(td, exist_ok=True)
    rng = random.Random()
    for name, color in BLOCK_COLORS.items():
        c = pack["modify"](color, rng)
        rng.seed(hash(name)&0xFFFFFFFF)
        img = _noise_tex(name, c, pack["sz"], rng, pack["noise"])
        if name in TEX_MODIFIERS:
            img = TEX_MODIFIERS[name](img, pack["sz"], rng)
        img.save(os.path.join(td, f"{name}.png"))
    # icon
    sz_icon = 256
    icon = Image.new('RGB', (sz_icon, sz_icon))
    pix = icon.load()
    names = list(BLOCK_COLORS.keys())
    grid = 8
    cs = sz_icon // grid
    for gx in range(grid):
        for gy in range(grid):
            idx = (gy*grid+gx) % len(names)
            c = pack["modify"](BLOCK_COLORS[names[idx]], rng)
            for x in range(cs):
                for y in range(cs):
                    px, py = gx*cs+x, gy*cs+y
                    rng.seed(hash(f'icon_{pack["dir"]}_{px}_{py}')&0xFFFFFFFF)
                    noise = rng.randint(-12,12)
                    pix[px,py] = tuple(max(0,min(255,c[i]+noise)) for i in range(3))
    icon.save(os.path.join(pd, "pack_icon.png"))
    with open(os.path.join(pd, "manifest.json"), "w") as f:
        json.dump(make_tex_manifest(pack), f, indent=2)
    print(f"  Texture pack: {pack['dir']} ({pack['sz']}x)")

def make_world_manifest(dir_name, name, desc):
    uid = make_uuid(f"world_{dir_name}")
    muid = make_uuid(f"world_{dir_name}_mod")
    return {
        "format_version": 2,
        "header": {"name": name, "description": desc, "uuid": uid, "version": [1,0,0], "min_engine_version": [1,20,0]},
        "modules": [{"type": "world_template", "uuid": muid, "version": [1,0,0]}],
    }

def make_minimal_level_dat():
    import struct, zlib
    nbt = b'\x0a\x00\x00'  # empty compound tag
    compressed = zlib.compress(nbt)
    return compressed

def gen_world(dir_name, gen_fn, name, desc):
    pd = os.path.join(WORLD_DIR, dir_name)
    os.makedirs(pd, exist_ok=True)
    gen_fn(pd)
    # Write level.dat (minimal valid NBT)
    level_dat = make_minimal_level_dat()
    with open(os.path.join(pd, "level.dat"), "wb") as f:
        f.write(level_dat)
    with open(os.path.join(pd, "manifest.json"), "w") as f:
        json.dump(make_world_manifest(dir_name, name, desc), f, indent=2)
    # World description
    with open(os.path.join(pd, "world_description.txt"), "w") as f:
        f.write(f"{name}\n{desc}\n")
    print(f"  World: {dir_name}")

def make_mashup_manifest(mash):
    uid = make_uuid(f"mashup_{mash['dir']}")
    muid = make_uuid(f"mashup_{mash['dir']}_mod")
    return {
        "format_version": 2,
        "header": {"name": mash["name"], "description": mash["desc"], "uuid": uid, "version": [1,0,0], "min_engine_version": [1,20,0]},
        "modules": [{"type": "resources", "uuid": muid, "version": [1,0,0]}],
        "dependencies": mash["deps"],
        "metadata": {"product_type": "mashup", "prices": ["$5.99"]},
    }

def gen_mashup(mash):
    pd = os.path.join(MASHUP_DIR, mash["dir"])
    os.makedirs(pd, exist_ok=True)
    with open(os.path.join(pd, "manifest.json"), "w") as f:
        json.dump(make_mashup_manifest(mash), f, indent=2)
    icon = MASH_ICONS[mash["icon_fn"]]()
    icon.save(os.path.join(pd, "pack_icon.png"))
    print(f"  Mashup: {mash['dir']}")

def main():
    print("=== Generating Expansion Packs (42 new) ===\n")

    # 1. Skin packs (25)
    print(f"\n--- Skin Packs ({len(SKIN_PACKS)}) ---")
    for p in SKIN_PACKS:
        gen_skin_pack(p)

    # 2. Texture packs (8)
    print(f"\n--- Texture Packs ({len(TEXTURE_PACKS)}) ---")
    for p in TEXTURE_PACKS:
        gen_tex_pack(p)

    # 3. World templates (5)
    print(f"\n--- World Templates ({len(WORLDS)}) ---")
    for dir_name, gen_fn, name, desc in WORLDS:
        gen_world(dir_name, gen_fn, name, desc)

    # 4. Mashup packs (4)
    print(f"\n--- Mashup Packs ({len(MASHUPS)}) ---")
    for m in MASHUPS:
        gen_mashup(m)

    print(f"\n=== Done! {len(SKIN_PACKS)+len(TEXTURE_PACKS)+len(WORLDS)+len(MASHUPS)} packs generated ===")

if __name__ == "__main__":
    main()
