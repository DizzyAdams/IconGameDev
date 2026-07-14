import os
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw
from src.generators.base_generator import BaseGenerator

class SkinPackGenerator(BaseGenerator):
    def gen_skin_tex(self, name: str, primary: tuple, secondary: tuple) -> Image.Image:
        img = Image.new('RGBA', (64, 64), (*primary, 255))
        pixels = img.load()
        # Seed locally using name hash to be deterministic and stable
        seed_val = hash(name) & 0xFFFFFFFF
        rng = random.Random(seed_val)
        pattern = rng.choice(['stripe_h', 'stripe_v', 'check', 'diag', 'dots', 'cross'])
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
                    pixels[x, y] = (int(r*0.2+sr*0.8), int(g*0.2+sg*0.8), int(b*0.2+sb*0.8), 255)
        return img

    def gen_skin_icon(self, colors: list) -> Image.Image:
        icon = Image.new('RGBA', (300, 300), (30, 30, 40, 255))
        draw = ImageDraw.Draw(icon)
        cx, cy = 150, 150
        for i, c in enumerate(colors):
            angle = i * 2.0
            px = cx + int(80 * math.cos(angle))
            py = cy + int(80 * math.sin(angle))
            draw.ellipse([px-40, py-40, px+40, py+40], fill=(*c, 255))
        return icon

    def generate(self, output_dir: Path, pack_dir_name: str, name: str, desc: str, skins: list) -> Path:
        """
        Generates a skin pack.
        skins: list of tuples/lists: (skin_name, primary_color_rgb, secondary_color_rgb)
        """
        if name is None or not isinstance(name, str):
            raise TypeError("Name must be a string")
        if desc is None or not isinstance(desc, str):
            raise TypeError("Description must be a string")
        if not isinstance(skins, (list, tuple)):
            raise TypeError("Skins must be a list or tuple")

        pack_dir = Path(output_dir) / pack_dir_name
        skins_dir = pack_dir / "textures" / "skins"
        skins_dir.mkdir(parents=True, exist_ok=True)

        sanitized_skins = []
        for sname, prim, sec in skins:
            if not isinstance(sname, str):
                raise TypeError("Skin name must be a string")
            
            # Sanitize skin name to prevent path traversal
            sanitized_sname = os.path.basename(sname).replace("..", "").replace("/", "").replace("\\", "")
            if not sanitized_sname:
                sanitized_sname = "default_skin"

            # Validate colors
            for color, color_label in [(prim, "primary"), (sec, "secondary")]:
                if not isinstance(color, (tuple, list)) or len(color) != 3:
                    raise TypeError(f"Skin {color_label} color must be a tuple/list of 3 elements")
                for c in color:
                    if not isinstance(c, (int, float)) or isinstance(c, bool):
                        raise TypeError(f"Color component must be a number, got {type(c)}")
                    if c < 0 or c > 255:
                        raise ValueError(f"Color component {c} out of bounds [0, 255]")

            # Sanitize colors (ensure RGB components are clipped/validated)
            clipped_prim = tuple(max(0, min(255, int(c))) for c in prim)
            clipped_sec = tuple(max(0, min(255, int(c))) for c in sec)

            sanitized_skins.append((sanitized_sname, clipped_prim, clipped_sec))

        for sname, prim, sec in sanitized_skins:
            img = self.gen_skin_tex(sname, prim, sec)
            img.save(skins_dir / f"{sname}.png")

        all_colors = [s[1] for s in sanitized_skins] + [s[2] for s in sanitized_skins]
        icon = self.gen_skin_icon(all_colors)
        icon.save(skins_dir / "icon.png")

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
                    "type": "skin_pack",
                    "uuid": uuids["module"],
                    "version": [1, 0, 0]
                }
            ],
        }

        with open(pack_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        skins_json = {
            "skins": [
                {
                    "localization_name": sname,
                    "geometry": "geometry.humanoid.custom",
                    "texture": f"{sname}.png",
                    "type": "free"
                }
                for sname, _, _ in sanitized_skins
            ],
            "serialize_name": name,
            "localization_name": name,
        }

        with open(pack_dir / "skins.json", "w") as f:
            json.dump(skins_json, f, indent=2)

        return pack_dir
