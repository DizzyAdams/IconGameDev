#!/usr/bin/env python3
"""Idempotent runnable check for the IP-scan hardening in audit_compliance.py.

Builds synthetic .mcpack packs (clean, IP-hidden-in-description, IP-only-in-
store_description, false-positive guard, and name-based) and asserts that BOTH
copies of audit_compliance.py flag IP hidden in header.description /
store_description while NOT false-flagging the guard.

Run:  python marketplace-content/scripts/verify_ip_scan.py
Exit 0 = hardened correctly, 2 = a check failed.
"""
import importlib.util
import io
import json
import os
import sys
import tempfile
import uuid as uuidlib
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent  # .../IconGameDev
COPY1 = REPO / "marketplace-content" / "scripts" / "audit_compliance.py"
COPY2 = REPO / "marketplace-content" / "marketplace-content" / "scripts" / "audit_compliance.py"
SRC = REPO / "marketplace-content" / "src"


def v4() -> str:
    return str(uuidlib.uuid4())


def make_pack(pack_dir: Path, filename: str, header_desc: str, store_desc: str,
              name: str = "Pack") -> None:
    manifest = {
        "format_version": 2,
        "header": {"name": name, "uuid": v4(), "version": [1, 0, 0],
                   "description": header_desc},
        "modules": [{"type": "skin_pack", "uuid": v4(), "version": [1, 0, 0]}],
        "store_description": store_desc,
    }
    with zipfile.ZipFile(pack_dir / filename, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))


def build_tmp() -> Path:
    d = Path(tempfile.mkdtemp(prefix="ipscan_"))
    # Clean: nothing banned, anywhere.
    make_pack(d, "clean-neon-skins.mcpack",
              "Premium neon 4D-effect skins for your world.",
              "8 neon skins, original artwork, no franchise content.", "Neon Skins")
    # IP hidden ONLY in header.description (name is clean).
    make_pack(d, "cool-battle-pack.mcpack",
              "Anime battle aesthetics inspired look.",
              "Cool combat skins.", "Cool Battle")
    # IP hidden ONLY in store_description (header.description clean).
    make_pack(d, "secret-otaku-pack.mcpack",
              "Cool original skin pack.",
              "Otaku themed collection of characters.", "Secret Pack")
    # False-positive guard: 'manganese' must NOT match r'\bmanga\b'.
    make_pack(d, "manganese-rocks.mcpack",
              "Manganese ore rock textures for mining.",
              "Realistic mineral pack.", "Manganese Rocks")
    # Existing name-based behaviour must still work.
    make_pack(d, "naruto-fan-pack.mcpack",
              "Original ninja skins.",
              "Hand-drawn shinobi pack.", "Naruto Fan")
    return d


def load(path: Path, extra_path=None):
    if extra_path:
        sys.path.insert(0, str(extra_path))
    spec = importlib.util.spec_from_file_location("audit_mod_" + path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_copy1(tmp: Path) -> str:
    mod = load(COPY1)
    buf = io.StringIO()
    with redirect_stdout(buf):
        mod.run_audit(str(tmp), fast=True)
    return buf.getvalue()


def run_copy2(tmp: Path) -> str:
    mod = load(COPY2, extra_path=SRC)  # needs BedrockValidator on path
    buf = io.StringIO()
    with redirect_stdout(buf):
        mod.audit_packs(str(tmp))
    return buf.getvalue()


def check(out: str, label: str) -> None:
    ip_section = out.split("IP violations:")[-1] if "IP violations:" in out else ""
    must_flag = ["cool-battle-pack.mcpack", "secret-otaku-pack.mcpack",
                 "naruto-fan-pack.mcpack"]
    must_not = ["clean-neon-skins.mcpack", "manganese-rocks.mcpack"]
    for f in must_flag:
        assert f in out, f"[{label}] EXPECTED IP flag missing: {f}\n---\n{out}"
    for f in must_not:
        assert f not in ip_section, f"[{label}] FALSE POSITIVE flagged: {f}\n---\n{out}"
    print(f"[{label}] OK: description/store_description IP caught, guard clean.")


def main() -> int:
    assert COPY1.exists(), f"missing {COPY1}"
    assert COPY2.exists(), f"missing {COPY2}"
    tmp = build_tmp()
    try:
        out1 = run_copy1(tmp)
        out2 = run_copy2(tmp)
        check(out1, "copy1 fast")
        check(out2, "copy2")
        print("\nALL CHECKS PASSED — IP scan hardened on both copies.")
        return 0
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
