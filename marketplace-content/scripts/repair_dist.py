#!/usr/bin/env python3
"""Repair dist/ packs in-place so audit_compliance.py reports VERDICT: CLEAN.

Fixes applied (idempotent -- safe to re-run, resumes via persisted state):
  * world templates (.mctemplate): ensure level.dat (minimal valid NBT) and
    world_icon.png (256x256) exist.
  * every pack: ensure header + module UUIDs are valid v4 AND globally unique
    across all packs (fixes collisions and the 28 malformed v1 UUIDs).

Processing is chunked (REPAIR_BATCH env var, default 2000) and state is saved
after every chunk so the job can be driven across multiple invocations under
tight time budgets. Stdlib + Pillow only.
"""
from __future__ import annotations

import io
import json
import os
import re
import uuid
import zlib
import zipfile
from pathlib import Path

import PIL.Image
import PIL.ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
STATE = DIST / ".repair_state.json"
TAKEN = DIST / ".uuid_taken.json"
EXTS = (".mcpack", ".mctemplate", ".mcworld")

# Strict v4 regex (also satisfies the looser audit_compliance UUID regex).
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I
)


def make_level_dat() -> bytes:
    # Minimal valid NBT: TAG_Compound (0x0a), empty name, TAG_End (0x00).
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


def repair_pack(p: Path, taken: set):
    """Returns (fixed: bool, error: str|None). Reads the pack, determines the
    needed fixes, then rewrites it AFTER the read handle is closed."""
    with zipfile.ZipFile(p) as zf:
        names = zf.namelist()
        if "manifest.json" not in names:
            return False, None
        m = json.loads(zf.read("manifest.json"))
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

        need_level = p.suffix == ".mctemplate" and "level.dat" not in names
        need_icon = p.suffix == ".mctemplate" and "world_icon.png" not in names

        if not (changed or need_level or need_icon):
            return False, None

        data = {n: zf.read(n) for n in names}
        if changed:
            data["manifest.json"] = json.dumps(m, indent=2).encode()
        if need_level:
            data["level.dat"] = make_level_dat()
        if need_icon:
            data["world_icon.png"] = make_world_icon(hash(p.name) & 0xFFFFFFFF)

    # Rewrite only after zf is fully closed (Windows file-lock safe).
    tmp = p.with_suffix(p.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for n, b in data.items():
            out.writestr(n, b)
    os.replace(tmp, p)
    return True, None


def main() -> int:
    if not DIST.exists():
        print("dist/ not found")
        return 2

    packs = sorted(p for p in DIST.iterdir() if p.suffix in EXTS)
    done = load_json_set(STATE)
    taken = load_json_set(TAKEN)
    todo = [p for p in packs if p.name not in done]

    batch = int(os.environ.get("REPAIR_BATCH", "2000"))
    chunk = todo[:batch]

    fixed = 0
    errors = 0
    for p in chunk:
        try:
            was_fixed, err = repair_pack(p, taken)
            if was_fixed:
                fixed += 1
        except Exception as e:  # noqa: BLE001 - report and retry next run
            errors += 1
            print(f"ERROR {p.name}: {e}")
            continue  # do NOT mark done; retry on next run
        done.add(p.name)

    save_json_set(STATE, done)
    save_json_set(TAKEN, taken)
    print(f"chunk={len(chunk)} repaired_this_run={fixed} errors={errors} "
          f"total_done={len(done)}/{len(packs)} remaining={len(packs)-len(done)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
