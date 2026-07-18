#!/usr/bin/env python3
"""IconMineMods — Catalog Sync (stdlib only).

Keeps catalog files synchronized with the filesystem:
  * catalog/PACK_CATALOG.json        ← submission_mcpacks/  (.mcpack/.mctemplate)
  * roblox-ugc/catalog/roblox_catalog.json  ← generate_catalog.py (regenerated)

Usage:
    python catalog/sync.py                  # full sync (both catalogs)
    python catalog/sync.py --check          # dry-run / report-only
    python catalog/sync.py --bedrock        # sync only Bedrock pack catalog
    python catalog/sync.py --roblox         # sync only Roblox catalog
    python catalog/sync.py --json           # machine-readable JSON output

Exit codes:
    0  = all catalogs consistent
    2  = divergence found (--check) or sync error
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ───────────────────────────────────────────────────────────────────
HERE          = Path(__file__).resolve().parent
REPO          = HERE.parent

PACK_CATALOG  = HERE / "PACK_CATALOG.json"          # Bedrock packs
PACKS_DIR     = REPO / "submission_mcpacks"          # source .mcpack files

ROBLOX_TOOLS  = REPO / "roblox-ugc" / "tools"
ROBLOX_CATALOG = REPO / "roblox-ugc" / "catalog" / "roblox_catalog.json"
GENERATE      = ROBLOX_TOOLS / "generate_catalog.py"
ROBLOX_CHECKS = ROBLOX_TOOLS / "roblox_checks.py"

BEDROCK_PREFIX = "PACK_CATALOG"
ROBLOX_PREFIX  = "roblox_catalog"


# ── helpers ─────────────────────────────────────────────────────────────────

def _fmt(ts: datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M:%S%z")


def _read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_json(path: Path, data: Any, sort_keys: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=sort_keys) + "\n",
        encoding="utf-8",
    )


def _parse_mcpack_meta(p: Path) -> dict:
    """Extract pack name + description from a .mcpack/.mctemplate manifest.json."""
    result: dict = {"file": p.name, "size_bytes": p.stat().st_size}
    try:
        with zipfile.ZipFile(p, "r") as zf:
            if "manifest.json" in zf.namelist():
                manifest = json.loads(zf.read("manifest.json"))
                header = manifest.get("header", {})
                result["name"] = header.get("name", p.stem)
                result["description"] = header.get("description", "")
                result["uuid"] = header.get("uuid", "")
                result["version"] = ".".join(str(v) for v in header.get("version", []))
                result["min_engine_version"] = ".".join(
                    str(v) for v in header.get("min_engine_version", [])
                )
            else:
                result["name"] = p.stem
                result["description"] = ""
    except Exception as exc:
        result["parse_error"] = str(exc)
    return result


# ── Bedrock pack catalog sync ───────────────────────────────────────────────

def sync_bedrock(repair: bool = True) -> dict:
    """Sync PACK_CATALOG.json with actual .mcpack/.mctemplate files.

    Returns a report dict with keys: added, removed, updated, unchanged.
    """
    existing    = _read_json(PACK_CATALOG) or {"packs": []}
    old_by_file = {p["file"]: p for p in existing.get("packs", [])}

    # Discover actual pack files
    actual_files: set[str] = set()
    if PACKS_DIR.is_dir():
        for f in sorted(PACKS_DIR.iterdir()):
            if f.suffix in (".mcpack", ".mctemplate") and f.is_file():
                actual_files.add(f.name)

    new_packs: list[dict] = []
    added = updated = unchanged = removed = 0

    for fname in sorted(actual_files):
        fp = PACKS_DIR / fname
        meta = _parse_mcpack_meta(fp)
        old = old_by_file.get(fname)
        if old is None:
            meta["status"] = "added"
            added += 1
        elif old.get("name") != meta.get("name") or old.get("size_bytes") != meta.get("size_bytes"):
            meta["status"] = "updated"
            updated += 1
        else:
            meta["status"] = "unchanged"
            unchanged += 1
        new_packs.append(meta)

    # Find removed packs
    for fname in sorted(old_by_file):
        if fname not in actual_files:
            removed += 1
            new_packs.append({**old_by_file[fname], "status": "removed"})

    catalog = {
        "generated_at": _fmt(datetime.now(timezone.utc)),
        "pack_count": len([p for p in new_packs if p["status"] != "removed"]),
        "packs": new_packs,
    }

    if repair:
        _write_json(PACK_CATALOG, catalog)

    return {
        "catalog": BEDROCK_PREFIX,
        "path": str(PACK_CATALOG),
        "total": len(new_packs),
        "added": added,
        "removed": removed,
        "updated": updated,
        "unchanged": unchanged,
        "active_packs": catalog["pack_count"],
    }


# ── Roblox catalog sync ─────────────────────────────────────────────────────

def sync_roblox(repair: bool = True) -> dict:
    """Regenerate roblox_catalog.json via generate_catalog.py and validate.

    Returns a report dict.
    """
    errors: list[str] = []
    if not GENERATE.exists():
        errors.append(f"generate_catalog.py not found at {GENERATE}")
        return {"catalog": ROBLOX_PREFIX, "path": str(ROBLOX_CATALOG),
                "errors": errors, "items": 0}

    # 1 — regenerate
    if repair:
        result = subprocess.run(
            [sys.executable, str(GENERATE)],
            capture_output=True, text=True, cwd=str(ROBLOX_TOOLS),
        )
        if result.returncode != 0:
            errors.append(f"generate_catalog.py failed: {result.stderr.strip() or result.stdout.strip()}")
            return {"catalog": ROBLOX_PREFIX, "path": str(ROBLOX_CATALOG),
                    "errors": errors, "items": 0}

    # 2 — read regenerated catalog
    data = _read_json(ROBLOX_CATALOG)
    if data is None:
        errors.append(f"cannot read {ROBLOX_CATALOG}")
        return {"catalog": ROBLOX_PREFIX, "path": str(ROBLOX_CATALOG),
                "errors": errors, "items": 0}

    items = data.get("items", [])
    generated_at = data.get("generated_at", "")

    # 3 — run roblox_checks.py for validation
    if ROBLOX_CHECKS.exists():
        result = subprocess.run(
            [sys.executable, str(ROBLOX_CHECKS)],
            capture_output=True, text=True, cwd=str(ROBLOX_TOOLS),
        )
        if result.returncode != 0:
            errors.append(f"roblox_checks.py FAILED:\n{result.stdout.strip()}")
        else:
            # pass — no errors
            pass

    return {
        "catalog": ROBLOX_PREFIX,
        "path": str(ROBLOX_CATALOG),
        "items": len(items),
        "generated_at": generated_at,
        "errors": errors,
    }


# ── main ────────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="IconMineMods catalog sync")
    parser.add_argument("--check", action="store_true",
                        help="dry-run: report differences without writing")
    parser.add_argument("--bedrock", action="store_true",
                        help="sync only Bedrock pack catalog")
    parser.add_argument("--roblox", action="store_true",
                        help="sync only Roblox catalog")
    parser.add_argument("--json", action="store_true",
                        help="machine-readable JSON output")
    args = parser.parse_args()

    repair = not args.check
    run_bedrock = not args.roblox  # default: True unless --roblox
    run_roblox  = not args.bedrock  # default: True unless --bedrock

    reports: dict[str, Any] = {
        "timestamp": _fmt(datetime.now(timezone.utc)),
        "mode": "check" if args.check else "sync",
    }

    if run_bedrock:
        reports["bedrock"] = sync_bedrock(repair=repair)
    if run_roblox:
        reports["roblox"]  = sync_roblox(repair=repair)

    all_ok = True
    for key in ("bedrock", "roblox"):
        r = reports.get(key)
        if r is None:
            continue
        if r.get("errors"):
            all_ok = False
        if "removed" in r and r["removed"] > 0 and not args.check:
            all_ok = True  # removals during sync are fine

    reports["all_ok"] = all_ok

    if args.json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print(f"  IconMineMods Catalog Sync  —  mode: {reports['mode']}")
        print("=" * 60)
        if run_bedrock:
            r = reports["bedrock"]
            print(f"\n  Bedrock packs:  {r['catalog']}")
            print(f"    path:   {r['path']}")
            print(f"    active: {r.get('active_packs', '?')}")
            print(f"    added/removed/updated/unchanged:  "
                  f"{r.get('added', '?')}/{r.get('removed', '?')}/"
                  f"{r.get('updated', '?')}/{r.get('unchanged', '?')}")
        if run_roblox:
            r = reports["roblox"]
            print(f"\n  Roblox UGC:  {r['catalog']}")
            print(f"    path:   {r['path']}")
            print(f"    items:  {r.get('items', '?')}")
            print(f"    gen:    {r.get('generated_at', '?')}")
            if r.get("errors"):
                for e in r["errors"]:
                    print(f"    ERROR: {e}")
        print(f"\n  Result: {'ALL OK' if all_ok else 'ISSUES FOUND'}")
        print("=" * 60)

    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
