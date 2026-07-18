#!/usr/bin/env bash
# =============================================================================
# Epic/Fortnite Creative — Publish / Submission Script
# =============================================================================
# Usage:
#   ./epic/publish.sh                  # generate submission package
#   ./epic/publish.sh --dry-run        # preview without creating ZIP
#   ./epic/publish.sh --export-uefn    # generate ready-to-import UEFN files
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EPIC_DIR="$ROOT_DIR/epic"
MAPS_DIR="$EPIC_DIR/maps"
SUBMISSION_DIR="$EPIC_DIR/submission_pending"
TIMESTAMP=$(date +%Y%m%d-%H%M)

mkdir -p "$SUBMISSION_DIR"

echo "=============================================="
echo "  Epic / Fortnite Creative — Publish Pipeline"
echo "  Timestamp: $TIMESTAMP"
echo "=============================================="

# ── Step 1: Pre-flight checks ────────────────────────────────────────────
echo ""
echo "── Step 1/4: Pre-flight checks ──"
for cmd in python3 zip; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "  ERROR: $cmd not found. Please install it."
        exit 1
    fi
done

# Check that templates exist
TOTAL_MAPS=$(ls -1 "$MAPS_DIR"/*.json 2>/dev/null | wc -l)
if [ "$TOTAL_MAPS" -eq 0 ]; then
    echo "  ERROR: No map templates found in $MAPS_DIR"
    exit 1
fi
echo -e "  ✓ Found $TOTAL_MAPS map templates in $MAPS_DIR"
echo -e "  ✓ All required tools available"

# ── Step 2: Validate all templates ───────────────────────────────────────
echo ""
echo "── Step 2/4: Validating templates ──"
VALID=0
INVALID=0
for f in "$MAPS_DIR"/*.json; do
    name=$(basename "$f")
    if python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
        VALID=$((VALID + 1))
    else
        echo "  ✗ $name — INVALID"
        INVALID=$((INVALID + 1))
    fi
done

if [ "$INVALID" -gt 0 ]; then
    echo "  ERROR: $INVALID invalid templates — aborting publish."
    exit 2
fi
echo "  ✓ $VALID templates valid"

# ── Step 3: Generate submission manifest ─────────────────────────────────
echo ""
echo "── Step 3/4: Generating submission manifest ──"
MANIFEST="$SUBMISSION_DIR/submission_manifest_$TIMESTAMP.json"
python3 -c "
import json, os
from pathlib import Path

maps_dir = Path('$MAPS_DIR')
templates = []
for f in sorted(maps_dir.glob('*.json')):
    d = json.loads(f.read_text())
    templates.append({
        'file': f.name,
        'template': d.get('template'),
        'display_name': d.get('display_name'),
        'game_mode': d.get('game_settings', {}).get('game_mode'),
        'max_players': d.get('game_settings', {}).get('max_players'),
        'tags': d.get('tags', [])
    })

manifest = {
    'submission_id': 'epic-$TIMESTAMP',
    'timestamp': '$TIMESTAMP',
    'project': 'IconGameDev',
    'platform': 'fortnite_creative',
    'engine': 'uefn',
    'total_maps': len(templates),
    'creator': 'IconGameDev',
    'default_language': 'pt-BR',
    'languages_supported': ['pt-BR', 'en-US'],
    'rating': 'E10+ (Everyone 10+)',
    'maps': templates
}
with open('$MANIFEST', 'w') as mf:
    json.dump(manifest, mf, indent=2)
"
echo "  ✓ Manifest: $MANIFEST"

# ── Step 4: Create submission package ────────────────────────────────────
if [ "${1:-}" != "--dry-run" ]; then
    echo ""
    echo "── Step 4/4: Creating submission package ──"
    
    PKG_DIR="$SUBMISSION_DIR/pkg_$TIMESTAMP"
    mkdir -p "$PKG_DIR"

    # Copy maps
    cp "$MAPS_DIR"/*.json "$PKG_DIR/"
    # Copy manifest
    cp "$MANIFEST" "$PKG_DIR/"
    # Copy submission guide
    if [ -f "$EPIC_DIR/SUBMISSION_GUIDE.md" ]; then
        cp "$EPIC_DIR/SUBMISSION_GUIDE.md" "$PKG_DIR/"
    fi

    ZIP_NAME="fortnite_submission_$TIMESTAMP.zip"
    (cd "$PKG_DIR" && zip -r "../$ZIP_NAME" . > /dev/null 2>&1)

    echo "  ✓ Package: $SUBMISSION_DIR/$ZIP_NAME"
    echo "  ✓ Size: $(du -h "$SUBMISSION_DIR/$ZIP_NAME" | cut -f1)"

    # ── Optional: Export UEFN-ready files ──
    if [ "${1:-}" = "--export-uefn" ]; then
        UEFN_DIR="$SUBMISSION_DIR/uefn_export_$TIMESTAMP"
        mkdir -p "$UEFN_DIR"
        for f in "$MAPS_DIR"/*.json; do
            name=$(basename "$f" .json)
            python3 -c "
import json
d = json.load(open('$f'))
uefn = {
    'ProjectName': d.get('template', ''),
    'DisplayName': d.get('display_name', ''),
    'Description': d.get('description', ''),
    'Tags': d.get('tags', []),
    'MapSettings': {
        'IslandType': d.get('island', {}).get('type', ''),
        'GameMode': d.get('game_settings', {}).get('game_mode', ''),
        'MaxPlayers': d.get('game_settings', {}).get('max_players', 16),
        'AllowBuilding': d.get('game_settings', {}).get('build_permission', 'full') != 'none',
        'TeamCount': 2 if 'team_size' in d.get('game_settings', {}) else 1
    }
}
with open('$UEFN_DIR/${name}_uefn_import.json', 'w') as uf:
    json.dump(uefn, uf, indent=2)
" 2>/dev/null
        done
        echo "  ✓ UEFN export: $UEFN_DIR"
    fi

    # Cleanup temp pkg dir
    rm -rf "$PKG_DIR"

    echo ""
    echo "=============================================="
    echo "  ✓ PUBLISH READY"
    echo "  Package: $ZIP_NAME"
    echo "  Upload to: https://create.fortnite.com/publish"
    echo "=============================================="
else
    echo ""
    echo "── Dry-run mode — no files created ──"
    echo "  Would create submission package with $TOTAL_MAPS maps."
fi
