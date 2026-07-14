from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any


MC_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MC_DIR))
from src.catalog.manifest_upgrader import best_price_range, improve_store_copy
from src.paths import DESC_DIR, DIST_DIR


def read_description_from_dist(pack_dir: str) -> str:
    desc_root = DESC_DIR / pack_dir
    for rel in ("description.txt", "description_en.txt", "description_pt.txt"):
        p = desc_root / rel
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="ignore")
            break
    else:
        return ""
    text = re.sub(r"§[0-9a-fk-or]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"©.*$", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text


def manifest_from_mcpack(mcpack_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(mcpack_path, "r") as zf:
        names = [n.replace("\\", "/") for n in zf.namelist()]
        for name in names:
            if name.endswith("manifest.json"):
                data = zf.read(name)
                try:
                    return json.loads(data)
                except Exception:
                    return {}
    return {}


def pick_type(manifest: dict[str, Any], pack_dir: str) -> str:
    md = manifest.get("metadata", {})
    if md.get("product_type"):
        return md["product_type"]
    for mod in manifest.get("modules", []):
        if isinstance(mod, dict) and mod.get("type"):
            mt = mod["type"]
            if mt == "resources" and "mashup" in pack_dir.lower():
                return "mashup"
            return mt
    return "skin_pack"


def auto_reprice(manifest: dict[str, Any], pack_dir: str) -> tuple[dict[str, Any], str, str]:
    pack_type = pick_type(manifest, pack_dir)
    lo, hi = best_price_range(pack_type)
    price = round((lo + hi) / 2, 2)
    mc_coins = max(1, int(round((price * 160) / 10.0) * 10))
    tier = "premium" if price >= 2.99 else "standard"
    price_str = f"${price:.2f} ({mc_coins} MC)"
    md = manifest.setdefault("metadata", {})
    md["price"] = price_str
    md["price_usd"] = round(price, 2)
    md["price_mc"] = mc_coins
    md["tier"] = tier
    md["product_type"] = pack_type
    md["status"] = md.get("status") or "pending_premium_review"
    md.setdefault("release_notes", {})
    md["release_notes"].setdefault("1.0.0", "Premium pack prepared for store submission.")
    return manifest, pack_type, price_str


def apply_copy(manifest: dict[str, Any], pack_dir: str) -> dict[str, Any]:
    md = manifest.setdefault("metadata", {})
    header = manifest.setdefault("header", {})
    raw = read_description_from_dist(pack_dir)
    improved = improve_store_copy(raw)
    if improved:
        md["store_description"] = improved
        header["description"] = improved
    md.setdefault("authors", ["Bedrock Minemods"])
    return manifest


def audit_one(pack_dir: str, mcpack: Path) -> dict[str, Any]:
    raw_manifest = manifest_from_mcpack(mcpack)
    priced, pack_type, price = auto_reprice(raw_manifest, pack_dir)
    final = apply_copy(priced, pack_dir)
    return {
        "pack_dir": pack_dir,
        "mcpack": str(mcpack),
        "type": final.get("metadata", {}).get("product_type"),
        "price": final.get("metadata", {}).get("price"),
        "tier": final.get("metadata", {}).get("tier"),
        "store_description": final.get("metadata", {}).get("store_description"),
        "header_description": final.get("header", {}).get("description"),
        "authors": final.get("metadata", {}).get("authors"),
    }


def run(sample_size: int = 10, out_path: str | None = None):
    mc_dir = DIST_DIR
    out_file = Path(out_path) if out_path else (MC_DIR / "out" / f"audit_{sample_size}.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in mc_dir.glob("*.mcpack")])[:sample_size]
    results = []
    for mcpack in files:
        pack_dir = mcpack.stem
        try:
            results.append(audit_one(pack_dir, mcpack))
        except Exception as exc:
            results.append({"pack_dir": mcpack.stem, "mcpack": str(mcpack), "error": str(exc)})
    out_file.write_text(json.dumps({"count": len(results), "items": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out_file))
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-size", type=int, default=10)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    run(args.sample_size, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
