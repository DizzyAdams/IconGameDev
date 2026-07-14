import os
from pathlib import Path
from src.utils.uuid_manager import UUIDManager

class BaseGenerator:
    def __init__(self, registry_path=None):
        if registry_path:
            self.uuid_manager = UUIDManager(registry_path=str(registry_path))
        else:
            self.uuid_manager = UUIDManager()

    def get_uuids(self, pack_key: str) -> dict:
        """Get header and module UUIDs for a pack key."""
        return self.uuid_manager.pack_uuids(pack_key)

    def get_uuid(self, context: str) -> str:
        """Get or create a single UUID for a given context string."""
        return self.uuid_manager.get_or_create(context)
