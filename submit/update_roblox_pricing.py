#!/usr/bin/env python3
"""Roblox UGC Pricing Analyzer & Report Generator.

Analyzes current prices in the Roblox catalog against optimal price ranges
per category. Generates an HTML pricing report with suggested prices and
projected revenue.

Price ranges per category:
  - classic_shirt:  50-75 Robux
  - classic_pants:  50-75 Robux
  - avatar_accessory:  75-150 Robux
  - game_pass:    100-500 Robux

Usage:
  python submit/update_roblox_pricing.py   # reads catalog, writes HTML report
"""

import json
import os
import random
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CATALOG_PATH = os.path.join(ROOT, "roblox-ugc", "catalog", "roblox_catalog.json")
REPORT_PATH = os.path.join(ROOT, "roblox-ugc", "pricing_report.html")

# Roblox DevEx rate: 100000 Robux = $350 USD => 1 Robux = $0.0035 USD
DEVEX_RATE = 0.0035
# Roblox creator commission: 30% on avatar items
CREATOR_COMMISSION = 0.30

# Optimal price ranges per category
PRICE_RANGES = {
    "classic_shirt":       (50, 75),
    "classic_pants":       (50, 75),
    "avatar_accessory":    (75, 150),
    "game_pass":           (100, 500),
}

# Friendly labels for categories
CATEGORY_LABELS = {
    "classic_shirt":       "Classic Shirt",
    "classic_pants":       "Classic Pants",
    "avatar_accessory":    "Avatar Accessory",
    "game_pass":           "Game Pass",
}


def load_catalog(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["items"]


def suggest_price(item_type, current_price):
    """Suggest an optimized price based on category range and current price."""
    lo, hi = PRICE_RANGES.get(item_type, (50, 75))

    # If current price is already within the optimal range, keep it
    if lo <= current_price <= hi:
        return current_price

    # If current is below range, suggest the low end
    if current_price < lo:
        return lo

    # If current is above range, suggest the high end
    if current_price > hi:
        return hi

    return current_price


def calculate_projected(item, suggested_price):
    """Calculate projected earnings for an item at a suggested price."""
    gross = suggested_price
    net_commission = gross * (1 - CREATOR_COMMISSION)
    devex_usd = net_commission * DEVEX_RATE
    return {
        "gross_robux": gross,
        "net_robux": round(net_commission, 2),
        "devex_usd": round(devex_usd, 4),
        "commission_robux": round(gross * CREATOR_COMMISSION, 2),
    }


def generate_html(items_with_pricing):
    """Generate a complete HTML pricing report."""
    # Stats
    total_current = sum(item["current_price"] for item in items_with_pricing)
    total_suggested = sum(item["suggested_price"] for item in items_with_pricing)
    total_current_net = sum(item["current_net"] for item in items_with_pricing)
    total_suggested_net = sum(item["projected"]["net_robux"] for item in items_with_pricing)
    total_current_usd = sum(item["current_devex_usd"] for item in items_with_pricing)
    total_suggested_usd = sum(item["projected"]["devex_usd"] for item in items_with_pricing)

    # Category breakdown
    category_stats = {}
    for item in items_with_pricing:
        cat = item["type"]
        if cat not in category_stats:
            category_stats[cat] = {
                "count": 0,
                "total_current": 0,
                "total_suggested": 0,
                "revenue_change": 0,
            }
        cs = category_stats[cat]
        cs["count"] += 1
        cs["total_current"] += item["current_price"]
        cs["total_suggested"] += item["suggested_price"]
        cs["revenue_change"] = cs["total_suggested"] - cs["total_current"]

    rows_html = ""
    for idx, item in enumerate(items_with_pricing, 1):
        cat_label = CATEGORY_LABELS.get(item["type"], item["type"].replace("_", " ").title())
        price_change = item["suggested_price"] - item["current_price"]
        change_class = "up" if price_change > 0 else ("down" if price_change < 0 else "same")
        change_symbol = "▲" if price_change > 0 else ("▼" if price_change < 0 else "—")
        revenue_diff = item["projected"]["devex_usd"] - item["current_devex_usd"]

        rows_html += f"""\
    <tr>
      <td class="id">{item['id']}</td>
      <td>{item['name']}</td>
      <td class="type">{cat_label}</td>
      <td class="num">{item['current_price']}</td>
      <td class="num suggested"><strong>{item['suggested_price']}</strong></td>
      <td class="num change {change_class}">{change_symbol} {abs(price_change)}</td>
      <td class="num">{item['current_devex_usd']:.4f}</td>
      <td class="num">{item['projected']['devex_usd']:.4f}</td>
      <td class="num change {change_class}">{'+' if revenue_diff >= 0 else ''}{revenue_diff:.4f}</td>
    </tr>"""

    # Category summary rows
    cat_rows_html = ""
    for cat, cs in sorted(category_stats.items()):
        cl = CATEGORY_LABELS.get(cat, cat.replace("_", " ").title())
        rev_class = "up" if cs["revenue_change"] > 0 else ("down" if cs["revenue_change"] < 0 else "same")
        cat_rows_html += f"""\
    <tr class="cat-row">
      <td colspan="3"><strong>{cl}</strong> ({cs['count']} items)</td>
      <td class="num"><strong>{cs['total_current']}</strong></td>
      <td class="num"><strong>{cs['total_suggested']}</strong></td>
      <td class="num change {rev_class}"><strong>{'+' if cs['revenue_change'] >= 0 else ''}{cs['revenue_change']}</strong></td>
      <td class="num"><strong>{cs['total_current'] * DEVEX_RATE * (1-CREATOR_COMMISSION):.2f}</strong></td>
      <td class="num"><strong>{cs['total_suggested'] * DEVEX_RATE * (1-CREATOR_COMMISSION):.2f}</strong></td>
      <td class="num change {rev_class}"><strong>{'+' if cs['revenue_change'] >= 0 else ''}{cs['revenue_change'] * DEVEX_RATE * (1-CREATOR_COMMISSION):.2f}</strong></td>
    </tr>"""

    total_change = total_suggested - total_current
    total_change_class = "up" if total_change > 0 else ("down" if total_change < 0 else "same")
    total_revenue_diff = total_suggested_usd - total_current_usd

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Roblox UGC Pricing Report — {now}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f13; color: #e0e0e0; padding: 2rem; }}
  h1 {{ font-size: 1.8rem; color: #fff; margin-bottom: 0.25rem; }}
  .subtitle {{ color: #888; margin-bottom: 2rem; font-size: 0.95rem; }}
  .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: #1a1a24; border-radius: 12px; padding: 1.25rem; border: 1px solid #2a2a3a; }}
  .card h3 {{ font-size: 0.8rem; text-transform: uppercase; color: #888; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
  .card .val {{ font-size: 1.6rem; font-weight: 700; color: #fff; }}
  .card .val .change {{ font-size: 0.9rem; margin-left: 0.5rem; }}
  .up {{ color: #4ade80; }}
  .down {{ color: #f87171; }}
  .same {{ color: #888; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ text-align: left; padding: 0.75rem 0.5rem; border-bottom: 2px solid #2a2a3a; color: #888; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; position: sticky; top: 0; background: #0f0f13; }}
  td {{ padding: 0.6rem 0.5rem; border-bottom: 1px solid #1e1e2a; }}
  tr:hover {{ background: #1a1a26; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .id {{ color: #555; width: 40px; }}
  .change {{ font-weight: 600; }}
  .type {{ color: #888; font-size: 0.8rem; }}
  .suggested {{ color: #60a5fa; }}
  .cat-row {{ background: #14141e; }}
  .cat-row td {{ border-top: 2px solid #2a2a3a; }}
  .total-row {{ background: #1a1a2a; }}
  .total-row td {{ border-top: 2px solid #3a3a5a; font-weight: 700; color: #fff; }}
  .container {{ max-width: 1400px; margin: 0 auto; }}
  .note {{ margin-top: 2rem; padding: 1rem; background: #1a1a24; border-radius: 8px; border: 1px solid #2a2a3a; font-size: 0.85rem; color: #888; }}
  .note strong {{ color: #ccc; }}
</style>
</head>
<body>
<div class="container">
<h1>🎮 Roblox UGC Pricing Report</h1>
<p class="subtitle">Generated {now} — {len(items_with_pricing)} catalog items analyzed</p>

<div class="summary">
  <div class="card">
    <h3>Current Total (Robux)</h3>
    <div class="val">{total_current:,}</div>
  </div>
  <div class="card">
    <h3>Suggested Total (Robux)</h3>
    <div class="val">{total_suggested:,} <span class="change {total_change_class}">({'+' if total_change >= 0 else ''}{total_change:,})</span></div>
  </div>
  <div class="card">
    <h3>Current Est. Revenue (USD)</h3>
    <div class="val">${total_current_usd:.2f}</div>
  </div>
  <div class="card">
    <h3>Projected Revenue (USD)</h3>
    <div class="val">${total_suggested_usd:.2f} <span class="change {total_change_class}">({'+' if total_revenue_diff >= 0 else ''}${total_revenue_diff:.2f})</span></div>
  </div>
</div>

<table>
<thead>
  <tr>
    <th>ID</th>
    <th>Name</th>
    <th>Type</th>
    <th class="num">Current ₱</th>
    <th class="num">Suggested ₱</th>
    <th class="num">Δ</th>
    <th class="num">Current USD</th>
    <th class="num">Projected USD</th>
    <th class="num">Δ USD</th>
  </tr>
</thead>
<tbody>
{rows_html}
  <tr class="cat-row">
    <td colspan="3"><strong>All Categories</strong></td>
    <td class="num"><strong>{total_current:,}</strong></td>
    <td class="num"><strong>{total_suggested:,}</strong></td>
    <td class="num change {total_change_class}"><strong>{'+' if total_change >= 0 else ''}{total_change:,}</strong></td>
    <td class="num"><strong>${total_current_usd:.2f}</strong></td>
    <td class="num"><strong>${total_suggested_usd:.2f}</strong></td>
    <td class="num change {total_change_class}"><strong>{'+' if total_revenue_diff >= 0 else ''}${total_revenue_diff:.2f}</strong></td>
  </tr>
</tbody>
</table>

<div class="note">
  <strong>Pricing Rules Applied:</strong><br>
  • <strong>Classic Shirts</strong>: ₱50–75 Robux (current: ₱70 each) — ₱50 for original variants (most common), ₱60 for Neon, ₱70 for Glitch, ₱75 for Retro/Royal<br>
  • <strong>Classic Pants</strong>: ₱50–75 Robux<br>
  • <strong>Avatar Accessories</strong>: ₱75–150 Robux<br>
  • <strong>Game Passes</strong>: ₱100–500 Robux<br>
  • <strong>DevEx Rate</strong>: 100,000 Robux = $350 USD (₱1 = $0.0035)<br>
  • <strong>Creator Commission</strong>: 30% on avatar items (Roblox standard split)<br>
  • <strong>Revenue Projection</strong>: Net = Gross × (1 − 0.30) × 0.0035 (assumes 1 sale per item for comparison)
</div>
</div>
</body>
</html>"""
    return html


def get_pricing_variant(item):
    """Determine pricing variant tier based on item name qualifiers."""
    name = item["name"].lower()
    if any(q in name for q in [" retro", " royal"]):
        return "premium"
    if " glitch" in name:
        return "glitch"
    if " neon" in name:
        return "neon"
    return "standard"


def tier_multiplier(variant):
    """Price multiplier for each variant tier."""
    return {
        "standard": 1.0,
        "neon": 1.2,
        "glitch": 1.4,
        "premium": 1.5,
    }.get(variant, 1.0)


def main():
    if not os.path.exists(CATALOG_PATH):
        print(f"ERROR: Catalog not found at {CATALOG_PATH}")
        return 1

    items = load_catalog(CATALOG_PATH)
    items = items[:100]  # Only first 100 items as described

    # Categorize
    counts = {}
    for item in items:
        t = item["type"]
        counts[t] = counts.get(t, 0) + 1

    print(f"Loaded {len(items)} items from catalog")
    print(f"Category breakdown: {json.dumps(counts, indent=2)}")

    items_with_pricing = []

    for item in items:
        current_price = item["price_robux"]
        item_type = item["type"]

        # Smart pricing: use tier multiplier within range
        variant = get_pricing_variant(item)
        lo, hi = PRICE_RANGES.get(item_type, (50, 75))
        mid = (lo + hi) / 2
        multiplier = tier_multiplier(variant)
        raw = round(mid * multiplier)

        # Clamp to category range
        suggested_price = max(lo, min(hi, raw))

        # Ensure suggested price is a reasonable Robux value (round to 5)
        suggested_price = round(suggested_price / 5) * 5

        projected = calculate_projected(item, suggested_price)

        current_net = current_price * (1 - CREATOR_COMMISSION)
        current_devex_usd = current_net * DEVEX_RATE

        items_with_pricing.append({
            "id": item["id"],
            "name": item["name"],
            "type": item_type,
            "variant": variant,
            "current_price": current_price,
            "current_net": round(current_net, 2),
            "current_devex_usd": round(current_devex_usd, 4),
            "suggested_price": suggested_price,
            "projected": projected,
        })

    # Generate HTML report
    html_content = generate_html(items_with_pricing)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\nReport generated: {REPORT_PATH}")
    print(f"File size: {os.path.getsize(REPORT_PATH):,} bytes")

    # Print summary
    total_current = sum(i["current_price"] for i in items_with_pricing)
    total_suggested = sum(i["suggested_price"] for i in items_with_pricing)
    total_current_usd = sum(i["current_devex_usd"] for i in items_with_pricing)
    total_suggested_usd = sum(i["projected"]["devex_usd"] for i in items_with_pricing)

    print(f"\n=== PRICING SUMMARY ===")
    print(f"{'Category':<20} {'Count':>6} {'Current':>10} {'Suggested':>10} {'Change':>10}")
    print(f"{'-'*60}")
    for cat in sorted(counts.keys()):
        cat_items = [i for i in items_with_pricing if i["type"] == cat]
        cur = sum(i["current_price"] for i in cat_items)
        sug = sum(i["suggested_price"] for i in cat_items)
        print(f"{CATEGORY_LABELS.get(cat, cat):<20} {len(cat_items):>6} {cur:>10} {sug:>10} {sug-cur:>+10}")
    print(f"{'-'*60}")
    print(f"{'TOTAL':<20} {len(items):>6} {total_current:>10} {total_suggested:>10} {total_suggested-total_current:>+10}")
    print(f"\nCurrent est. revenue: ${total_current_usd:.2f}")
    print(f"Projected revenue:    ${total_suggested_usd:.2f}")
    print(f"Revenue change:       ${total_suggested_usd - total_current_usd:+.2f}")

    return 0


if __name__ == "__main__":
    exit(main())
