class PlayerShops:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def create_shop(self, owner_xuid, item_id, amount, buy_price, sell_price):
        row = await self.db.fetchrow(
            "INSERT INTO economy_shops (owner_xuid, item_id, item_data, amount, buy_price, sell_price) "
            "VALUES ($1, $2, 0, $3, $4, $5) RETURNING id",
            owner_xuid, item_id, amount, buy_price, sell_price
        )
        return row["id"]

    async def buy_from_shop(self, shop_id, buyer_xuid, amount):
        async with self.db.acquire() as conn:
            async with conn.transaction():
                shop = await conn.fetchrow(
                    "SELECT * FROM economy_shops WHERE id = $1 AND buy_price IS NOT NULL FOR UPDATE", shop_id
                )
                if not shop:
                    return False, "Shop not found or not accepting purchases"
                if shop["amount"] < amount:
                    return False, "Not enough stock"
                cost = shop["buy_price"] * amount
                buyer = await conn.fetchrow("SELECT coins FROM players WHERE xuid = $1 FOR UPDATE", buyer_xuid)
                if not buyer or buyer["coins"] < cost:
                    return False, "Insufficient funds"

                await conn.execute("UPDATE players SET coins = coins - $1 WHERE xuid = $2", cost, buyer_xuid)
                await conn.execute(
                    "UPDATE players SET coins = coins + $1 WHERE xuid = $2", cost, shop["owner_xuid"]
                )
                await conn.execute(
                    "UPDATE economy_shops SET amount = amount - $1 WHERE id = $2", amount, shop_id
                )
                await conn.execute(
                    "INSERT INTO economy_transactions (from_xuid, to_xuid, amount, type) "
                    "VALUES ($1, $2, $3, 'shop_buy')", buyer_xuid, shop["owner_xuid"], cost
                )
        return True, {"item_id": shop["item_id"], "amount": amount}

    async def sell_to_shop(self, shop_id, seller_xuid, amount):
        async with self.db.acquire() as conn:
            async with conn.transaction():
                shop = await conn.fetchrow(
                    "SELECT * FROM economy_shops WHERE id = $1 AND sell_price IS NOT NULL FOR UPDATE", shop_id
                )
                if not shop:
                    return False, "Shop not found or not accepting sells"
                revenue = shop["sell_price"] * amount

                await conn.execute("UPDATE players SET coins = coins + $1 WHERE xuid = $2", revenue, seller_xuid)
                await conn.execute(
                    "UPDATE players SET coins = coins - $1 WHERE xuid = $2", revenue, shop["owner_xuid"]
                )
                await conn.execute(
                    "UPDATE economy_shops SET amount = amount + $1 WHERE id = $2", amount, shop_id
                )
                await conn.execute(
                    "INSERT INTO economy_transactions (from_xuid, to_xuid, amount, type) "
                    "VALUES ($1, $2, $3, 'shop_sell')", shop["owner_xuid"], seller_xuid, revenue
                )
        return True, {"item_id": shop["item_id"], "amount": amount}

    async def get_nearby(self, x, z, radius=50):
        rows = await self.db.fetch(
            "SELECT s.*, p.name AS owner_name FROM economy_shops s "
            "LEFT JOIN players p ON p.xuid = s.owner_xuid "
            "ORDER BY s.created_at DESC"
        )
        return list(rows)
