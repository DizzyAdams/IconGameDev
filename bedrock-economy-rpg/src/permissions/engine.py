PERM_GROUPS = {
    "default": {"prefix": "§7", "priority": 0},
    "vip":     {"prefix": "§a[VIP] ", "priority": 1},
    "mod":     {"prefix": "§9[Mod] ", "priority": 2},
    "admin":   {"prefix": "§c[Admin] ", "priority": 3},
    "owner":   {"prefix": "§4[Owner] ", "priority": 4},
}


class PermissionEngine:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def get_group(self, xuid: str) -> str:
        row = await self.db.fetchrow(
            "SELECT perm_group FROM players WHERE xuid = $1", xuid
        )
        return row["perm_group"] if row else "default"

    async def set_group(self, xuid: str, group: str) -> bool:
        if group not in PERM_GROUPS:
            return False
        await self.db.execute(
            "UPDATE players SET perm_group = $1 WHERE xuid = $2", group, xuid
        )
        return True

    def has_permission(self, group: str, required: str) -> bool:
        g = PERM_GROUPS.get(group, PERM_GROUPS["default"])
        r = PERM_GROUPS.get(required, PERM_GROUPS["default"])
        return g["priority"] >= r["priority"]

    def get_prefix(self, group: str) -> str:
        return PERM_GROUPS.get(group, PERM_GROUPS["default"])["prefix"]
