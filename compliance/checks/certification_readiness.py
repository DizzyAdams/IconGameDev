#!/usr/bin/env python3
"""Microsoft Store certification readiness check (dependency-free, stdlib only).

Scans the repository for required compliance artifacts and the dist/ folder for
IP-blocked pack names, then reports readiness across Store certification
dimensions. It does NOT re-validate pack structure -- see
`marketplace-content/scripts/audit_compliance.py` and `run_compliance.py`.

Usage:
    python compliance/checks/certification_readiness.py
    python compliance/checks/certification_readiness.py --root . --pack-dir marketplace-content/dist

Exit code: 0 = all required artifacts present AND no IP-blocked names in dist.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Same IP blocklist as scripts/audit_compliance.py and scripts/safe-rename.py.
IP_BLOCKED = [
    "pokemon", "naruto", "dragon-ball", "bleach", "genshin", "fnaf",
    "hello-kitty", "demon-slayer", "chainsaw-man", "one-piece", "jujutsu",
    "sonic", "tadc", "attack-on-titan", "little-nightmares", "marvel",
]

# Required compliance artifacts for Microsoft Store / Partner Program certification.
REQUIRED_ARTIFACTS = {
    "Partner requirements (00)": "compliance/00-microsoft-partner-requirements.md",
    "Technical compliance (01)": "compliance/01-technical-compliance.md",
    "Content compliance (02)": "compliance/02-content-compliance.md",
    "Business/tax compliance (03)": "compliance/03-business-compliance.md",
    "Submission pipeline (04)": "compliance/04-submission-pipeline.md",
    "Marketing assets (05)": "compliance/05-marketing-assets-guide.md",
    "QA guide (06)": "compliance/06-qa-guide.md",
    "Pricing strategy (07)": "compliance/07-pricing-strategy.md",
    "Store certification (08)": "compliance/08-store-certification.md",
    "Certification index": "compliance/INDEX.md",
    "Privacy policy template": "compliance/templates/privacy-policy.md",
    "Terms of use template": "compliance/templates/terms-of-use.md",
    "Age/IARC rating template": "compliance/templates/age-rating-iarc.md",
    "Store listing template": "compliance/templates/store-listing.md",
    "Pre-submission checklist": "compliance/checks/pre_submission_checklist.md",
    "Certification rollout sprints": "compliance/sprints/certification-rollout.md",
    "Code LICENSE": "LICENSE",
}


def scan_ip_blocked(pack_dir: Path) -> list[str]:
    if not pack_dir.exists():
        return []
    hits: list[str] = []
    for f in sorted(pack_dir.iterdir()):
        name = f.name.lower().replace("_", "-")
        for pat in IP_BLOCKED:
            if re.search(pat, name):
                hits.append(f.name)
                break
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Microsoft Store certification readiness check")
    ap.add_argument("--root", default=".")
    ap.add_argument("--pack-dir", default="marketplace-content/dist")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()

    print("=" * 72)
    print(" MICROSOFT STORE CERTIFICATION READINESS")
    print("=" * 72)

    missing = [(label, rel) for label, rel in REQUIRED_ARTIFACTS.items()
               if not (root / rel).exists()]
    art_total = len(REQUIRED_ARTIFACTS)
    art_ok = art_total - len(missing)
    print(f"\n[ARTIFACTS] {art_ok}/{art_total} required compliance docs present")
    for label, rel in missing:
        print(f"   MISSING: {label} -> {rel}")

    hits = scan_ip_blocked(root / args.pack_dir)
    print(f"\n[IP SCAN] {len(hits)} IP-blocked pack names in {args.pack_dir}")
    for h in hits[:20]:
        print(f"   BLOCKED: {h}")

    ip_ok = len(hits) == 0
    readiness = art_ok / art_total * 100
    verdict = "READY" if not missing and ip_ok else "NOT READY"

    print("\n" + "=" * 72)
    print(f" ARTIFACT READINESS: {readiness:.0f}%   IP-CLEAN: {'YES' if ip_ok else 'NO'}")
    if missing:
        print(" ACTION: create the missing artifacts above before submission.")
    if hits:
        print(" ACTION: run `python marketplace-content/scripts/safe-rename.py`")
        print("         then rebuild with `python marketplace-content/scripts/build-all.py`.")
    print(f" VERDICT: {verdict}")
    print("=" * 72)

    out = root / "compliance" / "checks" / "readiness_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "artifact_readiness_pct": round(readiness, 1),
        "missing_artifacts": [r for _, r in missing],
        "ip_blocked_packs": hits,
        "ip_clean": ip_ok,
        "verdict": verdict,
    }, indent=2))
    print(f" Report: {out}")

    return 0 if verdict == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
