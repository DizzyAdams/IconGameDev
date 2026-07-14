import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image

VALID_SKIN_SIZES = [(64, 32), (64, 64), (128, 128)]
MANIFEST_KEYS = ['format_version', 'header', 'modules']
HEADER_KEYS = ['name', 'uuid', 'version']
MODULE_KEYS = ['type', 'uuid', 'version']

class BedrockValidator:
    def __init__(self):
        self.results = []

    def validate_mcpack(self, mcpack_path):
        mcpack_path = Path(mcpack_path)
        r = {
            'file': mcpack_path.name,
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {},
            'uuids': []
        }

        if not mcpack_path.exists():
            r['valid'] = False
            r['errors'].append('File not found')
            return r

        tmp = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(mcpack_path, 'r') as zf:
                for member in zf.infolist():
                    resolved_base = Path(tmp).resolve()
                    resolved_target = resolved_base.joinpath(member.filename).resolve()
                    try:
                        resolved_target.relative_to(resolved_base)
                        zf.extract(member, tmp)
                    except ValueError:
                        r['valid'] = False
                        r['errors'].append(f'Zip Slip path traversal detected: {member.filename}')

            tmp_path = Path(tmp)
            manifest_file = tmp_path / 'manifest.json'

            # 1. Check required manifest.json
            if not manifest_file.exists():
                r['valid'] = False
                r['errors'].append('manifest.json missing')
            else:
                self._validate_manifest(manifest_file, r)

            # Determine type if manifest was successfully parsed
            pack_type = 'unknown'
            if r['valid']:
                try:
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        m = json.load(f)
                    
                    if isinstance(m, dict):
                        # Gather UUIDs for collision checking
                        header = m.get('header')
                        header_uuid = header.get('uuid') if isinstance(header, dict) else None
                        if header_uuid:
                            r['uuids'].append(header_uuid)
                        
                        modules = m.get('modules')
                        if isinstance(modules, list):
                            for mod in modules:
                                if isinstance(mod, dict):
                                    mod_uuid = mod.get('uuid')
                                    if mod_uuid:
                                        r['uuids'].append(mod_uuid)

                        # Determine pack type
                        metadata = m.get('metadata')
                        if isinstance(metadata, dict) and metadata.get('product_type') == 'mashup':
                            pack_type = 'mashup'
                        else:
                            if isinstance(modules, list):
                                for mod in modules:
                                    if isinstance(mod, dict):
                                        mod_type = mod.get('type')
                                        if mod_type == 'skin_pack':
                                            pack_type = 'skin'
                                            break
                                        elif mod_type == 'world_template':
                                            pack_type = 'world'
                                            break
                                        elif mod_type == 'resources':
                                            pack_type = 'texture'
                                            break
                except (TypeError, AttributeError, ValueError, json.JSONDecodeError) as e:
                    r['valid'] = False
                    r['errors'].append(f'manifest.json JSON error: {e}')

            # 2. Run validations based on pack type
            if pack_type == 'skin':
                self._validate_skins_component(tmp_path, r)
            elif pack_type == 'texture':
                self._validate_textures_component(tmp_path, r)
            elif pack_type == 'world':
                self._validate_world_component(tmp_path, r)
            elif pack_type == 'mashup':
                # Run world, skin, and texture validation suites
                self._validate_world_component(tmp_path, r)
                self._validate_skins_component(tmp_path, r, is_mashup=True)
                self._validate_textures_component(tmp_path, r)

            # Validate general PNGs (like pack_icon if it exists but is not validated yet)
            icon_path = tmp_path / 'pack_icon.png'
            if icon_path.exists() and pack_type != 'texture' and pack_type != 'mashup':
                # Don't fail validation if not 256 for non-texture packs (unless world icon)
                self._validate_png(icon_path, r, 'pack_icon', expected_size=256)

            # File and size statistics
            file_count = sum(1 for _ in tmp_path.rglob('*') if _.is_file())
            total_size = sum(_.stat().st_size for _ in tmp_path.rglob('*') if _.is_file())
            r['info'] = {
                'files': file_count,
                'size_bytes': total_size,
                'size_kb': round(total_size / 1024, 1)
            }

        except Exception as e:
            r['valid'] = False
            r['errors'].append(f'Validation error: {str(e)}')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        return r

    def _validate_manifest(self, path, r):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                m = json.load(f)
            
            if not isinstance(m, dict):
                r['valid'] = False
                r['errors'].append('Validation error: manifest.json must be a JSON object')
                return

            for k in MANIFEST_KEYS:
                if k not in m:
                    r['valid'] = False
                    r['errors'].append(f'manifest.json missing "{k}"')

            uuids = []
            if 'header' in m:
                header = m['header']
                if not isinstance(header, dict):
                    r['valid'] = False
                    r['errors'].append('Validation error: manifest.header must be a JSON object')
                else:
                    for k in HEADER_KEYS:
                        if k not in header:
                            r['valid'] = False
                            r['errors'].append(f'manifest.header missing "{k}"')
                    
                    uuid_val = header.get('uuid')
                    if uuid_val:
                        uuids.append(uuid_val)

                    if 'name' in header and isinstance(header['name'], str) and header['name'].startswith('pack.'):
                        r['warnings'].append(f'manifest.header.name uses localization key: {header["name"]}')

            if 'modules' in m:
                modules = m['modules']
                if not isinstance(modules, list):
                    r['valid'] = False
                    r['errors'].append('Validation error: manifest.modules must be a JSON array')
                else:
                    for i, mod in enumerate(modules):
                        if not isinstance(mod, dict):
                            r['valid'] = False
                            r['errors'].append(f'Validation error: modules[{i}] must be a JSON object')
                        else:
                            for k in MODULE_KEYS:
                                if k not in mod:
                                    r['valid'] = False
                                    r['errors'].append(f'modules[{i}] missing "{k}"')
                            uuid_val = mod.get('uuid')
                            if uuid_val:
                                uuids.append(uuid_val)

            # Local UUID Collision Check
            if len(uuids) != len(set(uuids)):
                r['valid'] = False
                r['errors'].append('Local UUID collision found in manifest')
                
        except (TypeError, AttributeError, ValueError, json.JSONDecodeError) as e:
            r['valid'] = False
            r['errors'].append(f'manifest.json JSON error: {str(e)}')

    def _validate_skins_component(self, base_path: Path, r: dict, is_mashup=False):
        skins_json_file = base_path / 'skins.json'
        if not skins_json_file.exists():
            if not is_mashup:
                r['warnings'].append('No skins.json found')
            return

        try:
            with open(skins_json_file, 'r', encoding='utf-8') as f:
                s = json.load(f)
            
            if not isinstance(s, dict):
                r['valid'] = False
                r['errors'].append('Validation error: skins.json must be a JSON object')
                return

            if 'skins' not in s or not isinstance(s['skins'], list):
                r['valid'] = False
                r['errors'].append('skins.json missing "skins" array')
                return

            # Enforce skin path and dimensions check
            for i, skin in enumerate(s['skins']):
                if not isinstance(skin, dict):
                    r['valid'] = False
                    r['errors'].append(f'Validation error: skins[{i}] must be a JSON object')
                    continue
                
                for k in ['localization_name', 'geometry', 'texture']:
                    if k not in skin:
                        r['valid'] = False
                        r['errors'].append(f'skins[{i}] missing "{k}"')
                
                tex = skin.get('texture', '')
                if tex and isinstance(tex, str):
                    # Skin PNG path must reside exactly under textures/skins/ (no walk relaxed match)
                    exact_path = base_path / "textures" / "skins" / tex
                    if not exact_path.exists():
                        r['warnings'].append(f'skin texture not found: {tex}')
                    else:
                        # Enforce skin size verification (width/height dimensions must be exactly 64x32, 64x64, or 128x128)
                        try:
                            with Image.open(exact_path) as img:
                                if img.size not in VALID_SKIN_SIZES:
                                    r['valid'] = False
                                    r['errors'].append(
                                        f'Skin texture {tex} has invalid dimensions {img.size[0]}x{img.size[1]}. '
                                        f'Expected 64x32, 64x64, or 128x128.'
                                    )
                        except Exception as e:
                            r['valid'] = False
                            r['errors'].append(f'Failed to open skin texture {tex}: {e}')
        except (TypeError, AttributeError, ValueError, json.JSONDecodeError) as e:
            r['valid'] = False
            r['errors'].append(f'skins.json validation error: {str(e)}')


    def _validate_textures_component(self, base_path: Path, r: dict):
        icon_path = base_path / 'pack_icon.png'
        if not icon_path.exists():
            r['warnings'].append('pack_icon.png missing (optional for resource packs)')
        else:
            try:
                with Image.open(icon_path) as img:
                    if img.size != (256, 256):
                        r['valid'] = False
                        r['errors'].append(f'pack_icon.png must be 256x256, got {img.size[0]}x{img.size[1]}')
            except Exception as e:
                r['valid'] = False
                r['errors'].append(f'Failed to open pack_icon.png: {e}')

    def _validate_world_component(self, base_path: Path, r: dict):
        level_dat = base_path / 'level.dat'
        world_icon = base_path / 'world_icon.png'

        if not level_dat.exists():
            r['valid'] = False
            r['errors'].append('level.dat missing')

        if not world_icon.exists():
            r['valid'] = False
            r['errors'].append('world_icon.png missing')
        else:
            try:
                with Image.open(world_icon) as img:
                    if img.size != (256, 256):
                        r['valid'] = False
                        r['errors'].append(f'world_icon.png must be 256x256, got {img.size[0]}x{img.size[1]}')
            except Exception as e:
                r['valid'] = False
                r['errors'].append(f'Failed to open world_icon.png: {e}')

    def _validate_png(self, path, r, label, expected_size=None):
        try:
            with Image.open(path) as img:
                if img.format != 'PNG':
                    r['warnings'].append(f'{label}: format is {img.format}, expected PNG')
                if expected_size and (img.size[0] != expected_size or img.size[1] != expected_size):
                    r['warnings'].append(f'{label}: size {img.size}, expected {expected_size}x{expected_size}')
                sz = os.path.getsize(path)
                if sz > 1_000_000:
                    r['warnings'].append(f'{label}: {sz/1024:.0f}KB exceeds 1MB')
        except Exception as e:
            r['valid'] = False
            r['errors'].append(f'{label}: PNG error - {e}')

    def validate_all(self, dist_dir):
        self.results = []
        packages = []
        
        dist_path = Path(dist_dir)
        if not dist_path.exists():
            return self.results

        # Locate all zip packages with Bedrock extensions
        exts = ('.mcpack', '.mctemplate', '.mcworld')
        for f in sorted(os.listdir(dist_path)):
            if f.endswith(exts):
                packages.append(dist_path / f)

        # 1. First pass: validate each package individually
        uuid_to_packs = {}
        for p in packages:
            r = self.validate_mcpack(str(p))
            self.results.append(r)
            
            # Record UUIDs for global collision check
            for u in r.get('uuids', []):
                if u:
                    uuid_to_packs.setdefault(u, []).append(r)

        # 2. Second pass: global UUID collision check
        for u, packs in uuid_to_packs.items():
            if len(packs) > 1:
                pack_names = ", ".join(p['file'] for p in packs)
                for r in packs:
                    r['valid'] = False
                    r['errors'].append(f'Global UUID collision for {u} with other packs: {pack_names}')

        return self.results

    def report(self):
        lines = []
        lines.append('='*60)
        lines.append('  BEDROCK VALIDATION REPORT')
        lines.append('='*60)
        total = len(self.results)
        passed = sum(1 for r in self.results if r['valid'])
        lines.append(f'  Total: {total} | Passed: {passed} | Failed: {total-passed}')
        lines.append('')
        for r in self.results:
            status = 'PASS' if r['valid'] else 'FAIL'
            lines.append(f'  [{status}] {r["file"]} ({r["info"].get("size_kb","?")}KB, {r["info"].get("files","?")} files)')
            for e in r['errors']:
                lines.append(f'         ERR: {e}')
            for w in r['warnings']:
                lines.append(f'         WARN: {w}')
        lines.append('')
        lines.append(f'  SUMMARY: {passed}/{total} passed')
        if total - passed > 0:
            lines.append(f'  WARNING: {total-passed} packs need fixes before submission')
        lines.append('='*60)
        return '\n'.join(lines)
