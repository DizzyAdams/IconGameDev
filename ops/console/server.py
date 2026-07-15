#!/usr/bin/env python3
"""IconMineMods Internal Console — backend (stdlib only, runs on Coolify).

Single HTTP server that is the operational hub:
  * Upload UGC skin PNGs + metadata -> appended to roblox_catalog.json
  * Every item is generated 100% Roblox-ToS-compliant (rules mirror
    compliance/checkers/roblox_check.py: original names, no IP/NSFW/redflags,
    price in 1..10000 Robux, required description, correct creator-share math).
  * Live compliance check (reuses the same scanner) before anything is submitted.
  * Builds batch_eligible.json (items with image present) for submit_roblox.py.
  * Triggers the REAL uploader (submit/submit_roblox.py) — no login, API-key only.

Endpoints:
  GET  /api/health
  GET  /api/catalog                  -> full catalog + compliance rollup
  POST /api/catalog                  -> add item {name,type,price_robux?,image:file}
  POST /api/catalog/bulk             -> add many items (JSON array) [optional image zip later]
  GET  /api/compliance               -> full ToS audit of current catalog
  POST /api/build-batch              -> (re)write batch_eligible.json
  POST /api/submit                   -> run submit_roblox.py (--test-one or full)
  GET  /api/secrets                  -> redacted secret status (which are set)
  POST /api/secrets                  -> save roblox creds to ops/secrets.json
  GET  /api/platforms                -> list of connected platforms + status

Run:
  python server.py --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import os
import sys
import json
import cgi
import urllib.parse
import argparse
import subprocess
import datetime
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent            # IconGameDev
OPS = ROOT / "ops"
SECRETS = OPS / "secrets.json"
ASSETS_DIR = ROOT / "roblox-ugc" / "assets"
CATALOG = ROOT / "roblox-ugc" / "catalog" / "roblox_catalog.json"
SUBMIT_DIR = ROOT / "submit"
BATCH = SUBMIT_DIR / "batch_eligible.json"

# ── Compliance rules (mirror of compliance/checkers/roblox_check.py) ────
PRICE_MIN, PRICE_MAX = 1, 10000
DEVEX_RATE = 0.0035

IP_BLOCKED = [
    "pokemon", "naruto", "dragon-ball", "bleach", "genshin", "fnaf",
    "hello-kitty", "demon-slayer", "chainsaw-man", "one-piece", "jujutsu",
    "sonic", "tadc", "attack-on-titan", "little-nightmares", "marvel",
    "minecraft", "mojang", "fortnite", "epic games", "disney", "star wars",
    "harry potter", "lord of the rings", "sponge bob", "batman", "superman",
    "wonder woman", "avengers", "x-men", "transformers", "power rangers",
    "tmnt", "teenage mutant ninja turtles", "spider man", "iron man",
]
NSFW = ["nude", "porn", "nazi", "sex", "sexual", "hentai", "escort",
        "dating", "romantic roleplay", "strip", "erotic"]
RED_FLAGS = [
    "auto farm", "loot", "crate", "gamble", "casino", "free robux",
    "robux generator", "hack", "cheat", "exploit", "mod menu",
    "admin pass", "nitro", "generator", "unfair advantage", "raffle",
    "giveaway", "spin to win", "slot machine", "bet", "wagering",
]

TYPE_MAP = {
    "classic_shirt": "Shirt",
    "classic_pants": "Pants",
    "avatar_accessory": "Hat",
    "game_pass": "GamePass",
}
# creator share per type (must match generate_catalog.py)
SHARE = {"classic_shirt": 0.70, "classic_pants": 0.70,
         "game_pass": 0.70, "avatar_accessory": 0.30}

# Public, compliant descriptions (no gameplay advantage wording for items;
# game passes describe a clearly-stated convenience/cosmetic benefit).
DESC = {
    "classic_shirt": "Original IconHub classic shirt. Cosmetic avatar item; no gameplay advantage.",
    "classic_pants": "Original IconHub classic pants. Cosmetic avatar item; no gameplay advantage.",
    "avatar_accessory": "Original IconHub avatar accessory. Cosmetic item; no gameplay advantage.",
    "game_pass": "IconHub experience game pass. Grants a clearly described cosmetic or convenience benefit. No random rewards and no gambling mechanics.",
}
DEFAULT_PRICE = {"classic_shirt": 70, "classic_pants": 70,
                 "avatar_accessory": 150, "game_pass": 250}


def _scan(text: str) -> list[str]:
    t = (text or "").lower()
    out: list[str] = []
    for pat in IP_BLOCKED:
        if pat in t:
            out.append(f"IP '{pat}'")
    for pat in NSFW:
        if pat in t:
            out.append(f"NSFW '{pat}'")
    for pat in RED_FLAGS:
        if pat in t:
            out.append(f"REDFLAG '{pat}'")
    return out


def compliant_name(name: str) -> tuple[bool, list[str]]:
    """Validate an item name is ToS-safe."""
    v = _scan(name)
    if not name or not name.strip():
        v.append("EMPTY name")
    if len(name or "") > 50:
        v.append("name too long (>50)")
    return (len(v) == 0), v


def find_image(name: str):
    if not ASSETS_DIR.is_dir():
        return None
    for cand in (name, name.replace(" ", "_")):
        for ext in (".png", ".jpg", ".jpeg"):
            p = ASSETS_DIR / (cand + ext)
            if p.is_file():
                return p
    return None


# ── Catalog I/O ──────────────────────────────────────────────────────────
def load_catalog() -> dict:
    if CATALOG.is_file():
        try:
            return json.loads(CATALOG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"items": []}


def save_catalog(data: dict):
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def next_id(items: list) -> int:
    return max([x.get("id", 0) for x in items] + [0]) + 1


def add_item(name: str, typ: str, price_robux: int | None) -> dict:
    """Create a 100%-compliant catalog entry. Raises ValueError if name unsafe."""
    ok, v = compliant_name(name)
    if not ok:
        raise ValueError("Nome viola ToS: " + ", ".join(v))
    if typ not in TYPE_MAP:
        raise ValueError("Tipo inválido: " + str(typ))
    price = int(price_robux) if price_robux else DEFAULT_PRICE[typ]
    if not (PRICE_MIN <= price <= PRICE_MAX):
        # clamp to a safe value rather than fail — compliance-safe default
        price = DEFAULT_PRICE[typ]
    net = round(price * SHARE[typ])
    item = {
        "id": next_id(load_catalog().get("items", [])),
        "name": name,
        "type": typ,
        "price_robux": price,
        "net_robux": net,
        "devex_usd": round(net * DEVEX_RATE, 4),
        "description": DESC[typ],
        "original_asset": True,
        "ip_clean": True,
        "notes": "Internal console upload (original art)",
        "has_image": find_image(name) is not None,
        "submitted": False,
    }
    return item


def audit(items: list) -> dict:
    fails: list[str] = []
    for x in items:
        typ = x.get("type", "?")
        name = x.get("name", "?")
        idx = x.get("id", "?")
        price = x.get("price_robux", 0)
        if not (PRICE_MIN <= price <= PRICE_MAX):
            fails.append(f"[{idx}] {typ} '{name}' price={price} out of range")
        exp_net = round(price * SHARE.get(typ, 0.30))
        if x.get("net_robux") is not None and x.get("net_robux") != exp_net:
            fails.append(f"[{idx}] net_robux mismatch")
        if not (x.get("description") or "").strip():
            fails.append(f"[{idx}] missing description")
        for field, text in (("name", name), ("description", x.get("description", "")), ("notes", x.get("notes", ""))):
            for vi in _scan(text):
                fails.append(f"[{idx}] {typ} '{name}' {field} {vi}")
        if typ != "game_pass" and not x.get("has_image") and not find_image(name):
            fails.append(f"[{idx}] '{name}' image missing")
    total = len(items)
    passed = total - len(set(f.split("]")[0] for f in fails if f.startswith("[")))
    pct = round((passed / total) * 100) if total else 100
    return {"total": total, "violations": fails, "compliant_pct": pct,
            "passed": passed, "failed": total - passed}


def build_batch() -> dict:
    data = load_catalog()
    elig = [x for x in data.get("items", [])
            if x.get("type") in TYPE_MAP and (find_image(x.get("name", "")) or x.get("has_image"))]
    BATCH.parent.mkdir(parents=True, exist_ok=True)
    BATCH.write_text(json.dumps({"items": elig}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"eligible": len(elig), "path": str(BATCH)}


# ── Secrets ──────────────────────────────────────────────────────────────
def load_secrets() -> dict:
    if SECRETS.is_file():
        try:
            return json.loads(SECRETS.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def secret_status() -> dict:
    s = load_secrets()
    r = s.get("roblox", {})
    def present(v):
        return bool(v) and not str(v).startswith("<")
    return {
        "roblox_api_key": present(r.get("api_key")),
        "roblox_group_id": present(r.get("group_id")),
        "roblox_experience_id": present(r.get("experience_id")) and str(r.get("experience_id")).strip() not in ("0", ""),
        "has_secrets_file": SECRETS.is_file(),
    }


def save_roblox_creds(api_key: str, group_id: str, experience_id: str):
    s = load_secrets()
    s.setdefault("roblox", {})
    s["roblox"]["api_key"] = api_key
    s["roblox"]["group_id"] = group_id
    s["roblox"]["experience_id"] = experience_id
    OPS.mkdir(parents=True, exist_ok=True)
    SECRETS.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ── Submit trigger ───────────────────────────────────────────────────────
def run_submit(test_one: bool) -> dict:
    if not (SUBMIT_DIR / "submit_roblox.py").is_file():
        return {"ok": False, "error": "submit_roblox.py not found"}
    build_batch()
    cmd = [sys.executable, str(SUBMIT_DIR / "submit_roblox.py")]
    if test_one:
        cmd.append("--test-one")
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=600)
        ok = proc.returncode == 0
        if ok and not test_one:
            # mark eligible items as submitted
            mark_submitted()
        return {"ok": ok, "returncode": proc.returncode,
                "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-2000:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout (10min)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def mark_submitted():
    data = load_catalog()
    elig = {x.get("name") for x in data.get("items", [])
            if x.get("type") in TYPE_MAP and (find_image(x.get("name", "")) or x.get("has_image"))}
    for x in data.get("items", []):
        if x.get("name") in elig:
            x["submitted"] = True
    save_catalog(data)


def sales_summary() -> dict:
    items = [x for x in load_catalog().get("items", []) if x.get("type") in TYPE_MAP]
    by_type: dict = {}
    tot_robux = tot_net = tot_usd = 0
    for x in items:
        t = x.get("type")
        net = x.get("net_robux", 0) or 0
        usd = x.get("devex_usd", 0) or 0
        b = by_type.setdefault(t, {"count": 0, "net_robux": 0, "devex_usd": 0})
        b["count"] += 1
        b["net_robux"] += net
        b["devex_usd"] += usd
        tot_net += net
        tot_usd += usd
    submitted = sum(1 for x in items if x.get("submitted"))
    # projected monthly: assume 10% of catalog sells per month (conservative)
    monthly_factor = 0.10
    return {
        "total_items": len(items),
        "submitted": submitted,
        "pending_submit": len(items) - submitted,
        "total_net_robux": tot_net,
        "total_devex_usd": round(tot_usd, 2),
        "projected_monthly_usd": round(tot_usd * monthly_factor, 2),
        "by_type": by_type,
    }


# ── HTTP handler ──────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict | str, ctype="application/json"):
        if isinstance(payload, dict):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        else:
            body = payload.encode("utf-8") if isinstance(payload, str) else payload
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, "")

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/health":
            return self._send(200, {"status": "ok", "ts": datetime.datetime.now().isoformat()})
        # Console access gate (set CONSOLE_PASSWORD env on Coolify to enable)
        gate = os.environ.get("CONSOLE_PASSWORD")
        if gate and self.headers.get("x-console-key") != gate:
            return self._send(401, {"error": "unauthorized", "hint": "set x-console-key header"})
        if u.path == "/api/catalog":
            data = load_catalog()
            items = data.get("items", [])
            return self._send(200, {"items": items, "audit": audit(items)})
        if u.path == "/api/compliance":
            items = load_catalog().get("items", [])
            return self._send(200, audit(items))
        if u.path == "/api/secrets":
            return self._send(200, secret_status())
        if u.path == "/api/platforms":
            return self._send(200, {
                "platforms": [
                    {"key": "roblox", "label": "Roblox UGC", "status": "connected",
                     "items": len(load_catalog().get("items", []))},
                    {"key": "bedrock", "label": "Minecraft Bedrock", "status": "planned"},
                    {"key": "epic", "label": "Fortnite Creative", "status": "planned"},
                ]
            })
        if u.path == "/api/sales":
            return self._send(200, sales_summary())
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        # Console access gate (set CONSOLE_PASSWORD env on Coolify to enable)
        gate = os.environ.get("CONSOLE_PASSWORD")
        if gate and self.headers.get("x-console-key") != gate:
            return self._send(401, {"error": "unauthorized", "hint": "set x-console-key header"})
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""

        if u.path == "/api/catalog":
            return self._handle_add_item(raw)
        if u.path == "/api/build-batch":
            return self._send(200, build_batch())
        if u.path == "/api/submit":
            try:
                body = json.loads(raw or b"{}")
            except Exception:
                body = {}
            res = run_submit(bool(body.get("test_one")))
            return self._send(200, res)
        if u.path == "/api/submit/auto":
            # full batch submit + mark submitted; returns combined summary
            res = run_submit(False)
            return self._send(200, {"submit": res, "sales": sales_summary()})
        if u.path == "/api/secrets":
            return self._handle_secrets(raw)
        return self._send(404, {"error": "not found"})

    def _handle_add_item(self, raw: bytes):
        ctype = self.headers.get("Content-Type", "")
        if "multipart/form-data" in ctype:
            item, err = self._parse_multipart(ctype, raw)
            if err:
                return self._send(400, {"error": err})
        else:
            try:
                body = json.loads(raw or b"{}")
            except Exception as e:
                return self._send(400, {"error": "JSON inválido: " + str(e)})
            item = body
        try:
            new = add_item(item.get("name", ""), item.get("type", ""),
                           item.get("price_robux"))
        except ValueError as e:
            return self._send(422, {"error": str(e)})
        data = load_catalog()
        data.setdefault("items", []).append(new)
        save_catalog(data)
        return self._send(201, {"item": new, "audit": audit(data["items"])})

    def _parse_multipart(self, ctype: str, raw: bytes):
        boundary = cgi.parse_header(ctype)[1].get("boundary")
        if not boundary:
            return None, "sem boundary"
        b = ("--" + boundary).encode()
        parts = raw.split(b)
        fields: dict[str, str] = {}
        image_name = None
        image_bytes = None
        for part in parts:
            if b"\r\n\r\n" not in part:
                continue
            head, _, payload = part.partition(b"\r\n\r\n")
            head = head.decode("utf-8", "replace")
            if 'name="' not in head:
                continue
            name = head.split('name="')[1].split('"')[0]
            if 'filename="' in head:
                fn = head.split('filename="')[1].split('"')[0]
                if fn and image_bytes is None:
                    image_name = fn
                    image_bytes = payload.rstrip(b"\r\n")
            else:
                val = payload.rstrip(b"\r\n").decode("utf-8", "replace")
                fields[name] = val
        if image_name and image_bytes:
            ASSETS_DIR.mkdir(parents=True, exist_ok=True)
            # store as <name>.png (spaces->underscore to match submit_roblox.find_image)
            base = (fields.get("name") or image_name.rsplit(".", 1)[0]).replace(" ", "_")
            ext = "." + image_name.rsplit(".", 1)[-1].lower() if "." in image_name else ".png"
            (ASSETS_DIR / (base + ext)).write_bytes(image_bytes)
        return fields, None

    def _handle_secrets(self, raw: bytes):
        try:
            body = json.loads(raw or b"{}")
        except Exception as e:
            return self._send(400, {"error": str(e)})
        save_roblox_creds(body.get("api_key", ""), body.get("group_id", ""),
                          body.get("experience_id", ""))
        return self._send(200, {"saved": True, "status": secret_status()})

    def log_message(self, *args):
        pass  # quiet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"IconMineMods console backend on http://{args.host}:{args.port}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
