#!/usr/bin/env python3
"""Repair SOURCE pack directories so `build-all.py` reproduces a CLEAN dist/.

Mirrors scripts/repair_dist.py but operates on the un-zipped source folders
(skin-packs, texture-packs, world-templates, mashup-packs):
  * world templates: ensure level.dat (minimal valid NBT) + world_icon.png
    (256x256) exist alongside manifest.json.
  * every manifest: ensure header + module UUIDs are valid v4 AND globally
    unique (fixes collisions and malformed UUIDs at the source of truth).

Chunked (REPAIR_BATCH env var, default 2000) with persisted state so it can be
driven across invocations. Stdlib + Pillow only.
"""
from __future__ import annotations

import io
import json
import os
import re
import uuid
import zlib
from pathlib import Path

import PIL.Image
import PIL.ImageDraw

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / ".source_repair_state.json"
TAKEN = ROOT / ".source_uuid_taken.json"
SOURCE_DIRS = ["skin-packs", "texture-packs", "world-templates", "mashup-packs"]

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I
)


def make_level_dat() -> bytes:
    return zlib.compress(b"\x0a\x00\x00")


def make_world_icon(seed: int) -> bytes:
    import random

    rng = random.Random(seed)
    sz = 256
    img = PIL.Image.new(
        "RGBA", (sz, sz),
        (rng.randint(40, 120), rng.randint(40, 120), rng.randint(120, 200), 255),
    )
    d = PIL.ImageDraw.Draw(img)
    cx, cy = sz // 2, sz // 2
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70],
              fill=(rng.randint(120, 220), rng.randint(80, 160), rng.randint(80, 160), 255))
    d.rectangle([cx - 50, cy - 10, cx + 50, cy + 50], fill=(139, 90, 43, 255))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def new_uuid(taken: set) -> str:
    while True:
        u = str(uuid.uuid4())
        if u not in taken:
            taken.add(u)
            return u


def load_json_set(path: Path) -> set:
    if path.exists():
        try:
            return set(json.loads(path.read_text()).get("items", []))
        except Exception:
            return set()
    return set()


def save_json_set(path: Path, items: set) -> None:
    path.write_text(json.dumps({"items": sorted(items)}, indent=2))


def repair_dir(d: Path, taken: set):
    """Returns (fixed, error). Adds missing world-template assets and rewrites
    manifest UUIDs in place."""
    mf = d / "manifest.json"
    if not mf.exists():
        return False, "no manifest.json"
    m = json.loads(mf.read_text(encoding="utf-8"))
    local_taken = set()
    changed = False

    def slot(val):
        nonlocal changed
        cur = str(val) if val is not None else ""
        if cur and UUID_RE.match(cur) and cur.lower() not in taken \
                and cur.lower() not in local_taken:
            taken.add(cur.lower())
            local_taken.add(cur.lower())
            return cur
        nu = new_uuid(taken)
        local_taken.add(nu.lower())
        changed = True
        return nu

    header = m.setdefault("header", {})
    header["uuid"] = slot(header.get("uuid"))
    for mod in m.get("modules", []):
        mod["uuid"] = slot(mod.get("uuid"))

    need_level = (d.parent.name == "world-templates") and not (d / "level.dat").exists()
    need_icon = (d.parent.name == "world-templates") and not (d / "world_icon.png").exists()

    if not (changed or need_level or need_icon):
        return False, None

    if need_level:
        (d / "level.dat").write_bytes(make_level_dat())
    if need_icon:
        (d / "world_icon.png").write_bytes(make_world_icon(hash(d.name) & 0xFFFFFFFF))
    if changed:
        mf.write_text(json.dumps(m, indent=2), encoding="utf-8")
    return True, None


def main() -> int:
    dirs = []
    for sd in SOURCE_DIRS:
        src = ROOT / sd
        if src.exists():
            dirs.extend(sorted(p for p in src.iterdir()
                               if p.is_dir() and not p.name.startswith(".")))
    if not dirs:
        print("no source dirs found")
        return 2

    done = load_json_set(STATE)
    taken = load_json_set(TAKEN)
    todo = [d for d in dirs if d.name not in done]

    batch = int(os.environ.get("REPAIR_BATCH", "2000"))
    chunk = todo[:batch]

    fixed = 0
    errors = 0
    for d in chunk:
        try:
            was_fixed, err = repair_dir(d, taken)
            if was_fixed:
                fixed += 1
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"ERROR {d}: {e}")
            continue
        done.add(d.name)

    save_json_set(STATE, done)
    save_json_set(TAKEN, taken)
    print(f"chunk={len(chunk)} repaired_this_run={fixed} errors={errors} "
          f"total_done={len(done)}/{len(dirs)} remaining={len(dirs)-len(done)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
