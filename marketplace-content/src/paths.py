from __future__ import annotations

from pathlib import Path

BASE: Path = Path(__file__).resolve().parent.parent

SKIN_DIR: Path = BASE / "skin-packs"
TEX_DIR: Path = BASE / "texture-packs"
WORLD_DIR: Path = BASE / "world-templates"
MASHUP_DIR: Path = BASE / "mashup-packs"
BEHAVIOR_DIR: Path = BASE / "behavior-packs"
DESCRIPTIONS_DIR: Path = BASE / "descriptions"
ASSETS_DIR: Path = BASE / "assets"
DIST_DIR: Path = BASE / "dist"
CATALOG_DIR: Path = BASE / "catalog"
OUT_DIR: Path = BASE / "out"

SOURCE_DIR: Path = BASE / "source"
CURATED_DIR: Path = BASE / "curated"
