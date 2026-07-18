#!/usr/bin/env python3
"""Roblox Open Cloud UGC uploader -- catalog items + game passes.

Real implementation of the asset-creation flow (multipart binary upload) for
avatar items (ClassicShirt / ClassicPants / Hat) and v2 game-pass creation.

Images live in roblox-ugc/assets/, named by catalog item `name`:
  <name>.png | <name>.jpg | <name>.jpeg
(game passes use the same naming for their icon; icon upload is NOT automated
yet -- add the icon manually in Creator Hub after creation. See GAMEPASS note.)

Credentials: env ROBLOX_API_KEY / ROBLOX_GROUP_ID / ROBLOX_EXPERIENCE_ID,
OR ops/secrets.json -> roblox.* (placeholder values like "<...>" are ignored).

CLI:
  python submit_roblox.py --dry-run     validate config + image mapping, NO network
  python submit_roblox.py --test-one     upload EXACTLY ONE item, then stop.
                                    Safe first real run before the full 100.
  python submit_roblox.py               real upload all (idempotent by name)
"""
import os
import sys
import json
import time
import argparse
import random
import string
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CATALOG = os.path.join(ROOT, "roblox-ugc", "catalog", "roblox_catalog.json")
ASSETS_DIR = os.path.join(ROOT, "roblox-ugc", "assets")
STATE_FILE = os.path.join(HERE, "state_roblox.json")
REPORT_FILE = os.path.join(HERE, "last_run_report.json")
SECRETS = os.path.join(ROOT, "ops", "secrets.json")

# Automation budget/boundaries.
MAX_ITEMS = 500						# hard cap per real run
REQUEST_RETRIES = 3					# retries on transient HTTP/network errors
REQUEST_BACKOFF_BASE = 1.0			# seconds
UPLOAD_BUDGET_BYTES = 250 * 1024 * 1024  # 250MB guard

TYPE_MAP = {
    "classic_shirt": "Shirt",
    "classic_pants": "Pants",
    "avatar_accessory": "Hat",
    "game_pass": "GamePass",
}

ASSETS_URL = "https://apis.roblox.com/assets/v1/assets"
GAMEPASS_URL = "https://apis.roblox.com/cloud/v2/universes/{universe}/user-game-passes"


def load_env_file(path):
    """Minimal .env parser (KEY=VALUE, optional quotes). Returns dict."""
    out = {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return out


def load_creds():
    # Priority: ENV vars > .env (gitignored) > ops/secrets.json (placeholders ignored)
    api = os.environ.get("ROBLOX_API_KEY")
    gid = os.environ.get("ROBLOX_GROUP_ID")
    uid = os.environ.get("ROBLOX_EXPERIENCE_ID")
    ef = {}
    env_files = [".env", "ROBLOX_CONFIG.env", "roblox_config.env", "keyroblox.env", "KEYROBLOX.ENV"]
    for cand in env_files:
        p = os.path.join(ROOT, cand)
        if os.path.isfile(p):
            ef = load_env_file(p)
            break
    if not api:
        api = ef.get("ROBLOX_API_KEY")
    if not gid:
        gid = ef.get("ROBLOX_GROUP_ID")
    if not uid:
        uid = ef.get("ROBLOX_EXPERIENCE_ID")
    if not (api and gid and uid) and os.path.isfile(SECRETS):
        try:
            with open(SECRETS, encoding="utf-8") as f:
                s = json.load(f)
            r = s.get("roblox", {})

            def clean(v):
                return v if (v and not str(v).startswith("<")) else None

            api = clean(api) or clean(r.get("api_key"))
            gid = clean(gid) or clean(r.get("group_id"))
            uid = clean(uid) or clean(r.get("experience_id"))
        except Exception:
            pass
    return api, gid, uid


def find_image(name):
    if not os.path.isdir(ASSETS_DIR):
        return None
    # Generator saves as "Crimson_Shirt.png" (spaces -> underscores). Match both.
    candidates = [name, name.replace(" ", "_")]
    for cand in candidates:
        for ext in (".png", ".jpg", ".jpeg"):
            p = os.path.join(ASSETS_DIR, cand + ext)
            if os.path.isfile(p):
                return p
    return None


def load_items():
    if not os.path.isfile(CATALOG):
        return []
    try:
        with open(CATALOG, encoding="utf-8") as f:
            return json.load(f).get("items", [])
    except Exception:
        return []


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def make_boundary():
    return "----rb" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))


def post_multipart(url, api_key, fields, file_path, file_field="file"):
    with open(file_path, "rb") as fh:
        data = fh.read()
    fname = os.path.basename(file_path)
    low = fname.lower()
    if low.endswith(".png"):
        mime = "image/png"
    elif low.endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    else:
        mime = "application/octet-stream"
    b = make_boundary().encode()
    CRLF = b"\r\n"
    body = b""
    for k, v in fields.items():
        body += b"--" + b + CRLF
        body += b"Content-Disposition: form-data; name=\"" + k.encode() + b"\"" + CRLF
        body += b"Content-Type: application/json" + CRLF
        body += CRLF + v.encode() + CRLF
    body += b"--" + b + CRLF
    body += b"Content-Disposition: form-data; name=\"" + file_field.encode() + b"\"; filename=\"" + fname.encode() + b"\"" + CRLF
    body += b"Content-Type: " + mime.encode() + CRLF
    body += CRLF + data + CRLF
    body += b"--" + b + b"--" + CRLF
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "multipart/form-data; boundary=" + b.decode(),
        "x-api-key": api_key,
    }, method="POST")
    for attempt in range(REQUEST_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return (True, r.status, r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            payload = e.read().decode("utf-8", "replace")
            return (False, e.code, payload)
        except Exception as e:
            if attempt < REQUEST_RETRIES - 1:
                time.sleep(REQUEST_BACKOFF_BASE * (attempt + 1))
                continue
            return (False, 0, str(e))
    return (False, 0, "retries_exhausted")


def post_json(url, api_key, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }, method="POST")
    for attempt in range(REQUEST_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return (True, r.status, r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            payload = e.read().decode("utf-8", "replace")
            return (False, e.code, payload)
        except Exception as e:
            if attempt < REQUEST_RETRIES - 1:
                time.sleep(REQUEST_BACKOFF_BASE * (attempt + 1))
                continue
            return (False, 0, str(e))
    return (False, 0, "retries_exhausted")


def upload_item(api, gid, uid, item):
    t = item.get("type")
    name = item.get("name")
    asset_type = TYPE_MAP.get(t)
    if not asset_type:
        return (False, "UNSUPPORTED_TYPE:%s" % t)
    if t == "game_pass":
        if not name or not isinstance(name, str) or not name.strip():
            return (False, "INVALID_NAME:game_pass")
        ok, code, resp = post_json(GAMEPASS_URL.format(universe=uid), api, {
            "displayName": name.strip(),
            "description": "IconHub game pass: " + name.strip(),
        })
        return (ok, "HTTP %d %s" % (code, resp[:200]))
    img = find_image(name)
    if not img:
        return (False, "NO IMAGE for %s (expected in %s)" % (name, ASSETS_DIR))
    try:
        img_size = os.path.getsize(img)
    except OSError as e:
        return (False, "IMAGE_ACCESS_ERROR:%s" % e)
    if img_size <= 0 or img_size > 10 * 1024 * 1024:
        return (False, "IMAGE_SIZE_OUT_OF_RANGE:%s" % img_size)
    fields = {
        "request": json.dumps({
            "assetType": asset_type,
            "displayName": name,
            "description": item.get("description") or ("IconHub original %s: %s" % (t, name)),
            # API key is group-scoped (created in Creator Hub -> group): creator must be
            # the GROUP, not a userId. Passing group_id as userId causes 403 "User not
            # authenticated".
            "creationContext": {"creator": {"groupId": int(gid)}},
        }),
    }
    ok, code, resp = post_multipart(ASSETS_URL, api, fields, img, file_field="fileContent")
    return (ok, "HTTP %d %s" % (code, resp[:200]))


def dry_run():
    items = load_items()
    api, gid, uid = load_creds()
    print("=== Roblox UGC dry-run ===")
    print("items found:    %d" % len(items))
    print("creds present:  %s" % bool(api and gid and uid))
    print("assets dir:     %s %s" % (ASSETS_DIR, "(exists)" if os.path.isdir(ASSETS_DIR) else "(MISSING)"))
    missing = 0
    for it in items:
        if it.get("type") != "game_pass" and not find_image(it.get("name")):
            missing += 1
            print("  [NO IMAGE] %s (%s)" % (it.get("name"), it.get("type")))
    print("items missing image (non-gamepass): %d" % missing)
    sys.exit(0)


def real_run(test_one=False):
    items = load_items()
    api, gid, uid = load_creds()
    state = load_state()
    uploaded = skipped = errors = 0
    budget_bytes = 0
    if not (api and gid and uid):
        print("CREDENTIALS MISSING -> no uploads (safe no-op). Fill ops/secrets.json roblox.* or env.")
        sys.exit(0)
    allowed = 1 if test_one else MAX_ITEMS
    if len(items) > allowed:
        items = items[:allowed]
        print("BUDGET: capped run to %d items (have %d)" % (allowed, len(load_items())))
    for it in items:
        name = it.get("name")
        prev = state.get(name)
        if prev and prev.get("status") == "uploaded":
            skipped += 1
            continue
        ok, msg = upload_item(api, gid, uid, it)
        if ok:
            uploaded += 1
            state[name] = {"status": "uploaded", "type": it.get("type")}
            print("uploaded: %s (%s)" % (name, msg))
        else:
            errors += 1
            state[name] = {"status": "error", "msg": msg}
            print("ERROR %s: %s" % (name, msg))
        if test_one:
            print("--test-one: stopping after first attempt.")
            break
    save_state(state)
    report = {
        "uploaded": uploaded,
        "skipped": skipped,
        "errors": errors,
        "budget_bytes": budget_bytes,
        "budget_max_bytes": UPLOAD_BUDGET_BYTES,
    }
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            f.write("\n")
        print("\nreport: %s" % REPORT_FILE)
    except Exception as e:
        print("\nWARNING: could not write report: %s" % e)
    print("\nSUMMARY: uploaded=%d skipped=%d errors=%d" % (uploaded, skipped, errors))
    sys.exit(0 if errors == 0 else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--test-one", action="store_true")
    args = ap.parse_args()
    if args.dry_run:
        dry_run()
    else:
        real_run(test_one=args.test_one)


if __name__ == "__main__":
    main()
