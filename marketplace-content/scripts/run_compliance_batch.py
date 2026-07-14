"""Batch wrapper for run_compliance over generated mass packs."""
import sys
from pathlib import Path
from run_compliance import run_compliance, report
ROOT = Path(__file__).resolve().parent.parent
pack_root = ROOT / "output" / "mass-1500"
pack_dirs = [str(p) for p in sorted(pack_root.glob("mass_*")) if p.is_dir()]
if not pack_dirs:
    print(f"No pack dirs found in {pack_root}")
    raise SystemExit(2)
results = run_compliance(pack_dirs)
print(report(results))
out = ROOT / "output" / "compliance" / "full-1500.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(
    __import__('json').dumps({"count": len(results), "items": results}, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
print(out)
raise SystemExit(0 if all(r['decision'] == 'APPROVED' for r in results) else 2)
