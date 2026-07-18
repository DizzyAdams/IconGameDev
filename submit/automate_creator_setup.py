import os
import sys
import time
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SECRETS_FILE = ROOT / "ops" / "secrets.json"

def update_secrets(api_key, user_id, experience_id):
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
    data["roblox"]["group_id"] = user_id
    data["roblox"]["experience_id"] = experience_id

    with open(SECRETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[OK] secrets.json updated with api_key, user_id: {user_id}, experience_id: {experience_id}")

def main():
    profile_path = r"C:\Users\forrydev\AppData\Roaming\Mozilla\Firefox\Profiles\0cv6qgha.default-release"
    print("=" * 70)
    print(" AUTOMATED CREATOR HUB & API KEY GENERATOR")
    print("=" * 70)
    print("IMPORTANT: Please make sure Firefox is CLOSED before running this script.")
    print("Press ENTER once Firefox is closed...")
    input()
    
    with sync_playwright() as p:
        try:
            print("Launching Firefox with your logged-in profile...")
            # We run in headful mode so the user can see it and we can debug easily
            context = p.firefox.launch_persistent_context(profile_path, headless=False)
            page = context.new_page()
            
            print("Navigating to Roblox Creator creations...")
            page.goto("https://create.roblox.com/dashboard/creations")
            page.wait_for_load_state("networkidle")
            
            # Check if logged in
            if "login" in page.url:
                print("[ERROR] You are not logged in to Roblox on this Firefox profile.")
                context.close()
                return
                
            print("[OK] Logged in successfully.")
            
            # Check if there is an experience. If not, create one
            # The creations URL is /dashboard/creations
            # Let's search for any experiences
            time.sleep(3)
            experience_id = None
            
            # Try to find an existing experience URL like /dashboard/creations/experiences/(\d+)/overview
            content = page.content()
            m = re.search(r"experiences/(\d+)", content)
            if m:
                experience_id = m.group(1)
                print(f"[INFO] Found existing experience ID: {experience_id}")
            else:
                print("[INFO] No existing experience found. Creating a new placeholder experience...")
                # Click "Create Experience" or navigate to creation template if we can
                # In Creator Hub, clicking create experience usually prompts to download Roblox Studio.
                # However, every Roblox account automatically comes with a default place!
                # Let's check develop.roblox.com to find the default place if not shown on dashboard.
                page.goto("https://www.roblox.com/home")
                page.wait_for_load_state("networkidle")
                # Every user has a default place. Let's try to query the user's creations via API inside the browser context
                user_id = page.evaluate("() => Roblox.CurrentUser.userId")
                print(f"[INFO] Current User ID: {user_id}")
                
                # Fetch universes via web API
                response = page.evaluate(f"""
                    fetch("https://develop.roblox.com/v1/users/{user_id}/universes?limit=10")
                        .then(r => r.json())
                """)
                universes = response.get("data", [])
                if universes:
                    experience_id = universes[0].get("id")
                    print(f"[INFO] Found default experience via API: {experience_id}")
                else:
                    print("[WARN] No experience found via API. Creating one is required for Game Passes.")
                    experience_id = "0"
            
            if not experience_id:
                experience_id = "0"
                
            # Get User ID
            page.goto("https://www.roblox.com/home")
            page.wait_for_load_state("networkidle")
            user_id = str(page.evaluate("() => Roblox.CurrentUser.userId"))
            print(f"[INFO] User ID: {user_id}")
            
            # Navigate to Credentials page to generate API Key
            print("Navigating to Credentials page...")
            page.goto("https://create.roblox.com/dashboard/credentials?tab=api-keys")
            time.sleep(4)
            
            # Check if there is already an API key named IconHub_AutoSubmit
            # If so, we might want to delete it or regenerate it, but let's just click "Create API Key"
            print("Creating new API Key...")
            page.locator("button:has-text('Create API Key'), button:has-text('Create Key')").first.click()
            time.sleep(2)
            
            # Fill name
            page.locator("input[placeholder='Enter name...'], input[id*='name']").first.fill("IconHub_AutoSubmit")
            
            # Add API Access Permissions
            # Click "Add API Access Permission" dropdown
            page.locator("button:has-text('Select API System')").first.click()
            time.sleep(1)
            page.locator("text=Asset API").first.click()
            time.sleep(1)
            
            # Click "Add Action" and select Read, Write
            page.locator("button:has-text('Add Action')").first.click()
            time.sleep(1)
            # Select write
            page.locator("text=Write").first.click()
            time.sleep(1)
            page.locator("button:has-text('Add Action')").first.click()
            time.sleep(1)
            page.locator("text=Read").first.click()
            time.sleep(1)
            
            # Scroll down to IP Access Limits
            # Click "Add IP Address"
            page.locator("input[placeholder='Enter IP Address...']").first.fill("0.0.0.0/0")
            page.locator("button:has-text('Add IP')").first.click()
            time.sleep(1)
            
            # Select Universe/Experience scope if required
            # By default it scopes to the creator.
            
            # Click "Save & Generate Key"
            page.locator("button:has-text('Save & Generate Key'), button:has-text('Create')").last.click()
            print("Generating key...")
            time.sleep(4)
            
            # Copy the API key from the modal
            # It usually shows a modal with the key and a copy button
            api_key = page.locator("div[role='dialog'] input, div.modal-body input").first.input_value()
            print(f"[SUCCESS] Generated API Key: {api_key[:10]}...")
            
            update_secrets(api_key, user_id, experience_id)
            
            print("Done! Closing browser.")
            context.close()
            
        except Exception as e:
            print("[ERROR] Automation failed:", e)
            print("You can complete it manually in the opened browser window.")
            # Keep browser open for manual fallback
            try:
                input("Press ENTER to close the browser...")
                context.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
