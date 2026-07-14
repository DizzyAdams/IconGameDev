RECIPES = {
    "iron_sword": {"materials": {"iron_ingot": 2, "stick": 1}, "result": "iron_sword", "station": "crafting_table"},
    "diamond_pickaxe": {"materials": {"diamond": 3, "stick": 2}, "result": "diamond_pickaxe", "station": "crafting_table"},
    "golden_apple": {"materials": {"apple": 1, "gold_ingot": 8}, "result": "golden_apple", "station": "crafting_table"},
    "xp_bottle": {"materials": {"glass_bottle": 1, "xp": 50}, "result": "xp_bottle", "station": "enchanting_table"},
    "speed_potion": {"materials": {"nether_wart": 1, "sugar": 1, "glass_bottle": 1}, "result": "speed_potion", "station": "brewing_stand"},
    "shield": {"materials": {"iron_ingot": 1, "planks": 6}, "result": "shield", "station": "crafting_table"},
    "bow": {"materials": {"stick": 3, "string": 3}, "result": "bow", "station": "crafting_table"},
    "fishing_rod": {"materials": {"stick": 3, "string": 2}, "result": "fishing_rod", "station": "crafting_table"},
}


class Crafting:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db
        self.economy = plugin.economy

    async def craft(self, xuid, recipe_id, amount=1):
        recipe = RECIPES.get(recipe_id)
        if not recipe:
            return False, "Recipe not found"

        for material, count in recipe["materials"].items():
            total_count = count * amount
            if material == "xp":
                player = await self.plugin.rpg.get_player(xuid)
                if player["xp"] < total_count:
                    return False, f"Need {total_count} XP (have {player['xp']})"
            else:
                row = await self.db.fetchrow(
                    "SELECT COUNT(*) AS cnt FROM players WHERE xuid = $1", xuid
                )
                has_material = await self.db.fetchrow(
                    "SELECT 1 FROM rpg_inventory WHERE xuid = $1 AND item_id = $2 AND quantity >= $3",
                    xuid, material, total_count
                )
                if not has_material:
                    return False, f"Need {total_count}x {material}"

        async with self.db.acquire() as conn:
            async with conn.transaction():
                for material, count in recipe["materials"].items():
                    total_count = count * amount
                    if material == "xp":
                        total_xp = total_count
                        player = await self.plugin.rpg.get_player(xuid)
                        new_xp = player["xp"] - total_xp
                        await conn.execute(
                            "UPDATE players SET xp = $1 WHERE xuid = $2",
                            max(0, new_xp), xuid
                        )
                    else:
                        await conn.execute(
                            "UPDATE rpg_inventory SET quantity = quantity - $1 "
                            "WHERE xuid = $2 AND item_id = $3",
                            total_count, xuid, material
                        )
                        await conn.execute(
                            "DELETE FROM rpg_inventory WHERE xuid = $1 AND item_id = $2 AND quantity <= 0",
                            xuid, material
                        )

                result_item = recipe["result"]
                existing = await conn.fetchrow(
                    "SELECT 1 FROM rpg_inventory WHERE xuid = $1 AND item_id = $2",
                    xuid, result_item
                )
                if existing:
                    await conn.execute(
                        "UPDATE rpg_inventory SET quantity = quantity + $1 WHERE xuid = $2 AND item_id = $3",
                        amount, xuid, result_item
                    )
                else:
                    await conn.execute(
                        "INSERT INTO rpg_inventory (xuid, item_id, quantity) VALUES ($1, $2, $3)",
                        xuid, result_item, amount
                    )

        return True, f"Crafted {amount}x {recipe['result']}"

    def get_recipes(self, station=None):
        if not station:
            return list(RECIPES.values())
        return [r for r in RECIPES.values() if r["station"] == station]
