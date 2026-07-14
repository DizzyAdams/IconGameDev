import os
import json
from pathlib import Path
from PIL import Image

from src.generators.base_generator import BaseGenerator
from src.generators.skin_generator import SkinPackGenerator
from src.generators.texture_generator import TexturePackGenerator
from src.generators.world_generator import WorldTemplateGenerator

class MashupPackGenerator(BaseGenerator):
    def __init__(self, registry_path=None):
        super().__init__(registry_path)
        self.skin_gen = SkinPackGenerator(registry_path)
        self.tex_gen = TexturePackGenerator(registry_path)
        self.world_gen = WorldTemplateGenerator(registry_path)

    def generate(self, output_dir: Path, pack_dir_name: str, name: str, desc: str,
                 world_draw_fn, world_bg: tuple, skins: list,
                 texture_modify, texture_sz: int, texture_noise: int) -> Path:
        """
        Generates a unified mashup pack combining world, skin, and texture sub-components.
        """
        pack_dir = Path(output_dir) / pack_dir_name
        pack_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generate World Template sub-component in the same directory
        self.world_gen.generate(output_dir, pack_dir_name, name, desc, world_draw_fn, world_bg)

        # 2. Generate Skin Pack sub-component in the same directory
        self.skin_gen.generate(output_dir, pack_dir_name, name, desc, skins)

        # 3. Generate Texture Pack sub-component in the same directory
        self.tex_gen.generate(output_dir, pack_dir_name, name, desc, texture_modify, texture_sz, texture_noise)

        # 4. Generate Mashup-specific manifest.json to overwrite components' manifests
        uuids = self.get_uuids(f"mashup_{pack_dir_name}")
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
            "metadata": {
                "product_type": "mashup"
            }
        }

        with open(pack_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        return pack_dir
