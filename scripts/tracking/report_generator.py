#!/usr/bin/env python3
"""
IconMineMods — Affiliate Report Generator
==========================================
Generates CSVs and summaries for affiliate performance analytics.

Usage:
    python scripts/tracking/report_generator.py                  # Full report (stdout)
    python scripts/tracking/report_generator.py --csv            # CSV output
    python scripts/tracking/report_generator.py --json           # JSON output (for dashboards)
    python scripts/tracking/report_generator.py --period 2026-07 # Filter by month
"""

import json
import csv
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_FILE = REPO_ROOT / "website-next" / "data" / "affiliates.json"
PACK_CATALOG = REPO_ROOT / "marketplace-content" / "catalog" / "PACK_CATALOG.json"
REPORTS_DIR = REPO_ROOT / "scripts" / "tracking" / "reports"


def load_data():
    if not DATA_FILE.exists():
        print(f"[ERRO] Arquivo não encontrado: {DATA_FILE}")
        sys.exit(1)
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_catalog() -> dict:
    """Load PACK_CATALOG.json and build a lookup dict keyed by product dir."""
    if not PACK_CATALOG.exists():
        print(f"[AVISO] Catálogo não encontrado: {PACK_CATALOG}")
        return {}
    try:
        with open(PACK_CATALOG, encoding="utf-8") as f:
            catalog = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[AVISO] Erro ao ler catálogo: {e}")
        return {}

    # Build lookup: dir name -> pack info (thumbnail from path, price from catalog)
    lookup: dict[str, dict] = {}
    for pack in catalog.get("packs", []):
        d = pack["dir"]
        lookup[d] = {
            "dir": d,
            "product_type": pack.get("product_type", "unknown"),
            "price_usd": pack.get("price_usd", 0.0),
            "price": pack.get("price", "$0.00"),
            "tier": pack.get("tier", "standard"),
            "description": pack.get("store_description", ""),
        }
    return lookup


def fmt_brl(n: float) -> str:
    return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_date(d: str) -> str:
    """Normalize date string."""
    if not d:
        return "-"
    try:
        dt = datetime.fromisoformat(d)
        return dt.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return d[:10]


def build_affiliate_report(data: dict, catalog: dict | None = None, period: str | None = None) -> list[dict]:
    """Build a report row for each affiliate."""
    rows = []
    for a in data.get("affiliates", []):
        aid = a["id"]
        aff_commissions = [c for c in data.get("commissions", []) if c.get("affiliate_id") == aid]
        aff_links = [l for l in data.get("links", []) if l.get("affiliate_id") == aid]

        # Filter by period if set
        if period:
            aff_commissions = [c for c in aff_commissions if c.get("date", "").startswith(period)]
            aff_links = [l for l in aff_links if l.get("created", "").startswith(period)]

        total_earned = sum(c.get("amount", 0) for c in aff_commissions)
        total_pending = sum(c.get("amount", 0) for c in aff_commissions if c.get("status") == "pending")
        total_paid = sum(c.get("amount", 0) for c in aff_commissions if c.get("status") == "paid")
        total_clicks = sum(l.get("clicks", 0) for l in aff_links)
        total_conversions = sum(l.get("conversions", 0) for l in aff_links)
        conv_rate = round((total_conversions / total_clicks * 100), 1) if total_clicks > 0 else 0

        # Enrich with catalog data if available
        product_breakdown: dict[str, dict] = {}
        for c in aff_commissions:
            prod_name = c.get("product", "unknown")
            cat_info = (catalog or {}).get(prod_name, {})
            if prod_name not in product_breakdown:
                product_breakdown[prod_name] = {
                    "dir": prod_name,
                    "product_type": cat_info.get("product_type", "unknown"),
                    "price_usd": cat_info.get("price_usd", 0.0),
                    "price": cat_info.get("price", "$0.00"),
                    "tier": cat_info.get("tier", "standard"),
                    "description": cat_info.get("description", ""),
                    "commission_count": 0,
                    "total_commission": 0.0,
                }
            product_breakdown[prod_name]["commission_count"] += 1
            product_breakdown[prod_name]["total_commission"] += c.get("amount", 0)

        rows.append({
            "id": aid,
            "name": a.get("name", ""),
            "email": a.get("email", ""),
            "platform": a.get("platform", ""),
            "ref_code": a.get("ref_code", ""),
            "commission_rate": a.get("commission_rate", 15),
            "commission_type": a.get("commission_type", "percentage"),
            "status": a.get("status", "active"),
            "joined": a.get("joined", ""),
            "payout_method": a.get("payout_method", ""),
            "total_earned": round(total_earned, 2),
            "total_pending": round(total_pending, 2),
            "total_paid": round(total_paid, 2),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "conversion_rate": conv_rate,
            "link_count": len(aff_links),
            "commission_count": len(aff_commissions),
            "product_breakdown": dict(sorted(
                product_breakdown.items(),
                key=lambda x: -x[1]["total_commission"]
            )),
        })

    return sorted(rows, key=lambda r: -r["total_earned"])


def build_product_report(catalog: dict, data: dict, period: str | None = None) -> list[dict]:
    """Build a product-level sales report from commissions, enriched by catalog."""
    product_map: dict[str, dict] = {}
    commissions = data.get("commissions", [])
    if period:
        commissions = [c for c in commissions if c.get("date", "").startswith(period)]

    for c in commissions:
        prod = c.get("product", "unknown")
        if prod not in product_map:
            cat_info = (catalog or {}).get(prod, {})
            product_map[prod] = {
                "dir": prod,
                "product_type": cat_info.get("product_type", "unknown"),
                "price_usd": cat_info.get("price_usd", 0.0),
                "price": cat_info.get("price", "$0.00"),
                "tier": cat_info.get("tier", "standard"),
                "description": cat_info.get("description", ""),
                "total_sales": 0,
                "total_commission": 0.0,
                "commission_count": 0,
            }
        product_map[prod]["total_sales"] += 1
        product_map[prod]["total_commission"] += c.get("amount", 0)
        product_map[prod]["commission_count"] += 1

    return sorted(
        product_map.values(),
        key=lambda x: -x["total_commission"]
    )


def build_tracking_log_report(data: dict, period: str | None = None) -> list[dict]:
    """Build a report from the tracking log."""
    tracking = data.get("tracking", [])
    if period:
        tracking = [t for t in tracking if t.get("timestamp", "").startswith(period)]
    return tracking


def print_text_report(data: dict, catalog: dict | None = None, period: str | None = None):
    """Print a formatted text report to stdout."""
    settings = data.get("settings", {})
    affiliates = data.get("affiliates", [])

    print("=" * 70)
    print("  ICONMINEMODS — RELATÓRIO DE DESEMPENHO DE AFILIADOS")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}" +
          (f"  |  Período: {period}" if period else ""))
    print("=" * 70)

    rows = build_affiliate_report(data, catalog, period)
    tracking = build_tracking_log_report(data, period)
    products = build_product_report(catalog or {}, data, period)

    # Summary
    total_earned = sum(r["total_earned"] for r in rows)
    total_pending = sum(r["total_pending"] for r in rows)
    total_paid = sum(r["total_paid"] for r in rows)
    total_clicks = sum(r["total_clicks"] for r in rows)
    total_conversions = sum(r["total_conversions"] for r in rows)
    total_commissions = sum(r["commission_count"] for r in rows)

    print(f"\n📊 RESUMO")
    print(f"  {'Afiliados:':<25} {len(rows)}")
    print(f"  {'Total Cliques:':<25} {total_clicks}")
    print(f"  {'Total Conversões:':<25} {total_conversions}")
    print(f"  {'Comissões Registradas:':<25} {total_commissions}")
    print(f"  {'Total Ganho:':<25} {fmt_brl(total_earned)}")
    print(f"  {'Total Pago:':<25} {fmt_brl(total_paid)}")
    print(f"  {'Total Pendente:':<25} {fmt_brl(total_pending)}")
    print(f"  {'Cookie Duration:':<25} {settings.get('cookie_days', 30)} dias")
    print(f"  {'Mínimo p/ Saque:':<25} {fmt_brl(settings.get('min_payout', 50))}")

    # Per affiliate
    print(f"\n📋 DESEMPENHO POR AFILIADO")
    print(f"  {'#' :<4} {'Nome':<20} {'Ref':<18} {'Cliques':<10} {'Conv.':<8} {'Tx':<8} {'Ganho':<12} {'Pend.':<12} {'Com%':<6}")
    print(f"  {'-'*4} {'-'*20} {'-'*18} {'-'*10} {'-'*8} {'-'*8} {'-'*12} {'-'*12} {'-'*6}")
    for i, r in enumerate(rows, 1):
        print(f"  {i:<4} {r['name'][:19]:<20} {r['ref_code'][:17]:<18} "
              f"{r['total_clicks']:<10} {r['total_conversions']:<8} "
              f"{r['conversion_rate']:<8} {fmt_brl(r['total_earned']):<12} "
              f"{fmt_brl(r['total_pending']):<12} {r['commission_rate']}%")

    # Product breakdown per affiliate (top 3 products)
    print(f"\n📦 PRODUTOS MAIS VENDIDOS POR AFILIADO")
    for r in rows:
        pb = r.get("product_breakdown", {})
        if pb:
            top3 = list(pb.items())[:3]
            names = ", ".join(f"{p['total_commission']:.0f}x {k}" for k, p in top3)
            print(f"  {r['name'][:18]:<20} → {names}")

    # Product-level report from catalog
    if products:
        print(f"\n📈 DESEMPENHO POR PRODUTO (catálogo real)")
        print(f"  {'Produto':<30} {'Tipo':<14} {'Preço':<10} {'Tier':<12} {'Vendas':<8} {'Comissão':<12}")
        print(f"  {'-'*30} {'-'*14} {'-'*10} {'-'*12} {'-'*8} {'-'*12}")
        for p in products[:10]:
            print(f"  {p['dir'][:28]:<30} {p['product_type'][:12]:<14} "
                  f"{p['price']:<10} {p['tier'][:10]:<12} "
                  f"{p['total_sales']:<8} {fmt_brl(p['total_commission']):<12}")
        if len(products) > 10:
            print(f"  ... e mais {len(products) - 10} produtos")
        print(f"  {'Cobertura do catálogo:':<30} {len(products)}/{len(catalog)} produtos referenciados"
              ) if catalog else None

    # Recent tracking events
    if tracking:
        print(f"\n📝 ÚLTIMOS EVENTOS DE TRACKING")
        recent = tracking[-20:]
        for t in recent:
            stamp = fmt_date(t.get("timestamp", ""))
            ttype = t.get("type", "?")
            ref = t.get("ref_code", "")
            aff_name = next((a.get("name", "") for a in affiliates if a.get("ref_code") == ref), ref)
            if ttype == "click":
                print(f"  🖱 {stamp} — Clique: {aff_name}")
            elif ttype == "conversion":
                print(f"  💰 {stamp} — Conversão: {aff_name} | "
                      f"R$ {t.get('amount', 0):.2f} → comissão R$ {t.get('commission', 0):.2f}")

    print()


def to_csv(data: dict, catalog: dict | None = None, period: str | None = None):
    """Export affiliate report to CSV."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_affiliate_report(data, catalog, period)

    suffix = f"_{period}" if period else ""
    filename = f"affiliate_report{suffix}.csv"
    filepath = REPORTS_DIR / filename

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ CSV exportado: {filepath} ({len(rows)} linhas)")


def to_json(data: dict, catalog: dict | None = None, period: str | None = None):
    """Export affiliate report to JSON."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_affiliate_report(data, catalog, period)
    tracking = build_tracking_log_report(data, period)
    products = build_product_report(catalog or {}, data, period)
    settings = data.get("settings", {})

    report = {
        "generated_at": datetime.now().isoformat(),
        "period": period or "all",
        "affiliates": rows,
        "products": products,
        "tracking_events": len(tracking),
        "settings": settings,
    }

    suffix = f"_{period}" if period else ""
    filename = f"affiliate_report{suffix}.json"
    filepath = REPORTS_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON exportado: {filepath}")


def main():
    data = load_data()
    catalog = load_catalog()
    args = sys.argv[1:]

    period = None
    for a in args:
        if a.startswith("--period="):
            period = a.split("=", 1)[1]

    if "--csv" in args:
        to_csv(data, catalog, period)
    elif "--json" in args:
        to_json(data, catalog, period)
    else:
        print_text_report(data, catalog, period)


if __name__ == "__main__":
    main()
