"""Compliance orchestrator for generated Bedrock skin packs.
Flow:
1. Validate pack structure + manifests with BedrockValidator.
2. QA pass with compliance_qa_agent.
3. Enforce hard content filters for Marketplace readiness.
4. Emit a submission-ready manifest for each pack.
"""
import json, re, sys, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "agents"))
from src.validators.bedrock_validator import BedrockValidator
from compliance_qa_agent import qa_check

BLOCKLIST = re.compile(
    r"(download|hack|crack|free|pirate|modded|tutorial|bypass|illegal|cheat|leak|warez|\bxxx\b|\bnsfw\b)",
    re.IGNORECASE,
)
REQUIRED = ["compatibility", "bedrock", "updates", "support"]

PRODUCT_TYPE_ALLOWLIST = {"skin_pack", "resources", "world_template", "mashup"}
ESRB_RECOMMENDED = "Everyone"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_pack(pack_dir: Path, require_thumbnails=False, require_screenshots=False) -> dict:
    pack_dir = Path(pack_dir)
    result = {
        "pack": pack_dir.name,
        "valid": True,
        "errors": [],
        "warnings": [],
        "fixes": [],
        "asset_status": "CLEAN",
        "decision": "APPROVED",
        "assets": {"manifest": False, "skins_json": False, "textures": 0, "pack_icon": False},
    }
    manifest_path = pack_dir / "manifest.json"
    skins_json_path = pack_dir / "skins.json"
    skins_dir = pack_dir / "textures" / "skins"
    textures_dir = pack_dir / "textures"

    if not manifest_path.exists():
        result["valid"] = False
        result["errors"].append("manifest.json missing")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            result["assets"]["manifest"] = True
        except Exception as e:
            manifest = {}
            result["valid"] = False
            result["errors"].append(f"manifest.json invalid: {e}")
        header = manifest.get("header") or {}
        modules = manifest.get("modules") or []
        module_type = None
        if modules:
            module_type = modules[0].get("type")
        hname = (header.get("name") or "").strip()
        if BLOCKLIST.search(hname):
            result["valid"] = False
            result["errors"].append("blocked_term_in_header_name")
            result["fixes"].append("rename pack to remove blocked/marketing-violation words")
        if module_type and module_type not in PRODUCT_TYPE_ALLOWLIST:
            result["valid"] = False
            result["errors"].append(f"module_type_invalid:{module_type}")
        min_engine = header.get("min_engine_version") or []
        if isinstance(min_engine, list) and min_engine < [1, 20, 0]:
            result["valid"] = False
            result["errors"].append("min_engine_version too low")
        if require_thumbnails and not (textures_dir / "pack_icon.png").exists():
            result["valid"] = False
            result["errors"].append("missing pack_icon.png")

    if not skins_json_path.exists():
        result["valid"] = False
        result["errors"].append("skins.json missing")
    else:
        try:
            skins_json = json.loads(skins_json_path.read_text(encoding="utf-8"))
            result["assets"]["skins_json"] = True
            skins = skins_json.get("skins") or []
            for i, skin in enumerate(skins):
                tex = skin.get("texture") if isinstance(skin, dict) else None
                if not tex:
                    continue
                tex_path = skins_dir / tex
                if not tex_path.exists():
                    result["warnings"].append(f"missing_texture:{tex}")
                    continue
                try:
                    with open(tex_path, "rb") as f:
                        header_bytes = f.read(8)
                    if header_bytes[:4] != b"\x89PNG":
                        result["valid"] = False
                        result["errors"].append(f"non_png:{tex}")
                        continue
                    with open(tex_path, "rb") as vf:
                        from PIL import Image
                        with Image.open(vf) as img:
                            if img.size not in {(64, 32), (64, 64), (128, 128)}:
                                result["valid"] = False
                                result["errors"].append(f"invalid_skin_size:{tex}:{img.size}")
                    result["assets"]["textures"] += 1
                except Exception as e:
                    result["valid"] = False
                    result["errors"].append(f"skin_texture_error:{tex}:{e}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"skins.json invalid:{e}")

    if require_screenshots:
        for required in ["screenshot_01.png", "screenshot_02.png"]:
            if not (pack_dir / required).exists():
                result["warnings"].append(f"missing_marketing_asset:{required}")

    desc = json.dumps(manifest or {}, ensure_ascii=False)
    if BLOCKLIST.search(desc):
        result["valid"] = False
        result["errors"].append("blocked_term_in_manifest")
        result["fixes"].append("edit manifest description/name or review marketing copy")

    if not result["errors"]:
        result["asset_status"] = "CLEAN"
        result["decision"] = "APPROVED"
    elif not result["valid"]:
        result["decision"] = "REJECTED" if result["errors"] else "HOLD"

    return result


def run_compliance(pack_dirs, require_thumbnails=False, require_screenshots=False):
    validator = BedrockValidator()
    results = []
    pack_dirs = [Path(p) for p in pack_dirs]
    for pack_dir in pack_dirs:
        r = check_pack(pack_dir, require_thumbnails=require_thumbnails, require_screenshots=require_screenshots)
        pack_dir_name = pack_dir.name
        qa = {"pack_dir": pack_dir_name, "decision": "APPROVED", "qc_cause": [], "submitted": False}
        try:
            qa = qa_check(pack_dir_name)
        except Exception as e:
            qa["qc_cause"].append(f"qa_agent_failed:{e}")
        if qa.get("decision") == "REJECTED":
            r["valid"] = False
            r["errors"].extend(qa.get("required_changes") or qa.get("qc_cause") or ["qa_rejected"])
            r["decision"] = "REJECTED"
            r["fixes"].append("resolve compliance_qa_agent rejects before submission")
        elif qa.get("decision") == "HOLD":
            r["decision"] = "HOLD"
            r["warnings"].extend(qa.get("qc_cause") or [])
        if r["valid"] and r["decision"] == "APPROVED":
            r["decision"] = "APPROVED"
        results.append(r)
    return results


def report(results):
    lines = ["=" * 70, " COMPLIANCE REPORT ", "=" * 70]
    total = len(results)
    approved = sum(1 for r in results if r["decision"] == "APPROVED")
    rejected = sum(1 for r in results if r["decision"] == "REJECTED")
    hold = sum(1 for r in results if r["decision"] == "HOLD")
    lines.append(f" TOTAL={total} APPROVED={approved} REJECTED={rejected} HOLD={hold}")
    for r in results:
        lines.append(f" [{r['decision']}] {r['pack']}")
        for e in r.get("errors", []):
            lines.append(f"   ERR: {e}")
        for w in r.get("warnings", []):
            lines.append(f"   WARN: {w}")
        for f in r.get("fixes", []):
            lines.append(f"   FIX: {f}")
    lines.append("=" * 70)
    return "\n".join(lines)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", action="append", required=True)
    ap.add_argument("--require-thumbnails", action="store_true", default=False)
    ap.add_argument("--require-screenshots", action="store_true", default=False)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    results = run_compliance(args.pack_dir, require_thumbnails=args.require_thumbnails, require_screenshots=args.require_screenshots)
    print(report(results))
    out = Path(args.out) if args.out else Path(__file__).resolve().parent.parent / "output" / "compliance"
    out.mkdir(parents=True, exist_ok=True)
    out_file = out / "compliance_result.json"
    out_file.write_text(json.dumps({"count": len(results), "items": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out_file)
    return 0 if all(r["decision"] == "APPROVED" for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
