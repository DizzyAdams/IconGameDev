"""Generate multiple fast-monetization Behavior Packs (Add-ons)."""
import os
import json
import random

BASE = os.path.join(os.path.dirname(__file__), '..')
BP_DIR = os.path.join(BASE, 'behavior-packs')

def make_uuid(seed):
    h = hash(str(seed)) & 0xFFFFFFFFFFFFFFFF
    return f"f{h>>48:04x}{h>>32&0xFFFF:04x}-{h>>16&0xFFFF:04x}-{h&0xFFFF:04x}-{hash(str(seed)+'x')&0xFFFF:04x}-{hash(str(seed)+'y')&0xFFFFFFFFFF:012x}"

ADDONS = [
    {
        "id": "op_swords",
        "name": "OP Swords Add-On",
        "desc": "Adds 5 overpowered swords with custom effects to make you unstoppable!",
        "items": ["fire_sword", "ice_sword", "lightning_sword", "earth_sword", "void_sword"]
    },
    {
        "id": "lucky_blocks",
        "name": "Lucky Blocks Add-On",
        "desc": "Break a lucky block for random amazing loot or terrible disasters!",
        "items": ["lucky_block_gold", "lucky_block_diamond", "lucky_block_emerald"]
    },
    {
        "id": "pet_dragons",
        "name": "Pet Dragons Add-On",
        "desc": "Tame and ride 4 different elemental baby dragons!",
        "entities": ["fire_dragon", "water_dragon", "wind_dragon", "earth_dragon"]
    },
    {
        "id": "more_tnt",
        "name": "More TNT Add-On",
        "desc": "Explode your world with 10 new types of TNT!",
        "items": ["tnt_x5", "tnt_x10", "tnt_x50", "nuke", "blackhole_tnt"]
    },
    {
        "id": "mutant_mobs",
        "name": "Mutant Mobs Add-On",
        "desc": "Fight giant mutant versions of classic mobs!",
        "entities": ["mutant_zombie", "mutant_skeleton", "mutant_creeper", "mutant_enderman"]
    }
]

def make_manifest(addon):
    uid = make_uuid(addon["id"])
    muid = make_uuid(addon["id"] + "_mod")
    return {
        "format_version": 2,
        "header": {
            "name": addon["name"],
            "description": addon["desc"],
            "uuid": uid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "data",
                "uuid": muid,
                "version": [1, 0, 0]
            }
        ],
        "metadata": {
            "authors": ["Bedrock Mass Automation"],
            "product_type": "behavior_pack",
            "price": "$2.99"
        }
    }

def generate_item_json(item_name, namespace="addon"):
    return {
        "format_version": "1.20.0",
        "minecraft:item": {
            "description": {
                "identifier": f"{namespace}:{item_name}",
                "category": "equipment"
            },
            "components": {
                "minecraft:icon": {"texture": item_name},
                "minecraft:display_name": {"value": item_name.replace("_", " ").title()},
                "minecraft:damage": 10,
                "minecraft:max_stack_size": 1
            }
        }
    }

def generate_entity_json(entity_name, namespace="addon"):
    return {
        "format_version": "1.20.0",
        "minecraft:entity": {
            "description": {
                "identifier": f"{namespace}:{entity_name}",
                "is_spawnable": True,
                "is_summonable": True
            },
            "components": {
                "minecraft:health": {"value": 100, "max": 100},
                "minecraft:movement": {"value": 0.3},
                "minecraft:attack": {"damage": 15},
                "minecraft:physics": {}
            }
        }
    }

def main():
    os.makedirs(BP_DIR, exist_ok=True)
    for addon in ADDONS:
        addon_dir = os.path.join(BP_DIR, addon["id"])
        os.makedirs(addon_dir, exist_ok=True)
        
        # Manifest
        with open(os.path.join(addon_dir, "manifest.json"), "w") as f:
            json.dump(make_manifest(addon), f, indent=4)
        
        # Items
        if "items" in addon:
            items_dir = os.path.join(addon_dir, "items")
            os.makedirs(items_dir, exist_ok=True)
            for item in addon["items"]:
                with open(os.path.join(items_dir, f"{item}.json"), "w") as f:
                    json.dump(generate_item_json(item, addon["id"]), f, indent=4)
                    
        # Entities
        if "entities" in addon:
            entities_dir = os.path.join(addon_dir, "entities")
            os.makedirs(entities_dir, exist_ok=True)
            for entity in addon["entities"]:
                with open(os.path.join(entities_dir, f"{entity}.json"), "w") as f:
                    json.dump(generate_entity_json(entity, addon["id"]), f, indent=4)
                    
        print(f"Generated Behavior Pack: {addon['name']} ({addon['id']})")
        
if __name__ == "__main__":
    print("=== Generating Add-Ons (Behavior Packs) ===")
    main()
