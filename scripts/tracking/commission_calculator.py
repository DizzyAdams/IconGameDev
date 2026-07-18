#!/usr/bin/env python3
"""
IconMineMods — Commission Calculator
====================================
Auto-calculates affiliate commissions from sales data.

Usage:
    python scripts/tracking/commission_calculator.py [--period 2026-07]
    python scripts/tracking/commission_calculator.py --pay-pending
    python scripts/tracking/commission_calculator.py --report

Reads from: website-next/data/affiliates.json
Outputs:    summary of pending/payable commissions per affiliate
"""

import json
import sys
import os
from datetime import datetime, date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_FILE = REPO_ROOT / "website-next" / "data" / "affiliates.json"


def load_data():
    if not DATA_FILE.exists():
        print(f"[ERRO] Arquivo não encontrado: {DATA_FILE}")
        sys.exit(1)
    with open(DATA_FILE) as f:
        return json.load(f)


def fmt_brl(n: float) -> str:
    return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calc_pending(data: dict) -> dict:
    """Group pending commissions by affiliate."""
    affiliates = {a["id"]: a for a in data.get("affiliates", [])}
    pending: dict = {}

    for c in data.get("commissions", []):
        if c.get("status") != "pending":
            continue
        aid = c["affiliate_id"]
        if aid not in pending:
            aff = affiliates.get(aid, {})
            pending[aid] = {
                "name": aff.get("name", "Desconhecido"),
                "email": aff.get("email", ""),
                "ref_code": aff.get("ref_code", ""),
                "commission_rate": aff.get("commission_rate", 15),
                "commissions": [],
                "total_pending": 0.0,
            }
        pending[aid]["commissions"].append(c)
        pending[aid]["total_pending"] += c.get("amount", 0)

    return pending


def print_summary(data: dict):
    """Print summary of all affiliate commissions."""
    affiliates = data.get("affiliates", [])
    commissions = data.get("commissions", [])
    settings = data.get("settings", {})

    print("=" * 60)
    print("  ICONMINEMODS — RELATÓRIO DE COMISSÕES DE AFILIADOS")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    total_earned = sum(c.get("amount", 0) for c in commissions)
    total_pending = sum(c.get("amount", 0) for c in commissions if c.get("status") == "pending")
    total_paid = sum(c.get("amount", 0) for c in commissions if c.get("status") == "paid")
    min_payout = settings.get("min_payout", 50)

    print(f"\n📊 RESUMO GERAL")
    print(f"  {'Afiliados:':<20} {len(affiliates)}")
    print(f"  {'Total Comissões:':<20} {len(commissions)}")
    print(f"  {'Total Ganho:':<20} {fmt_brl(total_earned)}")
    print(f"  {'Total Pago:':<20} {fmt_brl(total_paid)}")
    print(f"  {'Total Pendente:':<20} {fmt_brl(total_pending)}")
    print(f"  {'Mínimo p/ Saque:':<20} {fmt_brl(min_payout)}")

    pending_group = calc_pending(data)

    if pending_group:
        print(f"\n⏳ COMISSÕES PENDENTES POR AFILIADO")
        for aid, p in sorted(pending_group.items(), key=lambda x: -x[1]["total_pending"]):
            flag = " ✅ ACIMA DO MÍN." if p["total_pending"] >= min_payout else " ⏸ ABAIXO DO MÍN."
            print(f"\n  {p['name']} ({p['ref_code']})")
            print(f"    Email:     {p['email']}")
            print(f"    Comissão:  {p['commission_rate']}%")
            print(f"    Pendente:  {fmt_brl(p['total_pending'])}{flag}")
            for c in p["commissions"][:5]:
                print(f"      • {c.get('date','?')} — {c.get('description','?')}: {fmt_brl(c.get('amount',0))}")
            if len(p["commissions"]) > 5:
                print(f"      ... +{len(p['commissions'])-5} comissões")

    # Top earners
    top = sorted(affiliates, key=lambda a: sum(
        c.get("amount", 0) for c in commissions if c.get("affiliate_id") == a.get("id")
    ), reverse=True)[:5]

    if top:
        print(f"\n🏆 TOP 5 AFILIADOS")
        for i, a in enumerate(top, 1):
            earned = sum(c.get("amount", 0) for c in commissions if c.get("affiliate_id") == a.get("id"))
            print(f"  {i}. {a.get('name','?')} ({a.get('ref_code','?')}) — {fmt_brl(earned)}")

    print("\n" + "=" * 60)


def pay_pending(data: dict):
    """Mark all pending commissions as 'paid' (simulate payout)."""
    paid_count = 0
    paid_total = 0.0
    for c in data.get("commissions", []):
        if c.get("status") == "pending":
            c["status"] = "paid"
            paid_count += 1
            paid_total += c.get("amount", 0)

    if paid_count == 0:
        print("Nenhuma comissão pendente para pagar.")
        return

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ {paid_count} comissões pagas: {fmt_brl(paid_total)}")


def main():
    data = load_data()
    args = sys.argv[1:]

    if "--pay-pending" in args:
        pay_pending(data)
    elif "--report" in args:
        print_summary(data)
    else:
        # Default: print summary filtered by period if provided
        period = None
        for a in args:
            if a.startswith("--period="):
                period = a.split("=")[1]
        print_summary(data)


if __name__ == "__main__":
    main()
