from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


MC_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MC_DIR))


MAP_DIR = MC_DIR / "descriptions"


def fx(pack_dir: str) -> tuple[str, str, str, list[str]]:
    desc_path = None
    for rel in ("description_en.txt", "description.txt", "description_pt.txt"):
        p = MAP_DIR / pack_dir / rel
        if p.exists():
            desc_path = p
            break
    if desc_path is None:
        return pack_dir, pack_dir.replace("-", " ").title(), "", []
    text = desc_path.read_text(encoding="utf-8", errors="ignore")
    title = re.sub(r"§[0-9a-fk-or]", "", text.split("\n", 1)[0]).strip() or pack_dir.replace("-", " ").title()
    body = re.sub(r"§[0-9a-fk-or]", "", text)
    body = re.sub(r"© .*$", "", body, flags=re.MULTILINE)
    body = "\n".join(line.strip() for line in body.split("\n") if line.strip())
    short = " ".join(body.split())[:120]
    tags = [
        pack_dir,
        "minecraft bedrock",
        "bedrock edition",
        "minecraft pack",
        f"{pack_dir.split('-')[0]} pack" if pack_dir else "pack",
    ]
    return pack_dir, title, short, tags[:6]


def run(pack_dir: str, out_dir: str | None = None):
    out = Path(out_dir or str(MC_DIR / "out"))
    out.mkdir(parents=True, exist_ok=True)
    slug, title, short, tags = fx(pack_dir)
    title_h = " ".join(w.capitalize() for w in slug.split("-"))
    preview = {
        "pack_dir": slug,
        "title": title,
        "title_human": title_h,
        "store_title": short or title,
        "tags": tags,
        "payload": {
            "title": f"{title} | Bedrock Minemods",
            "description": short or title,
            "tags": tags,
            "h1": title_h,
        },
    }
    per = out / f"seo_preview_{slug}.json"
    per.write_text(json.dumps(preview, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(per))
    return preview


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", required=True)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    run(args.pack_dir, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
