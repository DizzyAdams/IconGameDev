"""Incremental mass product generator up to TARGET_PRODUCTS (~5000).

Safe default behavior:
- only creates NEW packs that do not already exist
- keeps skin_pack as the primary growth channel (high Microsoft sales share)
- creates packs under skin-packs/, texture-packs/, world-templates/, mashup-packs/
- keeps descriptions/ and catalog/ in sync
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
import random
import string
from pathlib import Path
from typing import Any

MC_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MC_DIR))
from src.catalog.pack_catalog import PackCatalog  # noqa: E402


DEFAULT_CATALOG_PATH = MC_DIR / "catalog" / "PACK_CATALOG.json"
DESCRIPTIONS_DIR = MC_DIR / "descriptions"

TARGET_PRODUCTS = 5000
BATCH = 200

# NOTE: themes must never match IP_BLOCKED in scripts/audit_compliance.py
# (anime/kawaii/manga/otaku/waifu and franchise names are quarantined).
SKIN_THEMES = [
    "fantasy","scifi","medieval","modern","holiday","game","movie",
    "nature","cyber","retro","sports","music","space","horror","cute",
    "pirate","ninja","superhero","animal","myth","street","beach","winter",
    "steampunk","gothic","futuristic","tribal","robot","mystic","candy"
]
TEX_THEMES = [
    "realistic","8bit","16x","32x","dark","light","pvp","sky",
    "forest","desert","nether","end","cave","urban","neon","pastel",
    "faithful","low-res","ultra","water","lava","crystal","space"
]
WORLD_THEMES = [
    "survival","parkour","pvp","minigame","city","castle","island","space",
    "adventure","maze","tower-defense","ctf","hunger-games","prison","skyblock"
]
MASHUP_THEMES = [
    "cyberpunk","fantasy-rpg","horror","steampunk",
    "space-odyssey","medieval","tropical","underwater","western","viking",
    "crystal-realm"
]


def _slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "pack"


def _uid() -> str:
    return str(uuid.uuid4())


def _words(n: int) -> str:
    vocab = list(string.ascii_lowercase)
    return "-".join("".join(random.choices(vocab, k=random.randint(3,6))) for _ in range(max(1,n)))


def _store_copy(title: str, theme: str, kind: str) -> str:
    theme = theme.replace("-", " ").title()
    kind = kind.replace("_", " ").title()
    return f"{theme} {kind} — premium content for Minecraft Bedrock."


def _manifest(header_name: str, pack_type: str, header_uuid: str, module_uuid: str) -> dict[str, Any]:
    return {
        "format_version": 2,
        "header": {
            "name": header_name,
            "description": header_name,
            "uuid": header_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {
                "type": pack_type,
                "uuid": module_uuid,
                "version": [1, 0, 0],
            }
        ],
    }


def _skin_pack(theme: str, idx: int) -> dict[str, Any]:
    slug = _slug(f"{theme}-skins-{idx:04d}")
    name = f"{theme.replace('-',' ').title()} Skins {idx:04d}"
    header_uuid = _uid()
    module_uuid = _uid()
    manifest = _manifest(name, "skin_pack", header_uuid, module_uuid)
    pack_dir = MC_DIR / "skin-packs" / slug
    textures_dir = pack_dir / "textures" / "skins"
    textures_dir.mkdir(parents=True, exist_ok=True)
    skins = []
    for i in range(8):
        skin_name = f"{theme.title()}{i+1}"
        skins.append({
            "localization_name": skin_name,
            "geometry": "geometry.humanoid.custom",
            "texture": f"{skin_name}.png",
            "type": "free",
        })
    skins_json = {
        "skins": skins,
        "serialize_name": name,
        "localization_name": name,
    }
    return {
        "dir": slug,
        "path": str(pack_dir / "manifest.json"),
        "product_type": "skin_pack",
        "name": name,
        "store_description": _store_copy(name, theme, "skin pack"),
        "manifest": manifest,
        "skins_json": skins_json,
        "pack_dir": pack_dir,
    }


def _texture_pack(theme: str, idx: int) -> dict[str, Any]:
    slug = _slug(f"{theme}-textures-{idx:04d}")
    name = f"{theme.replace('-',' ').title()} Textures {idx:04d}"
    header_uuid = _uid()
    module_uuid = _uid()
    manifest = _manifest(name, "resources", header_uuid, module_uuid)
    pack_dir = MC_DIR / "texture-packs" / slug
    pack_dir.mkdir(parents=True, exist_ok=True)
    return {
        "dir": slug,
        "path": str(pack_dir / "manifest.json"),
        "product_type": "resources",
        "name": name,
        "store_description": _store_copy(name, theme, "texture pack"),
        "manifest": manifest,
        "pack_dir": pack_dir,
    }


def _world(theme: str, idx: int) -> dict[str, Any]:
    slug = _slug(f"{theme}-world-{idx:04d}")
    name = f"{theme.replace('-',' ').title()} World {idx:04d}"
    header_uuid = _uid()
    module_uuid = _uid()
    manifest = _manifest(name, "world_template", header_uuid, module_uuid)
    pack_dir = MC_DIR / "world-templates" / slug
    pack_dir.mkdir(parents=True, exist_ok=True)
    return {
        "dir": slug,
        "path": str(pack_dir / "manifest.json"),
        "product_type": "world_template",
        "name": name,
        "store_description": _store_copy(name, theme, "world template"),
        "manifest": manifest,
        "pack_dir": pack_dir,
    }


def _mashup(theme: str, idx: int) -> dict[str, Any]:
    slug = _slug(f"{theme}-mashup-{idx:04d}")
    name = f"{theme.replace('-',' ').title()} Mashup {idx:04d}"
    header_uuid = _uid()
    module_uuid = _uid()
    manifest = _manifest(name, "mashup", header_uuid, module_uuid)
    pack_dir = MC_DIR / "mashup-packs" / slug
    pack_dir.mkdir(parents=True, exist_ok=True)
    return {
        "dir": slug,
        "path": str(pack_dir / "manifest.json"),
        "product_type": "mashup",
        "name": name,
        "store_description": _store_copy(name, theme, "mashup pack"),
        "manifest": manifest,
        "pack_dir": pack_dir,
    }


def generator(kind: str, theme: str, idx: int) -> dict[str, Any]:
    if kind == "skin_pack":
        return _skin_pack(theme, idx)
    if kind == "resources":
        return _texture_pack(theme, idx)
    if kind == "world_template":
        return _world(theme, idx)
    if kind == "mashup":
        return _mashup(theme, idx)
    raise ValueError(kind)


def write_description(pack_dir: Path, store_description: str) -> Path:
    desc_dir = DESCRIPTIONS_DIR / pack_dir.name
    desc_dir.mkdir(parents=True, exist_ok=True)
    out = desc_dir / "description.txt"
    out.write_text(store_description + "\n", encoding="utf-8")
    return out


def write_pack(item: dict[str, Any]) -> None:
    pack_dir = item["pack_dir"]
    manifest_path = Path(item["path"])
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(item["manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    if item.get("skins_json"):
        (pack_dir / "skins.json").write_text(json.dumps(item["skins_json"], indent=2, ensure_ascii=False), encoding="utf-8")
    write_description(pack_dir, item["store_description"])


def catalog_bump(catalog: PackCatalog, item: dict[str, Any]) -> None:
    catalog.update(item["dir"], {
        "dir": item["dir"],
        "path": item["path"],
        "product_type": item["product_type"],
        "price_usd": 2.99 if item["product_type"] in {"skin_pack", "mashup"} else 1.99,
        "price": f"${2.99 if item['product_type'] in {'skin_pack','mashup'} else 1.99:.2f}",
        "tier": "standard",
        "store_description": item["store_description"],
    })


def run(target: int = TARGET_PRODUCTS, batch: int = BATCH, seed: int = 42) -> int:
    random.seed(seed)
    catalog = PackCatalog(catalog_path=DEFAULT_CATALOG_PATH)

    existing = {
        "skin_pack": {p.name for p in (MC_DIR / "skin-packs").glob("*") if p.is_dir()} if (MC_DIR / "skin-packs").exists() else set(),
        "resources": {p.name for p in (MC_DIR / "texture-packs").glob("*") if p.is_dir()} if (MC_DIR / "texture-packs").exists() else set(),
        "world_template": {p.name for p in (MC_DIR / "world-templates").glob("*") if p.is_dir()} if (MC_DIR / "world-templates").exists() else set(),
        "mashup": {p.name for p in (MC_DIR / "mashup-packs").glob("*") if p.is_dir()} if (MC_DIR / "mashup-packs").exists() else set(),
    }

    counts = {k: len(v) for k, v in existing.items()}
    current = sum(counts.values())
    if current >= target:
        print(json.dumps({"status": "already_done", "current": current, "target": target}))
        return 0

    quotas = {
        "skin_pack": int(target * 0.65),
        "resources": int(target * 0.18),
        "world_template": int(target * 0.12),
        "mashup": int(target * 0.05),
    }
    theme_map = {
        "skin_pack": SKIN_THEMES,
        "resources": TEX_THEMES,
        "world_template": WORLD_THEMES,
        "mashup": MASHUP_THEMES,
    }

    counters = {k: 1 for k in counts}
    created = 0
    while current < target and created < batch:
        for kind, quota in quotas.items():
            if current >= target or created >= batch:
                break
            while counts.get(kind, 0) < quota and current < target and created < batch:
                theme = random.choice(theme_map[kind])
                idx = counters[kind]
                counters[kind] += 1
                base_slug = _slug(f"{theme}-{kind}-{idx:04d}")
                if base_slug in existing.get(kind, set()):
                    continue
                item = generator(kind, theme, idx)
                if item["dir"] in existing.get(kind, set()):
                    continue
                write_pack(item)
                catalog_bump(catalog, item)
                existing.setdefault(kind, set()).add(item["dir"])
                counts[kind] = counts.get(kind, 0) + 1
                current += 1
                created += 1

    catalog.commit()
    return created


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=TARGET_PRODUCTS)
    ap.add_argument("--batch", type=int, default=BATCH)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)
    created = run(target=args.target, batch=args.batch, seed=args.seed)
    print(json.dumps({"created": created, "target": args.target}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
