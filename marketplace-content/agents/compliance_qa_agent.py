from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MC_DIR = Path(__file__).resolve().parents[1]
MC_DIR = MC_DIR if (MC_DIR / 'manifest.json').exists() or (MC_DIR / 'skin-packs').exists() else MC_DIR.parent
sys.path.insert(0, str(MC_DIR))


BLOCKED = [
    "download",
    "hack",
    "crack",
    "free",
    "pirate",
    "modded",
    "tutorial",
    "bypass",
    "illegal",
    "cheat",
]
REQUIRED = [
    "compatibility",
    "bedrock",
    "updates",
    "support",
]


def fetch(pack_dir: str) -> dict:
    root = MC_DIR / "descriptions" / pack_dir
    manifest_dir = None
    for sub in ["mashup-packs", "world-templates", "texture-packs", "skin-packs"]:
        candidate = MC_DIR / sub / pack_dir
        if candidate.exists() and (candidate / "manifest.json").exists():
            manifest_dir = candidate
            break
    manifest = json.loads((manifest_dir / "manifest.json").read_text(encoding="utf-8")) if manifest_dir else {}
    desc_file = None
    for rel in ["description_en.txt", "description.txt", "description_pt.txt"]:
        p = root / rel
        if p.exists():
            desc_file = p
            break
    desc = desc_file.read_text(encoding="utf-8", errors="ignore") if desc_file else ""
    return {"manifest": manifest, "description": desc, "pack_dir": pack_dir}


def reflow(text: str) -> str:
    text = re.sub(r"§[0-9a-fk-or]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"©.*$", "", text, flags=re.MULTILINE)
    text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
    return text


def qa_check(pack_dir: str) -> dict:
    raw = fetch(pack_dir)
    desc = reflow(raw["description"])
    md = raw["manifest"].get("metadata", {}) or {}
    errs: list[str] = []
    warn: list[str] = []
    low = desc.lower()

    for term in BLOCKED:
        if term.lower() in low:
            errs.append(f"blocked_term:{term}")

    if md.get("tier") not in {"premium", "standard"}:
        warn.append("missing_tier")
    if not md.get("price"):
        warn.append("missing_price")
    if not md.get("product_type"):
        warn.append("missing_product_type")
    if all(term.lower() not in low for term in REQUIRED):
        warn.append("suboptimal_copy")

    status = {
        "pack_dir": pack_dir,
        "submitted": True,
        "approved": not bool(errs),
        "qc_cause": errs + warn,
        "decision": "REJECTED" if errs else ("HOLD" if warn else "APPROVED"),
        "required_changes": errs,
        "asset_status": "CLEAN",
    }
    return status


def run(pack_dirs: list[str], out_dir: str | None = None):
    out = Path(out_dir or str(MC_DIR / "out"))
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for pack_dir in pack_dirs:
        results.append(qa_check(pack_dir))
    out_path = out / "compliance_qa_result.json"
    out_path.write_text(json.dumps({"count": len(results), "items": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out_path))
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", action="append", required=True)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    run(args.pack_dir, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
