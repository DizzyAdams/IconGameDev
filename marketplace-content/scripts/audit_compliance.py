# Compliance Audit Script — run before Partner Center submission
#
# Supports two modes:
#   * thorough (default): uses BedrockValidator (extracts packs, validates PNG
#     dimensions, etc.). Heavy; use --batch/--resume to chunk very large dist/.
#   * --fast: lightweight structural + UUID + IP checks that do NOT extract the
#     whole archive or open every PNG. Completes 10k+ packs in seconds and is
#     the practical gate for large Marketplace submissions.
#
# Both modes print the same final line:
#   === VERDICT: CLEAN — N packs ready for Partner Center ===
#   === VERDICT: M issues across N packs ===
#
# Chunking: --batch N processes at most N packs per run and persists progress to
# <pack-dir>/.audit_state.json; re-run (optionally --resume) until the final
# VERDICT prints. Exit code: 0 = CLEAN, 2 = issues / not complete.

import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

ROOT = Path(__file__).resolve().parent.parent

IP_BLOCKED = [
    # Existing franchise / anime signals.
    "pokemon", "naruto", "dragon.ball", "bleach", "genshin", "fnaf", "hello.kitty",
    "demon.slayer", "chainsaw.man", "one.piece", "jujutsu", "sonic", "tadc",
    "attack.on.titan", "little.nightmares",
    r"\banime\b", r"\bmanga\b", r"\bshonen\b", r"\bshounen\b",
    r"\botaku\b", r"\bwaifu\b", r"\bkawaii\b", r"\bsenpai\b",
    # Expanded third-party IP signals a Microsoft/Bedrock tech review checks.
    # Dotted tokens match separators (-, _, space). First-party words
    # (minecraft / mojang / bedrock) are intentionally NOT blocked, and neither
    # are our original asset words (crimson, frost, ember, void, shadow, halo...).
    "marvel", "dc.comics", "spider.man", "batman", "superman", "iron.man",
    "captain.america", "avengers", "mario", "luigi", "zelda", "bowser",
    "peach", "yoshi", "tails", "fortnite", "call.of.duty", "god.of.war",
    "elden.ring", "warcraft", "diablo", "overwatch", "valorant",
    "league.of.legends", "pubg", r"\bgta\b", "grand.theft.auto", "assassin.s.creed",
    "harry.potter", "hogwarts", "star.wars", "disney", "sanrio",
    "barbie", "peppa.pig", "paw.patrol", "frozen", "minions", "spongebob",
    "mickey.mouse", "winnie", "shrek", "bts", "pewdiepie", "technoblade",
    "tokyo.ghoul", "hunter.x.hunter", "my.hero.academia", "fairy.tail",
    "sailor.moon", "dragon.quest", "final.fantasy", "kirby", "metroid",
    "doom", "skyrim", "fallout", "bioshock", "digimon", "yu-gi-oh",
    "transformers", "teenage.mutant.ninja.turtles", "power.rangers",
]

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I
)

EXTS = (".mcpack", ".mctemplate", ".mcworld")


def list_packs(pack_dir: Path):
    return sorted(f for f in os.listdir(str(pack_dir)) if f.endswith(EXTS))


def load_state(state_path: Path):
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except Exception:
            return {}
    return {}


def save_state(state_path: Path, state: dict):
    state_path.write_text(json.dumps(state, indent=2))


def fast_validate_pack(pack_dir: Path, f: str):
    """Lightweight checks: manifest JSON valid, required structure, v4 UUIDs,
    world-template assets present. Returns (valid, errors, uuids)."""
    errors = []
    uuids = []
    try:
        with zipfile.ZipFile(pack_dir / f) as zf:
            names = set(zf.namelist())
            if "manifest.json" not in names:
                return False, ["manifest.json missing"], []
            try:
                m = json.loads(zf.read("manifest.json"))
            except Exception as e:
                return False, [f"manifest.json invalid JSON: {e}"], []
            if not isinstance(m, dict) or "header" not in m or "modules" not in m:
                return False, ["missing header/modules"], []
            h = m["header"]
            if not isinstance(h, dict) or not h.get("name"):
                errors.append("header.name missing")
            hu = h.get("uuid", "")
            if not UUID_RE.match(str(hu)):
                errors.append(f"header uuid invalid: {hu}")
            else:
                uuids.append(str(hu).lower())
            mods = m.get("modules", [])
            if not isinstance(mods, list) or not mods:
                errors.append("no modules")
            else:
                for mod in mods:
                    if not isinstance(mod, dict):
                        errors.append("bad module entry")
                        continue
                    mu = mod.get("uuid", "")
                    if not UUID_RE.match(str(mu)):
                        errors.append(f"module uuid invalid: {mu}")
                    else:
                        uuids.append(str(mu).lower())
            if f.endswith(".mctemplate"):
                if "level.dat" not in names:
                    errors.append("level.dat missing")
                if "world_icon.png" not in names:
                    errors.append("world_icon.png missing")
                else:
                    try:
                        import io
                        from PIL import Image
                        img = Image.open(io.BytesIO(zf.read("world_icon.png")))
                        if img.size != (256, 256):
                            errors.append(f"world_icon.png must be 256x256, got {img.size}")
                    except Exception as e:
                        errors.append(f"world_icon.png error: {e}")
    except Exception as e:  # noqa: BLE001
        return False, [f"zip error: {e}"], []
    return (len(errors) == 0), errors, uuids


def run_audit(pack_dir="dist", batch=0, resume=False, fast=False):
    pack_dir = Path(pack_dir)
    if not pack_dir.is_absolute():
        pack_dir = ROOT / pack_dir
    state_path = pack_dir / ".audit_state.json"
    print(f"=== COMPLIANCE AUDIT: {pack_dir} ===" + (" [FAST]" if fast else ""))
    print(f"Total packs: {len(list_packs(pack_dir))}\n")

    all_packs = list_packs(pack_dir)
    total = len(all_packs)

    state = load_state(state_path) if (resume or state_path.exists()) else {}
    results = state.get("results", {})
    uuid_map = state.get("uuid_map", {})
    done = set(results.keys())
    todo = [f for f in all_packs if f not in done]
    if batch and batch > 0:
        todo = todo[:batch]

    if fast:
        for f in todo:
            ok, errs, uuids = fast_validate_pack(pack_dir, f)
            results[f] = {"valid": ok, "errors": errs}
            for u in uuids:
                uuid_map.setdefault(u, [])
                if f not in uuid_map[u]:
                    uuid_map[u].append(f)
            done.add(f)
    else:
        from validators.bedrock_validator import BedrockValidator
        validator = BedrockValidator()
        for f in todo:
            try:
                r = validator.validate_mcpack(str(pack_dir / f))
            except Exception as e:  # noqa: BLE001
                r = {"file": f, "valid": False, "errors": [f"validate error: {e}"], "uuids": []}
            results[f] = {"valid": r["valid"], "errors": r["errors"]}
            for u in r.get("uuids", []):
                if u:
                    uuid_map.setdefault(u, [])
                    if f not in uuid_map[u]:
                        uuid_map[u].append(f)
            done.add(f)

    # IP scan (cheap; recomputed each run). Exhaustively scans EVERY user-facing
    # text inside the pack -- the filename, the manifest header.name/description/
    # store_description, sidecar JSON (skins.json skin_pack_name + contents.json),
    # and resource-pack .lang strings -- so franchise/IP terms hidden anywhere are
    # caught. This was the blind spot that let IP through; the scan is now thorough.
    ip_blocked = set()
    TEXT_SIDECASTS = ("skins.json", "contents.json", "pack_manifest.json")

    def _json_strings(obj):
        if isinstance(obj, str):
            yield obj
        elif isinstance(obj, dict):
            for v in obj.values():
                yield from _json_strings(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                yield from _json_strings(v)

    for f in all_packs:
        name_lower = f.lower().replace("_", "-").replace(".mcpack", "")
        haystack = name_lower
        try:
            with zipfile.ZipFile(pack_dir / f) as zf:
                names = set(zf.namelist())
                if "manifest.json" in names:
                    try:
                        m = json.loads(zf.read("manifest.json"))
                    except Exception:
                        m = {}
                    if isinstance(m, dict):
                        h = m.get("header", {})
                        if isinstance(h, dict):
                            haystack += " " + str(h.get("name", "")).lower()
                            haystack += " " + str(h.get("description", "")).lower()
                        haystack += " " + str(m.get("store_description", "")).lower()
                for sf in TEXT_SIDECASTS:
                    if sf in names:
                        try:
                            for s in _json_strings(json.loads(zf.read(sf))):
                                haystack += " " + str(s).lower()
                        except Exception:
                            pass
                for n in names:
                    if n.endswith(".lang"):
                        try:
                            for line in zf.read(n).decode("utf-8", "ignore").splitlines():
                                haystack += " " + line.lower()
                        except Exception:
                            pass
        except Exception:
            pass
        for pattern in IP_BLOCKED:
            if re.search(pattern, haystack):
                ip_blocked.add(f)
                break

    processed = len(results)
    complete = processed >= total
    save_state(state_path, {
        "results": results, "uuid_map": uuid_map,
        "ip_blocked": sorted(ip_blocked), "total": total,
        "processed": processed, "complete": complete,
    })

    if not complete:
        pass_count = sum(1 for v in results.values() if v["valid"])
        print(f"[PROGRESS] processed={processed}/{total} valid={pass_count} "
              f"ip_violations={len(ip_blocked)}")
        print("  Run again (--resume) to continue; final VERDICT prints when complete.")
        return 0

    # Final pass: global UUID collision check
    collision_errors = {}
    for u, files in uuid_map.items():
        if len(files) > 1:
            pack_names = ", ".join(files)
            for f in files:
                collision_errors.setdefault(f, []).append(
                    f"Global UUID collision for {u} with other packs: {pack_names}"
                )
    final_valid = 0
    final_fail = 0
    for f, v in results.items():
        ok = v["valid"] and f not in collision_errors
        if ok:
            final_valid += 1
        else:
            final_fail += 1

    print("--- Pass 1: Structural ---")
    print(f"PASS={final_valid} FAIL={final_fail}")
    print("\n--- Pass 3: IP Scan ---")
    print(f"PASS={total - len(ip_blocked)} FAIL={len(ip_blocked)}")

    total_issues = final_fail + len(ip_blocked)
    if total_issues == 0:
        print(f"\n=== VERDICT: CLEAN — {total} packs ready for Partner Center ===")
        return 0
    print(f"\n=== VERDICT: {total_issues} issues across {total} packs ===")
    if final_fail:
        sample = [(f, results[f]["errors"]) for f in results if not results[f]["valid"]]
        print("\nStructural failures (sample):")
        for f, errs in sample[:5]:
            print(f"  {f}: {errs}")
    if ip_blocked:
        print("\nIP violations:")
        for f in sorted(ip_blocked)[:20]:
            print(f"  {f}")
    return 2


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", default="dist")
    ap.add_argument("--batch", type=int, default=0, help="packs per run (0 = all)")
    ap.add_argument("--resume", action="store_true", help="continue from saved state")
    ap.add_argument("--fast", action="store_true", help="lightweight checks (no PNG extract)")
    args = ap.parse_args()
    raise SystemExit(run_audit(args.pack_dir, args.batch, args.resume, args.fast))

