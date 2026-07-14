import math

JOBS = {
    "miner": {
        "break_blocks": {"stone", "cobblestone", "deepslate", "iron_ore", "gold_ore", "diamond_ore",
                         "emerald_ore", "lapis_ore", "redstone_ore", "coal_ore", "copper_ore",
                         "netherite_ore", "ancient_debris"}
    },
    "woodcutter": {
        "break_blocks": {"oak_log", "spruce_log", "birch_log", "jungle_log", "acacia_log",
                         "dark_oak_log", "cherry_log", "mangrove_log", "oak_wood", "spruce_wood",
                         "birch_wood", "jungle_wood", "acacia_wood", "dark_oak_wood"}
    },
    "farmer": {
        "break_blocks": {"wheat", "carrots", "potatoes", "beetroots", "melon", "pumpkin",
                         "sugar_cane", "cactus", "nether_wart", "cocoa", "berry_bush"}
    },
    "hunter": {
        "kill_entities": {"zombie", "skeleton", "spider", "creeper", "enderman", "witch",
                          "blaze", "ghast", "hoglin", "piglin_brute", "warden", "evoker",
                          "vindicator", "ravager", "phantom"}
    },
    "fisher": {
        "special": "fishing"
    }
}

XP_PER_ACTION = 10
XP_PER_LEVEL = 100


class JobsSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def join_job(self, xuid, job_name):
        if job_name not in JOBS:
            return False, "Invalid job"
        existing = await self.db.fetchrow(
            "SELECT 1 FROM rpg_skills WHERE xuid = $1 AND skill_name = $2", xuid, f"job_{job_name}"
        )
        if existing:
            return False, "Already in this job"
        await self.db.execute(
            "INSERT INTO rpg_skills (xuid, skill_name, level, xp) VALUES ($1, $2, 1, 0) "
            "ON CONFLICT (xuid, skill_name) DO UPDATE SET level = rpg_skills.level",
            xuid, f"job_{job_name}"
        )
        return True, f"Joined {job_name}"

    async def leave_job(self, xuid):
        await self.db.execute(
            "DELETE FROM rpg_skills WHERE xuid = $1 AND skill_name LIKE 'job_%'", xuid
        )
        return True, "Left your job"

    async def get_job(self, xuid):
        row = await self.db.fetchrow(
            "SELECT skill_name, level, xp FROM rpg_skills WHERE xuid = $1 AND skill_name LIKE 'job_%' "
            "ORDER BY level DESC LIMIT 1",
            xuid
        )
        if not row:
            return None
        job_name = row["skill_name"].replace("job_", "", 1)
        return {"job": job_name, "level": row["level"], "xp": row["xp"]}

    async def add_xp(self, xuid, amount):
        job = await self.get_job(xuid)
        if not job:
            return None
        total_xp = job["xp"] + amount
        level = job["level"]
        next_level_xp = XP_PER_LEVEL * level
        leveled_up = False
        while total_xp >= next_level_xp:
            total_xp -= next_level_xp
            level += 1
            next_level_xp = XP_PER_LEVEL * level
            leveled_up = True
        await self.db.execute(
            "UPDATE rpg_skills SET level = $1, xp = $2 WHERE xuid = $3 AND skill_name = $4",
            level, total_xp, xuid, f"job_{job['job']}"
        )
        return {"job": job["job"], "level": level, "xp": total_xp, "leveled_up": leveled_up}

    async def get_level(self, xuid):
        job = await self.get_job(xuid)
        if not job:
            return 0
        return job["level"]
