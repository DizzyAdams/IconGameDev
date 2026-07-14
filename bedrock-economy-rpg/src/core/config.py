import json
from pathlib import Path


class ConfigManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self._cfg = {}

    def load(self) -> dict:
        path = Path("config/bedrock-economy-rpg.json")
        if path.exists():
            self._cfg = json.loads(path.read_text())
        self._cfg.setdefault("database", {
            "dsn": "postgresql://user:pass@localhost:5432/minecraft"
        })
        self._cfg.setdefault("cache", {
            "host": "localhost",
            "port": 6379,
            "db": 0,
        })
        self._cfg.setdefault("economy", {
            "start_balance": 100,
            "currency": "coins",
            "transfer_tax": 0.02,
        })
        self._cfg.setdefault("rpg", {
            "max_level": 100,
            "xp_multiplier": 1.0,
            "classes": ["adventurer", "warrior", "mage", "archer", "rogue"],
        })
        return self._cfg
