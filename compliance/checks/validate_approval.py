#!/usr/bin/env python3
"""validate_approval.py — first-try approval validator for ALL live packs.

Scans every source pack under marketplace-content/{skin-packs,texture-packs,
world-templates,mashup-packs} and reports, with exact failure reasons, which
packs would be rejected by an automated marketplace gate (Microsoft / Roblox /
Epic). This is the real "100% approval accuracy" enforcer: it validates the
packs that actually ship, not a stale dist/ folder.

For each pack it checks:
  * manifest.json present + valid JSON
  * header.uuid is a v4 UUID; modules have v4 UUIDs
  * header.version is [major,minor,patch]
  * title <= 60 chars (Partner Center hard limit)
  * name is not on the IP blocklist
  * skin_pack has skins.json with >=1 skin
  * the pack BUILDS into a valid .mcpack (assets generated deterministically)

Output: a readiness % and a JSON report (compliance/checks/approval_report.json).
Exit 0 = 100% buildable/approvable; 2 = any pack fails.

Usage:
    python compliance/checks/validate_approval.py
    python compliance/checks/validate_approval.py --pack-dir marketplace-content
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from approval_pack_builder import build_pack_bytes, inspect_source  # noqa: E402

PACK_FOLDERS = {
    "skin-packs": "skin_pack",
    "texture-packs": "resources",
    "world-templates": "world_template",
    "mashup-packs": "mashup",
}


def validate(root: Path, verbose: bool = False) -> dict:
    failures: list[dict] = []
    total = 0
    by_type: dict[str, int] = {}
    build_errors = 0

    for folder in PACK_FOLDERS:
        fp = root / "marketplace-content" / folder
        if not fp.is_dir():
            continue
        for d in sorted(os.listdir(fp)) if (fp.is_dir()) else []:
            sd = fp / d
            if not sd.is_dir():
                continue
            total += 1
            by_type[folder] = by_type.get(folder, 0) + 1
            info = inspect_source(str(sd))
            pack_problems = list(info.problems)
            # attempt a real build (this also validates asset generation)
            try:
                _ = build_pack_bytes(str(sd))
            except Exception as e:
                pack_problems.append(f"build failed: {e}")
                build_errors += 1
            if pack_problems:
                failures.append({"pack": f"{folder}/{d}", "type": info.ptype, "problems": pack_problems})
                if verbose:
                    print(f"  FAIL {folder}/{d}: {pack_problems}")

    passed = total - len(failures)
    pct = round(passed / total * 100, 2) if total else 0.0
    report = {
        "total_packs": total,
        "passed": passed,
        "failed": len(failures),
        "build_errors": build_errors,
        "approval_pct": pct,
        "by_type": by_type,
        "failures": failures,
        "verdict": "100% APPROVABLE" if not failures else f"{pct:.1f}% APPROVABLE",
    }
    return report


def main(argv=None) -> int:
    import os
    ap = argparse.ArgumentParser(description="First-try approval validator for live packs")
    ap.add_argument("--pack-dir", default="marketplace-content")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    print("=" * 72)
    print(" ICONMINEMODS — LIVE-PACK APPROVAL VALIDATOR")
    print("=" * 72)
    report = validate(root, verbose=args.verbose)

    print(f"\n Total packs scanned : {report['total_packs']}")
    print(f" Build-OK            : {report['passed']}")
    print(f" Failed              : {report['failed']}  (build errors: {report['build_errors']})")
    print(f" Approval accuracy   : {report['approval_pct']}%")
    print(f" By type             : {report['by_type']}")
    if report["failures"]:
        print(f"\n First 25 failures:")
        for f in report["failures"][:25]:
            print(f"   - {f['pack']}: {f['problems']}")
    print(f"\n VERDICT: {report['verdict']}")
    print("=" * 72)

    out = root / "compliance" / "checks" / "approval_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f" Report: {out}")

    return 0 if not report["failures"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
