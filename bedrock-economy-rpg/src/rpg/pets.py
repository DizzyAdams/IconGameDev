PETS = {
    "wolf": {"name": "Wolf", "speed": 1.2, "abilities": ["fetch", "guard"], "cost": {"coins": 500, "level": 5}},
    "dragonling": {"name": "Dragonling", "speed": 1.5, "abilities": ["scout", "burn"], "cost": {"coins": 2000, "gems": 50, "level": 20}},
    "fox": {"name": "Fox", "speed": 1.3, "abilities": ["hunt", "dig"], "cost": {"coins": 800, "level": 10}},
    "panda": {"name": "Panda", "speed": 0.8, "abilities": ["forage", "sit"], "cost": {"coins": 300, "level": 3}},
    "ghost": {"name": "Ghost", "speed": 1.6, "abilities": ["haunt", "phase"], "cost": {"coins": 1500, "gems": 25, "level": 15}},
    "fairy": {"name": "Fairy", "speed": 1.8, "abilities": ["heal", "light"], "cost": {"coins": 1000, "gems": 10, "level": 10}},
}

PET_XP_PER_LEVEL = 200


class PetSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_pets ("
            "xuid VARCHAR(32) NOT NULL, "
            "pet_id VARCHAR(64) NOT NULL, "
            "level INT DEFAULT 1, "
            "experience INT DEFAULT 0, "
            "active BOOLEAN DEFAULT FALSE, "
            "PRIMARY KEY (xuid, pet_id))"
        )

    async def adopt(self, xuid, pet_id):
        pet = PETS.get(pet_id)
        if not pet:
            return False, "Pet not found"

        await self._ensure_tables()

        existing = await self.db.fetchrow(
            "SELECT 1 FROM rpg_pets WHERE xuid = $1 AND pet_id = $2", xuid, pet_id
        )
        if existing:
            return False, "Pet already adopted"

        player = await self.plugin.rpg.get_player(xuid)
        if player["level"] < pet["cost"].get("level", 1):
            return False, f"Need level {pet['cost']['level']}"
        coins = pet["cost"].get("coins", 0)
        if coins and not await self.plugin.economy.remove(xuid, coins):
            return False, f"Need {coins} coins"
        gems = pet["cost"].get("gems", 0)
        if gems:
            if player["gems"] < gems:
                return False, f"Need {gems} gems"
            await self.db.execute(
                "UPDATE players SET gems = gems - $1 WHERE xuid = $2", gems, xuid
            )

        await self.db.execute(
            "INSERT INTO rpg_pets (xuid, pet_id, level, experience) VALUES ($1, $2, 1, 0)",
            xuid, pet_id
        )
        return True, f"Adopted {pet['name']}!"

    async def get_pets(self, xuid):
        await self._ensure_tables()
        rows = await self.db.fetch(
            "SELECT * FROM rpg_pets WHERE xuid = $1", xuid
        )
        result = []
        for r in rows:
            pet_def = PETS.get(r["pet_id"])
            if not pet_def:
                continue
            entry = dict(r)
            entry["name"] = pet_def["name"]
            entry["speed"] = pet_def["speed"]
            entry["abilities"] = self._get_unlocked_abilities(pet_def["abilities"], r["level"])
            entry["max_abilities"] = len(pet_def["abilities"])
            result.append(entry)
        return result

    async def level_up(self, xuid, pet_id):
        row = await self.db.fetchrow(
            "SELECT level, experience FROM rpg_pets WHERE xuid = $1 AND pet_id = $2",
            xuid, pet_id
        )
        if not row:
            return False, "Pet not found"

        pet_def = PETS.get(pet_id)
        if not pet_def:
            return False, "Pet data missing"

        xp_needed = PET_XP_PER_LEVEL * row["level"]
        if row["experience"] < xp_needed:
            return False, f"Need {xp_needed - row['experience']} more XP"

        new_level = row["level"] + 1
        new_xp = row["experience"] - xp_needed
        await self.db.execute(
            "UPDATE rpg_pets SET level = $1, experience = $2 WHERE xuid = $3 AND pet_id = $4",
            new_level, new_xp, xuid, pet_id
        )
        return True, f"{pet_def['name']} reached level {new_level}!"

    async def add_xp(self, xuid, pet_id, amount):
        row = await self.db.fetchrow(
            "SELECT experience FROM rpg_pets WHERE xuid = $1 AND pet_id = $2",
            xuid, pet_id
        )
        if not row:
            return False
        await self.db.execute(
            "UPDATE rpg_pets SET experience = experience + $1 WHERE xuid = $2 AND pet_id = $3",
            amount, xuid, pet_id
        )
        return True

    async def set_active(self, xuid, pet_id):
        await self._ensure_tables()

        has_pet = await self.db.fetchrow(
            "SELECT 1 FROM rpg_pets WHERE xuid = $1 AND pet_id = $2", xuid, pet_id
        )
        if not has_pet:
            return False, "Pet not found"

        await self.db.execute(
            "UPDATE rpg_pets SET active = FALSE WHERE xuid = $1", xuid
        )
        await self.db.execute(
            "UPDATE rpg_pets SET active = TRUE WHERE xuid = $1 AND pet_id = $2",
            xuid, pet_id
        )
        pet_def = PETS.get(pet_id)
        return True, f"{pet_def['name']} is now following you!"

    async def get_active(self, xuid):
        row = await self.db.fetchrow(
            "SELECT * FROM rpg_pets WHERE xuid = $1 AND active = TRUE", xuid
        )
        if not row:
            return None
        pet_def = PETS.get(row["pet_id"])
        if not pet_def:
            return None
        entry = dict(row)
        entry["name"] = pet_def["name"]
        entry["speed"] = pet_def["speed"]
        entry["abilities"] = self._get_unlocked_abilities(pet_def["abilities"], row["level"])
        return entry

    def _get_unlocked_abilities(self, abilities, level):
        unlocked = []
        for i, ab in enumerate(abilities):
            if level >= (i * 5 + 1):
                unlocked.append(ab)
        return unlocked
