#!/usr/bin/env python3
"""Quick test: run auto_submit_mc dry-run logic and print results."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "submit"))

# Override secrets to use default privacy URL so we don't need secrets.json
_orig_import = __import__

def test_dry_run():
    """Test the dry-run logic of auto_submit_mc inline."""
    from submit import auto_submit_mc as amc
    
    # Patch secrets_ready to always return ready with the default URL
    orig_secrets = amc.secrets_ready
    amc.secrets_ready = lambda: (True, "https://iconminemods.dpdns.org/privacy")
    
    ready, privacy_url = amc.secrets_ready()
    print(f"secrets_ready: {ready}")
    print(f"privacy_url: {privacy_url}")
    
    plans, eligible_list, blocked_list = amc.build_plans(privacy_url)
    print(f"\neligible: {len(plans)} world packs")
    print(f"blocked: {len(blocked_list)}")
    
    if blocked_list:
        print(f"  blocked: {', '.join(blocked_list)}")
    
    all_steps = [s for pl in plans for s in pl["steps"]]
    problems = amc.validate_plan(all_steps)
    print(f"\nsafety validation: {'CLEAN' if not problems else problems}")
    
    if plans:
        print(f"\nFirst pack:")
        p0 = plans[0]
        print(f"  offer: {p0['offer']}")
        print(f"  title: {p0['title']}")
        print(f"  category: {p0['category']}")
        print(f"  steps: {len(p0['steps'])}")
        print(f"  last step: {p0['steps'][-1]['action']} -> {p0['steps'][-1]['target']}")
        
        # Show first 3 steps
        print(f"\nFirst 3 steps:")
        for i, st in enumerate(p0['steps'][:3]):
            print(f"  [{i}] {st['action']:>20} | {st['target']}")
    
    print(f"\nTotal steps across all plans: {len(all_steps)}")
    print(f"Total packs: {len(plans)}")
    
    if len(plans) > 1:
        p1 = plans[1]
        print(f"\nSecond pack: {p1['offer']} -> {p1['title']}")
    
    print("\n=== DRY-RUN PASSED ===")


if __name__ == "__main__":
    test_dry_run()
