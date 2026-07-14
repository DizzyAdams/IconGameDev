# Technical Compliance — Bedrock Marketplace

## 1. Manifest v2 Schema

Every .mcpack must have `manifest.json`:

```json
{
  "format_version": 2,
  "header": {
    "name": "Pack Name",
    "description": "Pack description 150-300 chars",
    "uuid": "<uuid-v4>",
    "version": [1, 0, 0],
    "min_engine_version": [1, 20, 0]
  },
  "modules": [
    {
      "type": "skin_pack",
      "uuid": "<uuid-v4>",
      "version": [1, 0, 0]
    }
  ]
}
```

### Module Types

| Pack Type | module type |
|-----------|-------------|
| Skin Pack | `skin_pack` |
| Texture Pack | `resources` |
| World Template | `world_template` |
| Mashup | `resources` |
| Behavior Pack | `data` |
| Add-on | `script` |

## 2. UUID Requirements

- Must be **version 4** UUIDs (random)
- Each pack needs at least 2 UUIDs (header + module)
- UUIDs must be unique across ALL packs
- Never reuse UUIDs from other creators
- Use our UUID Manager: `src/utils/uuid_manager.py`

## 3. File Structure

### Skin Pack
```
pack-name/
├── manifest.json
├── skins.json
├── textures/
│   └── skins/
│       ├── skin1.png (64x64 or 128x128)
│       ├── skin2.png
│       └── icon.png (pack icon)
```

### Texture Pack
```
pack-name/
├── manifest.json
├── pack_icon.png
└── textures/
    └── blocks/
        ├── stone.png
        ├── grass_top.png
        └── ... (all required block textures)
```

### World Template
```
pack-name/
├── manifest.json
├── world_icon.png
├── thumbnail.png
└── level.dat (minimal valid NBT)
```

### Mashup Pack
```
pack-name/
├── manifest.json
├── pack_icon.png
└── (combines skin + texture + world)
```

## 4. PNG Specifications

| Asset | Size | Format | Max Size |
|-------|------|--------|----------|
| Skin texture | 64x64 or 128x128 | RGBA PNG | 1 MB |
| Pack icon | 256x256 | RGBA PNG | 500 KB |
| World icon | 256x256 | RGBA PNG | 500 KB |
| Thumbnail | 800x450 | JPG/PNG | 2 MB |
| Key art | 1920x1080 | JPG/PNG | 5 MB |
| Screenshot | 1280x720 | JPG/PNG | 3 MB |

## 5. skins.json Format

```json
{
  "skins": [
    {
      "localization_name": "SkinName1",
      "geometry": "geometry.humanoid.custom",
      "texture": "SkinName1.png",
      "type": "free"
    }
  ],
  "serialize_name": "Pack Name",
  "localization_name": "Pack Name"
}
```

## 6. Version Management

- Start at [1, 0, 0]
- Increment on updates:
  - [1, 0, 1] = minor fix
  - [1, 1, 0] = new skins added
  - [2, 0, 0] = major overhaul
- max version number: 255 per segment

## 7. Validation Checklist

Run before submission:

```bash
python src/validators/bedrock_validator.py
```

Checks:
- [ ] manifest.json exists and valid JSON
- [ ] All required UUIDs present
- [ ] Module types correct
- [ ] All referenced PNG files exist
- [ ] PNG dimensions valid
- [ ] PNG is RGBA mode
- [ ] File size limits
- [ ] skins.json valid (skin packs only)
