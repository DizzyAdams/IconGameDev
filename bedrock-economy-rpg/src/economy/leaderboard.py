class Leaderboard:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def top_balance(self, limit=10):
        rows = await self.db.fetch(
            "SELECT xuid, name, coins FROM players ORDER BY coins DESC LIMIT $1", limit
        )
        return [{"rank": i + 1, "xuid": r["xuid"], "name": r["name"], "value": r["coins"]}
                for i, r in enumerate(rows)]

    async def top_level(self, limit=10):
        rows = await self.db.fetch(
            "SELECT xuid, name, level, xp FROM players ORDER BY level DESC, xp DESC LIMIT $1", limit
        )
        return [{"rank": i + 1, "xuid": r["xuid"], "name": r["name"], "level": r["level"], "xp": r["xp"]}
                for i, r in enumerate(rows)]

    async def top_gems(self, limit=10):
        rows = await self.db.fetch(
            "SELECT xuid, name, gems FROM players ORDER BY gems DESC LIMIT $1", limit
        )
        return [{"rank": i + 1, "xuid": r["xuid"], "name": r["name"], "value": r["gems"]}
                for i, r in enumerate(rows)]

    async def top_playtime(self, limit=10):
        rows = await self.db.fetch(
            "SELECT xuid, name, playtime_seconds FROM players ORDER BY playtime_seconds DESC LIMIT $1", limit
        )
        return [{"rank": i + 1, "xuid": r["xuid"], "name": r["name"],
                 "value": r["playtime_seconds"]}
                for i, r in enumerate(rows)]

    async def display_sidebar(self, players):
        lines = ["§6=== LEADERBOARD ==="]
        for p in players:
            lines.append(f"§e#{p['rank']} §f{p['name']} §7- §a{p['value']}")
        return "\n".join(lines)
