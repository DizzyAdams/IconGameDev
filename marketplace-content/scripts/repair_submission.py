#!/usr/bin/env python3
"""Repair submission_mcpacks in-place so audit_compliance.py reports CLEAN.

Reuses repair_dist.repair_pack (single source of truth for the zip-rewrite +
valid v4 UUID logic) over submission_mcpacks instead of dist/. Idempotent;
progress is persisted to submission_mcpacks/.repair_state.json and the taken-UUID
set is seeded from dist/ so repaired UUIDs stay globally unique.

Usage:
  python scripts/repair_submission.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from repair_dist import repair_pack, EXTS  # reuse the proven repair logic

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "submission_mcpacks"
STATE = SRC / ".repair_state.json"
TAKEN = SRC / ".uuid_taken.json"
TAKEN_DIST = ROOT / "marketplace-content" / "dist" / ".uuid_taken.json"


def load_set(p: Path) -> set:
    if p.exists():
        try:
            return set(json.loads(p.read_text()).get("items", []))
        except Exception:
            return set()
    return set()


def save_set(p: Path, s: set) -> None:
    p.write_text(json.dumps({"items": sorted(s)}, indent=2))


def main() -> int:
    if not SRC.is_dir():
        print("submission_mcpacks not found")
        return 2
    packs = sorted(x for x in SRC.iterdir() if x.suffix in EXTS)
    done = load_set(STATE)
    # Seed taken UUIDs from dist/ so repaired IDs stay globally unique.
    taken = load_set(TAKEN) | load_set(TAKEN_DIST)
    todo = [p for p in packs if p.name not in done]

    fixed = errs = 0
    for p in todo:
        try:
            was, _ = repair_pack(p, taken)
            if was:
                fixed += 1
        except Exception as e:  # noqa: BLE001 - report and keep going
            errs += 1
            print(f"ERROR {p.name}: {e}")
            continue
        done.add(p.name)
    save_set(STATE, done)
    save_set(TAKEN, taken)
    print(f"scanned={len(todo)} fixed={fixed} errors={errs} total_packs={len(packs)}")
    return 0 if errs == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
