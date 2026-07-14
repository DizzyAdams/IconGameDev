import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

MC_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MC_DIR))
from src.catalog.pack_catalog import PackCatalog
from src.catalog.compliance_suggester import suggest
from src.catalog.manifest_upgrader import (
    best_price_range,
    read_description,
    improve_store_copy,
    write_manifest,
)
from src.paths import SKIN_DIR, TEX_DIR, WORLD_DIR, MASHUP_DIR, DESCRIPTIONS_DIR

CATALOG_DEFAULT = MC_DIR / "catalog" / "PACK_CATALOG.json"


def iterate_pack_roots(subdir: str):
    base = MC_DIR / subdir
    if not base.exists():
        return []
    out = []
    for d in sorted(base.iterdir()):
        if d.is_dir() and (d / "manifest.json").exists():
            out.append(d)
    return out


def detect_pack_type(manifest_path: Path, manifest: dict[str, Any], pack_dir: str) -> str:
    metadata = manifest.get("metadata", {})
    if metadata.get("product_type") in {"skin_pack", "resources", "world_template", "mashup"}:
        return metadata["product_type"]

    for mod in manifest.get("modules", []):
        if not isinstance(mod, dict):
            continue
        mt = mod.get("type")
        if mt == "mashup":
            return "mashup"
        if mt == "skin_pack":
            return "skin_pack"
        if mt == "world_template":
            return "world_template"
        if mt == "resources":
            rel = str(manifest_path)
            if "mashup-packs" in rel or "mashup" in pack_dir.lower():
                return "mashup"
            return "resources"
    return "skin_pack"


def process_pack(manifest_path: Path, pack_dir: str, catalog: PackCatalog, *, dry_run: bool = False) -> dict[str, Any] | None:
    try:
        manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] Invalid JSON: {manifest_path}: {exc}", file=sys.stderr)
        return None

    desc_root = manifest_path.parent.parent / "descriptions" / pack_dir
    desc_raw = read_description(desc_root, pack_dir)
    pack_type = detect_pack_type(manifest_path, manifest, pack_dir)

    metadata = manifest.setdefault("metadata", {})
    metadata["product_type"] = pack_type
    header = manifest.setdefault("header", {})
    rec = catalog.get(pack_dir)

    price_usd = None
    tier = None
    if isinstance(rec, dict):
        raw_price = rec.get("price_usd")
        if isinstance(raw_price, (int, float)):
            price_usd = float(raw_price)
        elif rec.get("price"):
            m = re.search(r"([0-9]+(?:\.[0-9]{2})?)", str(rec["price"]))
            if m:
                price_usd = float(m.group(1))
        tier = rec.get("tier") or metadata.get("tier")

    lo, hi = best_price_range(pack_type)
    if price_usd is None:
        price_usd = float(lo)
    price_usd = max(lo, min(price_usd, hi))
    price_mc = max(1, int(round((price_usd * 160) / 10.0) * 10))
    if tier is None:
        tier = "premium" if price_usd >= 2.99 else "standard"

    metadata["price"] = f"${price_usd:.2f} ({price_mc} MC)"
    metadata["price_usd"] = round(price_usd, 2)
    metadata["price_mc"] = price_mc
    metadata["tier"] = tier

    improved = improve_store_copy(desc_raw)
    if improved:
        metadata["store_description"] = improved
        header["description"] = improved

    if isinstance(rec, dict) and rec.get("author"):
        metadata["authors"] = [str(rec["author"])]

    if isinstance(rec, dict) and rec.get("tags"):
        metadata["tags"] = [str(t) for t in rec["tags"]][:6]

    metadata.setdefault("status", "pending_premium_review")
    metadata.setdefault("release_notes", {})
    metadata["release_notes"].setdefault("1.0.0", "Premium pack prepared for store submission.")
    manifest.setdefault("format_version", 2)

    if not dry_run:
        write_manifest(manifest_path, manifest)

    return {
        "dir": pack_dir,
        "type": pack_type,
        "manifest": str(manifest_path),
        "description": header.get("description"),
        "price": metadata.get("price"),
        "tier": metadata.get("tier"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skin-dir", default="skin-packs")
    ap.add_argument("--texture-dir", default="texture-packs")
    ap.add_argument("--world-dir", default="world-templates")
    ap.add_argument("--mashup-dir", default="mashup-packs")
    ap.add_argument("--catalog", default=str(CATALOG_DEFAULT))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    catalog = PackCatalog(catalog_path=Path(args.catalog))
    processed = []
    errors = []

    for subdir in [args.skin_dir, args.texture_dir, args.world_dir, args.mashup_dir]:
        roots = iterate_pack_roots(subdir)
        for pack_root in roots:
            pack_dir = pack_root.name
            try:
                row = process_pack(pack_root / "manifest.json", pack_dir, catalog, dry_run=bool(args.dry_run))
                if row is None:
                    continue
                processed.append(row)
                if args.limit and len(processed) >= args.limit:
                    break
            except Exception as exc:
                errors.append({"dir": pack_dir, "error": str(exc)})
        if args.limit and len(processed) >= args.limit:
            break

    summary = {
        "processed": processed,
        "errors": errors,
        "count": len(processed),
        "types": {},
    }
    for row in processed:
        t = row.get("type", "unknown")
        summary["types"][t] = summary["types"].get(t, 0) + 1
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    catalog.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
