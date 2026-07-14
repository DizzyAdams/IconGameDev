"""Marketplace Partner Program application checklist & helper."""
import json, uuid, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKLIST = [
    "1. Build portfolio: 3+ polished content pieces (we have 2 skin packs + 1 texture pack)",
    "2. Create Microsoft account (if not already)",
    "3. Go to https://creator.microsoft.com",
    "4. Click 'Apply to Partner Program'",
    "5. Prepare business info: legal name, tax ID (CPF/CNPJ), address",
    "6. Prepare payment info: bank account/PayPal",
    "7. Upload portfolio examples (.mcpack files)",
    "   - medieval-knights.mcpack",
    "   - anime-warriors.mcpack",
    "   - faithful-16x.mcpack",
    "8. Write description of creative process",
    "9. Submit & wait 2-4 weeks for review",
    "10. If accepted: set up payout in Partner Center",
]

def print_checklist():
    print("=== MINECRAFT PARTNER PROGRAM APPLICATION ===\n")
    for item in CHECKLIST:
        print(f"  [ ] {item}")
    print(f"\nYour .mcpacks are in: {ROOT / 'dist'}")
    print("Size check:")
    for f in (ROOT / "dist").glob("*.mcpack"):
        print(f"  {f.name}: {f.stat().st_size / 1024:.0f} KB")

def generate_manifest_preview():
    """Print a summary of all manifests for the application."""
    for pack_dir in ["skin-packs/medieval-knights", "skin-packs/anime-warriors", "texture-packs/faithful-16x"]:
        mf = ROOT / pack_dir / "manifest.json"
        if mf.exists():
            data = json.loads(mf.read_text())
            print(f"\n{pack_dir}:")
            print(f"  Name: {data['header']['name']}")
            print(f"  Desc: {data['header']['description']}")
            print(f"  Version: {'.'.join(str(v) for v in data['header']['version'])}")

if __name__ == "__main__":
    print_checklist()
    generate_manifest_preview()
