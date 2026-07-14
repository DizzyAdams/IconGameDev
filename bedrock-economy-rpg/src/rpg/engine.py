import math


class RpgEngine:
    XP_PER_LEVEL_BASE = 100
    XP_PER_LEVEL_FACTOR = 1.5

    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db
        self.cfg = plugin.cfg["rpg"]

    def xp_for_level(self, level: int) -> int:
        return int(self.XP_PER_LEVEL_BASE * (self.XP_PER_LEVEL_FACTOR ** (level - 1)))

    async def get_player(self, xuid: str) -> dict:
        row = await self.db.fetchrow(
            "SELECT class, level, xp, gems FROM players WHERE xuid = $1", xuid
        )
        if row:
            return dict(row)
        return {"class": "adventurer", "level": 1, "xp": 0, "gems": 0}

    async def set_class(self, xuid: str, cls: str):
        if cls not in self.cfg["classes"]:
            return False
        await self.db.execute(
            "UPDATE players SET class = $1 WHERE xuid = $2", cls, xuid
        )
        return True

    async def add_xp(self, xuid: str, amount: int) -> dict:
        data = await self.get_player(xuid)
        new_xp = data["xp"] + int(amount * self.cfg["xp_multiplier"])
        new_level = data["level"]
        gained_levels = 0

        while new_xp >= self.xp_for_level(new_level) and new_level < self.cfg["max_level"]:
            new_xp -= self.xp_for_level(new_level)
            new_level += 1
            gained_levels += 1
            gem_reward = gained_levels * 5
            await self.db.execute(
                "UPDATE players SET gems = gems + $1 WHERE xuid = $2",
                gem_reward, xuid,
            )

        await self.db.execute(
            "UPDATE players SET level = $1, xp = $2 WHERE xuid = $3",
            new_level, new_xp, xuid,
        )
        return {"level": new_level, "xp": new_xp, "gained_levels": gained_levels}
