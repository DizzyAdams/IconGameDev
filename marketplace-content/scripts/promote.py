"""Promotion & content calendar helper."""
import json, webbrowser
from datetime import datetime, timedelta

CONTENT_CALENDAR = [
    {"date": "Week 1", "action": "Apply to Partner Program"},
    {"date": "Week 2", "action": "Create TikTok: 15s skin showcase (Medieval Knights)"},
    {"date": "Week 3", "action": "Post to r/Minecraft: skin pack preview"},
    {"date": "Week 4", "action": "Create YouTube Short: 'How I made Minecraft skins'"},
    {"date": "Week 5", "action": "Discord: join 3 Minecraft creator servers"},
    {"date": "Week 6", "action": "TikTok: Anime Warriors behind-the-scenes"},
    {"date": "Week 7", "action": "Seasonal content: Halloween skin pack prep"},
    {"date": "Week 8", "action": "Check Partner Program status, follow up"},
]

PRICING = {
    "medieval-knights": {"price": "$1.99", "minecoins": 310, "earnings_per_sale": "$1.39"},
    "anime-warriors": {"price": "$1.99", "minecoins": 310, "earnings_per_sale": "$1.39"},
    "faithful-16x": {"price": "$2.99", "minecoins": 490, "earnings_per_sale": "$2.09"},
}

def print_calendar():
    print("=== CONTENT CALENDAR ===\n")
    for item in CONTENT_CALENDAR:
        print(f"  [{item['date']}] {item['action']}")

def print_pricing():
    print("\n=== PRICING STRATEGY ===\n")
    for pack, info in PRICING.items():
        print(f"  {pack}:")
        for k, v in info.items():
            print(f"    {k}: {v}")
        print()

def print_revenue_projection():
    print("=== REVENUE PROJECTION (70% share) ===\n")
    total = 0
    for name, info in PRICING.items():
        price = float(info["price"].replace("$", ""))
        dl = {"medieval-knights": 150, "anime-warriors": 120, "faithful-16x": 50}[name]
        rev = price * 0.7 * dl
        total += rev
        print(f"  {name}: ${price} × 70% × {dl} dl/mo = ${rev:.0f}/mo")
    print(f"\n  TOTAL: ${total:.0f}/mo")
    status = "MET" if total >= 400 else f"NEED {round(400 - total)} MORE"
    print(f"  Goal: $400/mo — {status}")

if __name__ == "__main__":
    print_calendar()
    print_pricing()
    print_revenue_projection()
