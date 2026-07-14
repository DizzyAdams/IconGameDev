from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


MC_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MC_DIR))
DEFAULT_OUT = MC_DIR / "out" / "assets-rapport.json"


def valid(text: str | None) -> bool:
    if not text:
        return False
    blacklist = [
        "minecraft logo",
        "mojang",
        "trademark",
        "© mojang",
        "microsoft logo",
        "nintendo",
        "sony",
    ]
    low = text.lower()
    return not any(b in low for b in blacklist)


def detect_assets_dir(base: Path, pack_dir: str) -> Path | None:
    for sub in ["skin-packs", "texture-packs", "world-templates", "mashup-packs"]:
        p = base / sub / pack_dir
        if p.exists() and (p / "manifest.json").exists():
            return p
    return None


def render_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    md = manifest.setdefault("metadata", {}) or {}
    header = manifest.setdefault("header", {}) or {}
    md.setdefault("authors", ["Bedrock Minemods"])
    md.setdefault("status", "pending_premium_review")
    md.setdefault("tier", md.get("tier") or "premium")
    if not header.get("description"):
        header["description"] = md.get("store_description", "")
    return manifest


def run(pack_dir: str, out_dir: str | None = None, dry_run: bool = False):
    out = Path(out_dir or str(MC_DIR / "out"))
    out.mkdir(parents=True, exist_ok=True)
    assets_dir = detect_assets_dir(MC_DIR, pack_dir)
    manifest_path = assets_dir / "manifest.json" if assets_dir else None

    result: dict[str, Any] = {
        "pack_dir": pack_dir,
        "assets_dir": str(assets_dir) if assets_dir else None,
        "manifest": str(manifest_path) if manifest_path else None,
        "queue": [],
    }
    if manifest_path is None:
        (out / "assets-rapport.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    header = manifest.get("header", {}) or {}
    md = manifest.get("metadata", {}) or {}

    result["queue"] = [
        {
            "name": header.get("name", pack_dir),
            "type": md.get("product_type", "skin_pack"),
            "author": md.get("authors", ["Bedrock Minemods"])[0],
            "status": md.get("status", "pending_premium_review"),
            "tier": md.get("tier", "premium"),
            "price": md.get("price"),
            "description": header.get("description") or md.get("store_description"),
        }
    ]

    manifest = render_manifest(manifest)
    if not dry_run:
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out_path = out / "assets-rapport.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", required=True)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--dry-run", action="store_true", default=False)
    args = ap.parse_args(argv)
    run(args.pack_dir, args.out_dir, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
