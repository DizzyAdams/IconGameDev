import json
import random

BOSSES = {
    "dragon": {"name": "Ender Dragon", "health": 500, "phases": 3, "attacks": ["fireball", "charge", "roar"], "loot": {"coins": 1000, "xp": 5000, "gems": 50}},
    "lich": {"name": "Lich King", "health": 300, "phases": 2, "attacks": ["frost", "summon", "drain"], "loot": {"coins": 500, "xp": 3000, "gems": 25}},
    "kraken": {"name": "Kraken", "health": 400, "phases": 3, "attacks": ["tentacle", "whirlpool", "ink"], "loot": {"coins": 750, "xp": 4000, "gems": 35}},
    "titan": {"name": "Ancient Titan", "health": 600, "phases": 4, "attacks": ["stomp", "beam", "quake", "fury"], "loot": {"coins": 1500, "xp": 6000, "gems": 75}},
    "phoenix": {"name": "Phoenix", "health": 250, "phases": 2, "attacks": ["fire_blast", "rebirth"], "loot": {"coins": 600, "xp": 3500, "gems": 30}},
}


class BossSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_active_bosses ("
            "id BIGSERIAL PRIMARY KEY, "
            "boss_type VARCHAR(64) NOT NULL, "
            "x DOUBLE PRECISION NOT NULL, "
            "y DOUBLE PRECISION NOT NULL, "
            "z DOUBLE PRECISION NOT NULL, "
            "dimension VARCHAR(32) NOT NULL, "
            "health INT NOT NULL, "
            "max_health INT NOT NULL, "
            "phase INT DEFAULT 1, "
            "participants JSONB DEFAULT '[]'::jsonb)"
        )

    async def spawn_boss(self, boss_id, x, y, z, dimension):
        config = BOSSES.get(boss_id)
        if not config:
            return False, "Unknown boss type"

        await self._ensure_tables()
        row = await self.db.fetchrow(
            "INSERT INTO rpg_active_bosses (boss_type, x, y, z, dimension, health, max_health) "
            "VALUES ($1, $2, $3, $4, $5, $6, $6) RETURNING id",
            boss_id, x, y, z, dimension, config["health"]
        )
        return True, f"Spawned {config['name']}", row["id"]

    async def damage_boss(self, boss_id, player_xuid, damage):
        config = BOSSES.get(boss_id)
        if not config:
            return False, "Unknown boss type"

        row = await self.db.fetchrow(
            "SELECT * FROM rpg_active_bosses WHERE boss_type = $1", boss_id
        )
        if not row:
            return False, "Boss not active"

        new_health = max(0, row["health"] - damage)

        participants = json.loads(row["participants"]) if row["participants"] else []
        existing = next((p for p in participants if p["xuid"] == player_xuid), None)
        if existing:
            existing["damage"] += damage
        else:
            participants.append({"xuid": player_xuid, "damage": damage})

        phase = row["phase"]
        phase_threshold = config["health"] // config["phases"]
        max_health = row["max_health"]
        new_phase = config["phases"] - (new_health // phase_threshold)
        if new_health > 0 and new_health <= max_health - phase_threshold * row["phase"]:
            new_phase = row["phase"] + 1 if row["phase"] < config["phases"] else row["phase"]
        else:
            new_phase = row["phase"]

        if new_health <= 0:
            await self.db.execute(
                "DELETE FROM rpg_active_bosses WHERE id = $1", row["id"]
            )
            participants.sort(key=lambda p: p["damage"], reverse=True)
            await self.on_boss_kill(boss_id, participants)
            return True, f"{config['name']} defeated!", {"killed": True, "phase": row["phase"]}

        phase_changed = new_phase != row["phase"]
        await self.db.execute(
            "UPDATE rpg_active_bosses SET health = $1, phase = $2, participants = $3::jsonb WHERE id = $4",
            new_health, new_phase, json.dumps(participants), row["id"]
        )

        msg = f"{config['name']} took {damage} damage ({new_health}/{max_health} HP)"
        if phase_changed:
            msg += f" | Phase {new_phase}/{config['phases']}!"
        return True, msg, {"killed": False, "phase": new_phase, "health": new_health}

    async def on_boss_kill(self, boss_id, participants):
        config = BOSSES.get(boss_id)
        if not config:
            return

        total_damage = sum(p["damage"] for p in participants) or 1
        for p in participants:
            share = p["damage"] / total_damage
            coins = int(config["loot"]["coins"] * share)
            xp = int(config["loot"]["xp"] * share)
            gems = int(config["loot"]["gems"] * share)
            if coins:
                await self.plugin.economy.add(p["xuid"], coins)
            if xp:
                await self.plugin.rpg.add_xp(p["xuid"], xp)
            if gems:
                await self.plugin.rpg.add_gems(p["xuid"], gems)

    async def get_active_bosses(self):
        await self._ensure_tables()
        rows = await self.db.fetch("SELECT * FROM rpg_active_bosses")
        result = []
        for r in rows:
            entry = dict(r)
            config = BOSSES.get(r["boss_type"])
            entry["name"] = config["name"] if config else r["boss_type"]
            result.append(entry)
        return result

    def get_boss_config(self, boss_id):
        return BOSSES.get(boss_id)
