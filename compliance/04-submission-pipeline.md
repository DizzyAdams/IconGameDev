# Submission Pipeline — Build to Marketplace

## 1. Pre-Submission Checklist

- [ ] All packs pass technical validation
- [ ] No IP-infringing names or content
- [ ] Screenshots generated (4 per pack, 1280x720)
- [ ] Pack icons present (256x256 or 300x300)
- [ ] Store descriptions written (EN + PT)
- [ ] Pricing set (see pricing strategy)
- [ ] Age rating determined

## 2. Build Pipeline

```
generate-massive-packs.py  →  Generate source packs
    ↓
safe-rename.py             →  Rename franchise content
    ↓
build-all.py               →  Build .mcpacks to dist/
    ↓
generate-screenshots.py    →  Create screenshots
    ↓
generate-descriptions.py   →  Generate store text
    ↓
generate-site.py           →  Build catalog website
```

## 3. Partner Center Submission

1. Log in to https://partner.microsoft.com
2. Go to Marketplace → Create new offer
3. Select product type (Skin Pack / Texture Pack / World / Mashup)
4. Upload .mcpack
5. Fill metadata:
   - Title (60 chars max)
   - Description (100-300 chars)
   - Search terms (5 max)
   - Category
6. Upload screenshots (4-6, 1280x720)
7. Upload icon (256x256 PNG)
8. Upload hero art (1920x1080)
9. Set age rating (ESRB E for most packs)
10. Set pricing (see pricing strategy)
11. Submit for review

## 4. Review Process

- Standard: 3-5 business days
- Rejection reasons:
  - IP infringement → Use safe names
  - Low quality → Verify 256x+ textures
  - Missing assets → Check checklist
  - Technical issues → Validate manifests

## 5. Post-Acceptance

- Set release date
- Monitor sales via Partner dashboard
- Update packs monthly with new content
- Track Minecoin conversion (160 coins = $0.99)
