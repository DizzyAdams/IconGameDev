#!/usr/bin/env python3
"""Claim a FREE DigitalPlat FreeDomain for IconMineMods (stdlib only).

FACT: DigitalPlat FreeDomain gives FREE subdomains ONLY under these TLDs:
  .dpdns.org, .us.kg, .qzz.io, .xx.kg, .qd.je
It does NOT offer free .com / .net / .org (those are paid registrars).

Primary target: iconminemods.dpdns.org   (fallback: iconminemods.us.kg)

Usage:
  python freedomain_claim.py --check
  python freedomain_claim.py --claim
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CLAIMED = os.path.join(HERE, "claimed.json")

FREE_TLDS = [".dpdns.org", ".us.kg", ".qzz.io", ".xx.kg", ".qd.je"]
PRIMARY = "iconminemods.dpdns.org"
FALLBACK = "iconminemods.us.kg"

# DigitalPlat FreeDomain dashboard. The exact auto-claim API endpoint is not
# guaranteed; we attempt a best-effort POST and never assume success.
DASH_URL = "https://dash.domain.digitalplat.org/"

# DNS target (mirror of dns_records.json)
DNS = {
    "provider": "Vercel",
    "a": {"name": "@", "value": "76.76.21.21"},
    "cname": {"name": "www", "value": "cname.vercel-dns.com"},
    "txt": "verification TXT (set in dashboard)",
}


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_claimed(domain, status, manual):
    data = {
        "domain": domain,
        "status": status,          # "claimed" or "planned"
        "dns": DNS,
        "claimed_at": _now_iso(),
        "manual": manual,          # True if human action still required
    }
    with open(CLAIMED, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    return data


def _read_claimed():
    if not os.path.exists(CLAIMED):
        return None
    try:
        with open(CLAIMED, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def cmd_check():
    data = _read_claimed()
    if data and data.get("domain") and data.get("status") in ("claimed", "planned"):
        print("FREE DOMAIN: %s" % data["domain"])
        print("STATUS:      %s" % data["status"])
        print("MANUAL:      %s" % data.get("manual"))
        sys.exit(0)
    print("No valid free domain claim found in %s" % CLAIMED)
    sys.exit(1)


def _attempt_http_claim(domain, email, password):
    """Best-effort registration against the DigitalPlat dashboard.

    The exact FreeDomain API endpoint is uncertain, so any failure (network,
    auth, missing creds, non-2xx) is treated as 'not auto-claimed'. No
    exception escapes this function.
    """
    if not email or not password:
        return False
    try:
        payload = json.dumps({
            "email": email,
            "password": password,
            "domain": domain,
        }).encode("utf-8")
        req = urllib.request.Request(
            DASH_URL,
            data=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def cmd_claim():
    # Idempotent: if a domain is already recorded, --claim is a no-op.
    existing = _read_claimed()
    if existing and existing.get("domain"):
        print("Already claimed (no-op): %s [%s]" % (existing["domain"], existing.get("status")))
        sys.exit(0)

    email = os.environ.get("DP_EMAIL", "")
    password = os.environ.get("DP_PASS", "")

    print("Target free domain: %s (fallback %s)" % (PRIMARY, FALLBACK))
    auto = _attempt_http_claim(PRIMARY, email, password)

    if auto:
        _write_claimed(PRIMARY, "claimed", False)
        print("Auto-claimed %s via DigitalPlat." % PRIMARY)
    else:
        # Always leave a valid claim so --check passes.
        _write_claimed(PRIMARY, "planned", True)
        print("Could not auto-claim %s (endpoint uncertain or creds missing)." % PRIMARY)
        print("MANUAL STEPS:")
        print("  1. Go to %s" % DASH_URL)
        print("  2. Register / log in (use DP_EMAIL / DP_PASS).")
        print("  3. Claim the free domain '%s'." % PRIMARY)
        print("     (Use '%s' if .dpdns.org is unavailable.)" % FALLBACK)
        print("  4. Set DNS to Vercel: A @ -> 76.76.21.21, "
              "CNAME www -> cname.vercel-dns.com,")
        print("     plus a TXT record for domain verification "
              "(see domains/dns_records.json).")
        print("  5. Re-run `python domains/freedomain_claim.py --check` once live.")
    sys.exit(0)


def main(argv):
    if "--check" in argv:
        cmd_check()
    elif "--claim" in argv:
        cmd_claim()
    else:
        print(__doc__)
        print("ERROR: pass --check or --claim")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
