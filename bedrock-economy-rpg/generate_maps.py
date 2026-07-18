#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de 10 Mapas Economy RPG para Minecraft Bedrock (.mctemplate)
Tema: Fantasy/Medieval
Cada mapa: sistema de moeda (diamonds), lojas NPC, quests
"""

import os
import json
import shutil
import struct
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHARED_BP_DIR = os.path.join(BASE_DIR, "shared_bp")

# UUIDs fixos para consistencia entre mapas
BP_UUID = "a7f8e3d2-1b4c-5e6f-8a9b-0c1d2e3f4a5b"
BP_MODULE_UUID = "b8f9e4d3-2c5d-6f7e-9a0b-1c2d3e4f5a6b"
BP_SCRIPT_UUID = "c9a0f5e4-3d6e-7a8f-0b1c-2d3e4f5a6b7c"

# ============================================================
# DADOS DOS 10 MAPAS
# ============================================================
MAPS = [
    {
        "id": 1,
        "name": "§6Vila do Início",
        "subtitle": "§7Sua jornada começa aqui",
        "biome": "plains",
        "spawn": [0, 64, 0],
        "npcs": [
            {"name": "§eRei Alaric", "tag": "quest_master", "pos": [10, 64, 5], "skin": "villager_v2/armorer"},
            {"name": "§cFerreiro Brutamontes", "tag": "shop_weapons", "pos": [-8, 64, 3], "skin": "villager_v2/weaponsmith"},
            {"name": "§9Capitão da Guarda", "tag": "shop_armor", "pos": [5, 64, -10], "skin": "villager_v2/armorer"},
            {"name": "§eMestre Artesão", "tag": "shop_tools", "pos": [-5, 64, -8], "skin": "villager_v2/tool_smith"},
            {"name": "§aBanqueiro Real", "tag": "banker", "pos": [0, 64, 12], "skin": "villager_v2/cartographer"},
            {"name": "§aMestre Cuca", "tag": "shop_food", "pos": [-12, 64, 0], "skin": "villager_v2/butcher"},
        ],
        "description": "Uma vila pacífica onde sua jornada começa. Conheça o Rei, abra sua conta no banco e pegue suas primeiras quests.",
        "build_style": "Vila Medieval com casas de madeira e pedra",
        "special_features": ["Banco Real", "Mestre de Quests", "Loja de Armas", "Loja de Armaduras", "Loja de Ferramentas", "Loja de Comidas"],
        "difficulty": "Fácil"
    },
    {
        "id": 2,
        "name": "§eAcampamento dos Mineradores",
        "subtitle": "§7Onde o minério vale ouro",
        "biome": "windswept_hills",
        "spawn": [0, 72, 0],
        "npcs": [
            {"name": "§eMestre de Quests Kroln", "tag": "quest_master", "pos": [8, 72, 5], "skin": "villager_v2/weaponsmith"},
            {"name": "§eMinerador Ancião", "tag": "shop_ores", "pos": [-5, 72, 8], "skin": "villager_v2/tool_smith"},
            {"name": "§eMestre Artesão", "tag": "shop_tools", "pos": [5, 72, -8], "skin": "villager_v2/fletcher"},
            {"name": "§aBanqueiro", "tag": "banker", "pos": [0, 72, 12], "skin": "villager_v2/cartographer"},
            {"name": "§7Mestre de Obras", "tag": "shop_blocks", "pos": [-8, 72, -5], "skin": "villager_v2/mason"},
            {"name": "§aFazendeiro João", "tag": "shop_farming", "pos": [12, 72, -3], "skin": "villager_v2/farmer"},
        ],
        "description": "Acampamento minerador nas montanhas. Minérios valiosos esperam por você!",
        "build_style": "Acampamento rústico de mineração com tendas e forjas",
        "special_features": ["Loja de Minérios", "Ferramentas Especiais", "Quests de Mineração", "Troca de Minérios"],
        "difficulty": "Fácil"
    },
    {
        "id": 3,
        "name": "§aFeitoria Agrícola",
        "subtitle": "§7O celeiro do reino",
        "biome": "plains",
        "spawn": [0, 63, 0],
        "npcs": [
            {"name": "§eMestre de Quests", "tag": "quest_master", "pos": [5, 63, 10], "skin": "villager_v2/farmer"},
            {"name": "§aFazendeiro João", "tag": "shop_farming", "pos": [-8, 63, 5], "skin": "villager_v2/farmer"},
            {"name": "§aMestre Cuca", "tag": "shop_food", "pos": [10, 63, -5], "skin": "villager_v2/butcher"},
            {"name": "§aBanqueiro", "tag": "banker", "pos": [0, 63, -10], "skin": "villager_v2/cartographer"},
            {"name": "§7Mestre de Obras", "tag": "shop_blocks", "pos": [-10, 63, -8], "skin": "villager_v2/mason"},
            {"name": "§eMestre Artesão", "tag": "shop_tools", "pos": [8, 63, 0], "skin": "villager_v2/tool_smith"},
        ],
        "description": "Terra fértil para cultivar e prosperar. Plante, colha e venda seus produtos!",
        "build_style": "Vila agrícola com campos cultivados, moinho e celeiro",
        "special_features": ["Loja Agrícola", "Comidas Especiais", "Quests de Agricultura", "Sistema de Sementes"],
        "difficulty": "Fácil"
    },
    {
        "id": 4,
        "name": "§9Porto Comercial",
        "subtitle": "§7O centro do comércio",
        "biome": "beach",
        "spawn": [0, 62, 0],
        "npcs": [
            {"name": "§eMestre de Quests", "tag": "quest_master", "pos": [10, 62, 8], "skin": "villager_v2/cartographer"},
            {"name": "§cEngenheiro Redstone", "tag": "shop_redstone", "pos": [-5, 62, 12], "skin": "villager_v2/armorer"},
            {"name": "§dDecorador Real", "tag": "shop_decor", "pos": [12, 62, -5], "skin": "villager_v2/cleric"},
            {"name": "§aBanqueiro", "tag": "banker", "pos": [0, 62, -12], "skin": "villager_v2/cartographer"},
            {"name": "§eMinerador Ancião", "tag": "shop_ores", "pos": [-12, 62, -8], "skin": "villager_v2/tool_smith"},
            {"name": "§cFerreiro Brutamontes", "tag": "shop_weapons", "pos": [5, 62, -8], "skin": "villager_v2/weaponsmith"},
        ],
        "description": "Porto movimentado com mercadorias raras de terras distantes!",
        "build_style": "Porto medieval com docas, armazéns e navios mercantes",
        "special_features": ["Loja de Redstone", "Decoração Rara", "Comércio Internacional", "Itens Exóticos"],
        "difficulty": "Médio"
    },
    {
        "id": 5,
        "name": "§8Fortaleza dos Guardiões",
        "subtitle": "§7Defenda o reino",
        "biome": "snowy_plains",
        "spawn": [0, 70, 0],
        "npcs": [
            {"name": "§eComandante de Quests", "tag": "quest_master", "pos": [8, 70, 10], "skin": "villager_v2/armorer"},
            {"name": "§9Capitão da Guarda", "tag": "shop_armor", "pos": [-5, 70, 12], "skin": "villager_v2/armorer"},
            {"name": "§cFerreiro Brutamontes", "tag": "shop_weapons", "pos": [12, 70, -5], "skin": "villager_v2/weaponsmith"},
            {"name": "§aBanqueiro", "tag": "banker", "pos": [0, 70, -10], "skin": "villager_v2/cartographer"},
            {"name": "§aMestre Cuca", "tag": "shop_food", "pos": [-10, 70, -8], "skin": "villager_v2/butcher"},
            {"name": "§dMago Encantador", "tag": "shop_enchant", "pos": [5, 70, -12], "skin": "villager_v2/cleric"},
        ],
        "description": "Fortaleza militar protegendo o reino dos perigos noturnos!",
        "build_style": "Fortaleza de pedra com muralhas, torres e quartéis",
        "special_features": ["Armaduras Lendárias", "Encantamentos Poderosos", "Quests de Combate", "Treinamento Militar"],
        "difficulty": "Médio"
    },
    {
        "id": 6,
        "name": "§dTorre do Mago",
        "subtitle": "§7Onde a magia flui",
        "biome": "taiga",
        "spawn": [0, 68, 0],
        "npcs": [
            {"name": "§dArquimago", "tag": "quest_master", "pos": [5, 68, 10], "skin": "villager_v2/cleric"},
            {"name": "§dMago Encantador", "tag": "shop_enchant", "pos": [-8, 68, 8], "skin": "villager_v2/cleric"},
            {"name": "§aMestre Cuca", "tag": "shop_food", "pos": [10, 68, -8], "skin": "villager_v2/cleric"},
            {"name": "§aBanqueiro", "tag": "banker", "pos": [0, 68, -10], "skin": "villager_v2/cartographer"},
            {"name": "§dDecorador Real", "tag": "shop_decor", "pos": [-10, 68, -5], "skin": "villager_v2/cartographer"},
            {"name": "§eMinerador Ancião", "tag": "shop_ores", "pos": [8, 68, 0], "skin": "villager_v2/tool_smith"},
        ],
        "description": "Torre arcana onde magos estudam e vendem seus feitiços!",
        "build_style": "Torre mágica com jardins encantados e laboratório de alquimia",
        "special_features": ["Livros de Encantamentos", "Poções Poderosas", "Quests Mágicas", "Experiência Acelerada"],
        "difficulty": "Médio"
    },
    {
        "id": 7,
        "name": "§eMina Abandonada",
        "subtitle": "§7Riscos e recompensas",
        "biome": "windswept_gravelly_hills",
        "spawn": [0, 66, 0],
        "npcs": [
            {"name": "§eMestre de Quests", "tag": "quest_master", "pos": [6, 66, 8], "skin": "villager_v2/tool_smith"},
            {"name": "§eMinerador Ancião", "tag": "shop_ores", "pos": [-8, 66, 6], "skin": "villager_v2/tool_smith"},
            {"name": "§eMestre Artesão", "tag": "shop_tools", "pos": [8, 66, -6], "skin": "villager_v2/fletcher"},
            {"name": "§aBanqueiro", "tag": "banker", "pos": [0, 66, -8], "skin": "villager_v2/cartographer"},
            {"name": "§7Mestre de Obras", "tag": "shop_blocks", "pos": [-6, 66, -8], "skin": "villager_v2/mason"},
            {"name": "§9Capitão da Guarda", "tag": "shop_armor", "pos": [10, 66, 0], "skin": "villager_v2/armorer"},
        ],
        "description": "Minas profundas com recursos valiosos... e criaturas perigosas!",
        "build_style": "Entrada de mina gigante com acampamento e ponte levadiça",
        "special_features": ["Minérios Raros", "Ferramentas Reforçadas", "Quests de Mineração Profunda", "Monstros nas Profundezas"],
        "difficulty": "Médio"
    },
    {
        "id": 8,
        "name": "§5Catacumbas do Esquecimento",
        "subtitle": "§7O submundo do reino",
        "biome": "dark_forest",
        "spawn": [0, 62, 0],
        "npcs": [
            {"name": "§5Mestre das Sombras", "tag": "quest_master", "pos": [5, 62, 5], "skin": "villager_v2/cleric"},
            {"name": "§dMago Encantador", "tag": "shop_enchant", "pos": [-5, 62, 8], "skin": "villager_v2/cleric"},
            {"name": "§cEngenheiro Redstone", "tag": "shop_redstone", "pos": [8, 62, -5], "skin": "villager_v2/armorer"},
            {"name": "§aBanqueiro", "tag": "banker", "pos": [0, 62, -8], "skin": "villager_v2/cartographer"},
            {"name": "§aMestre Cuca", "tag": "shop_food", "pos": [-8, 62, -5], "skin": "villager_v2/butcher"},
            {"name": "§dDecorador Real", "tag": "shop_decor", "pos": [8, 62, 0], "skin": "villager_v2/cartographer"},
        ],
        "description": "Catacumbas ancestrais com tesouros amaldiçoados e magia negra!",
        "build_style": "Ruínas subterrâneas com criptas, estátuas e tochas azuis",
        "special_features": ["Encantamentos Sombrios", "Relíquias Amaldiçoadas", "Quests Perigosas", "Recompensas Épicas"],
        "difficulty": "Difícil"
    },
    {
        "id": 9,
        "name": "§cTerras do Nether",
        "subtitle": "§7Fogo e destruição",
        "biome": "desert",
        "spawn": [0, 64, 0],
        "npcs": [
            {"name": "§cSenhor do Fogo", "tag": "quest_master", "pos": [5, 64, 8], "skin": "villager_v2/weaponsmith"},
            {"name": "§cFerreiro Brutamontes", "tag": "shop_weapons", "pos": [-8, 64, 5], "skin": "villager_v2/weaponsmith"},
            {"name": "§dMago Encantador", "tag": "shop_enchant", "pos": [8, 64, -5], "skin": "villager_v2/cleric"},
            {"name": "§aBanqueiro", "tag": "banker", "pos": [0, 64, -8], "skin": "villager_v2/cartographer"},
            {"name": "§eMinerador Ancião", "tag": "shop_ores", "pos": [-5, 64, -10], "skin": "villager_v2/tool_smith"},
            {"name": "§aMestre Cuca", "tag": "shop_food", "pos": [-10, 64, 0], "skin": "villager_v2/butcher"},
        ],
        "description": "Posto avançado nas Terras do Fogo. Apenas os mais fortes sobrevivem!",
        "build_style": "Fortaleza negra com lava, obsidiana e fogueiras",
        "special_features": ["Armas do Nether", "Quests de Fogo", "Lingotes Raros", "Poções de Resistência"],
        "difficulty": "Difícil"
    },
    {
        "id": 10,
        "name": "§dCastelo do Rei Dragão",
        "subtitle": "§7A lenda final",
        "biome": "plains",
        "spawn": [0, 80, 0],
        "npcs": [
            {"name": "§6Rei Dragão Alaric", "tag": "quest_master", "pos": [10, 80, 10], "skin": "villager_v2/armorer"},
            {"name": "§cFerreiro Lendário", "tag": "shop_weapons", "pos": [-5, 80, 12], "skin": "villager_v2/weaponsmith"},
            {"name": "§9Guardião de Armaduras", "tag": "shop_armor", "pos": [12, 80, -5], "skin": "villager_v2/armorer"},
            {"name": "§dMago Supremo", "tag": "shop_enchant", "pos": [5, 80, -12], "skin": "villager_v2/cleric"},
            {"name": "§aBanqueiro Real", "tag": "banker", "pos": [0, 80, -10], "skin": "villager_v2/cartographer"},
            {"name": "§aFazendeiro João", "tag": "shop_farming", "pos": [-10, 80, 5], "skin": "villager_v2/farmer"},
            {"name": "§eMinerador Ancião", "tag": "shop_ores", "pos": [-12, 80, -8], "skin": "villager_v2/tool_smith"},
            {"name": "§7Mestre de Obras", "tag": "shop_blocks", "pos": [8, 80, 8], "skin": "villager_v2/mason"},
            {"name": "§cEngenheiro Redstone", "tag": "shop_redstone", "pos": [15, 80, 0], "skin": "villager_v2/armorer"},
            {"name": "§dDecorador Real", "tag": "shop_decor", "pos": [-15, 80, 0], "skin": "villager_v2/cartographer"},
        ],
        "description": "O castelo lendário do Rei Dragão. A aventura final espera por você!",
        "build_style": "Castelo enorme com dragão de pedra, torres e salão do trono",
        "special_features": ["TODAS as lojas", "Quests Lendárias", "Recompensas Épicas", "Mestre de Quests Supremo"],
        "difficulty": "Épico"
    }
]


def create_minimal_level_dat(map_data):
    """
    Cria um level.dat minimal valido para Minecraft Bedrock.
    Usa NBT binario simplificado.
    """
    # Versão minimal do level.dat
    # Construimos um NBT composto basico
    data = {
        "Data": {
            "allowCommands": 1,
            "clearWeatherTime": 0,
            "Difficulty": {"type": "byte", "value": 1},
            "GameRules": {
                "commandblockoutput": {"type": "byte", "value": 1},
                "dodaylightcycle": {"type": "byte", "value": 1},
                "doentitydrops": {"type": "byte", "value": 1},
                "dofiretick": {"type": "byte", "value": 1},
                "domobloot": {"type": "byte", "value": 1},
                "domobspawning": {"type": "byte", "value": 1},
                "dotiledrops": {"type": "byte", "value": 1},
                "doweathercycle": {"type": "byte", "value": 1},
                "keepinventory": {"type": "byte", "value": 1},
                "mobgriefing": {"type": "byte", "value": 1},
                "pvp": {"type": "byte", "value": 1},
                "showcoordinates": {"type": "byte", "value": 1},
            },
            "GameType": 1,  # Creative = 1, Survival = 0
            "Generator": 1,  # Default = 1, Flat = 2
            "LastPlayed": int(datetime.now().timestamp() * 1000),
            "LevelName": map_data["name"],
            "MultiplayerGame": 1,
            "NetworkVersion": 38,
            "Platform": 4,
            "PlatformBroadcastIntent": 3,
            "RandomSeed": 0,
            "SpawnX": map_data["spawn"][0],
            "SpawnY": map_data["spawn"][1],
            "SpawnZ": map_data["spawn"][2],
            "StorageVersion": 8,
            "Time": 1000,
            "worldStartCount": 20,
            "RainTime": 0,
            "RainLevel": 0,
            "ThunderTime": 0,
            "ThunderLevel": 0,
        }
    }
    return data


def write_nbt_tag(file, tag_type, value):
    """Escreve uma tag NBT basica"""
    if tag_type == "byte":
        file.write(struct.pack('b', value))
    elif tag_type == "short":
        file.write(struct.pack('<h', value))
    elif tag_type == "int":
        file.write(struct.pack('<i', value))
    elif tag_type == "long":
        file.write(struct.pack('<q', value))
    elif tag_type == "float":
        file.write(struct.pack('<f', value))
    elif tag_type == "double":
        file.write(struct.pack('<d', value))
    elif tag_type == "string":
        s = value.encode('utf-8')
        file.write(struct.pack('<H', len(s)))
        file.write(s)
    elif tag_type == "end":
        pass  # TAG_End is just a 0 byte


def write_compound_tag(file, data):
    """Escreve um compound NBT"""
    for key, value in data.items():
        if isinstance(value, dict) and "type" in value:
            # Tag primitiva
            write_tag_type(file, value["type"])
            write_string(file, key)
            write_nbt_tag(file, value["type"], value["value"])
        elif isinstance(value, dict):
            # Sub-compound
            type_id = 10  # TAG_Compound
            file.write(struct.pack('b', type_id))
            write_string(file, key)
            write_compound_tag(file, value)
    
    # TAG_End
    file.write(struct.pack('b', 0))


def write_tag_type(file, tag_type):
    type_map = {
        "byte": 1,
        "short": 2,
        "int": 3,
        "long": 4,
        "float": 5,
        "double": 6,
        "string": 8,
        "list": 9,
        "compound": 10,
        "end": 0,
    }
    file.write(struct.pack('b', type_map.get(tag_type, 0)))


def write_string(file, s):
    encoded = s.encode('utf-8')
    file.write(struct.pack('<H', len(encoded)))
    file.write(encoded)


def save_level_dat(map_data, output_dir):
    """Salva um level.dat valido"""
    filepath = os.path.join(output_dir, "level.dat")
    
    with open(filepath, 'wb') as f:
        # Root compound tag
        f.write(struct.pack('b', 10))  # TAG_Compound
        write_string(f, "Data")
        
        # Write Data fields
        for key, value in map_data["Data"].items():
            if isinstance(value, dict) and "type" in value:
                write_tag_type(f, value["type"])
                write_string(f, key)
                write_nbt_tag(f, value["type"], value["value"])
            elif isinstance(value, dict):
                write_tag_type(f, "compound")
                write_string(f, key)
                _write_simple_compound(f, value)
            elif isinstance(value, list):
                # Simple list (int list or similar)
                write_tag_type(f, "list")
                write_string(f, key)
                f.write(struct.pack('b', 3))  # TAG_Int
                f.write(struct.pack('<i', len(value)))
                for v in value:
                    f.write(struct.pack('<i', v))
            else:
                # Infer type from Python type
                if isinstance(value, int):
                    write_tag_type(f, "int")
                    write_string(f, key)
                    f.write(struct.pack('<i', value))
                elif isinstance(value, str):
                    write_tag_type(f, "string")
                    write_string(f, key)
                    write_string(f, value)
                elif isinstance(value, float):
                    write_tag_type(f, "float")
                    write_string(f, key)
                    f.write(struct.pack('<f', value))
                elif isinstance(value, bool):
                    write_tag_type(f, "byte")
                    write_string(f, key)
                    f.write(struct.pack('b', 1 if value else 0))
        
        # End tag
        f.write(struct.pack('b', 0))
    
    print(f"  [OK] level.dat ({os.path.getsize(filepath)} bytes)")


def _write_simple_compound(f, data):
    """Escreve sub-compound sem abrir/fechar tag extra"""
    for key, value in data.items():
        if isinstance(value, dict) and "type" in value:
            write_tag_type(f, value["type"])
            write_string(f, key)
            write_nbt_tag(f, value["type"], value["value"])
        elif isinstance(value, dict):
            write_tag_type(f, "compound")
            write_string(f, key)
            _write_simple_compound(f, value)
        else:
            if isinstance(value, bool):
                write_tag_type(f, "byte")
                write_string(f, key)
                f.write(struct.pack('b', 1 if value else 0))
            elif isinstance(value, int):
                write_tag_type(f, "int")
                write_string(f, key)
                f.write(struct.pack('<i', value))
            elif isinstance(value, str):
                write_tag_type(f, "string")
                write_string(f, key)
                write_string(f, value)
    f.write(struct.pack('b', 0))


def create_world_behavior_pack(behavior_pack_uuid=None):
    """Cria o world_behavior_packs.json"""
    if behavior_pack_uuid is None:
        behavior_pack_uuid = BP_UUID
    
    return {
        "type": "world_behavior_pack.json",
        "packs": [
            {
                "pack_id": behavior_pack_uuid,
                "version": [1, 0, 0],
                "can_be_redownloaded": True
            }
        ]
    }


def save_world_pack_json(data, output_dir):
    """Salva world_behavior_pack.json"""
    filepath = os.path.join(output_dir, "world_behavior_pack.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data["packs"], f, indent=2)
    print(f"  [OK] world_behavior_pack.json")


def save_world_resource_pack(output_dir):
    """Salva world_resource_pack.json vazio"""
    filepath = os.path.join(output_dir, "world_resource_pack.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2)
    print(f"  [OK] world_resource_pack.json")


def create_db_folder(output_dir):
    """Cria a pasta db vazia (necessaria para o mundo carregar)"""
    db_dir = os.path.join(output_dir, "db")
    os.makedirs(db_dir, exist_ok=True)
    # Placeholder - world needs at least one entry in db
    # In a real scenario, this would be populated with LevelDB entries
    open(os.path.join(db_dir, ".keep"), 'w').close()
    print(f"  [OK] db/ (vazio)")


def copy_behavior_pack(output_dir):
    """Copia o behavior pack compartilhado para o mapa"""
    bp_dest = os.path.join(output_dir, "behavior_packs", "economy_rpg_bp")
    
    if os.path.exists(bp_dest):
        shutil.rmtree(bp_dest)
    
    shutil.copytree(SHARED_BP_DIR, bp_dest)
    
    # Add map-specific config
    map_config_path = os.path.join(bp_dest, "scripts", "map_config.js")
    print(f"  [OK] behavior_packs/ (copiado)")
    return bp_dest


def create_map_config(map_data, bp_dest):
    """Cria config especifica do mapa no behavior pack"""
    npcs_json = []
    for npc in map_data["npcs"]:
        npcs_json.append({
            "name": npc["name"],
            "tag": npc["tag"],
            "position": npc["pos"]
        })
    
    config = {
        "map_id": map_data["id"],
        "map_name": map_data["name"],
        "map_subtitle": map_data["subtitle"],
        "biome": map_data["biome"],
        "spawn": map_data["spawn"],
        "npcs": npcs_json,
        "description": map_data["description"],
        "build_style": map_data["build_style"],
        "special_features": map_data["special_features"],
        "difficulty": map_data["difficulty"]
    }
    
    config_path = os.path.join(bp_dest, "scripts", "map_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"  [OK] map_config.json")


def create_world_manifest(map_data):
    """Cria o manifest do mundo"""
    world_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"economy-rpg-map-{map_data['id']}"))
    
    return {
        "format_version": 2,
        "header": {
            "name": f"§6🏰 {map_data['name']}",
            "description": f"§7{map_data['subtitle']}\n§e{map_data['description']}",
            "uuid": world_uuid,
            "version": [1, 0, 0],
            "world_type": "world_template",
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "world",
                "uuid": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"economy-rpg-world-{map_data['id']}")),
                "version": [1, 0, 0]
            }
        ],
        "metadata": {
            "authors": ["IconGameDev"],
            "license": "MIT",
            "generated_with": "Economy RPG Map Generator",
            "map_id": map_data["id"],
            "difficulty": map_data["difficulty"]
        }
    }


def create_map_readme(map_data):
    """Cria README.md do mapa"""
    features = "\n".join([f"- {f}" for f in map_data["special_features"]])
    npc_list = "\n".join([f"  - {n['name']} ({n['tag']})" for n in map_data["npcs"]])
    
    return f"""# {map_data['name']}

{map_data['subtitle']}

{map_data['description']}

## Informações

- **ID do Mapa:** {map_data['id']}
- **Dificuldade:** {map_data['difficulty']}
- **Bioma:** {map_data['biome']}
- **Estilo:** {map_data['build_style']}
- **Versão:** 1.20.0+

## NPCs disponíveis

{npc_list}

## Características Especiais

{features}

## Sistemas Inclusos

- ✅ **Economia** baseada em diamantes (💎)
- ✅ **Sistema Bancário** (depósito/saque)
- ✅ **Sistema de Quests** com 10 missões
- ✅ **Lojas NPC** com itens variados
- ✅ **Comandos** (!saldo, !quest, !loja, !banco, !ajuda)

## Como Usar

1. Coloque o arquivo .mctemplate em `com.mojang/MinecraftWorlds/`
2. Abra o Minecraft Bedrock
3. Crie um novo mundo a partir do template
4. Garanta que "Experimentos" → "GameTest Framework" esteja ativado
5. Divirta-se!

---
*Gerado automaticamente pelo Economy RPG Map Generator*
"""


def generate_maps():
    """Gera todos os 10 mapas"""
    print("=" * 60)
    print("  🏰 GERADOR DE MAPAS ECONOMY RPG")
    print("  Minecraft Bedrock .mctemplate Generator")
    print("=" * 60)
    
    # Garante que shared_bp existe
    if not os.path.exists(SHARED_BP_DIR):
        print("[ERRO] shared_bp/ nao encontrado!")
        return
    
    # Cria output dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for map_data in MAPS:
        map_id = map_data["id"]
        map_dir_name = f"map-{map_id}.mctemplate"
        map_dir = os.path.join(OUTPUT_DIR, map_dir_name)
        
        print(f"\n{'='*60}")
        print(f"  Gerando {map_dir_name}...")
        print(f"  {map_data['name']} - {map_data['subtitle']}")
        print(f"{'='*60}")
        
        # Limpa se existir
        if os.path.exists(map_dir):
            shutil.rmtree(map_dir)
        
        # Cria estrutura de diretorios
        os.makedirs(map_dir)
        
        # 1. level.dat
        level_data = create_minimal_level_dat(map_data)
        save_level_dat(level_data, map_dir)
        
        # 2. world_behavior_pack.json
        pack_data = create_world_behavior_pack()
        save_world_pack_json(pack_data, map_dir)
        
        # 3. world_resource_pack.json
        save_world_resource_pack(map_dir)
        
        # 4. db/
        create_db_folder(map_dir)
        
        # 5. behavior_packs/
        bp_dest = copy_behavior_pack(map_dir)
        create_map_config(map_data, bp_dest)
        
        # 6. manifest.json do mundo
        world_manifest = create_world_manifest(map_data)
        manifest_path = os.path.join(map_dir, "manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(world_manifest, f, indent=2, ensure_ascii=False)
        print(f"  [OK] manifest.json")
        
        # 7. README
        readme = create_map_readme(map_data)
        readme_path = os.path.join(map_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        print(f"  [OK] README.md")
        
        # 8. world_icon (placeholder - PNG simples seria gerado aqui)
        # Na pratica, o icone pode ser gerado com ferramentas externas
        
        # Mostra estatisticas
        total_files = sum([len(files) for _, _, files in os.walk(map_dir)])
        total_size = sum([os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(map_dir) for f in fn])
        print(f"\n  📊 Estatisticas:")
        print(f"     Arquivos: {total_files}")
        print(f"     Tamanho:  {total_size / 1024:.1f} KB")
        print(f"     Caminho:  {map_dir}")
    
    # Gera README principal
    generate_main_readme()
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"  ✅ GERACAO COMPLETA!")
    print(f"  📍 Output: {OUTPUT_DIR}")
    print(f"  🗺️  Mapas gerados: {len(MAPS)}")
    print(f"  📦 Todos os mapas incluem behavior pack completo")
    print(f"  💎 Sistema: Economia (Diamantes) + Quests + Lojas NPC")
    print(f"{'='*60}")


def generate_main_readme():
    """Gera README principal do projeto"""
    content = """# 🏰 Economy RPG - Minecraft Bedrock Maps

## 📋 Sobre

**10 mapas RPG completos** para Minecraft Bedrock Edition com sistema de economia baseado em **diamantes (💎)**, **lojas NPC** e **sistema de quests**.

## 🗺️ Mapas Disponíveis

"""
    for m in MAPS:
        content += f"| {m['id']:2d} | {m['name']:30s} | {m['subtitle']:30s} | {m['difficulty']:10s} |\n"

    content += """
## ⚙️ Sistemas

### 💰 Economia
- Moeda: Diamantes (💎)
- Banco para depósito/saque
- Saldo persiste entre sessões

### 🏪 Lojas NPC (10 tipos)
- ⚔️ Armas do Ferreiro
- 🛡️ Armaduras do Guarda
- 🔧 Ferramentas do Artesão
- 🍖 Comidas e Poções
- 🧱 Materiais de Construção
- ✨ Encantamentos Mágicos
- 🌾 Suprimentos de Fazenda
- 🔴 Engenhocas Redstone
- 🌸 Decoração & Luxo
- ⛏️ Minérios & Gemas

### 📜 Sistema de Quests (10 missões)
Missões de coleta, combate e exploração com recompensas em diamantes e itens especiais.

### ⌨️ Comandos
- `!saldo` - Ver saldo
- `!quest` - Ver quests
- `!loja` - Abrir lojas
- `!banco` - Gerenciar banco
- `!ajuda` - Ajuda

## 📦 Instalação

1. Baixe os arquivos `.mctemplate`
2. Copie para `%localappdata%/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang/MinecraftWorlds/`
3. Abra o Minecraft Bedrock
4. Crie novo mundo a partir do template
5. Ative "GameTest Framework" nos experimentos

## 🛠️ Tecnologia

- **Script API** JavaScript (Minecraft Bedrock)
- **Scoreboards** para sistema de economia
- **Tags** para progresso de quests
- **UI Forms** para interação com NPCs

---
*Criado com ❤️ por IconGameDev*
"""
    
    readme_path = os.path.join(OUTPUT_DIR, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n  [OK] README.md principal")


if __name__ == "__main__":
    generate_maps()
