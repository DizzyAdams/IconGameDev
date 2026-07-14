from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from src.catalog.pack_catalog import PackCatalog
from src.catalog.compliance_suggester import suggest, COMPLIANCE_RISK_HINTS


COIN_PER_USD = 160
DEFAULT_USD_TO_MC = {
    "skin_pack": (1.99, 3.99),
    "resources": (2.99, 5.99),
    "world_template": (3.99, 5.99),
    "mashup": (5.99, 7.99),
}
CAPTION_MAX_LEN = 140
TAG_LIMIT = 5
FORBIDDEN_PHRASES = [
    "bait-and-switch",
    "sale ends",
    "discount today",
    "only today",
    "must buy",
    "limited time offer",
]


def best_price_range(pack_type: str) -> tuple[float, float]:
    return DEFAULT_USD_TO_MC.get(pack_type, (1.99, 3.99))


def keyword_score(text: str, keywords: list[str]) -> int:
    t = text.lower()
    return sum(1 for k in keywords if k.lower() in t)


def sanitize_description(desc: str) -> str:
    s = desc.strip().replace("\r", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > CAPTION_MAX_LEN:
        s = s[:CAPTION_MAX_LEN - 1].rstrip() + "…"
    for bad in FORBIDDEN_PHRASES:
        s = s.replace(bad, "great value")
    return s


def safe_tags(tags: list[str]) -> list[str]:
    seen = []
    for tag in tags:
        t = re.sub(r"[^a-z0-9\- ]+", "", tag.lower()).strip()
        if t and t not in seen and len(seen) < TAG_LIMIT:
            seen.append(t.replace(" ", "-"))
    return seen


def price_to_mc(usd: float) -> int:
    return max(1, int(round((usd * COIN_PER_USD) / 10.0) * 10))


def ensure_metadata(manifest_path: Path, pack_dir: str, catalog: PackCatalog, *, dry_run: bool=False) -> dict[str, Any]:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    rec = catalog.get(pack_dir)

    header = manifest.setdefault("header", {})
    existing_desc = header.get("description", "")
    if isinstance(rec, dict) and rec.get("description"):
        header["description"] = sanitize_description(rec["description"])
    elif existing_desc:
        header["description"] = sanitize_description(existing_desc)

    metadata_block = manifest.setdefault("metadata", {})

    pack_type = "skin_pack"
    modules = manifest.get("modules", [])
    if isinstance(modules, list):
        for m in modules:
            if isinstance(m, dict):
                mt = m.get("type")
                if mt in {"skin_pack", "resources", "world_template", "mashup"}:
                    pack_type = mt
                    break

    price_usd = None
    expected_mc = None
    expected_band = None
    if isinstance(rec, dict):
        raw_price = rec.get("price_usd")
        if isinstance(raw_price, (int, float)):
            price_usd = float(raw_price)
        elif rec.get("price"):
            m = re.search(r"\$?([0-9]+(?:\.[0-9]{2})?)", str(rec["price"]))
            if m:
                price_usd = float(m.group(1))
        expected_band = rec.get("tier")

    sugg = suggest(pack_type, current_price_usd=price_usd)

    if price_usd is None:
        price_usd = float(sugg.get("suggested_price_usd", best_price_range(pack_type)[0]))

    price_usd = max(best_price_range(pack_type)[0], min(price_usd, best_price_range(pack_type)[1]))
    expected_mc = price_to_mc(price_usd)

    metadata_block.setdefault("authors", [rec.get("author", "Bedrock Minemods") if isinstance(rec, dict) else "Bedrock Minemods"])
    metadata_block.setdefault("product_type", pack_type)
    metadata_block.setdefault("price_usd", round(price_usd, 2))
    metadata_block.setdefault("price_mc", expected_mc)
    metadata_block.setdefault("price", f"${price_usd:.2f} ({expected_mc} MC)")
    metadata_block.setdefault("tier", "premium" if price_usd >= 2.99 else "standard")
    metadata_block.setdefault("status", "pending_review")

    if isinstance(rec, dict) and rec.get("tags"):
        tags = safe_tags(rec["tags"])
    else:
        tags = [pack_type.replace("_", " "), "minecraft", "bedrock", "premium"]
    metadata_block.setdefault("tags", tags)

    desc_text = header.get("description", "")
    metadata_block.setdefault("conversion_keywords", {
        "quality_signals": keyword_score(desc_text, ["amazing", "epic", "premium", "complete", "detailed", "original"]),
        "theme_signals": keyword_score(desc_text, ["anime", "fantasy", "cyberpunk", "medieval", "horror", "pvp", "winter", "summer"]),
        "pack_type": pack_type,
    })

    if isinstance(rec, dict) and rec.get("compliance_risk"):
        metadata_block.setdefault("compliance_risk", rec["compliance_risk"])
        metadata_block.setdefault("compliance_review", COMPLIANCE_RISK_HINTS.get(rec["compliance_risk"], ""))
    else:
        metadata_block.setdefault("compliance_risk", "low")
        metadata_block.setdefault("compliance_review", COMPLIANCE_RISK_HINTS["low"])

    metadata_block.setdefault("release_notes", {
        "1.0.0": "Initial premium submission prepared for Microsoft Partner Program review."
    })

    manifest.setdefault("format_version", 2)

    if not dry_run:
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def iter_manifests(root: Path):
    for manifest_path in root.rglob("manifest.json"):
        if manifest_path.is_file():
            yield manifest_path


def main(argv: list[str] | None=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs-dir", default="skin-packs", help="Base packs dir relative to marketplace-content")
    ap.add_argument("--texture-dir", default="texture-packs")
    ap.add_argument("--world-dir", default="world-templates")
    ap.add_argument("--mashup-dir", default="mashup-packs")
    ap.add_argument("--catalog", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    mc_dir = Path(__file__).resolve().parent.parent.parent
    catalog_path = Path(args.catalog) if args.catalog else mc_dir / "catalog" / "PACK_CATALOG.json"
    catalog = PackCatalog(catalog_path=catalog_path)

    processed = []
    for subdir in [args.packs_dir, args.texture_dir, args.world_dir, args.mashup_dir]:
        base = mc_dir / subdir
        if not base.exists():
            continue
        for manifest_path in iter_manifests(base):
            pack_dir = manifest_path.parent.name
            before = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest = ensure_metadata(manifest_path, pack_dir, catalog, dry_run=bool(args.dry_run))
            processed.append({
                "dir": pack_dir,
                "manifest": str(manifest_path),
                "metadata": manifest.get("metadata", {}),
            })

    print(json.dumps({"processed": processed, "count": len(processed)}, indent=2, ensure_ascii=False))
    catalog.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
