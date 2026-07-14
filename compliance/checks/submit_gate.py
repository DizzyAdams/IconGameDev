#!/usr/bin/env python3
"""Submission gate for Minecraft Bedrock Marketplace (Microsoft Partner Center).

Single go/no-go for first-try approval. Runs the fast, reliable gates and
(optionally) the heavier structural audit.

Fast gates (always):
  1. safe-rename.py            -> ensure no franchise names in sources (idempotent)
  2. certification_readiness.py -> 17/17 artifacts + IP scan on dist/

Heavy gate (--audit):
  3. audit_compliance.py       -> structural + UUID v4 + IP scan (slow on large dist/)

Usage:
    python compliance/checks/submit_gate.py
    python compliance/checks/submit_gate.py --audit
Exit code 0 = GO (safe to submit); 2 = NO-GO.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MC = ROOT / "marketplace-content"


def _run(label: str, cmd: list[str], cwd: Path):
    print(f"\n--- {label} ---")
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True,
                               text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("  (timed out — run this step separately on large dist/)")
        return 2, ""
    except FileNotFoundError as e:
        return 2, f"missing: {e}"
    out = (proc.stdout or "") + (proc.stderr or "")
    print("\n".join(out.strip().splitlines()[-12:]))
    return proc.returncode, out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Minecraft Bedrock submission gate")
    ap.add_argument("--pack-dir", default="marketplace-content/dist")
    ap.add_argument("--audit", action="store_true",
                    help="also run the heavy structural audit (slow on large dist/)")
    args = ap.parse_args(argv)

    print("=" * 72)
    print(" MINECRAFT BEDROCK — SUBMISSION GATE (first-try enforcement)")
    print("=" * 72)

    _run("1/3 safe-rename (idempotent)",
         [sys.executable, "scripts/safe-rename.py"], MC)

    rc3, out3 = _run("2/3 certification_readiness",
                     [sys.executable, "compliance/checks/certification_readiness.py",
                      "--pack-dir", args.pack_dir], ROOT)
    ready = "VERDICT: READY" in out3

    clean = True
    if args.audit:
        # Resolve the pack dir to an absolute path at the repo root so the audit
        # scans the REAL directory (e.g. submission_mcpacks lives at the repo root,
        # not under marketplace-content/). audit_compliance accepts absolute paths.
        mc_abs = Path(args.pack_dir)
        if not mc_abs.is_absolute():
            mc_abs = ROOT / args.pack_dir
        # Use --fast (lightweight structural + UUID + IP checks) so the gate is
        # achievable on large dist/ folders; thorough mode is available via
        # `python marketplace-content/scripts/audit_compliance.py --pack-dir dist`.
        rc2, out2 = _run("3/3 audit_compliance (dist)",
                         [sys.executable, "scripts/audit_compliance.py",
                          "--pack-dir", str(mc_abs.resolve()), "--fast"], MC)
        clean = "VERDICT: CLEAN" in out2

    print("\n" + "=" * 72)
    print(f" readiness READY : {'YES' if ready else 'NO'}")
    if args.audit:
        print(f" audit CLEAN     : {'YES' if clean else 'NO'}")
    go = ready and (not args.audit or clean)
    print(f" VERDICT: {'GO - safe to submit' if go else 'NO-GO - fix issues above'}")
    print("=" * 72)
    return 0 if go else 2


if __name__ == "__main__":
    raise SystemExit(main())
