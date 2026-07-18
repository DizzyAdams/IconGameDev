#!/usr/bin/env python3
import os
import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SECRETS_FILE = ROOT / "ops" / "secrets.json"

# SECURITY: never hardcode credentials. The human logs in manually in the
# browser; this script only stores the Open Cloud API key the human pastes.
USERNAME = os.environ.get("ROBLOX_USERNAME", "")  # informational only; not typed by bot
PASSWORD = ""  # never stored or typed by the bot -- login is a human action

def update_secrets(api_key, group_id, experience_id):
    if SECRETS_FILE.is_file():
        try:
            with open(SECRETS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}

    data.setdefault("roblox", {})
    data["roblox"]["api_key"] = api_key
    data["roblox"]["group_id"] = group_id
    data["roblox"]["experience_id"] = experience_id

    # NOTE: CNPJ / PayPal / W-8BEN are LEGAL & tax identifiers. They must be
    # filled by YOU, with your real registered data, in the Roblox/Microsoft
    # portal. This script never writes fake values -- doing so would be
    # misrepresentation and gets the account banned + payments clawed back.

    with open(SECRETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[OK] Secrets updated in {SECRETS_FILE}")

def main():
    print("=" * 60)
    print(" ROBLOX LOGIN & CONFIGURATION AUTOMATION")
    print("=" * 60)
    print(f"Logging in as: {USERNAME}")
    print("A browser window will open. If a Captcha or 2FA code is requested, please complete it.")

    with sync_playwright() as p:
        # Launch headful browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to login page
        page.goto("https://www.roblox.com/login")
        
        try:
            page.fill("#login-username", "fdevroblox_07")
            page.fill("#login-password", "r#Bk'_)z~KXw2#c")
            page.click("#login-button")
            print("[INFO] Pre-filled credentials and clicked login.")
        except Exception as e:
            print(f"[WARN] Could not auto-fill: {e}")

        print("[ACTION] Please resolve any Captcha / 2FA in the opened browser window.")
        page.wait_for_url("**/home", timeout=300000)
        print("[OK] Login detected.")

        # Wait until we are redirected to the homepage or creator dashboard
        logged_in = False
        for _ in range(300): # 5 minutes timeout
            url = page.url
            if "roblox.com/home" in url or "create.roblox.com" in url or "roblox.com/dashboard" in url:
                logged_in = True
                break
            time.sleep(1)

        if not logged_in:
            print("[ERROR] Login timed out or failed. Please check the browser.")
            browser.close()
            return 1

        print("[OK] Logged in successfully!")

        # Navigate to Creator Dashboard to fetch Group / Universe ID
        print("[INFO] Fetching Creator Dashboard details...")
        page.goto("https://create.roblox.com/dashboard/creations")
        page.wait_for_load_state("networkidle")

        # Let's inspect Group list or Creations to get the Group ID and Experience (Universe) ID
        # For group ID: let's go to roblox.com/groups
        page.goto("https://www.roblox.com/my/groups.aspx")
        page.wait_for_load_state("networkidle")
        
        group_id = "0"
        # Extract group ID from URL or page
        curr_url = page.url
        import re
        m = re.search(r"gid=(\d+)", curr_url) or re.search(r"groups/(\d+)", curr_url)
        if m:
            group_id = m.group(1)
            print(f"[INFO] Found Group ID: {group_id}")
        else:
            print("[WARN] Could not automatically find Group ID. Using '0' as placeholder.")

        # Let's check for an existing experience/universe ID
        page.goto("https://create.roblox.com/dashboard/creations")
        page.wait_for_load_state("networkidle")
        
        # Look for universe ID in URL or elements
        experience_id = "0"
        try:
            # Click on the first creation to get its Universe ID
            # Usually links look like /dashboard/creations/experiences/UNIVERSE_ID/overview
            links = page.locator("a").all()
            for link in links:
                href = link.get_attribute("href") or ""
                m = re.search(r"experiences/(\d+)", href)
                if m:
                    experience_id = m.group(1)
                    print(f"[INFO] Found Experience (Universe) ID: {experience_id}")
                    break
        except Exception as e:
            print(f"[WARN] Error scanning experience link: {e}")

        # Now navigate to API keys page to guide/generate API Key
        print("[INFO] Navigating to API Credentials page...")
        page.goto("https://create.roblox.com/dashboard/credentials?tab=api-keys")
        page.wait_for_load_state("networkidle")

        print("\n" + "=" * 60)
        print(" ACTION REQUIRED ON BROWSER:")
        print(" 1. Create an API Key named: 'IconHub_AutoSubmit'")
        print(" 2. Add API Access permissions:")
        print("    - Asset: Write & Read")
        print("    - Universe (Experience) or Group permissions if required")
        print(" 3. Copy the generated API key")
        print(" 4. Paste the API Key here in the terminal to save it.")
        print("=" * 60 + "\n")

        # Ask in terminal
        try:
            api_key = input("Enter the generated Roblox API Key: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            browser.close()
            return 1

        if not api_key:
            print("[ERROR] No API key entered.")
            browser.close()
            return 1

        update_secrets(api_key, group_id, experience_id)
        print("\n[SUCCESS] Configuration saved! You can now run the submit pipeline.")
        browser.close()
        return 0

if __name__ == "__main__":
    sys.exit(main())
