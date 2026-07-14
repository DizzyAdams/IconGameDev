from datetime import datetime, timezone, timedelta

BASE_INTEREST = 0.005
TIER_RATES = [
    (0, 0.005),
    (10000, 0.0075),
    (50000, 0.01),
    (100000, 0.015),
    (500000, 0.025),
]


class Banking:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_account(self, xuid):
        await self.db.execute(
            "INSERT INTO economy_banking (xuid, balance, interest_rate, last_interest_paid) "
            "VALUES ($1, 0, $2, NOW()) ON CONFLICT (xuid) DO NOTHING",
            xuid, BASE_INTEREST
        )

    async def deposit(self, xuid, amount):
        if amount <= 0:
            return False, "Amount must be positive"
        async with self.db.acquire() as conn:
            async with conn.transaction():
                player = await conn.fetchrow("SELECT coins FROM players WHERE xuid = $1 FOR UPDATE", xuid)
                if not player or player["coins"] < amount:
                    return False, "Insufficient coins"
                await self._ensure_account(xuid)
                await conn.execute("UPDATE players SET coins = coins - $1 WHERE xuid = $2", amount, xuid)
                await conn.execute(
                    "UPDATE economy_banking SET balance = balance + $1 WHERE xuid = $2", amount, xuid
                )
                await conn.execute(
                    "INSERT INTO economy_transactions (from_xuid, to_xuid, amount, type) "
                    "VALUES ($1, NULL, $2, 'bank_deposit')", xuid, amount
                )
        return True, f"Deposited {amount} coins"

    async def withdraw(self, xuid, amount):
        if amount <= 0:
            return False, "Amount must be positive"
        async with self.db.acquire() as conn:
            async with conn.transaction():
                bank = await conn.fetchrow(
                    "SELECT balance FROM economy_banking WHERE xuid = $1 FOR UPDATE", xuid
                )
                if not bank or bank["balance"] < amount:
                    return False, "Insufficient bank balance"
                await conn.execute(
                    "UPDATE economy_banking SET balance = balance - $1 WHERE xuid = $2", amount, xuid
                )
                await conn.execute("UPDATE players SET coins = coins + $1 WHERE xuid = $2", amount, xuid)
                await conn.execute(
                    "INSERT INTO economy_transactions (from_xuid, to_xuid, amount, type) "
                    "VALUES (NULL, $1, $2, 'bank_withdraw')", xuid, amount
                )
        return True, f"Withdrew {amount} coins"

    async def get_balance(self, xuid):
        await self._ensure_account(xuid)
        row = await self.db.fetchrow("SELECT balance FROM economy_banking WHERE xuid = $1", xuid)
        return row["balance"] if row else 0

    async def apply_interest(self):
        updated = await self.db.fetch(
            "UPDATE economy_banking b "
            "SET balance = balance + CAST(balance * b.interest_rate AS BIGINT), "
            "last_interest_paid = NOW() "
            "WHERE balance > 0 "
            "RETURNING xuid, balance, CAST(balance * b.interest_rate AS BIGINT) AS interest"
        )
        for row in updated:
            await self.db.execute(
                "INSERT INTO economy_transactions (from_xuid, to_xuid, amount, type) "
                "VALUES (NULL, $1, $2, 'bank_interest')", row["xuid"], row["interest"]
            )
        return len(updated)

    async def get_interest_rate(self, xuid):
        await self._ensure_account(xuid)
        row = await self.db.fetchrow(
            "SELECT balance, interest_rate FROM economy_banking WHERE xuid = $1", xuid
        )
        if not row:
            return BASE_INTEREST
        rate = row["interest_rate"]
        for threshold, tier_rate in TIER_RATES:
            if row["balance"] >= threshold:
                rate = tier_rate
        if rate != row["interest_rate"]:
            await self.db.execute(
                "UPDATE economy_banking SET interest_rate = $1 WHERE xuid = $2", rate, xuid
            )
        return float(rate)
