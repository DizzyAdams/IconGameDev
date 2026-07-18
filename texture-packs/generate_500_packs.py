#!/usr/bin/env python3
"""
Generator for 500 Minecraft Bedrock Texture Packs
Procedural textures via PIL — no IP, all original
"""
import os, json, math, random, struct, zlib, io
from PIL import Image, ImageFilter, ImageDraw, ImageChops

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
random.seed(42)

# ── 500 pack names across themes ──────────────────────────────────
THEMES = {
    "natural": [
        "Verdant Valley", "Crimson Forest", "Amber Plains", "Sapphire Shores", "Jade Jungle",
        "Coral Reef", "Autumn Grove", "Spring Meadow", "Desert Dunes", "Tundra Wilds",
        "Rainforest Canopy", "Volcanic Slope", "Glacial Peaks", "Mangrove Delta", "Savanna Sun",
        "Cherry Blossom", "Bamboo Forest", "Lavender Fields", "Pine Highlands", "Mossy Cavern",
        "Wildflower Patch", "Riverstone", "Crystal Lake", "Sunflower Valley", "Fern Grotto",
        "Maple Woods", "Cactus Flat", "Lily Pond", "Hickory Forest", "Coastal Cliffs",
        "Boulder Field", "Thornbrush", "Alpine Tundra", "Cypress Swamp", "Redwood Basin",
        "Grassland Panorama", "Oasis Springs", "Canyon Rim", "Iceberg Strait", "Seagrass Meadow",
        "Dewdrop Garden", "Hazel Woods", "Obsidian Shore", "Pumice Desert", "Slate Mountains",
        "Basalt Columns", "Tuya Plateau", "Fjord Edge", "Lagoon Shallows", "Salt Flats",
        "Willow Creek", "Poppy Field", "Honeysuckle", "Clover Patch", "Buttercup Hill",
    ],
    "medieval": [
        "Stone Keep", "Iron Bastion", "Cobblestone Alley", "Royal Throne", "Knight's Honor",
        "Cathedral Vault", "Castle Ward", "Merchant Quarter", "Dungeon Deep", "Rampart Watch",
        "Tavern Hearth", "Blacksmith Forge", "Chapel Light", "Drawbridge", "Palisade Wall",
        "Guard Tower", "Market Square", "Candlekeep", "Great Hall", "Armory Vault",
        "Moonsilver", "Kingsroad", "Mill Wheel", "Granary Store", "Stable Hayloft",
        "Courtyard Stone", "Banquet Table", "Wine Cellar", "Scroll Library", "Wizard Spire",
        "Barracks Row", "Siege Camp", "Herbalist Hut", "Fletcher Shop", "Tannery Row",
        "Jousting Field", "Keep Gate", "Barbican", "Curtain Wall", "Moat Crossing",
        "Cleric Shrine", "Guildhall", "Treasury Vault", "Sentinel Post", "Watchtower Peak",
        "Inn Commonroom", "Alchemist Lab", "Map Room", "War Council", "Crown Jewels",
        "Peasant Cottage", "Lord Manor", "Serf Field", "Abbey Cloister", "Pilgrim Path",
    ],
    "fantasy": [
        "Elven Glade", "Dwarf Hall", "Fairy Ring", "Dragon Lair", "Phoenix Ascent",
        "Unicorn Valley", "Griffin Aerie", "Mermaid Cove", "Centaur Plains", "Pegasus Sky",
        "Goblin Warren", "Troll Bridge", "Ogre Marsh", "Witch Hut", "Warlock Sanctum",
        "Sorcerer Tower", "Enchanted Forest", "Mystic Well", "Arcane Library", "Rune Stone",
        "Starlight Temple", "Moonwell", "Sunbeam Altar", "Shadow Vale", "Twilight Woods",
        "Crystal Cave", "Ethereal Plains", "Spirit Glen", "Fey Crossing", "Blighted Moor",
        "Ivy Tower", "Thorn Castle", "Glass Spire", "Obsidian Hold", "Amethyst Throne",
        "Emerald Sanctuary", "Ruby Forge", "Sapphire Lagoon", "Diamond Vault", "Opal Gate",
        "Mythril Mine", "Adamant Wall", "Void Portal", "Astral Plane", "Dream Weave",
        "Nightmare Realm", "Celestial Terrace", "Prism Bridge", "Echo Cave", "Mirage Desert",
        "Hollow Tree", "Glimmer Pond", "Whispering Wood", "Gaia Heart", "Primordial Spring",
    ],
    "sci-fi": [
        "Neon Grid", "Cyber Station", "Holo Deck", "Quantum Lab", "Void Cruiser",
        "Star Haven", "Mars Colony", "Lunar Base", "Solar Array", "Asteroid Mine",
        "Space Dock", "Warp Core", "Shield Matrix", "Laser Turret", "Plasma Conduit",
        "Circuit Board", "Server Farm", "Data Nexus", "Binary Stream", "Pixel Horizon",
        "Hive Mind", "Synthetic Realm", "Nano Forge", "Zero Point", "Hyper Gate",
        "Dark Matter", "Photon Array", "Gravity Well", "Tesla Coil", "Flux Capacitor",
        "Android Factory", "Drone Bay", "Control Room", "Observation Deck", "Cryo Chamber",
        "Hydroponic Bay", "Med Bay", "Engine Core", "Bridge Command", "Airlock Entry",
        "Transporter Pad", "Holodeck", "Replicator Lab", "Stasis Pod", "Telemetry Array",
        "Signal Tower", "Orbital Platform", "Research Station", "Refinery Hub", "Cargo Bay",
        "Mining Rig", "Sentinel Drone", "Ion Cannon", "Terraformer", "Colony Dome",
    ],
    "cartoon": [
        "Toon Town", "Candy Land", "Jelly World", "Bubble Pop", "Rainbow Road",
        "Cartoon Network", "Comic Strip", "Pixel Party", "Gummy Grove", "Lollipop Lane",
        "Goo Lagoon", "Silly Valley", "Whimsy Woods", "Doodle Pad", "Scribble Zone",
        "Pastel Park", "Fuzzy Fields", "Bouncy Castle", "Tickle Creek", "Giggle Gorge",
        "Wacky Woods", "Zany Hill", "Loony Lake", "Quirky Quarry", "Funky Forest",
        "Jolly Jungle", "Cheerful Canyon", "Happy Hollow", "Merry Meadow", "Sunny Shore",
        "Blob World", "Splat Town", "Ink Well", "Crayon Cave", "Marker Isle",
        "Chalk Zone", "Glitter Gulch", "Sparkle Springs", "Marshmallow Mountain", "Cupcake Coast",
        "Sprinkle Summit", "Frosting Falls", "Jellybean Junction", "Cotton Candy Cloud", "Caramel Creek",
        "Bubblegum Bridge", "Licorice Lane", "Gumball Grove", "Taffy Town", "Fudge Fields",
        "Waffle Woods", "Pancake Plains", "Donut Desert", "Cookie Canyon", "Candy Cane Forest",
    ],
    "realistic": [
        "HD Natural", "Ultra Stone", "Photo Real", "True Grass", "Real Wood",
        "Authentic Dirt", "Genuine Sand", "Actual Water", "Real Rock", "Genuine Gravel",
        "True Metal", "Real Gold", "Silver Vein", "Diamond Cut", "Iron Wrought",
        "Stone Wall", "Brick Facade", "Concrete Mix", "Asphalt Road", "Marble Tile",
        "Tile Floor", "Plank Deck", "Slate Roof", "Shingle Cover", "Granite Block",
        "Sandstone", "Limestone", "Obsidian Glass", "Lava Flow", "Snow Cap",
        "Ice Sheet", "Mud Crack", "Clay Deposit", "Soil Layer", "Pebble Path",
        "Cobble Street", "Pavement", "Terracotta", "Porcelain", "Ceramic Glaze",
        "Canvas Weave", "Leather Grain", "Paper Texture", "Fabric Cloth", "Wool Knit",
        "Burlap Sack", "Satin Sheen", "Velvet Touch", "Denim Blue", "Linen Weave",
    ],
    "steampunk": [
        "Brass Gear", "Copper Pipe", "Steam Core", "Clock Tower", "Airship Deck",
        "Cogwheel", "Pressure Valve", "Boiler Room", "Piston Engine", "Vapor Trail",
        "Brass Compass", "Sextant View", "Riveted Plate", "Iron Lattice", "Gauge Panel",
        "Leather Bind", "Canvas Balloon", "Propeller Spin", "Gearshift", "Flywheel",
        "Anvil Forge", "Bellows", "Crank Shaft", "Hydraulic Press", "Steam Whistle",
        "Pendulum", "Chronometer", "Calipers", "Vernier Scale", "Torsion Spring",
        "Ratchet Gear", "Cam Shaft", "Spindle", "Axle Joint", "Bearing Cage",
        "Chain Link", "Pulley Wheel", "Winch Drum", "Capstan", "Rudder Plate",
        "Keel Beam", "Hull Rivet", "Mast Bracket", "Rigging Knot", "Lantern Glow",
        "Furnace Door", "Ash Pan", "Smoke Stack", "Condenser Coil", "Turbine Blade",
    ],
}

ALL_PACKS = []
for theme, packs in THEMES.items():
    for name in packs:
        ALL_PACKS.append((theme, name))

# Ensure exactly 500
assert len(ALL_PACKS) == 500, f"Expected 500 packs, got {len(ALL_PACKS)}"

RESOLUTION_TIERS = [
    ("256x", 256, 1.99),
    ("512x", 512, 3.99),
    ("1024x", 1024, 5.99),
]

UUID_NAMESPACE = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

def make_uuid(seed_str):
    return str(uuid.uuid5(UUID_NAMESPACE, seed_str))

# ── Procedural texture generators ────────────────────────────────

def _noise(w, h, scale=1.0):
    """Simple value noise"""
    img = Image.new("L", (w, h))
    pix = img.load()
    for x in range(w):
        for y in range(h):
            pix[x, y] = int(random.random() * 255)
    if scale > 1:
        img = img.resize((int(w/scale), int(h/scale)), Image.NEAREST).resize((w, h), Image.LINEAR)
    return img

def _smooth_noise(w, h, octaves=3):
    base = Image.new("L", (w, h))
    for o in range(octaves):
        layer = _noise(w, h, 2**o)
        base = ImageChops.add(base, ImageChops.multiply(layer, Image.new("L", (w, h), 128)))
    return base.point(lambda x: min(int(x/octaves), 255))

def _tileable(img):
    """Make an image tileable by blurring edges"""
    w, h = img.size
    # Blend edges with mirrored version
    blend = 8
    l = img.crop((0, 0, blend, h))
    r = img.crop((w-blend, 0, w, h)).transpose(Image.FLIP_LEFT_RIGHT)
    t = img.crop((0, 0, w, blend))
    b = img.crop((0, h-blend, w, h)).transpose(Image.FLIP_TOP_BOTTOM)
    img.paste(Image.blend(l, r, 0.5), (0, 0))
    return img

def gen_grass(w, h, theme_idx):
    colors = [(107,142,35), (85,107,47), (34,139,34), (0,100,0), (60,179,113),
              (154,205,50), (173,255,47), (124,252,0), (50,205,50), (144,238,144)]
    if theme_idx > 6:
        colors = [(139,90,43), (160,82,45), (205,133,63), (210,180,140), (188,143,143)]
    c = random.choice(colors)
    noise = _smooth_noise(w, h, 2)
    r = noise.point(lambda x: int(c[0] * x/255 * 0.5 + c[0]*0.5))
    g = noise.point(lambda x: int(c[1] * x/255 * 0.5 + c[1]*0.5))
    b = noise.point(lambda x: int(c[2] * x/255 * 0.5 + c[2]*0.5))
    img = Image.merge("RGB", (r, g, b))
    return _tileable(img)

def gen_stone(w, h, theme_idx):
    gray = random.randint(80, 160)
    noise = _smooth_noise(w, h, 3)
    r = noise.point(lambda x: int(gray * (x/255) * 0.4 + gray*0.6))
    g = noise.point(lambda x: int(gray * (x/255) * 0.4 + gray*0.6))
    b = noise.point(lambda x: int(gray * (x/255) * 0.4 + gray*0.6))
    img = Image.merge("RGB", (r, g, b))
    draw = ImageDraw.Draw(img)
    for _ in range(w//4):
        x, y = random.randint(0,w-1), random.randint(0,h-1)
        draw.line([(x,y), (x+random.randint(2,8), y+random.randint(-2,2))], fill=(0,0,0,30), width=1)
    return _tileable(img)

def gen_wood(w, h, theme_idx):
    colors = [(139,90,43), (160,82,45), (205,133,63), (222,184,135), (210,180,140),
              (101,67,33), (92,51,23), (128,64,0), (72,38,12), (160,120,80)]
    c = random.choice(colors)
    img = Image.new("RGB", (w, h), c)
    draw = ImageDraw.Draw(img)
    spacing = random.randint(4, 12)
    for y in range(0, h, spacing):
        v = random.randint(-3, 3)
        draw.line([(0, y+v), (w-1, y+v+random.randint(-1,1))], fill=(max(0,c[0]-30), max(0,c[1]-20), max(0,c[2]-15)), width=random.randint(1,3))
    noise = _smooth_noise(w, h, 1)
    for x in range(w):
        for y in range(h):
            p = img.getpixel((x,y))
            n = noise.getpixel((x,y))/255
            img.putpixel((x,y), tuple(min(255, int(v * (0.85 + n*0.3))) for v in p))
    return _tileable(img)

def gen_dirt(w, h, theme_idx):
    colors = [(139,119,90), (160,140,110), (120,100,70), (100,80,50), (150,130,100)]
    c = random.choice(colors)
    noise = _smooth_noise(w, h, 2)
    r = noise.point(lambda x: int(c[0] * (x/255) * 0.3 + c[0]*0.7))
    g = noise.point(lambda x: int(c[1] * (x/255) * 0.3 + c[1]*0.7))
    b = noise.point(lambda x: int(c[2] * (x/255) * 0.3 + c[2]*0.7))
    img = Image.merge("RGB", (r, g, b))
    draw = ImageDraw.Draw(img)
    for _ in range(w*h//500):
        x, y = random.randint(0,w-1), random.randint(0,h-1)
        draw.point((x,y), fill=(0,0,0,20))
    return _tileable(img)

def gen_sand(w, h, theme_idx):
    colors = [(238,214,175), (244,228,196), (222,198,160), (255,229,180), (210,185,150)]
    c = random.choice(colors)
    noise = _smooth_noise(w, h, 2)
    r = noise.point(lambda x: int(c[0] * (x/255) * 0.15 + c[0]*0.85))
    g = noise.point(lambda x: int(c[1] * (x/255) * 0.15 + c[1]*0.85))
    b = noise.point(lambda x: int(c[2] * (x/255) * 0.15 + c[2]*0.85))
    img = Image.merge("RGB", (r, g, b))
    return _tileable(img)

def gen_water(w, h, theme_idx):
    colors = [(30,144,255), (0,191,255), (65,105,225), (25,25,112), (70,130,180),
              (0,100,200), (40,120,240), (80,160,255)]
    c = random.choice(colors)
    noise = _smooth_noise(w, h, 2)
    r = noise.point(lambda x: int(c[0] * (x/255) * 0.3 + c[0]*0.7))
    g = noise.point(lambda x: int(c[1] * (x/255) * 0.3 + c[1]*0.7))
    b = noise.point(lambda x: int(c[2] * (x/255) * 0.3 + c[2]*0.7))
    img = Image.merge("RGB", (r, g, b))
    return _tileable(img)

def gen_lava(w, h, theme_idx):
    colors = [(255,69,0), (255,140,0), (255,0,0), (200,0,0), (255,100,0)]
    c = random.choice(colors)
    noise = _smooth_noise(w, h, 2)
    r = noise.point(lambda x: min(255, int(c[0] * (x/255) * 0.4 + c[0]*0.6)))
    g = noise.point(lambda x: min(255, int(c[1] * (x/255) * 0.4 + c[1]*0.6)))
    b = noise.point(lambda x: min(255, int(c[2] * (x/255) * 0.4 + c[2]*0.6)))
    img = Image.merge("RGB", (r, g, b))
    return _tileable(img)

def gen_metal(w, h, theme_idx):
    gray = random.randint(120, 200)
    noise = _smooth_noise(w, h, 2)
    r = noise.point(lambda x: int(gray * (x/255) * 0.3 + gray*0.7))
    g = noise.point(lambda x: int(gray * (x/255) * 0.3 + gray*0.7))
    b = noise.point(lambda x: int(gray * (x/255) * 0.3 + gray*0.7))
    img = Image.merge("RGB", (r, g, b))
    if random.random() > 0.5:
        draw = ImageDraw.Draw(img)
        for _ in range(w//8):
            x = random.randint(0,w-1)
            draw.line([(x,0), (x+random.randint(-2,2), h-1)], fill=(180,180,180,30), width=1)
    return _tileable(img)

def gen_planks(w, h, theme_idx):
    colors = [(139,90,43), (160,82,45), (222,184,135), (210,180,140), (245,222,179)]
    c = random.choice(colors)
    img = Image.new("RGB", (w, h), c)
    draw = ImageDraw.Draw(img)
    bw = w // random.randint(4, 8)
    for x in range(0, w, bw):
        draw.line([(x,0), (x,h-1)], fill=(max(0,c[0]-40), max(0,c[1]-30), max(0,c[2]-20)), width=2)
    noise = _smooth_noise(w, h, 1)
    for x in range(w):
        for y in range(h):
            p = img.getpixel((x,y))
            n = noise.getpixel((x,y))/255
            img.putpixel((x,y), tuple(min(255, int(v * (0.8 + n*0.4))) for v in p))
    return _tileable(img)

def gen_brick(w, h, theme_idx):
    colors = [(178,34,34), (139,0,0), (160,82,45), (205,133,63), (128,0,0)]
    c = random.choice(colors)
    mortar = (80, 80, 80)
    img = Image.new("RGB", (w, h), mortar)
    draw = ImageDraw.Draw(img)
    bh = h // random.randint(4, 6)
    bw = w // random.randint(3, 5)
    offset = 0
    for row in range(h // bh + 1):
        for col in range(w // bw + 2):
            x = col * bw + (offset if row % 2 == 0 else 0)
            y = row * bh
            draw.rectangle([x+1, y+1, x+bw-2, y+bh-2], fill=c)
    return _tileable(img)

def gen_cobblestone(w, h, theme_idx):
    gray = random.randint(80, 140)
    img = Image.new("RGB", (w, h), (gray, gray, gray))
    draw = ImageDraw.Draw(img)
    cell = w // 4
    for gx in range(4):
        for gy in range(4):
            cx, cy = gx*cell, gy*cell
            v = random.randint(-15, 15)
            c = (gray+v, gray+v, gray+v)
            draw.ellipse([cx+2, cy+2, cx+cell-2, cy+cell-2], fill=c)
    noise = _smooth_noise(w, h, 1)
    for x in range(w):
        for y in range(h):
            n = noise.getpixel((x,y))/255
            p = img.getpixel((x,y))
            img.putpixel((x,y), tuple(min(255, int(v * (0.85 + n*0.3))) for v in p))
    return _tileable(img)

def gen_pattern(w, h, pattern_type):
    """Generic geometric pattern"""
    img = Image.new("RGB", (w, h), (30, 30, 40))
    draw = ImageDraw.Draw(img)
    primary = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
    secondary = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
    if pattern_type == "checker":
        cs = w // random.randint(4, 8)
        for x in range(0, w, cs):
            for y in range(0, h, cs):
                if (x//cs + y//cs) % 2 == 0:
                    draw.rectangle([x, y, x+cs-1, y+cs-1], fill=primary)
    elif pattern_type == "dots":
        for _ in range(w*h//200):
            x, y = random.randint(0,w-1), random.randint(0,h-1)
            r = random.randint(2, 6)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=primary)
    elif pattern_type == "stripes":
        spacing = random.randint(8, 20)
        for x in range(0, w, spacing):
            draw.rectangle([x, 0, x+spacing//3, h-1], fill=primary)
    elif pattern_type == "zigzag":
        step = w // 6
        for y in range(0, h, step):
            pts = []
            for x in range(0, w+step, step):
                pts.extend([x, y + (random.randint(-1,1)*step//2)])
            if len(pts) >= 4:
                draw.line(pts, fill=primary, width=2)
    noise = _smooth_noise(w, h, 1)
    for x in range(w):
        for y in range(h):
            n = noise.getpixel((x,y))/255
            p = img.getpixel((x,y))
            img.putpixel((x,y), tuple(min(255, int(v * (0.9 + n*0.2))) for v in p))
    return _tileable(img)

def gen_sky(w, h, theme_idx):
    colors = [(135,206,235), (0,0,139), (25,25,112), (70,130,180), (100,149,237)]
    c = random.choice(colors)
    img = Image.new("RGB", (w, h), c)
    noise = _smooth_noise(w, h, 2)
    for x in range(w):
        for y in range(h):
            n = noise.getpixel((x,y))/255
            img.putpixel((x,y), tuple(min(255, int(v * (0.7 + n*0.6))) for v in c))
    draw = ImageDraw.Draw(img)
    for _ in range(w*h//2000):
        x, y = random.randint(0,w-1), random.randint(0,h//2)
        rs = random.randint(1, 4)
        draw.ellipse([x-rs, y-rs, x+rs, y+rs], fill=(255,255,255,40))
    return _tileable(img)

def gen_item(w, h, item_type, theme_idx):
    """Generate a simple item texture"""
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    colors = [(255,215,0), (192,192,192), (255,69,0), (0,255,0), (0,191,255), (255,20,147)]
    c = random.choice(colors)
    if item_type == "sword":
        draw.rectangle([w//2-2, 0, w//2+2, h//2], fill=c)
        draw.rectangle([w//2-6, h//2, w//2+6, h//2+8], fill=(139,69,19))
    elif item_type == "gem":
        draw.ellipse([4, 4, w-5, h-5], fill=c)
        draw.ellipse([w//4, h//4, w//2, h//2], fill=(255,255,255,80))
    elif item_type == "potion":
        draw.ellipse([w//3, 0, 2*w//3, h], fill=c)
        draw.rectangle([w//3-2, 0, 2*w//3+2, h//6], fill=(192,192,192))
    elif item_type == "coin":
        draw.ellipse([2, 2, w-3, h-3], fill=c)
        draw.text((w//2-4, h//2-6), "$", fill=(0,0,0))
    elif item_type == "feather":
        pts = [(w//2,0), (0,h), (w//2, h-2), (w-1, h)]
        draw.polygon(pts, fill=(255,255,255))
        draw.line([(w//2,0), (w//2, h)], fill=(128,128,128), width=1)
    elif item_type == "scroll":
        draw.rectangle([w//4, 2, 3*w//4, h-3], fill=(245,222,179))
        draw.line([(w//4, 2), (w//4, h-3)], fill=(139,90,43), width=2)
        draw.line([(3*w//4, 2), (3*w//4, h-3)], fill=(139,90,43), width=2)
    elif item_type == "ring":
        draw.ellipse([4, 4, w-5, h-5], outline=c, width=3)
        draw.ellipse([w//3, h//3, 2*w//3, 2*h//3], fill=c)
    return img

TEXTURE_GENERATORS = [
    gen_grass, gen_stone, gen_wood, gen_dirt, gen_sand,
    gen_water, gen_lava, gen_metal, gen_planks, gen_brick,
    gen_cobblestone, gen_sky,
]

ITEM_TYPES = ["sword", "gem", "potion", "coin", "feather", "scroll", "ring"]

# ── Pack icon generator ──────────────────────────────────────────

def gen_pack_icon(w, h, theme, pack_name):
    """Generate a unique pack icon based on theme and name"""
    img = Image.new("RGB", (w, h), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    # Theme-based color palette
    palette = {
        "natural": [(34,139,34), (107,142,35), (0,100,0), (85,107,47), (60,179,113)],
        "medieval": [(139,90,43), (160,82,45), (128,0,0), (101,67,33), (205,133,63)],
        "fantasy": [(138,43,226), (75,0,130), (218,112,214), (147,0,211), (255,0,255)],
        "sci-fi": [(0,191,255), (0,255,255), (0,255,127), (255,215,0), (173,255,47)],
        "cartoon": [(255,105,180), (255,20,147), (255,69,0), (50,205,50), (255,215,0)],
        "realistic": [(128,128,128), (192,192,192), (169,169,169), (105,105,105), (112,128,144)],
        "steampunk": [(184,134,11), (218,165,32), (160,82,45), (139,90,43), (210,105,30)],
    }
    colors = palette.get(theme, palette["natural"])
    bg_color = random.choice(colors)
    # Background gradient
    for y in range(h):
        t = y / h
        r = int(bg_color[0] * (1-t) + bg_color[0]*0.3*t)
        g = int(bg_color[1] * (1-t) + bg_color[1]*0.3*t)
        b = int(bg_color[2] * (1-t) + bg_color[2]*0.3*t)
        draw.line([(0,y), (w-1,y)], fill=(r,g,b))
    # Decorative elements
    accent = random.choice(colors)
    for _ in range(5):
        cx, cy = random.randint(w//6, 5*w//6), random.randint(h//6, 5*h//6)
        r = random.randint(10, 40)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=accent, width=2)
    # Central icon
    cx, cy = w//2, h//2
    if theme == "natural":
        draw.ellipse([cx-20, cy-20, cx+20, cy+20], fill=(34,139,34))
        draw.line([(cx, cy-30), (cx, cy)], fill=(139,90,43), width=4)
    elif theme == "medieval":
        draw.rectangle([cx-15, cy-25, cx+15, cy+25], fill=(128,128,128))
        draw.polygon([(cx-20, cy-25), (cx+20, cy-25), (cx, cy-40)], fill=(128,0,0))
    elif theme == "fantasy":
        draw.polygon([(cx, cy-30), (cx-25, cy+20), (cx+25, cy+20)], fill=(138,43,226))
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=(255,215,0))
    elif theme == "sci-fi":
        draw.ellipse([cx-20, cy-20, cx+20, cy+20], fill=(0,191,255))
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=(0,255,255))
    elif theme == "cartoon":
        draw.ellipse([cx-20, cy-20, cx+20, cy+20], fill=(255,105,180))
        draw.ellipse([cx-8, cy-12, cx-3, cy-7], fill=(0,0,0))
        draw.ellipse([cx+3, cy-12, cx+8, cy-7], fill=(0,0,0))
    elif theme == "realistic":
        draw.ellipse([cx-20, cy-20, cx+20, cy+20], fill=(128,128,128))
        draw.ellipse([cx-15, cy-15, cx+15, cy+15], fill=(192,192,192))
    elif theme == "steampunk":
        draw.ellipse([cx-20, cy-20, cx+20, cy+20], fill=(184,134,11))
        r = 15
        for a in range(0, 360, 30):
            import math
            ex = cx + int(r * math.cos(math.radians(a)))
            ey = cy + int(r * math.sin(math.radians(a)))
            draw.ellipse([ex-3, ey-3, ex+3, ey+3], fill=(218,165,32))
    # Add border
    draw.rectangle([0, 0, w-1, h-1], outline=(255,255,255,50), width=2)
    return img

# ── UUID helper ─────────────────────────────────────────
import uuid

# ── Main generator ───────────────────────────────────────────────

def generate_pack(pack_dir, theme, pack_name, res_label, res, price):
    """Generate a complete Bedrock texture pack"""
    pack_id = pack_name.lower().replace(" ", "_").replace("'", "")
    pack_uuid = make_uuid(f"texture-{pack_id}-{res_label}")
    module_uuid = make_uuid(f"module-{pack_id}-{res_label}")

    # manifest.json (v2)
    manifest = {
        "format_version": 2,
        "header": {
            "name": f"§l{pack_name}",
            "description": f"§7{res_label} Texture Pack — {pack_name}\n§e${price:.2f}\n§8Theme: {theme.title()} | Resolution: {res_label}\nOriginal procedural textures, no IP",
            "uuid": pack_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
            "pack_scope": "world",
        },
        "modules": [
            {
                "type": "resources",
                "uuid": module_uuid,
                "version": [1, 0, 0],
            }
        ],
        "metadata": {
            "authors": ["IconMinemods"],
            "license": "All Rights Reserved — Original procedural textures",
            "price_usd": price,
            "resolution": res_label,
            "theme": theme,
        }
    }

    os.makedirs(pack_dir, exist_ok=True)
    with open(os.path.join(pack_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # pack_icon.png
    icon = gen_pack_icon(res, res, theme, pack_name)
    icon.save(os.path.join(pack_dir, "pack_icon.png"), "PNG")

    # Texture directories
    blocks_dir = os.path.join(pack_dir, "textures", "blocks")
    items_dir = os.path.join(pack_dir, "textures", "items")
    os.makedirs(blocks_dir, exist_ok=True)
    os.makedirs(items_dir, exist_ok=True)

    # Generate block textures
    theme_idx = list(THEMES.keys()).index(theme) if theme in THEMES else 0
    block_names = [
        f"{pack_id}_grass", f"{pack_id}_stone", f"{pack_id}_wood",
        f"{pack_id}_dirt", f"{pack_id}_sand", f"{pack_id}_water",
        f"{pack_id}_planks",
    ]
    generators = [gen_grass, gen_stone, gen_wood, gen_dirt, gen_sand, gen_water, gen_planks]

    for bname, gen in zip(block_names, generators):
        tex = gen(res, res, theme_idx)
        tex.save(os.path.join(blocks_dir, f"{bname}.png"), "PNG")

    if random.random() > 0.5:
        extra = gen_brick(res, res, theme_idx)
        extra.save(os.path.join(blocks_dir, f"{pack_id}_brick.png"), "PNG")

    # Generate item textures
    item_names = [f"{pack_id}_{it}" for it in ITEM_TYPES[:4]]
    for iname, itype in zip(item_names, ITEM_TYPES[:4]):
        tex = gen_item(res, res, itype, theme_idx)
        tex.save(os.path.join(items_dir, f"{iname}.png"), "PNG")


def main():
    # Distribution
    tier_dist = [167, 166, 167]  # total = 500

    pack_idx = 0
    stats = {
        "total_packs": 0,
        "by_resolution": {"256x": 0, "512x": 0, "1024x": 0},
        "by_price": {"1.99": 0, "3.99": 0, "5.99": 0},
        "by_theme": {},
        "errors": [],
    }

    for ti, (res_label, res, price) in enumerate(RESOLUTION_TIERS):
        count = tier_dist[ti]
        packs_for_tier = ALL_PACKS[pack_idx:pack_idx + count]
        pack_idx += count

        print(f"\n{'='*60}")
        print(f"  Generating {count} packs @ {res_label} (${price:.2f})")
        print(f"{'='*60}")

        for theme, pack_name in packs_for_tier:
            pack_id_dir = pack_name.lower().replace(" ", "_").replace("'", "")
            pack_dir = os.path.join(BASE_DIR, f"{theme}_{pack_id_dir}_{res_label}")
            try:
                generate_pack(pack_dir, theme, pack_name, res_label, res, price)
                stats["total_packs"] += 1
                stats["by_resolution"][res_label] = stats["by_resolution"].get(res_label, 0) + 1
                stats["by_price"][str(price)] = stats["by_price"].get(str(price), 0) + 1
                stats["by_theme"][theme] = stats["by_theme"].get(theme, 0) + 1
            except Exception as e:
                stats["errors"].append((pack_name, str(e)))
                print(f"  ERROR: {pack_name}: {e}")

            if stats["total_packs"] % 50 == 0:
                print(f"  ... {stats['total_packs']}/500 packs generated")

    # Final report
    print(f"\n{'='*60}")
    print(f"  GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Total packs: {stats['total_packs']}")
    print(f"  By resolution:")
    for res, cnt in sorted(stats["by_resolution"].items()):
        print(f"    {res}: {cnt}")
    print(f"  By price:")
    for price, cnt in sorted(stats["by_price"].items()):
        print(f"    ${price}: {cnt}")
    print(f"  By theme:")
    for theme, cnt in sorted(stats["by_theme"].items()):
        print(f"    {theme}: {cnt}")
    if stats["errors"]:
        print(f"  Errors: {len(stats['errors'])}")
        for e in stats["errors"][:5]:
            print(f"    {e[0]}: {e[1]}")
    else:
        print(f"  Errors: 0")

    # Also verify some packs
    print(f"\n  --- Sample pack verification ---")
    sample_dirs = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and d != "__pycache__"][:3]
    for sd in sample_dirs:
        sd_path = os.path.join(BASE_DIR, sd)
        manifest_path = os.path.join(sd_path, "manifest.json")
        icon_path = os.path.join(sd_path, "pack_icon.png")
        blocks = os.listdir(os.path.join(sd_path, "textures", "blocks")) if os.path.exists(os.path.join(sd_path, "textures", "blocks")) else []
        items = os.listdir(os.path.join(sd_path, "textures", "items")) if os.path.exists(os.path.join(sd_path, "textures", "items")) else []
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                m = json.load(f)
            print(f"\n  Pack: {sd}")
            print(f"    Name: {m['header']['name']}")
            print(f"    Resolution: {m['metadata']['resolution']}")
            print(f"    Price: ${m['metadata']['price_usd']}")
            print(f"    Theme: {m['metadata']['theme']}")
            print(f"    Block textures: {len(blocks)}")
            print(f"    Item textures: {len(items)}")

    # Save report
    report_path = os.path.join(BASE_DIR, "REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Texture Packs Generation Report\n\n")
        f.write(f"**Total packs:** {stats['total_packs']}\n")
        f.write(f"**Total files:** {sum(stats['by_resolution'].values())} packs\n\n")
        f.write(f"## Resolution Breakdown\n\n")
        for res, cnt in sorted(stats["by_resolution"].items()):
            f.write(f"- **{res}**: {cnt} packs\n")
        f.write(f"\n## Price Breakdown\n\n")
        for price, cnt in sorted(stats["by_price"].items()):
            f.write(f"- **${price}**: {cnt} packs\n")
        f.write(f"\n## Theme Breakdown\n\n")
        for theme, cnt in sorted(stats["by_theme"].items()):
            f.write(f"- **{theme}**: {cnt} packs\n")
        f.write(f"\n## Errors\n\n")
        if stats["errors"]:
            for e in stats["errors"]:
                f.write(f"- {e[0]}: {e[1]}\n")
        else:
            f.write("None\n")
        f.write(f"\n## Total Size\n\n")
        total_size = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, dn, fn in os.walk(BASE_DIR)
            for f in fn
            if not f.endswith(".py")
        )
        f.write(f"**{total_size / (1024*1024):.1f} MB**\n")

    print(f"\n  Report saved to: {report_path}")
    return stats

if __name__ == "__main__":
    stats = main()
    print(f"\n  DONE — {stats['total_packs']} texture packs generated.")
