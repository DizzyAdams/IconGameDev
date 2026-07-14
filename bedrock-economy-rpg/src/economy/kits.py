from datetime import datetime, timezone, timedelta

KITS = {
    "starter": {"cooldown_hours": 24, "price": 0, "items": [("stone_pickaxe", 1), ("bread", 16), ("torch", 8)]},
    "miner": {"cooldown_hours": 12, "price": 500, "items": [("iron_pickaxe", 1), ("torch", 32), ("cooked_beef", 8)]},
    "warrior": {"cooldown_hours": 12, "price": 500, "items": [("iron_sword", 1), ("shield", 1), ("golden_apple", 2)]},
    "farmer": {"cooldown_hours": 6, "price": 200, "items": [("iron_hoe", 1), ("wheat_seeds", 16), ("bone_meal", 8)]},
    "archer": {"cooldown_hours": 12, "price": 750, "items": [("bow", 1), ("arrow", 32), ("leather_chestplate", 1)]},
    "enchanter": {"cooldown_hours": 24, "price": 2000, "items": [("book", 3), ("lapis_lazuli", 32), ("obsidian", 4)]},
}


class Kits:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS economy_kit_cooldowns ("
            "xuid VARCHAR(32) NOT NULL, "
            "kit_name VARCHAR(64) NOT NULL, "
            "claimed_at TIMESTAMPTZ DEFAULT NOW(), "
            "PRIMARY KEY (xuid, kit_name))"
        )

    async def claim(self, xuid, kit_name):
        kit = KITS.get(kit_name)
        if not kit:
            return False, "Kit not found", None

        await self._ensure_tables()

        async with self.db.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "SELECT claimed_at FROM economy_kit_cooldowns WHERE xuid = $1 AND kit_name = $2",
                    xuid, kit_name
                )
                now = datetime.now(timezone.utc)
                if row:
                    elapsed = (now - row["claimed_at"]).total_seconds()
                    cooldown_secs = kit["cooldown_hours"] * 3600
                    if elapsed < cooldown_secs:
                        remaining = int(cooldown_secs - elapsed)
                        return False, f"Cooldown: {remaining//3600}h {(remaining%3600)//60}m", None

                if kit["price"] > 0:
                    player = await conn.fetchrow(
                        "SELECT coins FROM players WHERE xuid = $1 FOR UPDATE", xuid
                    )
                    if not player or player["coins"] < kit["price"]:
                        return False, "Insufficient coins", None
                    await conn.execute(
                        "UPDATE players SET coins = coins - $1 WHERE xuid = $2", kit["price"], xuid
                    )

                await conn.execute(
                    "INSERT INTO economy_kit_cooldowns (xuid, kit_name, claimed_at) "
                    "VALUES ($1, $2, $3) "
                    "ON CONFLICT (xuid, kit_name) DO UPDATE SET claimed_at = $3",
                    xuid, kit_name, now
                )

        return True, f"Kit {kit_name} claimed", kit["items"]

    async def get_cooldown(self, xuid, kit_name):
        kit = KITS.get(kit_name)
        if not kit:
            return 0
        await self._ensure_tables()
        row = await self.db.fetchrow(
            "SELECT claimed_at FROM economy_kit_cooldowns WHERE xuid = $1 AND kit_name = $2",
            xuid, kit_name
        )
        if not row:
            return 0
        elapsed = (datetime.now(timezone.utc) - row["claimed_at"]).total_seconds()
        cooldown_secs = kit["cooldown_hours"] * 3600
        remaining = int(cooldown_secs - elapsed)
        return max(0, remaining)
