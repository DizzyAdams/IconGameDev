import json, os, base64, io
from PIL import Image

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "blockbench-templates")
OUTPUT_DIR = os.path.join(TEMPLATES_DIR, "generated")

HEAD = {
    "name": "head", "from": [-4, 24, -4], "to": [4, 32, 4],
    "faces": {
        "north": {"uv": [8, 8, 16, 16]},
        "south": {"uv": [24, 8, 32, 16]},
        "east": {"uv": [0, 8, 8, 16]},
        "west": {"uv": [16, 8, 24, 16]},
        "up": {"uv": [8, 0, 16, 8]},
        "down": {"uv": [16, 0, 24, 8]},
    },
}

BODY = {
    "name": "body", "from": [-4, 12, -2], "to": [4, 24, 2],
    "faces": {
        "north": {"uv": [20, 16, 28, 28]},
        "south": {"uv": [32, 16, 40, 28]},
        "east": {"uv": [16, 16, 20, 28]},
        "west": {"uv": [28, 16, 32, 28]},
        "up": {"uv": [20, 12, 28, 16]},
        "down": {"uv": [28, 12, 36, 16]},
    },
}

RIGHT_ARM = {
    "name": "right_arm", "from": [1, 12, -2], "to": [5, 24, 2],
    "faces": {
        "north": {"uv": [56, 16, 60, 28]},
        "south": {"uv": [52, 16, 56, 28]},
        "east": {"uv": [60, 16, 64, 28]},
        "west": {"uv": [52, 28, 56, 40]},
        "up": {"uv": [56, 12, 60, 16]},
        "down": {"uv": [60, 12, 64, 16]},
    },
}

LEFT_ARM = {
    "name": "left_arm", "from": [-5, 12, -2], "to": [-1, 24, 2],
    "faces": {
        "north": {"uv": [40, 16, 44, 28]},
        "south": {"uv": [48, 16, 52, 28]},
        "east": {"uv": [36, 16, 40, 28]},
        "west": {"uv": [44, 16, 48, 28]},
        "up": {"uv": [40, 12, 44, 16]},
        "down": {"uv": [44, 12, 48, 16]},
    },
}

LEFT_LEG = {
    "name": "left_leg", "from": [-4, 0, -2], "to": [0, 12, 2],
    "faces": {
        "north": {"uv": [4, 16, 8, 28]},
        "south": {"uv": [12, 16, 16, 28]},
        "east": {"uv": [0, 16, 4, 28]},
        "west": {"uv": [8, 16, 12, 28]},
        "up": {"uv": [4, 12, 8, 16]},
        "down": {"uv": [8, 12, 12, 16]},
    },
}

RIGHT_LEG = {
    "name": "right_leg", "from": [0, 0, -2], "to": [4, 12, 2],
    "faces": {
        "north": {"uv": [20, 48, 24, 60]},
        "south": {"uv": [28, 48, 32, 60]},
        "east": {"uv": [16, 48, 20, 60]},
        "west": {"uv": [24, 48, 28, 60]},
        "up": {"uv": [20, 44, 24, 48]},
        "down": {"uv": [24, 44, 28, 48]},
    },
}

BASE_ELEMENTS = [HEAD, BODY, LEFT_ARM, RIGHT_ARM, LEFT_LEG, RIGHT_LEG]

ANIME_HEAD = {
    "name": "head", "from": [-5, 23, -5], "to": [5, 33, 5],
    "faces": {
        "north": {"uv": [8, 8, 18, 18]},
        "south": {"uv": [28, 8, 38, 18]},
        "east": {"uv": [0, 8, 8, 18]},
        "west": {"uv": [18, 8, 28, 18]},
        "up": {"uv": [8, 0, 18, 8]},
        "down": {"uv": [18, 0, 28, 8]},
    },
}

ANIME_BODY = {
    "name": "body", "from": [-4, 12, -2], "to": [4, 24, 2],
    "faces": {
        "north": {"uv": [20, 20, 28, 32]},
        "south": {"uv": [32, 20, 40, 32]},
        "east": {"uv": [16, 20, 20, 32]},
        "west": {"uv": [28, 20, 32, 32]},
        "up": {"uv": [20, 16, 28, 20]},
        "down": {"uv": [28, 16, 36, 20]},
    },
}

ANIME_RIGHT_ARM = {
    "name": "right_arm", "from": [1, 12, -2], "to": [4, 24, 2],
    "faces": {
        "north": {"uv": [56, 20, 59, 32]},
        "south": {"uv": [50, 20, 53, 32]},
        "east": {"uv": [59, 20, 64, 32]},
        "west": {"uv": [50, 32, 53, 44]},
        "up": {"uv": [56, 16, 59, 20]},
        "down": {"uv": [59, 16, 64, 20]},
    },
}

ANIME_LEFT_ARM = {
    "name": "left_arm", "from": [-4, 12, -2], "to": [-1, 24, 2],
    "faces": {
        "north": {"uv": [40, 20, 43, 32]},
        "south": {"uv": [49, 20, 52, 32]},
        "east": {"uv": [36, 20, 40, 32]},
        "west": {"uv": [43, 20, 49, 32]},
        "up": {"uv": [40, 16, 43, 20]},
        "down": {"uv": [43, 16, 49, 20]},
    },
}

ANIME_LEFT_LEG = {
    "name": "left_leg", "from": [-4, 0, -2], "to": [0, 12, 2],
    "faces": {
        "north": {"uv": [4, 20, 8, 32]},
        "south": {"uv": [12, 20, 16, 32]},
        "east": {"uv": [0, 20, 4, 32]},
        "west": {"uv": [8, 20, 12, 32]},
        "up": {"uv": [4, 16, 8, 20]},
        "down": {"uv": [8, 16, 12, 20]},
    },
}

ANIME_RIGHT_LEG = {
    "name": "right_leg", "from": [0, 0, -2], "to": [4, 12, 2],
    "faces": {
        "north": {"uv": [20, 48, 24, 60]},
        "south": {"uv": [28, 48, 32, 60]},
        "east": {"uv": [16, 48, 20, 60]},
        "west": {"uv": [24, 48, 28, 60]},
        "up": {"uv": [20, 44, 24, 48]},
        "down": {"uv": [24, 44, 28, 48]},
    },
}

ANIME_ELEMENTS = [ANIME_HEAD, ANIME_BODY, ANIME_LEFT_ARM, ANIME_RIGHT_ARM, ANIME_LEFT_LEG, ANIME_RIGHT_LEG]

TEMPLATES = {
    "classic": {"elements": BASE_ELEMENTS, "outliner_name": "classic_skin"},
    "anime": {"elements": ANIME_ELEMENTS, "outliner_name": "anime_skin"},
}


def interpolate_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def generate_skin_texture(width=64, height=64, primary=(100, 130, 180), secondary=(200, 200, 210)):
    img = Image.new('RGBA', (width, height))
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            t = (x + y) / (width + height)
            if (y // 4) % 3 == 0:
                pixels[x, y] = (*secondary, 255)
            else:
                pixels[x, y] = (*primary, 255)
    return img


def generate_anime_texture(width=64, height=64, primary=(255, 200, 200), secondary=(255, 255, 255)):
    img = Image.new('RGBA', (width, height))
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            if 12 <= y < 20 and 12 <= x < 22:
                dx, dy = x - 17, y - 16
                if abs(dx) < 2 and abs(dy) < 2:
                    c = (40, 40, 40)
                elif 9 <= x < 13 and 14 <= y < 18:
                    c = (40, 40, 40)
                else:
                    c = primary
            else:
                c = primary
            pixels[x, y] = (*c, 255)
    return img


def build_model(elements, texture_img):
    buf = io.BytesIO()
    texture_img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "format_version": "4",
        "resolution": {"width": 64, "height": 64},
        "elements": elements,
        "textures": [{"name": "skin.png", "source": f"data:image/png;base64,{b64}"}],
        "outliner": [{"name": "body_group", "children": [e["name"] for e in elements]}],
    }


def save_bbmodel(name, elements, texture_img, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    model = build_model(elements, texture_img)
    path = os.path.join(output_dir, f"{name}.bbmodel")
    with open(path, 'w') as f:
        json.dump(model, f, indent=2)
    print(f"Generated {path}")
    return path


def save_from_template(name, template_key, texture_fn):
    tpl = TEMPLATES[template_key]
    tex = texture_fn()
    return save_bbmodel(name, tpl["elements"], tex)


if __name__ == "__main__":
    save_from_template("example_classic", "classic", generate_skin_texture)
    save_from_template("example_anime", "anime", generate_anime_texture)
    print("Done. Open .bbmodel files in Blockbench to edit.")
