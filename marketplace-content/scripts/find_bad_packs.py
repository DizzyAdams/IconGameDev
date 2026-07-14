#!/usr/bin/env python3
"""Find packs that hang or error during the fast-audit operations (zip open +
manifest parse + world_icon PIL open). Reports offenders with a per-pack
timeout so a single bad pack can't stall the scan."""
import io
import json
import queue
import threading
import zipfile
from pathlib import Path

import PIL.Image

ROOT = Path("dist")
EXTS = (".mcpack", ".mctemplate", ".mcworld")
UUID_RE = None  # not needed for hang detection


def check(path: Path):
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        if "manifest.json" not in names:
            return "no manifest"
        m = json.loads(zf.read("manifest.json"))
        if path.suffix == ".mctemplate":
            if "world_icon.png" not in names:
                return "no world_icon"
            img = PIL.Image.open(io.BytesIO(zf.read("world_icon.png")))
            if img.size != (256, 256):
                return f"bad icon size {img.size}"
    return None


def main():
    packs = sorted(p for p in ROOT.iterdir() if p.suffix in EXTS)
    bad = []
    for f in packs:
        q: "queue.Queue" = queue.Queue()
        def run(fp=f):
            try:
                q.put(check(fp))
            except Exception as e:  # noqa: BLE001
                q.put(f"ERR: {e}")
        t = threading.Thread(target=run, daemon=True)
        t.start()
        t.join(2.0)
        if t.is_alive():
            bad.append(("TIMEOUT", f.name))
        else:
            r = q.get() if not q.empty() else None
            if r:
                bad.append((r, f.name))
    print(f"scanned {len(packs)} packs; offenders: {len(bad)}")
    for r, n in bad[:50]:
        print(f"  {r}  {n}")


if __name__ == "__main__":
    main()
