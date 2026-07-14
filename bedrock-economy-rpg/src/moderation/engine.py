import time
from datetime import datetime, timedelta


class ModerationEngine:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db
        self._muted = {}

    async def warn(self, moderator, target_xuid, reason):
        await self._log_action(target_xuid, moderator, "warn", reason)
        return True

    async def mute(self, moderator, target_xuid, reason, duration_minutes=30):
        await self._log_action(target_xuid, moderator, "mute", reason, duration_minutes * 60)
        self._muted[target_xuid] = time.time() + duration_minutes * 60
        return True

    async def unmute(self, moderator, target_xuid):
        self._muted.pop(target_xuid, None)
        await self._log_action(target_xuid, moderator, "unmute", "Lifted by moderator")
        return True

    async def kick(self, moderator, target_xuid, reason):
        await self._log_action(target_xuid, moderator, "kick", reason)
        return True

    async def ban(self, moderator, target_xuid, reason, duration_hours=None):
        expires = None
        if duration_hours:
            expires = datetime.now() + timedelta(hours=duration_hours)
        await self._log_action(
            target_xuid, moderator, "ban" if not duration_hours else "tempban", reason,
            duration_hours * 3600 if duration_hours else None,
        )
        await self.db.execute(
            "UPDATE players SET is_banned = TRUE, ban_reason = $1, banned_until = $2 WHERE xuid = $3",
            reason, expires, target_xuid,
        )
        return True

    async def pardon(self, moderator, target_xuid):
        await self.db.execute(
            "UPDATE players SET is_banned = FALSE, ban_reason = NULL, banned_until = NULL WHERE xuid = $1",
            target_xuid,
        )
        await self._log_action(target_xuid, moderator, "pardon", "Ban lifted")
        return True

    async def is_muted(self, xuid):
        expiry = self._muted.get(xuid)
        if expiry and time.time() > expiry:
            self._muted.pop(xuid, None)
            return False
        return expiry is not None

    async def is_banned(self, xuid):
        row = await self.db.fetchrow(
            "SELECT is_banned, banned_until FROM players WHERE xuid = $1", xuid
        )
        if row and row["is_banned"]:
            if row["banned_until"] and datetime.now() > row["banned_until"]:
                await self.pardon("System", xuid)
                return False
            return True
        return False

    async def get_history(self, target_xuid, limit=20):
        return await self.db.fetch(
            "SELECT * FROM moderation_log WHERE target_xuid = $1 ORDER BY created_at DESC LIMIT $2",
            target_xuid, limit,
        )

    async def _log_action(self, target, moderator_xuid, action, reason, duration_seconds=None):
        await self.db.execute(
            "INSERT INTO moderation_log (target_xuid, moderator_xuid, action, reason, duration_seconds) VALUES ($1, $2, $3, $4, $5)",
            target, moderator_xuid, action, reason, duration_seconds,
        )
