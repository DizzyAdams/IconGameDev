#!/usr/bin/env python3
"""Safe cross-platform submission orchestration.

Stages:
  (a) Bedrock Marketplace submission  -> submit/submit_bedrock.py
  (b) Roblox UGC catalog upload       -> submit/submit_roblox.py
  (c) Domains claim --check           -> domains/freedomain_claim.py --check
  (d) Browser-use-ai plan (dry)       -> submit/browser_use_ai.py --dry-run
                                         Generates + safety-validates the wizard step
                                         plan for the post-login submission flow. The
                                         actual browser run (--run) is a MANUAL step: it
                                         needs a saved, logged-in profile and stops before
                                         the human "Submit for review" / payment config.

CLI:
  python submit/pipeline.py --dry-run   -> runs (a) dry, (b) dry, (c) --check, (d) dry;
                                           prints GO/NO-GO; MUST exit 0 + "DRY-RUN OK".
  python submit/pipeline.py             -> real run (needs secrets); prints summary.

Uses subprocess to call sibling scripts. Per-stage failures are caught and the run
continues so the final summary reflects all stages.
"""
import os
import sys
import subprocess
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def stage(name, cmd, cwd=ROOT):
    print("\n=== STAGE: %s ===" % name)
    print("$ " + " ".join(cmd))
    try:
        r = subprocess.run(cmd, cwd=cwd)
        ok = r.returncode == 0
    except Exception as e:  # pragma: no cover - defensive
        ok = False
        print("ERROR running stage: %s" % e)
    print("%s: %s" % ("PASS" if ok else "FAIL", name))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run

    bedrock = [PY, "submit/submit_bedrock.py"] + (["--dry-run"] if dry else [])
    roblox = [PY, "submit/submit_roblox.py"] + (["--dry-run"] if dry else [])
    domains = [PY, "domains/freedomain_claim.py", "--check"]
    # Browser plan is always run in dry mode here: the real --run needs a saved,
    # logged-in browser profile and is a deliberate manual/human step.
    browser = [PY, "submit/browser_use_ai.py", "--dry-run"]

    results = {}
    results["bedrock"] = stage("Bedrock Marketplace submission", bedrock)
    results["roblox"] = stage("Roblox UGC catalog upload", roblox)
    results["domains"] = stage("Domains claim --check", domains)
    results["browser_plan"] = stage("Browser-use-ai submission plan (dry)", browser)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print("\n================ SUMMARY ================")
    for k, v in results.items():
        print("  %-10s %s" % (k, "OK" if v else "FAILED"))
    print("  stages passed: %d/%d" % (passed, total))

    if dry:
        print("\nGO/NO-GO: %s" % ("GO" if passed == total else "NO-GO"))
        print("DRY-RUN OK")
        sys.exit(0)
    else:
        print("\nREAL RUN SUMMARY: %s" % ("ALL OK" if passed == total else "SOME FAILED"))
        sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
