from datetime import datetime, timezone


class GuildSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_guilds ("
            "id BIGSERIAL PRIMARY KEY, "
            "name VARCHAR(64) NOT NULL UNIQUE, "
            "level INT DEFAULT 1, "
            "xp INT DEFAULT 0, "
            "bank BIGINT DEFAULT 0, "
            "owner_xuid VARCHAR(32) NOT NULL, "
            "created_at TIMESTAMPTZ DEFAULT NOW())"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_guild_members ("
            "guild_id BIGINT NOT NULL REFERENCES rpg_guilds(id) ON DELETE CASCADE, "
            "xuid VARCHAR(32) NOT NULL, "
            "role VARCHAR(16) DEFAULT 'member', "
            "joined_at TIMESTAMPTZ DEFAULT NOW(), "
            "PRIMARY KEY (guild_id, xuid))"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_guild_invites ("
            "guild_id BIGINT NOT NULL REFERENCES rpg_guilds(id) ON DELETE CASCADE, "
            "xuid VARCHAR(32) NOT NULL, "
            "invited_by VARCHAR(32) NOT NULL, "
            "created_at TIMESTAMPTZ DEFAULT NOW(), "
            "PRIMARY KEY (guild_id, xuid))"
        )

    async def create(self, name, owner_xuid):
        await self._ensure_tables()

        in_guild = await self.db.fetchrow(
            "SELECT 1 FROM rpg_guild_members WHERE xuid = $1", owner_xuid
        )
        if in_guild:
            return False, "Already in a guild"

        try:
            row = await self.db.fetchrow(
                "INSERT INTO rpg_guilds (name, owner_xuid) VALUES ($1, $2) RETURNING id",
                name, owner_xuid
            )
            await self.db.execute(
                "INSERT INTO rpg_guild_members (guild_id, xuid, role) VALUES ($1, $2, 'owner')",
                row["id"], owner_xuid
            )
            return True, f"Guild '{name}' created", row["id"]
        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return False, "Guild name already taken"
            return False, str(e)

    async def invite(self, guild_id, inviter_xuid, target_xuid):
        row = await self.db.fetchrow(
            "SELECT role FROM rpg_guild_members WHERE guild_id = $1 AND xuid = $2",
            guild_id, inviter_xuid
        )
        if not row:
            return False, "Not a member of this guild"
        if row["role"] not in ("owner", "officer"):
            return False, "No permission to invite"

        target = await self.db.fetchrow(
            "SELECT 1 FROM rpg_guild_members WHERE xuid = $1", target_xuid
        )
        if target:
            return False, "Target already in a guild"

        await self.db.execute(
            "INSERT INTO rpg_guild_invites (guild_id, xuid, invited_by) VALUES ($1, $2, $3) "
            "ON CONFLICT (guild_id, xuid) DO UPDATE SET invited_by = $3, created_at = NOW()",
            guild_id, target_xuid, inviter_xuid
        )
        return True, "Invite sent"

    async def join(self, guild_id, xuid):
        invite = await self.db.fetchrow(
            "SELECT * FROM rpg_guild_invites WHERE guild_id = $1 AND xuid = $2",
            guild_id, xuid
        )
        if not invite:
            return False, "No invite"

        existing = await self.db.fetchrow(
            "SELECT 1 FROM rpg_guild_members WHERE xuid = $1", xuid
        )
        if existing:
            return False, "Already in a guild"

        async with self.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM rpg_guild_invites WHERE guild_id = $1 AND xuid = $2",
                    guild_id, xuid
                )
                await conn.execute(
                    "INSERT INTO rpg_guild_members (guild_id, xuid, role) VALUES ($1, $2, 'member')",
                    guild_id, xuid
                )
        return True, "Joined guild"

    async def leave(self, xuid):
        row = await self.db.fetchrow(
            "SELECT guild_id, role FROM rpg_guild_members WHERE xuid = $1", xuid
        )
        if not row:
            return False, "Not in a guild"

        if row["role"] == "owner":
            return False, "Transfer ownership before leaving"

        await self.db.execute(
            "DELETE FROM rpg_guild_members WHERE xuid = $1", xuid
        )
        return True, "Left guild"

    async def get_guild(self, guild_id):
        guild = await self.db.fetchrow("SELECT * FROM rpg_guilds WHERE id = $1", guild_id)
        if not guild:
            return None

        members = await self.db.fetch(
            "SELECT gm.*, p.name FROM rpg_guild_members gm "
            "LEFT JOIN players p ON p.xuid = gm.xuid "
            "WHERE gm.guild_id = $1 ORDER BY gm.joined_at",
            guild_id
        )

        return {"guild": dict(guild), "members": [dict(m) for m in members]}

    async def get_player_guild(self, xuid):
        row = await self.db.fetchrow(
            "SELECT guild_id FROM rpg_guild_members WHERE xuid = $1", xuid
        )
        if not row:
            return None
        return await self.get_guild(row["guild_id"])

    async def add_bank(self, guild_id, amount):
        guild = await self.db.fetchrow(
            "SELECT bank FROM rpg_guilds WHERE id = $1", guild_id
        )
        if not guild:
            return False, "Guild not found"

        await self.db.execute(
            "UPDATE rpg_guilds SET bank = bank + $1 WHERE id = $2", amount, guild_id
        )
        return True, f"Deposited {amount} coins to guild bank"

    async def get_top(self, limit=10):
        rows = await self.db.fetch(
            "SELECT g.*, COUNT(m.xuid) AS member_count "
            "FROM rpg_guilds g "
            "LEFT JOIN rpg_guild_members m ON m.guild_id = g.id "
            "GROUP BY g.id "
            "ORDER BY g.level DESC, g.bank DESC "
            "LIMIT $1", limit
        )
        return [dict(r) for r in rows]
