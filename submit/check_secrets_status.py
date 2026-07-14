#!/usr/bin/env python3
"""Local, non-leaking status check for ops/secrets.json.

Prints, per field, only FILLED or PLACEHOLDER -- never the secret value itself.
Run:  python submit/check_secrets_status.py
"""
import os
import json
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "ops", "secrets.json")


def st(v):
    if isinstance(v, str):
        return "PLACEHOLDER" if (v.strip().startswith("<") or v.strip() == "") else "FILLED"
    if isinstance(v, dict):
        return {k: st(x) for k, x in v.items()}
    return "FILLED"


def main():
    if not os.path.isfile(PATH):
        print("MISSING: ops/secrets.json (cp ops/secrets.example.json ops/secrets.json)")
        sys.exit(2)
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)
    print("secrets status (values hidden):")
    any_placeholder = False
    for sec, val in d.items():
        if sec == "_comment":
            continue
        print("  [%s]" % sec)
        if isinstance(val, dict):
            for k, v in val.items():
                s = st(v)
                if s == "PLACEHOLDER":
                    any_placeholder = True
                print("    %-14s %s" % (k, s))
        else:
            s = st(val)
            if s == "PLACEHOLDER":
                any_placeholder = True
            print("    %s" % s)
    print("\nREADINESS: %s" % ("READY (no placeholders)" if not any_placeholder
                               else "NOT READY (fill the PLACEHOLDER fields, then re-run)"))
    sys.exit(0 if not any_placeholder else 1)


if __name__ == "__main__":
    main()
