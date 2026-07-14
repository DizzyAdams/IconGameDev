import os
import random
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

from src.generators.skin_generator import SkinPackGenerator
from src.packagers.packager import Packager
from src.validators.bedrock_validator import BedrockValidator

def _generate_and_package_volume(args):
    vol_num, output_dir, dist_dir, skins_chunk, registry_path = args
    gen = SkinPackGenerator(registry_path=registry_path)
    pack_dir_name = f"skin-pack-vol-{vol_num}"
    name = f"Skin Pack Volume {vol_num}"
    desc = f"Volume {vol_num} of the massive 500-skin collection."
    
    # Generate pack folder
    pack_dir = gen.generate(output_dir, pack_dir_name, name, desc, skins_chunk)
    
    # Package into .mcpack
    archive_path = Packager.package(pack_dir, dist_dir)
    return str(archive_path)

class BulkIngestor:
    def __init__(self, output_dir: Path, dist_dir: Path, registry_path=None):
        self.output_dir = Path(output_dir)
        self.dist_dir = Path(dist_dir)
        self.registry_path = registry_path

    def run(self, num_skins=500, skins_per_pack=10):
        if not isinstance(skins_per_pack, int) or isinstance(skins_per_pack, bool):
            raise TypeError("skins_per_pack must be an integer")
        if skins_per_pack <= 0:
            raise ValueError("skins_per_pack must be greater than zero and must not be zero")

        # 1. Generate skin inputs deterministically
        rng = random.Random(42)
        skins = []
        for i in range(num_skins):
            skin_name = f"Skin_{i}"
            prim = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            sec = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            skins.append((skin_name, prim, sec))

        # 2. Chunk into volumes of 10 skins
        chunks = [skins[i:i + skins_per_pack] for i in range(0, len(skins), skins_per_pack)]

        # Prepare arguments for multiprocessing
        tasks = []
        for idx, chunk in enumerate(chunks):
            vol_num = idx + 1
            tasks.append((vol_num, self.output_dir, self.dist_dir, chunk, self.registry_path))

        # 3. Parallel execution using ProcessPoolExecutor
        results = []
        with ProcessPoolExecutor() as executor:
            for path_str in executor.map(_generate_and_package_volume, tasks):
                results.append(Path(path_str))

        # 4. Validate each built volume
        validator = BedrockValidator()
        validation_results = []
        for path in results:
            val_res = validator.validate_mcpack(str(path))
            validation_results.append(val_res)
            
        return results, validation_results
