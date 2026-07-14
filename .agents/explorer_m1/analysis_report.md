# Bedrock MineMods Marketplace-Content Analysis and Design Proposal

## 1. Bulk Ingestion and Compilation of 500 Skins

### 1.1 Codebase Assessment
A thorough analysis of the codebase reveals that:
- There is **no active specification or script** specifically named "bulk ingestion/compilation of 500 skin inputs" in the workspace.
- The `marketplace-content/scripts/generate-massive-packs.py` and `generate-all-skin-packs.py` scripts contain procedural generator routines using the Pillow (`PIL`) library to generate skin PNGs in memory and write them directly to folders.
- There are no physical input folders containing a static batch of 500 player skins.
- The reference to "500 skin inputs" comes from the orchestrator's requirements list (`plan.md` Milestone 4 and `context.md` Acceptance Criteria), which requires compiling a mock batch of 500 skin inputs to `.mcpack` formats.

### 1.2 Performance Bottlenecks & Design Challenges
Generating and zipping 500 skins sequentially presents several bottlenecks:
1. **CPU Overhead**: PIL's pixel loops and drawing routines are CPU-bound. In Python, single-threaded execution will be constrained by the Global Interpreter Lock (GIL).
2. **Disk I/O**: Creating directories and writing 500 PNG files individually to disk before packaging can cause substantial disk I/O bottlenecks.
3. **Memory Consumption**: Holding large amounts of image bytes in memory simultaneously can lead to performance degradation if not batched or streamed.

### 1.3 Proposed Parallel and Batched Implementation
To satisfy performance and resource requirements, we propose utilizing Python's standard library `concurrent.futures.ProcessPoolExecutor` to distribute the CPU-heavy image drawing tasks across multiple processes.

#### Ingestion Approach:
- **Batching**: Group the 500 skins into logical skin packs (e.g., 50 packs of 10 skins, or 5 packs of 100 skins). Bedrock Marketplace skin packs typically contain between 6 and 16 skins. Having 500 skins in a single pack is not recommended due to client-side loading limits.
- **Parallelism**: Use `ProcessPoolExecutor` to spawn multiple worker processes. Each process compiles a complete skin pack folder (generating the 64x64 or 128x128 skin PNGs, the `skins.json`, and the `manifest.json`), then compresses them directly.

#### Pseudo-Code Proposal for `BulkSkinIngestor`:
```python
# C:\Users\forrydev\Desktop\bedrock_minemods\marketplace-content\src\generators\bulk_ingestor.py
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from src.generators.skin_generator import SkinPackGenerator
from src.packagers.packager import Packager
from src.utils.uuid_manager import UUIDManager

def process_pack_batch(pack_config, output_dir, registry_path):
    """Worker function executed in a separate process."""
    # Instantiating dependencies inside worker to avoid serializing locks
    manager = UUIDManager(registry_path=registry_path)
    generator = SkinPackGenerator(uuid_manager=manager)
    
    # 1. Generate the folder structure and files
    pack_dir = generator.generate(pack_config, output_dir)
    
    # 2. Package it to .mcpack
    zip_path = Packager.package(pack_dir, output_dir / "dist")
    return zip_path

class BulkSkinIngestor:
    def __init__(self, output_dir: Path, registry_path: Path):
        self.output_dir = Path(output_dir)
        self.registry_path = Path(registry_path)
        
    def ingest_bulk_skins(self, all_skins_metadata: list, skins_per_pack: int = 10):
        """
        Groups 500 skin metadata definitions, generates packs in parallel, and zips them.
        all_skins_metadata: list of dicts {"name": ..., "primary": ..., "secondary": ...}
        """
        # Chunk 500 skins into packs of size skins_per_pack
        chunks = [all_skins_metadata[i:i + skins_per_pack] for i in range(0, len(all_skins_metadata), skins_per_pack)]
        
        pack_configs = []
        for index, chunk in enumerate(chunks):
            pack_configs.append({
                "name": f"Bulk Skin Pack Volume {index + 1}",
                "description": f"Volume {index + 1} of bulk ingested skins.",
                "dir_name": f"bulk-skins-vol-{index + 1}",
                "skins": chunk
            })
            
        print(f"Scheduling {len(pack_configs)} skin packs for generation (Total: {len(all_skins_metadata)} skins).")
        
        # Parallel execution using ProcessPoolExecutor
        results = []
        max_workers = min(os.cpu_count() or 4, len(pack_configs))
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_pack_batch, config, self.output_dir, self.registry_path)
                for config in pack_configs
            ]
            for fut in futures:
                results.append(fut.result())
                
        return results
```

---

## 2. Generator Class API Design

We will implement the generators inside `src/generators/` using standard object-oriented design, inheriting from a common `BaseGenerator` and integrating the `UUIDManager`.

### 2.1 File Structure under `src/generators/`
```
marketplace-content/src/generators/
├── __init__.py
├── base_generator.py
├── skin_generator.py
├── texture_generator.py
├── world_generator.py
└── mashup_generator.py
```

### 2.2 API Class Contracts and UUID Integration
To guarantee UUID persistence across generation pipelines, the `BaseGenerator` class accepts a `UUIDManager` instance and uses it to resolve deterministic/persistent UUIDs for `manifest.json`.

#### 1. `BaseGenerator` (`src/generators/base_generator.py`)
```python
from abc import ABC, abstractmethod
from pathlib import Path
from src.utils.uuid_manager import UUIDManager

class BaseGenerator(ABC):
    def __init__(self, uuid_manager: UUIDManager = None):
        # Fall back to default location if no manager is supplied
        self.uuid_manager = uuid_manager or UUIDManager()

    def generate_manifest(self, name: str, description: str, pack_key: str, module_type: str, metadata: dict = None) -> dict:
        """Helper to generate a compliant manifest.json schema with persistent UUIDs."""
        uuids = self.uuid_manager.pack_uuids(pack_key)
        manifest = {
            "format_version": 2,
            "header": {
                "name": name,
                "description": description,
                "uuid": uuids["header"],
                "version": [1, 0, 0],
                "min_engine_version": [1, 20, 0]
            },
            "modules": [
                {
                    "type": module_type,
                    "uuid": uuids["module"],
                    "version": [1, 0, 0]
                }
            ]
        }
        if metadata:
            manifest["metadata"] = metadata
        return manifest

    @abstractmethod
    def generate(self, config: dict, output_dir: Path) -> Path:
        """
        Executes pack generation.
        config: dict containing pack attributes (name, skins, colors, etc.)
        output_dir: base folder where the pack directory will be created.
        Returns: Path to the generated pack directory.
        """
        pass
```

#### 2. `SkinPackGenerator` (`src/generators/skin_generator.py`)
```python
import json
from pathlib import Path
from PIL import Image, ImageDraw
from .base_generator import BaseGenerator

class SkinPackGenerator(BaseGenerator):
    def generate(self, config: dict, output_dir: Path) -> Path:
        # Expected config: {"name": str, "description": str, "dir_name": str, "skins": list of (name, primary_rgb, secondary_rgb)}
        pack_dir = Path(output_dir) / config["dir_name"]
        skins_dir = pack_dir / "textures" / "skins"
        skins_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Generate skin PNGs (64x64 default)
        for name, primary, secondary in config["skins"]:
            img = self._generate_skin_image(primary, secondary)
            img.save(skins_dir / f"{name}.png")
            
        # 2. Generate pack icon.png
        icon = self._generate_pack_icon([c[1] for c in config["skins"]] + [c[2] for c in config["skins"]])
        icon.save(skins_dir / "icon.png")
        
        # 3. Write manifest.json
        manifest = self.generate_manifest(
            name=config["name"],
            description=config["description"],
            pack_key=config["dir_name"],
            module_type="skin_pack"
        )
        with open(pack_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
            
        # 4. Write skins.json
        skins_json = {
            "skins": [
                {
                    "localization_name": name,
                    "geometry": "geometry.humanoid.custom",
                    "texture": f"{name}.png",
                    "type": "free"
                }
                for name, _, _ in config["skins"]
            ],
            "serialize_name": config["name"],
            "localization_name": config["name"]
        }
        with open(pack_dir / "skins.json", "w") as f:
            json.dump(skins_json, f, indent=2)
            
        return pack_dir

    def _generate_skin_image(self, primary, secondary) -> Image.Image:
        # Implements standard pattern generation (stripe/check) in a 64x64 RGBA canvas
        img = Image.new('RGBA', (64, 64), (*primary, 255))
        pixels = img.load()
        for x in range(64):
            for y in range(64):
                if (x + y) % 8 < 4:
                    pixels[x, y] = (*secondary, 255)
        return img

    def _generate_pack_icon(self, colors) -> Image.Image:
        icon = Image.new('RGBA', (300, 300), (30, 30, 40, 255))
        draw = ImageDraw.Draw(icon)
        for i, c in enumerate(colors[:8]): # Draw up to 8 ellipses for visual index
            draw.ellipse([20 + i*30, 100, 70 + i*30, 150], fill=(*c, 255))
        return icon
```

#### 3. `TexturePackGenerator` (`src/generators/texture_generator.py`)
```python
import json
import random
from pathlib import Path
from PIL import Image
from .base_generator import BaseGenerator

class TexturePackGenerator(BaseGenerator):
    def generate(self, config: dict, output_dir: Path) -> Path:
        # Expected config: {"name": str, "description": str, "dir_name": str, "resolution": int, "blocks": dict}
        pack_dir = Path(output_dir) / config["dir_name"]
        blocks_dir = pack_dir / "textures" / "blocks"
        blocks_dir.mkdir(parents=True, exist_ok=True)
        
        resolution = config.get("resolution", 16)
        
        # 1. Generate Block Textures with procedural noise
        for name, color in config["blocks"].items():
            img = self._generate_block_texture(name, color, resolution)
            img.save(blocks_dir / f"{name}.png")
            
        # 2. Generate pack_icon.png (in root directory for texture packs)
        icon = Image.new('RGBA', (256, 256), (50, 100, 150, 255))
        icon.save(pack_dir / "pack_icon.png")
        
        # 3. Write manifest.json
        manifest = self.generate_manifest(
            name=config["name"],
            description=config["description"],
            pack_key=config["dir_name"],
            module_type="resources"
        )
        with open(pack_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
            
        return pack_dir

    def _generate_block_texture(self, name, color, resolution) -> Image.Image:
        img = Image.new('RGB', (resolution, resolution))
        pix = img.load()
        rng = random.Random(hash(name) & 0xFFFFFFFF)
        for x in range(resolution):
            for y in range(resolution):
                noise = rng.randint(-15, 15)
                pix[x, y] = tuple(max(0, min(255, c + noise)) for c in color)
        return img
```

#### 4. `WorldTemplateGenerator` (`src/generators/world_generator.py`)
```python
import json
import zlib
from pathlib import Path
from PIL import Image, ImageDraw
from .base_generator import BaseGenerator

class WorldTemplateGenerator(BaseGenerator):
    def generate(self, config: dict, output_dir: Path) -> Path:
        # Expected config: {"name": str, "description": str, "dir_name": str}
        pack_dir = Path(output_dir) / config["dir_name"]
        pack_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Write minimal level.dat (NBT payload)
        with open(pack_dir / "level.dat", "wb") as f:
            f.write(zlib.compress(b'\x0a\x00\x00'))
            
        # 2. Draw world_icon.png (256x256)
        world_icon = Image.new('RGBA', (256, 256), (34, 139, 34, 255))
        world_icon.save(pack_dir / "world_icon.png")
        
        # 3. Draw thumbnail.png (800x450)
        thumbnail = Image.new('RGBA', (800, 450), (135, 206, 235, 255))
        thumbnail.save(pack_dir / "thumbnail.png")
        
        # 4. Write manifest.json
        manifest = self.generate_manifest(
            name=config["name"],
            description=config["description"],
            pack_key=f"world_{config['dir_name']}",
            module_type="world_template"
        )
        with open(pack_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
            
        return pack_dir
```

#### 5. `MashupPackGenerator` (`src/generators/mashup_generator.py`)
```python
import json
from pathlib import Path
from PIL import Image
from .base_generator import BaseGenerator
from .skin_generator import SkinPackGenerator
from .texture_generator import TexturePackGenerator
from .world_generator import WorldTemplateGenerator

class MashupPackGenerator(BaseGenerator):
    def generate(self, config: dict, output_dir: Path) -> Path:
        # Expected config: {
        #   "name": str, "description": str, "dir_name": str,
        #   "skins": list, "blocks": dict, "resolution": int
        # }
        pack_dir = Path(output_dir) / config["dir_name"]
        pack_dir.mkdir(parents=True, exist_ok=True)
        
        # Instantiate sub-generators with the same UUIDManager
        skin_gen = SkinPackGenerator(self.uuid_manager)
        tex_gen = TexturePackGenerator(self.uuid_manager)
        world_gen = WorldTemplateGenerator(self.uuid_manager)
        
        # 1. Generate skin contents inside pack_dir (textures/skins/)
        skin_gen.generate(config, output_dir)
        
        # 2. Generate texture contents inside pack_dir (textures/blocks/)
        tex_gen.generate(config, output_dir)
        
        # 3. Generate world files inside pack_dir (level.dat, world_icon.png, thumbnail.png)
        world_gen.generate(config, output_dir)
        
        # 4. Save pack_icon.png (overwriting standard skin icon at root)
        icon = Image.new('RGBA', (256, 256), (120, 50, 200, 255))
        icon.save(pack_dir / "pack_icon.png")
        
        # 5. Overwrite manifest.json with unified Mashup manifest
        manifest = self.generate_manifest(
            name=config["name"],
            description=config["description"],
            pack_key=f"mashup_{config['dir_name']}",
            module_type="resources",
            metadata={"product_type": "mashup"}
        )
        with open(pack_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
            
        return pack_dir
```

---

## 3. Packager Design (`src/packagers/packager.py`)

The packager must package folder structures into compressed zip files. It must dynamically detect the pack type from the manifest content to apply the correct file extension:
- **Skin Pack, Texture Pack, Mashup Pack**: `.mcpack`
- **World Template**: `.mctemplate` (or `.mcworld` as fallback)

### 3.1 Code Architecture and Implementation
The Packager uses Python's native `zipfile` library. It reads the extracted `manifest.json` file inside the target folder, parses the modules, and updates the compression target suffix accordingly.

```python
# C:\Users\forrydev\Desktop\bedrock_minemods\marketplace-content\src\packagers\packager.py
import json
import zipfile
from pathlib import Path

class Packager:
    @staticmethod
    def package(pack_dir: Path, output_dir: Path) -> Path:
        """
        Compresses the pack directory into a zip archive with a custom extension.
        pack_dir: Path to the generated pack source.
        output_dir: Path to write the final compiled archive.
        Returns: Path to the written zip file.
        """
        pack_dir = Path(pack_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = pack_dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"manifest.json missing in {pack_dir}")

        # 1. Parse manifest to identify extension
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        extension = ".mcpack"  # Default fallback
        modules = manifest.get("modules", [])
        
        for module in modules:
            module_type = module.get("type")
            if module_type == "world_template":
                extension = ".mctemplate"
                break
                
        # 2. Execute zip compilation
        archive_path = output_dir / f"{pack_dir.name}{extension}"
        
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in pack_dir.rglob("*"):
                # Skip writing empty directory nodes to avoid zip bloating
                if file_path.is_file():
                    archive_name = file_path.relative_to(pack_dir)
                    zf.write(file_path, archive_name)
                    
        return archive_path
```

---

## 4. Bedrock Validator Refactoring Design

We propose a comprehensive refactoring of `src/validators/bedrock_validator.py` to fix existing false positives and support advanced compliance rules.

### 4.1 Refactoring Blueprint & Key Additions
1. **Dynamic Schema & Distinct Pack Type Validation**:
   Inspect `manifest.json` on entry. Determine target pack type: `skin`, `texture`, `world`, or `mashup`. Apply assertions conditionally.
2. **Skin Dimension Validation**:
   Enforce width/height sizes for skin textures:
   - Width 64: Height must be 32 (legacy) or 64 (standard).
   - Width 128: Height must be 128 (HD).
   - Reject any other layout configurations with an error.
3. **Folder Path Validation**:
   For skin packs, verify that all skins listed in `skins.json` are present exactly under `textures/skins/{filename}.png` inside the archive. Reject walk-based relaxed checks that allow files at root.
4. **UUID Collision Checks**:
   - **Local Collision**: Check if the manifest header and any modules share the same UUID.
   - **Global Collision**: Loop through all files in the output build directory and verify that no two different packages share header/module UUIDs.

### 4.2 Proposed Validator Code Structure
```python
# C:\Users\forrydev\Desktop\bedrock_minemods\marketplace-content\src\validators\bedrock_validator.py
import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image

class BedrockValidator:
    def __init__(self):
        self.results = []

    def validate_mcpack(self, mcpack_path) -> dict:
        """Validates a single package file against Bedrock Marketplace guidelines."""
        r = {
            'file': os.path.basename(mcpack_path),
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        if not os.path.exists(mcpack_path):
            r['valid'] = False
            r['errors'].append('File not found')
            return r

        tmp = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(mcpack_path, 'r') as zf:
                zf.extractall(tmp)

            tmp_path = Path(tmp)
            manifest_path = tmp_path / 'manifest.json'
            
            if not manifest_path.exists():
                r['valid'] = False
                r['errors'].append('manifest.json missing')
                return r

            # 1. Validate manifest file and get pack characteristics
            pack_type, header_uuid, module_uuids = self._validate_manifest(manifest_path, r)
            r['info']['pack_type'] = pack_type
            r['info']['header_uuid'] = header_uuid
            r['info']['module_uuids'] = module_uuids

            # 2. Run distinct validation suites based on pack type
            if pack_type == 'skin':
                self._validate_skin_pack(tmp_path, r)
            elif pack_type == 'texture':
                self._validate_texture_pack(tmp_path, r)
            elif pack_type == 'world':
                self._validate_world_template(tmp_path, r)
            elif pack_type == 'mashup':
                self._validate_mashup_pack(tmp_path, r)
            else:
                r['warnings'].append(f'Unknown pack type for module type: {pack_type}')

            # 3. Size and file counters info
            file_count = sum(len(files) for _, _, files in os.walk(tmp))
            total_size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(tmp) for f in fn)
            r['info']['files'] = file_count
            r['info']['size_kb'] = round(total_size / 1024, 1)

        except Exception as e:
            r['valid'] = False
            r['errors'].append(f'Validation processing error: {str(e)}')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        return r

    def _validate_manifest(self, path: Path, r: dict) -> tuple:
        """Parses manifest.json and returns (pack_type, header_uuid, module_uuids)."""
        pack_type = 'unknown'
        header_uuid = None
        module_uuids = []
        
        try:
            with open(path) as f:
                m = json.load(f)
        except json.JSONDecodeError as e:
            r['valid'] = False
            r['errors'].append(f'manifest.json JSON error: {e}')
            return pack_type, header_uuid, module_uuids

        # Basic fields existence checks
        for k in ['format_version', 'header', 'modules']:
            if k not in m:
                r['valid'] = False
                r['errors'].append(f'manifest.json missing "{k}"')

        # Header UUID checks
        if 'header' in m:
            h = m['header']
            for k in ['name', 'description', 'uuid', 'version']:
                if k not in h:
                    r['valid'] = False
                    r['errors'].append(f'manifest.header missing "{k}"')
            header_uuid = h.get('uuid')
            
            # Warn on default translations key prefix
            if 'name' in h and h['name'].startswith('pack.'):
                r['warnings'].append(f'manifest.header.name uses localization key: {h["name"]}')

        # Module validation and pack type determination
        if 'modules' in m:
            for i, mod in enumerate(m['modules']):
                for k in ['type', 'uuid', 'version']:
                    if k not in mod:
                        r['valid'] = False
                        r['errors'].append(f'modules[{i}] missing "{k}"')
                
                m_uuid = mod.get('uuid')
                if m_uuid:
                    module_uuids.append(m_uuid)

            # Determine type from modules list
            first_module_type = m['modules'][0].get('type') if m['modules'] else None
            if first_module_type == 'skin_pack':
                pack_type = 'skin'
            elif first_module_type == 'world_template':
                pack_type = 'world'
            elif first_module_type == 'resources':
                # Check for Mashup Metadata block
                is_mashup = m.get('metadata', {}).get('product_type') == 'mashup'
                pack_type = 'mashup' if is_mashup else 'texture'

        # Local UUID Collision Check
        if header_uuid and header_uuid in module_uuids:
            r['valid'] = False
            r['errors'].append(f'Local UUID Collision: manifest header and module share UUID: {header_uuid}')

        return pack_type, header_uuid, module_uuids

    def _validate_skin_pack(self, tmp_path: Path, r: dict):
        """Runs the validation checks specific to Skin Packs."""
        skins_json_path = tmp_path / 'skins.json'
        
        if not skins_json_path.exists():
            r['valid'] = False
            r['errors'].append('skins.json missing in skin pack')
            return

        # Check skins.json contents
        try:
            with open(skins_json_path) as f:
                s = json.load(f)
        except json.JSONDecodeError as e:
            r['valid'] = False
            r['errors'].append(f'skins.json JSON error: {e}')
            return

        if 'skins' not in s or not isinstance(s['skins'], list):
            r['valid'] = False
            r['errors'].append('skins.json missing "skins" array')
            return

        # Verify textures paths and properties
        for i, skin in enumerate(s['skins']):
            for k in ['localization_name', 'geometry', 'texture']:
                if k not in skin:
                    r['valid'] = False
                    r['errors'].append(f'skins[{i}] missing field "{k}"')
                    
            tex = skin.get('texture', '')
            if tex:
                # Force folder path check: must reside in textures/skins/
                expected_png_path = tmp_path / 'textures' / 'skins' / tex
                if not expected_png_path.exists():
                    r['valid'] = False
                    r['errors'].append(f'Skin texture "{tex}" is missing from expected path textures/skins/')
                else:
                    self._validate_skin_dimensions(expected_png_path, r, tex)

        # Validate pack icon
        icon_path = tmp_path / 'textures' / 'skins' / 'icon.png'
        if not icon_path.exists():
            r['warnings'].append('icon.png missing from textures/skins/')
        else:
            self._validate_png_metadata(icon_path, r, 'icon.png', max_size_bytes=500_000)

    def _validate_texture_pack(self, tmp_path: Path, r: dict):
        """Runs checks specific to Texture Packs."""
        # Require pack_icon.png in root folder
        icon_path = tmp_path / 'pack_icon.png'
        if not icon_path.exists():
            r['valid'] = False
            r['errors'].append('pack_icon.png missing from texture pack root directory')
        else:
            self._validate_png_metadata(icon_path, r, 'pack_icon.png', expected_size=(256, 256))

        # Check that blocks folder has files
        blocks_dir = tmp_path / 'textures' / 'blocks'
        if not blocks_dir.exists() or not any(blocks_dir.iterdir()):
            r['warnings'].append('textures/blocks/ directory is missing or empty')

    def _validate_world_template(self, tmp_path: Path, r: dict):
        """Runs checks specific to World Templates."""
        # Require level.dat file
        if not (tmp_path / 'level.dat').exists():
            r['valid'] = False
            r['errors'].append('level.dat missing from world template')

        # Require world_icon.png
        icon_path = tmp_path / 'world_icon.png'
        if not icon_path.exists():
            r['valid'] = False
            r['errors'].append('world_icon.png missing from world template root')
        else:
            self._validate_png_metadata(icon_path, r, 'world_icon.png', expected_size=(256, 256))

    def _validate_mashup_pack(self, tmp_path: Path, r: dict):
        """Runs validation checks combining world, textures, and skins."""
        self._validate_world_template(tmp_path, r)
        self._validate_texture_pack(tmp_path, r)
        # Verify skins inside mashup if skins.json is present
        if (tmp_path / 'skins.json').exists():
            self._validate_skin_pack(tmp_path, r)

    def _validate_skin_dimensions(self, path: Path, r: dict, label: str):
        """Verifies skin dimensions match Minecraft standards (64x32, 64x64, 128x128)."""
        try:
            with Image.open(path) as img:
                if img.format != 'PNG':
                    r['warnings'].append(f'{label}: format is {img.format}, expected PNG')
                
                w, h = img.size
                if (w == 64 and h in [32, 64]) or (w == 128 and h == 128):
                    # Compliance met
                    pass
                else:
                    r['valid'] = False
                    r['errors'].append(f'Skin "{label}" has invalid dimensions {w}x{h}. Must be 64x32, 64x64 or 128x128.')
                    
                # Warn if file exceeds 1MB limits
                sz = os.path.getsize(path)
                if sz > 1_000_000:
                    r['warnings'].append(f'Skin "{label}" is {sz/1024:.0f}KB, exceeds 1MB limit')
        except Exception as e:
            r['valid'] = False
            r['errors'].append(f'{label}: PNG parsing error - {e}')

    def _validate_png_metadata(self, path: Path, r: dict, label: str, expected_size: tuple = None, max_size_bytes: int = None):
        """Utility to check general PNG conditions (format, sizes, dimensions)."""
        try:
            with Image.open(path) as img:
                if img.format != 'PNG':
                    r['warnings'].append(f'{label}: format is {img.format}, expected PNG')
                if expected_size and img.size != expected_size:
                    r['warnings'].append(f'{label}: size is {img.size}, expected {expected_size[0]}x{expected_size[1]}')
                
                sz = os.path.getsize(path)
                if max_size_bytes and sz > max_size_bytes:
                    r['warnings'].append(f'{label}: size ({sz/1024:.1f}KB) exceeds {max_size_bytes/1024:.0f}KB')
        except Exception as e:
            r['valid'] = False; r['errors'].append(f'{label}: validation error - {e}')

    def validate_all(self, dist_dir) -> list:
        """
        Validates all archive packages in a directory and performs global UUID collision checks.
        """
        self.results = []
        uuid_registry = {}  # uuid -> list of pack names using it
        
        # 1. Individual verification
        dist_path = Path(dist_dir)
        if not dist_path.exists():
            return []

        for item in sorted(dist_path.iterdir()):
            if item.suffix in ['.mcpack', '.mcworld', '.mctemplate']:
                res = self.validate_mcpack(str(item))
                self.results.append(res)
                
                # Extract UUID metadata recorded in info
                h_uuid = res.get('info', {}).get('header_uuid')
                m_uuids = res.get('info', {}).get('module_uuids', [])
                
                # Index UUID occurrences
                if h_uuid:
                    uuid_registry.setdefault(h_uuid, []).append(item.name)
                for m_uuid in m_uuids:
                    if m_uuid:
                        uuid_registry.setdefault(m_uuid, []).append(item.name)

        # 2. Check Global UUID Collision
        collisions = {uid: files for uid, files in uuid_registry.items() if len(files) > 1}
        if collisions:
            for res in self.results:
                h_uuid = res.get('info', {}).get('header_uuid')
                m_uuids = res.get('info', {}).get('module_uuids', [])
                
                for col_uuid, affected_files in collisions.items():
                    if col_uuid == h_uuid or col_uuid in m_uuids:
                        other_files = [f for f in affected_files if f != res['file']]
                        res['valid'] = False
                        res['errors'].append(
                            f"Global UUID Collision: UUID {col_uuid} is also used in: {', '.join(other_files)}"
                        )

        return self.results
```
