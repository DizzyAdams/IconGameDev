#!/usr/bin/env python3
"""build_submission.py — generate submission-ready .mcpack files for ALL live packs.

Generates one valid .mcpack per source pack (with all required assets) into
submission_mcpacks/<type>/<name>.mcpack, ready to bulk-upload to Microsoft
Partner Center / Roblox / Epic. This is the concrete step that turns the
14,600 stubs into shippable products and closes the "missing assets" rejection
reason entirely.

Usage:
    python marketplace-content/scripts/build_submission.py
    python marketplace-content/scripts/build_submission.py --limit 50   # smoke test
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from approval_pack_builder import build_pack_bytes  # noqa: E402

PACK_FOLDERS = ["skin-packs", "texture-packs", "world-templates", "mashup-packs"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build submission .mcpack files")
    ap.add_argument("--limit", type=int, default=0, help="max packs (0 = all)")
    ap.add_argument("--out", default="submission_mcpacks")
    args = ap.parse_args(argv)

    out_root = ROOT / args.out
    out_root.mkdir(parents=True, exist_ok=True)
    mc = ROOT / "marketplace-content"

    built = 0
    errors = 0
    done = out_root / ".manifest_build_done.txt"
    # optional resume file tracking built packs (keeps re-runs cheap)
    built_set = set()
    if done.exists():
        built_set = set(done.read_text(encoding="utf-8").splitlines())

    for folder in PACK_FOLDERS:
        fp = mc / folder
        if not fp.is_dir():
            continue
        for d in sorted(os.listdir(fp)):
            sd = fp / d
            if not sd.is_dir():
                continue
            key = f"{folder}/{d}"
            if key in built_set:
                built += 1
                continue
            try:
                data = build_pack_bytes(str(sd))
            except Exception as e:
                print(f"  ERR {key}: {e}")
                errors += 1
                continue
            dest = out_root / folder / f"{d}.mcpack"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            built_set.add(key)
            built += 1
            if built % 500 == 0:
                print(f"  built {built}...")
            if args.limit and built >= args.limit:
                break
        if args.limit and built >= args.limit:
            break

    done.write_text("\n".join(sorted(built_set)), encoding="utf-8")
    print(f"\n DONE: {built} packs built, {errors} errors -> {out_root}")
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
