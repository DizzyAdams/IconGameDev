import json
import zipfile
from pathlib import Path

class Packager:
    @staticmethod
    def package(pack_dir: Path, output_dir: Path) -> Path:
        pack_dir = Path(pack_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        manifest_path = pack_dir / "manifest.json"
        ext = ".mcpack"  # Default
        
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                
                # Check for mashup metadata
                metadata = manifest.get("metadata", {})
                if metadata.get("product_type") == "mashup":
                    ext = ".mcpack"
                else:
                    modules = manifest.get("modules", [])
                    for mod in modules:
                        mod_type = mod.get("type")
                        if mod_type == "world_template":
                            ext = ".mctemplate"
                            break
                        elif mod_type == "skin_pack":
                            ext = ".mcpack"
                            break
                        elif mod_type == "resources":
                            ext = ".mcpack"
                            break
            except Exception:
                pass
                
        archive_name = pack_dir.name + ext
        archive_path = output_dir / archive_name
        
        # Write to zip, skipping __pycache__ and hidden system files
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(pack_dir.rglob("*")):
                if file_path.is_dir():
                    continue
                # Skip hidden files/folders (starting with .) and __pycache__
                parts = file_path.relative_to(pack_dir).parts
                if any(p.startswith(".") or p == "__pycache__" for p in parts):
                    continue
                zf.write(file_path, str(file_path.relative_to(pack_dir)))
                
        return archive_path
