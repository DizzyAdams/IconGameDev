from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


MC_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MC_DIR))


def fetch(pack_dir: str):
    manifest_path = None
    for sub in ["mashup-packs", "world-templates", "texture-packs", "skin-packs"]:
        candidate = MC_DIR / sub / pack_dir / "manifest.json"
        if candidate.exists():
            manifest_path = candidate
            break
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path else {}
    return manifest


def run(pack_dir: str, out_dir: str | None = None):
    out = Path(out_dir or str(MC_DIR / "out"))
    out.mkdir(parents=True, exist_ok=True)
    manifest = fetch(pack_dir)
    raw = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
    checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    digest = {
        "pack_dir": pack_dir,
        "sku": f"BDM-{pack_dir[:16]}-{checksum[-4:]}",
        "type": manifest.get("metadata", {}).get("product_type"),
        "price": manifest.get("metadata", {}).get("price"),
        "tier": manifest.get("metadata", {}).get("tier"),
        "status": manifest.get("metadata", {}).get("status"),
        "manifest": str(manifest.get("metadata", {}).get("manifest") or ""),
    }
    out_path = out / "sales_manifest_digest.json"
    out_path.write_text(json.dumps(digest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out_path))
    return digest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", required=True)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    run(args.pack_dir, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
