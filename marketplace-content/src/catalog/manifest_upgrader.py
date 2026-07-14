from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.catalog.pack_catalog import PackCatalog
from src.catalog.compliance_suggester import suggest


DEFAULT_USD_TO_MC = {
    "skin_pack": (1.99, 3.99),
    "resources": (2.99, 5.99),
    "world_template": (3.99, 5.99),
    "mashup": (5.99, 7.99),
}
CAPTION_MAX_LEN = 140
FORBIDDEN_PHRASES = [
    "bait-and-switch",
    "sale ends",
    "discount today",
    "only today",
    "must buy",
    "limited time offer",
]


def best_price_range(pack_type: str) -> tuple[float, float]:
    return DEFAULT_USD_TO_MC.get(pack_type, (1.99, 3.99))


def read_description(pack_root: Path, pack_dir: str) -> str:
    descriptions_root = pack_root.parent.parent / "descriptions" / pack_dir
    candidates = [
        descriptions_root / "description.txt",
        descriptions_root / "description_en.txt",
        descriptions_root / "description_pt.txt",
    ]
    for p in candidates:
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="ignore")
            break
    else:
        return ""
    text = re.sub(r"§[0-9a-fk-or]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"©.*$", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text


def improve_store_copy(raw: str) -> str | None:
    if not raw:
        return None
    lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
    if not lines:
        return None
    # Prefer the first substantive sentence, skipping the pack title itself
    candidate = None
    for line in lines[1:]:
        if len(line) >= 20:
            candidate = line
            break
    if candidate is None:
        candidate = lines[0]
    s = " ".join(candidate.split())
    if len(s) > CAPTION_MAX_LEN:
        s = s[:CAPTION_MAX_LEN - 1].rstrip() + "…"
    for bad in FORBIDDEN_PHRASES:
        s = s.replace(bad, "great value")
    return s


def detect_pack_type(manifest: dict[str, Any], pack_dir: str) -> str:
    # metadata wins when present
    metadata = manifest.get("metadata", {})
    if metadata.get("product_type") in {"skin_pack", "resources", "world_template", "mashup"}:
        return metadata["product_type"]

    # Mashup packs often declare module type resources, but live under mashup-packs
    for mod in manifest.get("modules", []):
        if not isinstance(mod, dict):
            continue
        mt = mod.get("type")
        if mt == "skin_pack":
            return "skin_pack"
        if mt == "world_template":
            return "world_template"
        if mt == "mashup":
            return "mashup"
        if mt == "resources":
            if "mashup-packs" in str(manifest) or "mashup" in pack_dir.lower():
                return "mashup"
            return "resources"
    return "skin_pack"


def set_manifest_metadata(manifest_path: Path, pack_dir: str, pack_type: str, desc_raw: str, catalog: PackCatalog) -> dict[str, Any] | None:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest: dict[str, Any] = json.load(f)

    metadata = manifest.setdefault("metadata", {})
    metadata["product_type"] = pack_type
    header = manifest.setdefault("header", {})
    rec = catalog.get(pack_dir)

    price_usd = None
    tier = None
    if isinstance(rec, dict):
        raw_price = rec.get("price_usd")
        if isinstance(raw_price, (int, float)):
            price_usd = float(raw_price)
        elif rec.get("price"):
            m = re.search(r"([0-9]+(?:\.[0-9]{2})?)", str(rec["price"]))
            if m:
                price_usd = float(m.group(1))
        tier = rec.get("tier") or metadata.get("tier")

    sugg = suggest(pack_type, current_price_usd=price_usd)
    price_usd = float(sugg.get("suggested_price_usd", best_price_range(pack_type)[0]))
    lo, hi = best_price_range(pack_type)
    price_usd = max(lo, min(price_usd, hi))
    price_mc = max(1, int(round((price_usd * 160) / 10.0) * 10))
    if tier is None:
        tier = "premium" if price_usd >= 2.99 else "standard"

    authors = ["Bedrock Minemods"]
    if isinstance(rec, dict) and rec.get("author"):
        authors = [str(rec["author"])]
    metadata["authors"] = authors
    metadata["price"] = f"${price_usd:.2f} ({price_mc} MC)"
    metadata["price_usd"] = round(price_usd, 2)
    metadata["price_mc"] = price_mc
    metadata["tier"] = tier

    improved = improve_store_copy(desc_raw)
    if improved:
        metadata["store_description"] = improved
        header["description"] = improved

    if isinstance(rec, dict) and rec.get("tags"):
        metadata["tags"] = [str(t) for t in rec["tags"]][:6]

    metadata.setdefault("status", "pending_premium_review")
    metadata.setdefault("release_notes", {})
    metadata["release_notes"].setdefault("1.0.0", "Premium pack prepared for store submission.")

    manifest.setdefault("format_version", 2)
    return manifest


def write_manifest(manifest_path: Path, manifest: dict[str, Any]) -> None:
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
