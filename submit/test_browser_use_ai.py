#!/usr/bin/env python3
"""Offline self-check for submit/browser_use_ai.py.

No browser, no network, no secrets. Verifies the safety boundary and the plan
generator. Run:  python submit/test_browser_use_ai.py
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import browser_use_ai as b

failures = []


def check(name, cond):
    print(("[OK]   " if cond else "[FAIL] ") + name)
    if not cond:
        failures.append(name)


# --- 1. Safety filter blocks money/identity/login steps ---
check("blocks payment step", b.is_blocked_step("fill payment method paypal"))
check("blocks checkout step", b.is_blocked_step("click checkout"))
check("blocks 2fa step", b.is_blocked_step("enter 2fa code"))
check("blocks login step", b.is_blocked_step("click sign in"))
check("blocks w-8ben step", b.is_blocked_step("fill w-8ben tax profile"))
check("blocks submit-for-review step", b.is_blocked_step("click submit for review"))
check("allows safe fill title step", not b.is_blocked_step("fill Offer display name"))
check("allows safe iarc step", not b.is_blocked_step("iarc IARC questionnaire"))

# --- 2. Human gate detection ---
check("detects human gate", b.is_human_gate("human_gate Submit for review"))

# --- 3. Plan generation ends on a human_gate and is clean ---
sample_offer = {
    "offerName": "neon-skin-pack",
    "title": "Neon Skin Pack",
    "description": "Neon Skin Pack brings 10 amazing skins to your Minecraft Bedrock world!",
    "searchTerms": ["minecraft skins", "neon skin", "bedrock skins", "skin pack", "minecraft bedrock"],
    "category": "Skin Pack",
    "ageRating": "E",
    "priceTierMinecoins": 310,
}
steps = b.build_step_plan(sample_offer, "https://iconminemods.dpdns.org/privacy")
problems = b.validate_plan(steps)
check("plan has no safety problems", problems == [])
check("plan ends on human_gate", steps[-1]["action"] == "human_gate")
check("plan never contains a payment action",
      not any(b.is_blocked_step("%s %s" % (s["action"], s["target"])) for s in steps))

# --- 4. A plan with an injected payment step is caught ---
evil = steps[:-1] + [{"action": "fill", "target": "Payout method paypal", "value": "x@paypal.com"}]
check("validate_plan catches injected payment step",
      any("blocked by safety filter" in p for p in b.validate_plan(evil)))

# --- 5. secrets_ready guard logic ---
ready, info = b.secrets_ready()
check("secrets_ready returns a (bool, str) tuple", isinstance(ready, bool) and isinstance(info, str))
# A placeholder privacy URL must be refused.
fake = {"domain": {"privacy_url": "<URL>"}}
orig = b.load_secrets
b.load_secrets = lambda: fake
check("secrets_ready refuses placeholder privacy_url", b.secrets_ready()[0] is False)
b.load_secrets = orig  # restore

# --- 6b. run_plan refuses without an authenticated session (no browser launched) ---
rc = b.run_plan([], "ms", False, "firefox", False)
check("run_plan refuses without session (no launch)", rc == 1)

# --- 6. Real packs (if present) build without error and stay clean ---
if os.path.isdir(os.path.join(b.ROOT, "submission_mcpacks")):
    plans, n_elig, n_block = b.build_plans("https://iconminemods.dpdns.org/privacy")
    all_steps = [s for pl in plans for s in pl["steps"]]
    check("real build_plans produces plans", n_elig >= 0)
    check("real plans pass validation", b.validate_plan(all_steps) == [])

print("\n" + ("ALL CHECKS PASSED (%d)" % (len(failures) == 0 and 1)) if not failures
      else "FAILURES: %s" % json.dumps(failures, ensure_ascii=False))
sys.exit(1 if failures else 0)
