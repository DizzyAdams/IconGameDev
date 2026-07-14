from datetime import datetime, timezone, timedelta

QUESTS = {
    "daily_miner": {"name": "Miner's Daily", "type": "daily", "goal": {"type": "break", "target": "stone", "count": 100}, "rewards": {"coins": 50, "xp": 100}},
    "daily_hunter": {"name": "Hunter's Daily", "type": "daily", "goal": {"type": "kill", "target": "zombie", "count": 10}, "rewards": {"coins": 75, "xp": 150}},
    "weekly_dungeon": {"name": "Dungeon Delver", "type": "weekly", "goal": {"type": "dungeon", "count": 3}, "rewards": {"coins": 500, "xp": 1000, "gems": 10}},
    "story_intro": {"name": "First Steps", "type": "story", "goal": {"type": "reach_level", "target": 5}, "rewards": {"coins": 100, "xp": 200, "gems": 5}},
    "story_merchant": {"name": "Merchant Route", "type": "story", "goal": {"type": "trade", "count": 10}, "rewards": {"coins": 200, "xp": 300}},
    "daily_fisher": {"name": "Fisher's Daily", "type": "daily", "goal": {"type": "fish", "count": 30}, "rewards": {"coins": 60, "xp": 120}},
    "weekly_boss": {"name": "Bounty Hunter", "type": "weekly", "goal": {"type": "kill_boss", "count": 2}, "rewards": {"coins": 800, "xp": 2000, "gems": 15}},
    "story_enchanter": {"name": "Apprentice Enchanter", "type": "story", "goal": {"type": "enchant", "count": 5}, "rewards": {"coins": 300, "xp": 500, "gems": 10}},
}


class QuestEngine:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db
        self.economy = plugin.economy
        self.rpg = plugin.rpg

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_quests ("
            "xuid VARCHAR(32) NOT NULL, "
            "quest_id VARCHAR(64) NOT NULL, "
            "progress INT DEFAULT 0, "
            "accepted_at TIMESTAMPTZ DEFAULT NOW(), "
            "PRIMARY KEY (xuid, quest_id))"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_completed_quests ("
            "xuid VARCHAR(32) NOT NULL, "
            "quest_id VARCHAR(64) NOT NULL, "
            "completed_at TIMESTAMPTZ DEFAULT NOW(), "
            "PRIMARY KEY (xuid, quest_id))"
        )

    async def accept_quest(self, xuid, quest_id):
        quest = QUESTS.get(quest_id)
        if not quest:
            return False, "Quest not found"

        await self._ensure_tables()

        completed = await self.db.fetchrow(
            "SELECT completed_at FROM rpg_completed_quests WHERE xuid = $1 AND quest_id = $2",
            xuid, quest_id
        )
        if completed:
            if quest["type"] == "story":
                return False, "Story quest already completed"
            elapsed = (datetime.now(timezone.utc) - completed["completed_at"]).total_seconds()
            if quest["type"] == "daily" and elapsed < 86400:
                return False, "Daily quest already completed today"
            if quest["type"] == "weekly" and elapsed < 604800:
                return False, "Weekly quest already completed this week"

        existing = await self.db.fetchrow(
            "SELECT 1 FROM rpg_quests WHERE xuid = $1 AND quest_id = $2", xuid, quest_id
        )
        if existing:
            return False, "Quest already active"

        await self.db.execute(
            "INSERT INTO rpg_quests (xuid, quest_id, progress) VALUES ($1, $2, 0)",
            xuid, quest_id
        )
        return True, f"Accepted quest: {quest['name']}"

    async def progress(self, xuid, quest_id, amount=1):
        quest = QUESTS.get(quest_id)
        if not quest:
            return False, "Quest not found"

        row = await self.db.fetchrow(
            "SELECT progress FROM rpg_quests WHERE xuid = $1 AND quest_id = $2",
            xuid, quest_id
        )
        if not row:
            return False, "Quest not active"

        new_progress = row["progress"] + amount
        if new_progress >= quest["goal"]["count"]:
            new_progress = quest["goal"]["count"]
            await self.db.execute(
                "UPDATE rpg_quests SET progress = $1 WHERE xuid = $2 AND quest_id = $3",
                new_progress, xuid, quest_id
            )
            return True, "Quest completed! Use /quest claim to collect rewards."
        else:
            await self.db.execute(
                "UPDATE rpg_quests SET progress = $1 WHERE xuid = $2 AND quest_id = $3",
                new_progress, xuid, quest_id
            )
            return True, f"Progress: {new_progress}/{quest['goal']['count']}"

    async def claim_reward(self, xuid, quest_id):
        quest = QUESTS.get(quest_id)
        if not quest:
            return False, "Quest not found"

        row = await self.db.fetchrow(
            "SELECT progress FROM rpg_quests WHERE xuid = $1 AND quest_id = $2",
            xuid, quest_id
        )
        if not row:
            return False, "Quest not active"
        if row["progress"] < quest["goal"]["count"]:
            return False, "Quest not yet completed"

        async with self.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM rpg_quests WHERE xuid = $1 AND quest_id = $2",
                    xuid, quest_id
                )
                await conn.execute(
                    "INSERT INTO rpg_completed_quests (xuid, quest_id, completed_at) VALUES ($1, $2, $3)",
                    xuid, quest_id, datetime.now(timezone.utc)
                )

        rewards = quest["rewards"]
        if rewards.get("coins"):
            await self.economy.add(xuid, rewards["coins"])
        if rewards.get("xp"):
            await self.rpg.add_xp(xuid, rewards["xp"])
        if rewards.get("gems"):
            await self.rpg.add_gems(xuid, rewards["gems"])

        return True, f"Claimed rewards for {quest['name']}"

    async def get_active(self, xuid):
        await self._ensure_tables()
        rows = await self.db.fetch(
            "SELECT * FROM rpg_quests WHERE xuid = $1", xuid
        )
        result = []
        for r in rows:
            q = QUESTS.get(r["quest_id"])
            if q:
                result.append({
                    "quest_id": r["quest_id"],
                    "name": q["name"],
                    "type": q["type"],
                    "progress": r["progress"],
                    "goal": q["goal"]["count"],
                    "rewards": q["rewards"]
                })
        return result

    async def reset_dailies(self):
        await self._ensure_tables()
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        daily_ids = [qid for qid, q in QUESTS.items() if q["type"] in ("daily", "weekly")]
        for qid in daily_ids:
            await self.db.execute(
                "DELETE FROM rpg_completed_quests WHERE quest_id = $1 AND completed_at < $2",
                qid, cutoff
            )
