#!/usr/bin/env bash
# =============================================================================
# Epic/Fortnite Creative — Build & Validate Script
# =============================================================================
# Usage:
#   ./epic/build.sh           # validate all templates
#   ./epic/build.sh --full    # validate + generate deployment artifacts
#   ./epic/build.sh --publish # do everything + package for submission
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EPIC_DIR="$ROOT_DIR/epic"
MAPS_DIR="$EPIC_DIR/maps"
BUILD_DIR="$EPIC_DIR/build"
SUBMISSION_DIR="$EPIC_DIR/submission_pending"
TIMESTAMP=$(date +%Y%m%d-%H%M)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

mkdir -p "$BUILD_DIR" "$SUBMISSION_DIR"

echo "=============================================="
echo "  Epic / Fortnite Creative — Build Pipeline"
echo "  Timestamp: $TIMESTAMP"
echo "=============================================="

# ── Step 1: Validate JSON templates ──────────────────────────────────────
echo ""
echo "── Step 1/4: Validating JSON templates ──"
VALIDATION_FAILED=0
for f in "$MAPS_DIR"/*.json; do
    name=$(basename "$f")
    if python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $name"
    else
        echo -e "  ${RED}✗${NC} $name — invalid JSON"
        VALIDATION_FAILED=1
    fi
done

if [ "$VALIDATION_FAILED" -eq 1 ]; then
    echo -e "\n${RED}ERROR: One or more templates failed JSON validation.${NC}"
    exit 2
fi
echo -e "  ${GREEN}All templates valid.${NC}"

# ── Step 2: Check required fields ────────────────────────────────────────
echo ""
echo "── Step 2/4: Checking required fields ──"
FIELD_FAILED=0
for f in "$MAPS_DIR"/*.json; do
    name=$(basename "$f")
    issues=$(python3 -c "
import json
d = json.load(open('$f'))
req = ['template', 'version', 'display_name', 'description', 'game_settings']
for k in req:
    if k not in d: print(f'  [MISSING] {k}')
if 'max_players' not in d.get('game_settings', {}):
    print('  [MISSING] game_settings.max_players')
")
    if [ -n "$issues" ]; then
        echo -e "  ${RED}✗${NC} $name"
        echo "$issues"
        FIELD_FAILED=1
    else
        echo -e "  ${GREEN}✓${NC} $name"
    fi
done
if [ "$FIELD_FAILED" -eq 1 ]; then exit 2; fi

# ── Step 3: Build template index ─────────────────────────────────────────
echo ""
echo "── Step 3/4: Generating template index ──"
INDEX="$BUILD_DIR/template_index.json"
echo "[" > "$INDEX"
first=true
for f in "$MAPS_DIR"/*.json; do
    name=$(basename "$f" .json)
    if [ "$first" = true ]; then first=false; else echo "," >> "$INDEX"; fi
    python3 -c "
import json
d = json.load(open('$f'))
idx = {
    'file': '$name.json',
    'template': d.get('template', ''),
    'display_name': d.get('display_name', ''),
    'tags': d.get('tags', []),
    'max_players': d.get('game_settings', {}).get('max_players', 0),
    'description': d.get('description', '')[:80] + '...'
}
print(json.dumps(idx, indent=2))
" >> "$INDEX"
done
echo "" >> "$INDEX"
echo "]" >> "$INDEX"
echo -e "  ${GREEN}✓${NC} Generated $INDEX"

# ── Step 4: Generate summary ─────────────────────────────────────────────
echo ""
echo "── Step 4/4: Generating summary ──"
SUMMARY="$BUILD_DIR/build_summary.txt"
TOTAL=$(ls -1 "$MAPS_DIR"/*.json 2>/dev/null | wc -l)
echo "Epic/Fortnite Creative Build Summary" > "$SUMMARY"
echo "===================================" >> "$SUMMARY"
echo "Timestamp: $TIMESTAMP" >> "$SUMMARY"
echo "Templates validated: $TOTAL" >> "$SUMMARY"
echo "" >> "$SUMMARY"
echo "Maps:" >> "$SUMMARY"
for f in "$MAPS_DIR"/*.json; do
    python3 -c "
import json
d = json.load(open('$f'))
print(f\"  - {d.get('display_name','?')} ({d.get('template','?')})\")" >> "$SUMMARY"
done
echo "" >> "$SUMMARY"
echo "Build: ${GREEN}SUCCESS${NC}" | sed 's/\\033\[[0-9;]*m//g' >> "$SUMMARY"
echo -e "  ${GREEN}✓${NC} Generated $SUMMARY"

# ── Full mode: generate deploy artifacts ─────────────────────────────────
if [ "${1:-}" = "--full" ] || [ "${1:-}" = "--publish" ]; then
    echo ""
    echo "── Full mode: Generating deployment artifacts ──"
    # Package each map template into a structured submission ZIP
    for f in "$MAPS_DIR"/*.json; do
        name=$(basename "$f" .json)
        pkg_dir="$BUILD_DIR/pkg_$TIMESTAMP/$name"
        mkdir -p "$pkg_dir"
        cp "$f" "$pkg_dir/"
        # Generate a simple UEFN project manifest
        python3 -c "
import json
d = json.load(open('$f'))
manifest = {
    'project_name': d.get('display_name', name),
    'template': d.get('template', ''),
    'uefn_version': d.get('uefn_version', '>=31.0'),
    'island_type': d.get('island', {}).get('type', 'flat'),
    'max_players': d.get('game_settings', {}).get('max_players', 0),
    'game_mode': d.get('game_settings', {}).get('game_mode', ''),
    'dependencies': [],
    'generated': '$TIMESTAMP',
    'generator': 'IconGameDev Epic Pipeline'
}
with open('$pkg_dir/uefn_project.json', 'w') as mf:
    json.dump(manifest, mf, indent=2)
"
        echo -e "  ${GREEN}✓${NC} $name packaged"
    done

    # Create the submission ZIP
    if [ "${1:-}" = "--publish" ]; then
        ZIP_NAME="epic_submission_$TIMESTAMP.zip"
        (cd "$BUILD_DIR/pkg_$TIMESTAMP" && zip -r "$SUBMISSION_DIR/$ZIP_NAME" . > /dev/null 2>&1)
        echo -e "\n  ${GREEN}✓${NC} Submission package: $SUBMISSION_DIR/$ZIP_NAME"
    fi
fi

echo ""
echo "=============================================="
echo -e "  ${GREEN}BUILD COMPLETE${NC} — all templates validated."
echo "=============================================="
