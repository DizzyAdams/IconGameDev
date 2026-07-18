#!/usr/bin/env python3
"""Clone the IconHub experience kit into a new themed Roblox experience.

Copies experiences/IconHub/ to experiences/<name>/, replacing "IconHub" with
the theme name and "Surreal" with the theme's item prefix (in file contents
AND file names). Stdlib only, idempotent (existing target dir is left
untouched unless --force).

Usage:
    python make_experience.py --name NeonRacing --theme neon_racing
    python make_experience.py --name NeonRacing --theme neon_racing --force
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIENCES = HERE.parent / "experiences"
SOURCE = EXPERIENCES / "IconHub"
THEMES_FILE = EXPERIENCES / "themes.json"


def load_theme(theme_id: str) -> dict:
    themes = json.loads(THEMES_FILE.read_text(encoding="utf-8"))
    for t in themes:
        if t["id"] == theme_id or t["name"] == theme_id:
            return t
    raise SystemExit(f"unknown theme {theme_id!r}; known: {[t['id'] for t in themes]}")


def make_experience(name: str, theme_id: str, force: bool = False) -> Path:
    theme = load_theme(theme_id)
    if theme["name"] != name:
        print(f"note: theme {theme_id!r} is named {theme['name']!r}; using --name {name!r}")
    dest = EXPERIENCES / name
    if dest.exists():
        if not force:
            print(f"skip: {dest} already exists (use --force to rebuild)")
            return dest
        shutil.rmtree(dest)

    prefix = theme["item_prefix"]
    for src_path in sorted(SOURCE.rglob("*")):
        if src_path.is_dir():
            continue
        rel = src_path.relative_to(SOURCE)
        # Rename path parts containing Surreal / IconHub.
        new_parts = [p.replace("Surreal", prefix).replace("IconHub", name) for p in rel.parts]
        out_path = dest.joinpath(*new_parts)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        data = src_path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            out_path.write_bytes(data)
            continue
        text = text.replace("IconHub", name).replace("Surreal", prefix)
        out_path.write_text(text, encoding="utf-8")

    # Stamp theme metadata.
    (dest / "theme.json").write_text(json.dumps(theme, indent=2) + "\n", encoding="utf-8")
    print(f"created: {dest}")
    return dest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Clone IconHub into a themed experience")
    ap.add_argument("--name", required=True)
    ap.add_argument("--theme", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    make_experience(args.name, args.theme, args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
