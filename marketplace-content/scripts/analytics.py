"""Analytics for Marketplace performance tracking."""
import csv, json
from pathlib import Path
from datetime import datetime

class MarketplaceAnalytics:
    def __init__(self, data_dir="analytics_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def log_sale(self, pack_name, price, rating=None):
        """Log a sale entry."""
        row = {
            "timestamp": datetime.now().isoformat(),
            "pack": pack_name,
            "price": price,
            "creator_earnings": price * 0.70,
            "rating": rating or 0,
        }
        log_file = self.data_dir / "sales.csv"
        write_header = not log_file.exists()
        with open(log_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def summary(self):
        """Print summary from sales log."""
        log_file = self.data_dir / "sales.csv"
        if not log_file.exists():
            print("No sales data yet.")
            return
        with open(log_file) as f:
            rows = list(csv.DictReader(f))
        total = sum(float(r["creator_earnings"]) for r in rows)
        by_pack = {}
        for r in rows:
            by_pack.setdefault(r["pack"], []).append(r)
        print(f"=== ANALYTICS SUMMARY ===")
        print(f"Total sales: {len(rows)}")
        print(f"Total revenue: ${total:.2f}")
        print(f"\nPer pack:")
        for pack, sales in sorted(by_pack.items(), key=lambda x: -len(x[1])):
            rev = sum(float(s["creator_earnings"]) for s in sales)
            print(f"  {pack}: {len(sales)} sales, ${rev:.2f}")

if __name__ == "__main__":
    a = MarketplaceAnalytics()
    a.summary()
