"""Minimal economy engine tests (ponytail: no framework)."""
import sys, pytest
sys.path.insert(0, "src")
from economy.engine import EconomyEngine
from rpg.engine import RpgEngine


class FakeCache:
    async def get(self, k): return None
    async def set(self, k, v, ttl=0): pass
    async def delete(self, k): pass
    async def close(self): pass


class FakeDB:
    def __init__(self):
        self._data = {}

    async def fetchrow(self, q, *a):
        return self._data.get(a[0])

    async def execute(self, q, *a):
        if "INSERT" in q:
            self._data[a[0]] = {"coins": a[5]}
        elif "UPDATE" in q:
            if a[-1] in self._data:
                self._data[a[-1]]["coins"] = a[0]
        return "OK"

    async def fetch(self, q, *a):
        return [{"name": "a", "coins": 100}, {"name": "b", "coins": 50}]


class FakePlugin:
    def __init__(self):
        self._db = FakeDB()
        self._cache = FakeCache()
        self.cfg = {
            "economy": {"start_balance": 100, "currency": "coins", "transfer_tax": 0.02},
            "rpg": {"max_level": 100, "xp_multiplier": 1.0, "classes": ["adventurer", "warrior", "mage"]},
        }


@pytest.mark.asyncio
async def test_economy_flow():
    p = FakePlugin()
    eco = EconomyEngine(p)

    p._db._data["test_xuid"] = {"coins": 100}

    bal = await eco.get_balance("test_xuid")
    assert bal == 100, f"Expected 100, got {bal}"

    await eco.add("test_xuid", 50)
    assert await eco.get_balance("test_xuid") == 150

    ok = await eco.remove("test_xuid", 30)
    assert ok
    assert await eco.get_balance("test_xuid") == 120

    ok = await eco.remove("test_xuid", 999)
    assert not ok

    await eco.set_balance("test_xuid", 500)
    assert await eco.get_balance("test_xuid") == 500


@pytest.mark.asyncio
async def test_transfer_with_tax():
    p = FakePlugin()
    eco = EconomyEngine(p)

    p._db._data["alice_xuid"] = {"coins": 1000}
    p._db._data["bob_xuid"] = {"coins": 0}

    ok = await eco.transfer("alice_xuid", "bob_xuid", 100)
    assert ok
    assert await eco.get_balance("alice_xuid") == 898  # 1000 - 100 - 2 tax
    assert await eco.get_balance("bob_xuid") == 100


@pytest.mark.asyncio
async def test_rpg_xp():
    p = FakePlugin()
    rpg = RpgEngine(p)

    p._db._data["test_xuid"] = {"class": "adventurer", "level": 1, "xp": 0, "gems": 0}
    result = await rpg.add_xp("test_xuid", 150)
    assert result["level"] >= 2
    assert result["gained_levels"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
