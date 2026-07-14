"""Revenue projection for the IconGameDev Bedrock Marketplace portfolio.

Real portfolio measured from marketplace-content/ source dirs:
  skin-packs 6294, texture-packs 1737, world-templates 1200, mashup-packs 458
  -> 9689 packs total; 8521 .mcpack already built in dist/.

All prices are competitive Minecoin-tier-aligned (USD). Microsoft keeps 30%,
creator receives 70%. Target: cumulative US$ 50,000 in creator payouts.
"""
from __future__ import annotations

# Real portfolio (counts measured from marketplace-content/ source dirs).
PORTFOLIO = {
    "skin_packs":     {"count": 6294, "price": 1.99, "sales_per_pack_mo": 0.5},
    "texture_packs":  {"count": 1737, "price": 2.99, "sales_per_pack_mo": 0.4},
    "world_templates": {"count": 1200, "price": 3.99, "sales_per_pack_mo": 0.3},
    "mashup_packs":   {"count": 458,  "price": 4.99, "sales_per_pack_mo": 0.3},
}
CREATOR_CUT = 0.70
TARGET_TOTAL_USD = 50_000
DIST_BUILT = 8521


def project() -> None:
    monthly_net = 0.0
    print("=== BEDROCK MARKETPLACE - PROJECAO DE RECEITA (realista/conservadora) ===\n")
    print(f"  Portfolio fonte: {sum(d['count'] for d in PORTFOLIO.values())} packs "
          f"({DIST_BUILT} .mcpack em dist/)\n")
    for cat, d in PORTFOLIO.items():
        gross = d["count"] * d["price"] * d["sales_per_pack_mo"]
        net = gross * CREATOR_CUT
        monthly_net += net
        name = cat.replace("_", " ").title()
        print(f"  {name:16s} {d['count']:5d} packs @ ${d['price']:.2f} x "
              f"{d['sales_per_pack_mo']:.1f}/mo = ${net:>9,.2f}/mo (liq 70%)")
    annual_net = monthly_net * 12
    months_to_target = TARGET_TOTAL_USD / monthly_net if monthly_net else float("inf")
    print(f"\n  {'LIQUIDO/mes':16s} ${monthly_net:>9,.2f}")
    print(f"  {'LIQUIDO/ano':16s} ${annual_net:>9,.2f}")
    print(f"  {'Meta cumulativa':16s} ${TARGET_TOTAL_USD:>9,.2f}")
    print(f"  {'Tempo p/meta':16s} {months_to_target:>8.1f} meses "
          f"(~{months_to_target / 12:.1f} anos) a esta taxa")


if __name__ == "__main__":
    project()
