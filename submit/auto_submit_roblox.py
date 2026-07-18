#!/usr/bin/env python3
"""
Roblox Open Cloud UGC auto-submitter — batch upload de itens PNG para Roblox Marketplace.

Escaneia roblox-ugc/items/ (ou assets/) por PNGs, faz match com o catálogo
(roblox_catalog.json), e faz upload batch usando a Assets API v1 da Roblox.

Fluxo:
  1. Lê catálogo + credenciais
  2. Escaneia diretório de PNGs
  3. Faz match imagem → item do catálogo (por nome + tipo)
  4. Filtra itens já enviados (state_roblox.json)
  5. Envia em batch com rate limiting
  6. Gera relatório final

CLI:
  python auto_submit_roblox.py                      # upload batch completo
  python auto_submit_roblox.py --dry-run             # valida sem enviar
  python auto_submit_roblox.py --test-one            # envia 1 item e para
  python auto_submit_roblox.py --items-dir items     # diretório customizado
  python auto_submit_roblox.py --unmatched-only      # só itens sem match no catálogo
  python auto_submit_roblox.py --rate-limit 1.5      # delay entre uploads (segundos)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import random
import string
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

CATALOG_DIR = ROOT / "roblox-ugc" / "catalog"
CATALOG_FILE = CATALOG_DIR / "roblox_catalog.json"
ASSETS_DIR = ROOT / "roblox-ugc" / "assets"
ITEMS_DIR = ROOT / "roblox-ugc" / "items"

STATE_FILE = HERE / "state_roblox.json"
REPORT_FILE = HERE / "last_run_report.json"
SECRETS_FILE = ROOT / "ops" / "secrets.json"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ASSETS_URL = "https://apis.roblox.com/assets/v1/assets"
GAMEPASS_URL = "https://apis.roblox.com/cloud/v2/universes/{universe}/user-game-passes"

TYPE_MAP: dict[str, str] = {
    "classic_shirt": "Shirt",
    "classic_pants": "Pants",
    "avatar_accessory": "Hat",
    "game_pass": "GamePass",
}

SUFFIX_MAP: dict[str, str] = {
    "classic_shirt": "Shirt",
    "classic_pants": "Pants",
    "avatar_accessory": "Accessory",
    "game_pass": "Pass",
}

ITEM_TYPES_BY_SUFFIX: dict[str, str] = {v: k for k, v in SUFFIX_MAP.items()}

DESC_MAP: dict[str, str] = {
    "classic_shirt": "Original IconHub classic shirt. Cosmetic avatar item; no gameplay advantage.",
    "classic_pants": "Original IconHub classic pants. Cosmetic avatar item; no gameplay advantage.",
    "avatar_accessory": "Original IconHub avatar accessory. Cosmetic item; no gameplay advantage.",
    "game_pass": "IconHub experience game pass. Cosmetic or convenience benefit. No random rewards.",
}

PRICE_MAP: dict[str, int] = {
    "classic_shirt": 70,
    "classic_pants": 70,
    "avatar_accessory": 150,
    "game_pass": 250,
}

# Upload budget / boundaries
MAX_ITEMS_PER_RUN = 500
REQUEST_RETRIES = 3
REQUEST_BACKOFF_BASE = 1.0  # seconds
UPLOAD_BUDGET_BYTES = 250 * 1024 * 1024  # 250 MB
DEFAULT_RATE_LIMIT = 1.0  # seconds between uploads

# --dry-run implies rate_limit=0; real runs use this default
VARIANTS = {"Neon", "Glitch", "Retro", "Royal", "Shadow", "Prism",
            "Ember", "Frost", "Golden", "Lunar", "Storm", "Void"}

# ---------------------------------------------------------------------------
# Credentials loader (copied from submit_roblox.py)
# ---------------------------------------------------------------------------


def load_env_file(path: str | Path) -> dict[str, str]:
    """Minimal .env parser (KEY=VALUE, optional quotes). Returns dict."""
    out: dict[str, str] = {}
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


def load_creds() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (api_key, group_id, experience_id) or (None, None, None)."""
    api = os.environ.get("ROBLOX_API_KEY")
    gid = os.environ.get("ROBLOX_GROUP_ID")
    uid = os.environ.get("ROBLOX_EXPERIENCE_ID")

    ef: dict[str, str] = {}
    for cand in [".env", "ROBLOX_CONFIG.env", "roblox_config.env",
                 "keyroblox.env", "KEYROBLOX.ENV"]:
        p = ROOT / cand
        if p.is_file():
            ef = load_env_file(p)
            break
    if not api:
        api = ef.get("ROBLOX_API_KEY")
    if not gid:
        gid = ef.get("ROBLOX_GROUP_ID")
    if not uid:
        uid = ef.get("ROBLOX_EXPERIENCE_ID")

    if not (api and gid and uid) and SECRETS_FILE.is_file():
        try:
            with open(SECRETS_FILE, encoding="utf-8") as f:
                s = json.load(f)
            r = s.get("roblox", {})

            def clean(v: object) -> str | None:
                return str(v) if (v and not str(v).startswith("<")) else None

            api = clean(api) or clean(r.get("api_key"))
            gid = clean(gid) or clean(r.get("group_id"))
            uid = clean(uid) or clean(r.get("experience_id"))
        except Exception:
            pass

    return api, gid, uid


def verify_auth(api: str, gid: str) -> tuple[bool, str, str]:
    """
    Pre-flight auth check against Roblox Open Cloud. Returns (ok, detail, creator_type).
    Tries Group API first, if 404 tries User API.
    A 401/403 here means the key is invalid/expired/wrong-account.
    """
    import urllib.request as _ur
    # Try Group first
    url_group = f"https://apis.roblox.com/cloud/v2/groups/{gid}"
    req_group = _ur.Request(url_group, headers={"x-api-key": api, "Accept": "application/json"})
    try:
        with _ur.urlopen(req_group, timeout=20) as resp:
            return True, f"HTTP {resp.status}", "Group"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Try User
            url_user = f"https://apis.roblox.com/cloud/v2/users/{gid}"
            req_user = _ur.Request(url_user, headers={"x-api-key": api, "Accept": "application/json"})
            try:
                with _ur.urlopen(req_user, timeout=20) as resp_user:
                    return True, f"HTTP {resp_user.status}", "User"
            except urllib.error.HTTPError as e_user:
                body = ""
                try:
                    body = e_user.read().decode("utf-8", "ignore")[:200]
                except Exception:
                    pass
                return False, f"User API: HTTP {e_user.code} {body}", "User"
            except Exception as e_user:
                return False, f"User API: {type(e_user).__name__}: {e_user}", "User"
        else:
            body = ""
            try:
                body = e.read().decode("utf-8", "ignore")[:200]
            except Exception:
                pass
            return False, f"Group API: HTTP {e.code} {body}", "Group"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", "Group"


def wait_for_valid_key(gid: str, poll: int = 30, timeout: int = 86400) -> Optional[tuple[str, str, str]]:
    """
    Poll ops/secrets.json (and .env) until load_creds() yields a key that
    passes verify_auth(). Returns the working (api_key, detail, creator_type), or None on timeout.
    Used by --wait-for-key so the pipeline can run unattended in background
    the moment the human drops a valid key in.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        api, g, u = load_creds()
        if api and g:
            ok, detail, creator_type = verify_auth(api, g)
            if ok:
                print(f"[OK] Chave válida detectada ({detail}, tipo: {creator_type}). Iniciando submit.")
                return api, detail, creator_type
            else:
                print(f"[...] Chave ainda inválida ({detail}). Aguardando nova chave...")
        else:
            print("[...] Sem chave em ops/secrets.json/.env. Aguardando...")
        time.sleep(poll)
    return None



def load_catalog() -> list[dict]:
    """Load items from the Roblox catalog JSON. Returns empty list on failure."""
    if not CATALOG_FILE.is_file():
        return []
    try:
        with open(CATALOG_FILE, encoding="utf-8") as f:
            return json.load(f).get("items", [])
    except Exception:
        return []


def build_catalog_by_name(items: list[dict]) -> dict[str, dict]:
    """Index catalog items by name for O(1) lookup."""
    return {it["name"]: it for it in items if "name" in it}


# ---------------------------------------------------------------------------
# Local state for idempotent runs
# ---------------------------------------------------------------------------


def load_state() -> dict:
    if STATE_FILE.is_file():
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


# ---------------------------------------------------------------------------
# Image discovery
# ---------------------------------------------------------------------------


def scan_png_dir(items_dir: Path) -> list[Path]:
    """Return sorted list of .png file paths in items_dir."""
    if not items_dir.is_dir():
        return []
    pngs = sorted(items_dir.glob("*.png"))
    return pngs


def infer_item_type(filename_stem: str) -> Optional[str]:
    """
    Try to infer item type from filename.
    E.g. 'Crimson Wings Accessory Frost' -> 'avatar_accessory'
         'Crimson Shirt' -> 'classic_shirt'
         'Crimson Shirt Neon' -> 'classic_shirt'
    """
    # Check for suffix in filename
    for suffix, typ in ITEM_TYPES_BY_SUFFIX.items():
        # The suffix could appear as the SECOND-TO-LAST word before variant
        # e.g. "Crimson Wings Accessory Frost" -> "Accessory" is the suffix
        # e.g. "Double XP Pass" -> "Pass" is the suffix... but Pass isn't a real type
        parts = filename_stem.split()
        for i, p in enumerate(parts):
            if p == suffix:
                # Check if it's actually the type suffix and not part of the name
                # Simple heuristic: the suffix word appears in the name
                return typ
    return None


def strip_variant(name: str) -> str:
    """
    Strip known variant suffix from name.
    'Crimson Shirt Neon' -> 'Crimson Shirt'
    'Crimson Wings Accessory Frost' -> 'Crimson Wings Accessory'
    """
    parts = name.split()
    if len(parts) >= 2 and parts[-1] in VARIANTS:
        return " ".join(parts[:-1])
    return name


def match_image_to_catalog(
    png_path: Path, catalog_index: dict[str, dict]
) -> Optional[dict]:
    """
    Try to match a PNG file to a catalog item.
    Strategy:
      1. Exact match: filename_stem == catalog item name
      2. Strip variant: strip_variant(filename_stem) == catalog item name
    Returns the catalog item dict, or None.
    """
    stem = png_path.stem

    # Exact
    if stem in catalog_index:
        return catalog_index[stem]

    # Strip variant
    base = strip_variant(stem)
    if base in catalog_index:
        return catalog_index[base]

    return None


def auto_discover_items(
    items_dir: Path,
    catalog_index: dict[str, dict],
    unmatched_only: bool = False,
) -> list[tuple[Path, Optional[dict]]]:
    """
    Scan items_dir for PNGs and match to catalog.
    Returns list of (png_path, catalog_item_or_None).

    When unmatched_only=True, only return items NOT found in catalog_index.
    """
    pngs = scan_png_dir(items_dir)
    results: list[tuple[Path, Optional[dict]]] = []

    for png in pngs:
        cat_item = match_image_to_catalog(png, catalog_index)
        if unmatched_only and cat_item is not None:
            continue
        results.append((png, cat_item))

    return results


# ---------------------------------------------------------------------------
# HTTP helpers (reused/adapted from submit_roblox.py)
# ---------------------------------------------------------------------------


def _make_boundary() -> str:
    return "----rb" + "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(16)
    )


# Roblox template sizes (transparent PNG on exact canvas). Wrong size => auto-reject.
TEMPLATE_DIMS: dict[str, tuple[int, int]] = {
    "Shirt": (585, 559),
    "Pants": (559, 559),
    "Hat": (1024, 1024),
}


def normalize_image(src: Path, asset_type: str) -> Path:
    """
    Paste the source art centered onto a transparent canvas of the EXACT
    Roblox template size for the asset type (no distortion). Returns a temp
    PNG path to upload. Source is left untouched.

    NOTE: classic shirt/pants are 2D templates and this satisfies the
    dimension gate. 'Hat' (avatar_accessory) in practice also needs a 3D
    model on Roblox; this only fixes the image dimension, not the model.
    """
    dims = TEMPLATE_DIMS.get(asset_type)
    if not dims:
        return src
    try:
        from PIL import Image
        img = Image.open(src).convert("RGBA")
        canvas = Image.new("RGBA", dims, (0, 0, 0, 0))
        # center the art (may be smaller or larger than the target)
        cw, ch = canvas.size
        iw, ih = img.size
        left = max(0, (cw - iw) // 2)
        top = max(0, (ch - ih) // 2)
        # If source is larger, shrink to fit width/height to avoid clipping
        if iw > cw or ih > ch:
            img = img.copy()
            img.thumbnail((cw, ch), Image.LANCZOS)
            iw, ih = img.size
            left = max(0, (cw - iw) // 2)
            top = max(0, (ch - ih) // 2)
        canvas.paste(img, (left, top), img)
        tmp = src.with_suffix("").parent / f"__norm_{asset_type}_{src.stem}.png"
        tmp = HERE / tmp.name
        canvas.save(tmp, "PNG")
        return tmp
    except Exception as e:
        print(f"  [WARN] normalize_image failed ({e}); using original")
        return src


def post_multipart(
    url: str, api_key: str, fields: dict[str, str], file_path: str | Path,
    file_field: str = "file",
) -> tuple[bool, int, str]:
    """Multipart/form-data upload. Returns (ok, http_code, body_preview)."""
    with open(file_path, "rb") as fh:
        data = fh.read()
    fname = os.path.basename(str(file_path))
    low = fname.lower()
    if low.endswith(".png"):
        mime = "image/png"
    elif low.endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    else:
        mime = "application/octet-stream"

    boundary = _make_boundary()
    b = boundary.encode()
    CRLF = b"\r\n"
    body = b""
    for k, v in fields.items():
        body += b"--" + b + CRLF
        body += b'Content-Disposition: form-data; name="' + k.encode() + b'"' + CRLF
        body += b"Content-Type: application/json" + CRLF
        body += CRLF + v.encode() + CRLF
    body += b"--" + b + CRLF
    body += (
        b'Content-Disposition: form-data; name="' + file_field.encode()
        + b'"; filename="' + fname.encode() + b'"' + CRLF
    )
    body += b"Content-Type: " + mime.encode() + CRLF
    body += CRLF + data + CRLF
    body += b"--" + b + b"--" + CRLF

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "x-api-key": api_key,
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    for attempt in range(REQUEST_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return (True, r.status, r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            payload = e.read().decode("utf-8", "replace")
            # 429 = rate limited — always retry
            if e.code == 429 and attempt < REQUEST_RETRIES - 1:
                wait = REQUEST_BACKOFF_BASE * (attempt + 1) * 2
                print(f"  [RATE-LIMITED] retrying in {wait:.1f}s...")
                time.sleep(wait)
                continue
            return (False, e.code, payload[:500])
        except Exception as e:
            if attempt < REQUEST_RETRIES - 1:
                time.sleep(REQUEST_BACKOFF_BASE * (attempt + 1))
                continue
            return (False, 0, str(e))
    return (False, 0, "retries_exhausted")


def post_json(
    url: str, api_key: str, payload: dict
) -> tuple[bool, int, str]:
    """JSON POST. Returns (ok, http_code, body_preview)."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        method="POST",
    )
    for attempt in range(REQUEST_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return (True, r.status, r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            payload_text = e.read().decode("utf-8", "replace")
            if e.code == 429 and attempt < REQUEST_RETRIES - 1:
                wait = REQUEST_BACKOFF_BASE * (attempt + 1) * 2
                print(f"  [RATE-LIMITED] retrying in {wait:.1f}s...")
                time.sleep(wait)
                continue
            return (False, e.code, payload_text[:500])
        except Exception as e:
            if attempt < REQUEST_RETRIES - 1:
                time.sleep(REQUEST_BACKOFF_BASE * (attempt + 1))
                continue
            return (False, 0, str(e))
    return (False, 0, "retries_exhausted")


# ---------------------------------------------------------------------------
# Upload logic
# ---------------------------------------------------------------------------


def upload_asset_item(
    api: str, gid: str, item_type: str, display_name: str,
    description: str, image_path: Path, creator_type: str = "Group"
) -> tuple[bool, str]:
    """Upload an avatar asset (shirt, pants, accessory) via Assets API v1."""
    asset_type = TYPE_MAP.get(item_type)
    if not asset_type:
        return (False, f"UNSUPPORTED_TYPE:{item_type}")

    # Validate image
    try:
        img_size = image_path.stat().st_size
    except OSError as e:
        return (False, f"IMAGE_ACCESS_ERROR:{e}")
    if img_size <= 0 or img_size > 10 * 1024 * 1024:
        return (False, f"IMAGE_SIZE_OUT_OF_RANGE:{img_size}")

    creator_dict = {"groupId": int(gid), "type": "Group"} if creator_type == "Group" else {"userId": int(gid), "type": "User"}
    fields = {
        "request": json.dumps({
            "assetType": asset_type,
            "displayName": display_name,
            "description": description,
            "creationContext": {
                "creator": creator_dict,
            },
        }),
    }
    # Force exact template dimensions so Roblox does not reject on size
    upload_path = normalize_image(image_path, asset_type)
    ok, code, resp = post_multipart(ASSETS_URL, api, fields, upload_path, file_field="fileContent")
    # cleanup temp normalization file
    if upload_path != image_path:
        try:
            upload_path.unlink()
        except OSError:
            pass
    return (ok, f"HTTP {code} {resp[:200]}")


def upload_game_pass(
    api: str, uid: str, display_name: str, description: str
) -> tuple[bool, str]:
    """Create a game pass via Cloud v2 API. Icon must be added manually."""
    url = GAMEPASS_URL.format(universe=uid)
    ok, code, resp = post_json(url, api, {
        "displayName": display_name,
        "description": description,
    })
    return (ok, f"HTTP {code} {resp[:200]}")


def auto_upload_item(
    api: str, gid: str, uid: str,
    png_path: Path, cat_item: Optional[dict],
    price_robux: int, description: str,
    item_type: Optional[str] = None,
    creator_type: str = "Group",
) -> tuple[bool, str]:
    """
    Upload a single PNG as a Roblox item.
    If cat_item is provided, uses its type and name.
    Otherwise infers from filename or falls back to classic_shirt.

    Returns (ok, message).
    """
    if cat_item:
        typ = cat_item.get("type", "classic_shirt")
        name = cat_item["name"]
        desc = cat_item.get("description") or description
    elif item_type:
        typ = item_type
        name = png_path.stem
        desc = description
    else:
        # Infer type from filename
        inferred = infer_item_type(png_path.stem)
        typ = inferred or "classic_shirt"
        name = png_path.stem
        desc = description

    if typ == "game_pass":
        return upload_game_pass(api, uid, name, desc)
    else:
        return upload_asset_item(api, gid, typ, name, desc, png_path, creator_type=creator_type)


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------


def auto_submit(args: argparse.Namespace) -> int:
    """Main batch submit logic. Returns exit code."""
    api, gid, uid = load_creds()
    if not (api and gid and uid):
        print("[ERROR] Credenciais ausentes. Defina ROBLOX_API_KEY, ROBLOX_GROUP_ID "
              "e ROBLOX_EXPERIENCE_ID via env, .env ou ops/secrets.json")
        return 1

    creator_type = "Group"
    detail = "Unknown"
    # --wait-for-key: poll until a VALID key exists (background-friendly)
    if args.wait_for_key:
        print("[wait-for-key] Aguardando chave valida em ops/secrets.json ...")
        res = wait_for_valid_key(gid)
        if not res:
            print("[ERROR] Timeout aguardando chave valida.")
            return 1
        api, detail, creator_type = res  # a credencial validada
    else:
        # Pre-flight auth check (cheap, no uploads burnt) — fail fast on dead key
        ok, detail, creator_type = verify_auth(api, gid)
        if not ok:
            print(f"[ERROR] Chave Roblox NAO autoriza ({detail}). "
                  f"Gere uma API key valida em create.roblox.com/dashboard/credentials "
                  f"(Asset: Create) e cole aqui. Nenhum upload foi feito.")
            return 1
    print(f"[OK] Autenticacao Roblox OK ({detail}, tipo: {creator_type}).")

    # Load catalog
    catalog_items = load_catalog()
    catalog_index = build_catalog_by_name(catalog_items)
    print(f"[INFO] Catálogo carregado: {len(catalog_items)} itens")

    # Determine items directory
    items_dir = args.items_dir
    if items_dir is None:
        if ITEMS_DIR.is_dir():
            items_dir = ITEMS_DIR
        elif ASSETS_DIR.is_dir():
            items_dir = ASSETS_DIR
        else:
            print(f"[ERROR] Nenhum diretório de itens encontrado "
                  f"(tentados: {ITEMS_DIR}, {ASSETS_DIR})")
            return 1
    else:
        items_dir = Path(items_dir)

    print(f"[INFO] Diretório de imagens: {items_dir}")

    # Discover items
    discovered = auto_discover_items(
        items_dir, catalog_index, unmatched_only=args.unmatched_only
    )
    if not discovered:
        print("[INFO] Nenhum PNG encontrado para upload.")
        return 0

    matched = sum(1 for _, c in discovered if c is not None)
    unmatched = sum(1 for _, c in discovered if c is None)
    print(f"[INFO] PNGs encontrados: {len(discovered)} "
          f"(match catalog: {matched}, sem match: {unmatched})")

    # Load state (previously uploaded)
    state = load_state()
    print(f"[INFO] State carregado: {len(state)} itens registrados")

    # Filter already-uploaded
    to_upload: list[tuple[Path, Optional[dict]]] = []
    skipped_count = 0
    for png, cat_item in discovered:
        if cat_item:
            key = cat_item["name"]
        else:
            key = png.stem
        prev = state.get(key)
        if prev and prev.get("status") == "uploaded" and not args.force:
            skipped_count += 1
            continue
        to_upload.append((png, cat_item))

    print(f"[INFO] Já enviados (skip): {skipped_count}")
    print(f"[INFO] A enviar: {len(to_upload)}")

    if args.dry_run:
        print("\n=== DRY RUN — nenhum upload real ===")
        for png, cat_item in to_upload[:20]:
            name = cat_item["name"] if cat_item else png.stem
            typ = cat_item.get("type", "inferido") if cat_item else "inferido"
            print(f"  [DRY] {name:<40} ({typ}) <- {png.name}")
        if len(to_upload) > 20:
            print(f"  ... e mais {len(to_upload) - 20} itens")
        print(f"\nTotal simulated uploads: {len(to_upload)}")
        print("=== FIM DRY RUN ===\n")
        return 0

    # Budget cap
    allowed = args.max_items or MAX_ITEMS_PER_RUN
    if len(to_upload) > allowed:
        print(f"[INFO] BUDGET: capped to {allowed} items (have {len(to_upload)})")
        to_upload = to_upload[:allowed]

    # Real upload loop
    uploaded = 0
    errors = 0
    budget_bytes = 0
    rate_limit = args.rate_limit

    print(f"\n{'='*60}")
    print(f"Iniciando upload batch ({len(to_upload)} itens)...")
    print(f"{'='*60}\n")

    for idx, (png, cat_item) in enumerate(to_upload, 1):
        if cat_item:
            name = cat_item["name"]
            typ = cat_item.get("type", "classic_shirt")
            desc = cat_item.get("description") or DESC_MAP.get(typ, "")
        else:
            name = png.stem
            typ = "classic_shirt"  # fallback
            desc = DESC_MAP["classic_shirt"]

        item_type_inferred = item_type if (item_type := infer_item_type(png.stem)) else typ

        print(f"[{idx}/{len(to_upload)}] {name} ({item_type_inferred})...", end=" ")

        ok, msg = auto_upload_item(
            api, gid, uid, png, cat_item,
            price_robux=PRICE_MAP.get(item_type_inferred, 70),
            description=desc,
            item_type=item_type_inferred,
            creator_type=creator_type,
        )

        key = cat_item["name"] if cat_item else png.stem
        if ok:
            uploaded += 1
            state[key] = {"status": "uploaded", "type": item_type_inferred}
            print(f"OK: {msg[:80]}")
        else:
            errors += 1
            state[key] = {"status": "error", "msg": msg}
            print(f"ERR: {msg[:80]}")

        save_state(state)

        # Track image bytes
        try:
            budget_bytes += png.stat().st_size
        except OSError:
            pass

        # Rate limit
        if rate_limit > 0 and idx < len(to_upload):
            time.sleep(rate_limit)

        # Test-one mode
        if args.test_one:
            print("[--test-one] Parando após primeiro upload.")
            break

    # Save state
    save_state(state)

    # Report
    report = {
        "uploaded": uploaded,
        "skipped": skipped_count,
        "errors": errors,
        "budget_bytes": budget_bytes,
        "budget_max_bytes": UPLOAD_BUDGET_BYTES,
        "items_remaining": len(to_upload) - uploaded - errors,
        "catalog_total": len(catalog_items),
    }
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            f.write("\n")
        print(f"\n[OK] Relatório salvo: {REPORT_FILE}")
    except Exception as e:
        print(f"\n[WARN] Não foi possível salvar relatório: {e}")

    print(f"\n{'='*60}")
    print(f"RESUMO: enviados={uploaded}  skipped={skipped_count}  erros={errors}")
    print(f"{'='*60}")

    return 0 if errors == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Auto-submissão Roblox UGC — upload batch de PNGs para o Marketplace.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python auto_submit_roblox.py --dry-run\n"
            "  python auto_submit_roblox.py --test-one\n"
            "  python auto_submit_roblox.py\n"
            "  python auto_submit_roblox.py --items-dir ../custom_items --rate-limit 2.0\n"
        ),
    )
    ap.add_argument("--dry-run", action="store_true",
                    help="Valida configuração sem enviar nada.")
    ap.add_argument("--test-one", action="store_true",
                    help="Envia EXATAMENTE UM item e para.")
    ap.add_argument("--force", action="store_true",
                    help="Re-envia itens já marcados como enviados.")
    ap.add_argument("--unmatched-only", action="store_true",
                    help="Só processa PNGs sem correspondência no catálogo.")
    ap.add_argument("--items-dir", type=str, default=None,
                    help="Diretório customizado com PNGs (default: roblox-ugc/items/ ou assets/).")
    ap.add_argument("--max-items", type=int, default=None,
                    help=f"Número máximo de itens a enviar (default: {MAX_ITEMS_PER_RUN}).")
    ap.add_argument("--rate-limit", type=float, default=DEFAULT_RATE_LIMIT,
                    help=f"Delay entre uploads em segundos (default: {DEFAULT_RATE_LIMIT}).")
    ap.add_argument("--wait-for-key", action="store_true",
                    help="Em background: fica pollando ops/secrets.json ate uma chave VALIDA aparecer, entao submete sozinho.")
    return ap.parse_args(argv)


def main() -> int:
    args = parse_args()
    return auto_submit(args)


if __name__ == "__main__":
    raise SystemExit(main())
