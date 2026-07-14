from datetime import datetime, timezone, timedelta


class AuctionHouse:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def list_item(self, seller_xuid, item_id, amount, starting_bid, buyout_price=None, duration_hours=24):
        ends_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        row = await self.db.fetchrow(
            "INSERT INTO economy_auctions (seller_xuid, item_id, item_data, amount, starting_bid, buyout_price, ends_at) "
            "VALUES ($1, $2, 0, $3, $4, $5, $6) RETURNING id",
            seller_xuid, item_id, amount, starting_bid, buyout_price, ends_at
        )
        return row["id"]

    async def place_bid(self, auction_id, bidder_xuid, amount):
        async with self.db.acquire() as conn:
            async with conn.transaction():
                auction = await conn.fetchrow(
                    "SELECT * FROM economy_auctions WHERE id = $1 AND status = 'active' FOR UPDATE",
                    auction_id
                )
                if not auction:
                    return False, "Auction not found or expired"
                min_bid = auction["current_bid"] if auction["current_bid"] else auction["starting_bid"]
                if amount <= min_bid:
                    return False, "Bid must be higher than current bid"
                if auction["buyout_price"] and amount >= auction["buyout_price"]:
                    return False, "Use /ah buyout instead"

                row = await conn.fetchrow("SELECT coins FROM players WHERE xuid = $1 FOR UPDATE", bidder_xuid)
                if not row or row["coins"] < amount:
                    return False, "Insufficient funds"

                if auction["bidder_xuid"]:
                    await conn.execute(
                        "UPDATE players SET coins = coins + $1 WHERE xuid = $2",
                        auction["current_bid"], auction["bidder_xuid"]
                    )

                await conn.execute("UPDATE players SET coins = coins - $1 WHERE xuid = $2", amount, bidder_xuid)
                await conn.execute(
                    "UPDATE economy_auctions SET current_bid = $1, bidder_xuid = $2 WHERE id = $3",
                    amount, bidder_xuid, auction_id
                )
                await conn.execute(
                    "INSERT INTO economy_transactions (from_xuid, to_xuid, amount, type) "
                    "VALUES ($1, NULL, $2, 'auction_bid')", bidder_xuid, amount
                )
        return True, "Bid placed"

    async def buyout(self, auction_id, buyer_xuid):
        async with self.db.acquire() as conn:
            async with conn.transaction():
                auction = await conn.fetchrow(
                    "SELECT * FROM economy_auctions WHERE id = $1 AND status = 'active' FOR UPDATE",
                    auction_id
                )
                if not auction or not auction["buyout_price"]:
                    return False, "Buyout not available"

                buyer = await conn.fetchrow("SELECT coins FROM players WHERE xuid = $1 FOR UPDATE", buyer_xuid)
                if not buyer or buyer["coins"] < auction["buyout_price"]:
                    return False, "Insufficient funds"

                price = auction["buyout_price"]
                if auction["bidder_xuid"] and auction["current_bid"]:
                    await conn.execute(
                        "UPDATE players SET coins = coins + $1 WHERE xuid = $2",
                        auction["current_bid"], auction["bidder_xuid"]
                    )

                await conn.execute("UPDATE players SET coins = coins - $1 WHERE xuid = $2", price, buyer_xuid)
                await conn.execute(
                    "UPDATE players SET coins = coins + $1 WHERE xuid = $2", price, auction["seller_xuid"]
                )
                await conn.execute(
                    "UPDATE economy_auctions SET status = 'completed', current_bid = $1, bidder_xuid = $2 WHERE id = $3",
                    price, buyer_xuid, auction_id
                )
                await conn.execute(
                    "INSERT INTO economy_transactions (from_xuid, to_xuid, amount, type) "
                    "VALUES ($1, $2, $3, 'auction_buyout')", buyer_xuid, auction["seller_xuid"], price
                )
        return True, {
            "item_id": auction["item_id"], "amount": auction["amount"],
            "seller_xuid": auction["seller_xuid"]
        }

    async def get_active(self, page=0, per_page=10):
        offset = page * per_page
        rows = await self.db.fetch(
            "SELECT a.*, p.name AS seller_name FROM economy_auctions a "
            "LEFT JOIN players p ON p.xuid = a.seller_xuid "
            "WHERE a.status = 'active' ORDER BY a.ends_at ASC LIMIT $1 OFFSET $2",
            per_page, offset
        )
        total = await self.db.fetchval("SELECT COUNT(*) FROM economy_auctions WHERE status = 'active'")
        return {"items": list(rows), "total": total, "page": page, "per_page": per_page}

    async def expire_old(self):
        now = datetime.now(timezone.utc)
        expired = await self.db.fetch(
            "UPDATE economy_auctions SET status = 'expired' "
            "WHERE status = 'active' AND ends_at <= $1 "
            "RETURNING id, seller_xuid, current_bid, bidder_xuid", now
        )
        for a in expired:
            if a["bidder_xuid"] and a["current_bid"]:
                await self.db.execute(
                    "UPDATE players SET coins = coins + $1 WHERE xuid = $2",
                    a["current_bid"], a["bidder_xuid"]
                )
        return len(expired)
