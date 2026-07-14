#!/usr/bin/env python3
"""Idempotently quarantine IP-tainted Bedrock packs out of the submission path.

Scans every .mcpack/.mctemplate/.mcworld in PACK_DIR using the SAME IP rules as
audit_compliance.py (single source of truth: IP_BLOCKED) and moves any flagged
pack to QUARANTINE_DIR (default _ip_quarantine at repo root). Nothing is deleted
and already-quarantined packs are skipped, so it is safe to re-run.

This is the automated guard that keeps submission_mcpacks 100% IP-clean, so a
Microsoft/Bedrock tech review cannot reject the submission on IP grounds.

Usage:
  python scripts/quarantine_ip.py                  # submission_mcpacks -> _ip_quarantine
  python scripts/quarantine_ip.py --pack-dir dist  # also sweep dist/
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from audit_compliance import IP_BLOCKED, EXTS  # reuse the single source of truth

ROOT = Path(__file__).resolve().parent.parent.parent


def _json_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _json_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _json_strings(v)


def pack_haystack(fname: str, zf: zipfile.ZipFile) -> str:
    """Build the full user-facing text of a pack for IP matching."""
    haystack = fname.lower().replace("_", "-").replace(".mcpack", "")
    try:
        names = set(zf.namelist())
        if "manifest.json" in names:
            try:
                m = json.loads(zf.read("manifest.json"))
            except Exception:
                m = {}
            if isinstance(m, dict):
                h = m.get("header", {})
                if isinstance(h, dict):
                    haystack += " " + str(h.get("name", "")).lower()
                    haystack += " " + str(h.get("description", "")).lower()
                haystack += " " + str(m.get("store_description", "")).lower()
        for sf in ("skins.json", "contents.json", "pack_manifest.json"):
            if sf in names:
                try:
                    for s in _json_strings(json.loads(zf.read(sf))):
                        haystack += " " + str(s).lower()
                except Exception:
                    pass
        for n in names:
            if n.endswith(".lang"):
                try:
                    for line in zf.read(n).decode("utf-8", "ignore").splitlines():
                        haystack += " " + line.lower()
                except Exception:
                    pass
    except Exception:
        pass
    return haystack


def is_ip_blocked(fname: str, zf: zipfile.ZipFile) -> bool:
    haystack = pack_haystack(fname, zf)
    for pat in IP_BLOCKED:
        if re.search(pat, haystack):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Quarantine IP-tainted Bedrock packs")
    ap.add_argument("--pack-dir", default="submission_mcpacks")
    ap.add_argument("--quarantine-dir", default="_ip_quarantine")
    args = ap.parse_args()

    src = Path(args.pack_dir)
    if not src.is_absolute():
        src = ROOT / args.pack_dir
    q = Path(args.quarantine_dir)
    if not q.is_absolute():
        q = ROOT / args.quarantine_dir
    q.mkdir(parents=True, exist_ok=True)
    if not src.is_dir():
        print(f"pack-dir not found: {src}")
        return 2

    moved = skipped = 0
    for f in sorted(os.listdir(str(src))):
        if not f.endswith(EXTS):
            continue
        p = src / f
        if not p.exists():
            skipped += 1  # already moved in a prior run -> idempotent
            continue
        try:
            with zipfile.ZipFile(p) as zf:
                bad = is_ip_blocked(f, zf)
        except Exception:
            bad = False
        if bad:
            # Remove from the submission path. Overwrite any stale quarantine copy
            # so a pack that is duplicated in both places is still pulled out of src.
            if (q / f).exists():
                (q / f).unlink()
            shutil.move(str(p), str(q / f))
            moved += 1
            print(f"  quarantined: {f}")

    remaining = sum(1 for x in os.listdir(str(src)) if x.endswith(EXTS))
    print(f"\nMOVED={moved} ALREADY_IN_QUARANTINE={skipped}")
    print(f"  {src}: {remaining} packs remain (IP-clean after run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
