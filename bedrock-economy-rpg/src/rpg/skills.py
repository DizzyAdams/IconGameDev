SKILL_TREES = {
    "warrior": {
        "name": "Warrior Path",
        "skills": [
            {"id": "warrior_strength", "name": "Strength", "max_level": 5, "per_level": {"damage_mult": 0.1}},
            {"id": "warrior_defense", "name": "Defense", "max_level": 5, "per_level": {"defense_mult": 0.1}},
            {"id": "warrior_rage", "name": "Rage", "max_level": 3, "per_level": {"crit_chance": 0.05}},
            {"id": "warrior_charge", "name": "Charge", "max_level": 3, "per_level": {"speed_mult": 0.1}},
            {"id": "warrior_mastery", "name": "Weapon Mastery", "max_level": 5, "per_level": {"attack_speed": 0.1}},
        ]
    },
    "mage": {
        "name": "Mage Path",
        "skills": [
            {"id": "mage_power", "name": "Spell Power", "max_level": 5, "per_level": {"spell_damage": 0.15}},
            {"id": "mage_mana", "name": "Mana Pool", "max_level": 5, "per_level": {"mana_bonus": 10}},
            {"id": "mage_frost", "name": "Frost Magic", "max_level": 3, "per_level": {"frost_damage": 0.12}},
            {"id": "mage_fire", "name": "Fire Magic", "max_level": 3, "per_level": {"fire_damage": 0.12}},
            {"id": "mage_arcane", "name": "Arcane Mastery", "max_level": 5, "per_level": {"cooldown_reduction": 0.08}},
        ]
    },
    "archer": {
        "name": "Archer Path",
        "skills": [
            {"id": "archer_aim", "name": "Precision", "max_level": 5, "per_level": {"aim_mult": 0.12}},
            {"id": "archer_speed", "name": "Quick Shot", "max_level": 5, "per_level": {"shot_speed": 0.1}},
            {"id": "archer_trap", "name": "Traps", "max_level": 3, "per_level": {"trap_damage": 0.15}},
            {"id": "archer_camouflage", "name": "Camouflage", "max_level": 3, "per_level": {"sneak_bonus": 0.1}},
            {"id": "archer_mastery", "name": "Bow Mastery", "max_level": 5, "per_level": {"bow_damage": 0.1}},
        ]
    },
    "rogue": {
        "name": "Rogue Path",
        "skills": [
            {"id": "rogue_stealth", "name": "Stealth", "max_level": 5, "per_level": {"stealth_duration": 2}},
            {"id": "rogue_backstab", "name": "Backstab", "max_level": 5, "per_level": {"backstab_mult": 0.2}},
            {"id": "rogue_poison", "name": "Poisons", "max_level": 3, "per_level": {"poison_damage": 0.1}},
            {"id": "rogue_speed", "name": "Agility", "max_level": 3, "per_level": {"speed_bonus": 0.08}},
            {"id": "rogue_mastery", "name": "Dagger Mastery", "max_level": 5, "per_level": {"dagger_damage": 0.12}},
        ]
    },
    "adventurer": {
        "name": "Adventurer Path",
        "skills": [
            {"id": "adv_luck", "name": "Luck", "max_level": 5, "per_level": {"luck_bonus": 0.1}},
            {"id": "adv_survival", "name": "Survival", "max_level": 5, "per_level": {"heal_bonus": 0.1}},
            {"id": "adv_trading", "name": "Trading", "max_level": 3, "per_level": {"trade_discount": 0.05}},
            {"id": "adv_exploration", "name": "Exploration", "max_level": 3, "per_level": {"explore_bonus": 0.1}},
            {"id": "adv_mastery", "name": "Adventurer Mastery", "max_level": 5, "per_level": {"xp_bonus": 0.1}},
        ]
    }
}


class SkillTree:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_skills ("
            "xuid VARCHAR(32) NOT NULL, "
            "skill_id VARCHAR(64) NOT NULL, "
            "level INT DEFAULT 1, "
            "PRIMARY KEY (xuid, skill_id))"
        )

    async def learn_skill(self, xuid, skill_id):
        tree = self._find_skill(skill_id)
        if not tree:
            return False, "Skill not found"

        player = await self.plugin.rpg.get_player(xuid)
        if player["class"] not in SKILL_TREES:
            return False, "No class selected"
        if tree["class_tree"] != player["class"]:
            return False, f"Skill belongs to {tree['class_tree']}, not {player['class']}"

        await self._ensure_tables()
        skill_def = tree["skill"]
        row = await self.db.fetchrow(
            "SELECT level FROM rpg_skills WHERE xuid = $1 AND skill_id = $2", xuid, skill_id
        )
        current_level = row["level"] if row else 0
        if current_level >= skill_def["max_level"]:
            return False, "Skill already at max level"

        cost_coins = current_level * 100 + 100
        cost_xp = current_level * 50 + 50
        eco = self.plugin.economy
        if not await eco.remove(xuid, cost_coins):
            return False, f"Need {cost_coins} coins"
        rpg = self.plugin.rpg
        player_data = await rpg.get_player(xuid)
        if player_data["xp"] < cost_xp:
            return False, f"Need {cost_xp} XP"

        await rpg.add_xp(xuid, -cost_xp)

        if row:
            await self.db.execute(
                "UPDATE rpg_skills SET level = level + 1 WHERE xuid = $1 AND skill_id = $2",
                xuid, skill_id
            )
        else:
            await self.db.execute(
                "INSERT INTO rpg_skills (xuid, skill_id, level) VALUES ($1, $2, 1)",
                xuid, skill_id
            )
        return True, f"Learned {skill_def['name']} level {current_level + 1}"

    async def get_skills(self, xuid):
        await self._ensure_tables()
        rows = await self.db.fetch(
            "SELECT * FROM rpg_skills WHERE xuid = $1", xuid
        )
        player_skills = {r["skill_id"]: r["level"] for r in rows}
        result = []
        for class_key, tree in SKILL_TREES.items():
            for sk in tree["skills"]:
                lvl = player_skills.get(sk["id"], 0)
                entry = {"id": sk["id"], "name": sk["name"], "level": lvl, "max_level": sk["max_level"]}
                if lvl > 0 and sk.get("per_level"):
                    entry["effects"] = {k: round(v * lvl, 2) for k, v in sk["per_level"].items()}
                result.append(entry)
        return result

    async def get_class_skills(self, player_class):
        tree = SKILL_TREES.get(player_class)
        if not tree:
            return None
        return {"name": tree["name"], "class": player_class, "skills": tree["skills"]}

    def _find_skill(self, skill_id):
        for class_key, tree in SKILL_TREES.items():
            for sk in tree["skills"]:
                if sk["id"] == skill_id:
                    return {"class_tree": class_key, "skill": sk}
        return None
