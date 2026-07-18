#!/usr/bin/env python3
"""auto_submit_mc: batch upload .mctemplate world packs to Partner Center via Playwright.

Reads every .mctemplate in submission_mcpacks/ and drives the Partner Center
"Create offer" wizard for each one, using the same description/title templates
from submit_bedrock.py.  Stops before "Submit for review" (human gate).

CLI modes (mirror browser_use_ai.py patterns):

  # 1) DRY-RUN: build + validate plan, no browser
  python submit/auto_submit_mc.py --dry-run

  # 2) CAPTURE-LOGIN: open Firefox for MANUAL login (bot waits, never types creds)
  python submit/auto_submit_mc.py --capture-login

  # 3) RUN with saved profile: drive the wizard from a pre-authenticated session
  python submit/auto_submit_mc.py --run

  # 4) ONE-COMMAND (recommended for daily use):
  set BROWSER_PROFILE_MS=C:\\Users\\forrydev\\AppData\\Local\\firefox-ms-profile
  python submit/auto_submit_mc.py --auto

Requires: playwright (pip install playwright && playwright install firefox).
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PACKS_DIR = os.path.join(ROOT, "submission_mcpacks")
STATE_FILE = os.path.join(HERE, "state_auto_submit_mc.json")
PLAN_FILE = os.path.join(HERE, "auto_submit_mc_plan.json")

# ---------------------------------------------------------------------------
# Reuse the same blocked-IP safety filter from submit_bedrock.
# ---------------------------------------------------------------------------
BLOCKED_IP = [
    "pokemon", "naruto", "dragon-ball", "bleach", "genshin", "fnaf", "hello-kitty",
    "demon-slayer", "chainsaw-man", "one-piece", "jujutsu", "sonic", "tadc",
    "attack-on-titan", "little-nightmares", "marvel", "minecraft", "mojang",
]

DEFAULT_COUNT = 10     # number-of-worlds placeholder (cosmetic)
DEFAULT_PRICE = 310    # Minecoins tier


def is_blocked(filename):
    f = filename.lower()
    return any(term in f for term in BLOCKED_IP)


def name_from_filename(filename):
    """Strip .mctemplate (or .mcpack) extension and return the base slug."""
    low = filename.lower()
    for ext in (".mctemplate", ".mcpack"):
        if low.endswith(ext):
            return filename[:-len(ext)]
    return filename


def build_offer(filename):
    """Build offer dict for a .mctemplate world pack.

    This mirrors submit_bedrock.build_offer() but:
      - accepts .mctemplate as a valid extension
      - defaults category to "World"
      - description says "worlds" instead of "skins"
    """
    base = name_from_filename(filename)

    # Title: kebab-case -> Title Case, capped at 60 chars
    title = base.replace("-", " ").replace("_", " ").title()
    if len(title) > 60:
        title = title[:60].rsplit(" ", 1)[0]

    category = "World"
    desc_raw = (
        f"{title} brings {DEFAULT_COUNT} original Minecraft worlds "
        f"to your Bedrock game. Explore unique builds, "
        f"challenging terrain, and immersive environments "
        f"perfect for survival, adventure, or creative play."
    )
    # Clamp 100-300 chars
    desc = " ".join(desc_raw.split())[:300]
    while len(desc) < 100:
        desc = (desc + " Great value for Minecraft Bedrock players.")[:300]
    if len(desc) == 300 and not desc.endswith((".", "!", "?")):
        desc = desc.rsplit(" ", 1)[0]

    search_terms = [
        "minecraft bedrock",
        "minecraft worlds",
        base + " world",
        "world template",
        "bedrock marketplace",
    ][:5]

    return {
        "offerName": base,
        "sourcePack": filename,
        "title": title,
        "description": desc,
        "descriptionLength": len(desc),
        "searchTerms": search_terms,
        "category": category,
        "ageRating": "E10+",
        "priceTierMinecoins": DEFAULT_PRICE,
    }


def validate_offer(o):
    errs = []
    if len(o["title"]) > 60:
        errs.append("title>60")
    if not (100 <= o["descriptionLength"] <= 300):
        errs.append("desc not 100-300")
    if len(o["searchTerms"]) != 5:
        errs.append("searchTerms != 5")
    if o["priceTierMinecoins"] not in {160, 310, 440, 800, 1500, 3500, 7000}:
        errs.append("bad price tier")
    return errs


# ---------------------------------------------------------------------------
# Safety boundary copied from browser_use_ai.py – never cross into money/identity
# ---------------------------------------------------------------------------
_BLOCKED_TOKENS = (
    r"payment", r"payout", r"checkout", r"paypal", r"wise", r"payoneer",
    r"credit\s*card", r"debit\s*card", r"bank\s*account", r"bank\s*details",
    r"card\s*number", r"cvv", r"2fa", r"two[- ]factor", r"verify", r"verification",
    r"sign\s*in", r"sign\s*up", r"log\s*in", r"login", r"password",
    r"w-8ben", r"w8ben", r"tax\s*profile", r"tin", r"cnpj", r"cpf",
    r"date\s*of\s*birth", r"identity", r"kyc",
    r"submit\s*for\s*review", r"submit\s*offer", r"publish", r"release",
)
BLOCKED_RE = re.compile(r"\b(?:" + "|".join(_BLOCKED_TOKENS) + r")\b", re.IGNORECASE)
HUMAN_GATE_RE = re.compile(r"(submit\s*for\s*review|publish|release|finish)", re.IGNORECASE)


def is_blocked_step(label):
    if label is None:
        return False
    if label.startswith("human_gate "):
        return False
    return bool(BLOCKED_RE.search(label or ""))


def is_human_gate(label):
    return bool(HUMAN_GATE_RE.search(label or ""))


# ---------------------------------------------------------------------------
# Step plan builder – one ordered wizard-plan per world pack
# ---------------------------------------------------------------------------
def build_step_plan(offer, privacy_url):
    """Return ordered wizard steps for one .mctemplate offer."""
    base = offer["offerName"]
    mcpack_path = os.path.join(ROOT, "submission_mcpacks", offer["sourcePack"])

    steps = [
        {"action": "navigate_create_offer",
         "target": "Partner Center -> Marketplace -> Minecraft -> Create offer",
         "value": "", "note": "Open the new-offer wizard."},

        {"action": "fill",
         "target": "Offer/display name (title <=60)",
         "value": offer["title"],
         "note": "Must match manifest header name."},

        {"action": "fill",
         "target": "Description (100-300 chars)",
         "value": offer["description"],
         "note": "First 100 chars hook the buyer; no price words / external links."},

        {"action": "fill",
         "target": "Search terms (5)",
         "value": ", ".join(offer["searchTerms"]),
         "note": "5 terms."},

        {"action": "select",
         "target": "Category",
         "value": offer["category"],
         "note": "Skin Pack | Texture Pack | World | Mashup."},

        {"action": "select",
         "target": "Age rating",
         "value": offer["ageRating"],
         "note": "E / E10+ (IARC generated at submit)."},

        {"action": "select",
         "target": "Price tier",
         "value": str(offer["priceTierMinecoins"]),
         "note": "Minecoins tier."},

        {"action": "upload",
         "target": "Package upload (.mctemplate)",
         "value": mcpack_path,
         "note": "Wait for file chooser. Expected .mctemplate (world template)."},

        {"action": "declare",
         "target": "Product declarations",
         "value": "data collection=No, ads=No, restricted resources=No, mandatory account=No",
         "note": "Answer the 4 standard declarations."},

        {"action": "iarc",
         "target": "IARC questionnaire",
         "value": "violence=fantasy-only, language=No, nudity=No, drugs=No, gambling=No, fear=mild, hate=No",
         "note": "Generates the age-rating certificate automatically."},

        {"action": "fill",
         "target": "Privacy policy URL",
         "value": privacy_url,
         "note": "Required if any data is collected; packs themselves collect none."},

        # HUMAN GATE – bot stops here
        {"action": "human_gate", "target": "Submit for review", "value": "",
         "note": "STOP. Human reviews, confirms payment method, and clicks Submit for review."},
    ]
    return steps


def list_packs():
    """List .mctemplate files in submission_mcpacks/, sorted."""
    if not os.path.isdir(PACKS_DIR):
        return []
    return sorted(
        f for f in os.listdir(PACKS_DIR)
        if f.lower().endswith(".mctemplate")
    )


# ---------------------------------------------------------------------------
# Secrets helper – reads only non-sensitive bits (privacy URL)
# ---------------------------------------------------------------------------
def load_secrets():
    path = os.path.join(ROOT, "ops", "secrets.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def secrets_ready():
    s = load_secrets()
    if not s:
        return False, "ops/secrets.json missing (cp ops/secrets.example.json ops/secrets.json)"
    privacy = (s.get("domain", {}) or {}).get("privacy_url", "")
    if not privacy or privacy.startswith("<"):
        return False, "domain.privacy_url still a placeholder in ops/secrets.json"
    return True, privacy


def build_plans(privacy_url):
    packs = list_packs()
    eligible = [f for f in packs if not is_blocked(f)]
    blocked = [f for f in packs if is_blocked(f)]
    plans = []
    for f in eligible:
        offer = build_offer(f)
        plans.append({
            "offer": offer["offerName"],
            "title": offer["title"],
            "category": offer["category"],
            "steps": build_step_plan(offer, privacy_url),
        })
    return plans, eligible, blocked


def validate_plan(steps):
    problems = []
    for i, st in enumerate(steps):
        label = f"{st.get('action')} {st.get('target')}"
        if is_blocked_step(label):
            problems.append(f"step {i} blocked by safety filter: {label}")
    if not steps or steps[-1].get("action") != "human_gate":
        problems.append("plan does not end on a human_gate (would not halt before submit)")
    return problems


# ---------------------------------------------------------------------------
# State persistence (idempotent skip)
# ---------------------------------------------------------------------------
def load_state():
    if not os.path.isfile(STATE_FILE):
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


# ---------------------------------------------------------------------------
# Playwright runner
# ---------------------------------------------------------------------------
LOGIN_URL = "https://partner.microsoft.com/dashboard"
PRIVACY_URL_DEFAULT = "https://iconminemods.dpdns.org/privacy"


def _resolve_profile():
    """Check BROWSER_PROFILE_MS env var, then sessions.partner_center_profile in secrets."""
    val = os.environ.get("BROWSER_PROFILE_MS") or ""
    if not val:
        s = load_secrets()
        if s:
            val = (s.get("sessions") or {}).get("partner_center_profile", "")
    # Ignore placeholders
    if isinstance(val, str) and val.strip().startswith("<"):
        return ""
    return val


def _resolve_cookies():
    val = os.environ.get("BROWSER_COOKIES_MS") or ""
    if not val:
        s = load_secrets()
        if s:
            val = (s.get("sessions") or {}).get("cookies_file", "")
    return val


def run_capture_login(browser="firefox"):
    """Open browser for MANUAL login. Bot waits, never types creds."""
    profile = _resolve_profile()
    if not profile:
        print("REFUSED: set BROWSER_PROFILE_MS (a writable Firefox profile dir).")
        return 1
    from playwright.sync_api import sync_playwright
    print(f"MANUAL LOGIN: a {browser} window will open. Log in BY HAND, then CLOSE")
    print("the browser. The bot will NOT type your password/2FA.")
    with sync_playwright() as p:
        if browser == "firefox":
            ctx = p.firefox.launch_persistent_context(profile, headless=False)
        else:
            ctx = p.chromium.launch_persistent_context(profile, headless=False)
        page = ctx.new_page()
        page.goto(LOGIN_URL)
        print("...waiting for you to log in and close the browser...")
        ctx.close()
    print(f"Session saved in profile: {profile}")
    print("Now run: python submit/auto_submit_mc.py --run")
    return 0


def run_auto(plans, browser="firefox"):
    """ONE-COMMAND flow: open browser, human logs in, bot drives wizard."""
    profile = _resolve_profile()
    if not profile:
        print("REFUSED: set BROWSER_PROFILE_MS to a writable Firefox profile dir.")
        return 1
    from playwright.sync_api import sync_playwright
    print(f"AUTO MODE: a {browser} window will open at the Partner Center login page.")
    print(">> Log in BY HAND (the bot NEVER types your password/2FA/KYC).")
    print(">> When the portal is open and you are logged in, return here and press ENTER.")
    with sync_playwright() as p:
        if browser == "firefox":
            ctx = p.firefox.launch_persistent_context(profile, headless=False)
        else:
            ctx = p.chromium.launch_persistent_context(profile, headless=False)
        page = ctx.new_page()
        page.goto(LOGIN_URL)
        try:
            input(">>> Press ENTER after you have logged in and the portal is ready... ")
        except (EOFError, KeyboardInterrupt):
            print("\nAborted. Browser closed; session saved.")
            ctx.close()
            return 1
        _drive_wizard(ctx, page, plans)
        print("\nBrowser left OPEN at the human gate. Configure the payment method and")
        print("click 'Submit for review' yourself.")
        print("When done, return here and press ENTER to close the browser.")
        try:
            input(">>> Press ENTER to close the browser... ")
        except (EOFError, KeyboardInterrupt):
            pass
        ctx.close()
    print("Session persisted.")
    return 0


def run_with_profile(plans, browser="firefox"):
    """Drive wizard from a previously captured (logged-in) profile."""
    profile = _resolve_profile()
    cookies = _resolve_cookies()
    if not profile and not cookies:
        print("REFUSED: no authenticated session.")
        print("Run --capture-login first (you log in by hand; session saved),")
        print("or set BROWSER_PROFILE_MS / sessions.partner_center_profile.")
        return 1
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        if profile:
            if browser == "firefox":
                ctx = p.firefox.launch_persistent_context(profile, headless=False)
            else:
                ctx = p.chromium.launch_persistent_context(profile, headless=False)
        else:
            if browser == "firefox":
                ctx = p.firefox.launch(headless=False)
            else:
                ctx = p.chromium.launch(headless=False)
            if cookies and os.path.isfile(cookies):
                with open(cookies, encoding="utf-8") as f:
                    ctx.add_cookies(json.load(f))
        page = ctx.new_page()
        page.goto(LOGIN_URL)
        _drive_wizard(ctx, page, plans)
        ctx.close()
    return 0


def _drive_wizard(ctx, page, plans):
    """Drive every safe step of every world-pack plan; stop at first human gate."""
    state = load_state()
    for plan in plans:
        name = plan["offer"]
        prev = state.get(name)
        if prev and prev.get("status") == "done":
            print(f"\n=== offer: {name} ===  (idempotent skip – already processed)")
            continue

        print(f"\n=== offer: {name} ===")
        for st in plan["steps"]:
            label = f"{st['action']} {st['target']}"
            if is_blocked_step(label):
                print(f"  BLOCKED (safety): {label}")
                continue
            if st["action"] == "human_gate":
                print(f"  HUMAN GATE: {st['target']} -- bot stops. Review, set payment method, "
                      "click submit.")
                state[name] = {"status": "done", "title": plan["title"]}
                save_state(state)
                return  # halt the whole run at the gate; human takes over for this pack
            _execute(page, st)

    # If we finish all packs without hitting a gate (shouldn't happen), save state
    for plan in plans:
        name = plan["offer"]
        if name not in state:
            state[name] = {"status": "done", "title": plan["title"]}
    save_state(state)


def _execute(page, step):
    """Execute one wizard step using Playwright locators.

    For dynamic Partner Center React forms we use a best-effort heuristic:
      - fill:   page.get_by_label() or get_by_placeholder()
      - select: page.get_by_label().select_option()
      - click:  page.get_by_role() or get_by_text()
      - upload: page.get_by_label().set_input_files()
    When the heuristic fails, the user can retry with --llm (via browser_use_ai.py)
    or fill the field manually.
    """
    action = step["action"]
    target = step["target"]
    value = step["value"]
    print(f"  [{action:>20}] {target} -> {value[:60] if value else ''}")

    if action in ("navigate_create_offer", "human_gate"):
        return  # these are logical steps, not UI actions
    if action == "iarc":
        print("    (IARC questionnaire – answer manually or via LLM decider)")
        return

    try:
        if action == "fill":
            # Try label first, then placeholder, then generic input
            try:
                page.get_by_label(target, exact=False).fill(value)
            except Exception:
                try:
                    page.get_by_placeholder(target, exact=False).fill(value)
                except Exception:
                    page.locator("input:visible, textarea:visible").first.fill(value)
        elif action == "select":
            try:
                page.get_by_label(target, exact=False).select_option(value)
            except Exception:
                page.locator(f"select:visible").select_option(value)
        elif action == "upload":
            # File chooser: the upload step typically has a file input
            page.locator("input[type=file]:visible").set_input_files(value)
        elif action == "declare":
            # Product declarations: auto-click all "No" radio buttons
            no_buttons = page.locator("input[type=radio][value='No']:visible, "
                                      "label:has-text('No') input[type=radio]:visible")
            count = no_buttons.count()
            if count > 0:
                for i in range(count):
                    no_buttons.nth(i).click()
                print(f"    clicked {count} 'No' declaration(s)")
            else:
                print("    (no 'No' radio buttons found – may need manual interaction)")
        else:
            print(f"    (unknown action: {action})")
    except Exception as e:
        print(f"    [warn] {e}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="auto_submit_mc: batch upload .mctemplate world packs to Partner Center",
    )
    ap.add_argument("--dry-run", action="store_true",
                    help="build + validate plan, no browser")
    ap.add_argument("--run", action="store_true",
                    help="drive wizard from a saved, logged-in profile")
    ap.add_argument("--capture-login", action="store_true",
                    help="open browser for MANUAL login; bot waits, never types creds")
    ap.add_argument("--auto", action="store_true",
                    help="ONE-COMMAND: open browser, you log in by hand, bot drives wizard")
    ap.add_argument("--browser", choices=["firefox", "chromium"], default="firefox",
                    help="browser engine (default firefox)")
    args = ap.parse_args()

    # --- Secrets check ---
    ready, info = secrets_ready()
    privacy_url = info if ready else PRIVACY_URL_DEFAULT
    if not ready:
        print(f"WARN: {info}")
        print(f"Using fallback privacy URL: {privacy_url}")
        print("Set domain.privacy_url in ops/secrets.json to suppress this warning.\n")

    # --- Build plans ---
    plans, eligible_list, blocked_list = build_plans(privacy_url)
    all_steps = [s for pl in plans for s in pl["steps"]]
    problems = validate_plan(all_steps)

    # Write plan file
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "platform": "ms",
            "offer_count": len(plans),
            "blocked_count": len(blocked_list),
            "plans": plans,
            "validation_problems": problems,
        }, f, indent=2, ensure_ascii=False)

    print("=== auto_submit_mc plan (.mctemplate worlds) ===")
    print(f"eligible packs: {len(plans)} | blocked (skipped): {len(blocked_list)}")
    if blocked_list:
        print(f"  blocked files: {', '.join(blocked_list)}")
    print(f"steps per offer: {len(all_steps) // max(1, len(plans))} | "
          f"ends on human_gate: {all_steps[-1]['action'] == 'human_gate' if all_steps else 'N/A'}")
    print(f"safety validation: {'CLEAN' if not problems else '; '.join(problems)}")
    print(f"plan written to: {PLAN_FILE}")

    if plans:
        print("\n--- sample: first eligible pack ---")
        p0 = plans[0]
        print(f"  file: {eligible_list[0]}")
        print(f"  title: {p0['title']}")
        print(f"  category: {p0['category']}")
        print(f"  steps: {len(p0['steps'])} (last: {p0['steps'][-1]['action']})")

    if args.capture_login:
        return run_capture_login(args.browser)

    if args.auto:
        return run_auto(plans, args.browser)

    if args.dry_run or not args.run:
        print("\nDRY-RUN OK (no browser launched). To submit for real:")
        print("  1) set BROWSER_PROFILE_MS to a writable Firefox profile dir")
        print("  2) python submit/auto_submit_mc.py --capture-login")
        print("     (you log in by hand; bot waits)")
        print("  3) python submit/auto_submit_mc.py --run")
        print("     (bot drives the wizard for each pack; stops at human gate)")
        print("  OR one-command: python submit/auto_submit_mc.py --auto")
        return 0 if not problems else 1

    return run_with_profile(plans, args.browser)


if __name__ == "__main__":
    sys.exit(main())
