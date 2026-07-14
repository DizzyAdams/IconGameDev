#!/usr/bin/env python3
"""
Fix Bedrock manifest.json files for Microsoft Marketplace compliance.
- Ensures format_version = 2
- Validates/Generates UUIDs for header and modules
- Ensures version arrays are 3 integers
- Ensures min_engine_version is valid
- Ensures authors is a non-empty list
- Ensures price or price field
- Creates backups
- Collects screenshots/icons
"""

import json
import os
import shutil
import uuid
from pathlib import Path

MANIFEST_ROOT = Path("marketplace-content")
BACKUP_DIR = Path("audit/backup")
REPORT_PATH = Path("audit/fix_report.json")
SCREENSHOT_DIR = Path("audit/screenshots")

KNOWN_PRODUCT_TYPES = {
    "skin_pack",
    "texture_pack", 
    "world_template",
    "behavior_pack",
    "mashup",
    "addon",
}

def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def ensure_uuid(existing: str | None, used: set[str]) -> str:
    if existing and is_valid_uuid(existing) and existing not in used:
        return existing
    # generate new unique
    while True:
        new = str(uuid.uuid4())
        if new not in used:
            used.add(new)
            return new

def normalize_price(price_str: str) -> dict:
    """Convert a price string like '$2.99' to components for price_usd and price_mc."""
    # Remove currency symbols and commas
    cleaned = price_str.replace("$", "").replace("€", "").replace("£", "").replace(",", "")
    try:
        amount = float(cleaned)
    except ValueError:
        # fallback
        return {}
    price_usd = {"currency": "USD", "amount": round(amount, 2)}
    # Approximate conversion to Minecoins: 1 USD ≈ 160 Minecoins
    minecoins = int(round(amount * 160))
    price_mc = {"currency": "MXN", "amount": minecoins}
    return {"price_usd": price_usd, "price_mc": price_mc}

def main():
    # Prepare directories
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    manifest_files = list(MANIFEST_ROOT.rglob("manifest.json"))
    print(f"Found {len(manifest_files)} manifest files.")
    
    used_uuids = set()
    report = {
        "total": len(manifest_files),
        "modified": 0,
        "details": []
    }
    
    for mf in manifest_files:
        rel = mf.relative_to(MANIFEST_ROOT)
        backup_path = BACKUP_DIR / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"ERROR reading {mf}: {e}")
            report["details"].append({"file": str(rel), "error": str(e)})
            continue
        
        changes = []
        modified = False
        
        # Ensure format_version
        if data.get("format_version") != 2:
            data["format_version"] = 2
            changes.append("format_version set to 2")
            modified = True
        
        # Header
        header = data.setdefault("header", {})
        # UUID
        old_uuid = header.get("uuid")
        new_uuid = ensure_uuid(old_uuid, used_uuids)
        if old_uuid != new_uuid:
            header["uuid"] = new_uuid
            changes.append(f"header.uuid: {old_uuid} -> {new_uuid}")
            modified = True
        # version
        ver = header.get("volume") or header.get("version")  # in case of typo, but we expect version
        # Use version key
        ver = header.get("version")
        if not (isinstance(ver, list) and len(ver) == 3 and all(isinstance(v, int) for v in ver)):
            header["version"] = [1, 0, 0]
            changes.append("header.version set to [1,0,0]")
            modified = True
        # min_engine_version
        mev = header.get("min_engine_version")
        if not (isinstance(mev, list) and len(mev) == 3 and all(isinstance(v, int) for v in mev)):
            header["min_engine_version"] = [1, 20, 0]
            changes.append("header.min_engine_version set to [1,20,0]")
            modified = True
        # name & description (ensure non-empty strings)
        if not isinstance(header.get("name", ""), str) or not header["name"].strip():
            header["name"] = "Unnamed Pack"
            changes.append("header.name set to placeholder")
            modified = True
        if not isinstance(header.get("description", ""), str) or not header["description"].strip():
            header["description"] = "Description not provided."
            changes.append("header.description set to placeholder")
            modified = True
        
        # Modules
        modules = data.setdefault("modules", [])
        if not isinstance(modules, list):
            modules = []
            data["modules"] = modules
            changes.append("modules reset to list")
            modified = True
        
        for i, mod in enumerate(modules):
            if not isinstance(mod, dict):
                mod = {}
                modules[i] = mod
                changes.append(f"modules[{i}] reset to dict")
                modified = True
            # type
            mtype = mod.get("type")
            if not mtype:
                # infer from parent folder
                parent_name = mf.parent.name.lower()
                if "skin" in parent_name:
                    mtype = "skin_pack"
                elif "behavior" in parent_name:
                    mtype = "behavior_pack"
                elif "texture" in parent_name:
                    mtype = "texture_pack"
                elif "world" in parent_name:
                    mtype = "world_template"
                elif "mashup" in parent_name:
                    mtype = "mashup"
                else:
                    mtype = "addon"
                mod["type"] = mtype
                changes.append(f"modules[{i}].type set to {mtype}")
                modified = True
            # UUID
            old_muuid = mod.get("uuid")
            new_muuid = ensure_uuid(old_muuid, used_uuids)
            if old_muuid != new_muuid:
                mod["uuid"] = new_muuid
                changes.append(f"modules[{i}].uuid: {old_muuid} -> {new_muuid}")
                modified = True
            # version
            mver = mod.get("version")
            if not (isinstance(mver, list) and len(mver) == 3 and all(isinstance(v, int) for v in mver)):
                mod["version"] = [1, 0, 0]
                changes.append(f"modules[{i}].version set to [1,0,0]")
                modified = True
        
        # Metadata
        meta = data.setdefault("metadata", {})
        # authors
        authors = meta.get("authors")
        if not isinstance(authors, list) or not authors:
            meta["authors"] = ["Bedrock Minemods"]
            changes.append('metadata.authors set to ["Bedrock Minemods"]')
            modified = True
        # product_type (optional but recommend)
        pt = meta.get("product_type")
        if pt and pt not in KNOWN_PRODUCT_TYPES:
            # keep but note
            changes.append(f"WARNING: product_type '{pt}' not in known list {sorted(KNOWN_PRODUCT_TYPES)}")
        # price / prices
        has_price = "price" in meta
        has_prices = "prices" in meta
        if not has_price and not has_prices:
            # set default price
            meta["price"] = "$2.99"
            changes.append('metadata.price set to "$2.99"')
            modified = True
            has_price = True
        # ensure price is string
        if has_price:
            p = meta["price"]
            if not isinstance(p, str):
                try:
                    p = str(p)
                except Exception:
                    p = "$2.99"
                meta["price"] = p
                changes.append('metadata.price forced to string')
                modified = True
            # derive price_usd and price_mc if missing
            if "price_usd" not in meta or "price_mc" not in meta:
                extra = normalize_price(meta["price"])
                if extra:
                    for k, v in extra.items():
                        if k not in meta:
                            meta[k] = v
                            changes.append(f"metadata.{k} set")
                            modified = True
        
        if modified:
            # Backup original
            shutil.copy2(mf, backup_path)
            # Write updated
            with open(mf, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            report["modified"] += 1
            print(f"Modified {rel}")
        else:
            print(f"No changes needed for {rel}")
        
        # Collect screenshot/icon
        # Look for icon.png in same directory or textures/
        icon_candidates = [
            mf.parent / "icon.png",
            mf.parent / "textures" / "icon.png",
            mf.parent / "textures" / "skins" / "icon.png",
        ]
        icon_path = None
        for cand in icon_candidates:
            if cand.is_file():
                icon_path = cand
                break
        if icon_path:
            dest = SCREENSHOT_DIR / rel.parent / icon_path.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(icon_path, dest)
        else:
            # fallback: copy any .png in textures
            tex_dir = mf.parent / "textures"
            if tex_dir.is_dir():
                pngs = list(tex_dir.rglob("*.png"))
                if pngs:
                    dest = SCREENSHOT_DIR / rel.parent / f"{rel.parent.name}_thumb.png"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(pngs[0], dest)
        
        report["details"].append({
            "file": str(rel),
            "changes": changes if changes else ["none"],
            "backup": str(backup_path)
        })
    
    # Write report
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total manifests: {report['total']}")
    print(f"Modified: {report['modified']}")
    print(f"Backup saved to: {BACKUP_DIR.resolve()}")
    print(f"Report written to: {REPORT_PATH.resolve()}")
    print(f"Screenshots/icons collected in: {SCREENSHOT_DIR.resolve()}")

if __name__ == "__main__":
    main()