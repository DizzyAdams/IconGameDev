#!/usr/bin/env python3
"""browser-use-ai: drive the post-login submission wizards to approval-ready.

This is the "automate everything possible, leave payment config manual" layer.
It drives Microsoft Partner Center (Create offer) and Roblox Creator Hub from a
PRE-AUTHENTICATED browser profile, filling every field from the existing pack
offer data (reused from submit_bedrock.build_offer) and the rendered compliance
templates. It stops BEFORE "Submit for review" so a human reviews and sets the
payment method, then clicks submit.

Explicitly NOT automated (legal / ToS / safety boundaries):
  - Account creation, login, 2FA, age verification        -> human only
  - KYC tax (W-8BEN, W-8BEN-E), IARC identity              -> human only
  - Payment method config (PayPal / Wise / Payoneer)        -> human only
  - The final "Submit for review" click                     -> human only

Any step whose label matches the safety filter is REFUSED and logged. This is
the single guard that keeps money/identity actions out of the bot.

CLIs:
  python submit/browser_use_ai.py --dry-run
        Build the step plan for all eligible packs, validate it, write
        submit/browser_plan_ms.json, and print a human review sheet. No browser.
  python submit/browser_use_ai.py --platform ms --capture-login
        Open FIREFOX for you to log in BY HAND. The bot waits and never types
        your password/2FA. Close the browser when done; the session is saved.
  python submit/browser_use_ai.py --platform ms --run --browser firefox
        Drive the wizard for Microsoft Partner Center using the saved Firefox
        profile (BROWSER_PROFILE_MS / sessions.partner_center_profile). Stops
        before submit. Cookies file also supported via BROWSER_COOKIES_MS.
  python submit/browser_use_ai.py --platform roblox --run --llm
        Same for Roblox, using the LLM decider from config.yaml.

  ONE-COMMAND FLOW (what most users want):
  python submit/browser_use_ai.py --platform ms --auto --browser firefox
        Opens the browser, YOU log in by hand (bot never types creds), press
        ENTER, and the bot IMMEDIATELY drives the wizard on the same open
        session -- no second command. Stops at the human gate and leaves the
        browser open so you configure payment + click "Submit for review".

Requires: playwright (installed). openai is used only with --llm.
"""
import os
import re
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)  # allow `import submit_bedrock` whether run from ROOT or submit/

from submit_bedrock import build_offer, list_packs, is_blocked, BLOCKED_IP  # reuse one source of truth

PLAN_FILE = os.path.join(HERE, "browser_plan_ms.json")

# --------------------------------------------------------------------------------------
# Safety boundary: the bot must NEVER touch money, identity, login, or the final submit.
# --------------------------------------------------------------------------------------
# Word-boundary anchored so e.g. "tin" does not match inside "rating".
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

# Steps whose label contains these are human-checkpoint steps (bot halts, reports).
HUMAN_GATE_RE = re.compile(r"(submit\s*for\s*review|publish|release|finish)", re.IGNORECASE)


def is_blocked_step(label):
    """True if a step must never be performed by the bot.

    The intentional human_gate ("Submit for review") step is explicitly exempt:
    it is the stop point where the bot hands control back to the human, so it is
    not "blocked" -- it is simply never executed by the bot.
    """
    if label is None:
        return False
    if label.startswith("human_gate "):
        return False
    return bool(BLOCKED_RE.search(label or ""))


def is_human_gate(label):
    """True if a step is the human approval gate (bot stops here)."""
    return bool(HUMAN_GATE_RE.search(label or ""))


# --------------------------------------------------------------------------------------
# Secrets: read only the non-secret bits we need (privacy URL). Refuse if still a
# placeholder so we never drive a wizard with bogus data.
# --------------------------------------------------------------------------------------
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


# --------------------------------------------------------------------------------------
# Step plan: one ordered, human-readable list of wizard actions per pack.
# --------------------------------------------------------------------------------------
def build_step_plan(offer, privacy_url):
    """Return ordered steps to reach approval-ready for one offer.

    `offer` is the dict from submit_bedrock.build_offer (title, description,
    searchTerms, category, ageRating, priceTierMinecoins, mcpack path).
    """
    base = offer["offerName"]
    mcpack = os.path.join(ROOT, "submission_mcpacks", base + ".mcpack")
    steps = [
        {"action": "navigate_create_offer", "target": "Partner Center -> Marketplace -> Minecraft -> Create offer",
         "value": "", "note": "Open the new-offer wizard."},
        {"action": "fill", "target": "Offer/display name (title <=60)", "value": offer["title"],
         "note": "Must match manifest header name."},
        {"action": "fill", "target": "Description (100-300 chars)", "value": offer["description"],
         "note": "First 100 chars hook the buyer; no price words / external links."},
        {"action": "fill", "target": "Search terms (5)", "value": ", ".join(offer["searchTerms"]),
         "note": "5 terms."},
        {"action": "select", "target": "Category", "value": offer["category"],
         "note": "Skin Pack | Texture Pack | World | Mashup."},
        {"action": "select", "target": "Age rating", "value": offer["ageRating"],
         "note": "E / E10+ (IARC generated at submit)."},
        {"action": "select", "target": "Price tier", "value": str(offer["priceTierMinecoins"]),
         "note": "Minecoins tier."},
        {"action": "upload", "target": "Package upload (.mcpack)", "value": mcpack,
         "note": "Wait for file chooser."},
        {"action": "declare", "target": "Product declarations",
         "value": "data collection=No, ads=No, restricted resources=No, mandatory account=No",
         "note": "Answer the 4 standard declarations."},
        {"action": "iarc", "target": "IARC questionnaire",
         "value": "violence=fantasy-only, language=No, nudity=No, drugs=No, gambling=No, fear=mild, hate=No",
         "note": "Generates the age-rating certificate automatically."},
        {"action": "fill", "target": "Privacy policy URL", "value": privacy_url,
         "note": "Required if any data is collected; packs themselves collect none."},
        # --- HUMAN GATE: bot stops here. Payment method already configured by human. ---
        {"action": "human_gate", "target": "Submit for review", "value": "",
         "note": "STOP. Human reviews, confirms payment method, and clicks Submit for review."},
    ]
    return steps


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
    return plans, len(eligible), len(blocked)


def validate_plan(steps):
    """Self-check: every step is safe to perform (no money/identity/login), and the
    plan ends on a human_gate. Returns list of problems (empty == clean)."""
    problems = []
    for i, st in enumerate(steps):
        label = "%s %s" % (st.get("action"), st.get("target"))
        if is_blocked_step(label):
            problems.append("step %d blocked by safety filter: %s" % (i, label))
    if not steps or steps[-1].get("action") != "human_gate":
        problems.append("plan does not end on a human_gate (would not halt before submit)")
    return problems


# --------------------------------------------------------------------------------------
# Runner (real browser). Only invoked with --run and a pre-authenticated profile.
# --------------------------------------------------------------------------------------
def _resolve_profile(env_name):
    val = os.environ.get(env_name) or (load_secrets() or {}).get("sessions", {}).get(
        "partner_center_profile" if "MS" in env_name else "roblox_profile", "")
    # Ignore placeholder values so we never launch a browser against a bogus dir.
    if isinstance(val, str) and val.strip().startswith("<"):
        return ""
    return val


def _resolve_cookies():
    return os.environ.get("BROWSER_COOKIES_MS") or (load_secrets() or {}).get(
        "sessions", {}).get("cookies_file", "")


LOGIN_URLS = {
    "ms": "https://partner.microsoft.com/dashboard",
    "roblox": "https://create.roblox.com/",
}


def _open_context(p, browser, profile, cookies_file):
    """Return (ctx, page) for a post-login session. Uses a saved profile if given,
    otherwise a fresh context with imported cookies. Never performs login."""
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
        if cookies_file and os.path.isfile(cookies_file):
            with open(cookies_file, encoding="utf-8") as f:
                ctx.add_cookies(json.load(f))
    return ctx, ctx.new_page()


def run_plan(plans, platform, use_llm, browser="firefox", capture_login=False):
    from playwright.sync_api import sync_playwright  # imported lazily; requires the package

    if capture_login:
        # HUMAN logs in manually in the opened browser; the bot only waits. It never
        # types credentials. On close, the session is persisted in the profile dir.
        profile = _resolve_profile("BROWSER_PROFILE_MS" if platform == "ms" else "BROWSER_PROFILE_ROBLOX")
        if not profile:
            print("REFUSED: set BROWSER_PROFILE_MS (a writable dir) for the login session.")
            return 1
        print("MANUAL LOGIN: a %s window will open. Log in BY HAND, then CLOSE the" % browser)
        print("browser. The bot will NOT type your password/2FA -- that is your action.")
        with sync_playwright() as p:
            if browser == "firefox":
                ctx = p.firefox.launch_persistent_context(profile, headless=False)
            else:
                ctx = p.chromium.launch_persistent_context(profile, headless=False)
            page = ctx.new_page()
            page.goto(LOGIN_URLS.get(platform, "https://partner.microsoft.com/"))
            print("...waiting for you to log in and close the browser...")
            ctx.close()  # blocks until the human closes the browser
        print("Session saved in profile: %s" % profile)
        print("Now run: python submit/browser_use_ai.py --platform %s --run" % platform)
        return 0

    # ONE-COMMAND FLOW: open the browser, human logs in, then the bot drives the
    # wizard on the SAME open session -- no second command needed.
    if getattr(run_plan, "_auto", False):
        return _run_auto(plans, platform, use_llm, browser)

    profile = _resolve_profile("BROWSER_PROFILE_MS" if platform == "ms" else "BROWSER_PROFILE_ROBLOX")
    cookies = _resolve_cookies()
    if not profile and not cookies:
        print("REFUSED: no authenticated session for %s." % platform)
        print("Either: (a) run --capture-login once (you log in by hand; session saved), or")
        print("(b) set BROWSER_PROFILE_MS / sessions.partner_center_profile, or")
        print("(c) export cookies to a file and set BROWSER_COOKIES_MS / sessions.cookies_file.")
        print("(d) use --auto to log in in the same run.")
        print("This tool never performs login/2FA/KYC -- that is a human action.")
        return 1

    decider = _LLMDecider() if use_llm else None
    with sync_playwright() as p:
        ctx, page = _open_context(p, browser, profile, cookies)
        page.goto(LOGIN_URLS.get(platform, "https://partner.microsoft.com/"))
        _drive_wizard(ctx, page, plans, platform, decider)
        ctx.close()
    return 0


def _drive_wizard(ctx, page, plans, platform, decider):
    """Drive every safe step of every offer plan; stop at the first human gate.

    Operates on an already-open, already-logged-in page (works for both the
    --run profile flow and the --auto live-login flow). Never executes a
    blocked step or crosses the human gate.
    """
    for plan in plans:
        print("\n=== offer: %s ===" % plan["offer"])
        for st in plan["steps"]:
            label = "%s %s" % (st["action"], st["target"])
            if is_blocked_step(label):
                print("  BLOCKED (safety): %s" % label)
                continue
            if st["action"] == "human_gate":
                print("  HUMAN GATE: %s -- bot stops. Review, set payment method, "
                      "click submit." % st["target"])
                return  # halt the whole run at the gate; human takes over
            _execute(page, st, decider)


def _run_auto(plans, platform, use_llm, browser="firefox"):
    """Open the browser, let the HUMAN log in by hand, then auto-drive the wizard."""
    from playwright.sync_api import sync_playwright  # imported lazily
    profile = _resolve_profile("BROWSER_PROFILE_MS" if platform == "ms" else "BROWSER_PROFILE_ROBLOX")
    if not profile:
        print("REFUSED: set BROWSER_PROFILE_MS (or BROWSER_PROFILE_ROBLOX) to a writable dir.")
        return 1
    print("AUTO MODE: a %s window will open at the %s login page." % (browser, platform))
    print(">> Log in BY HAND (the bot NEVER types your password/2FA/KYC).")
    print(">> When the portal is open and you are logged in, return here and press ENTER.")
    with sync_playwright() as p:
        if browser == "firefox":
            ctx = p.firefox.launch_persistent_context(profile, headless=False)
        else:
            ctx = p.chromium.launch_persistent_context(profile, headless=False)
        page = ctx.new_page()
        page.goto(LOGIN_URLS.get(platform, "https://partner.microsoft.com/"))
        try:
            input(">>> Press ENTER after you have logged in and the portal is ready... ")
        except (EOFError, KeyboardInterrupt):
            print("\nAborted. Browser closed; session saved in profile: %s" % profile)
            ctx.close()
            return 1
        decider = _LLMDecider() if use_llm else None
        _drive_wizard(ctx, page, plans, platform, decider)
        # Leave the browser open so the human configures payment + clicks Submit.
        print("\nBrowser left OPEN at the human gate. Configure the payment method and "
              "click 'Submit for review' yourself.")
        print("When done, return here and press ENTER to close the browser (optional).")
        try:
            input(">>> Press ENTER to close the browser... ")
        except (EOFError, KeyboardInterrupt):
            pass
        ctx.close()
    print("Session persisted in profile: %s" % profile)
    return 0


def _execute(page, step, decider):
    """Execute one safe step. With no LLM, falls back to a readable log (selectors on
    Partner Center are dynamic React; the LLM decider resolves them at runtime)."""
    if decider is not None:
        decider.act(page, step)
    else:
        print("  [preview] %-18s %s -> %s" % (step["action"], step["target"], step["value"] or ""))


class _LLMDecider:
    """Optional: maps a step to a Playwright action using an OpenAI-compatible LLM
    (config.yaml model + base_url). The LLM only picks a selector/action for an
    already-validated SAFE step; it can never author a blocked or human-gate step."""

    def __init__(self):
        try:
            import yaml  # config.yaml is YAML
        except ImportError:
            yaml = None
        cfg = {}
        if yaml is not None and os.path.isfile(os.path.join(ROOT, "config.yaml")):
            with open(os.path.join(ROOT, "config.yaml"), encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        model = (cfg.get("model") or {}).get("default", "gpt-4o-mini")
        base = cfg.get("providers", {}).get("openai_compatible", {}).get("base_url", "")
        self.model = model
        self.base_url = base
        key = os.environ.get("OPENAI_API_KEY") or os.environ.get("NVIDIA_API_KEY") or ""
        if not key:
            print("WARN: no OPENAI_API_KEY/NVIDIA_API_KEY set; LLM decider will degrade to preview.")
        self._key = key

    def act(self, page, step):
        # Safety double-check (defense in depth): never act on a blocked step.
        if is_blocked_step("%s %s" % (step["action"], step["target"])):
            print("  BLOCKED by LLM guard: %s" % step["target"])
            return
        # Build a small accessibility snapshot for the LLM to choose a control.
        try:
            snap = page.evaluate("() => document.body.innerText.slice(0, 4000)")
        except Exception:
            snap = ""
        prompt = (
            "You drive a browser to fill a marketplace offer form. Given the page text "
            "and the step, return ONLY a JSON action: "
            '{"kind":"fill"|"click"|"select"|"upload", "text":<visible label substring>, '
            '"value":<string>}. Step: %s. Page excerpt:\n%s'
            % (json.dumps(step), snap[:1500])
        )
        action = self._ask(prompt)
        if not action:
            print("  [preview] (llm unavailable) %s -> %s" % (step["target"], step["value"] or ""))
            return
        try:
            if action.get("kind") == "fill":
                page.get_by_text(action["text"], exact=False).fill(action["value"])
            elif action.get("kind") == "click":
                page.get_by_text(action["text"], exact=False).click()
            elif action.get("kind") == "select":
                page.get_by_text(action["text"], exact=False).select_option(action["value"])
            elif action.get("kind") == "upload":
                page.get_by_text(action["text"], exact=False).set_input_files(action["value"])
            print("  [llm] %s" % action)
        except Exception as e:
            print("  [llm-error] %s: %s" % (step["target"], e))

    def _ask(self, prompt):
        if not self._key:
            return None
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self._key, base_url=self.base_url or None)
            r = client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}],
                temperature=0, max_tokens=200)
            txt = r.choices[0].message.content or ""
            s = txt.find("{"); e = txt.rfind("}")
            if s >= 0 and e > s:
                return json.loads(txt[s:e + 1])
        except Exception as e:
            print("  [llm-call-error] %s" % e)
        return None


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="browser-use-ai submission wizard driver")
    ap.add_argument("--platform", choices=["ms", "roblox"], default="ms")
    ap.add_argument("--browser", choices=["firefox", "chromium"], default="firefox",
                    help="browser engine (default firefox)")
    ap.add_argument("--dry-run", action="store_true", help="build + validate plan, no browser")
    ap.add_argument("--run", action="store_true", help="drive wizard from a pre-auth profile")
    ap.add_argument("--capture-login", action="store_true",
                    help="open browser for MANUAL login; bot waits, never types creds")
    ap.add_argument("--auto", action="store_true",
                    help="ONE-COMMAND flow: open browser, you log in by hand, then bot "
                         "auto-drives the wizard on the same session (stops at human gate)")
    ap.add_argument("--llm", action="store_true", help="use LLM decider (config.yaml + API key)")
    args = ap.parse_args()

    ready, info = secrets_ready()
    if not ready:
        print("SECRETS NOT READY: %s" % info)
        print("Fill ops/secrets.json before generating a submission plan.")
        sys.exit(2)

    plans, n_eligible, n_blocked = build_plans(info)
    all_steps = [s for pl in plans for s in pl["steps"]]
    problems = validate_plan(all_steps)

    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump({"platform": args.platform, "plans": plans,
                   "eligible": n_eligible, "blocked": n_blocked,
                   "validation_problems": problems}, f, indent=2, ensure_ascii=False)

    print("=== browser-use-ai plan (%s) ===" % args.platform)
    print("eligible packs: %d | blocked(skipped): %d" % (n_eligible, n_blocked))
    print("steps per offer: %d | ends on human_gate: %s"
          % (len(all_steps) // max(1, len(plans)),
             all_steps[-1]["action"] == "human_gate" if all_steps else False))
    print("safety validation: %s" % ("CLEAN" if not problems else "; ".join(problems)))
    print("plan written to: %s" % PLAN_FILE)

    if args.capture_login:
        sys.exit(run_plan(plans, args.platform, args.llm, args.browser, capture_login=True))

    if args.auto:
        run_plan._auto = True
        sys.exit(run_plan(plans, args.platform, args.llm, args.browser, False))

    if args.dry_run or not args.run:
        print("\nDRY-RUN OK (no browser launched). Review the plan, then:")
        print("  1) human: configure payment method in the portal (PayPal/Wise).")
        print("  2) run with --run using a saved, logged-in browser profile.")
        print("  3) human: click 'Submit for review' after the bot halts at the gate.")
        sys.exit(0 if not problems else 1)

    sys.exit(run_plan(plans, args.platform, args.llm, args.browser, args.capture_login))


if __name__ == "__main__":
    main()
