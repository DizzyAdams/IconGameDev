from __future__ import annotations
from typing import Any


COMPLIANCE_TIERS = {
    "skin_pack": {"min_suggested_usd": 1.99, "max_suggested_usd": 3.99, "typical_sale_lift": 1.25},
    "resources": {"min_suggested_usd": 2.99, "max_suggested_usd": 5.99, "typical_sale_lift": 1.18},
    "world_template": {"min_suggested_usd": 3.99, "max_suggested_usd": 5.99, "typical_sale_lift": 1.20},
    "mashup": {"min_suggested_usd": 5.99, "max_suggested_usd": 7.99, "typical_sale_lift": 1.35},
}

COMPLIANCE_RISK_HINTS = {
    "low": "Keep pack name and descriptions generic. Focus on texture/skin quality.",
    "medium": "Rename pack to generic theme; avoid trademarked terms in-store copy.",
    "high": "Redesign to original characters; do not submit until rethemed.",
}


def suggest(pack_type: str, current_price_usd: float | None = None) -> dict[str, Any]:
    tier = COMPLIANCE_TIERS.get(pack_type)
    if tier is None:
        return {"status": "unknown_pack_type", "tier": None, "message": "Define price band manually."}

    message = (
        f"Suggested band: ${tier['min_suggested_usd']:.2f}-${tier['max_suggested_usd']:.2f}. "
        f"Premium positioning expected."
    )
    suggestion: dict[str, Any] = {
        "status": "ok",
        "pack_type": pack_type,
        "tier": tier,
        "message": message,
        "suggested_price_usd": tier["min_suggested_usd"] if current_price_usd is None else current_price_usd,
        "price_floor_usd": tier["min_suggested_usd"],
        "price_ceiling_usd": tier["max_suggested_usd"],
        "band": "premium",
        "expected_lift": tier["typical_sale_lift"],
    }
    return suggestion
