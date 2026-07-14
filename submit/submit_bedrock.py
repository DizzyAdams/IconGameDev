#!/usr/bin/env python3
"""Microsoft Partner Center / Microsoft Store submission for Minecraft Bedrock Marketplace.

Stdlib + urllib only. Best-effort Microsoft Store Submission API client.

Reads packs from submission_mcpacks/ (os.listdir), one offer per .mcpack, building
offer payloads that reuse the field format in compliance/templates/store-listing.md
(Title <=60, Description 100-300, 5 Search terms, Category, Age rating, Price tier).

CLI:
  python submit_bedrock.py --dry-run   -> validate config + print sample payloads for
                                          first 3 eligible packs, exit 0. NO network.
  python submit_bedrock.py             -> real submit (needs MS_* env creds).
                                          Idempotent by pack name.

Hard compliance rule: skip any pack whose filename contains a blocked IP term
(reuse list below). Prints skipped count.

TODO(human): confirm the exact Microsoft Store / Minecraft Partner Center submission
endpoint and request schema. The URIs below are best-effort placeholders.
"""
import os
import sys
import json
import argparse
import urllib.parse
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PACKS_DIR = os.path.join(ROOT, "submission_mcpacks")
STATE_FILE = os.path.join(HERE, "state_bedrock.json")

# Blocked IP terms (reuse from compliance rules).
BLOCKED_IP = [
    "pokemon", "naruto", "dragon-ball", "bleach", "genshin", "fnaf", "hello-kitty",
    "demon-slayer", "chainsaw-man", "one-piece", "jujutsu", "sonic", "tadc",
    "attack-on-titan", "little-nightmares", "marvel", "minecraft", "mojang",
]

# Best-effort Microsoft identity + Store Submission API (TODO: verify).
TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
SUBMIT_URL = "https://manage.devcenter.microsoft.com/v1.0/my/inappproducts"
SCOPE = "https://manage.devcenter.microsoft.com/.default"

PRICE_TIERS = {160, 310, 440, 800, 1500, 3500, 7000}
DEFAULT_PRICE = 310
DEFAULT_COUNT = 10


def is_blocked(filename):
    f = filename.lower()
    return any(term in f for term in BLOCKED_IP)


def infer_category(base):
    b = base.lower()
    if "mashup" in b:
        return "Mashup"
    if "world" in b:
        return "World"
    if "texture" in b:
        return "Texture Pack"
    return "Skin Pack"


def noun_for(category):
    return {
        "Skin Pack": "skins",
        "Texture Pack": "textures",
        "World": "worlds",
        "Mashup": "mashups",
    }.get(category, "skins")


def clamp_description(text):
    text = " ".join(text.split())
    text = text[:300]
    while len(text) < 100:
        text = (text + " Great value for Minecraft Bedrock players.")[:300]
    if len(text) == 300 and not text.endswith((".", "!", "?")):
        text = text.rsplit(" ", 1)[0]
    return text


def search_terms(title):
    base = title.lower().replace("  ", " ")
    return [
        "minecraft bedrock",
        "minecraft skins",
        base + " skins",
        "skin pack",
        "bedrock marketplace",
    ][:5]


def build_offer(filename):
    base = filename[:-len(".mcpack")] if filename.lower().endswith(".mcpack") else filename
    title = base.replace("-", " ").replace("_", " ").title()
    if len(title) > 60:
        title = title[:60].rsplit(" ", 1)[0]
    category = infer_category(base)
    desc = clamp_description(
        "%s brings %d original %s to your Minecraft Bedrock world. "
        "Crisp original art, instant in-game apply, perfect for builders and explorers."
        % (title, DEFAULT_COUNT, noun_for(category))
    )
    return {
        "offerName": base,
        "sourcePack": filename,
        "title": title,
        "description": desc,
        "descriptionLength": len(desc),
        "searchTerms": search_terms(title),
        "category": category,
        "ageRating": "E10+",
        "priceTierMinecoins": DEFAULT_PRICE,
        "partnerId": os.environ.get("MS_PARTNER_ID", ""),
    }


def validate_offer(o):
    errs = []
    if len(o["title"]) > 60:
        errs.append("title>60")
    if not (100 <= o["descriptionLength"] <= 300):
        errs.append("desc not 100-300")
    if len(o["searchTerms"]) != 5:
        errs.append("searchTerms != 5")
    if o["priceTierMinecoins"] not in PRICE_TIERS:
        errs.append("bad price tier")
    return errs


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


def get_token():
    tenant = os.environ.get("MS_TENANT_ID")
    cid = os.environ.get("MS_CLIENT_ID")
    secret = os.environ.get("MS_CLIENT_SECRET")
    if not (tenant and cid and secret):
        return None
    url = TOKEN_URL.format(tenant=tenant)
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": secret,
        "scope": SCOPE,
    }).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()).get("access_token")
    except Exception as e:
        print("token error: %s" % e)
        return None


def submit_offer(token, offer):
    partner = os.environ.get("MS_PARTNER_ID", "")
    payload = {
        "partnerId": partner,
        "offerName": offer["offerName"],
        "listing": {
            "title": offer["title"],
            "description": offer["description"],
            "searchTerms": offer["searchTerms"],
            "category": offer["category"],
            "ageRating": offer["ageRating"],
            "priceTierMinecoins": offer["priceTierMinecoins"],
        },
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        SUBMIT_URL, data=data,
        headers={
            "Authorization": "Bearer %s" % token,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return (200 <= r.status < 300, "HTTP %d" % r.status)
    except urllib.error.HTTPError as e:
        return (False, "HTTP %d" % e.code)
    except Exception as e:
        return (False, str(e))


def list_packs():
    if not os.path.isdir(PACKS_DIR):
        return []
    return sorted(f for f in os.listdir(PACKS_DIR) if f.lower().endswith(".mcpack"))


def dry_run():
    packs = list_packs()
    blocked = [f for f in packs if is_blocked(f)]
    eligible = [f for f in packs if not is_blocked(f)]
    print("=== Bedrock Marketplace dry-run ===")
    print("packs found:        %d" % len(packs))
    print("eligible:           %d" % len(eligible))
    print("skipped (blocked):  %d" % len(blocked))
    has_creds = bool(os.environ.get("MS_TENANT_ID")
                     and os.environ.get("MS_CLIENT_ID")
                     and os.environ.get("MS_CLIENT_SECRET")
                     and os.environ.get("MS_PARTNER_ID"))
    print("creds present:      %s" % has_creds)
    print("\n--- sample payloads (first 3 eligible) ---")
    for f in eligible[:3]:
        o = build_offer(f)
        errs = validate_offer(o)
        print("\n# %s  (validation: %s)" % (f, "OK" if not errs else ",".join(errs)))
        print(json.dumps(o, indent=2))
    sys.exit(0)


def real_run():
    packs = list_packs()
    blocked = [f for f in packs if is_blocked(f)]
    eligible = [f for f in packs if not is_blocked(f)]
    token = get_token()
    state = load_state()
    submitted = skipped = errors = 0

    print("=== Bedrock Marketplace real submit ===")
    print("eligible: %d | blocked(skipped): %d" % (len(eligible), len(blocked)))

    if token is None:
        print("MS_* credentials missing -> skipping network (no submits).")

    for f in eligible:
        o = build_offer(f)
        name = o["offerName"]
        prev = state.get(name)
        if prev and prev.get("status") == "submitted":
            print("idempotent skip: %s" % name)
            skipped += 1
            continue
        if token is None:
            print("skip (no creds): %s" % name)
            skipped += 1
            continue
        ok, msg = submit_offer(token, o)
        if ok:
            submitted += 1
            state[name] = {"status": "submitted", "title": o["title"]}
            print("submitted: %s (%s)" % (name, msg))
        else:
            errors += 1
            state[name] = {"status": "error", "msg": msg}
            print("ERROR %s: %s" % (name, msg))
    save_state(state)
    print("\nSUMMARY: submitted=%d skipped=%d errors=%d blocked=%d"
          % (submitted, skipped, errors, len(blocked)))
    sys.exit(0 if errors == 0 else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.dry_run:
        dry_run()
    else:
        real_run()


if __name__ == "__main__":
    main()

