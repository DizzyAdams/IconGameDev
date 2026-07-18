#!/usr/bin/env python3
"""Generate comprehensive PACK_CATALOG.json for IconGameDev Bedrock marketplace.

Scans:
  - submission_mcpacks/  (.mcpack = skin packs, .mctemplate = world templates)
  - marketplace-content/output/mass-skins/  (if it exists — extra skin packs)
  - marketplace-content/skin-packs/         (if it exists — extra skin packs)
  - skin-packs/output/                      (if it exists — extra skin packs)

Output: marketplace-content/catalog/PACK_CATALOG.json
"""

import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# ── paths ───────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
REPO = HERE.parent

OUTPUT = REPO / "marketplace-content" / "catalog" / "PACK_CATALOG.json"

# Source directories to scan
SOURCE_DIRS = [
    REPO / "submission_mcpacks",
    REPO / "marketplace-content" / "output" / "mass-skins",
    REPO / "marketplace-content" / "skin-packs",
    REPO / "skin-packs" / "output",
]

DEFAULT_PRICE = 2.99
DEFAULT_PRICE_STR = "$2.99"
DEFAULT_CATEGORY = "skin_pack"

# ── category/keyword mapping for themed packs ─────────────────────────────
THEME_CATEGORIES = {
    "fantasy": "fantasy",
    "dragon": "fantasy",
    "knight": "fantasy",
    "medieval": "fantasy",
    "elf": "fantasy",
    "wizard": "fantasy",
    "magic": "fantasy",
    "valkyrie": "fantasy",
    "demon": "fantasy",
    "angel": "fantasy",
    "celestial": "fantasy",
    "dwarf": "fantasy",
    "phoenix": "fantasy",
    "crystal": "fantasy",
    "mythic": "fantasy",
    "cyber": "cyberpunk",
    "neon": "cyberpunk",
    "cyberpunk": "cyberpunk",
    "hologram": "cyberpunk",
    "void": "cyberpunk",
    "hacker": "cyberpunk",
    "plasma": "cyberpunk",
    "animal": "animals",
    "wolf": "animals",
    "dragon_pet": "animals",
    "panda": "animals",
    "fox": "animals",
    "bear": "animals",
    "eagle": "animals",
    "cat": "animals",
    "shark": "animals",
    "owl": "animals",
    "tiger": "animals",
    "pixel": "pixel-art",
    "retro": "pixel-art",
    "arcade": "pixel-art",
    "8-bit": "pixel-art",
    "gameboy": "pixel-art",
    "nes": "pixel-art",
    "beach": "beach",
    "summer": "seasonal",
    "christmas": "seasonal",
    "halloween": "seasonal",
    "back-to-school": "seasonal",
    "superhero": "superheroes",
    "steampunk": "steampunk",
    "western": "western",
    "viking": "viking",
    "underwater": "underwater",
    "tropical": "tropical",
    "space": "sci-fi",
    "ninja": "ninja",
    "samurai": "ninja",
    "zombie": "horror",
    "candyland": "cute",
    "cottagecore": "cute",
    "african": "cultural",
    "aztec": "cultural",
    "mayan": "cultural",
    "celtic": "cultural",
    "cowboy": "western",
}

# ── helpers ─────────────────────────────────────────────────────────────────

def _fmt(ts: datetime | None = None) -> str:
    return (ts or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%S%z")


def _derive_name(filename: str) -> str:
    """Derive a readable display name from a pack filename."""
    stem = Path(filename).stem
    # Remove common prefixes for cleaner names
    cleaned = stem
    for prefix in ["batch_", "beach-skins-", "animal-skins-"]:
        if cleaned.startswith(prefix):
            rest = cleaned[len(prefix):]
            prefix_name = {
                "batch_": "Skin Pack ",
                "beach-skins-": "Beach Skin ",
                "animal-skins-": "Animal Skin ",
            }[prefix]
            if rest.isdigit():
                cleaned = f"{prefix_name}{rest}"
            elif rest:
                cleaned = f"{prefix_name}{rest.replace('-', ' ').title()}"
            break
    # Handle themed packs: replace hyphens with spaces and title-case
    cleaned = cleaned.replace("-", " ").replace("_", " ").title()
    # Fix common naming issues
    cleaned = cleaned.replace("Mcpack", "Skin Pack").replace("Mctemplate", "World Template")
    return cleaned


def _derive_category(filename: str) -> str:
    """Derive a category from filename."""
    stem = Path(filename).stem.lower()
    # Check batch packs
    if stem.startswith("batch_"):
        return "skin_pack"
    if stem.startswith("beach"):
        return "beach"
    if stem.startswith("animal"):
        return "animals"
    if stem.startswith("neon-skins-") or "neon" in stem:
        return "cyberpunk"
    # Check theme keywords
    for keyword, category in THEME_CATEGORIES.items():
        if keyword in stem:
            return category
    # World templates
    if filename.endswith(".mctemplate"):
        for series in ["crystal-vale", "sunken-relic", "voidforge", "stormwatch",
                        "verdant-hollow", "emberfall", "frostspire", "mythic-dawn",
                        "aether-drift", "neon-forge"]:
            if series in stem:
                return series.replace("-", " ")
        return "world_template"
    return "skin_pack"


def _extract_manifest_meta(filepath: Path) -> dict:
    """Extract pack metadata from a .mcpack / .mctemplate manifest.json."""
    meta = {"file": filepath.name}
    try:
        with zipfile.ZipFile(filepath, "r") as zf:
            if "manifest.json" in zf.namelist():
                manifest = json.loads(zf.read("manifest.json"))
                header = manifest.get("header", {})
                meta["name"] = header.get("name", _derive_name(filepath.name))
                meta["description"] = header.get("description", "")
                meta["uuid"] = header.get("uuid", "")

                # Determine product_type from manifest
                modules = manifest.get("modules", [])
                if any(m.get("type") == "world" for m in modules):
                    meta["product_type"] = "world"
                elif any(m.get("type") == "skin_pack" for m in modules):
                    meta["product_type"] = "skin_pack"
                else:
                    # Check metadata
                    md = manifest.get("metadata", {})
                    meta["product_type"] = md.get("product_type", "skin_pack")
            else:
                meta["name"] = _derive_name(filepath.name)
                meta["description"] = ""
    except Exception:
        meta["name"] = _derive_name(filepath.name)
        meta["description"] = ""
        meta["parse_error"] = True

    if "product_type" not in meta:
        if filepath.suffix == ".mctemplate":
            meta["product_type"] = "world"
        else:
            meta["product_type"] = "skin_pack"

    return meta


def categorize_pack(meta: dict) -> str:
    """Determine the category string for a pack."""
    # If we have a manifest with metadata, use that
    if meta.get("product_type") == "world":
        return "world_template"
    return _derive_category(meta.get("file", ""))


def main() -> int:
    print("=" * 60)
    print("  IconGameDev — Pack Catalog Generator")
    print("=" * 60)

    packs: list[dict] = []
    seen_files: set[str] = set()

    for src_dir in SOURCE_DIRS:
        if not src_dir.is_dir():
            print(f"  [SKIP] {src_dir} — not found")
            continue

        count = 0
        for f in sorted(src_dir.iterdir()):
            if f.suffix not in (".mcpack", ".mctemplate"):
                continue
            if not f.is_file():
                continue
            if f.name in seen_files:
                continue
            seen_files.add(f.name)

            meta = _extract_manifest_meta(f)
            category = categorize_pack(meta)
            product_type = meta.get("product_type", "skin_pack")
            name = meta.get("name", _derive_name(f.name))

            entry = {
                "dir": f.stem,
                "name": name,
                "category": category,
                "product_type": product_type,
                "price": DEFAULT_PRICE_STR,
                "price_usd": DEFAULT_PRICE,
                "store_description": meta.get("description", ""),
                "compliance_status": "pending",
            }

            # Override price for world templates to be same as skin packs
            if product_type == "world":
                entry["price"] = DEFAULT_PRICE_STR
                entry["price_usd"] = DEFAULT_PRICE

            packs.append(entry)
            count += 1

        print(f"  [{src_dir.name}] found {count} packs")

    # Sort packs alphabetically by name
    packs.sort(key=lambda p: p["name"].lower())

    catalog = {
        "generated_at": _fmt(),
        "pack_count": len(packs),
        "packs": packs,
    }

    # Write output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Summary
    skin_count = sum(1 for p in packs if p["product_type"] == "skin_pack")
    world_count = sum(1 for p in packs if p["product_type"] == "world")

    print(f"\n  Summary:")
    print(f"    Total packs:     {len(packs)}")
    print(f"    Skin packs:      {skin_count}")
    print(f"    World templates: {world_count}")
    print(f"    Output:          {OUTPUT}")
    print(f"    File size:       {OUTPUT.stat().st_size:,} bytes")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
