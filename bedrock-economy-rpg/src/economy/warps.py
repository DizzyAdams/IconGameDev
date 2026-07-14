class Warps:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS economy_warps ("
            "id BIGSERIAL PRIMARY KEY, "
            "owner_xuid VARCHAR(32) NOT NULL, "
            "name VARCHAR(64) NOT NULL, "
            "x DOUBLE PRECISION NOT NULL, "
            "y DOUBLE PRECISION NOT NULL, "
            "z DOUBLE PRECISION NOT NULL, "
            "dimension VARCHAR(32) NOT NULL, "
            "price BIGINT DEFAULT 0, "
            "visits BIGINT DEFAULT 0, "
            "created_at TIMESTAMPTZ DEFAULT NOW(), "
            "UNIQUE(owner_xuid, name))"
        )

    async def create_warp(self, xuid, name, x, y, z, dimension, price=0):
        await self._ensure_tables()
        try:
            row = await self.db.fetchrow(
                "INSERT INTO economy_warps (owner_xuid, name, x, y, z, dimension, price) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id",
                xuid, name, x, y, z, dimension, price
            )
            return True, row["id"]
        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return False, "Warp name already exists"
            return False, str(e)

    async def warp(self, xuid, warp_name):
        async with self.db.acquire() as conn:
            async with conn.transaction():
                warp = await conn.fetchrow(
                    "SELECT * FROM economy_warps WHERE LOWER(name) = LOWER($1) FOR UPDATE", warp_name
                )
                if not warp:
                    return False, "Warp not found", None

                if warp["price"] > 0 and warp["owner_xuid"] != xuid:
                    player = await conn.fetchrow(
                        "SELECT coins FROM players WHERE xuid = $1 FOR UPDATE", xuid
                    )
                    if not player or player["coins"] < warp["price"]:
                        return False, "Insufficient coins", None
                    await conn.execute(
                        "UPDATE players SET coins = coins - $1 WHERE xuid = $2", warp["price"], xuid
                    )
                    await conn.execute(
                        "UPDATE players SET coins = coins + $1 WHERE xuid = $2",
                        warp["price"], warp["owner_xuid"]
                    )

                await conn.execute(
                    "UPDATE economy_warps SET visits = visits + 1 WHERE id = $1", warp["id"]
                )

        return True, f"Warping to {warp['name']}", {
            "x": warp["x"], "y": warp["y"], "z": warp["z"],
            "dimension": warp["dimension"]
        }

    async def list_warps(self, page=0, per_page=10):
        offset = page * per_page
        rows = await self.db.fetch(
            "SELECT w.*, p.name AS owner_name FROM economy_warps w "
            "LEFT JOIN players p ON p.xuid = w.owner_xuid "
            "ORDER BY w.visits DESC LIMIT $1 OFFSET $2",
            per_page, offset
        )
        total = await self.db.fetchval("SELECT COUNT(*) FROM economy_warps")
        return {"items": list(rows), "total": total, "page": page, "per_page": per_page}

    async def delete_warp(self, xuid, warp_name):
        result = await self.db.execute(
            "DELETE FROM economy_warps WHERE owner_xuid = $1 AND LOWER(name) = LOWER($2)",
            xuid, warp_name
        )
        if result == "DELETE 0" or (isinstance(result, str) and "0" in result):
            return False, "Warp not found or not yours"
        return True, "Warp deleted"
