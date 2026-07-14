#!/usr/bin/env python3
"""Render website-next/data/epic.json from epic/maps.json (single source of truth).

Reproducible + idempotent (stdlib only). Keeps the shape the site's
/api/platform route expects: { brand, platform, status, maps[], stats }.

Usage:
    python epic/render_site_data.py           # write
    python epic/render_site_data.py --check   # verify in sync (exit 1 if not)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "epic" / "maps.json"
DST = ROOT / "website-next" / "data" / "epic.json"


def build() -> dict:
    src = json.loads(SRC.read_text(encoding="utf-8"))
    maps = src.get("maps", [])
    return {
        "brand": "IconMineMods",
        "platform": "Epic Games",
        "status": "em_breve",  # catalog ready; not published until account/KYC done
        "maps": maps,
        "stats": {
            "total_revenue": 0,   # no sales until published
            "published": 0,
            "catalog": len(maps),
        },
    }


def main() -> int:
    data = build()
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    check = "--check" in sys.argv
    if check:
        current = DST.read_text(encoding="utf-8") if DST.exists() else ""
        if current != out:
            print(f"OUT OF SYNC: {DST} differs from epic/maps.json ({data['stats']['catalog']} maps)")
            return 1
        print(f"IN SYNC: {DST} ({data['stats']['catalog']} maps)")
        return 0
    DST.write_text(out, encoding="utf-8")
    print(f"WROTE {DST} ({data['stats']['catalog']} maps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
