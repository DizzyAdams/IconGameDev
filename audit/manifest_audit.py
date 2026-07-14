#!/usr/bin/env python3
import json
import os
import sys
import uuid as uuid_module
from pathlib import Path

MANIFEST_PATH = "marketplace-content"

REQUIRED_HEADER = ["name", "description", "uuid", "version", "min_engine_version"]
REQUIRED_MODULE = ["type", "uuid", "version"]
REQUIRED_METADATA = ["authors", "product_type"]

def is_valid_uuid(val):
    try:
        uuid_module.UUID(str(val))
        return True
    except ValueError:
        return False

def check_manifest(path):
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {e}"}
    
    issues = []
    warnings = []
    
    # Check format_version
    if data.get("format_version") != 2:
        issues.append("format_version must be 2")
    
    # Header
    header = data.get("header", {})
    for field in REQUIRED_HEADER:
        if field not in header:
            issues.append(f"Missing header.{field}")
        elif not header[field]:
            issues.append(f"header.{field} is empty")
    if "uuid" in header and not is_valid_uuid(header["uuid"]):
        issues.append("header.uuid is not a valid UUID")
    if "version" in header:
        if not isinstance(header["version"], list) or len(header["version"]) != 3:
            issues.append("header.version must be a list of three integers")
        else:
            for v in header["version"]:
                if not isinstance(v, int):
                    issues.append("header.version elements must be integers")
    if "min_engine_version" in header:
        if not isinstance(header["min_engine_version"], list) or len(header["min_engine_version"]) != 3:
            issues.append("header.min_engine_version must be a list of three integers")
        else:
            for v in header["min_engine_version"]:
                if not isinstance(v, int):
                    issues.append("header.min_engine_version elements must be integers")
    
    # Modules
    modules = data.get("modules", [])
    if not modules:
        issues.append("modules list is empty")
    for i, mod in enumerate(modules):
        for field in REQUIRED_MODULE:
            if field not in mod:
                issues.append(f"modules[{i}] missing {field}")
            elif not mod[field]:
                issues.append(f"modules[{i}].{field} is empty")
        if "uuid" in mod and not is_valid_uuid(mod["uuid"]):
            issues.append(f"modules[{i}].uuid is not a valid UUID")
        if "version" in mod:
            if not isinstance(mod["version"], list) or len(mod["version"]) != 3:
                issues.append(f"modules[{i}].version must be a list of three integers")
            else:
                for v in mod["version"]:
                    if not isinstance(v, int):
                        issues.append(f"modules[{i}].version elements must be integers")
    
    # Metadata
    metadata = data.get("metadata", {})
    for field in REQUIRED_METADATA:
        if field not in metadata:
            issues.append(f"Missing metadata.{field}")
        elif not metadata[field]:
            issues.append(f"metadata.{field} is empty")
    # Price or prices
    if "price" not in metadata and "prices" not in metadata:
        issues.append("metadata missing price or prices")
    # Authors should be list
    if "authors" in metadata and not isinstance(metadata["authors"], list):
        issues.append("metadata.authors should be a list")
    # product_type should be one of known types
    known_types = ["skin_pack", "texture_pack", "world_template", "behavior_pack", "mashup", "addon"]
    if "product_type" in metadata and metadata["product_type"] not in known_types:
        warnings.append(f"metadata.product_type '{metadata['product_type']}' not in known types {known_types}")
    
    # Check for duplicate UUIDs across file? We'll do later.
    
    return {
        "path": path,
        "issues": issues,
        "warnings": warnings,
        "data": data
    }

def main():
    root = Path(MANIFEST_PATH)
    manifest_files = list(root.rglob("manifest.json"))
    print(f"Found {len(manifest_files)} manifest files")
    
    all_issues = []
    all_warnings = []
    uuids_seen = set()
    
    for mf in manifest_files:
        result = check_manifest(mf)
        if "error" in result:
            print(f"ERROR in {mf}: {result['error']}")
            all_issues.append({"file": str(mf), "error": result["error"]})
            continue
        issues = result["issues"]
        warnings = result["warnings"]
        data = result["data"]
        if issues:
            all_issues.append({"file": str(mf), "issues": issues})
        if warnings:
            all_warnings.append({"file": str(mf), "warnings": warnings})
        # Collect UUIDs
        header_uuid = data.get("header", {}).get("uuid")
        if header_uuid:
            if header_uuid in uuids_seen:
                all_issues.append({"file": str(mf), "issues": [f"Duplicate header UUID {header_uuid}"]})
            else:
                uuids_seen.add(header_uuid)
        for mod in data.get("modules", []):
            muuid = mod.get("uuid")
            if muuid:
                if muuid in uuids_seen:
                    all_issues.append({"file": str(mf), "issues": [f"Duplicate module UUID {muuid}"]})
                else:
                    uuids_seen.add(muuid)
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total manifests checked: {len(manifest_files)}")
    print(f"Manifests with issues: {len(all_issues)}")
    print(f"Manifests with warnings: {len(all_warnings)}")
    
    if all_issues:
        print("\n--- ISSUES ---")
        for item in all_issues:
            print(f"{item['file']}:")
            if "error" in item:
                print(f"  ERROR: {item['error']}")
            else:
                for iss in item["issues"]:
                    print(f"  - {iss}")
    if all_warnings:
        print("\n--- WARNINGS ---")
        for item in all_warnings:
            print(f"{item['file']}:")
            for warn in item["warnings"]:
                print(f"  - {warn}")
    
    # Write detailed report
    report_path = Path("audit/manifest_report.json")
    report_path.parent.mkdir(exist_ok=True)
    report = {
        "total": len(manifest_files),
        "issues": all_issues,
        "warnings": all_warnings
    }
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"\nDetailed report written to {report_path}")

if __name__ == "__main__":
    main()