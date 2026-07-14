ENCHANTS = {
    "sharpness": {"name": "Sharpness", "max_level": 5, "applies_to": ["sword", "axe"], "cost_per_level": {"xp": 100, "gems": 5}},
    "protection": {"name": "Protection", "max_level": 4, "applies_to": ["helmet", "chestplate", "leggings", "boots"], "cost_per_level": {"xp": 100, "gems": 5}},
    "efficiency": {"name": "Efficiency", "max_level": 5, "applies_to": ["pickaxe", "axe", "shovel"], "cost_per_level": {"xp": 80, "gems": 3}},
    "fortune": {"name": "Fortune", "max_level": 3, "applies_to": ["pickaxe"], "cost_per_level": {"xp": 200, "gems": 10}},
    "unbreaking": {"name": "Unbreaking", "max_level": 3, "applies_to": ["sword", "pickaxe", "axe", "helmet", "chestplate", "leggings", "boots"], "cost_per_level": {"xp": 50, "gems": 2}},
    "power": {"name": "Power", "max_level": 5, "applies_to": ["bow"], "cost_per_level": {"xp": 100, "gems": 5}},
    "thorns": {"name": "Thorns", "max_level": 3, "applies_to": ["chestplate"], "cost_per_level": {"xp": 150, "gems": 8}},
}


class Enchanting:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_item_enchants ("
            "item_id VARCHAR(128) NOT NULL, "
            "enchant_id VARCHAR(64) NOT NULL, "
            "level INT DEFAULT 1, "
            "PRIMARY KEY (item_id, enchant_id))"
        )

    async def enchant(self, xuid, item_id, enchant_id, level=1):
        enchant = ENCHANTS.get(enchant_id)
        if not enchant:
            return False, "Enchant not found"

        if level < 1 or level > enchant["max_level"]:
            return False, f"Level must be 1-{enchant['max_level']}"

        await self._ensure_tables()

        item_row = await self.db.fetchrow(
            "SELECT quantity FROM rpg_inventory WHERE xuid = $1 AND item_id = $2",
            xuid, item_id
        )
        if not item_row or item_row["quantity"] < 1:
            return False, "Item not found in inventory"

        applies = any(item_id.startswith(t) or item_id == t for t in enchant["applies_to"])
        if not applies:
            applies = item_id in enchant["applies_to"]
        if not applies:
            return False, f"{enchant['name']} cannot be applied to {item_id}"

        existing = await self.db.fetchrow(
            "SELECT level FROM rpg_item_enchants WHERE item_id = $1 AND enchant_id = $2",
            item_id, enchant_id
        )
        if existing:
            return False, "Item already has this enchantment"

        total_xp = enchant["cost_per_level"]["xp"] * level
        total_gems = enchant["cost_per_level"]["gems"] * level

        player = await self.plugin.rpg.get_player(xuid)
        if player["xp"] < total_xp:
            return False, f"Need {total_xp} XP"
        if player["gems"] < total_gems:
            return False, f"Need {total_gems} gems"

        async with self.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE players SET xp = xp - $1, gems = gems - $2 WHERE xuid = $3",
                    total_xp, total_gems, xuid
                )
                await conn.execute(
                    "INSERT INTO rpg_item_enchants (item_id, enchant_id, level) VALUES ($1, $2, $3)",
                    item_id, enchant_id, level
                )

        return True, f"Applied {enchant['name']} {level} to {item_id}"

    async def get_item_enchants(self, item_id):
        await self._ensure_tables()
        rows = await self.db.fetch(
            "SELECT * FROM rpg_item_enchants WHERE item_id = $1", item_id
        )
        result = []
        for r in rows:
            enchant = ENCHANTS.get(r["enchant_id"])
            entry = dict(r)
            if enchant:
                entry["name"] = enchant["name"]
            result.append(entry)
        return result

    async def remove_enchant(self, item_id, enchant_id):
        await self.db.execute(
            "DELETE FROM rpg_item_enchants WHERE item_id = $1 AND enchant_id = $2",
            item_id, enchant_id
        )
