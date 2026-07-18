#!/usr/bin/env python3
"""IconMineMods — Catalog Backup + Sitemap Generator (stdlib only).

Three operations in one script:
  1. BACKUP  — Timestamped backup of catalog files into catalog/backups/
  2. SITEMAP — Generate XML sitemap from catalog data for SEO
  3. CLEANUP — Purge old backups (keeps the N most recent)

Usage:
    python catalog/backup.py                    # backup + sitemap + cleanup
    python catalog/backup.py --backup-only      # backup only
    python catalog/backup.py --sitemap-only     # generate sitemap only
    python catalog/backup.py --cleanup-only     # prune old backups only
    python catalog/backup.py --keep 10          # keep 10 backups (default: 7)
    python catalog/backup.py --json             # machine-readable JSON output

Exit codes:
    0  = success
    2  = error
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ───────────────────────────────────────────────────────────────────
HERE            = Path(__file__).resolve().parent
REPO            = HERE.parent

PACK_CATALOG    = HERE / "PACK_CATALOG.json"
BACKUP_DIR      = HERE / "backups"
SITEMAP_PATH    = HERE / "sitemap.xml"

# Roblox catalog
ROBLOX_CATALOG  = REPO / "roblox-ugc" / "catalog" / "roblox_catalog.json"

# Domain config (for sitemap base URL)
DOMAIN_CONFIG   = REPO / "domains.config.json"

DEFAULT_KEEP    = 7


# ── helpers ─────────────────────────────────────────────────────────────────

def _fmt(ts: datetime | None = None) -> str:
    return (ts or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")


def _read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


# ── backup ──────────────────────────────────────────────────────────────────

def do_backup() -> dict:
    """Copy catalog files to catalog/backups/ with a timestamp prefix.

    Returns a report dict.
    """
    ts = _fmt()
    backup_dir = _ensure_dir(BACKUP_DIR)
    copied: list[dict] = []
    errors: list[str] = []

    sources: list[tuple[Path, str]] = [
        (PACK_CATALOG,   "PACK_CATALOG"),
        (ROBLOX_CATALOG, "roblox_catalog"),
    ]

    for src, label in sources:
        if not src.exists():
            errors.append(f"{label}: source not found at {src}")
            continue
        dest = backup_dir / f"{ts}__{label}{src.suffix}"
        try:
            shutil.copy2(str(src), str(dest))
            copied.append({
                "label": label,
                "source": str(src),
                "dest": str(dest),
                "size_bytes": _file_size(dest),
            })
        except OSError as exc:
            errors.append(f"{label}: copy failed: {exc}")

    return {
        "operation": "backup",
        "timestamp": ts,
        "backup_dir": str(backup_dir),
        "files": copied,
        "errors": errors,
    }


# ── sitemap ─────────────────────────────────────────────────────────────────

def _base_url() -> str:
    """Return the primary domain URL for the sitemap."""
    cfg = _read_json(DOMAIN_CONFIG)
    if cfg:
        primary = cfg.get("primary", "")
        if primary:
            # Ensure https://
            if primary.startswith("http://") or primary.startswith("https://"):
                return primary.rstrip("/")
            return f"https://{primary}"
    return "https://iconminemods.dpdns.org"


def _priority(item_type: str) -> str:
    """Sitemap priority heuristic based on catalog item type."""
    return {
        "classic_shirt": "0.5",
        "classic_pants": "0.5",
        "avatar_accessory": "0.6",
        "game_pass": "0.7",
    }.get(item_type, "0.5")


def _changefreq(item_type: str) -> str:
    """Sitemap change frequency heuristic."""
    return {
        "classic_shirt": "monthly",
        "classic_pants": "monthly",
        "avatar_accessory": "weekly",
        "game_pass": "weekly",
    }.get(item_type, "monthly")


def generate_sitemap() -> dict:
    """Generate a sitemap.xml from catalog data.

    Includes:
      - Static pages (/, /catalog, /roblox, /admin, /afiliados)
      - Roblox catalog items
      - Bedrock pack catalog items
      - API documentation endpoints

    Returns a report dict.
    """
    base = _base_url()
    errors: list[str] = []

    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # ── static pages ────────────────────────────────────────────────────────
    static_pages: list[tuple[str, str, str]] = [
        ("/",                          "1.0", "daily"),
        ("/catalog",                   "0.8", "weekly"),
        ("/roblox",                    "0.8", "weekly"),
        ("/dashboard",                 "0.6", "weekly"),
        ("/admin",                     "0.3", "monthly"),
        ("/afiliados",                 "0.5", "monthly"),
        ("/privacy",                   "0.4", "monthly"),
        ("/submissoes",                "0.5", "weekly"),
    ]

    for path, prio, freq in static_pages:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = base + path
        ET.SubElement(url, "lastmod").text = now_iso
        ET.SubElement(url, "changefreq").text = freq
        ET.SubElement(url, "priority").text = prio

    # ── Roblox catalog items ────────────────────────────────────────────────
    roblox_data = _read_json(ROBLOX_CATALOG)
    roblox_count = 0
    if roblox_data:
        items = roblox_data.get("items", [])
        for item in items:
            item_id = item.get("id")
            item_type = item.get("type", "")
            if item_id is None:
                continue
            url = ET.SubElement(urlset, "url")
            slug = str(item.get("name", f"item-{item_id}")).lower().replace(" ", "-")
            ET.SubElement(url, "loc").text = (
                f"{base}/roblox/item/{item_id}/{slug}"
            )
            ET.SubElement(url, "lastmod").text = now_iso
            ET.SubElement(url, "changefreq").text = _changefreq(item_type)
            ET.SubElement(url, "priority").text = _priority(item_type)
            roblox_count += 1
    else:
        errors.append(f"cannot read {ROBLOX_CATALOG} for sitemap")

    # ── Bedrock pack catalog items ──────────────────────────────────────────
    pack_data = _read_json(PACK_CATALOG)
    pack_count = 0
    if pack_data:
        packs = pack_data.get("packs", [])
        for pack in packs:
            fname = pack.get("file", "")
            if not fname or pack.get("status") == "removed":
                continue
            url = ET.SubElement(urlset, "url")
            slug = Path(fname).stem.lower().replace(" ", "-").replace("_", "-")
            ET.SubElement(url, "loc").text = f"{base}/catalog/pack/{slug}"
            ET.SubElement(url, "lastmod").text = now_iso
            ET.SubElement(url, "changefreq").text = "weekly"
            ET.SubElement(url, "priority").text = "0.6"
            pack_count += 1
    else:
        errors.append(f"cannot read {PACK_CATALOG} for sitemap")

    # ── API endpoints ───────────────────────────────────────────────────────
    api_endpoints = [
        "/api/submissions",
        "/api/catalog",
    ]
    for path in api_endpoints:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = base + path
        ET.SubElement(url, "lastmod").text = now_iso
        ET.SubElement(url, "changefreq").text = "hourly"
        ET.SubElement(url, "priority").text = "0.3"

    # ── serialize ───────────────────────────────────────────────────────────
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    xml_bytes = ET.tostring(urlset, encoding="utf-8", xml_declaration=True)
    SITEMAP_PATH.write_bytes(xml_bytes)

    return {
        "operation": "sitemap",
        "path": str(SITEMAP_PATH),
        "size_bytes": _file_size(SITEMAP_PATH),
        "base_url": base,
        "entries": {
            "static": len(static_pages),
            "roblox_items": roblox_count,
            "bedrock_packs": pack_count,
            "api_endpoints": len(api_endpoints),
            "total": len(static_pages) + roblox_count + pack_count + len(api_endpoints),
        },
        "errors": errors,
    }


# ── cleanup ─────────────────────────────────────────────────────────────────

def do_cleanup(keep: int = DEFAULT_KEEP) -> dict:
    """Remove old backup files, keeping only the `keep` most recent per prefix.

    Returns a report dict.
    """
    backup_dir = BACKUP_DIR
    if not backup_dir.is_dir():
        return {"operation": "cleanup", "deleted": 0, "kept": 0}

    # Group backup files by prefix (PACK_CATALOG or roblox_catalog)
    groups: dict[str, list[Path]] = {}
    for f in sorted(backup_dir.iterdir()):
        if f.is_file():
            # format: <timestamp>__<prefix>.<ext>
            prefix = f.stem.split("__", 1)[-1] if "__" in f.stem else f.stem
            groups.setdefault(prefix, []).append(f)

    deleted_total = 0
    kept_total = 0
    deleted_files: list[str] = []

    for prefix, files in groups.items():
        files.sort()  # oldest first
        if len(files) <= keep:
            kept_total += len(files)
            continue
        to_delete = files[:-keep]
        to_keep   = files[-keep:]
        for f in to_delete:
            try:
                f.unlink()
                deleted_files.append(str(f))
            except OSError:
                pass
        deleted_total += len(to_delete)
        kept_total    += len(to_keep)

    return {
        "operation": "cleanup",
        "keep": keep,
        "deleted": deleted_total,
        "kept": kept_total,
        "deleted_files": deleted_files,
    }


# ── main ────────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="IconMineMods catalog backup + sitemap generator"
    )
    parser.add_argument("--backup-only", action="store_true",
                        help="run backup only")
    parser.add_argument("--sitemap-only", action="store_true",
                        help="generate sitemap only")
    parser.add_argument("--cleanup-only", action="store_true",
                        help="prune old backups only")
    parser.add_argument("--keep", type=int, default=DEFAULT_KEEP,
                        help=f"number of backups to keep (default: {DEFAULT_KEEP})")
    parser.add_argument("--json", action="store_true",
                        help="machine-readable JSON output")
    args = parser.parse_args()

    alone = sum([args.backup_only, args.sitemap_only, args.cleanup_only])

    results: dict[str, Any] = {
        "timestamp": _fmt(),
    }

    if alone == 0:
        # Full: backup → sitemap → cleanup
        results["backup"]  = do_backup()
        results["sitemap"] = generate_sitemap()
        results["cleanup"] = do_cleanup(keep=args.keep)
    elif args.backup_only:
        results["backup"]  = do_backup()
    elif args.sitemap_only:
        results["sitemap"] = generate_sitemap()
    elif args.cleanup_only:
        results["cleanup"] = do_cleanup(keep=args.keep)

    all_ok = True
    for key in ("backup", "sitemap", "cleanup"):
        r = results.get(key)
        if r is None:
            continue
        if r.get("errors"):
            all_ok = False

    results["all_ok"] = all_ok

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("  IconMineMods Catalog Backup + Sitemap")
        print("=" * 60)
        for key in ("backup", "sitemap", "cleanup"):
            r = results.get(key)
            if r is None:
                continue
            op = r.get("operation", key).upper()
            print(f"\n  [{op}]")
            for k, v in r.items():
                if k in ("operation",):
                    continue
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    for entry in v:
                        print(f"    {entry.get('label', entry.get('file', '?'))}: "
                              f"{entry.get('dest', entry.get('path', '?'))}  "
                              f"({entry.get('size_bytes', 0)} bytes)")
                elif isinstance(v, dict):
                    for sk, sv in v.items():
                        print(f"    {sk}: {sv}")
                elif k == "errors" and v:
                    for e in v:
                        print(f"    ERROR: {e}")
                else:
                    print(f"    {k}: {v}")
        print(f"\n  Result: {'ALL OK' if all_ok else 'ISSUES FOUND'}")
        print("=" * 60)

    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
