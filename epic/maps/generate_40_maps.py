#!/usr/bin/env python3
"""Generate 40 new Fortnite Creative maps in epic/maps/ (10 PvP, 10 PvE/co-op, 10 racing/parkour, 10 social/hub)."""

import json, os, textwrap

OUT = os.path.dirname(os.path.abspath(__file__))

def w(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {os.path.basename(path)}")

# ── PVP MAPS (11–20) ──────────────────────────────────────────────────

pvp_maps = [
    {
        "template": "capture-the-flag",
        "display_name": "Capture the Flag — Bandeira Vermelha vs Azul",
        "description": "5v5 capture the flag. Cada time protege sua base e tenta capturar a bandeira adversária. 3 capturas para vencer. Veículos e power-ups no centro do mapa.",
        "tags": ["capture-the-flag", "pvp", "competitive", "5v5", "team"],
        "max_players": 10, "game_mode": "capture_the_flag", "team_size": [5],
        "elimination_mode": "respawn_after_cap", "allow_respawn": True,
        "respawn_delay_sec": 5, "rounds_to_win": 3, "round_time_sec": 600,
        "flag_capture_time_sec": 10, "flag_drop_on_kill": True,
        "starting_health": 100, "starting_shield": 50,
        "pois": [
            {"id": "base_blue", "name": "Base Azul", "type": "urban", "size_tier": "small"},
            {"id": "base_red", "name": "Base Vermelha", "type": "urban", "size_tier": "small"},
            {"id": "mid_01", "name": "Centro", "type": "forest", "size_tier": "medium"},
            {"id": "power_up", "name": "Torre de Power-Ups", "type": "special", "size_tier": "small"},
        ],
    },
    {
        "template": "sniper-duel",
        "display_name": "Sniper Duel — Precisão Mortal",
        "description": "8 jogadores, apenas snipers. Combate de longa distância em um vale montanhoso com cobertura limitada. Bolha de tempestade fechando lentamente.",
        "tags": ["sniper", "pvp", "competitive", "solo", "precision"],
        "max_players": 8, "game_mode": "free_for_all", "team_size": [1],
        "elimination_mode": "score_target", "elimination_target": 25,
        "starting_health": 100, "starting_shield": 0,
        "weapons_only": ["sniper_bolt", "sniper_heavy", "sniper_hunting"],
        "infinite_ammo": True, "headshot_multiplier": 2.5,
        "storm_phases": 4, "storm_wait_time_sec": 45, "storm_shrink_time_sec": 60,
    },
    {
        "template": "infected",
        "display_name": "Infected — Último Sobrevivente",
        "description": "1 infectado no início. Cada eliminação vira outro infectado. Último humano vivo vence. Armadilhas e esconderijos espalhados pelo mapa.",
        "tags": ["infected", "pvp", "party", "casual", "transformation"],
        "max_players": 16, "game_mode": "infected", "team_size": [1],
        "elimination_mode": "last_survivor", "starting_infected": 1,
        "infected_weapon": "pickaxe_legendary", "human_weapons": ["pistol", "shotgun_tactical"],
        "round_time_sec": 300, "rounds_to_win": 3,
        "starting_health": 100, "allow_respawn": False,
        "pois": [
            {"id": "zone_a", "name": "Armazém", "type": "industrial", "size_tier": "medium"},
            {"id": "zone_b", "name": "Floresta Negra", "type": "forest", "size_tier": "large"},
            {"id": "zone_c", "name": "Subterrâneo", "type": "underground", "size_tier": "medium"},
        ],
    },
    {
        "template": "king-of-the-hill",
        "display_name": "King of the Hill — Dominação Central",
        "description": "8v8. Controle o ponto central por tempo acumulado. Zona de tempestade fecha ao redor do ponto. Primeiro time com 100 pontos vence.",
        "tags": ["king-of-the-hill", "pvp", "competitive", "domination", "8v8"],
        "max_players": 16, "game_mode": "king_of_the_hill", "team_size": [8],
        "elimination_mode": "score_target", "elimination_target": 100,
        "hill_capture_time_sec": 15, "hill_points_per_sec": 2,
        "hill_locations": 3, "hill_rotation_interval_sec": 90,
        "allow_respawn": True, "respawn_delay_sec": 8,
        "starting_health": 100, "starting_shield": 50,
    },
    {
        "template": "free-for-all",
        "display_name": "Free for All — Vale-Tudo",
        "description": "12 jogadores, todos contra todos. 50 eliminações para vencer. Spawn aleatório no mapa. Loot espalhado e baús aéreos frequentes.",
        "tags": ["free-for-all", "pvp", "casual", "solo", "ffa"],
        "max_players": 12, "game_mode": "free_for_all", "team_size": [1],
        "elimination_mode": "score_target", "elimination_target": 50,
        "allow_respawn": True, "respawn_delay_sec": 5, "respawn_mode": "random",
        "loot_tier_weights": {"common": 15, "uncommon": 30, "rare": 35, "epic": 15, "legendary": 5},
        "supply_drops": {"count": 5, "interval_sec": 60},
    },
    {
        "template": "payload",
        "display_name": "Payload — Ataque e Defesa",
        "description": "6v6. Time atacante empurra o carrinho até o fim do trajeto. Defensores tentam impedir. 2 rodadas com troca de lado.",
        "tags": ["payload", "pvp", "competitive", "6v6", "escort"],
        "max_players": 12, "game_mode": "payload", "team_size": [6],
        "elimination_mode": "round_win", "rounds_to_win": 2,
        "round_time_sec": 480, "payload_speed": "medium",
        "payload_checkpoints": 3, "overtime_enabled": True,
        "allow_respawn": True, "respawn_delay_sec": 6,
        "track_length_tiles": 80,
    },
    {
        "template": "grid-war",
        "display_name": "Grid War — Guerra Territorial",
        "description": "10v10. Conquiste quadrados do grid pintando o chão. Time com mais quadrados ao final do tempo vence. Construção liberada.",
        "tags": ["grid-war", "pvp", "competitive", "10v10", "territory"],
        "max_players": 20, "game_mode": "grid_war", "team_size": [10],
        "elimination_mode": "territory_control", "round_time_sec": 600,
        "grid_size": "16x16", "paint_speed": 1.5,
        "allow_respawn": True, "respawn_delay_sec": 5,
        "starting_materials": {"wood": 200, "stone": 100, "metal": 50},
        "harvest_rate_multiplier": 3.0,
    },
    {
        "template": "sword-fight",
        "display_name": "Sword Fight — Batalha de Lâminas",
        "description": "8 jogadores, apenas espadas (Kinetic Blade, Lightsaber, Infinity Blade). Combate corpo a corpo em arena medieval com plataformas móveis.",
        "tags": ["sword-fight", "pvp", "casual", "melee", "arena"],
        "max_players": 8, "game_mode": "free_for_all", "team_size": [1],
        "elimination_mode": "score_target", "elimination_target": 20,
        "weapons_only": ["kinetic_blade", "lightsaber", "infinity_blade"],
        "starting_health": 150, "starting_shield": 50,
        "gravity": 0.8, "fall_damage": False,
        "power_ups": {"damage_boost": True, "speed_boost": True, "shield_regen": True},
    },
    {
        "template": "build-battle-arena",
        "display_name": "Build Battle Arena — Construção e Combate",
        "description": "4v4. Combina construção rápida e combate. Área pequena com materiais infinitos. Primeiro a 30 eliminações vence. Inspirado em Arena BHE.",
        "tags": ["build-battle", "pvp", "competitive", "4v4", "building"],
        "max_players": 8, "game_mode": "team_elimination", "team_size": [4],
        "elimination_mode": "score_target", "elimination_target": 30,
        "allow_respawn": True, "respawn_delay_sec": 3,
        "starting_materials": {"wood": 999, "stone": 999, "metal": 999},
        "harvest_rate_multiplier": 10.0,
        "arena_size_tiles": 30, "storm_phases": 2,
    },
    {
        "template": "arena-duos",
        "display_name": "Arena Duos — Parceria Letal",
        "description": "6 duplas em batalha. 20 eliminações para vencer. Storm circle rápido. Loot equilibrado. Ideal para treino de duplas competitivo.",
        "tags": ["arena-duos", "pvp", "competitive", "duos", "2v2v2"],
        "max_players": 12, "game_mode": "battle_royale", "team_size": [2],
        "elimination_mode": "score_target", "elimination_target": 20,
        "allow_respawn": False, "down_but_not_out": True,
        "storm_phases": 6, "storm_wait_time_sec": 60, "storm_shrink_time_sec": 90,
        "starting_health": 100, "max_shield": 100,
    },
]

# ── PVE / CO-OP MAPS (21–30) ─────────────────────────────────────────

pve_maps = [
    {
        "template": "horde-survival",
        "display_name": "Horde Survival — Noite dos Zumbis",
        "description": "4 jogadores contra ondas infinitas de zumbis. Cada 5 ondas um mini-boss aparece. Compre armas entre as ondas. Score baseado em ondas sobrevividas.",
        "tags": ["horde", "pve", "coop", "survival", "4-player", "zombie"],
        "max_players": 4, "game_mode": "horde_survival", "team_size": [4],
        "starting_health": 100, "starting_materials": {"wood": 50, "stone": 0, "metal": 0},
        "waves": {"total": 30, "enemy_scaling": "exponential", "boss_interval": 5},
        "currency_system": {"type": "gold", "earn_per_kill": 10, "earn_per_wave": 50},
        "shop_items": [{"name": "pistol", "cost": 100}, {"name": "shotgun", "cost": 300}, {"name": "rifle", "cost": 500}],
        "allow_respawn": True, "respawn_delay_sec": 15, "lives_pool": 20,
    },
    {
        "template": "wave-defense",
        "display_name": "Wave Defense — Escudo Final",
        "description": "Até 8 jogadores defendem um gerador central. 25 ondas de inimigos variados (zumbis, robôs, criaturas). Construa defesas entre as ondas.",
        "tags": ["wave-defense", "pve", "coop", "defense", "building"],
        "max_players": 8, "game_mode": "wave_defense", "team_size": [8],
        "starting_health": 100, "starting_shield": 50,
        "waves": {"total": 25, "enemy_types": ["zombie", "robot", "creature", "flying"], "boss_waves": [10, 20, 25]},
        "generator_health": 5000, "generator_shield": 1000,
        "starting_materials": {"wood": 200, "stone": 100, "metal": 50},
        "allow_respawn": True, "respawn_delay_sec": 10,
    },
    {
        "template": "monster-hunt",
        "display_name": "Monster Hunt — Caça aos Gigantes",
        "description": "4 jogadores caçam monstros gigantes espalhados pelo mapa. Cada monstro tem mecânicas únicas e fraquezas. Explore, colete loot e derrote os chefes.",
        "tags": ["monster-hunt", "pve", "coop", "exploration", "boss"],
        "max_players": 4, "game_mode": "monster_hunt", "team_size": [4],
        "monsters": [
            {"name": "Rei da Montanha", "zone": "snow", "health": 10000, "weakness": "fire"},
            {"name": "Titã do Pântano", "zone": "swamp", "health": 8000, "weakness": "energy"},
            {"name": "Guardião do Vulcão", "zone": "lava", "health": 12000, "weakness": "ice"},
        ],
        "starting_health": 100, "starting_shield": 100, "lives_pool": 9,
        "allow_respawn": True, "respawn_delay_sec": 20,
        "pois": [
            {"id": "snow_zone", "name": "Pico Gelado", "type": "snow", "size_tier": "large"},
            {"id": "swamp_zone", "name": "Pântano Sombrio", "type": "forest", "size_tier": "large"},
            {"id": "lava_zone", "name": "Vulcão", "type": "desert", "size_tier": "large"},
        ],
    },
    {
        "template": "tower-defense",
        "display_name": "Tower Defense — Defesa da Torre",
        "description": "2-4 jogadores constroem torres e armadilhas para defender o cristal central. 30 ondas de inimigos. Melhore suas torres entre as ondas.",
        "tags": ["tower-defense", "pve", "coop", "strategy", "building"],
        "max_players": 4, "game_mode": "tower_defense", "team_size": [4],
        "waves": {"total": 30, "path_count": 3},
        "crystal_health": 3000,
        "tower_types": ["auto_turret", "sniper_tower", "flame_tower", "freeze_tower", "shock_tower"],
        "starting_gold": 500, "gold_per_kill": 15, "gold_per_wave": 100,
        "allow_respawn": True,
    },
    {
        "template": "zombie-survival",
        "display_name": "Zombie Survival — Apocalipse",
        "description": "Jogadores solos ou em squad. Mapa aberto com saque, missões e hordas de zumbis. Complete objetivos para extrair de helicóptero. Inspirado em CoD Zombies.",
        "tags": ["zombie", "pve", "coop", "open-world", "survival"],
        "max_players": 4, "game_mode": "zombie_survival", "team_size": [4],
        "starting_health": 100, "starting_shield": 0,
        "zombie_types": ["walker", "sprinter", "exploder", "giant", "poison"],
        "difficulty_levels": 10, "round_time_sec": 1800,
        "objectives": ["power_activation", "teleporter_build", "pack_a_punch", "boss_fight"],
        "loot_pool": {"chest_spawn_rate": 0.6, "floor_loot_density": 0.3},
    },
    {
        "template": "dungeon-crawl",
        "display_name": "Dungeon Crawl — Masmorra Sombria",
        "description": "1-3 jogadores exploram masmorras geradas proceduralmente. Salas com armadilhas, puzzles e monstros. Chefão no final. RPG elements com upgrade de armas.",
        "tags": ["dungeon", "pve", "coop", "rpg", "exploration"],
        "max_players": 3, "game_mode": "dungeon_crawl", "team_size": [3],
        "dungeon_floors": 5, "rooms_per_floor": 8,
        "room_types": ["combat", "puzzle", "treasure", "rest", "boss"],
        "starting_health": 100, "starting_shield": 0,
        "lives_pool": 3, "perma_death": False,
        "upgrade_stations": ["weapon_bench", "health_shrine", "shield_fountain"],
    },
    {
        "template": "boss-rush",
        "display_name": "Boss Rush — Desafio dos Titãs",
        "description": "Derrote 5 chefes consecutivos com apenas 3 vidas. Cada chefe é único com habilidades especiais. Entre batalhas: upgrade station. Modo speedrun disponível.",
        "tags": ["boss-rush", "pve", "coop", "challenge", "speedrun"],
        "max_players": 4, "game_mode": "boss_rush", "team_size": [4],
        "bosses": [
            {"name": "Golem de Pedra", "health": 5000, "abilities": ["rock_smash", "ground_pound"]},
            {"name": "Dragão de Gelo", "health": 8000, "abilities": ["ice_breath", "freeze_aura"]},
            {"name": "Cavaleiro Sombrio", "health": 10000, "abilities": ["teleport_slash", "dark_blast"]},
            {"name": "Aranha Rainha", "health": 12000, "abilities": ["web_trap", "poison_spit", "spawn_minions"]},
            {"name": "Titã Final", "health": 20000, "abilities": ["meteor_shower", "shockwave", "laser_beam"]},
        ],
        "lives_pool": 3, "time_between_bosses_sec": 30,
    },
    {
        "template": "escort-mission",
        "display_name": "Escort Mission — Comboio Protegido",
        "description": "4 jogadores protegem um veículo que atravessa o mapa. Hordas de inimigos atacam em pontos específicos. Conserte o veículo entre as ondas.",
        "tags": ["escort", "pve", "coop", "defense", "vehicle"],
        "max_players": 4, "game_mode": "escort", "team_size": [4],
        "convoy_health": 3000, "convoy_speed": "slow",
        "ambush_points": 6, "repair_kit_count": 10,
        "difficulty_scaling": True,
        "starting_health": 100, "starting_shield": 50,
        "allow_respawn": True, "respawn_delay_sec": 12,
        "path_length_tiles": 120,
    },
    {
        "template": "defense-line",
        "display_name": "Defense Line — Linha de Frente",
        "description": "8 jogadores defendem 3 pontos estratégicos em um mapa de guerra. Inimigos avançam em ondas sincronizadas. Coordenação essencial para vitória.",
        "tags": ["defense", "pve", "coop", "8-player", "tactical"],
        "max_players": 8, "game_mode": "defense_line", "team_size": [8],
        "defense_points": 3, "waves": {"total": 20, "enemy_scaling": "moderate", "type_mix": True},
        "point_health": 2000, "fallback_on_breach": True,
        "starting_materials": {"wood": 300, "stone": 200, "metal": 100},
        "harvest_rate_multiplier": 2.0, "allow_respawn": True, "respawn_delay_sec": 8,
    },
    {
        "template": "raid-mode",
        "display_name": "Raid Mode — Invasão Épica",
        "description": "6 jogadores invadem uma fortaleza inimiga. Múltiplos objetivos: destruir geradores, hackear terminais, eliminar comandantes. Chefão final no bunker.",
        "tags": ["raid", "pve", "coop", "6-player", "objective"],
        "max_players": 6, "game_mode": "raid", "team_size": [6],
        "objectives": [
            {"id": "obj_01", "name": "Destruir Geradores", "type": "destroy", "count": 4},
            {"id": "obj_02", "name": "Hackear Terminais", "type": "hack", "count": 3},
            {"id": "obj_03", "name": "Eliminar Comandantes", "type": "eliminate", "count": 2},
            {"id": "obj_04", "name": "Derrotar Chefão", "type": "boss", "count": 1},
        ],
        "starting_health": 150, "starting_shield": 50,
        "starting_materials": {"wood": 100, "stone": 50, "metal": 50},
        "lives_pool": 12,
    },
]

# ── RACING / PARKOUR MAPS (31–40) ────────────────────────────────────

racing_maps = [
    {
        "template": "circuit-race",
        "display_name": "Circuit Race — GP Radical",
        "description": "8 corredores em um circuito de 3 voltas. Boost pads, atalhos e terrenos variados. Veículos: Whiplash e ATK. 3 voltas para completar.",
        "tags": ["racing", "circuit", "pvp", "vehicle", "competitive"],
        "max_players": 8, "game_mode": "circuit_race", "team_size": [1],
        "laps": 3, "checkpoints": 12, "track_length_tiles": 150,
        "vehicles": ["whiplash", "atk"],
        "boost_pads": 8, "shortcuts": 3,
        "allow_respawn": True, "respawn_at_last_checkpoint": True,
        "elimination_mode": "position_ranking",
    },
    {
        "template": "drift-track",
        "display_name": "Drift Track — Derrapagem Extrema",
        "description": "Pista de drift com curvas fechadas. Pontuação por drift e velocidade. 6 jogadores. Modo time trial e corrida. Veículos esportivos.",
        "tags": ["racing", "drift", "pvp", "casual", "skill"],
        "max_players": 6, "game_mode": "drift_race", "team_size": [1],
        "checkpoints": 10, "track_type": "closed_circuit",
        "scoring": {"drift_points": True, "speed_bonus": True, "combo_multiplier": 1.5},
        "vehicles": ["whiplash_sport"],
        "round_time_sec": 300, "gravity": 1.0,
    },
    {
        "template": "parkour-challenge",
        "display_name": "Parkour Challenge — Salto Extremo",
        "description": "12 jogadores competem em uma pista de parkour vertical com 4 andares. Checkpoints, atalhos perigosos e plataformas móveis. Tempo limite de 8 minutos.",
        "tags": ["parkour", "racing", "pvp", "casual", "vertical"],
        "max_players": 12, "game_mode": "parkour_race", "team_size": [1],
        "track_floors": 4, "checkpoints": 16, "total_obstacles": 40,
        "difficulty_curve": "moderate", "time_limit_sec": 480,
        "allow_respawn": True, "respawn_at_checkpoint": True,
        "hazard_types": ["moving_platforms", "wall_jumps", "sliding_ramps", "speed_boosters"],
    },
    {
        "template": "obstacle-course",
        "display_name": "Obstacle Course — Prova de Fogo",
        "description": "Pista de obstáculos cronometrada. 20 desafios: escorregadores, paredes, saltos e túneis. Melhor tempo vence. Modo solo e em equipe.",
        "tags": ["obstacle-course", "racing", "pvp", "casual", "time-trial"],
        "max_players": 8, "game_mode": "obstacle_race", "team_size": [1],
        "obstacles": 20, "time_limit_sec": 600,
        "allow_respawn": True, "respawn_at_obstacle_start": True,
        "obstacle_types": ["slide", "wall_climb", "long_jump", "crawl_tunnel", "balance_beam"],
    },
    {
        "template": "ski-slalom",
        "display_name": "Ski Slalom — Velocidade na Neve",
        "description": "6 jogadores descem uma montanha coberta de neve. Desvie de árvores e obstáculos. Portões para pontuação. 2 descidas, melhor tempo vence.",
        "tags": ["racing", "ski", "winter", "casual", "time-trial"],
        "max_players": 6, "game_mode": "ski_slalom", "team_size": [1],
        "gates": 25, "runs": 2,
        "terrain": "snow_mountain", "track_length_tiles": 80,
        "gravity": 1.2, "slide_friction": 0.3,
        "allow_respawn": True, "respawn_at_last_gate": True,
    },
    {
        "template": "bmx-park",
        "display_name": "BMX Park — Manobras Radicais",
        "description": "Parque de BMX com rampas, half-pipes e rails. 8 jogadores. Competição de manobras: pontuação por trick, combo e air time. Use o Hoverboard.",
        "tags": ["bmx", "racing", "casual", "park", "tricks"],
        "max_players": 8, "game_mode": "tricks_competition", "team_size": [1],
        "park_size_tiles": 60, "ramps": 12, "half_pipes": 4, "rails": 8,
        "round_time_sec": 180, "trick_scoring": {"air_time": True, "rotation": True, "combo_multiplier": 2.0},
        "vehicle": "hoverboard", "gravity": 0.9,
    },
    {
        "template": "hoverboard-race",
        "display_name": "Hoverboard Race — Corrida Flutuante",
        "description": "8 jogadores em hoverboards por pistas aéreas com anéis e boost gates. Pista suspensa no céu com plataformas flutuantes. 2 voltas.",
        "tags": ["hoverboard", "racing", "pvp", "aerial", "casual"],
        "max_players": 8, "game_mode": "hoverboard_race", "team_size": [1],
        "laps": 2, "rings": 30, "boost_gates": 10,
        "track_type": "aerial_floating", "track_length_tiles": 120,
        "vehicle": "hoverboard", "gravity": 0.7,
        "fall_damage": False, "allow_respawn": True,
    },
    {
        "template": "gauntlet-run",
        "display_name": "Gauntlet Run — Corrida Mortal",
        "description": "Corra pela pista mais perigosa já criada. 30 salas com armadilhas letais. 10 jogadores. Apenas 3 vidas. Chegue ao final para vencer.",
        "tags": ["gauntlet", "parkour", "pvp", "hardcore", "deathrun-advanced"],
        "max_players": 10, "game_mode": "gauntlet_run", "team_size": [1],
        "rooms": 30, "lives_per_player": 3,
        "difficulty": "extreme", "time_limit_sec": 900,
        "hazard_types": ["laser_maze", "crushing_walls", "floor_spikes", "flame_chamber", "piston_gauntlet"],
        "checkpoint_interval": 5, "allow_respawn": True, "respawn_at_checkpoint": True,
    },
    {
        "template": "time-trial",
        "display_name": "Time Trial — Contra o Relógio",
        "description": "8 jogadores em corrida contra o relógio individual. 3 voltas, melhor volta conta. Fantasmas dos melhores tempos visíveis. Recordes salvos.",
        "tags": ["time-trial", "racing", "solo", "competitive", "record"],
        "max_players": 8, "game_mode": "time_trial", "team_size": [1],
        "track_length_tiles": 100, "laps": 3, "checkpoints": 15,
        "ghost_enabled": True, "leaderboard_size": 50,
        "vehicles": ["whiplash", "atk", "quadcrasher"],
        "allow_respawn": True, "respawn_at_last_checkpoint": True,
    },
    {
        "template": "water-race",
        "display_name": "Water Race — Velocidade Aquática",
        "description": "Corrida aquática com barcos. 6 jogadores. Pista com corredeiras, redemoinhos e atalhos. 2 voltas. Cuidado com as cataratas!",
        "tags": ["water", "racing", "pvp", "boat", "casual"],
        "max_players": 6, "game_mode": "water_race", "team_size": [1],
        "laps": 2, "checkpoints": 8,
        "vehicles": ["motorboat", "speedboat"],
        "track_features": ["rapids", "whirlpools", "waterfalls", "shortcuts"],
        "track_length_tiles": 90,
        "allow_respawn": True, "respawn_at_last_checkpoint": True,
        "gravity": 1.0,
    },
]

# ── SOCIAL / HUB MAPS (41–50) ────────────────────────────────────────

social_maps = [
    {
        "template": "social-hub",
        "display_name": "Social Hub — Ponto de Encontro",
        "description": "Hub social com 50 jogadores. Áreas de estar, pista de dança, campo de futebol, piscina e salas VIP. Minigames espalhados. Economia de moedas.",
        "tags": ["social", "hub", "party", "casual", "rp", "hangout"],
        "max_players": 50, "game_mode": "social_hub", "team_size": [1],
        "allow_storm": False, "starting_health": 200,
        "fall_damage": False, "friendly_fire": False,
        "zones": ["dance_floor", "pool", "soccer_field", "observation_deck", "cinema_room", "vip_lounge", "parkour_garden"],
        "currency": {"name": "Star Coins", "earn_rate": 1, "per_minute": True},
        "mini_games": ["obstacle_course", "shooting_range", "race_track"],
    },
    {
        "template": "creative-hub",
        "display_name": "Creative Hub — Ilha da Criatividade",
        "description": "Hub de Creative com 30 jogadores. 10 ilhas temáticas com portais. Salas de prática de construção, edição e aim. Mapas da comunidade destacados.",
        "tags": ["creative", "hub", "practice", "community", "building"],
        "max_players": 30, "game_mode": "creative_hub", "team_size": [1],
        "practice_rooms": ["build_practice", "edit_course", "aim_trainer", "retake_practice", "piece_control"],
        "portal_count": 10,
        "starting_materials": {"wood": 999, "stone": 999, "metal": 999},
        "allow_flight": True, "fall_damage": False,
    },
    {
        "template": "party-games",
        "display_name": "Party Games — Festa de Minigames",
        "description": "16 jogadores em 8 minigames aleatórios. Cada rodada um jogo diferente: corrida de obstáculos, deathmatch, construção, puzzles. Pontuação cumulativa.",
        "tags": ["party", "minigames", "casual", "variety", "8v8"],
        "max_players": 16, "game_mode": "party_games", "team_size": [1],
        "minigames": 8,
        "game_pool": ["floor_is_lava", "spleef", "tag", "sumo", "musical_chairs", "build_off", "prop_elimination", "race"],
        "round_time_sec": 120, "rounds_to_win": 5,
        "scoring": {"win_bonus": 10, "second_place": 5, "participation": 1},
    },
    {
        "template": "movie-night",
        "display_name": "Movie Night — Cinema na Ilha",
        "description": "24 jogadores assistem filmes e vídeos em tela gigante. Sala de cinema temática com poltronas, pipoca e efeitos de iluminação. Sessões agendadas.",
        "tags": ["social", "cinema", "hangout", "casual"],
        "max_players": 24, "game_mode": "cinema", "team_size": [1],
        "screens": {"main": {"size": "80x45", "type": "projector"}, "lounge": {"size": "40x22", "type": "tv"}},
        "features": ["reclining_seats", "dimming_lights", "surround_sound", "snack_bar"],
        "fall_damage": False, "starting_health": 200,
    },
    {
        "template": "music-festival",
        "display_name": "Music Festival — Festival Eletrônico",
        "description": "30 jogadores em um festival de música com palco principal, pista de dança, luzes sincronizadas e área VIP. DJ sets ao vivo com triggers.",
        "tags": ["social", "music", "party", "festival", "hangout"],
        "max_players": 30, "game_mode": "music_festival", "team_size": [1],
        "stages": 2, "dance_floors": 3, "vip_areas": 2,
        "lighting_effects": ["laser_show", "strobe", "color_cycle", "fireworks"],
        "audio_triggers": 20, "emote_zones": True,
        "starting_health": 200, "fall_damage": False,
    },
    {
        "template": "art-gallery",
        "display_name": "Art Gallery — Galeria de Arte",
        "description": "20 jogadores. Exposição de arte com pinturas, esculturas e instalações interativas. Votações para melhor obra. Sala de criação com recursos ilimitados.",
        "tags": ["social", "art", "creative", "exhibition", "casual"],
        "max_players": 20, "game_mode": "art_gallery", "team_size": [1],
        "exhibition_halls": 5, "featured_artworks": 25,
        "voting_system": True, "creation_studio": True,
        "allow_flight": True, "fall_damage": False,
    },
    {
        "template": "trading-plaza",
        "display_name": "Trading Plaza — Praça de Troca",
        "description": "40 jogadores em uma praça de comércio. Trocas de itens cosméticos, salas de leilão e feira livre. Sistema de reputação entre jogadores.",
        "tags": ["social", "trading", "market", "hub", "economy"],
        "max_players": 40, "game_mode": "trading_plaza", "team_size": [1],
        "market_stalls": 20, "auction_house": True,
        "features": ["trade_requests", "reputation_system", "wishlist", "showcase_pedestals"],
        "starting_health": 200, "fall_damage": False,
    },
    {
        "template": "parkour-hub",
        "display_name": "Parkour Hub — Central de Parkour",
        "description": "Hub de parkour com 16 jogadores. 8 ilhas de parkour de dificuldade progressiva. Leaderboards, conquistas e salas de prática livre.",
        "tags": ["parkour", "hub", "casual", "practice", "community"],
        "max_players": 16, "game_mode": "parkour_hub", "team_size": [1],
        "islands": [
            {"id": "easy_01", "difficulty": "easy", "time_estimate_sec": 60},
            {"id": "easy_02", "difficulty": "easy", "time_estimate_sec": 90},
            {"id": "medium_01", "difficulty": "medium", "time_estimate_sec": 120},
            {"id": "medium_02", "difficulty": "medium", "time_estimate_sec": 150},
            {"id": "hard_01", "difficulty": "hard", "time_estimate_sec": 180},
            {"id": "hard_02", "difficulty": "hard", "time_estimate_sec": 240},
            {"id": "expert_01", "difficulty": "expert", "time_estimate_sec": 300},
            {"id": "expert_02", "difficulty": "expert", "time_estimate_sec": 360},
        ],
        "fall_damage": False, "allow_flight": False,
        "leaderboard_size": 100,
    },
    {
        "template": "lounge",
        "display_name": "Lounge — Relaxamento e Social",
        "description": "Lounge sofisticado para 12 jogadores. Áreas temáticas: fogueira, jardim zen, sala de jogos de tabuleiro, cafeteria e observatório estelar.",
        "tags": ["social", "lounge", "hangout", "casual", "relax"],
        "max_players": 12, "game_mode": "lounge", "team_size": [1],
        "areas": ["campfire_hangout", "zen_garden", "board_game_room", "cafe", "star_observatory"],
        "board_games": 6, "conversation_zones": 5,
        "starting_health": 200, "fall_damage": False,
        "time_of_day_setting": "sunset",
    },
    {
        "template": "gameshow-studio",
        "display_name": "GameShow Studio — Programa de Auditório",
        "description": "8 competidores + plateia. 4 rodadas de jogos estilo programa de TV: quiz, provas físicas, torre de copos e desafio final. Plateia interativa.",
        "tags": ["gameshow", "party", "social", "quiz", "competitive"],
        "max_players": 24, "game_mode": "gameshow", "team_size": [1],
        "contestants": 8, "audience": 16,
        "rounds": [
            {"name": "Quiz Rápido", "type": "trivia", "questions": 10, "time_per_question_sec": 15},
            {"name": "Prova Física", "type": "obstacle", "duration_sec": 60},
            {"name": "Torre de Copos", "type": "build", "duration_sec": 45},
            {"name": "Desafio Final", "type": "final_challenge", "duration_sec": 90},
        ],
        "audience_voting": True, "prize_pool": True,
    },
]

# ── WRITE ALL MAPS ───────────────────────────────────────────────────

map_batches = [
    (11, pvp_maps, "PvP"),
    (21, pve_maps, "PvE/Co-op"),
    (31, racing_maps, "Racing/Parkour"),
    (41, social_maps, "Social/Hub"),
]

total = 0
for start_n, maps, category in map_batches:
    print(f"\n{'='*50}")
    print(f"  {category} maps ({start_n}–{start_n+len(maps)-1})")
    print(f"{'='*50}")
    for i, m in enumerate(maps):
        n = start_n + i
        theme = m["template"]
        filename = f"{n:02d}_{theme}.json"
        filepath = os.path.join(OUT, filename)

        # Build full JSON with the standard Fortnite creative schema
        data = {
            "template": m["template"],
            "version": "1.0.0",
            "uefn_version": ">=31.0",
            "display_name": m["display_name"],
            "description": m["description"],
            "tags": m["tags"],

            "island": {
                "type": "flat_grid_128x128" if m["max_players"] > 12 else "flat_grid_64x64",
                "template_id": f"island_{m['template']}",
                "starting_weather": "clear",
                "time_of_day": "day",
                "allow_storm": m.get("storm_phases", 0) > 0,
            },
        }

        if m.get("storm_phases"):
            data["island"]["storm_phases"] = m["storm_phases"]
            data["island"]["storm_wait_time_sec"] = m.get("storm_wait_time_sec", 90)
            data["island"]["storm_shrink_time_sec"] = m.get("storm_shrink_time_sec", 120)

        game_settings = {
            "max_players": m["max_players"],
            "min_players": 1 if m["max_players"] <= 4 else 2,
            "game_mode": m["game_mode"],
            "allow_respawn": m.get("allow_respawn", False),
            "fall_damage": m.get("fall_damage", True),
            "friendly_fire": m.get("friendly_fire", False if "pve" in m["template"] or "social" in m["template"] else True),
            "elimination_mode": m.get("elimination_mode", "last_standing"),
            "starting_health": m.get("starting_health", 100),
        }

        if "team_size" in m:
            game_settings["team_size"] = m["team_size"]

        if "starting_shield" in m:
            game_settings["starting_shield"] = m["starting_shield"]
            game_settings["max_shield"] = m.get("max_shield", 100)

        if "starting_materials" in m:
            game_settings["starting_materials"] = m["starting_materials"]
            game_settings["harvest_rate_multiplier"] = m.get("harvest_rate_multiplier", 1.0)

        if "gravity" in m:
            game_settings["gravity"] = m["gravity"]

        if "round_time_sec" in m:
            game_settings["round_time_sec"] = m["round_time_sec"]

        if "rounds_to_win" in m:
            game_settings["rounds_to_win"] = m["rounds_to_win"]

        if "respawn_delay_sec" in m:
            game_settings["respawn_delay_sec"] = m["respawn_delay_sec"]

        if "lives_pool" in m:
            game_settings["lives_pool"] = m["lives_pool"]

        if "lives_per_player" in m:
            game_settings["lives_per_player"] = m["lives_per_player"]

        if "elimination_target" in m:
            game_settings["elimination_target"] = m["elimination_target"]

        data["game_settings"] = game_settings

        # Category-specific sections
        if category == "PvP" and "pois" in m:
            data["pois"] = m["pois"]

        if category == "PvP" and "weapons_only" in m:
            data["weapon_restrictions"] = {"allowed": m["weapons_only"], "infinite_ammo": m.get("infinite_ammo", False)}

        if category == "PvP" and "power_ups" in m:
            data["power_ups"] = m["power_ups"]

        if category == "PvP" and "loot_tier_weights" in m:
            data["loot_pool"] = {"tier_weights": m["loot_tier_weights"]}

        if category == "PvP" and "supply_drops" in m:
            if "loot_pool" not in data:
                data["loot_pool"] = {}
            data["loot_pool"]["supply_drops"] = m["supply_drops"]

        if category == "PvP" and "hill_locations" in m:
            data["hill_settings"] = {
                "hill_capture_time_sec": m["hill_capture_time_sec"],
                "hill_points_per_sec": m["hill_points_per_sec"],
                "hill_locations": m["hill_locations"],
                "hill_rotation_interval_sec": m["hill_rotation_interval_sec"],
            }

        if category == "PvP" and "flag_capture_time_sec" in m:
            data["ctf_settings"] = {
                "flag_capture_time_sec": m["flag_capture_time_sec"],
                "flag_drop_on_kill": m["flag_drop_on_kill"],
            }

        if category == "PvP" and "starting_infected" in m:
            data["infected_settings"] = {
                "starting_infected": m["starting_infected"],
                "infected_weapon": m["infected_weapon"],
                "human_weapons": m["human_weapons"],
            }

        if category == "PvP" and "grid_size" in m:
            data["grid_settings"] = {
                "grid_size": m["grid_size"],
                "paint_speed": m["paint_speed"],
            }

        if category == "PvP" and "payload_speed" in m:
            data["payload_settings"] = {
                "payload_speed": m["payload_speed"],
                "payload_checkpoints": m["payload_checkpoints"],
                "overtime_enabled": m["overtime_enabled"],
                "track_length_tiles": m["track_length_tiles"],
            }

        if category == "PvP" and "arena_size_tiles" in m:
            data["arena_settings"] = {
                "arena_size_tiles": m["arena_size_tiles"],
                "starting_materials": m["starting_materials"],
                "harvest_rate_multiplier": m["harvest_rate_multiplier"],
            }

        if category == "PvE/Co-op":
            if "waves" in m:
                data["wave_settings"] = m["waves"]
            if "currency_system" in m:
                data["economy"] = m["currency_system"]
                data["shop"] = {"items": m["shop_items"]}
            if "generator_health" in m:
                data["generator"] = {"health": m["generator_health"], "shield": m.get("generator_shield", 0)}
            if "monsters" in m:
                data["monsters"] = m["monsters"]
            if "tower_types" in m:
                data["tower_defense"] = {
                    "crystal_health": m["crystal_health"],
                    "tower_types": m["tower_types"],
                    "starting_gold": m["starting_gold"],
                    "gold_per_kill": m["gold_per_kill"],
                    "gold_per_wave": m["gold_per_wave"],
                }
            if "zombie_types" in m:
                data["zombie_settings"] = {
                    "zombie_types": m["zombie_types"],
                    "difficulty_levels": m["difficulty_levels"],
                    "objectives": m["objectives"],
                }
                if "loot_pool" in m:
                    data["loot_pool"] = m["loot_pool"]
            if "dungeon_floors" in m:
                data["dungeon_settings"] = {
                    "dungeon_floors": m["dungeon_floors"],
                    "rooms_per_floor": m["rooms_per_floor"],
                    "room_types": m["room_types"],
                    "lives_pool": m["lives_pool"],
                    "perma_death": m["perma_death"],
                    "upgrade_stations": m["upgrade_stations"],
                }
            if "bosses" in m:
                data["boss_settings"] = {
                    "bosses": m["bosses"],
                    "lives_pool": m["lives_pool"],
                    "time_between_bosses_sec": m["time_between_bosses_sec"],
                }
            if "convoy_health" in m:
                data["escort_settings"] = {
                    "convoy_health": m["convoy_health"],
                    "convoy_speed": m["convoy_speed"],
                    "ambush_points": m["ambush_points"],
                    "repair_kit_count": m["repair_kit_count"],
                    "difficulty_scaling": m["difficulty_scaling"],
                    "path_length_tiles": m["path_length_tiles"],
                }
            if "defense_points" in m:
                data["defense_settings"] = {
                    "defense_points": m["defense_points"],
                    "point_health": m["point_health"],
                    "fallback_on_breach": m["fallback_on_breach"],
                }
            if "objectives" in m and "generator_health" not in m:
                data["raid_settings"] = {
                    "objectives": m["objectives"],
                    "lives_pool": m["lives_pool"],
                }
            if "pois" in m:
                data["pois"] = m["pois"]

        if category == "Racing/Parkour":
            data["track_settings"] = {
                "track_length_tiles": m.get("track_length_tiles", 100),
                "checkpoints": m.get("checkpoints", 10),
                "laps": m.get("laps", 1),
                "allow_respawn": m.get("allow_respawn", True),
                "respawn_at_last_checkpoint": m.get("respawn_at_last_checkpoint", True),
            }
            if "vehicles" in m:
                data["track_settings"]["vehicles"] = m["vehicles"]
            if "boost_pads" in m:
                data["track_settings"]["boost_pads"] = m["boost_pads"]
            if "shortcuts" in m:
                data["track_settings"]["shortcuts"] = m["shortcuts"]
            if "scoring" in m:
                data["track_settings"]["scoring"] = m["scoring"]
            if "track_type" in m:
                data["track_settings"]["track_type"] = m["track_type"]
            if "track_floors" in m:
                data["track_settings"]["track_floors"] = m["track_floors"]
                data["track_settings"]["total_obstacles"] = m["total_obstacles"]
            if "obstacles" in m:
                data["track_settings"]["obstacles"] = m["obstacles"]
                data["track_settings"]["obstacle_types"] = m["obstacle_types"]
            if "gates" in m:
                data["track_settings"]["gates"] = m["gates"]
                data["track_settings"]["runs"] = m["runs"]
                data["track_settings"]["terrain"] = m["terrain"]
            if "park_size_tiles" in m:
                data["track_settings"]["park_size_tiles"] = m["park_size_tiles"]
                data["track_settings"]["ramps"] = m["ramps"]
                data["track_settings"]["half_pipes"] = m["half_pipes"]
                data["track_settings"]["rails"] = m["rails"]
            if "rings" in m:
                data["track_settings"]["rings"] = m["rings"]
                data["track_settings"]["boost_gates"] = m["boost_gates"]
            if "rooms" in m:
                data["track_settings"]["rooms"] = m["rooms"]
                data["track_settings"]["lives_per_player"] = m["lives_per_player"]
                data["track_settings"]["difficulty"] = m["difficulty"]
                data["track_settings"]["hazard_types"] = m["hazard_types"]
                data["track_settings"]["checkpoint_interval"] = m["checkpoint_interval"]
            if "ghost_enabled" in m:
                data["track_settings"]["ghost_enabled"] = m["ghost_enabled"]
                data["track_settings"]["leaderboard_size"] = m["leaderboard_size"]
            if "track_features" in m:
                data["track_settings"]["track_features"] = m["track_features"]

        if category == "Social/Hub":
            data["social_settings"] = {
                "starting_health": m.get("starting_health", 200),
                "allow_storm": m.get("allow_storm", False),
                "fall_damage": m.get("fall_damage", False),
                "friendly_fire": m.get("friendly_fire", False),
            }
            if "zones" in m:
                data["social_settings"]["zones"] = m["zones"]
            if "currency" in m:
                data["social_settings"]["currency"] = m["currency"]
            if "mini_games" in m:
                data["social_settings"]["mini_games"] = m["mini_games"]
            if "practice_rooms" in m:
                data["social_settings"]["practice_rooms"] = m["practice_rooms"]
            if "portal_count" in m:
                data["social_settings"]["portal_count"] = m["portal_count"]
                data["social_settings"]["allow_flight"] = m.get("allow_flight", False)
            if "minigames" in m:
                data["social_settings"]["minigames"] = m["minigames"]
                data["social_settings"]["game_pool"] = m["game_pool"]
                data["social_settings"]["scoring"] = m["scoring"]
            if "screens" in m:
                data["social_settings"]["screens"] = m["screens"]
                data["social_settings"]["features"] = m["features"]
            if "stages" in m:
                data["social_settings"]["stages"] = m["stages"]
                data["social_settings"]["dance_floors"] = m["dance_floors"]
                data["social_settings"]["vip_areas"] = m["vip_areas"]
                data["social_settings"]["lighting_effects"] = m["lighting_effects"]
                data["social_settings"]["audio_triggers"] = m["audio_triggers"]
                data["social_settings"]["emote_zones"] = m["emote_zones"]
            if "exhibition_halls" in m:
                data["social_settings"]["exhibition_halls"] = m["exhibition_halls"]
                data["social_settings"]["featured_artworks"] = m["featured_artworks"]
                data["social_settings"]["voting_system"] = m["voting_system"]
                data["social_settings"]["creation_studio"] = m["creation_studio"]
            if "market_stalls" in m:
                data["social_settings"]["market_stalls"] = m["market_stalls"]
                data["social_settings"]["auction_house"] = m["auction_house"]
                data["social_settings"]["features"] = m["features"]
            if "islands" in m:
                data["social_settings"]["islands"] = m["islands"]
                data["social_settings"]["leaderboard_size"] = m["leaderboard_size"]
            if "areas" in m:
                data["social_settings"]["areas"] = m["areas"]
                data["social_settings"]["board_games"] = m["board_games"]
                data["social_settings"]["conversation_zones"] = m["conversation_zones"]
                if "time_of_day_setting" in m:
                    data["island"]["time_of_day"] = m["time_of_day_setting"]
            if "rounds" in m:
                data["social_settings"]["rounds"] = m["rounds"]
                data["social_settings"]["contestants"] = m["contestants"]
                data["social_settings"]["audience"] = m["audience"]
                data["social_settings"]["audience_voting"] = m["audience_voting"]
                data["social_settings"]["prize_pool"] = m["prize_pool"]

        # Devices (common to all)
        devices = [{"type": "class_selector", "enabled": True}]
        if m.get("allow_respawn"):
            devices.append({"type": "respawn_manager", "respawn_delay_sec": m.get("respawn_delay_sec", 5)})
        if m["game_mode"] in ("battle_royale", "team_rumble", "free_for_all", "capture_the_flag"):
            devices.append({"type": "item_spawner", "positions": "auto-distributed", "count": 100})
        devices.append({"type": "scoreboard", "visible": True})
        data["devices"] = devices

        # Version history
        data["version_history"] = [
            {"version": "1.0.0", "date": "2025-07-13", "changes": [f"Template inicial {m['display_name']}"]}
        ]

        w(filepath, data)
        total += 1

print(f"\n{'='*50}")
print(f"  TOTAL: {total} maps generated in {OUT}")
print(f"{'='*50}")
