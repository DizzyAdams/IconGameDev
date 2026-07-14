# Quality Assurance Guide

## 1. Automated Checks

Run before every submission:

```bash
# 1. Validate all manifests
python -c "
import json
from pathlib import Path
for f in Path('.').rglob('manifest.json'):
    d = json.loads(f.read_text())
    h = d.get('header', {})
    assert 'uuid' in h, f'{f}: missing uuid'
    assert 'version' in h, f'{f}: missing version'
    assert 'name' in h, f'{f}: missing name'
    print(f'OK {f.parent.name}')
"

# 2. Check PNGs are valid
python -c "
from PIL import Image
from pathlib import Path
for f in Path('.').rglob('*.png'):
    try:
        img = Image.open(f)
        img.verify()
    except:
        print(f'CORRUPT: {f}')
"

# 3. Count packs per category
python -c "
from pathlib import Path
for d in ['skin-packs','texture-packs','world-templates','mashup-packs']:
    p = Path(d)
    if p.exists():
        print(f'{d}: {len([x for x in p.iterdir() if x.is_dir()])} packs')
"
```

## 2. Manual QA Checklist

Per pack, verify:
- [ ] Manifest has correct `format_version: 2`
- [ ] All UUIDs are unique (no duplicates)
- [ ] Names match between manifest and store description
- [ ] No broken image paths
- [ ] World templates have `level.dat`
- [ ] Skin packs have `skins.json` and textures
- [ ] All PNGs open correctly

## 3. Content Review

- [ ] No offensive or inappropriate content
- [ ] No trademarked characters or logos
- [ ] No Minecraft/Mojank/Microsoft trademarks in name
- [ ] Age rating appropriate (E for all packs)
- [ ] Descriptions are clear and accurate

## 4. Performance Testing

- Pack file size under 10MB (ideally under 5MB)
- natural-256x at 6MB is the largest - consider compressing
- No unnecessary files in .mcpack (no .git, __pycache__)
- All textures use proper resolution for their pack

## 5. Testing on Devices

Before full submission, test on:
- [ ] Windows 10/11 (native Bedrock)
- [ ] Android (mobile/tablet)
- [ ] iOS (if available)
- [ ] Xbox (if available)
- [ ] Nintendo Switch (if available)

## 6. Rebuild After Changes

After any change to source files:
```bash
python scripts/build-all.py
```
Always rebuild before submission.

## 7. Version Management

- Start at v1.0.0 for initial submission
- Increment patch for fixes (v1.0.1)
- Increment minor for new content (v1.1.0)
- Increment major for overhauls (v2.0.0)
- Update version in manifest.json before rebuild
