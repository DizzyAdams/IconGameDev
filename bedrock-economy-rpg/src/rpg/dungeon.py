import json
import random

ROOM_TEMPLATES = ["combat", "treasure", "puzzle", "boss", "empty", "shop"]


class DungeonGenerator:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _ensure_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS rpg_dungeons ("
            "xuid VARCHAR(32) PRIMARY KEY, "
            "dungeon_data JSONB NOT NULL, "
            "current_room INT DEFAULT 0, "
            "active BOOLEAN DEFAULT TRUE)"
        )

    def generate(self, seed=None, difficulty=1, rooms=5):
        random.seed(seed)
        layout = {"rooms": [], "connections": [], "difficulty": difficulty}
        boss_placed = False
        for i in range(rooms):
            if not boss_placed and i == rooms - 1:
                room_type = "boss"
                boss_placed = True
            else:
                room_type = random.choice(ROOM_TEMPLATES)
            layout["rooms"].append({
                "id": i,
                "type": room_type,
                "mobs": self._spawn_mobs(room_type, difficulty) if room_type in ("combat", "boss") else [],
                "chests": self._gen_loot(room_type, difficulty),
                "cleared": False,
            })
        for i in range(rooms - 1):
            layout["connections"].append((i, i + 1))
        if rooms > 2:
            branch = random.randint(1, rooms - 2)
            layout["connections"].append((0, branch))
        return layout

    def _spawn_mobs(self, room_type, difficulty):
        mobs_by_type = {
            "combat": ["zombie", "skeleton", "spider"],
            "boss": ["zombie_pigman", "evoker", "vindicator"],
        }
        pool = mobs_by_type.get(room_type, ["zombie"])
        count = difficulty + 1 if room_type == "combat" else difficulty + 2
        return [random.choice(pool) for _ in range(count)]

    def _gen_loot(self, room_type, difficulty):
        if room_type == "treasure":
            return [
                {"item": "diamond", "count": random.randint(1, 3)},
                {"item": "gold_ingot", "count": random.randint(3, 8)},
            ]
        elif room_type == "boss":
            return [
                {"item": "netherite_ingot", "count": 1},
                {"item": "enchanted_golden_apple", "count": random.randint(1, 2)},
            ]
        elif room_type == "shop":
            return []
        return [{"item": "iron_ingot", "count": random.randint(1, 5)}]

    async def start_dungeon(self, xuid, difficulty=1):
        seed = random.randint(0, 2 ** 31)
        layout = self.generate(seed=seed, difficulty=difficulty, rooms=5)
        await self._ensure_tables()
        await self.db.execute(
            "INSERT INTO rpg_dungeons (xuid, dungeon_data, current_room, active) "
            "VALUES ($1, $2::jsonb, 0, TRUE) "
            "ON CONFLICT (xuid) DO UPDATE SET dungeon_data = $2::jsonb, current_room = 0, active = TRUE",
            xuid, json.dumps(layout)
        )
        return layout

    async def complete_room(self, xuid, room_id):
        row = await self.db.fetchrow(
            "SELECT dungeon_data, current_room FROM rpg_dungeons WHERE xuid = $1 AND active = TRUE",
            xuid
        )
        if not row:
            return False, "No active dungeon"

        layout = json.loads(row["dungeon_data"])
        if room_id != row["current_room"]:
            return False, f"Must clear room {row['current_room']} first"
        if room_id >= len(layout["rooms"]):
            return False, "Room does not exist"

        room = layout["rooms"][room_id]
        room["cleared"] = True
        layout["rooms"][room_id] = room

        next_room = row["current_room"] + 1
        if next_room >= len(layout["rooms"]):
            await self.db.execute(
                "UPDATE rpg_dungeons SET active = FALSE, dungeon_data = $1::jsonb "
                "WHERE xuid = $2",
                json.dumps(layout), xuid
            )
            return True, "Dungeon cleared!", {"completed": True, "loot": room["chests"]}

        await self.db.execute(
            "UPDATE rpg_dungeons SET current_room = $1, dungeon_data = $2::jsonb "
            "WHERE xuid = $3",
            next_room, json.dumps(layout), xuid
        )
        return True, f"Room {room_id} cleared! Proceed to room {next_room}.", {
            "completed": False, "loot": room["chests"], "next_room": next_room
        }

    async def get_dungeon(self, xuid):
        row = await self.db.fetchrow(
            "SELECT * FROM rpg_dungeons WHERE xuid = $1 AND active = TRUE", xuid
        )
        if not row:
            return None
        return dict(row)
