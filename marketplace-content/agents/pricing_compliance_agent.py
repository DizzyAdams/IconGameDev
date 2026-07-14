from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


MC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MC_DIR))
from src.catalog.manifest_upgrader import best_price_range, improve_store_copy  # noqa: E402


def load_description(pack_dir: str) -> str | None:
    desc_root = MC_DIR / "descriptions" / pack_dir
    for rel in ("description.txt", "description_en.txt", "description_pt.txt"):
        p = desc_root / rel
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="ignore")
            break
    else:
        return None
    text = re.sub(r"§[0-9a-fk-or]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"©.*$", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text


def load_manifest(pack_dir: str, subdir: str) -> dict[str, Any] | None:
    candidates = [MC_DIR / subdir / pack_dir / "manifest.json"]
    if "mashup" in pack_dir:
        candidates.append(MC_DIR / "mashup-packs" / pack_dir / "manifest.json")
    for p in candidates:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return None


def save_manifest(pack_dir: str, manifest: dict[str, Any], dry_run: bool = False) -> str | None:
    # write back to first existing manifest under mc/
    for subdir in ["skin-packs", "texture-packs", "world-templates", "mashup-packs"]:
        candidate = MC_DIR / subdir / pack_dir / "manifest.json"
        if candidate.exists():
            if not dry_run:
                candidate.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return str(candidate)
    return None


def auto_reprice(manifest: dict[str, Any], pack_type: str | None) -> dict[str, Any]:
    md = manifest.setdefault("metadata", {})
    pt = pack_type or md.get("product_type")
    if "mashup" in str(manifest).lower() or (pt or "").lower() == "mashup":
        pt = "mashup"
    lo, hi = best_price_range(pt or "skin_pack")
    price = round((lo + hi) / 2, 2)
    mc_coins = max(1, int(round((price * 160) / 10.0) * 10))
    md.setdefault("price_usd", price)
    md["price"] = f"${price:.2f} ({mc_coins} MC)"
    md["price_mc"] = mc_coins
    md["tier"] = md.get("tier") or ("premium" if price >= 2.99 else "standard")
    md["product_type"] = pt
    md["status"] = md.get("status") or "pending_premium_review"
    md.setdefault("release_notes", {})
    md["release_notes"].setdefault("1.0.0", "Premium pack prepared for store submission.")
    return manifest


def run(pack_dir: str, subdir_hint: str | None = None, dry_run: bool = False, limit: int = 0, out_dir: str | None = None):
    if out_dir is None:
        out_dir = str(MC_DIR / "out")
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    catalogue: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    queue: list[tuple[str, str]] = []

    if pack_dir:
        queue.append((pack_dir, subdir_hint or "skin-packs"))
    else:
        for subdir in ["skin-packs", "texture-packs", "world-templates", "mashup-packs"]:
            base = MC_DIR / subdir
            if not base.exists():
                continue
            for d in sorted(base.iterdir()):
                if d.is_dir() and (d / "manifest.json").exists():
                    queue.append((d.name, subdir))

    done = 0
    for pack, subdir in queue:
        try:
            manifest = load_manifest(pack, subdir)
            if manifest is None:
                errors.append({"dir": pack, "error": "manifest not found"})
                continue
            desc_raw = load_description(pack) or ""
            improved = improve_store_copy(desc_raw)
            type_hint = {
                "skin-packs": "skin_pack",
                "texture-packs": "resources",
                "world-templates": "world_template",
                "mashup-packs": "mashup",
            }.get(subdir, "skin_pack")
            manifest = auto_reprice(manifest, type_hint)
            if improved:
                manifest.setdefault("metadata", {})["store_description"] = improved
                manifest.setdefault("header", {})["description"] = improved
            dest = save_manifest(pack, manifest, dry_run=dry_run)
            catalogue.append({
                "dir": pack,
                "path": dest,
                "price": manifest.get("metadata", {}).get("price"),
                "tier": manifest.get("metadata", {}).get("tier"),
                "description": manifest.get("metadata", {}).get("store_description"),
            })
            done += 1
            if limit and done >= limit:
                break
        except Exception as exc:  # pragma: no cover - defensive
            errors.append({"dir": pack, "error": str(exc)})

    report = {
        "pack_dir": pack_dir or "__all__",
        "count": len(catalogue),
        "errors": len(errors),
        "files": [c["path"] for c in catalogue if c["path"]],
        "catalogue": catalogue,
        "errors_detail": errors,
    }
    out_path = Path(out_dir) / "org-pricing-compliance-report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out_path))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", default="")
    ap.add_argument("--subdir-hint", default="skin-packs")
    ap.add_argument("--dry-run", action="store_true", default=False)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    run(
        pack_dir=args.pack_dir,
        subdir_hint=args.subdir_hint,
        dry_run=bool(args.dry_run),
        limit=int(args.limit),
        out_dir=args.out_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
