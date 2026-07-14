from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


MC_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MC_DIR))


def detect_subdir(pack_dir: str) -> str:
    for sub in ["mashup-packs", "world-templates", "texture-packs", "skin-packs"]:
        if (MC_DIR / sub / pack_dir).exists() and (MC_DIR / sub / pack_dir / "manifest.json").exists():
            return sub
    return "skin-packs"


def index_pack(pack_dir: str) -> dict:
    subdir = detect_subdir(pack_dir)
    manifest_path = MC_DIR / subdir / pack_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    out = {
        "pack_dir": pack_dir,
        "store_url": f"/store/{pack_dir}",
        "manifest": str(manifest_path),
        "price": manifest.get("metadata", {}).get("price"),
        "tier": manifest.get("metadata", {}).get("tier"),
        "description": manifest.get("header", {}).get("description") or manifest.get("metadata", {}).get("store_description"),
        "product_type": manifest.get("metadata", {}).get("product_type") or subdir,
    }
    return out


def run(pack_dir: str, out_dir: str | None = None, sync: bool = False):
    out = Path(out_dir or str(MC_DIR / "out"))
    out.mkdir(parents=True, exist_ok=True)
    entry = index_pack(pack_dir)
    out_path = out / f"catalog_index_{pack_dir}.json"
    out_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    if sync:
        catalog_path = out / "catalog_index.json"
        catalog = []
        if catalog_path.exists():
            try:
                catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            except Exception:
                catalog = []
        catalog = [x for x in catalog if x.get("pack_dir") != pack_dir]
        catalog.append(entry)
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out_path))
    return entry


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", required=True)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--sync-catalog", action="store_true", default=False)
    args = ap.parse_args(argv)
    run(args.pack_dir, args.out_dir, bool(args.sync_catalog))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
