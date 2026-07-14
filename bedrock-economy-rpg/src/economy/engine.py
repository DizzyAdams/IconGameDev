class EconomyEngine:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db
        self.cfg = plugin.cfg["economy"]
        self._cache = plugin._cache

    async def get_balance(self, xuid: str) -> int:
        cached = await self._cache.get(f"eco:{xuid}")
        if cached is not None:
            return int(cached)
        row = await self.db.fetchrow(
            "SELECT coins FROM players WHERE xuid = $1", xuid
        )
        bal = row["coins"] if row else self.cfg["start_balance"]
        await self._cache.set(f"eco:{xuid}", str(bal), 60)
        return bal

    async def set_balance(self, xuid: str, amount: int):
        await self.db.execute(
            "UPDATE players SET coins = $1 WHERE xuid = $2", amount, xuid
        )
        await self._cache.set(f"eco:{xuid}", str(amount), 60)

    async def add(self, xuid: str, amount: int) -> int:
        bal = await self.get_balance(xuid)
        bal += amount
        await self.set_balance(xuid, bal)
        return bal

    async def remove(self, xuid: str, amount: int) -> bool:
        bal = await self.get_balance(xuid)
        if bal < amount:
            return False
        bal -= amount
        await self.set_balance(xuid, bal)
        return True

    async def transfer(self, from_xuid: str, to_xuid: str, amount: int) -> bool:
        tax = int(amount * self.cfg["transfer_tax"])
        total = amount + tax
        if not await self.remove(from_xuid, total):
            return False
        await self.add(to_xuid, amount)
        return True
