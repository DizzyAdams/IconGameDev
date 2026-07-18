// ============================================================
// Economy RPG - Main Script
// Sistema de Economia (Diamonds), Quests e Lojas NPC
// Minecraft Bedrock Script API
// ============================================================

import { world, system, ItemStack, Player, Entity } from "@minecraft/server";
import { ActionFormData, ModalFormData, MessageFormData } from "@minecraft/server-ui";

// ============================================================
// CONFIGURACAO
// ============================================================
const CONFIG = {
    CURRENCY: "minecraft:diamond",
    CURRENCY_NAME: "§bDiamante§r",
    CURRENCY_ICON: "§b💎",
    BANK_BLOCK: "minecraft:barrel",
    QUEST_MASTER_TAG: "quest_master",
    SHOP_KEEPER_TAG: "shop_keeper",
    QUEST_COMPLETE_PREFIX: "quest_complete_",
};

// ============================================================
// DADOS DOS MAPAS
// ============================================================
const MAP_DATA = {
    // Será preenchido pelo gerador de mapas
};

// ============================================================
// SISTEMA DE ECONOMIA
// ============================================================
class EconomySystem {
    constructor() {
        this.scoreboard = world.scoreboard;
        this._initScoreboard();
    }

    _initScoreboard() {
        const objectives = this.scoreboard.getObjectives();
        if (!objectives.find(o => o.id === "money")) {
            this.scoreboard.addObjective("money", "§b💎 Diamantes");
        }
    }

    getBalance(player) {
        try {
            return this.scoreboard.getObjective("money").getScore(player);
        } catch {
            this.setBalance(player, 0);
            return 0;
        }
    }

    setBalance(player, amount) {
        const obj = this.scoreboard.getObjective("money");
        obj.setScore(player, Math.max(0, amount));
    }

    addBalance(player, amount) {
        const current = this.getBalance(player);
        this.setBalance(player, current + amount);
        player.sendMessage(`§a+${amount} ${CONFIG.CURRENCY_NAME} §7(Saldo: §b${current + amount}§7)`);
    }

    removeBalance(player, amount) {
        const current = this.getBalance(player);
        if (current >= amount) {
            this.setBalance(player, current - amount);
            player.sendMessage(`§c-${amount} ${CONFIG.CURRENCY_NAME} §7(Saldo: §b${current - amount}§7)`);
            return true;
        }
        player.sendMessage(`§c❌ Saldo insuficiente! Necessário: ${amount} ${CONFIG.CURRENCY_NAME}`);
        return false;
    }

    depositDiamonds(player) {
        const inventory = player.getComponent("inventory").container;
        let total = 0;
        for (let i = 0; i < inventory.size; i++) {
            const item = inventory.getItem(i);
            if (item && item.typeId === CONFIG.CURRENCY) {
                total += item.amount;
                inventory.setItem(i, undefined);
            }
        }
        if (total > 0) {
            this.addBalance(player, total);
            player.sendMessage(`§a💰 Depositou ${total} ${CONFIG.CURRENCY_NAME} no banco!`);
        } else {
            player.sendMessage(`§c❌ Você não tem diamantes no inventário!`);
        }
    }

    withdrawDiamonds(player, amount) {
        if (this.removeBalance(player, amount)) {
            const inventory = player.getComponent("inventory").container;
            const maxStack = 64;
            let remaining = amount;
            while (remaining > 0) {
                const stackSize = Math.min(remaining, maxStack);
                const item = new ItemStack(CONFIG.CURRENCY, stackSize);
                const added = inventory.addItem(item);
                if (added) {
                    const leftover = remaining - (stackSize - (added.amount || 0));
                    this.addBalance(player, leftover);
                    player.sendMessage(`§c❌ Inventário cheio!`);
                    return;
                }
                remaining -= stackSize;
            }
            player.sendMessage(`§a💰 Sacou ${amount} ${CONFIG.CURRENCY_NAME}!`);
        }
    }
}

// ============================================================
// SISTEMA DE QUESTS
// ============================================================
class QuestSystem {
    constructor(economy) {
        this.economy = economy;
        this.quests = this._loadQuests();
        this._initQuestScoreboard();
    }

    _initQuestScoreboard() {
        const objectives = world.scoreboard.getObjectives();
        if (!objectives.find(o => o.id === "quest_points")) {
            world.scoreboard.addObjective("quest_points", "§a⭐ Pontos de Quest");
        }
        if (!objectives.find(o => o.id === "quest_progress")) {
            world.scoreboard.addObjective("quest_progress", "§e📜 Progresso");
        }
    }

    _loadQuests() {
        return [
            {
                id: "q_welcome",
                name: "§6Bem-vindo ao Reino",
                description: "§7Fale com o Rei para receber sua primeira missão!",
                type: "talk",
                target: "king",
                requirement: 1,
                reward_money: 50,
                reward_xp: 100,
                reward_item: { id: "minecraft:iron_sword", amount: 1, name: "§bEspada do Iniciante" }
            },
            {
                id: "q_miner",
                name: "§6O Trabalhador Minas",
                description: "§7Mine 32 carvão para aquecer a forja do ferreiro!",
                type: "collect",
                target: "minecraft:coal",
                requirement: 32,
                reward_money: 100,
                reward_xp: 200
            },
            {
                id: "q_iron",
                name: "§6Ferro para o Reino",
                description: "§7Colete 16 lingotes de ferro para os guardas!",
                type: "collect",
                target: "minecraft:iron_ingot",
                requirement: 16,
                reward_money: 150,
                reward_xp: 300
            },
            {
                id: "q_gold",
                name: "§6Presente Real",
                description: "§7Entregue 8 lingotes de ouro ao tesoureiro real!",
                type: "collect",
                target: "minecraft:gold_ingot",
                requirement: 8,
                reward_money: 250,
                reward_xp: 400
            },
            {
                id: "q_monster",
                name: "§6Defensor do Reino",
                description: "§7Derrote 10 monstros que ameaçam a vila!",
                type: "kill",
                target: "any",
                requirement: 10,
                reward_money: 300,
                reward_xp: 500,
                reward_item: { id: "minecraft:diamond_sword", amount: 1, name: "§bEspada do Defensor" }
            },
            {
                id: "q_builder",
                name: "§6Construtor Real",
                description: "§7Colete 64 pedras para reconstruir a muralha!",
                type: "collect",
                target: "minecraft:stone",
                requirement: 64,
                reward_money: 200,
                reward_xp: 250
            },
            {
                id: "q_farmer",
                name: "§6Feitor do Campo",
                description: "§7Plante e colha 32 trigos para alimentar o povo!",
                type: "collect",
                target: "minecraft:wheat",
                requirement: 32,
                reward_money: 120,
                reward_xp: 180
            },
            {
                id: "q_ender",
                name: "§6Olho do Guardião",
                description: "§7Derrote 5 Endermans e colete suas pérolas!",
                type: "collect",
                target: "minecraft:ender_pearl",
                requirement: 5,
                reward_money: 500,
                reward_xp: 800,
                reward_item: { id: "minecraft:elytra", amount: 1, name: "§dAsas do Herói" }
            },
            {
                id: "q_nether",
                name: "§6Fogo do Nether",
                description: "§7Colete 16 Blaze Rods do Nether!",
                type: "collect",
                target: "minecraft:blaze_rod",
                requirement: 16,
                reward_money: 400,
                reward_xp: 600
            },
            {
                id: "q_enchant",
                name: "§6Mestre Encantador",
                description: "§7Gaste 30 níveis de encantamento!",
                type: "enchant",
                target: "xp_levels",
                requirement: 30,
                reward_money: 350,
                reward_xp: 0
            }
        ];
    }

    getActiveQuest(player) {
        const tags = player.getTags();
        for (const quest of this.quests) {
            if (tags.includes(`quest_${quest.id}`) && !tags.includes(`${CONFIG.QUEST_COMPLETE_PREFIX}${quest.id}`)) {
                return quest;
            }
        }
        return null;
    }

    getCompletedQuests(player) {
        const tags = player.getTags();
        return this.quests.filter(q => tags.includes(`${CONFIG.QUEST_COMPLETE_PREFIX}${q.id}`));
    }

    getAvailableQuests(player) {
        const tags = player.getTags();
        const completed = this.getCompletedQuests(player);
        return this.quests.filter(q => 
            !tags.includes(`quest_${q.id}`) && 
            !completed.find(c => c.id === q.id)
        );
    }

    startQuest(player, questId) {
        const quest = this.quests.find(q => q.id === questId);
        if (!quest) {
            player.sendMessage(`§c❌ Quest não encontrada!`);
            return;
        }
        
        player.addTag(`quest_${questId}`);
        player.addTag(`quest_progress_${questId}_0`);
        
        const obj = world.scoreboard.getObjective("quest_progress");
        obj.setScore(player, 0);
        
        player.sendMessage(`§a📜 Nova Quest: ${quest.name}`);
        player.sendMessage(`§7${quest.description}`);
        player.sendMessage(`§e🏆 Recompensa: §b${quest.reward_money} ${CONFIG.CURRENCY_NAME}`);
        this._showQuestLog(player);
    }

    updateProgress(player, questId, progress) {
        const quest = this.quests.find(q => q.id === questId);
        if (!quest) return;
        
        const tags = player.getTags();
        if (tags.includes(`${CONFIG.QUEST_COMPLETE_PREFIX}${questId}`)) return;
        
        const obj = world.scoreboard.getObjective("quest_progress");
        const current = Math.min(progress, quest.requirement);
        obj.setScore(player, current);
        
        if (current >= quest.requirement) {
            this._completeQuest(player, quest);
        } else {
            player.sendMessage(`§e📜 ${quest.name}: §7${current}/${quest.requirement}`);
        }
    }

    _completeQuest(player, quest) {
        player.addTag(`${CONFIG.QUEST_COMPLETE_PREFIX}${quest.id}`);
        
        // Remove old progress tags
        for (const tag of player.getTags()) {
            if (tag.startsWith(`quest_progress_${quest.id}`)) {
                player.removeTag(tag);
            }
        }
        
        // Reward money
        this.economy.addBalance(player, quest.reward_money);
        
        // Reward XP
        if (quest.reward_xp > 0) {
            player.addExperience(quest.reward_xp);
        }
        
        // Reward item
        if (quest.reward_item) {
            const inventory = player.getComponent("inventory").container;
            const item = new ItemStack(quest.reward_item.id, quest.reward_item.amount);
            if (quest.reward_item.name) {
                item.nameTag = quest.reward_item.name;
            }
            const remaining = inventory.addItem(item);
            if (remaining) {
                player.spawnAt(item, player.location);
                player.sendMessage(`§e📦 Item dropado no chão (inventário cheio)!`);
            }
        }
        
        player.sendMessage(`§a✅ §lQUEST COMPLETA!§r`);
        player.sendMessage(`§a💰 +${quest.reward_money} ${CONFIG.CURRENCY_NAME}`);
        player.sendMessage(`§b⭐ +${quest.reward_xp} XP`);
        world.sendMessage(`§6🏆 ${player.name} completou a quest: ${quest.name}!`);
        
        this._showQuestLog(player);
    }

    _showQuestLog(player) {
        const quest = this.getActiveQuest(player);
        const completed = this.getCompletedQuests(player);
        
        player.sendMessage(`§6=== 📜 Diário de Quests ===`);
        if (quest) {
            const obj = world.scoreboard.getObjective("quest_progress");
            const progress = obj.getScore(player);
            player.sendMessage(`§eAtiva: ${quest.name} §7(${progress}/${quest.requirement})`);
        } else {
            player.sendMessage(`§7Nenhuma quest ativa. Fale com o Mestre de Quests!`);
        }
        player.sendMessage(`§aCompletadas: §7${completed.length}/${this.quests.length}`);
    }
}

// ============================================================
// SISTEMA DE LOJAS NPC
// ============================================================
class ShopSystem {
    constructor(economy) {
        this.economy = economy;
        this.shops = this._loadShops();
    }

    _loadShops() {
        return [
            {
                id: "shop_weapons",
                name: "§c⚔️ Armas do Ferreiro",
                npc_name: "§cFerreiro Brutamontes",
                items: [
                    { id: "minecraft:wooden_sword", name: "§7Espada de Madeira", price: 10, enchantable: true },
                    { id: "minecraft:stone_sword", name: "§8Espada de Pedra", price: 25, enchantable: true },
                    { id: "minecraft:iron_sword", name: "§fEspada de Ferro", price: 75, enchantable: true },
                    { id: "minecraft:diamond_sword", name: "§bEspada de Diamante", price: 300, enchantable: true },
                    { id: "minecraft:bow", name: "§6Arco Longo", price: 100, enchantable: true },
                    { id: "minecraft:arrow", name: "§fFlecha (16)", price: 10 },
                    { id: "minecraft:shield", name: "§6Escudo", price: 50 }
                ]
            },
            {
                id: "shop_armor",
                name: "§9🛡️ Armaduras do Guarda",
                npc_name: "§9Capitão da Guarda",
                items: [
                    { id: "minecraft:leather_helmet", name: "§6Capuz de Couro", price: 15 },
                    { id: "minecraft:leather_chestplate", name: "§6Túnica de Couro", price: 25 },
                    { id: "minecraft:leather_leggings", name: "§6Calças de Couro", price: 20 },
                    { id: "minecraft:leather_boots", name: "§6Botas de Couro", price: 15 },
                    { id: "minecraft:iron_helmet", name: "§fElmo de Ferro", price: 80 },
                    { id: "minecraft:iron_chestplate", name: "§fPeitoral de Ferro", price: 140 },
                    { id: "minecraft:iron_leggings", name: "§fGrevas de Ferro", price: 110 },
                    { id: "minecraft:iron_boots", name: "§fBotas de Ferro", price: 80 },
                    { id: "minecraft:diamond_helmet", name: "§bElmo de Diamante", price: 400 },
                    { id: "minecraft:diamond_chestplate", name: "§bPeitoral de Diamante", price: 600 },
                    { id: "minecraft:diamond_leggings", name: "§bGrevas de Diamante", price: 500 },
                    { id: "minecraft:diamond_boots", name: "§bBotas de Diamante", price: 400 }
                ]
            },
            {
                id: "shop_tools",
                name: "§e🔧 Ferramentas do Artesão",
                npc_name: "§eMestre Artesão",
                items: [
                    { id: "minecraft:wooden_pickaxe", name: "§7Picareta de Madeira", price: 8 },
                    { id: "minecraft:stone_pickaxe", name: "§8Picareta de Pedra", price: 20 },
                    { id: "minecraft:iron_pickaxe", name: "§fPicareta de Ferro", price: 60 },
                    { id: "minecraft:diamond_pickaxe", name: "§bPicareta de Diamante", price: 250 },
                    { id: "minecraft:iron_axe", name: "§fMachado de Ferro", price: 55 },
                    { id: "minecraft:diamond_axe", name: "§bMachado de Diamante", price: 220 },
                    { id: "minecraft:iron_shovel", name: "§fPá de Ferro", price: 30 },
                    { id: "minecraft:diamond_shovel", name: "§bPá de Diamante", price: 150 },
                    { id: "minecraft:fishing_rod", name: "§6Vara de Pescar", price: 30 },
                    { id: "minecraft:shears", name: "§6Tesoura", price: 15 }
                ]
            },
            {
                id: "shop_food",
                name: "§a🍖 Comidas e Poções",
                npc_name: "§aMestre Cuca",
                items: [
                    { id: "minecraft:bread", name: "§6Pão (8)", price: 5 },
                    { id: "minecraft:cooked_beef", name: "§6Bife Cozido (8)", price: 12 },
                    { id: "minecraft:golden_carrot", name: "§eCenoura Dourada", price: 20 },
                    { id: "minecraft:golden_apple", name: "§eMaçã Dourada", price: 40 },
                    { id: "minecraft:potion", name: "§dPoção de Cura", price: 50, potionType: "healing" },
                    { id: "minecraft:potion", name: "§bPoção de Força", price: 80, potionType: "strength" },
                    { id: "minecraft:potion", name: "§aPoção de Velocidade", price: 60, potionType: "swiftness" },
                    { id: "minecraft:potion", name: "§5Poção de Regeneração", price: 100, potionType: "regeneration" }
                ]
            },
            {
                id: "shop_blocks",
                name: "§7🧱 Materiais de Construção",
                npc_name: "§7Mestre de Obras",
                items: [
                    { id: "minecraft:stone", name: "§7Pedra (64)", price: 10 },
                    { id: "minecraft:oak_planks", name: "§6Tábuas (64)", price: 8 },
                    { id: "minecraft:glass", name: "§bVidro (32)", price: 15 },
                    { id: "minecraft:bricks", name: "§cTijolos (32)", price: 20 },
                    { id: "minecraft:stone_bricks", name: "§7Tijolos de Pedra (32)", price: 18 },
                    { id: "minecraft:torch", name: "§eTochas (16)", price: 5 },
                    { id: "minecraft:ladder", name: "§6Escadas (16)", price: 8 },
                    { id: "minecraft:chest", name: "§6Baú", price: 30 }
                ]
            },
            {
                id: "shop_enchant",
                name: "§d✨ Encantamentos Mágicos",
                npc_name: "§dMago Encantador",
                items: [
                    { id: "minecraft:enchanted_book", name: "§dLivro: Sharpness III", price: 200, enchant: "sharpness", level: 3 },
                    { id: "minecraft:enchanted_book", name: "§dLivro: Efficiency III", price: 180, enchant: "efficiency", level: 3 },
                    { id: "minecraft:enchanted_book", name: "§dLivro: Protection III", price: 200, enchant: "protection", level: 3 },
                    { id: "minecraft:enchanted_book", name: "§dLivro: Fortune II", price: 250, enchant: "fortune", level: 2 },
                    { id: "minecraft:enchanted_book", name: "§dLivro: Unbreaking III", price: 150, enchant: "unbreaking", level: 3 },
                    { id: "minecraft:experience_bottle", name: "§bFrasco de XP (5)", price: 30 },
                    { id: "minecraft:experience_bottle", name: "§bFrasco de XP (10)", price: 50 }
                ]
            },
            {
                id: "shop_farming",
                name: "§a🌾 Suprimentos de Fazenda",
                npc_name: "§aFazendeiro João",
                items: [
                    { id: "minecraft:wheat_seeds", name: "§6Sementes de Trigo (16)", price: 3 },
                    { id: "minecraft:carrot", name: "§6Cenoura (8)", price: 6 },
                    { id: "minecraft:potato", name: "§6Batata (8)", price: 6 },
                    { id: "minecraft:bone_meal", name: "§fFarinha de Osso (16)", price: 8 },
                    { id: "minecraft:water_bucket", name: "§9Balde de Água", price: 20 },
                    { id: "minecraft:hoe", name: "§fEnxada de Ferro", price: 40 }
                ]
            },
            {
                id: "shop_redstone",
                name: "§c🔴 Engenhocas Redstone",
                npc_name: "§cEngenheiro Redstone",
                items: [
                    { id: "minecraft:redstone", name: "§cRedstone (16)", price: 12 },
                    { id: "minecraft:repeater", name: "§cRepetidor", price: 15 },
                    { id: "minecraft:comparator", name: "§cComparador", price: 20 },
                    { id: "minecraft:piston", name: "§6Pistão", price: 25 },
                    { id: "minecraft:observer", name: "§8Observador", price: 18 },
                    { id: "minecraft:hopper", name: "§8Funil", price: 30 },
                    { id: "minecraft:dropper", name: "§8Distribuidor", price: 22 },
                    { id: "minecraft:dispenser", name: "§8Dispenser", price: 25 },
                    { id: "minecraft:rail", name: "§7Trilho (16)", price: 10 },
                    { id: "minecraft:powered_rail", name: "§6Trilho Elétrico (8)", price: 15 }
                ]
            },
            {
                id: "shop_decor",
                name: "§d🌸 Decoração & Luxo",
                npc_name: "§dDecorador Real",
                items: [
                    { id: "minecraft:painting", name: "§6Quadro", price: 20 },
                    { id: "minecraft:item_frame", name: "§6Moldura", price: 15 },
                    { id: "minecraft:flower_pot", name: "§6Vaso de Flor", price: 10 },
                    { id: "minecraft:bookshelf", name: "§6Estante (4)", price: 25 },
                    { id: "minecraft:enchanting_table", name: "§dMesa de Encantamentos", price: 300 },
                    { id: "minecraft:anvil", name: "§7Bigorna", price: 150 },
                    { id: "minecraft:crafting_table", name: "§6Bancada (4)", price: 5 },
                    { id: "minecraft:furnace", name: "§8Forno (4)", price: 8 }
                ]
            },
            {
                id: "shop_ores",
                name: "§e⛏️ Minérios & Gemas",
                npc_name: "§eMinerador Ancião",
                items: [
                    { id: "minecraft:coal", name: "§8Carvão (32)", price: 8 },
                    { id: "minecraft:iron_ingot", name: "§fLingote de Ferro (8)", price: 20 },
                    { id: "minecraft:gold_ingot", name: "§eLingote de Ouro (4)", price: 30 },
                    { id: "minecraft:diamond", name: "§bDiamante", price: 50 },
                    { id: "minecraft:emerald", name: "§aEsmeralda", price: 40 },
                    { id: "minecraft:lapis_lazuli", name: "§9Lápis-Lazúli (16)", price: 15 },
                    { id: "minecraft:redstone", name: "§cRedstone (16)", price: 12 },
                    { id: "minecraft:quartz", name: "§fQuartzo do Nether (8)", price: 25 }
                ]
            }
        ];
    }

    getShop(shopId) {
        return this.shops.find(s => s.id === shopId);
    }

    openShop(player, shopId) {
        const shop = this.getShop(shopId);
        if (!shop) {
            player.sendMessage(`§c❌ Loja não encontrada!`);
            return;
        }

        const form = new ActionFormData()
            .title(shop.name)
            .body(`§7Bem-vindo à loja!\n§eSeu Saldo: §b${this.economy.getBalance(player)} ${CONFIG.CURRENCY_NAME}\n§7Clique em um item para comprar.`);
        
        form.button("§c❌ Sair da Loja", "textures/ui/icon_close");
        
        for (const item of shop.items) {
            const canAfford = this.economy.getBalance(player) >= item.price;
            const status = canAfford ? "§a✅" : "§c❌";
            form.button(`${item.name}\n§7${item.price} 💎 ${status}`, "textures/ui/icon_buy");
        }
        
        form.show(player).then(response => {
            if (response.canceled) return;
            const idx = response.selection - 1;
            if (idx < 0 || idx >= shop.items.length) return;
            
            const item = shop.items[idx];
            if (this.economy.removeBalance(player, item.price)) {
                const inventory = player.getComponent("inventory").container;
                const stack = new ItemStack(item.id);
                if (item.potionType) {
                    // For potions we need special handling
                }
                const remaining = inventory.addItem(stack);
                if (remaining) {
                    player.spawnAt(stack, player.location);
                    player.sendMessage(`§e📦 Item dropado no chão (inventário cheio)!`);
                }
                player.sendMessage(`§a✅ Você comprou ${item.name}!`);
            }
        });
    }
}

// ============================================================
// SISTEMA DE NPC - INTERACAO
// ============================================================
class NPCMaster {
    constructor(economy, questSystem, shopSystem) {
        this.economy = economy;
        this.questSystem = questSystem;
        this.shopSystem = shopSystem;
    }

    openQuestMaster(player) {
        const available = this.questSystem.getAvailableQuests(player);
        const active = this.questSystem.getActiveQuest(player);
        
        const form = new ActionFormData()
            .title("§6📜 Mestre de Quests")
            .body(`§7Olá, aventureiro! Precisas de trabalho?\n\n§eQuests Ativas: §6${active ? 1 : 0}\n§eCompletadas: §6${this.questSystem.getCompletedQuests(player).length}`);
        
        form.button("§c❌ Sair", "textures/ui/icon_close");
        form.button("§e📋 Ver Quests Ativas", "textures/ui/icon_book_writable");
        
        if (available.length > 0) {
            form.button(`§a📜 Aceitar Nova Quest (§e${available.length}§a)`, "textures/ui/icon_book_writable");
        }
        
        form.show(player).then(response => {
            if (response.canceled) return;
            
            if (response.selection === 1) {
                this.showActiveQuest(player);
            } else if (response.selection === 2 && available.length > 0) {
                this.showAvailableQuests(player, available);
            }
        });
    }

    showActiveQuest(player) {
        const quest = this.questSystem.getActiveQuest(player);
        if (!quest) {
            player.sendMessage("§c❌ Nenhuma quest ativa no momento!");
            return;
        }
        
        const obj = world.scoreboard.getObjective("quest_progress");
        const progress = obj.getScore(player);
        
        const form = new MessageFormData()
            .title(`§6📜 ${quest.name}`)
            .body(`§7${quest.description}\n\n§eProgresso: §6${progress}/${quest.requirement}\n§eRecompensa: §b${quest.reward_money} 💎`)
            .button1("§c❌ Cancelar Quest")
            .button2("§a✅ Continuar");
        
        form.show(player).then(response => {
            if (response.selection === 0) {
                // Cancel quest
                player.removeTag(`quest_${quest.id}`);
                for (const tag of player.getTags()) {
                    if (tag.startsWith(`quest_progress_${quest.id}`)) {
                        player.removeTag(tag);
                    }
                }
                player.sendMessage(`§c❌ Quest "${quest.name}" cancelada!`);
            }
        });
    }

    showAvailableQuests(player, available) {
        const form = new ActionFormData()
            .title("§a📜 Quests Disponíveis")
            .body("§7Escolha uma quest para aceitar:");
        
        form.button("§c❌ Voltar", "textures/ui/icon_close");
        
        for (const quest of available) {
            form.button(`${quest.name}\n§7${quest.description}\n§e💰 ${quest.reward_money} 💎`);
        }
        
        form.show(player).then(response => {
            if (response.canceled || response.selection === 0) {
                this.openQuestMaster(player);
                return;
            }
            
            const quest = available[response.selection - 1];
            if (quest) {
                this.questSystem.startQuest(player, quest.id);
            }
        });
    }

    openBank(player) {
        const form = new ActionFormData()
            .title("§b💰 Banco Real")
            .body(`§7Bem-vindo ao Banco Real!\n\n§eSeu Saldo: §b${this.economy.getBalance(player)} ${CONFIG.CURRENCY_NAME}\n\n§7O que deseja fazer?`)
            .button("§a💵 Depositar Diamantes", "textures/ui/icon_deposit")
            .button("§e💸 Sacar Diamantes", "textures/ui/icon_withdraw")
            .button("§b📊 Ver Saldo", "textures/ui/icon_info")
            .button("§c❌ Sair", "textures/ui/icon_close");
        
        form.show(player).then(response => {
            if (response.canceled) return;
            switch (response.selection) {
                case 0:
                    this.economy.depositDiamonds(player);
                    break;
                case 1:
                    this._showWithdrawMenu(player);
                    break;
                case 2:
                    player.sendMessage(`§b💎 Seu saldo: §e${this.economy.getBalance(player)} ${CONFIG.CURRENCY_NAME}`);
                    break;
            }
        });
    }

    _showWithdrawMenu(player) {
        const form = new ModalFormData()
            .title("§e💸 Sacar Diamantes")
            .slider("§7Quantidade:", 1, 64, 1, 1);
        
        const balance = this.economy.getBalance(player);
        
        form.show(player).then(response => {
            if (response.canceled) return;
            const amount = response.formValues[0];
            if (amount > 0) {
                this.economy.withdrawDiamonds(player, amount);
            }
        });
    }

    openShop(player, shopId) {
        this.shopSystem.openShop(player, shopId);
    }

    handleNPCClick(player, npcTag) {
        if (npcTag === "banker") {
            this.openBank(player);
        } else if (npcTag === "quest_master") {
            this.openQuestMaster(player);
        } else if (npcTag.startsWith("shop_")) {
            this.openShop(player, npcTag);
        } else {
            player.sendMessage(`§7NPC: Olá, ${player.name}!`);
        }
    }
}

// ============================================================
// EVENTOS
// ============================================================
let economy, questSystem, shopSystem, npcMaster;

function initialize() {
    economy = new EconomySystem();
    questSystem = new QuestSystem(economy);
    shopSystem = new ShopSystem(economy);
    npcMaster = new NPCMaster(economy, questSystem, shopSystem);
    
    console.log("[EconomyRPG] §aSistema de Economia RPG inicializado!");
    world.sendMessage("§6⚔️ §lBem-vindo ao Economy RPG!§r");
    world.sendMessage("§7Use diamantes como moeda. Fale com NPCs para comprar, vender e fazer quests!");
}

// Player joins - give welcome message
world.afterEvents.playerSpawn.subscribe((event) => {
    const player = event.player;
    if (!event.initialSpawn) return;
    
    system.runTimeout(() => {
        player.sendMessage("§6=== ⚔️ Economy RPG ===");
        player.sendMessage("§e💰 Use diamantes como moeda!");
        player.sendMessage("§e📜 Fale com o §6Mestre de Quests§e para missões!");
        player.sendMessage("§e🏪 Compre itens nas lojas NPC!");
        player.sendMessage(`§b💎 Seu saldo inicial: ${economy.getBalance(player)}`);
    }, 20);
});

// Player interact with entity (NPC)
world.afterEvents.entityHitEntity.subscribe((event) => {
    const { damagingEntity, hitEntity } = event;
    if (!(damagingEntity instanceof Player)) return;
    
    const player = damagingEntity;
    const npc = hitEntity;
    
    if (npc.hasTag("npc")) {
        for (const tag of npc.getTags()) {
            if (tag.startsWith("quest_master") || tag.startsWith("shop_") || tag === "banker") {
                npcMaster.handleNPCClick(player, tag);
                break;
            }
        }
    }
});

// Block break tracking for quests
world.afterEvents.playerBreakBlock.subscribe((event) => {
    const player = event.player;
    const block = event.brokenBlockPermutation;
    
    const quest = questSystem.getActiveQuest(player);
    if (!quest || quest.type !== "collect") return;
    
    const tags = player.getTags();
    const progressTag = tags.find(t => t.startsWith(`quest_progress_${quest.id}`));
    if (!progressTag) return;
    
    const currentProgress = parseInt(progressTag.split('_').pop()) || 0;
    const newProgress = currentProgress + 1;
    
    // Update tag
    player.removeTag(progressTag);
    player.addTag(`quest_progress_${quest.id}_${newProgress}`);
    
    questSystem.updateProgress(player, quest.id, newProgress);
});

// Mob kill tracking for quests
world.afterEvents.entityDie.subscribe((event) => {
    const { damageSource: { damagingEntity } } = event;
    if (!(damagingEntity instanceof Player)) return;
    
    const player = damagingEntity;
    const quest = questSystem.getActiveQuest(player);
    if (!quest || quest.type !== "kill") return;
    
    const tags = player.getTags();
    const progressTag = tags.find(t => t.startsWith(`quest_progress_${quest.id}`));
    if (!progressTag) return;
    
    const currentProgress = parseInt(progressTag.split('_').pop()) || 0;
    const newProgress = currentProgress + 1;
    
    player.removeTag(progressTag);
    player.addTag(`quest_progress_${quest.id}_${newProgress}`);
    
    questSystem.updateProgress(player, quest.id, newProgress);
});

// Inventory tracking for collection quests
system.runInterval(() => {
    for (const player of world.getAllPlayers()) {
        const quest = questSystem.getActiveQuest(player);
        if (!quest || quest.type !== "collect") return;
        
        const inventory = player.getComponent("inventory").container;
        let totalCollected = 0;
        
        for (let i = 0; i < inventory.size; i++) {
            const item = inventory.getItem(i);
            if (item && item.typeId === quest.target) {
                totalCollected += item.amount;
            }
        }
        
        const tags = player.getTags();
        const progressTag = tags.find(t => t.startsWith(`quest_progress_${quest.id}`));
        const trackedProgress = progressTag ? parseInt(progressTag.split('_').pop()) || 0 : 0;
        
        if (totalCollected > trackedProgress) {
            if (progressTag) player.removeTag(progressTag);
            player.addTag(`quest_progress_${quest.id}_${totalCollected}`);
            questSystem.updateProgress(player, quest.id, totalCollected);
        }
    }
}, 40); // Check every 2 seconds

// Player chat commands
world.beforeEvents.chatSend.subscribe((event) => {
    const player = event.sender;
    const message = event.message.toLowerCase();
    
    if (message.startsWith("!saldo") || message.startsWith("!money")) {
        event.cancel = true;
        player.sendMessage(`§b💎 Seu saldo: §e${economy.getBalance(player)} ${CONFIG.CURRENCY_NAME}`);
    } else if (message.startsWith("!quest") || message.startsWith("!q")) {
        event.cancel = true;
        questSystem._showQuestLog(player);
    } else if (message.startsWith("!loja") || message.startsWith("!shop")) {
        event.cancel = true;
        const shopForm = new ActionFormData()
            .title("§6🏪 Lojas do Reino")
            .body("§7Escolha uma loja:");
        
        shopForm.button("§c❌ Sair");
        for (const shop of shopSystem.shops) {
            shopForm.button(`${shop.name}\n§7${shop.npc_name}`);
        }
        
        shopForm.show(player).then(response => {
            if (response.canceled || response.selection === 0) return;
            const shop = shopSystem.shops[response.selection - 1];
            if (shop) {
                shopSystem.openShop(player, shop.id);
            }
        });
    } else if (message.startsWith("!banco") || message.startsWith("!bank")) {
        event.cancel = true;
        npcMaster.openBank(player);
    } else if (message.startsWith("!ajuda") || message.startsWith("!help")) {
        event.cancel = true;
        player.sendMessage("§6=== Comandos do Economy RPG ===");
        player.sendMessage("§e!saldo §7- Ver seu saldo");
        player.sendMessage("§e!quest §7- Ver quests ativas");
        player.sendMessage("§e!loja §7- Abrir lojas");
        player.sendMessage("§e!banco §7- Abrir banco");
        player.sendMessage("§e!loja §7- Lista de lojas");
        player.sendMessage("§e!ajuda §7- Mostrar esta mensagem");
    }
});

// Initialize
initialize();
