from __future__ import annotations
import json
from pathlib import Path
from typing import Any


DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "catalog" / "PACK_CATALOG.json"


class PackCatalog:
    def __init__(self, catalog_path: str | Path = DEFAULT_CATALOG_PATH):
        self.catalog_path = Path(catalog_path)
        self.data: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self.catalog_path.exists():
            self.data = {}
            return
        with self.catalog_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self.data = {str(item.get("dir")): item for item in raw.get("packs", []) if item.get("dir")}

    def get(self, pack_dir: str) -> dict[str, Any] | None:
        return self.data.get(pack_dir)

    def update(self, pack_dir: str, values: dict[str, Any]) -> dict[str, Any]:
        rec = self.data.setdefault(pack_dir, {})
        rec.update(values)
        return rec

    def commit(self) -> None:
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "packs": [
                self.data[k] for k in sorted(self.data, key=lambda x: (self.data[x].get("category", "ZZZ"), x))
            ]
        }
        with self.catalog_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
