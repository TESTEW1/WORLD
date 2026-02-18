import discord
from discord.ext import commands, tasks
import random
import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
import json

# ================= INTENTS =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
DB_FILE = "world_csi.db"
CANAL_BETA = "🌎・mundo-csi"
ADMIN_ID = 769951556388257812

# ================= CLASSES =================
CLASSES = {
    "Guerreiro": {
        "emoji": "⚔️",
        "hp_bonus": 30,
        "atk_bonus": 15,
        "def_bonus": 10,
        "description": "Mestre do combate corpo a corpo, resistente e poderoso."
    },
    "Mago": {
        "emoji": "🔮",
        "hp_bonus": 10,
        "atk_bonus": 25,
        "def_bonus": 5,
        "description": "Manipulador de energias arcanas, devastador mas frágil."
    },
    "Arqueiro": {
        "emoji": "🏹",
        "hp_bonus": 15,
        "atk_bonus": 20,
        "def_bonus": 8,
        "description": "Atirador preciso, ágil e letal à distância."
    },
    "Paladino": {
        "emoji": "🛡️",
        "hp_bonus": 25,
        "atk_bonus": 12,
        "def_bonus": 15,
        "description": "Guerreiro sagrado, equilibrado entre ataque e defesa."
    },
    "Assassino": {
        "emoji": "🗡️",
        "hp_bonus": 12,
        "atk_bonus": 22,
        "def_bonus": 6,
        "description": "Mestre das sombras, golpes críticos devastadores."
    },
    "Necromante": {
        "emoji": "💀",
        "hp_bonus": 8,
        "atk_bonus": 23,
        "def_bonus": 7,
        "description": "Senhor dos mortos, drena vida dos inimigos."
    },
    "Berserker": {
        "emoji": "🪓",
        "hp_bonus": 35,
        "atk_bonus": 18,
        "def_bonus": 5,
        "description": "Fúria incontrolável, quanto menor o HP mais forte."
    },
    "Druida": {
        "emoji": "🌿",
        "hp_bonus": 20,
        "atk_bonus": 14,
        "def_bonus": 12,
        "description": "Guardião da natureza, se cura ao coletar recursos."
    },
    "Monge": {
        "emoji": "👊",
        "hp_bonus": 18,
        "atk_bonus": 16,
        "def_bonus": 14,
        "description": "Mestre das artes marciais, equilibrado e versátil."
    },
    "Bardo": {
        "emoji": "🎵",
        "hp_bonus": 15,
        "atk_bonus": 10,
        "def_bonus": 10,
        "mana_bonus": 20,
        "description": "Músico encantador, bônus de XP e sorte aumentada."
    }
}

# ================= MANA POR CLASSE =================
CLASS_MANA = {
    "Guerreiro":  {"base_mana": 30,  "mana_per_level": 2},
    "Mago":       {"base_mana": 100, "mana_per_level": 8},
    "Arqueiro":   {"base_mana": 40,  "mana_per_level": 3},
    "Paladino":   {"base_mana": 60,  "mana_per_level": 4},
    "Assassino":  {"base_mana": 50,  "mana_per_level": 3},
    "Necromante": {"base_mana": 80,  "mana_per_level": 6},
    "Berserker":  {"base_mana": 20,  "mana_per_level": 1},
    "Druida":     {"base_mana": 70,  "mana_per_level": 5},
    "Monge":      {"base_mana": 55,  "mana_per_level": 4},
    "Bardo":      {"base_mana": 65,  "mana_per_level": 5},
}

# ================= HABILIDADES POR CLASSE (PvP) =================
CLASS_SKILLS = {
    "Guerreiro": [
        {"name": "🗡️ Golpe Devastador", "mana_cost": 0, "dmg_mult": 1.4, "desc": "Um golpe poderoso com toda a força!"},
        {"name": "🛡️ Ataque Protetor", "mana_cost": 10, "dmg_mult": 1.2, "def_bonus": 10, "desc": "Ataca enquanto se defende."},
        {"name": "⚔️ Fúria do Guerreiro", "mana_cost": 20, "dmg_mult": 1.8, "desc": "Desencadeia uma rajada de golpes furiosos!"},
        {"name": "🔥 Grito de Batalha", "mana_cost": 15, "dmg_mult": 1.5, "stun_chance": 0.2, "desc": "Grita aterrorizante que pode paralisar."},
    ],
    "Mago": [
        {"name": "🔥 Bola de Fogo", "mana_cost": 25, "dmg_mult": 2.0, "desc": "Uma esfera flamejante de destruição!"},
        {"name": "⚡ Relâmpago Arcano", "mana_cost": 30, "dmg_mult": 2.2, "stun_chance": 0.3, "desc": "Eletricidade arcana que pode paralisar."},
        {"name": "❄️ Toque Gelado", "mana_cost": 20, "dmg_mult": 1.6, "slow_chance": 0.4, "desc": "Congela o adversário reduzindo sua ação."},
        {"name": "🌀 Explosão do Vazio", "mana_cost": 40, "dmg_mult": 2.8, "desc": "Poder do abismo canalizado em destruição!"},
    ],
    "Arqueiro": [
        {"name": "🏹 Flecha Certeira", "mana_cost": 0, "dmg_mult": 1.5, "desc": "Uma flecha lançada com precisão mortal."},
        {"name": "💨 Chuva de Flechas", "mana_cost": 20, "dmg_mult": 1.7, "desc": "Múltiplas flechas caem como chuva!"},
        {"name": "🎯 Tiro Perfurante", "mana_cost": 15, "dmg_mult": 2.0, "ignore_def": True, "desc": "Flecha que penetra qualquer defesa."},
        {"name": "🌿 Flecha Envenenada", "mana_cost": 10, "dmg_mult": 1.3, "poison": True, "desc": "Veneno que corrói lentamente."},
    ],
    "Paladino": [
        {"name": "✨ Golpe Sagrado", "mana_cost": 15, "dmg_mult": 1.6, "desc": "Energia divina concentrada em um golpe!"},
        {"name": "🛡️ Escudo da Fé", "mana_cost": 20, "dmg_mult": 1.0, "self_heal": 30, "desc": "Cura a si mesmo enquanto defende."},
        {"name": "☀️ Julgamento Divino", "mana_cost": 35, "dmg_mult": 2.0, "desc": "O julgamento dos céus cai sobre o inimigo!"},
        {"name": "🌟 Aura de Proteção", "mana_cost": 25, "dmg_mult": 1.2, "def_bonus": 20, "desc": "Aura que reduz o dano recebido."},
    ],
    "Assassino": [
        {"name": "🗡️ Golpe Sorrateiro", "mana_cost": 0, "dmg_mult": 1.8, "crit_chance": 0.4, "desc": "Das sombras, um golpe mortal!"},
        {"name": "💨 Dança das Lâminas", "mana_cost": 20, "dmg_mult": 1.5, "desc": "Uma sequência vertiginosa de ataques."},
        {"name": "☠️ Veneno Assassino", "mana_cost": 15, "dmg_mult": 1.3, "poison": True, "desc": "Aplica veneno letal no adversário."},
        {"name": "🌑 Golpe das Sombras", "mana_cost": 30, "dmg_mult": 2.5, "crit_chance": 0.5, "desc": "Ataque das trevas com alta chance crítica!"},
    ],
    "Necromante": [
        {"name": "💀 Dreno de Vida", "mana_cost": 20, "dmg_mult": 1.5, "self_heal": 20, "desc": "Rouba HP do adversário!"},
        {"name": "🦴 Invocar Esqueleto", "mana_cost": 30, "dmg_mult": 1.7, "desc": "Um esqueleto guerreiro ataca!"},
        {"name": "🌑 Maldição Sombria", "mana_cost": 25, "dmg_mult": 1.4, "weaken": True, "desc": "Maldição que enfraquece o inimigo."},
        {"name": "☠️ Morte Instantânea", "mana_cost": 50, "dmg_mult": 3.0, "desc": "Toca o véu entre vida e morte!"},
    ],
    "Berserker": [
        {"name": "🪓 Frenesi", "mana_cost": 0, "dmg_mult": 2.0, "desc": "Ataque frenético sem controle!"},
        {"name": "💢 Ira Incontrolável", "mana_cost": 15, "dmg_mult": 2.2, "self_dmg": 10, "desc": "Sacrifica HP próprio por poder devastador."},
        {"name": "🩸 Sede de Sangue", "mana_cost": 10, "dmg_mult": 1.8, "hp_scale": True, "desc": "Quanto menos HP, mais forte o golpe!"},
        {"name": "💥 Explosão de Fúria", "mana_cost": 25, "dmg_mult": 2.8, "desc": "Toda a raiva liberada em um instante!"},
    ],
    "Druida": [
        {"name": "🌿 Golpe Natural", "mana_cost": 0, "dmg_mult": 1.3, "self_heal": 15, "desc": "A natureza cura ao atacar."},
        {"name": "🌪️ Tempestade de Folhas", "mana_cost": 20, "dmg_mult": 1.6, "desc": "Uma tempestade de espinhos e folhas!"},
        {"name": "🐺 Fúria Animal", "mana_cost": 30, "dmg_mult": 2.0, "desc": "Transforma-se em besta selvagem!"},
        {"name": "⚡ Trovão da Terra", "mana_cost": 35, "dmg_mult": 2.3, "stun_chance": 0.3, "desc": "A terra responde com trovão!"},
    ],
    "Monge": [
        {"name": "👊 Soco do Dragão", "mana_cost": 0, "dmg_mult": 1.5, "desc": "Um soco carregado de ki!"},
        {"name": "🌀 Cem Golpes", "mana_cost": 20, "dmg_mult": 1.7, "desc": "Cem golpes em menos de um segundo!"},
        {"name": "⚡ Raio de Ki", "mana_cost": 25, "dmg_mult": 2.0, "desc": "Energia vital lançada como projétil!"},
        {"name": "🧘 Golpe Transcendente", "mana_cost": 40, "dmg_mult": 2.5, "desc": "O corpo e a mente em perfeita harmonia."},
    ],
    "Bardo": [
        {"name": "🎵 Nota Dissonante", "mana_cost": 10, "dmg_mult": 1.3, "stun_chance": 0.3, "desc": "Uma nota que atordoa o adversário!"},
        {"name": "🎸 Acorde do Caos", "mana_cost": 20, "dmg_mult": 1.6, "desc": "Um acorde que confunde os sentidos."},
        {"name": "🎺 Fanfarra da Ruína", "mana_cost": 15, "dmg_mult": 1.5, "weaken": True, "desc": "Enfraquece o inimigo com música mágica."},
        {"name": "🎻 Sinfonia da Destruição", "mana_cost": 35, "dmg_mult": 2.2, "desc": "A música se torna força destrutiva pura!"},
    ],
}

# ================= RARITY DICE BONUS =================
RARITY_DICE_BONUS = {
    "Comum": 0,
    "Incomum": 0,
    "Raro": 1,
    "Épico": 1,
    "Lendário": 2,
    "Mítico": 2,
    "Divino": 3,
    "Primordial": 4,
}

# ================= RARIDADES (expandidas) =================
RARITIES = {
    "Comum": {"color": 0xAAAAAA, "emoji": "⚪"},
    "Incomum": {"color": 0x00FF00, "emoji": "🟢"},
    "Raro": {"color": 0x0000FF, "emoji": "🔵"},
    "Épico": {"color": 0x800080, "emoji": "🟣"},
    "Lendário": {"color": 0xFFD700, "emoji": "🟡"},
    "Mítico": {"color": 0xFF4400, "emoji": "🔴"},
    "Divino": {"color": 0x00FFFF, "emoji": "💎"},
    "Primordial": {"color": 0xFF00FF, "emoji": "🌈"}
}

# ================= PETS POR MUNDO =================
PETS = {
    1: [
        {"name": "Slime Bebê", "emoji": "💧", "rarity": "Comum", "bonus_hp": 10, "bonus_atk": 3},
        {"name": "Coelho Mágico", "emoji": "🐰", "rarity": "Incomum", "bonus_hp": 15, "bonus_atk": 5},
        {"name": "Fada da Floresta", "emoji": "🧚", "rarity": "Raro", "bonus_hp": 20, "bonus_atk": 8}
    ],
    10: [
        {"name": "Lobo Cinzento", "emoji": "🐺", "rarity": "Incomum", "bonus_hp": 25, "bonus_atk": 12},
        {"name": "Coruja Espectral", "emoji": "🦉", "rarity": "Raro", "bonus_hp": 30, "bonus_atk": 15},
        {"name": "Espírito da Floresta", "emoji": "👻", "rarity": "Épico", "bonus_hp": 40, "bonus_atk": 20}
    ],
    20: [
        {"name": "Escorpião Dourado", "emoji": "🦂", "rarity": "Raro", "bonus_hp": 35, "bonus_atk": 18},
        {"name": "Escaravelho Místico", "emoji": "🪲", "rarity": "Épico", "bonus_hp": 45, "bonus_atk": 23},
        {"name": "Esfinge Menor", "emoji": "🦁", "rarity": "Lendário", "bonus_hp": 60, "bonus_atk": 30}
    ],
    30: [
        {"name": "Raposa Ártica", "emoji": "🦊", "rarity": "Épico", "bonus_hp": 50, "bonus_atk": 25},
        {"name": "Dragão de Gelo Bebê", "emoji": "🐉", "rarity": "Lendário", "bonus_hp": 70, "bonus_atk": 35},
        {"name": "Fênix de Gelo", "emoji": "🦅", "rarity": "Mítico", "bonus_hp": 100, "bonus_atk": 50}
    ],
    40: [
        {"name": "Salamandra de Fogo", "emoji": "🦎", "rarity": "Épico", "bonus_hp": 55, "bonus_atk": 28},
        {"name": "Fênix Carmesim", "emoji": "🔥", "rarity": "Lendário", "bonus_hp": 80, "bonus_atk": 40},
        {"name": "Dragão de Magma", "emoji": "🐲", "rarity": "Mítico", "bonus_hp": 120, "bonus_atk": 60}
    ],
    50: [
        {"name": "Espectro Sombrio", "emoji": "👤", "rarity": "Lendário", "bonus_hp": 90, "bonus_atk": 45},
        {"name": "Elemental do Vazio", "emoji": "🌀", "rarity": "Mítico", "bonus_hp": 130, "bonus_atk": 65},
        {"name": "Entidade Cósmica", "emoji": "✨", "rarity": "Divino", "bonus_hp": 180, "bonus_atk": 90}
    ],
    60: [
        {"name": "Anjo Guardião", "emoji": "👼", "rarity": "Divino", "bonus_hp": 200, "bonus_atk": 100},
        {"name": "Querubim Guerreiro", "emoji": "😇", "rarity": "Divino", "bonus_hp": 250, "bonus_atk": 120},
        {"name": "Arcanjo Primordial", "emoji": "🕊️", "rarity": "Primordial", "bonus_hp": 400, "bonus_atk": 200}
    ]
}

# ================= POÇÕES =================
POTIONS = {
    "Poção de Vida Menor": {"rarity": "Comum", "hp_restore": 30, "emoji": "🧪"},
    "Poção de Vida": {"rarity": "Incomum", "hp_restore": 60, "emoji": "🧪"},
    "Poção de Vida Maior": {"rarity": "Raro", "hp_restore": 100, "emoji": "💊"},
    "Poção de Vida Superior": {"rarity": "Épico", "hp_restore": 150, "emoji": "💊"},
    "Elixir da Vida": {"rarity": "Lendário", "hp_restore": 250, "emoji": "⚗️"},
    "Elixir Divino": {"rarity": "Divino", "hp_restore": 500, "emoji": "✨"},
    "Poção de XP Menor": {"rarity": "Incomum", "xp_gain": 50, "emoji": "✨"},
    "Poção de XP": {"rarity": "Raro", "xp_gain": 100, "emoji": "✨"},
    "Poção de XP Maior": {"rarity": "Épico", "xp_gain": 200, "emoji": "💫"},
    "Elixir de XP": {"rarity": "Lendário", "xp_gain": 500, "emoji": "🌟"},
    "Poção de Força": {"rarity": "Raro", "temp_atk": 20, "duration": 5, "emoji": "💪"},
    "Poção de Defesa": {"rarity": "Raro", "temp_def": 15, "duration": 5, "emoji": "🛡️"},
    "Poção de Sorte": {"rarity": "Épico", "luck_bonus": 2, "duration": 3, "emoji": "🍀"},
    "Antídoto": {"rarity": "Comum", "cure_poison": True, "emoji": "💉"},
    "Poção de Ressurreição": {"rarity": "Mítico", "revive": True, "emoji": "💀"}
}

# ================= SISTEMA DE QUESTS =================
QUESTS = {
    1: [  # Campos Iniciais
        {
            "id": "campos_001",
            "name": "🐀 A Praga dos Ratos",
            "description": "Os aldeões estão desesperados. Ratos selvagens invadiram os campos e destroem as colheitas. Elimine 5 Ratos Selvagens e traga paz à região.",
            "type": "individual",
            "objective": "hunt",
            "target": "Rato Selvagem",
            "count": 5,
            "reward_xp": 150,
            "reward_coins": 30,
            "reward_item": "Poção de Vida",
            "lore": "Os aldeões sussurram sobre uma criatura maior controlando os ratos... O Rato Rei.",
            "npc": "Aldeão Theron",
            "difficulty": "Fácil"
        },
        {
            "id": "campos_002",
            "name": "🌿 Ervas do Curandeiro",
            "description": "O curandeiro da aldeia precisa de recursos para preparar remédios. Colete 8 recursos diferentes dos Campos Iniciais.",
            "type": "individual",
            "objective": "collect",
            "count": 8,
            "reward_xp": 100,
            "reward_coins": 20,
            "reward_item": "Poção de XP Menor",
            "lore": "O curandeiro menciona que as ervas desta região têm propriedades mágicas únicas desde a queda do primeiro meteoro.",
            "npc": "Curandeira Elara",
            "difficulty": "Fácil"
        },
        {
            "id": "campos_003",
            "name": "👑 A Caça ao Slime Rei",
            "description": "Uma equipe de aventureiros deve unir forças para derrotar o Slime Rei que aterroriza a região. Missão para 2-3 jogadores.",
            "type": "team",
            "min_players": 2,
            "max_players": 3,
            "objective": "boss",
            "target": "Slime Rei",
            "reward_xp": 400,
            "reward_coins": 80,
            "reward_item": "Espada de Ferro",
            "lore": "O Slime Rei absorveu a magia de um cristal antigo e agora é imune a ataques solitários. Apenas a força combinada pode pará-lo.",
            "npc": "Capitão Aldric",
            "difficulty": "Médio"
        },
        {
            "id": "campos_004",
            "name": "📚 O Diário Perdido",
            "description": "Um explorador perdeu seu diário precioso nos campos. Explore a região e encontre o artefato perdido.",
            "type": "individual",
            "objective": "explore",
            "count": 3,
            "reward_xp": 80,
            "reward_coins": 15,
            "reward_item": None,
            "lore": "O diário menciona uma rota secreta para as Montanhas Geladas... algo que nenhum mapa oficial mostra.",
            "npc": "Explorador Miko",
            "difficulty": "Fácil"
        }
    ],
    10: [  # Floresta Sombria
        {
            "id": "floresta_001",
            "name": "🕷️ O Ninho Maldito",
            "description": "Aranhas Gigantes bloqueiam a passagem principal da floresta. Elimine-as para reabrir o caminho dos mercadores.",
            "type": "individual",
            "objective": "hunt",
            "target": "Aranha Gigante",
            "count": 6,
            "reward_xp": 350,
            "reward_coins": 50,
            "reward_item": "Poção de Vida Maior",
            "lore": "As aranhas foram atraídas por um artefato élfico enterrado nas profundezas da floresta.",
            "npc": "Mercador Brynn",
            "difficulty": "Médio"
        },
        {
            "id": "floresta_002",
            "name": "🌲 O Ent Adormecido",
            "description": "Uma equipe deve despertar e pacificar o Ent Ancião antes que sua fúria destrua a floresta inteira.",
            "type": "team",
            "min_players": 2,
            "max_players": 3,
            "objective": "boss",
            "target": "Ent Ancião",
            "reward_xp": 900,
            "reward_coins": 150,
            "reward_item": "Armadura Élfica",
            "lore": "O Ent Ancião tem 3.000 anos. Ele guarda em sua memória o segredo da origem da floresta.",
            "npc": "Druida Sylvara",
            "difficulty": "Difícil"
        },
        {
            "id": "floresta_003",
            "name": "👻 Sussurros Espectrais",
            "description": "Espíritos Florestais perturbam a paz. Explore a floresta e descubra o que os inquieta.",
            "type": "individual",
            "objective": "explore",
            "count": 5,
            "reward_xp": 280,
            "reward_coins": 40,
            "reward_item": "Poção de XP",
            "lore": "Os espíritos mencionam uma 'Chave de Ébano' escondida nas raízes da árvore mais antiga.",
            "npc": "Espírito Ancião Vel",
            "difficulty": "Médio"
        }
    ],
    20: [  # Deserto das Almas
        {
            "id": "deserto_001",
            "name": "⚰️ A Maldição do Faraó",
            "description": "Múmias emergem das tumbas atacando viajantes. Três guerreiros devem adentrar a pirâmide e quebrar a maldição.",
            "type": "team",
            "min_players": 2,
            "max_players": 3,
            "objective": "boss",
            "target": "Faraó Amaldiçoado",
            "reward_xp": 1200,
            "reward_coins": 200,
            "reward_item": "Lâmina Flamejante",
            "lore": "O Faraó Kha-Mentu foi traído por seus sacerdotes e amaldiçoado para guardar seus próprios tesouros por toda a eternidade.",
            "npc": "Arqueólogo Ramses",
            "difficulty": "Difícil"
        },
        {
            "id": "deserto_002",
            "name": "🏺 Artefatos da Dinastia",
            "description": "Colete recursos únicos do deserto para reconstituir um artefato sagrado da civilização perdida.",
            "type": "individual",
            "objective": "collect",
            "count": 10,
            "reward_xp": 500,
            "reward_coins": 70,
            "reward_item": "Poção de Vida Superior",
            "lore": "Os artefatos da Dinastia de Ouro revelam que os humanos não foram os primeiros a habitar este mundo.",
            "npc": "Sábia Nefertiri",
            "difficulty": "Médio"
        },
        {
            "id": "deserto_003",
            "name": "🦂 Caçador de Escorpiões",
            "description": "Elimine Escorpiões Gigantes que envenenaram o único oásis da região.",
            "type": "individual",
            "objective": "hunt",
            "target": "Escorpião Gigante",
            "count": 8,
            "reward_xp": 600,
            "reward_coins": 90,
            "reward_item": "Antídoto",
            "lore": "O veneno dos escorpiões, se processado corretamente, pode curar qualquer doença conhecida.",
            "npc": "Nômade Hassan",
            "difficulty": "Médio"
        }
    ],
    30: [  # Montanhas Geladas
        {
            "id": "gelo_001",
            "name": "❄️ O Coração Congelado",
            "description": "O Yeti Colossal capturou três aldeões. Uma equipe deve resgatá-los e derrotar a besta.",
            "type": "team",
            "min_players": 2,
            "max_players": 3,
            "objective": "boss",
            "target": "Yeti Colossal",
            "reward_xp": 1800,
            "reward_coins": 280,
            "reward_item": "Armadura Rúnica",
            "lore": "O Yeti Colossal é na verdade um guardião criado pelos Titãs do Gelo para proteger um segredo nas profundezas da montanha.",
            "npc": "Ancião da Montanha Bjorn",
            "difficulty": "Muito Difícil"
        },
        {
            "id": "gelo_002",
            "name": "💎 Cristais da Profundidade",
            "description": "Minere cristais de gelo raros das cavernas mais profundas para o ferreiro da fortaleza.",
            "type": "individual",
            "objective": "collect",
            "count": 12,
            "reward_xp": 700,
            "reward_coins": 100,
            "reward_item": "Poção de XP Maior",
            "lore": "Os cristais de gelo desta região têm memória. Ao tocá-los, você vê fragmentos do passado.",
            "npc": "Ferreiro Helga",
            "difficulty": "Médio"
        }
    ],
    40: [  # Reino Vulcânico
        {
            "id": "vulcao_001",
            "name": "🐲 O Dragão de Magma",
            "description": "O Dragão de Magma desperta após séculos de sono. Três heróis devem uni-lo ou derrotá-lo.",
            "type": "team",
            "min_players": 3,
            "max_players": 3,
            "objective": "boss",
            "target": "Dragão de Magma",
            "reward_xp": 2500,
            "reward_coins": 400,
            "reward_item": "Excalibur",
            "lore": "O Dragão de Magma Ignarius foi o primeiro ser criado quando o mundo era apenas fogo e pedra. Ele guarda a Chama Original.",
            "npc": "Profeta Ignar",
            "difficulty": "Lendário"
        },
        {
            "id": "vulcao_002",
            "name": "🌋 A Forja Sagrada",
            "description": "Colete núcleos de fogo da lava ativa para reacender a Forja Sagrada dos anões.",
            "type": "individual",
            "objective": "collect",
            "count": 15,
            "reward_xp": 900,
            "reward_coins": 130,
            "reward_item": "Martelo do Trovão",
            "lore": "A Forja Sagrada foi usada para criar as primeiras armas dos deuses. Está apagada há 1.000 anos.",
            "npc": "Anão-Mestre Doran",
            "difficulty": "Difícil"
        }
    ],
    50: [  # Abismo Arcano
        {
            "id": "abismo_001",
            "name": "🌀 O Senhor das Sombras",
            "description": "O Senhor das Sombras ameaça consumir toda a realidade. Três campeões devem confrontá-lo no coração do abismo.",
            "type": "team",
            "min_players": 3,
            "max_players": 3,
            "objective": "boss",
            "target": "Senhor das Sombras",
            "reward_xp": 4000,
            "reward_coins": 600,
            "reward_item": "Cetro da Eternidade",
            "lore": "O Senhor das Sombras é um ser que existia antes do universo. Ele não deseja destruição — deseja retornar ao vazio primordial.",
            "npc": "Arquimago Zephyr",
            "difficulty": "Mítico"
        },
        {
            "id": "abismo_002",
            "name": "📖 Tomos Proibidos",
            "description": "Recupere tomos de conhecimento proibido espalhados pelo Abismo Arcano antes que se corrompam.",
            "type": "individual",
            "objective": "explore",
            "count": 7,
            "reward_xp": 1200,
            "reward_coins": 160,
            "reward_item": "Poção de XP Maior",
            "lore": "Os tomos foram escritos por entidades que existiram antes dos deuses. Seu conteúdo pode enlouquecer mortais despreparados.",
            "npc": "Bibliotecária Spectra",
            "difficulty": "Muito Difícil"
        }
    ],
    60: [  # Trono Celestial
        {
            "id": "celestial_001",
            "name": "👑 O Imperador Astral",
            "description": "A batalha final. Três lendas vivas devem enfrentar o Imperador Astral pelo destino de todos os mundos.",
            "type": "team",
            "min_players": 3,
            "max_players": 3,
            "objective": "boss",
            "target": "Imperador Astral",
            "reward_xp": 10000,
            "reward_coins": 1000,
            "reward_item": "Armadura do Primeiro Deus",
            "lore": "O Imperador Astral não é um inimigo — é um teste. Aqueles dignos de passar herdarão o trono do universo.",
            "npc": "Voz do Cosmos",
            "difficulty": "Primordial"
        },
        {
            "id": "celestial_002",
            "name": "🌟 Fragmentos da Criação",
            "description": "Reúna os Fragmentos Estelares espalhados pelo Trono Celestial para reconstruir o Cristal da Origem.",
            "type": "individual",
            "objective": "collect",
            "count": 20,
            "reward_xp": 3000,
            "reward_coins": 500,
            "reward_item": "Elixir Divino",
            "lore": "O Cristal da Origem foi destruído durante a Primeira Guerra Celestial. Sua reconstrução poderia criar — ou destruir — um novo universo.",
            "npc": "Guardião Estelar Auron",
            "difficulty": "Lendário"
        }
    ]
}

# ================= EMPREGOS DO REINO =================
JOBS = {
    "Ferreiro": {
        "emoji": "⚒️",
        "min_level": 5,
        "description": "Mestre das forjas. Cria e melhora equipamentos com materiais coletados.",
        "salary_coins": (8, 18),
        "salary_xp": (50, 120),
        "perks": [
            "Pode craftar armas únicas com `forjar arma`",
            "20% desconto ao comprar equipamentos na loja",
            "+2 bônus em dados ao coletar recursos de metal",
            "Pode identificar qualidade de itens com `inspecionar item`",
        ],
        "work_action": "Você martela o ferro com maestria. Faíscas voam enquanto uma lâmina toma forma.",
        "work_msgs": [
            "🔨 Você forja uma espada encomendada por um guarda. Trabalho limpo!",
            "⚒️ Um anão visita sua forja e aprova sua técnica — raro elogio!",
            "🔥 O fogo da forja revela um inchaço no aço. Você o reforja melhor ainda.",
            "⚙️ Você repara a armadura de um cavaleiro. Ele parte em silêncio, mas com respeito.",
            "⛏️ Uma lâmina perfeita sai da forja. Você a guarda — ninguém ainda merece.",
        ]
    },
    "Arcano": {
        "emoji": "🔮",
        "min_level": 5,
        "description": "Estudioso dos mistérios mágicos. Pesquisa feitiços e fenômenos sobrenaturais.",
        "salary_coins": (5, 12),
        "salary_xp": (80, 180),
        "perks": [
            "+15 de mana máxima permanente",
            "Pode usar `estudar magia` para ganhar XP extra",
            "50% de chance de identificar itens mágicos automaticamente",
            "Acesso à `biblioteca arcana` com lore exclusivo",
        ],
        "work_action": "Você mergulha em pergaminhos proibidos, decifrando runas antigas com os olhos vibrando.",
        "work_msgs": [
            "📚 Você decifra um pergaminho que ninguém leu por 300 anos. Revelação inquietante.",
            "✨ Uma fórmula mágica que você criou funciona pela primeira vez. Que satisfação!",
            "🌀 Uma anomalia arcana surge no laboratório. Você a contém por um fio.",
            "🔮 Você cataloga uma criatura mágica nunca documentada. A academia vai amar isso.",
            "💫 Seus estudos sobre o Abismo revelam uma verdade que deveria permanecer escondida.",
        ]
    },
    "Curandeiro": {
        "emoji": "💚",
        "min_level": 5,
        "description": "Guardião da vida. Cura ferimentos e doenças usando ervas e magia de cura.",
        "salary_coins": (6, 14),
        "salary_xp": (40, 100),
        "perks": [
            "Regenera +10 HP ao usar `trabalhar` além do salário",
            "Poções custam 30% menos na loja",
            "`curar` tem 25% de chance de curar completamente",
            "Pode usar `curar aliado @user` para curar outros jogadores",
        ],
        "work_action": "Suas mãos brilham com energia de cura enquanto você atende os feridos.",
        "work_msgs": [
            "💚 Você salva um mercador picado por uma aranha venenosa. Ele chora de alívio.",
            "🌿 Suas ervas curam uma criança com febre arcana. A mãe te abraça com força.",
            "⚕️ Um guerreiro chega quase morto. Você trabalha a noite toda. Ele sobrevive.",
            "🍃 Você descobre uma combinação de ervas que alivia veneno de drago. Anotado.",
            "💊 Você trata 12 aldeões com gripe mágica num só dia. Exausto, mas feliz.",
        ]
    },
    "Mercador": {
        "emoji": "💰",
        "min_level": 5,
        "description": "Comerciante astuto. Compra e vende itens obtendo lucro em cada transação.",
        "salary_coins": (15, 30),
        "salary_xp": (20, 60),
        "perks": [
            "Vende itens por 25% a mais de valor",
            "Acesso a `mercado negro` com itens raros",
            "Pode `negociar` para reduzir custo de compras",
            "+5 coins extras ao concluir qualquer quest",
        ],
        "work_action": "Você negocia com viajantes, comprando barato e vendendo caro com um sorriso encantador.",
        "work_msgs": [
            "💰 Você compra uma gema por 3 moedas e vende por 30. Que dia excelente!",
            "🤝 Um nobre paga o triplo por um item comum — ele nem sabia que era comum.",
            "📊 Sua rota comercial entre dois reinos rende 50% a mais este mês.",
            "🏪 Um rival tenta te sabotar. Você sorri e leva o cliente dele embora.",
            "💎 Você fareja um item raro num lote de bugigangas. Fortuna bem merecida.",
        ]
    },
    "Escriba": {
        "emoji": "📜",
        "min_level": 5,
        "description": "Guardião do conhecimento. Registra histórias, cria mapas e decifra textos antigos.",
        "salary_coins": (4, 10),
        "salary_xp": (100, 220),
        "perks": [
            "Descobre locais no mapa 2x mais rápido ao explorar",
            "Pode escrever `crônica` para ganhar XP bônus registrando aventuras",
            "Acesso a livros de lore exclusivos com `ler arquivo`",
            "Pode `mapear` áreas para revelar locais secretos",
        ],
        "work_action": "Sua pena raspa o pergaminho enquanto você registra histórias que outros esquecem.",
        "work_msgs": [
            "📜 Você traduz um mapa antigo e revela uma rota perdida há séculos.",
            "✍️ Um herói lendário te pede para escrever sua biografia. Honra inesperada.",
            "🗺️ Você completa o mapa de uma região inteira em uma semana. Perfeição.",
            "📖 Seu arquivo sobre criaturas mágicas se torna referência para todo o reino.",
            "🔍 Você encontra uma inconsistência em crônicas antigas. A história foi alterada.",
        ]
    },
    "Cavaleiro": {
        "emoji": "⚔️",
        "min_level": 10,
        "description": "Protetor jurado das cidades e do povo. Defende contra invasões, patrulha e mantém a ordem.",
        "salary_coins": (10, 22),
        "salary_xp": (60, 140),
        "perks": [
            "+20 HP máximos permanentes",
            "Pode usar `patrulhar` para ganhar XP e defender a cidade",
            "Pode convocar até 2 jogadores em defesa com `convocar cavaleiros`",
            "Resistência a dano aumentada em 15% durante batalhas",
        ],
        "work_action": "Você patrulha as ruas de armadura brilhante, a mão na espada, os olhos vigilantes.",
        "work_msgs": [
            "⚔️ Você intercepta ladrões no mercado. Eles fogem ao ver sua armadura.",
            "🛡️ Uma criança perdida chora no beco escuro. Você a leva em segurança para casa.",
            "🗡️ Um bêbado começa uma briga na taverna. Você a encerra com uma palavra firme.",
            "🏰 Você escolta uma caravana real por 3 dias. Sem incidentes. Exatamente como deve ser.",
            "⚡ Um bandido saca a espada. Você a desarma em um movimento. Sem derramamento de sangue.",
        ],
        "city_defense_cooldown": 3600  # 1 hora
    },
    "Guarda_Real": {
        "emoji": "🛡️",
        "min_level": 15,
        "description": "Elite da proteção real. Defende o reino com força e lealdade absolutas.",
        "salary_coins": (15, 30),
        "salary_xp": (80, 180),
        "perks": [
            "+35 HP máximos permanentes",
            "Pode usar `defender reino` em invasões de monstros",
            "Acesso a equipamentos da guarda real na loja",
            "Pode recrutar jogadores para a guarda com `recrutar guarda`",
        ],
        "work_action": "Você fica em posição de guarda nas portas do palácio, imóvel como uma estátua de aço.",
        "work_msgs": [
            "🛡️ Uma espiã tenta se infiltrar. Seu instinto a detecta antes de qualquer dano.",
            "👑 O rei te agradece pessoalmente por salvar sua filha de um sequestro.",
            "⚔️ Você treina recrutas por uma semana. Um deles tem talento genuíno.",
            "🏰 Um ataque surpresa na madrugada é repelido sob seu comando.",
            "🗡️ Você desarma um assassino dentro do salão do trono. Silenciosamente.",
        ]
    },
    "Rei": {
        "emoji": "👑",
        "min_level": 30,
        "description": "Soberano de uma cidade. Governa, toma decisões que afetam o povo e defende o reino.",
        "salary_coins": (0, 0),
        "salary_xp": (0, 0),
        "perks": [
            "Recebe tributo diário de coins baseado no nível da cidade",
            "Pode `governar` para tomar decisões que afetam eventos futuros",
            "Pode `decretar lei` com efeitos especiais no servidor",
            "Pode `convocar guerra` para batalhas massivas com outros jogadores",
            "Pode `nomear cavaleiro @user` para promover jogadores",
            "Recebe alertas de invasão antes de outros jogadores",
        ],
        "work_action": "Você assina decretos, ouve petições e toma decisões que afetam milhares de vidas.",
        "work_msgs": [
            "👑 Você media uma disputa de terras entre dois nobres. Decisão salomônica.",
            "⚖️ Uma petição popular chega: o povo quer menos impostos. Você considera.",
            "🏰 Um embaixador de outro reino chega. Diplomacia delicada se inicia.",
            "📜 Você assina um tratado de paz com os elfos. Trégua de 50 anos.",
            "👥 O povo celebra nas ruas ao ouvir sua decisão de perdoar uma dívida coletiva.",
        ]
    }
}

# ================= EVENTOS DE INVASÃO DE CIDADE =================
CITY_INVASION_EVENTS = {
    1: [
        {
            "id": "inv_campos_001",
            "title": "🐗 Horda de Javalis Raivosos",
            "description": "Uma horda de javalis gigantes avança pela estrada principal! O mercado está sendo destruído!",
            "enemy": "Javali Enraivecido",
            "enemy_count": 8,
            "hp": 180,
            "atk": 18,
            "xp_reward": 800,
            "coins_reward": 40,
            "min_defenders": 1,
            "dialogue_options": [
                {"text": "🌾 Espalhar feno para distrair os javalis para longe", "success_chance": 0.65, "align": +5},
                {"text": "⚔️ Atacar a liderança da horda diretamente", "success_chance": 0.55, "align": +3},
                {"text": "📯 Tocar o alarme e evacuar os moradores", "success_chance": 0.80, "align": +8},
            ]
        },
        {
            "id": "inv_campos_002",
            "title": "🐀 Praga de Ratos Mágicos",
            "description": "Ratos do tamanho de gatos estão invadindo os celeiros! As reservas de comida do inverno estão em risco!",
            "enemy": "Rato Mágico Gigante",
            "enemy_count": 15,
            "hp": 80,
            "atk": 10,
            "xp_reward": 600,
            "coins_reward": 30,
            "min_defenders": 1,
            "dialogue_options": [
                {"text": "🧀 Preparar iscas envenenadas nos celeiros", "success_chance": 0.75, "align": +3},
                {"text": "🔥 Acender tochas para afugentar a praga", "success_chance": 0.60, "align": +5},
                {"text": "🐱 Recrutar gatos mágicos da floresta", "success_chance": 0.85, "align": +7},
            ]
        },
    ],
    10: [
        {
            "id": "inv_floresta_001",
            "title": "👺 Ataque Goblin Organizado",
            "description": "Uma tribo de goblins com táticas militares invade a aldeia florestal! Eles têm catapultas improvisadas!",
            "enemy": "Guerreiro Goblin",
            "enemy_count": 12,
            "hp": 350,
            "atk": 28,
            "xp_reward": 1800,
            "coins_reward": 80,
            "min_defenders": 2,
            "dialogue_options": [
                {"text": "🤝 Tentar negociar — por que os goblins atacam?", "success_chance": 0.45, "align": +12},
                {"text": "🏹 Emboscada nas árvores antes que avancem", "success_chance": 0.65, "align": +4},
                {"text": "🔥 Destruir as catapultas primeiro", "success_chance": 0.70, "align": +2},
                {"text": "💀 Ataque total sem misericórdia", "success_chance": 0.80, "align": -5},
            ]
        },
        {
            "id": "inv_floresta_002",
            "title": "🕷️ Ninho de Aranhas Colossais",
            "description": "Um ninho de aranhas colossais foi perturbado e as criaturas invadem o acampamento!",
            "enemy": "Aranha Colossal",
            "enemy_count": 6,
            "hp": 500,
            "atk": 35,
            "xp_reward": 2000,
            "coins_reward": 90,
            "min_defenders": 2,
            "dialogue_options": [
                {"text": "🔥 Fogo destrói a teia e afasta as aranhas", "success_chance": 0.75, "align": +3},
                {"text": "🧪 Usar antídoto para atrair as aranhas para longe", "success_chance": 0.60, "align": +6},
                {"text": "⚔️ Combate direto com as criaturas", "success_chance": 0.55, "align": +2},
            ]
        },
    ],
    20: [
        {
            "id": "inv_deserto_001",
            "title": "💀 Exército de Mumificados",
            "description": "O selo de Kha-Mentu foi quebrado! Um exército de guerreiros mumificados marcha pelo deserto em direção ao Oásis!",
            "enemy": "Guerreiro Mumificado",
            "enemy_count": 20,
            "hp": 600,
            "atk": 42,
            "xp_reward": 3500,
            "coins_reward": 120,
            "min_defenders": 2,
            "dialogue_options": [
                {"text": "📜 Recitar a prece de descanso dos mortos", "success_chance": 0.55, "align": +10},
                {"text": "🏺 Quebrar o artefato que os controla", "success_chance": 0.65, "align": +5},
                {"text": "⚔️ Confronto direto — são mortos, sem negociação", "success_chance": 0.70, "align": 0},
                {"text": "🚪 Evacuar o oásis e deixá-los ir", "success_chance": 0.90, "align": +3},
            ]
        },
    ],
    30: [
        {
            "id": "inv_gelo_001",
            "title": "🦣 Ataque dos Yetis Furiosos",
            "description": "Uma tempestade de neve trouxe Yetis famintos até a Fortaleza Permafrost! Eles arranham as portas!",
            "enemy": "Yeti Furioso",
            "enemy_count": 5,
            "hp": 900,
            "atk": 60,
            "xp_reward": 4500,
            "coins_reward": 150,
            "min_defenders": 2,
            "dialogue_options": [
                {"text": "🥩 Jogar comida para além dos muros para atraí-los", "success_chance": 0.70, "align": +8},
                {"text": "🔥 Acender fogueiras nas paredes para afastá-los", "success_chance": 0.65, "align": +3},
                {"text": "⚔️ Sair e enfrentar os Yetis um a um", "success_chance": 0.50, "align": +5},
                {"text": "❄️ Usar magia para criar uma barreira de gelo maior", "success_chance": 0.75, "align": +4},
            ]
        },
    ],
    40: [
        {
            "id": "inv_vulcao_001",
            "title": "🐲 Dragões de Lava Jovens",
            "description": "A erupção acordou ninhadas de dragões de lava! Três criaturas atacam a Cidadela Cinzenta!",
            "enemy": "Dragão de Lava Jovem",
            "enemy_count": 3,
            "hp": 1500,
            "atk": 90,
            "xp_reward": 7000,
            "coins_reward": 200,
            "min_defenders": 3,
            "dialogue_options": [
                {"text": "🧊 Usar magia de gelo para acalmar as criaturas", "success_chance": 0.50, "align": +12},
                {"text": "🥚 Encontrar e proteger os ovos para negociar", "success_chance": 0.60, "align": +10},
                {"text": "⚔️ Batalha total — dragões ou cidadela", "success_chance": 0.65, "align": -2},
                {"text": "💎 Oferecer gemas como pagamento para recuo", "success_chance": 0.45, "align": +5},
            ]
        },
    ],
    50: [
        {
            "id": "inv_abismo_001",
            "title": "👁️ Invasão de Entidades do Vazio",
            "description": "Uma fenda no Abismo Arcano se abre! Entidades insanas emergem com fome de realidade!",
            "enemy": "Entidade do Vazio",
            "enemy_count": 4,
            "hp": 2000,
            "atk": 120,
            "xp_reward": 10000,
            "coins_reward": 300,
            "min_defenders": 3,
            "dialogue_options": [
                {"text": "🔮 Ritual de fechamento da fenda (arriscado)", "success_chance": 0.45, "align": +15},
                {"text": "📚 Usar conhecimento arcano para comunicar com elas", "success_chance": 0.35, "align": +10},
                {"text": "⚔️ Combate dimensional com tudo que tem", "success_chance": 0.60, "align": 0},
                {"text": "💥 Explodir a fenda com magia destrutiva", "success_chance": 0.70, "align": -5},
            ]
        },
    ],
    60: [
        {
            "id": "inv_celestial_001",
            "title": "😈 Queda de Anjos Corrompidos",
            "description": "Anjos caídos atacam o Trono Celestial! Seres de luz corrompida descem em chamas!",
            "enemy": "Anjo Caído",
            "enemy_count": 5,
            "hp": 3000,
            "atk": 160,
            "xp_reward": 20000,
            "coins_reward": 500,
            "min_defenders": 3,
            "dialogue_options": [
                {"text": "✨ Tentar purificar a corrupção com luz celestial", "success_chance": 0.40, "align": +20},
                {"text": "🕊️ Preces de redenção para os seres caídos", "success_chance": 0.35, "align": +15},
                {"text": "⚔️ Batalha épica — eles escolheram a queda", "success_chance": 0.65, "align": +3},
                {"text": "🌌 Usar o poder do Trono para bani-los de volta", "success_chance": 0.55, "align": +8},
            ]
        },
    ]
}

# ================= BOSSES VARIADOS POR REINO =================
WORLD_BOSSES_VARIANTS = {
    1: [
        {"name": "👑 Slime Rei Corrompido", "hp": 200, "atk": 18, "xp": 350, "coins": (20, 45),
         "desc": "O Slime Rei foi infectado por magia negra. Seu corpo negro borbulha com veneno arcano.",
         "intro": "Uma massa negra e pulsante bloqueia seu caminho. Olhos vermelhos piscam do interior do lodo."},
        {"name": "🐀 Rato dos Esgotos Ancestral", "hp": 170, "atk": 22, "xp": 300, "coins": (15, 35),
         "desc": "Um rato que viveu nos esgotos por 500 anos. Carrega doenças de cinco civilizações.",
         "intro": "Um rato do tamanho de um cavalo emerge das profundezas. Sua pele está coberta de runas."},
        {"name": "🌪️ Espírito do Campo", "hp": 250, "atk": 15, "xp": 400, "coins": (25, 50),
         "desc": "O espírito protetor dos campos foi corrompido. Antes guardava a terra. Agora a devora.",
         "intro": "O vento para subitamente. Uma forma etérea verde e dourada materializa com olhos vazios."},
        {"name": "🌱 Ent Jovem Enraivecido", "hp": 300, "atk": 12, "xp": 380, "coins": (18, 40),
         "desc": "Um ent jovem cujas raízes foram contaminadas por poluição arcana. Ele sofre e ataca.",
         "intro": "Um conjunto de árvores se levanta e toma forma humanoide colossal. Ele geme ao se mover."},
    ],
    10: [
        {"name": "🌲 Ent Ancião das Profundezas", "hp": 450, "atk": 30, "xp": 600, "coins": (30, 70),
         "desc": "O mais antigo dos ents. Viu o mundo nascer e quer ver morrer.",
         "intro": "A floresta inteira treme. Um ent de 400 anos se ergue, sua face entalhada em sofrimento."},
        {"name": "🕷️ Mãe das Aranhas", "hp": 380, "atk": 35, "xp": 550, "coins": (25, 60),
         "desc": "A aranha original. Todas as aranhas desta floresta desceram dela.",
         "intro": "Oito olhos vermelhos brilham na escuridão. Uma aranha colossal desce do teto da caverna."},
        {"name": "👺 Rei Goblin Estrategista", "hp": 400, "atk": 28, "xp": 580, "coins": (28, 65),
         "desc": "Não é apenas bruto — ele é inteligente. E isso o torna o goblin mais perigoso já visto.",
         "intro": "Um goblin de armadura élfica roubada senta num trono de ossos. Ele te olha com interesse."},
        {"name": "🌫️ Espectro do Herói Caído", "hp": 350, "atk": 40, "xp": 620, "coins": (20, 55),
         "desc": "Um herói que morreu sem completar sua missão. Preso entre vivos e mortos pela raiva.",
         "intro": "Uma figura translúcida em armadura enferrujada empunha uma espada de luz mortiça."},
    ],
    20: [
        {"name": "🔺 Faraó Kha-Mentu Ressurgido", "hp": 600, "atk": 45, "xp": 900, "coins": (40, 90),
         "desc": "O faraó da primeira civilização. Morreu traído por seus sacerdotes. Voltou com sede de vingança.",
         "intro": "A pirâmide treme. Bandagens douradas flutuam pelo ar. O faraó abre os olhos dourados."},
        {"name": "🦂 Grande Escorpião do Deserto", "hp": 550, "atk": 50, "xp": 850, "coins": (35, 80),
         "desc": "Escorpião com veneno capaz de matar um elefante. Protege ruínas por séculos.",
         "intro": "As dunas explodem. Um escorpião colossal surge do subsolo, pinças do tamanho de árvores."},
        {"name": "🌪️ Djinn do Vento de Areia", "hp": 500, "atk": 55, "xp": 880, "coins": (30, 75),
         "desc": "Gênio aprisionado há milênios. A raiva do cativeiro o transformou em algo incontrolável.",
         "intro": "Uma tempestade de areia para e toma forma humana. Olhos como tempestades te encarram."},
        {"name": "🏺 Golem da Argila Sagrada", "hp": 700, "atk": 38, "xp": 920, "coins": (45, 95),
         "desc": "Criado para proteger o templo. Agora que o templo caiu, ele não sabe o que proteger.",
         "intro": "Uma estátua de argila de 5 metros pisca. Runas sagradas brilham em seu peito. Ele avança."},
    ],
    30: [
        {"name": "❄️ Titã do Gelo Eterno", "hp": 800, "atk": 60, "xp": 1200, "coins": (50, 110),
         "desc": "Um titã de gelo que dormia no coração da montanha. Despertou com a invasão de aventureiros.",
         "intro": "Uma avalanche para no ar. Blocos de gelo se reorganizam numa forma colossal de 10 metros."},
        {"name": "🐉 Dragão de Cristal", "hp": 750, "atk": 70, "xp": 1300, "coins": (55, 120),
         "desc": "Um dragão cujas escamas viraram cristal por uma maldição. Belo e letal.",
         "intro": "Luz se refrata por toda a caverna. Um dragão translúcido de cristal azul te olha com curiosidade."},
        {"name": "🦣 Rei dos Yetis", "hp": 900, "atk": 55, "xp": 1100, "coins": (45, 100),
         "desc": "O patriarca de toda a tribo Yeti. Tão antigo que sua pelagem virou neve permanente.",
         "intro": "A temperatura cai 20 graus de repente. O maior ser que você já viu emerge da nevasca."},
        {"name": "🌊 Elemental de Gelo Primordial", "hp": 680, "atk": 75, "xp": 1350, "coins": (60, 130),
         "desc": "Um elemental que existia antes de qualquer montanha ser formada. Ele é a própria neve.",
         "intro": "Flocos de neve flutuam em padrão impossível. Eles se fundem numa entidade translúcida e feroz."},
    ],
    40: [
        {"name": "🌋 Ignarius, Dragão de Magma Ancião", "hp": 1100, "atk": 85, "xp": 1800, "coins": (70, 150),
         "desc": "O primeiro ser criado quando o mundo era fogo. Guarda a Chama Original com ciúme eterno.",
         "intro": "O vulcão erupciona de dentro pra fora. Magma toma forma. Ignarius abre os olhos de brasa."},
        {"name": "⚒️ Golem da Forja Corrompida", "hp": 950, "atk": 95, "xp": 1700, "coins": (65, 140),
         "desc": "A Forja Sagrada criou este golem para se defender. Mas a forja ficou louca.",
         "intro": "Ferramentas flutuam em espiral. O metal derretido toma forma de um guerreiro monstruoso."},
        {"name": "💀 Espírito do Forjador Traído", "hp": 880, "atk": 100, "xp": 1900, "coins": (75, 160),
         "desc": "Um forjador anão que foi assassinado pela coroa. Sua raiva o manteve vivo em forma etérea.",
         "intro": "O ar cheira a metal e ranço. Uma figura translúcida com martelo de fogo surge do nada."},
        {"name": "🔥 Salamandra Primordial", "hp": 1000, "atk": 90, "xp": 1750, "coins": (68, 145),
         "desc": "A salamandra que nasceu do primeiro fogo do universo. Criatura mais antiga do Reino.",
         "intro": "O chão de lava explode. Uma salamandra do tamanho de uma casa emerge, cantando em chamas."},
    ],
    50: [
        {"name": "🌀 O Senhor das Sombras", "hp": 1500, "atk": 120, "xp": 2800, "coins": (90, 200),
         "desc": "Entidade que existia antes do universo. Quer apagar a realidade e retornar ao silêncio primordial.",
         "intro": "A luz some. Não há escuridão — há ausência de tudo. Então ele fala: 'Você também cansou de existir?'"},
        {"name": "👁️ Olho do Abismo", "hp": 1200, "atk": 140, "xp": 3000, "coins": (100, 220),
         "desc": "Um olho do tamanho de uma casa que observa desde o início dos tempos. Enlouquece quem o encontra.",
         "intro": "Uma pupila vertical de 3 metros se abre no teto do Abismo. Você sente ser estudado até o DNA."},
        {"name": "🌌 Arquimago Zephyr Corrompido", "hp": 1350, "atk": 110, "xp": 2600, "coins": (85, 190),
         "desc": "O maior mago do mundo se corrompeu estudando o Abismo. Agora é parte dele.",
         "intro": "Uma silhueta familiar usa magias impossíveis. Você reconhece o rosto: Zephyr, com olhos vazios."},
        {"name": "♾️ Loop Temporal", "hp": 1100, "atk": 130, "xp": 2900, "coins": (95, 210),
         "desc": "Uma entidade que é o próprio tempo se loopando. Cada vez que você ataca, ela volta um segundo.",
         "intro": "Você sente déjà vu. E de novo. E de novo. Uma entidade surge com múltiplas versões de si mesma."},
    ],
    60: [
        {"name": "👑 Imperador Astral", "hp": 2500, "atk": 180, "xp": 5000, "coins": (150, 350),
         "desc": "O governante do Trono Celestial. Não é mau — é o teste final. Aqueles dignos passarão.",
         "intro": "O Trono brilha com luz insuportável. Uma figura de luz pura desce. 'Você chegou. Curioso.'"},
        {"name": "😈 Querubim Corrompido Makhael", "hp": 2000, "atk": 200, "xp": 5500, "coins": (160, 370),
         "desc": "O anjo mais belo que existiu, corrompido pela inveja. Sua queda criou um buraco no céu.",
         "intro": "Asas negras preenchem o horizonte. Um ser de beleza aterrorizante pousa, com espada de trevas."},
        {"name": "🌌 Vácuo da Criação", "hp": 3000, "atk": 150, "xp": 4500, "coins": (140, 320),
         "desc": "O espaço vazio onde a criação começa e termina. É o nada que deseja ser algo.",
         "intro": "O Trono implode em silêncio. No centro do vácuo, algo toma forma — ou talvez seja o vazio mesmo."},
        {"name": "⭐ O Primeiro Herói (Corrompido)", "hp": 2200, "atk": 190, "xp": 5200, "coins": (155, 360),
         "desc": "O primeiro aventureiro que passou por todos os reinos. Corrompido pelo poder do Trono.",
         "intro": "Você reconhece os equipamentos: os mesmos de todas as lendas antigas. Mas os olhos são do Vazio."},
    ]
}

# ================= SISTEMA DE ALINHAMENTO MORAL =================
ALIGNMENT_TITLES = {
    "Heroi":      {"emoji": "✨", "color": 0xFFD700, "desc": "Protetor dos inocentes, luz nas trevas."},
    "Anti-Heroi": {"emoji": "⚖️", "color": 0x888888, "desc": "Nem bom, nem mau. Apenas pragmático."},
    "Vilao":      {"emoji": "💀", "color": 0xFF0000, "desc": "O medo é sua arma. O poder é seu deus."},
    "Neutro":     {"emoji": "🌑", "color": 0x444444, "desc": "Ainda sem definição. O destino aguarda."},
}

# Pontos: +10 = herói, -10 = vilão, zona neutra = anti-herói
ALIGNMENT_SCENARIOS = {
    1: [  # Campos
        {
            "id": "esc_campos_001",
            "emoji": "🏘️",
            "title": "O Aldeão Desesperado",
            "description": "Um aldeão idoso se ajoelha diante de você, com lágrimas nos olhos. Seus filhos foram capturados pelo Slime Rei. Ele oferece suas últimas 3 moedas em pagamento.",
            "choices": [
                {"text": "✨ Aceitar a missão gratuitamente e ir resgatar os filhos",      "align": +10, "xp": 300, "coins": 0,   "result": "Você salva os filhos sem pedir nada em troca. A aldeia inteira celebra seu nome."},
                {"text": "⚖️ Aceitar as 3 moedas e completar a missão",                    "align": 0,   "xp": 200, "coins": 3,   "result": "Uma transação justa. Os filhos são salvos. O aldeão agradece com o que pôde."},
                {"text": "💀 Exigir todo o tesouro da aldeia para ajudar",                  "align": -10, "xp": 150, "coins": 15,  "result": "Você extorque o aldeão. Os filhos são salvos, mas você é amaldiçoado pelo sofrimento causado."},
                {"text": "🏃 Ignorar o pedido e seguir em frente",                         "align": -5,  "xp": 0,   "coins": 0,   "result": "Você passa direto. Os gritos do aldeão ecoam em sua mente por dias."},
            ]
        },
        {
            "id": "esc_campos_002",
            "emoji": "🐺",
            "title": "A Matilha Faminta",
            "description": "Uma matilha de lobos faminta bloqueia a estrada. Eles não são monstros — apenas animais com fome depois de uma seca prolongada. Aldeões assustados assistem de longe.",
            "choices": [
                {"text": "✨ Caçar comida e alimentar os lobos para liberarem a estrada",   "align": +8,  "xp": 250, "coins": 0,   "result": "Os lobos comem e se dispersam. Os aldeões nunca esquecerão o gesto."},
                {"text": "⚖️ Assustar a matilha para longe sem ferir nenhum",               "align": +3,  "xp": 180, "coins": 0,   "result": "Com ruído e fogo, você afasta os lobos. Eficiente e sem sangue."},
                {"text": "💀 Matar todos os lobos para garantir a estrada livre",            "align": -5,  "xp": 200, "coins": 5,   "result": "A estrada fica livre... e coberta de sangue. Os aldeões ficam em silêncio."},
                {"text": "⚖️ Cobrar dos aldeões para abrir a passagem",                     "align": -2,  "xp": 100, "coins": 8,   "result": "Negócio é negócio. Você dispersa os lobos, os aldeões pagam contrariados."},
            ]
        },
        {
            "id": "esc_campos_003",
            "emoji": "💰",
            "title": "O Tesouro do Ladrão",
            "description": "Você encontra um ladrão inconsciente após uma queda. Ao seu lado, uma bolsa com moedas roubadas de aldeões. Uma nota diz para quem pertence cada moeda.",
            "choices": [
                {"text": "✨ Devolver cada moeda ao dono certo usando a lista",              "align": +12, "xp": 200, "coins": 0,   "result": "Cada aldeão recebe de volta o que era seu. Sua honra cresce."},
                {"text": "⚖️ Guardar metade e devolver metade anonimamente",                "align": -2,  "xp": 100, "coins": 12,  "result": "Alguns aldeões recebem de volta algo. Você fica com o resto."},
                {"text": "💀 Ficar com tudo — o ladrão não merecia mesmo",                   "align": -8,  "xp": 50,  "coins": 25,  "result": "Você rouba do ladrão. O dinheiro é seu agora, mas o karma não esquece."},
                {"text": "🏥 Chamar um curandeiro para o ladrão e reportar à guarda",       "align": +10, "xp": 180, "coins": 0,   "result": "Justiça é feita. O ladrão recebe ajuda e responderá pelo que fez."},
            ]
        },
        {
            "id": "esc_campos_004",
            "emoji": "🔥",
            "title": "Celeiro em Chamas",
            "description": "Um celeiro pega fogo! Uma criança está presa dentro. O dono tenta entrar mas é segurado por outros. Você pode agir.",
            "choices": [
                {"text": "✨ Entrar correndo e salvar a criança (perde 30 HP)",              "align": +15, "xp": 400, "coins": 0,   "result": "Você entra pelas chamas. A criança está viva. Você sai queimado, mas vivo. Herói."},
                {"text": "⚖️ Organizar um balde de água com os aldeões antes",              "align": +5,  "xp": 200, "coins": 0,   "result": "Trabalho em equipe. A criança é salva com risco menor para todos."},
                {"text": "💀 Observar sem agir — não é problema seu",                       "align": -12, "xp": 0,   "coins": 0,   "result": "Você assiste. A criança sobrevive por sorte. Os aldeões nunca te perdoarão."},
                {"text": "⚖️ Entrar SE receberem uma boa recompensa primeiro",              "align": -6,  "xp": 200, "coins": 20,  "result": "Você negocia enquanto a criança grita. Ela sobrevive. A aldeia fica dividida sobre você."},
            ]
        },
    ],
    10: [  # Floresta
        {
            "id": "esc_floresta_001",
            "emoji": "🌲",
            "title": "O Acampamento Goblin",
            "description": "Você descobre um acampamento goblin. Mas ao se aproximar, vê que são goblins jovens — praticamente crianças — aprendendo a sobreviver sem adultos. Eles ficam com medo de você.",
            "choices": [
                {"text": "✨ Ensinar as crianças a pescar e coletar alimentos",               "align": +12, "xp": 350, "coins": 0,   "result": "Os jovens goblins aprendem. Décadas depois, eles serão pacifistas que lembram do herói."},
                {"text": "⚖️ Ignorar e passar sem interagir",                               "align": 0,   "xp": 0,   "coins": 0,   "result": "Você não ajuda, mas também não prejudica. Eles continuam sua vida."},
                {"text": "💀 Atacar o acampamento para 'eliminar uma ameaça futura'",        "align": -15, "xp": 300, "coins": 8,   "result": "Você ataca crianças indefesas. XP fácil, mas uma mancha irreparável na alma."},
                {"text": "⚖️ Roubar os alimentos deles discretamente",                      "align": -8,  "xp": 50,  "coins": 10,  "result": "Você rouba de crianças. Elas ficam com fome. O karma lembra."},
            ]
        },
        {
            "id": "esc_floresta_002",
            "emoji": "👁️",
            "title": "A Espiã da Floresta",
            "description": "Uma elfa te intercepta. Ela é uma espiã da resistência contra um tirano que governa um vilarejo próximo. Ela pede sua ajuda para entregar uma mensagem secreta.",
            "choices": [
                {"text": "✨ Ajudar a entrega da mensagem pro bem da resistência",           "align": +10, "xp": 400, "coins": 0,   "result": "A mensagem chega. A resistência se fortalece. Você fez parte da história."},
                {"text": "💀 Trair a espiã ao tirano em troca de ouro",                     "align": -15, "xp": 100, "coins": 30,  "result": "A espiã é capturada. O tirano te paga. A resistência cai por ora."},
                {"text": "⚖️ Pedir pagamento para a entrega",                               "align": -3,  "xp": 250, "coins": 15,  "result": "Serviço prestado por moedas. A elfa suspira, mas aceita."},
                {"text": "⚖️ Recusar — muito perigoso envolver-se em política",             "align": 0,   "xp": 0,   "coins": 0,   "result": "Você recusa e segue. A resistência encontra outro mensageiro."},
            ]
        },
    ],
    20: [  # Deserto
        {
            "id": "esc_deserto_001",
            "emoji": "🏺",
            "title": "A Tumba Profanada",
            "description": "Um grupo de saqueadores está violando uma tumba sagrada, levando artefatos dos ancestrais. Um ancião nomade te pede para intervir.",
            "choices": [
                {"text": "✨ Expulsar os saqueadores e devolver os artefatos ao ancião",    "align": +12, "xp": 500, "coins": 0,   "result": "Os artefatos voltam ao seu lugar. O ancião te abençoa com conhecimento antigo."},
                {"text": "⚖️ Expulsar os saqueadores e ficar com metade",                   "align": -3,  "xp": 300, "coins": 25,  "result": "Meio certo, meio errado. O ancião fica com o suficiente para o ritual."},
                {"text": "💀 Juntar-se aos saqueadores — mais dividido entre mais gente",   "align": -10, "xp": 200, "coins": 40,  "result": "Você saqueia junto. Riqueza fácil. A maldição do faraó observa em silêncio."},
                {"text": "⚖️ Negociar com os saqueadores para eles pararem",               "align": +5,  "xp": 200, "coins": 0,   "result": "Palavras no lugar de violência. Eles recuam. Alguns artefatos foram perdidos."},
            ]
        },
    ],
    30: [  # Montanhas
        {
            "id": "esc_gelo_001",
            "emoji": "🏔️",
            "title": "A Aldeia Sitiada",
            "description": "Uma aldeia nas montanhas está sitiada por bandidos que exigem tributo mensal. Os moradores estão famintos e com frio. Os bandidos são 5, todos armados.",
            "choices": [
                {"text": "✨ Enfrentar os 5 bandidos sozinho para libertar a aldeia",       "align": +15, "xp": 600, "coins": 0,   "result": "Batalha épica. Você vence. A aldeia é livre. Eles te constroem uma estátua."},
                {"text": "⚖️ Treinar os aldeões para se defenderem sozinhos",               "align": +10, "xp": 500, "coins": 0,   "result": "Você ensina a pescar. A aldeia aprende a se proteger para sempre."},
                {"text": "💀 Fazer um acordo com os bandidos — eles te pagam para manter controle", "align": -12, "xp": 150, "coins": 35, "result": "Você lucra com o sofrimento. Os aldeões continuam pagando. Agora para você também."},
                {"text": "⚖️ Negociar a saída dos bandidos com seu espólio de batalha",    "align": +3,  "xp": 300, "coins": 10,  "result": "Dinheiro muda mentes. Os bandidos partem. A aldeia respira aliviada."},
            ]
        },
    ],
    40: [  # Vulcão
        {
            "id": "esc_vulcao_001",
            "emoji": "🌋",
            "title": "A Última Criança Anã",
            "description": "Você encontra a única criança sobrevivente de uma civilização anã destruída pelo vulcão. Ela segura um mapa para um tesouro lendário de sua nação.",
            "choices": [
                {"text": "✨ Adotar a criança e protegê-la, esquecendo o tesouro",          "align": +15, "xp": 700, "coins": 0,   "result": "Você escolhe uma vida acima do ouro. A criança cresce para se tornar uma lenda."},
                {"text": "⚖️ Ajudar a criança a recuperar o tesouro de sua nação",          "align": +10, "xp": 600, "coins": 50,  "result": "Justo. O tesouro pertence a ela. Você recebe uma parte como herança da civilização."},
                {"text": "💀 Roubar o mapa e deixar a criança para trás",                   "align": -15, "xp": 200, "coins": 80,  "result": "Você rouba de uma órfã. O tesouro é seu. Mas o peso disso nunca sai."},
                {"text": "⚖️ Levar ao acampamento mais próximo e seguir adiante",           "align": +3,  "xp": 200, "coins": 0,   "result": "Você a coloca em segurança. Não ficou com o tesouro, mas também não abandonou."},
            ]
        },
    ],
    50: [  # Abismo
        {
            "id": "esc_abismo_001",
            "emoji": "👁️",
            "title": "O Pacto das Sombras",
            "description": "Uma entidade do Abismo te oferece poder imenso. Tudo que precisa é assinar um pacto — sacrificando a felicidade de três pessoas que não te conhecem.",
            "choices": [
                {"text": "✨ Recusar o pacto com firmeza e atacar a entidade",               "align": +15, "xp": 800, "coins": 0,   "result": "A entidade recua. Você resiste à tentação. Raro. Muito raro."},
                {"text": "💀 Assinar o pacto — poder acima de tudo",                        "align": -20, "xp": 1000, "coins": 100, "result": "O poder chega. Em algum lugar, três estranhos acordam com pesadelos eternos."},
                {"text": "⚖️ Fingir aceitar e depois quebrar o pacto",                     "align": -5,  "xp": 500, "coins": 50,  "result": "Você engana a entidade. Ela não esquece facilmente."},
                {"text": "⚖️ Negociar termos — sacrifício menor, poder menor",             "align": -8,  "xp": 600, "coins": 60,  "result": "Um acordo menor. Poder moderado. Culpa moderada. Tudo moderado."},
            ]
        },
    ],
    60: [  # Trono
        {
            "id": "esc_celestial_001",
            "emoji": "👑",
            "title": "O Julgamento Final",
            "description": "O Imperador Astral oferece a você o poder de reescrever a história de UMA pessoa — alguém que sofreu imerecidamente. Mas para isso, outra pessoa terá que sofrer no lugar.",
            "choices": [
                {"text": "✨ Recusar — o sofrimento não deve ser transferido, deve ser curado", "align": +20, "xp": 2000, "coins": 0,  "result": "O Imperador sorri. 'Finalmente alguém entendeu.' Você recebe a bênção do Trono."},
                {"text": "💀 Escolher quem sofre — transferir para um vilão conhecido",      "align": -5,  "xp": 1200, "coins": 200, "result": "Julgamento humano de sofrimento. A lógica parece boa... mas quem decide quem merece?"},
                {"text": "⚖️ Perguntar se há uma terceira opção antes de decidir",          "align": +8,  "xp": 1500, "coins": 0,   "result": "Existe sempre. O Imperador abre um caminho alternativo de cura sem custo."},
                {"text": "💀 Usar o poder em si mesmo — apagar seu próprio sofrimento",     "align": -10, "xp": 1000, "coins": 100, "result": "Egoísta. Funciona. Mas você perdeu a chance de ser verdadeiramente grande."},
            ]
        },
    ],
}

# ================= QUESTS ALINHAMENTO MORAL =================
ALIGNMENT_QUESTS = {
    "heroi": [
        {
            "id": "heroi_001",
            "name": "🛡️ Protetor das Crianças Perdidas",
            "description": "Crianças órfãs estão sendo escravizadas por um mercador corrupto. Resgate 8 crianças das grades.",
            "type": "individual", "objective": "hunt", "target": "Mercador Corrupto",
            "count": 1, "reward_xp": 2000, "reward_coins": 50, "reward_item": "Poção de Vida Superior",
            "align_required": "Heroi", "align_gain": +10,
            "lore": "O mercador tem conexões perigosas. Seja cuidadoso.",
            "npc": "Madre Celeste", "difficulty": "Difícil"
        },
        {
            "id": "heroi_002",
            "name": "✨ A Cura da Aldeia Amaldiçoada",
            "description": "Uma maldição arcana infecta uma aldeia inteira. Colete 12 ingredientes para o ritual de cura.",
            "type": "individual", "objective": "collect", "count": 12,
            "reward_xp": 1800, "reward_coins": 30, "reward_item": "Elixir da Vida",
            "align_required": "Heroi", "align_gain": +8,
            "lore": "A maldição foi lançada por um mago que perdeu a família nesta aldeia. Tragédia se alimenta de tragédia.",
            "npc": "Padre Elian", "difficulty": "Médio"
        },
    ],
    "anti_heroi": [
        {
            "id": "anti_001",
            "name": "⚖️ O Trabalho Sujo",
            "description": "O prefeito precisa de alguém para 'resolver' um problema sem fazer perguntas. Explore a área e descubra.",
            "type": "individual", "objective": "explore", "count": 5,
            "reward_xp": 1500, "reward_coins": 100, "reward_item": None,
            "align_required": None, "align_gain": -2,
            "lore": "O prefeito não diz o que quer. Você não pergunta. Esse é o acordo.",
            "npc": "Prefeito Sombra", "difficulty": "Médio"
        },
        {
            "id": "anti_002",
            "name": "⚖️ Informações Valiosas",
            "description": "Colete 10 artefatos de locais proibidos. Ninguém precisa saber de onde vieram.",
            "type": "individual", "objective": "collect", "count": 10,
            "reward_xp": 2000, "reward_coins": 80, "reward_item": "Poção de Sorte",
            "align_required": None, "align_gain": -3,
            "lore": "Informação é poder. E você está se tornando muito poderoso.",
            "npc": "Informante Xan", "difficulty": "Difícil"
        },
    ],
    "vilao": [
        {
            "id": "vilao_001",
            "name": "💀 A Purga dos Campos",
            "description": "Um lorde sombrio quer os campos 'limpos' de aldeões. Cace 10 monstros que 'protegem' as aldeias.",
            "type": "individual", "objective": "hunt", "target": None,
            "count": 10, "reward_xp": 2500, "reward_coins": 200, "reward_item": "Foice Maldita",
            "align_required": "Vilao", "align_gain": -10,
            "lore": "O Lorde Sombrio promete poder em troca de serviço. O preço é a sua humanidade.",
            "npc": "Lorde Maldito Vorn", "difficulty": "Médio"
        },
        {
            "id": "vilao_002",
            "name": "🌑 Sabotar a Resistência",
            "description": "Explore acampamentos da resistência e plante informações falsas. Visite 7 locais.",
            "type": "individual", "objective": "explore", "count": 7,
            "reward_xp": 3000, "reward_coins": 150, "reward_item": "Poção de Sorte",
            "align_required": "Vilao", "align_gain": -8,
            "lore": "A resistência luta pelo povo. Você luta pelo poder. Apenas um pode vencer.",
            "npc": "Chanceler das Sombras", "difficulty": "Difícil"
        },
    ]
}

# ================= BAÚS MIMIC =================
MIMIC_TIERS = [
    {
        "name": "Baú Comum",
        "emoji": "📦",
        "mimic_chance": 0.20,
        "loot_xp": (200, 400),
        "loot_coins": (5, 15),
        "loot_items": ["Comum", "Incomum"],
        "mimic_dmg": (20, 40),
        "mimic_xp_loss": (50, 100),
        "mimic_desc": "💥 O baú se abre e dentes enormes aparecem! O MIMIC te ataca!",
    },
    {
        "name": "Baú Élfico",
        "emoji": "🗝️",
        "mimic_chance": 0.30,
        "loot_xp": (500, 900),
        "loot_coins": (10, 25),
        "loot_items": ["Incomum", "Raro"],
        "mimic_dmg": (35, 65),
        "mimic_xp_loss": (120, 200),
        "mimic_desc": "🦷 O ornamento élfico era falso! Garras surgem das dobradiças! MIMIC ÉLFICO!",
    },
    {
        "name": "Baú Rúnico",
        "emoji": "🔮",
        "mimic_chance": 0.35,
        "loot_xp": (1000, 2000),
        "loot_coins": (15, 40),
        "loot_items": ["Raro", "Épico"],
        "mimic_dmg": (50, 90),
        "mimic_xp_loss": (200, 350),
        "mimic_desc": "🌑 As runas pulsam com vida própria! Um MIMIC RÚNICO emerge com poder arcano!",
    },
    {
        "name": "Baú Lendário",
        "emoji": "⚜️",
        "mimic_chance": 0.40,
        "loot_xp": (2000, 4000),
        "loot_coins": (20, 60),
        "loot_items": ["Épico", "Lendário"],
        "mimic_dmg": (80, 130),
        "mimic_xp_loss": (400, 600),
        "mimic_desc": "👁️ Os olhos do baú se abrem. Um MIMIC LENDÁRIO! A criatura mais antiga desta dungeon!",
    },
]

# ================= SISTEMA DE MAPA =================
MAP_LOCATIONS = {
    # Cada mundo tem uma lista de locais descobríveis
    1: {
        "world_name": "🌱 Campos Iniciais",
        "locations": [
            {"id": "campos_vila", "name": "🏘️ Vila dos Primeiros Passos", "type": "cidade", "discovered": True},
            {"id": "campos_pedreira", "name": "⛏️ Pedreira dos Iniciantes", "type": "recurso", "discovered": False},
            {"id": "campos_gruta", "name": "🕳️ Gruta do Slime Ancião", "type": "dungeon", "discovered": False},
            {"id": "campos_floresta_borda", "name": "🌿 Borda da Floresta Proibida", "type": "portal", "discovered": False},
            {"id": "campos_torre", "name": "🗼 Torre do Observador", "type": "npc_especial", "discovered": False},
        ]
    },
    10: {
        "world_name": "🌲 Floresta Sombria",
        "locations": [
            {"id": "floresta_acampamento", "name": "⛺ Acampamento das Sombras", "type": "cidade", "discovered": True},
            {"id": "floresta_arvore_milenar", "name": "🌳 Árvore Milenar do Ent", "type": "boss_local", "discovered": False},
            {"id": "floresta_rio_negro", "name": "🖤 Rio das Águas Negras", "type": "recurso", "discovered": False},
            {"id": "floresta_ruinas", "name": "🏚️ Ruínas do Reino Élfico", "type": "dungeon", "discovered": False},
            {"id": "floresta_claro", "name": "🌙 Clareira da Lua", "type": "evento_especial", "discovered": False},
        ]
    },
    20: {
        "world_name": "🏜️ Deserto das Almas",
        "locations": [
            {"id": "deserto_oasis", "name": "🌴 Oásis de Amun", "type": "cidade", "discovered": True},
            {"id": "deserto_piramide", "name": "🔺 Grande Pirâmide de Kha-Mentu", "type": "boss_local", "discovered": False},
            {"id": "deserto_mercado", "name": "🏪 Mercado das Almas", "type": "loja", "discovered": False},
            {"id": "deserto_oasis_secreto", "name": "💧 Oásis do Tempo", "type": "dungeon_secreta", "discovered": False},
            {"id": "deserto_ruinas_antigas", "name": "🏛️ Ruínas da Primeira Civilização", "type": "lore", "discovered": False},
        ]
    },
    30: {
        "world_name": "❄️ Montanhas Geladas",
        "locations": [
            {"id": "gelo_fortaleza", "name": "🏰 Fortaleza Permafrost", "type": "cidade", "discovered": True},
            {"id": "gelo_pico", "name": "🏔️ Pico dos Titãs", "type": "boss_local", "discovered": False},
            {"id": "gelo_mina", "name": "⛏️ Mina dos Cristais Eternos", "type": "recurso", "discovered": False},
            {"id": "gelo_palacio", "name": "❄️ Palácio de Cristal Perdido", "type": "dungeon_secreta", "discovered": False},
            {"id": "gelo_portal", "name": "🌌 Portal para o Vulcão", "type": "portal", "discovered": False},
        ]
    },
    40: {
        "world_name": "🌋 Reino Vulcânico",
        "locations": [
            {"id": "vulcao_cidadela", "name": "🔥 Cidadela Cinzenta", "type": "cidade", "discovered": True},
            {"id": "vulcao_cratera", "name": "🌋 Cratera Principal", "type": "boss_local", "discovered": False},
            {"id": "vulcao_forja", "name": "⚒️ A Forja Sagrada dos Anões", "type": "crafting", "discovered": False},
            {"id": "vulcao_camara", "name": "🔥 Câmara da Chama Original", "type": "dungeon_secreta", "discovered": False},
            {"id": "vulcao_rio_lava", "name": "🌊 Rio de Lava Eterna", "type": "recurso", "discovered": False},
        ]
    },
    50: {
        "world_name": "🌌 Abismo Arcano",
        "locations": [
            {"id": "abismo_torre", "name": "🗼 Torre do Conhecimento Perdido", "type": "cidade", "discovered": True},
            {"id": "abismo_vortex", "name": "🌀 Vórtice Central do Abismo", "type": "boss_local", "discovered": False},
            {"id": "abismo_biblioteca", "name": "📚 Biblioteca dos Tomos Proibidos", "type": "lore", "discovered": False},
            {"id": "abismo_loop", "name": "♾️ Loop Temporal", "type": "dungeon_secreta", "discovered": False},
            {"id": "abismo_portal", "name": "✨ Portal para o Trono", "type": "portal", "discovered": False},
        ]
    },
    60: {
        "world_name": "👑 Trono Celestial",
        "locations": [
            {"id": "celestial_antecamara", "name": "🏛️ Antecâmara do Trono", "type": "cidade", "discovered": True},
            {"id": "celestial_trono", "name": "👑 O Trono em Si", "type": "boss_local", "discovered": False},
            {"id": "celestial_alem", "name": "🌌 Além do Trono", "type": "dungeon_secreta", "discovered": False},
            {"id": "celestial_raiz", "name": "✨ Raiz da Criação", "type": "dungeon_secreta", "discovered": False},
            {"id": "celestial_arquivo", "name": "📜 Arquivo do Destino", "type": "lore", "discovered": False},
        ]
    },
}

# ================= NOVOS NPCs COM LORE =================
WORLD_NPCS_EXTRA = {
    1: [
        {
            "name": "Sábio Pell",
            "role": "Historiador dos Campos",
            "emoji": "📜",
            "dialogues": [
                "Estudei os Campos por 40 anos. Cada pedra aqui é uma página de história.",
                "Sabia que o primeiro herói que passou por aqui era uma cozinheira? Ela matou o Slime Rei com uma frigideira.",
                "Os slimes têm memória coletiva. Quando você mata um, os outros sentem. Por isso ficam mais agressivos.",
                "Encontrei inscrições de 3.000 anos atrás naquelas pedras. Dizem que 'o herói verdadeiro virá dos campos'. Poderia ser você.",
                "Minha teoria: este campo foi um campo de batalha divino. Os slimes são cicatrizes da guerra.",
            ]
        },
        {
            "name": "Criança Miko",
            "role": "Garoto Curioso",
            "emoji": "👦",
            "dialogues": [
                "Você é um aventureiro de verdade?! Isso é incrível! Quando crescer, vou ser como você!",
                "Vi um slime comer uma pedra inteira ontem. Por que eles comem pedra?",
                "Minha mãe diz para não falar com estranhos. Mas você não parece estranho... parece ÉPICO!",
                "Encontrei uma moeda dourada no campo. Papai disse que pertencia a um herói antigo. Posso te mostrar?",
                "Às vezes ouço o campo sussurrar à noite. Papai diz que é o vento. Mas eu sei que não é.",
            ]
        },
    ],
    10: [
        {
            "name": "Espírito Ancião Vel",
            "role": "Guardião Espectral",
            "emoji": "👻",
            "dialogues": [
                "Morri aqui há 800 anos. A floresta me manteve aqui para guardar um segredo.",
                "O Ent e eu somos velhos amigos. Ele estava aqui antes de mim. E estará depois.",
                "Há uma chave enterrada sob a árvore maior. Não a procure ainda. Você ainda não está pronto.",
                "Na vida, fui guerreiro. Na morte, aprendi que a paz verdadeira não vem da vitória, mas da compreensão.",
                "Se você ouvir a floresta cantar à meia-noite, não responda. Nunca responda.",
            ]
        },
        {
            "name": "Bruxo das Raízes",
            "role": "Místico da Floresta",
            "emoji": "🧙",
            "dialogues": [
                "Cada árvore desta floresta é uma palavra num livro que nenhum humano escreveu.",
                "Posso ler seu destino nas raízes expostas. Quer ouvir? Cuidado — a verdade pesa.",
                "Os goblins não são maus por natureza. São o reflexo de como os humanos os trataram.",
                "Há 300 anos, esta floresta era um jardim celestial. O que aconteceu? Os deuses discordaram.",
                "Vejo em você algo que não via há gerações. Uma chama que não se apaga com facilidade.",
            ]
        },
    ],
    20: [
        {
            "name": "Fantasma do General",
            "role": "Espírito Guerreiro",
            "emoji": "⚔️",
            "dialogues": [
                "Lutei na última guerra do Deserto. Mil anos atrás. Ainda não sei quem venceu.",
                "A areia guarda os mortos melhor que qualquer túmulo. Cada duna é um cemitério.",
                "O Faraó Kha-Mentu era meu general. Ele não merecia o que fizeram com ele.",
                "Há uma espada enterrada a 30 metros de profundidade aqui perto. Ela espera por alguém digno.",
                "No calor mais forte, quando a miragem aparece, olhe nos olhos dela. Ela mostra o futuro.",
            ]
        },
        {
            "name": "Mercante Ib",
            "role": "Comerciante Nômade",
            "emoji": "🐪",
            "dialogues": [
                "Viajei por todos os sete reinos. Este deserto é o mais honesto — ele mata com calor, sem subterfúgios.",
                "Já vendi uma estrela embalsamada uma vez. O cliente nunca descobriu que era falsa. Ou descobriu e não se importou.",
                "O mercado das almas está três dunas ao norte. Não compre nada lá que você não possa pagar com algo além de ouro.",
                "Ouvi que o Faraó Kha-Mentu tem uma câmara com mapas de reinos que ainda não existem.",
                "O escorpião que te pica hoje pode salvar sua vida amanhã. Aprendi isso do jeito difícil.",
            ]
        },
    ],
    30: [
        {
            "name": "Vidente das Neves",
            "role": "Oráculo das Montanhas",
            "emoji": "🔮",
            "dialogues": [
                "Vejo três futuros possíveis para você. Todos difíceis. Um deles é glorioso.",
                "O Yeti chorou uma vez. Eu vi. As lágrimas congelaram antes de chegar ao chão.",
                "Os Titãs do Gelo me ensinaram que o frio não mata — a resistência a ele sim.",
                "Há uma criança que vai mudar este mundo. Ela já nasceu. Você pode ter passado por ela.",
                "Quando a montanha cantar, três vezes, em noite sem lua — é hora do próximo ciclo começar.",
            ]
        },
    ],
    40: [
        {
            "name": "Anão Sobrevivente Krug",
            "role": "Último dos Forjadores",
            "emoji": "⚒️",
            "dialogues": [
                "Sou o último da minha linhagem. Os outros se fundiram com Ignarius voluntariamente. Fui covarde. Sobrevivi.",
                "A Forja Sagrada não está apagada — está esperando. Ela reconhece quem é digno.",
                "Aprendi 12 segredos de forja que nenhum humano conhece. Morrerei com eles... a menos que prove ser digno.",
                "O Dragão de Magma guarda as memórias da minha civilização. Quando você o derrotar... escute o rugido. Há palavras lá.",
                "Fiz a espada mais perfeita do mundo uma vez. Então a destruí. Não havia ninguém digno de empunhá-la.",
            ]
        },
    ],
    50: [
        {
            "name": "Ex-Entidade do Vazio",
            "role": "Ser Primordial Aposentado",
            "emoji": "🌌",
            "dialogues": [
                "Existia antes do universo. Decidi me tornar mortal para entender o que é ser frágil. Arrependo? Às vezes.",
                "O Senhor das Sombras é meu irmão mais novo. Ele nunca entendeu que o vazio não é casa — é solidão.",
                "Cada pensamento que você tem ecoa no Abismo por eternidades. Pense com cuidado.",
                "Vi o fim do universo em uma visão. Não era trágico. Era... tranquilo. Como dormir.",
                "Se quiser falar com os mortos, o Abismo tem um bairro deles. Mas eles cobram memórias como entrada.",
            ]
        },
    ],
    60: [
        {
            "name": "Alma de Herói",
            "role": "Espírito de Aventureiro Lendário",
            "emoji": "⭐",
            "dialogues": [
                "Cheguei onde você está. Passei pelo teste. O Imperador me perguntou o que eu mais queria. Disse 'nada'. E recebi tudo.",
                "O Trono não é um lugar. É um estado de ser. Você não SOBE ao Trono. Você SE TORNA o Trono.",
                "Meu maior erro foi achar que chegaria aqui mais forte. Na verdade, cheguei mais humano.",
                "Há segredos além do Trono que nem eu conheço. E estou aqui há 1.000 anos.",
                "O Imperador não quer ser derrotado. Quer ser compreendido. Há diferença.",
            ]
        },
        {
            "name": "Arquiteto do Cosmos",
            "role": "Construtor do Universo",
            "emoji": "🌌",
            "dialogues": [
                "Construí este universo peça por peça. Não é perfeito. Nenhuma criação é.",
                "Coloquei propositalmente as imperfeições. Sem elas, não haveria heróis — não haveria história.",
                "Você chegou ao fim do mapa. Mas o mapa é menor que o território.",
                "Vejo tudo que foi, é e será. E ainda assim, você me surpreende.",
                "Quando terminar aqui, se quiser, posso mostrar o que existe além deste universo. A escolha é sua.",
            ]
        },
    ]
}

# ================= NOVOS EVENTS EXPANDIDOS POR REINO =================
WORLD_EVENTS_EXTRA = {
    1: [
        "Um mercador suspeito oferece uma 'maçã encantada' de graça. Você aceita?",
        "Uma borboleta gigante te guia até um baú escondido no campo.",
        "Você escorrega em um slime invisível e cai no chão. Constrangedor.",
        "Uma velha anuncia que você é 'o escolhido'. Mas ela diz isso para todos.",
        "Um slime se apega à sua bota e não larga. Parece estar te adotando.",
        "Você encontra um mapa antigo rasgado pela metade.",
        "Uma fada minúscula te cutuca insistentemente apontando para uma direção.",
        "O vento traz o cheiro de uma batalha recente. Sangue e magia.",
        "Você tropeça em uma pedra que ressoa como um sino ao ser tocada.",
        "Um corvo negro te segue por uma hora e depois desaparece.",
        "Uma criança te pede para desenhar um mapa. Você descobre um local novo.",
        "O chão balança levemente — algo grande se move sob a terra.",
        "Você encontra as cinzas de uma fogueira recente com símbolos ao redor.",
        "Uma voz na sua cabeça diz 'olhe para cima'. No céu, forma de dragão nas nuvens.",
        "Um aventureiro mais experiente te dá um conselho vago mas profundo.",
        "Você acha um espelho partido. Reflete algo diferente do que está na sua frente.",
        "Uma erva rara brilha ao seu pé. Parece útil para poções.",
        "Uma estátua quebrada aponta na direção de uma dungeon desconhecida.",
        "Uma criança corre até você com uma mensagem: 'Não confie em ninguém de capuz hoje'.",
        "O céu fica vermelho por um instante. O narrador não explica por quê.",
    ],
    10: [
        "A floresta para completamente. Nenhum som. Por 30 segundos. Então retorna.",
        "Você ouve uma melodia linda vindo de lugar nenhum. Faz você sentir saudade de algo que nunca teve.",
        "Musgo cresce visivelmente enquanto você observa. A floresta está respondendo a você.",
        "Uma aranha do tamanho da sua cabeça te olha fixamente. Depois vai embora. Sem atacar.",
        "Você encontra uma árvore com nomes gravados. O último nome é o seu.",
        "Folhas caem em padrão perfeitamente geométrico ao seu redor.",
        "Um ent jovem te estuda de longe com curiosidade antes de recuar.",
        "Você descobre uma cabana abandonada com comida ainda fresca.",
        "Bioluminescência ilumina seu caminho na escuridão da floresta.",
        "Um espírito triste te pede para entregar uma mensagem a alguém já morto.",
        "A floresta parece menor do que deveria. Como se algo a comprimisse.",
        "Você encontra penas negras formando uma seta no chão.",
        "Um riacho subterrâneo burburinha com algo que parece palavras.",
        "Uma formação de cogumelos forma um círculo perfeito. Centro parece mais escuro.",
        "Você acha armadilha de caçador humano. Para que tipo de criatura?",
        "Frutos estranhos caem de uma árvore ao seu passar. Cheiram bem demais.",
        "Uma névoa roxa surge do chão e desaparece em segundos.",
        "Você ouve risadas de crianças mas não há ninguém.",
        "Uma serpente enorme cruza seu caminho sem te atacar. Ela carrega algo na boca.",
        "O sol entra pela copa das árvores formando a silhueta de uma espada no chão.",
    ],
}

# ================= QUESTS EXTRAS COM MUITO XP =================
QUESTS_EXTRA = {
    1: [
        {
            "id": "campos_bonus_001",
            "name": "⭐ O Grande Teste dos Campos",
            "description": "O Sábio Pell te desafia: cace 10 monstros diferentes, colete 10 recursos e explore 5 vezes — tudo para provar que é um aventureiro completo.",
            "type": "individual", "objective": "hunt", "target": None,
            "count": 10, "reward_xp": 3000, "reward_coins": 100, "reward_item": "Poção de XP Maior",
            "lore": "Pell registra cada herói que passa pelos campos. Poucos completam o teste. Você vai tentar?",
            "npc": "Sábio Pell", "difficulty": "Épico"
        },
    ],
    10: [
        {
            "id": "floresta_bonus_001",
            "name": "🌲 Pacificador da Floresta",
            "description": "Derrote 15 monstros da floresta para reduzir a agressividade das criaturas e restaurar o equilíbrio.",
            "type": "individual", "objective": "hunt", "target": None,
            "count": 15, "reward_xp": 5000, "reward_coins": 80, "reward_item": "Armadura Élfica",
            "lore": "A floresta está em desequilíbrio. Cada monstro que cai restaura um pouco da paz perdida.",
            "npc": "Espírito Ancião Vel", "difficulty": "Muito Difícil"
        },
    ],
    20: [
        {
            "id": "deserto_bonus_001",
            "name": "🏺 Historiador do Deserto",
            "description": "Colete 20 recursos únicos do deserto para o museu ambulante do mercante Ib.",
            "type": "individual", "objective": "collect", "count": 20,
            "reward_xp": 6000, "reward_coins": 60, "reward_item": "Poção de XP Maior",
            "lore": "Ib coleta a história do deserto. Cada artefato é uma memória de civilizações perdidas.",
            "npc": "Mercante Ib", "difficulty": "Épico"
        },
    ],
    30: [
        {
            "id": "gelo_bonus_001",
            "name": "❄️ Conquistador das Alturas",
            "description": "Explore 10 vezes as Montanhas Geladas e descubra todos os segredos que elas escondem.",
            "type": "individual", "objective": "explore", "count": 10,
            "reward_xp": 7000, "reward_coins": 50, "reward_item": "Elixir de XP",
            "lore": "As montanhas revelam seus segredos apenas aos mais persistentes.",
            "npc": "Vidente das Neves", "difficulty": "Muito Difícil"
        },
    ],
    40: [
        {
            "id": "vulcao_bonus_001",
            "name": "🔥 Herdeiro dos Forjadores",
            "description": "Colete 25 recursos do Reino Vulcânico para reconstruir a Forja Sagrada dos anões.",
            "type": "individual", "objective": "collect", "count": 25,
            "reward_xp": 9000, "reward_coins": 40, "reward_item": "Martelo do Trovão",
            "lore": "Krug acredita que você pode restaurar o legado dos forjadores. Prove a ele.",
            "npc": "Anão Sobrevivente Krug", "difficulty": "Lendário"
        },
    ],
    50: [
        {
            "id": "abismo_bonus_001",
            "name": "🌀 Sobrevivente do Vazio",
            "description": "Explore o Abismo Arcano 15 vezes e retorne sempre. A maioria não consegue.",
            "type": "individual", "objective": "explore", "count": 15,
            "reward_xp": 12000, "reward_coins": 30, "reward_item": "Cetro da Eternidade",
            "lore": "A Ex-Entidade do Vazio diz: 'Voltar do Abismo vivo 15 vezes significa que o universo ainda precisa de você.'",
            "npc": "Ex-Entidade do Vazio", "difficulty": "Mítico"
        },
    ],
    60: [
        {
            "id": "celestial_bonus_001",
            "name": "👑 A Saga Completa",
            "description": "Cace 20 guardiões celestiais para provar que chegou ao Trono como lenda viva.",
            "type": "individual", "objective": "hunt", "target": None,
            "count": 20, "reward_xp": 25000, "reward_coins": 20, "reward_item": "Armadura do Primeiro Deus",
            "lore": "A Alma de Herói diz: 'A saga completa de um herói não se mede em batalhas. Se mede em escolhas.'",
            "npc": "Alma de Herói", "difficulty": "Primordial"
        },
    ],
}

# ================= LIVROS DE LORE =================
LORE_BOOKS = {
    1: [
        {
            "title": "📖 Crônicas dos Campos — Vol. I",
            "content": """*Páginas amareladas, mas legíveis...*

**'A Origem dos Sete Reinos'**

No princípio, havia apenas o Vazio — um silêncio perfeito e eterno.
Então, a Primeira Chama surgiu do nada, e com ela nasceu o Mundo.

Os Campos Iniciais foram o primeiro solo a se solidificar das cinzas da criação.
Aqui, os primeiros seres vivos deram seus primeiros passos trêmulos.

Os antigos chamavam este lugar de 'Berço' — pois todo herói, 
independente de sua grandeza futura, começa aqui.

*'O guerreiro mais poderoso que existiu começou matando um slime,'* 
dizia o Sábio Aldren. *'Não se envergonhe do seu começo.'*

— Crônicas dos Campos, escrito pelo Historiador Pell, Ano 1 da Nova Era"""
        },
        {
            "title": "📖 Diário de um Aventureiro",
            "content": """*Rabiscado às pressas em tinta quase seca...*

**Dia 1:**
Cheguei aos Campos. Parece simples demais para ser perigoso.
Estava errado. Um coelho me mordeu.

**Dia 7:**
Encontrei outros aventureiros. Formamos um grupo.
Derrotamos o Slime Rei juntos. Nunca me senti tão vivo.

**Dia 15:**
A Floresta Sombria chama. Dizem que os que entram mudam para sempre.
Vou descobrir por quê.

*— Assinado: 'O Herói Sem Nome', encontrado nos Campos Iniciais*"""
        }
    ],
    10: [
        {
            "title": "📖 Sussurros da Floresta — Tomo Antigo",
            "content": """*Escrito em folhas de árvore, palavras que parecem vivas...*

**'A Floresta que Respira'**

A Floresta Sombria não é apenas uma floresta.
Ela é um ser vivo, consciente, e muito, muito antiga.

O Ent Ancião que habita seu coração tem 3.000 anos de memória.
Ele viu o mundo mudar, viu reinos nascer e morrer.

*Dizem os druidas que quem escuta a floresta com o coração aberto 
pode ouvir ela contar histórias do tempo em que os dragões ainda 
voavam livres sobre todos os reinos.*

Mas cuidado — a floresta também ouve você.
E ela lembra de tudo.

— Coletado pelo Druida Sylvara, Guardiã da Floresta"""
        }
    ],
    20: [
        {
            "title": "📖 Hieróglifos Traduzidos — Fragmento VII",
            "content": """*Tradução de hieróglifos encontrados em uma pirâmide semi-enterrada...*

**'O Testamento do Faraó Kha-Mentu'**

Eu, Kha-Mentu, Faraó da Décima Dinastia, escrevo isto em minha última hora.

Meus sacerdotes me traíram. Eles queriam o Olho de Ra para si mesmos.
Lançaram sobre mim uma maldição: guardar meus próprios tesouros por toda eternidade.

Mas há uma saída. O Olho de Ra ainda pulsa no centro da Grande Pirâmide.
Aquele que o recuperar pode quebrar qualquer maldição.

*Procure o herói que vier depois de mim. Diga-lhe: o segredo está 
onde o sol nunca brilha — mas a verdade sempre ilumina.*

— Kha-Mentu, Faraó Eterno, condenado a aguardar"""
        }
    ],
    30: [
        {
            "title": "📖 Canções do Gelo — Manuscrito",
            "content": """*Escrito em pergaminho congelado, as palavras tremem...*

**'A Balada do Yeti'**

Nem sempre o Yeti foi uma besta selvagem.

Há mil anos, Krom era um guardião gentil das montanhas,
criado pelos Titãs do Gelo para proteger o Cristal do Inverno Eterno.

Então vieram os primeiros humanos, gananciosos e ignorantes.
Eles tentaram roubar o Cristal para vender seu poder.

Krom os deteve — mas algo quebrou dentro dele naquele dia.
O guardião gentil tornou-se a besta que todos temem agora.

*O Cristal do Inverno Eterno ainda está lá, no coração da montanha.
Ainda aguarda um guardião digno.*

— Cantado pelos Bardos das Montanhas, transmitido oralmente por gerações"""
        }
    ],
    40: [
        {
            "title": "📖 Tábuas de Pedra Vulcânica — Transcrição",
            "content": """*Gravado em pedra por mãos que suportaram o calor das chamas...*

**'A Origem do Fogo'**

No segundo dia após a criação do mundo, a Primeira Chama se dividiu.

Uma parte tornou-se o sol.
Outra parte afundou nas profundezas e tornou-se o magma.
A terceira parte... tomou forma. Tornou-se Ignarius.

O Dragão de Magma não é uma criatura — é um elemento.
Tão fundamental quanto água, terra e ar.

*Matar Ignarius não destrói o fogo. Apenas o libera de sua forma.
Mas poucos compreendem isto antes de ser tarde demais.*

— Profeta Ignar, Guardião da Chama Primordial"""
        }
    ],
    50: [
        {
            "title": "📖 Fragmentos do Vazio — Texto Corrompido",
            "content": """*As palavras parecem se mover enquanto você lê...*

**'O Que Existe Antes do Começo'**

[TEXTO PARCIALMENTE ILEGÍVEL]

...antes dos deuses, havia o Vazio...
...o Senhor das Sombras não é o vilão desta história...
...ele apenas quer voltar para casa...
...o 'lar' dele é o nada absoluto...
...e se ele conseguir, tudo que existe...

[TEXTO RASGADO]

...a única forma de detê-lo é mostrar-lhe que a existência...
...vale mais que o silêncio do vazio...

[FIM DO FRAGMENTO]

*Nota da Bibliotecária Spectra: 'Leiam com cuidado. Este texto muda quem o lê.'*"""
        }
    ],
    60: [
        {
            "title": "📖 O Livro do Destino — Página Final",
            "content": """*Este livro parece ter sido escrito para você especificamente...*

**'A Profecia do Herói Final'**

Haverá um dia em que o Trono Celestial receberá um mortal.

Não um deus. Não um anjo. Um ser que começou nos Campos,
que sangrou na Floresta, que queimou no Vulcão,
que sobreviveu ao Abismo — e que chegou aqui.

O Imperador Astral não é um inimigo.
Ele é o último teste antes da ascensão.

*'O verdadeiro poder não é destruir os outros.
É ter o poder de destruir e escolher não fazê-lo.'*

O Trono aguarda.
A história foi escrita.
Apenas você pode decidir como ela termina.

— O Livro do Destino, autor desconhecido, data desconhecida"""
        },
        {
            "title": "📖 Memórias dos Deuses — Tomo Proibido",
            "content": """*As páginas brilham com luz sobrenatural...*

**'O Que os Deuses Temem'**

Os deuses não são imortais. São apenas muito, muito velhos.

O Imperador Astral sabe disso. Por isso ele testa os mortais —
buscando aquele que possa um dia carregá-lo
quando ele mesmo estiver pronto para descansar.

Há segredos que os deuses escondem:
— O Primeiro Deus não criou o universo. Ele *encontrou* ele.
— A morte não é o fim. É uma porta. Mas nem todos sabem abri-la.
— O verdadeiro nome do Vazio é amor. Um amor que consumiu tudo.

*'Se você leu até aqui, você já não é mais o mesmo.'*

— Arquivos da Biblioteca Celestial, acesso nível Divino"""
        },
        {
            "title": "📖 Crônicas da Guerra Primordial",
            "content": """*Escrito em luz solidificada, impossível de destruir...*

**'A Batalha Antes do Tempo'**

Antes que o universo existisse, houve uma guerra.

De um lado: a Luz Primordial, que queria existência, forma, vida.
Do outro: o Vazio Eterno, que queria silêncio, paz, nada.

Eles lutaram por uma eternidade que não tinha nome ainda.

A batalha terminou sem vencedor — ambos exaustos,
fizeram um acordo: criariam algo novo.
Algo que contivesse os dois.

Chamaram isso de *Universo*.

E plantaram dentro de cada ser vivo uma centelha de cada lado.
É por isso que todo ser carrega tanto amor quanto destruição.

*A guerra não terminou. Apenas mudou de palco.*

— Fragmento encontrado no 'Além do Trono'"""
        }
    ]
}

# ================= LIVROS DE LORE EXTRAS (por mundo) =================
LORE_BOOKS_EXTRA = {
    1: [
        {
            "title": "📖 O Bestiário dos Campos — Capítulo I",
            "content": """*Ilustrações detalhadas e notas à margem...*

**'Sobre os Slimes'**

Os slimes são os seres mais mal compreendidos dos Campos.

Eles não são criaturas — são memórias.
Cada slime é formado quando uma emoção humana intensa é derramada no solo:
lágrimas, sangue, esperança, desespero.

O Slime Rei é formado das memórias de centenas de heróis que falharam.
Ele não é mal. Ele é *acumulado*.

*'Olhe nos olhos de um slime. Você pode ver algo familiar?'*

Por isso matar um slime é sempre um pouco triste.
Você está apagando uma memória do mundo.

— Naturalista Pell, Campos Iniciais, Ano 23"""
        },
        {
            "title": "📖 Cartas Para Ninguém — Vol. 1",
            "content": """*Cartas sem destinatário, amarradas com fita vermelha...*

**Carta #1:**
*'Para quem vier depois de mim,'*

Eu estava onde você está agora. Com medo, sem saber nada.
Matei meu primeiro slime e quase chorei. Parece ridículo agora.

Saiba: cada derrota é um professor rigoroso.
Cada cicatriz é um capítulo da sua história.

Quando você chegar ao Trono Celestial
(e você chegará, se persistir),
olhe para trás e lembre do primeiro slime.

*'Quem ri do começo humilde não entende de grandeza.'*

Com amor,
— Um aventureiro que passou por aqui antes"""
        }
    ],
    10: [
        {
            "title": "📖 O Grimório da Floresta — Página Arrancada",
            "content": """*Manchas de seiva verde nas bordas rasgadas...*

**'Os Segredos das Trevas Verdes'**

A Floresta Sombria tem três camadas.

**A Primeira:** onde os aventureiros entram. Com goblins, aranhas, perigos visíveis.
**A Segunda:** onde apenas os experientes chegam. Os espíritos moram aqui.
**A Terceira:** onde ninguém volta. Lá fica o coração da floresta.

No coração existe uma árvore tão antiga que seus galhos tocam outros mundos.
Seus frutos concedem visões do passado e do futuro.

*Um fruto faz você ver tudo que já foi.*
*O outro, tudo que ainda será.*
*O terceiro... ninguém sabe. Ninguém comeu e se lembrou.*

— Druida Vel, desaparecido"""
        },
        {
            "title": "📖 Diário da Druida Sylvara — Entradas Escolhidas",
            "content": """*Escrito com tinta feita de seiva e terra...*

**Entrada 47:**
O Ent Ancião falou comigo hoje. Em 30 anos, é a segunda vez.

Ele disse: *'A floresta sangra.'*

Perguntei por quê. Ele disse: *'Porque os humanos esqueceram como ouvir.'*

Fiquei em silêncio por um longo tempo.

Depois ele disse algo que não consigo parar de pensar:
*'Não temo o fogo, nem o machado. Temo o esquecimento.
Porque uma árvore que ninguém lembra jamais existiu.'*

**Entrada 89:**
Hoje um aventureiro perguntou se a floresta é perigosa.
Respondi: *'A floresta é justa. Ela trata você como você a trata.'*
Ele não entendeu. Talvez entenda quando sair.

— Sylvara, Guardiã"""
        }
    ],
    20: [
        {
            "title": "📖 O Papiro da Eternidade — Tradução Incompleta",
            "content": """*Caracteres dourados sobre papiro preservado por magia...*

**'O Ciclo das Eras'**

O Deserto das Almas não é um deserto natural.

Há 5.000 anos, era um jardim. O mais belo do mundo.
Havia rios, florestas, cidades de ouro e cristal.

Então veio a Maldição do Faraó Kha-Mentu —
mas não como punição. Como *proteção*.

Kha-Mentu transformou o paraíso em deserto
para que os invasores não desejassem mais conquistá-lo.
Sacrificou a beleza para salvar os segredos.

*'O maior ato de amor pode parecer destruição para quem não entende.'*

Sob as areias ainda dormem as maravilhas do jardim original.
Esperando por alguém digno de acordá-las.

— Fragmento da Biblioteca do Faraó, Nível -7"""
        },
        {
            "title": "📖 O Livro dos Espíritos — Capítulo das Múmias",
            "content": """*Páginas que parecem sugar o calor das suas mãos...*

**'Por Que os Mortos Caminham'**

As múmias não são monstros. São guardas.

Cada múmia foi uma pessoa real que, em vida,
jurou proteger algo até o fim dos tempos.
Quando morreram, o juramento continuou.

O problema é que elas esqueceram o quê estão protegendo.
Lembram apenas do juramento.

*'Uma múmia que lembra o que protege se ajoelha diante do digno.
Uma múmia que esqueceu ataca tudo que se move.'*

Se você encontrar uma múmia que para e te olha sem atacar —
ela está lembrando. Não a interrompa.

Talvez ela encontre o que procura em você.

— Nefertiri, Guardiã dos Conhecimentos"""
        }
    ],
    30: [
        {
            "title": "📖 Sagas do Gelo — Volume III",
            "content": """*Pergaminho enrijecido pelo frio, mas legível...*

**'Os Titãs do Gelo'**

Antes dos humanos existirem, os Titãs do Gelo governavam estas montanhas.

Eram seres de 30 metros de altura, feitos de cristal e vento,
com memórias que se estendiam por eras geológicas.

Eles não lutavam. Criavam.
Cada Titã era responsável por uma lei da natureza:
— Boreas: o frio
— Glacius: o tempo (no sentido meteorológico)
— Permafrost: a permanência das coisas

Os humanos os confundiram com inimigos e atacaram.
Os Titãs, confusos com tamanha agressividade em seres tão pequenos,
*recuaram*.

Eles ainda estão aqui. Apenas menores. Esperando ser compreendidos.
O Yeti Colossal é um eco da memória deles.

— Bjorn, Anciãos das Montanhas"""
        },
        {
            "title": "📖 O Cristal do Inverno — Lenda Completa",
            "content": """*Glifos rúnicos que parecem pulsar com frio azul...*

**'O Segredo nas Profundezas'**

O Cristal do Inverno Eterno não é apenas uma joia.

É um arquivo. Um registro de tudo que já existiu e morreu no frio.
Cada criatura que morreu nestas montanhas tem sua memória guardada ali.

Por isso os Titãs do Gelo o protegiam com tanto cuidado.
Era a *biblioteca da morte* deles.

O Yeti Colossal, Krom, sente cada memória armazenada
como se fossem suas próprias. Sente a dor de cada ser.
É por isso que está sempre em sofrimento.

*'Quem derrotar Krom com compaixão, não com ódio,
pode ouvir ele sussurrar o nome do ser que mais sente falta.'*

Dizem que é sempre o mesmo nome.
Mas ninguém que ouviu jamais revelou qual é.

— Fragmento, Fortaleza Permafrost"""
        }
    ],
    40: [
        {
            "title": "📖 O Códice do Fogo — Primeira Revelação",
            "content": """*Gravado em obsidiana, legível apenas à luz do fogo...*

**'A Profecia de Ignarius'**

No dia em que o último vulcão se apagar,
o dragão retornará ao fogo primordial.

Mas antes disso, ele testará os guerreiros:
*'Apenas quem sobreviver ao fogo sem se tornar cinza
merece carregar a Chama Original em seu coração.'*

A Chama Original não é uma arma. É uma responsabilidade.
Quem a carrega sente o peso de tudo que foi criado com fogo:
cada estrela, cada vida, cada sonho que aqueceu alguém na noite fria.

Os Anões que forjaram as primeiras armas dos deuses carregavam essa chama.
Por isso suas criações eram imortais.

*'Forja com fogo do coração, não das mãos.'*

— Profeta Ignar, última visão antes de se tornar cinzas"""
        },
        {
            "title": "📖 Memórias de Lava — Registro Vulcânico",
            "content": """*Palavras que parecem ainda quentes ao toque...*

**'Civilização Antes do Fogo'**

Poucos sabem que o Reino Vulcânico foi habitado por uma civilização avançada.

Os Forjadores — assim eram chamados — dominavam a metalurgia mágica.
Criavam objetos que tinham *alma*: que sentiam, que pensavam, que escolhiam seus donos.

Quando Ignarius despertou pela última vez, eles não fugiram.
Fizeram uma escolha coletiva: fundir-se com o dragão.
Voluntariamente.

Agora Ignarius carrega dentro de si as memórias de toda uma civilização.
Cada rugido é uma canção em idioma extinto.
Cada chama é um nome que não existe mais.

*'Quando você derrota Ignarius, você libera as almas presas nele.
Não é uma batalha. É um funeral que durou 1.000 anos.'*

— Doran, Mestre-Ferreiro, herdeiro da tradição"""
        }
    ],
    50: [
        {
            "title": "📖 O Tratado do Vazio — Tradução Proibida",
            "content": """*As palavras se movem enquanto você as lê. Literalmente.*

**'O Que Existe Antes do Nada'**

Filósofos debatem há milênios sobre o que existe após a morte.
Poucos perguntam o que existia antes do nascimento.

A resposta é o Abismo Arcano.

Cada alma que nasce vem do Abismo.
Cada alma que morre retorna ao Abismo.
O Senhor das Sombras não é um vilão — é um *administrador*.

Ele cuida das almas em trânsito.
Ordena o caos entre o antes e o depois.

O problema é que há almas que não querem ir embora.
Que querem ficar no Abismo para sempre.
E o Senhor das Sombras não tem autoridade para forçá-las.

*'Todo monstro que você enfrenta no Abismo
era uma vez uma alma que tinha medo de seguir em frente.'*

— Spectra, Bibliotecária do Abismo"""
        },
        {
            "title": "📖 Cartas do Arquimago Zephyr — Correspondência Final",
            "content": """*Letras que brilham e se apagam alternadamente...*

**Para meu sucessor, seja você quem for:**

Passei 200 anos estudando o Abismo Arcano.
Aprendi uma coisa: quanto mais você sabe, mais você entende que não sabe nada.

As entidades do Vazio não são más.
São *antigas*. E antigas demais para entender coisas novas como você.

Quando encontrares o Senhor das Sombras,
não o trate como inimigo.
Trate-o como um ser que está aqui há muito mais tempo que você
e está muito, muito cansado.

Às vezes o maior ato de compaixão é dar descanso a quem não pode morrer.

*'O verdadeiro poder do Abismo não é destruição. É transformação.'*

Com esperança no futuro,
Arquimago Zephyr
P.S.: Meu livro de magias está escondido na Dimensão Invertida. Você vai precisar."""
        }
    ]
}

# ================= NPCs POR CIDADE =================
CITY_NPCS = {
    1: {
        "city_name": "🏘️ Vila dos Primeiros Passos",
        "npcs": [
            {
                "name": "Aldeão Theron",
                "role": "Fazendeiro",
                "emoji": "👨‍🌾",
                "dialogues": [
                    "Bem-vindo, viajante! Estes campos parecem simples, mas escondem mais segredos do que imaginamos.",
                    "Meu avô dizia que o primeiro Slime a aparecer nestes campos nasceu de uma lágrima do céu.",
                    "Você parece forte. Talvez pudesse ajudar com a praga dos ratos? Os Campos precisam de heróis como você.",
                    "Dizem que nas noites de lua cheia, o Slime Rei aparece no centro do campo. Ninguém voltou para confirmar... ainda."
                ]
            },
            {
                "name": "Curandeira Elara",
                "role": "Curandeira da Vila",
                "emoji": "👩‍⚕️",
                "dialogues": [
                    "As ervas destes campos têm propriedades mágicas. Cada planta guarda uma história.",
                    "Aprendi a curar com minha mãe, que aprendeu com a sua. A arte de curar é tão antiga quanto a dor.",
                    "Cuidado com as vespas gigantes ao norte. Seu veneno não mata rapidamente, mas faz você desejar que matasse.",
                    "Se precisar de uma poção, posso preparar algo... mas os ingredientes são raros por aqui."
                ]
            },
            {
                "name": "Capitão Aldric",
                "role": "Guarda da Vila",
                "emoji": "💂",
                "dialogues": [
                    "Fui aventureiro antes de ser guarda. Aprendi que trabalho em equipe salva mais vidas do que força individual.",
                    "O Slime Rei foi derrotado uma vez, há 50 anos. Mas os slimes absorvem a magia da terra e renascem.",
                    "Recrute companheiros se quiser enfrentar os grandes perigos. Nenhum herói conquista o mundo sozinho.",
                    "Minha espada está enferrujada agora. Mas já matei um boss com ela. Os tempos bons..."
                ]
            }
        ]
    },
    10: {
        "city_name": "🌲 Acampamento das Sombras",
        "npcs": [
            {
                "name": "Druida Sylvara",
                "role": "Guardiã da Floresta",
                "emoji": "🧙‍♀️",
                "dialogues": [
                    "A floresta fala para aqueles que sabem ouvir. Você consegue ouvi-la?",
                    "O Ent Ancião está inquieto. Algo perturba seu sono milenar. Temo o que pode acontecer se ele despertar com raiva.",
                    "Cada árvore aqui tem um nome. Eu os conheço todos. São minha família.",
                    "Os goblins desta floresta não são naturalmente maus. Algo os corrompeu. Descubra o que é e talvez encontre paz."
                ]
            },
            {
                "name": "Mercador Brynn",
                "role": "Comerciante Errante",
                "emoji": "🧔",
                "dialogues": [
                    "Comércio é a única linguagem universal. Até monstros têm preço.",
                    "Passei por aqui há um mês. A floresta estava diferente. Mais... viva. Não da forma boa.",
                    "Procuro a Teia Mágica das Aranhas Gigantes. Pago bem. Muito bem.",
                    "Ei, você não parece daqui. De onde veio? Dos Campos? Ah, a nostalgia..."
                ]
            }
        ]
    },
    20: {
        "city_name": "🏜️ Oásis de Amun",
        "npcs": [
            {
                "name": "Sábia Nefertiri",
                "role": "Guardiã dos Conhecimentos Antigos",
                "emoji": "👑",
                "dialogues": [
                    "Os hieróglifos nas pirâmides não são decoração. São advertências. Poucos tomam o cuidado de lê-las.",
                    "O Faraó Kha-Mentu não era um vilão. Era um rei traído. Há diferença.",
                    "Esta areia foi mar profundo uma vez. Tudo muda. Tudo passa. Até o deserto.",
                    "Você busca riquezas? As maiores riquezas deste deserto são os conhecimentos enterrados junto com os mortos."
                ]
            },
            {
                "name": "Nômade Hassan",
                "role": "Guia do Deserto",
                "emoji": "🧕",
                "dialogues": [
                    "O deserto testa cada viajante de forma diferente. Ele sabe o que você mais teme.",
                    "Minha família guia viajantes nestas areias há sete gerações. Perdemos apenas três. Não foi culpa nossa.",
                    "Há uma tempestade chegando. De areia ou de destino, não sei dizer. Mas algo está por vir.",
                    "O escorpião que te pica é o mesmo que te salva do veneno de outro. A vida no deserto é assim."
                ]
            }
        ]
    },
    30: {
        "city_name": "❄️ Fortaleza Permafrost",
        "npcs": [
            {
                "name": "Ancião da Montanha Bjorn",
                "role": "Líder Tribal",
                "emoji": "🧓",
                "dialogues": [
                    "Vivi 80 invernos nestas montanhas. O frio não é inimigo — é professor.",
                    "O Yeti não é um monstro. É um guardião mal compreendido. Mas compreender não significa que ele não vai te matar.",
                    "Há uma passagem secreta através das montanhas. Apenas os dignos a encontram. Você tem o que é necessário?",
                    "Meu pai viu os Titãs do Gelo uma vez. Disse que eram lindos e aterrorizantes ao mesmo tempo."
                ]
            },
            {
                "name": "Ferreiro Helga",
                "role": "Ferreria das Montanhas",
                "emoji": "⚒️",
                "dialogues": [
                    "Armas feitas com cristal de gelo nunca enferrujam. Nunca quebram. Nunca esquecem o sangue que derramaram.",
                    "Trabalhei para reis. Trabalhei para heróis. Nenhum deles agradeceu como você agradece com moedas.",
                    "O segredo de uma boa armadura não é a dureza. É a flexibilidade. Como a vida.",
                    "Preciso de mais cristais de gelo. Os das profundezas. Os outros não têm poder suficiente."
                ]
            }
        ]
    },
    40: {
        "city_name": "🌋 Cidadela Cinzenta",
        "npcs": [
            {
                "name": "Profeta Ignar",
                "role": "Profeta do Fogo",
                "emoji": "🔥",
                "dialogues": [
                    "O fogo não destrói. Transforma. Há diferença fundamental entre os dois.",
                    "Ignarius desperta a cada geração para testar se a humanidade evoluiu. Ela nunca evolui.",
                    "Vejo em suas chamas um destino extraordinário. Ou uma morte extraordinária. Difícil distinguir.",
                    "A Forja Sagrada é real. Eu a vi. Uma vez. Durou um segundo que pareceu uma eternidade."
                ]
            },
            {
                "name": "Anão-Mestre Doran",
                "role": "Mestre Ferreiro Divino",
                "emoji": "⚙️",
                "dialogues": [
                    "Em 300 anos de forja, nunca criei algo que não pudesse ser melhorado. Incluindo eu mesmo.",
                    "As melhores armas têm nomes. Você saberia como nomear a sua?",
                    "A Forja Sagrada foi criada pelos próprios deuses. Reacendê-la... bem. Que coisa seria essa.",
                    "Anões não temem a morte. Tememos morrer antes de terminar nossa obra-prima."
                ]
            }
        ]
    },
    50: {
        "city_name": "🌌 Torre do Conhecimento Perdido",
        "npcs": [
            {
                "name": "Arquimago Zephyr",
                "role": "Arquimago do Abismo",
                "emoji": "🧙",
                "dialogues": [
                    "A magia não é poder. É responsabilidade. O poder vem da sabedoria de quando não usar a magia.",
                    "Estudei o Senhor das Sombras por 200 anos. Quanto mais entendo, mais temo. E mais o compreendo.",
                    "O Abismo Arcano distorce a realidade, mas também revela verdades que a realidade normal esconde.",
                    "Você chegou até aqui. Isso significa que está pronto — ou é inconsciente demais para saber que não está."
                ]
            },
            {
                "name": "Bibliotecária Spectra",
                "role": "Guardiã dos Tomos Proibidos",
                "emoji": "📚",
                "dialogues": [
                    "Cada livro proibido foi proibido por uma razão. Geralmente por pessoas que queriam o conhecimento só para si.",
                    "Li um texto que descrevia o fim do universo. Depois disso, o chá nunca mais teve o mesmo gosto.",
                    "Conhecimento não é perigoso. O que fazemos com ele é que pode ser.",
                    "Procura algum livro em especial? Tenho... categorias especiais. Para visitantes especiais."
                ]
            }
        ]
    },
    60: {
        "city_name": "👑 Antecâmara do Trono",
        "npcs": [
            {
                "name": "Guardião Estelar Auron",
                "role": "Guardião do Trono Celestial",
                "emoji": "⚜️",
                "dialogues": [
                    "Poucos chegam até aqui. Menos ainda estão prontos para o que vem a seguir.",
                    "O Imperador Astral conhece seu nome desde o dia em que você nasceu. Ele esteve esperando.",
                    "Não venho aqui para dissuadi-lo. Venho para honrar sua jornada. O que você fez foi extraordinário.",
                    "O Trono Celestial não é um lugar. É um estado de ser. Você está se tornando algo além de mortal."
                ]
            },
            {
                "name": "Alma de Herói Lendário",
                "role": "Espírito dos Que Vieram Antes",
                "emoji": "👻",
                "dialogues": [
                    "Cheguei aqui antes de você. Falhei. Mas minha falha abriu o caminho para o seu sucesso.",
                    "Não tenho arrependimentos. Cada escolha que fiz me trouxe até aqui — mesmo depois da morte.",
                    "O Imperador... não é o que parece. Esteja preparado para a surpresa de sua vida.",
                    "Lute bem. Lute com honra. E quando terminar — não esqueça de onde veio."
                ]
            }
        ]
    }
}

# ================= MUNDOS E EVENTOS =================
WORLDS = {
    1: {
        "name": "🌱 Campos Iniciais",
        "emoji": "🌱",
        "xp_loss_multiplier": 0.3,
        "monsters": {
            "Slime": {"xp": (10, 20), "hp": 30, "atk": 5, "coins": (1, 3)},
            "Rato Selvagem": {"xp": (12, 22), "hp": 25, "atk": 7, "coins": (1, 4)},
            "Coelho Raivoso": {"xp": (11, 21), "hp": 20, "atk": 6, "coins": (1, 3)},
            "Javali Jovem": {"xp": (13, 23), "hp": 35, "atk": 8, "coins": (2, 5)},
            "Vespa Gigante": {"xp": (12, 22), "hp": 22, "atk": 7, "coins": (1, 4)}
        },
        "boss": {"name": "Slime Rei", "hp": 150, "atk": 15, "xp": 200, "level": 9, "coins": (15, 30)},
        "resources": ["Pedra fraca", "Grama mágica", "Couro de rato", "Flor silvestre", "Mel selvagem"],
        "dungeons": [
            {"name": "Caverna dos Slimes", "level": 1, "boss": "Slime Ancião"},
            {"name": "Toca dos Ratos", "level": 2, "boss": "Rato Rei"},
            {"name": "Ninho de Vespas", "level": 3, "boss": "Vespa Rainha"}
        ],
        "secret_dungeons": [
            {"name": "🕳️ Gruta Esquecida", "level": 1, "boss": "Guardião Primordial dos Campos", "secret": True},
            {"name": "🌀 Buraco no Tecido da Realidade", "level": 2, "boss": "Anomalia Viva", "secret": True}
        ],
        "events": [
            "Você encontra um riacho cristalino. A água brilha sob o sol.",
            "Um bando de pássaros voa sobre você, cantando melodias antigas.",
            "Você tropeça em uma pedra e cai de cara no chão.",
            "Uma borboleta dourada pousa em seu ombro por um instante.",
            "O vento carrega o aroma de flores silvestres.",
            "Você ouve risadas ao longe, mas não vê ninguém.",
            "Pegadas estranhas marcam o solo à sua frente.",
            "Uma névoa suave cobre o campo por alguns momentos.",
            "Você encontra um velho cajado abandonado no caminho.",
            "Um arco-íris surge após uma chuva rápida.",
            "Você pisa em um espinho e sente uma dor aguda.",
            "Uma placa enferrujada aponta para direções desconhecidas.",
            "Você encontra moedas espalhadas pelo chão.",
            "Um esquilo rouba sua comida e foge para uma árvore.",
            "Você sente uma presença te observando entre a grama alta.",
            "Uma criança perdida pede ajuda para encontrar o caminho.",
            "Você encontra um diário rasgado com histórias antigas.",
            "O sol se põe, pintando o céu de laranja e roxo.",
            "Você encontra uma fonte antiga com água mágica.",
            "Um mercador errante oferece itens misteriosos.",
            "Você ouve o som de uma batalha ao longe.",
            "Pegadas de sangue levam a uma caverna escura."
        ]
    },
    10: {
        "name": "🌲 Floresta Sombria",
        "emoji": "🌲",
        "xp_loss_multiplier": 0.5,
        "monsters": {
            "Goblin": {"xp": (25, 40), "hp": 60, "atk": 12, "coins": (3, 8)},
            "Lobo Negro": {"xp": (28, 45), "hp": 70, "atk": 15, "coins": (4, 9)},
            "Aranha Gigante": {"xp": (30, 43), "hp": 65, "atk": 14, "coins": (3, 8)},
            "Ogro Menor": {"xp": (32, 47), "hp": 80, "atk": 16, "coins": (5, 10)},
            "Espectro Florestal": {"xp": (29, 44), "hp": 55, "atk": 13, "coins": (4, 9)}
        },
        "boss": {"name": "Ent Ancião", "hp": 300, "atk": 25, "xp": 350, "level": 19, "coins": (25, 50)},
        "resources": ["Madeira escura", "Ervas raras", "Pele de lobo", "Teia mágica", "Musgo brilhante"],
        "dungeons": [
            {"name": "Covil dos Goblins", "level": 4, "boss": "Chefe Goblin"},
            {"name": "Ninho de Aranhas", "level": 5, "boss": "Aranha Rainha"},
            {"name": "Caverna do Ogro", "level": 6, "boss": "Ogro Cruel"}
        ],
        "secret_dungeons": [
            {"name": "🌑 Floresta Invertida", "level": 4, "boss": "Reflexo Sombrio", "secret": True},
            {"name": "🍄 Reino dos Cogumelos", "level": 5, "boss": "Rei Fúngico", "secret": True}
        ],
        "events": [
            "Galhos se movem sozinhos ao seu redor, como se estivessem vivos.",
            "Você ouve sussurros entre as árvores, mas não entende as palavras.",
            "Uma coruja de olhos vermelhos te observa de um galho alto.",
            "Raízes tentam prender seus pés enquanto você caminha.",
            "Você encontra um círculo de cogumelos brilhantes.",
            "Neblina densa obscurece sua visão por alguns minutos.",
            "Um veado fantasmagórico atravessa seu caminho e desaparece.",
            "Você tropeça e cai em um buraco coberto de folhas.",
            "Luzes misteriosas dançam entre as árvores.",
            "Você encontra um altar antigo coberto de musgo.",
            "Corvos negros grasnam alto, como se estivessem te alertando.",
            "Uma árvore cai perto de você com um estrondo.",
            "Você encontra marcas de garras profundas em um tronco.",
            "Um caminho de pétalas negras aparece misteriosamente.",
            "Você ouve o choro de uma criança, mas não encontra ninguém.",
            "Aranhas gigantes tecem teias bloqueando seu caminho.",
            "Você encontra um esqueleto segurando um mapa antigo.",
            "A lua cheia ilumina clareiras entre as árvores.",
            "Você encontra uma casa abandonada com a porta entreaberta.",
            "Olhos brilhantes te observam da escuridão.",
            "Você sente algo te seguindo, mas ao olhar não vê nada.",
            "Um portal de energia aparece brevemente e desaparece."
        ]
    },
    20: {
        "name": "🏜️ Deserto das Almas",
        "emoji": "🏜️",
        "xp_loss_multiplier": 0.7,
        "monsters": {
            "Escorpião Gigante": {"xp": (40, 60), "hp": 100, "atk": 20, "coins": (5, 12)},
            "Múmia": {"xp": (45, 65), "hp": 120, "atk": 22, "coins": (6, 13)},
            "Serpente de Areia": {"xp": (43, 63), "hp": 110, "atk": 21, "coins": (5, 12)},
            "Guardião de Tumba": {"xp": (47, 67), "hp": 130, "atk": 24, "coins": (7, 14)},
            "Espírito do Deserto": {"xp": (44, 64), "hp": 105, "atk": 20, "coins": (5, 12)}
        },
        "boss": {"name": "Faraó Amaldiçoado", "hp": 500, "atk": 35, "xp": 550, "level": 29, "coins": (40, 80)},
        "resources": ["Areia mágica", "Ossos antigos", "Vendas místicas", "Escaravelho dourado", "Papiro antigo"],
        "dungeons": [
            {"name": "Pirâmide Perdida", "level": 7, "boss": "Faraó Esquecido"},
            {"name": "Tumba dos Reis", "level": 8, "boss": "Anúbis Menor"},
            {"name": "Templo Subterrâneo", "level": 9, "boss": "Esfinge Guardiã"}
        ],
        "secret_dungeons": [
            {"name": "⭐ Oásis do Tempo Invertido", "level": 7, "boss": "Guardião do Paradoxo", "secret": True},
            {"name": "🏺 Catacumba dos Faraós Esquecidos", "level": 8, "boss": "Faraó Primordial", "secret": True}
        ],
        "events": [
            "Uma tempestade de areia surge do nada, cegando você temporariamente.",
            "Você afunda na areia movediça e luta para sair.",
            "Miragens de oásis aparecem ao longe, tentando te enganar.",
            "Você encontra uma pirâmide semi-enterrada na areia.",
            "Hieróglifos brilhantes aparecem nas dunas ao seu redor.",
            "Um escorpião gigante emerge da areia perto de você.",
            "Você encontra um sarcófago aberto e vazio.",
            "O sol escaldante te deixa exausto e sedento.",
            "Você ouve cânticos ancestrais vindos das dunas.",
            "Uma caravana de espíritos passa por você sem te notar.",
            "Você encontra joias espalhadas entre ossos antigos.",
            "Um redemoinho de areia forma uma figura humanóide.",
            "Você cai em uma armadilha antiga cheia de flechas.",
            "Marcas de antigas batalhas cobrem as ruínas ao redor.",
            "A lua ilumina hieróglifos que contam histórias perdidas.",
            "Você encontra um oásis real com água fresca.",
            "Serpentes de areia deslizam rapidamente ao seu redor.",
            "Você vê vultos de múmias caminhando ao longe.",
            "Uma maldição antiga faz você sentir fraqueza.",
            "Você encontra um amuleto enterrado na areia.",
            "Templos subterrâneos são revelados por ventos fortes.",
            "Você ouve o rugido de algo gigantesco sob a areia."
        ]
    },
    30: {
        "name": "❄️ Montanhas Geladas",
        "emoji": "❄️",
        "xp_loss_multiplier": 0.9,
        "monsters": {
            "Lobo de Gelo": {"xp": (60, 80), "hp": 150, "atk": 28, "coins": (7, 15)},
            "Golem de Neve": {"xp": (65, 85), "hp": 180, "atk": 30, "coins": (8, 16)},
            "Ogro Glacial": {"xp": (63, 83), "hp": 160, "atk": 29, "coins": (7, 15)},
            "Dragão de Gelo Jovem": {"xp": (70, 90), "hp": 200, "atk": 32, "coins": (10, 18)},
            "Elemental de Gelo": {"xp": (67, 87), "hp": 170, "atk": 31, "coins": (8, 16)}
        },
        "boss": {"name": "Yeti Colossal", "hp": 750, "atk": 45, "xp": 800, "level": 39, "coins": (50, 100)},
        "resources": ["Cristal de gelo", "Minério frio", "Pele de yeti", "Neve eterna", "Gema congelada"],
        "dungeons": [
            {"name": "Caverna Congelada", "level": 10, "boss": "Guardião do Gelo"},
            {"name": "Fortaleza de Gelo", "level": 11, "boss": "Rei do Inverno"},
            {"name": "Abismo Glacial", "level": 12, "boss": "Dragão Ancestral"}
        ],
        "secret_dungeons": [
            {"name": "🌨️ Núcleo do Inverno Eterno", "level": 10, "boss": "Titã do Gelo", "secret": True},
            {"name": "❄️ Palácio de Cristal Perdido", "level": 11, "boss": "Rainha das Neves", "secret": True}
        ],
        "events": [
            "Uma avalanche desce pela montanha em sua direção.",
            "Você escorrega em gelo fino e cai em uma fenda.",
            "O frio intenso congela suas roupas e músculos.",
            "Você encontra um viajante congelado segurando um mapa.",
            "Cristais de gelo cantam melodias com o vento.",
            "Uma tempestade de neve bloqueia completamente sua visão.",
            "Você encontra uma caverna quente com fontes termais.",
            "Pegadas gigantescas estão impressas na neve.",
            "Você ouve rugidos ecoando entre os picos.",
            "Estalactites de gelo caem perigosamente perto de você.",
            "Você encontra um monastério abandonado no topo.",
            "Espíritos congelados aparecem brevemente na nevasca.",
            "Você cai através de neve falsa em uma caverna.",
            "Lobos uivam ao longe sob a lua cheia.",
            "Você encontra equipamentos de expedições antigas.",
            "O vento forma figuras assustadoras com a neve.",
            "Você sente a montanha tremer levemente.",
            "Cristais gigantes emergem do gelo à sua frente.",
            "Você encontra marcas de batalha antigas no gelo.",
            "Uma ponte de gelo quebra sob seus pés.",
            "Você vê uma silhueta gigantesca no topo da montanha.",
            "A temperatura cai drasticamente de repente."
        ]
    },
    40: {
        "name": "🌋 Reino Vulcânico",
        "emoji": "🌋",
        "xp_loss_multiplier": 1.2,
        "monsters": {
            "Salamandra": {"xp": (80, 100), "hp": 200, "atk": 38, "coins": (10, 20)},
            "Demônio de Lava": {"xp": (85, 105), "hp": 230, "atk": 42, "coins": (12, 22)},
            "Elemental de Fogo": {"xp": (83, 103), "hp": 210, "atk": 40, "coins": (11, 21)},
            "Hidra de Magma": {"xp": (90, 110), "hp": 250, "atk": 45, "coins": (13, 23)},
            "Fênix Negra": {"xp": (87, 107), "hp": 220, "atk": 43, "coins": (12, 22)}
        },
        "boss": {"name": "Dragão de Magma", "hp": 1000, "atk": 55, "xp": 1100, "level": 49, "coins": (60, 120)},
        "resources": ["Pedra vulcânica", "Núcleo de fogo", "Escamas de dragão", "Obsidiana pura", "Cinza sagrada"],
        "dungeons": [
            {"name": "Caldeirão de Lava", "level": 13, "boss": "Senhor do Fogo"},
            {"name": "Forja Infernal", "level": 14, "boss": "Titã Flamejante"},
            {"name": "Coração do Vulcão", "level": 15, "boss": "Ifrit Primordial"}
        ],
        "secret_dungeons": [
            {"name": "🔥 Câmara da Chama Original", "level": 13, "boss": "Aspecto do Fogo Primordial", "secret": True},
            {"name": "🌋 Ventre do Vulcão Vivo", "level": 14, "boss": "Espírito do Vulcão", "secret": True}
        ],
        "events": [
            "Lava jorra de uma fissura bem ao seu lado.",
            "O chão racha e revela rios de magma abaixo.",
            "Gases tóxicos sobem de buracos fumegantes.",
            "Você tropeça e quase cai em um poço de lava.",
            "Um gêiser de lava explode próximo a você.",
            "Pedras incandescentes chovem do céu.",
            "Você encontra ruínas de uma civilização antiga queimada.",
            "O calor derrete parcialmente seu equipamento.",
            "Salamandras gigantes nadam livremente na lava.",
            "Você ouve rugidos vindos de cavernas profundas.",
            "Um vulcão ao longe entra em erupção.",
            "Você encontra cristais de fogo pulsantes.",
            "Demônios observam você das sombras flamejantes.",
            "Pontes de pedra desmoronam sob seus pés.",
            "Você vê esqueletos de aventureiros anteriores.",
            "Chamas azuis dançam misteriosamente ao redor.",
            "Você encontra um altar dedicado ao deus do fogo.",
            "A fumaça densa te faz tossir e perder a direção.",
            "Você sente tremores constantes sob seus pés.",
            "Criaturas de magma emergem das profundezas.",
            "Você encontra um ovo de dragão rachado e vazio.",
            "Asas gigantescas bloqueiam brevemente o sol vermelho."
        ]
    },
    50: {
        "name": "🌌 Abismo Arcano",
        "emoji": "🌌",
        "xp_loss_multiplier": 1.5,
        "monsters": {
            "Espectro": {"xp": (100, 130), "hp": 280, "atk": 48, "coins": (12, 22)},
            "Mago Sombrio": {"xp": (105, 135), "hp": 300, "atk": 52, "coins": (14, 24)},
            "Devorador de Almas": {"xp": (103, 133), "hp": 290, "atk": 50, "coins": (13, 23)},
            "Lich": {"xp": (110, 140), "hp": 320, "atk": 55, "coins": (15, 25)},
            "Golem Arcano": {"xp": (107, 137), "hp": 310, "atk": 53, "coins": (14, 24)}
        },
        "boss": {"name": "Senhor das Sombras", "hp": 1500, "atk": 70, "xp": 1600, "level": 59, "coins": (70, 140)},
        "resources": ["Essência arcana", "Fragmento sombrio", "Cristal do vazio", "Poeira estelar", "Runa mística"],
        "dungeons": [
            {"name": "Torre Arcana", "level": 16, "boss": "Arquimago Corrupto"},
            {"name": "Dimensão Sombria", "level": 17, "boss": "Entidade do Vazio"},
            {"name": "Biblioteca Proibida", "level": 18, "boss": "Guardião do Conhecimento"}
        ],
        "secret_dungeons": [
            {"name": "♾️ Loop Temporal Permanente", "level": 16, "boss": "Eco de Si Mesmo", "secret": True},
            {"name": "🌀 Dimensão Invertida", "level": 17, "boss": "Anti-Matéria Viva", "secret": True}
        ],
        "events": [
            "A gravidade inverte e você flutua sem controle.",
            "Portais dimensionais abrem e fecham ao seu redor.",
            "Você vê versões alternativas de si mesmo passando.",
            "O tempo parece congelar por alguns segundos.",
            "Sussurros de milhares de vozes ecoam em sua mente.",
            "Você atravessa uma cortina de energia e sente dor.",
            "Estrelas cadentes atravessam o vazio infinito.",
            "Você encontra fragmentos de realidades destruídas.",
            "Sombras ganham vida e tentam te tocar.",
            "Você vê memórias de pessoas desconhecidas.",
            "A realidade se distorce formando figuras impossíveis.",
            "Você sente sua essência sendo puxada do corpo.",
            "Criaturas do vazio te observam da escuridão.",
            "Você encontra um livro que escreve sozinho.",
            "Pontes de energia aparecem e desaparecem.",
            "Você ouve profecias sobre seu futuro.",
            "Magos mortos oferecem conhecimento proibido.",
            "Você cai em um loop temporal por instantes.",
            "Olhos gigantes se abrem no céu escuro.",
            "Você encontra artefatos de eras esquecidas.",
            "A linha entre sonho e realidade desaparece.",
            "Uma entidade cósmica nota sua presença."
        ]
    },
    60: {
        "name": "👑 Trono Celestial",
        "emoji": "👑",
        "xp_loss_multiplier": 2.0,
        "monsters": {
            "Guardião Celestial": {"xp": (140, 180), "hp": 400, "atk": 65, "coins": (15, 28)},
            "Anjo Caído": {"xp": (145, 185), "hp": 420, "atk": 68, "coins": (16, 30)},
            "Serafim Corrompido": {"xp": (150, 190), "hp": 450, "atk": 70, "coins": (18, 32)},
            "Querubim Guerreiro": {"xp": (155, 195), "hp": 480, "atk": 73, "coins": (19, 34)},
            "Arcanjo Negro": {"xp": (160, 200), "hp": 500, "atk": 75, "coins": (20, 35)}
        },
        "boss": {"name": "Imperador Astral", "hp": 2500, "atk": 100, "xp": 2500, "level": 60, "coins": (80, 160)},
        "resources": ["Essência celestial", "Fragmento estelar", "Coroa divina", "Lágrima de deus", "Pluma sagrada"],
        "dungeons": [
            {"name": "Santuário Celestial", "level": 19, "boss": "Avatar Divino"},
            {"name": "Palácio Estelar", "level": 20, "boss": "Deus Menor"},
            {"name": "Portal da Eternidade", "level": 21, "boss": "Guardião Final"}
        ],
        "secret_dungeons": [
            {"name": "🌌 Além do Trono", "level": 19, "boss": "O Que Não Tem Nome", "secret": True},
            {"name": "✨ Raiz da Criação", "level": 20, "boss": "Deus Esquecido", "secret": True}
        ],
        "events": [
            "Raios divinos atravessam as nuvens douradas.",
            "Você caminha sobre um chão de estrelas solidificadas.",
            "Anjos cantam hinos em línguas antigas.",
            "Você sente o peso de mil olhares celestiais.",
            "Portões gigantescos se abrem revelando o infinito.",
            "Suas feridas curam instantaneamente por luz divina.",
            "Você vê deuses antigos esculpidos em ouro.",
            "Colunas de mármore sustentam o próprio céu.",
            "Você encontra armas que mataram divindades.",
            "O trono vazio pulsa com poder incompreensível.",
            "Guardiões imortais testam sua dignidade.",
            "Você ouve profecias sobre o fim de todas as coisas.",
            "Asas de luz brotam temporariamente de suas costas.",
            "Você vê a criação e destruição de mundos.",
            "Energias primordiais fluem através de você.",
            "Você encontra o livro do destino aberto.",
            "Almas de heróis lendários te cumprimentam.",
            "Você sente o conhecimento de tudo por um instante.",
            "O Imperador te observa do trono distante.",
            "Você encontra a espada que cortou a primeira estrela.",
            "Sua mortalidade é questionada pela própria existência.",
            "Você está a um passo de se tornar uma lenda eterna."
        ]
    }
}

# ================= ITENS EXPANDIDOS (com Divino e Primordial) =================
ITEMS = {
    "weapons": [
        # Comum
        {"name": "Espada Enferrujada", "rarity": "Comum", "atk": 5},
        {"name": "Adaga de Pedra", "rarity": "Comum", "atk": 6},
        {"name": "Cajado de Madeira", "rarity": "Comum", "atk": 5},
        {"name": "Machado Quebrado", "rarity": "Comum", "atk": 6},
        {"name": "Lança de Bambu", "rarity": "Comum", "atk": 5},
        {"name": "Faca Cega", "rarity": "Comum", "atk": 4},
        {"name": "Porrete de Madeira", "rarity": "Comum", "atk": 5},
        {"name": "Foice Velha", "rarity": "Comum", "atk": 6},
        # Incomum
        {"name": "Espada de Ferro", "rarity": "Incomum", "atk": 12},
        {"name": "Machado de Batalha", "rarity": "Incomum", "atk": 14},
        {"name": "Arco Composto", "rarity": "Incomum", "atk": 13},
        {"name": "Martelo de Guerra", "rarity": "Incomum", "atk": 15},
        {"name": "Katana Básica", "rarity": "Incomum", "atk": 13},
        {"name": "Mangual de Ferro", "rarity": "Incomum", "atk": 14},
        {"name": "Espada Larga", "rarity": "Incomum", "atk": 13},
        {"name": "Lança de Ferro", "rarity": "Incomum", "atk": 12},
        {"name": "Claymore", "rarity": "Incomum", "atk": 15},
        {"name": "Arco Longo", "rarity": "Incomum", "atk": 14},
        {"name": "Alabarda", "rarity": "Incomum", "atk": 14},
        {"name": "Machado Duplo", "rarity": "Incomum", "atk": 15},
        # Raro
        {"name": "Espada de Madeira Negra", "rarity": "Raro", "atk": 25},
        {"name": "Lança Mística", "rarity": "Raro", "atk": 27},
        {"name": "Arco Élfico", "rarity": "Raro", "atk": 26},
        {"name": "Machado Rúnico", "rarity": "Raro", "atk": 28},
        {"name": "Cimitarra de Prata", "rarity": "Raro", "atk": 26},
        {"name": "Alabarda Encantada", "rarity": "Raro", "atk": 27},
        {"name": "Tridente de Aço", "rarity": "Raro", "atk": 25},
        {"name": "Katana Relâmpago", "rarity": "Raro", "atk": 28},
        {"name": "Arco das Sombras", "rarity": "Raro", "atk": 27},
        {"name": "Espada Lunar", "rarity": "Raro", "atk": 26},
        {"name": "Martelo Rúnico", "rarity": "Raro", "atk": 28},
        {"name": "Lança do Caçador", "rarity": "Raro", "atk": 27},
        {"name": "Foice Maldita", "rarity": "Raro", "atk": 26},
        {"name": "Adaga Venenosa", "rarity": "Raro", "atk": 25},
        {"name": "Clava Titânica", "rarity": "Raro", "atk": 28},
        # Épico
        {"name": "Lâmina Flamejante", "rarity": "Épico", "atk": 45},
        {"name": "Cajado Arcano", "rarity": "Épico", "atk": 48},
        {"name": "Espada do Vento", "rarity": "Épico", "atk": 46},
        {"name": "Machado Titânico", "rarity": "Épico", "atk": 50},
        {"name": "Arco das Estrelas", "rarity": "Épico", "atk": 47},
        {"name": "Lança do Dragão", "rarity": "Épico", "atk": 49},
        {"name": "Foice Sombria", "rarity": "Épico", "atk": 48},
        {"name": "Martelo do Trovão", "rarity": "Épico", "atk": 51},
        {"name": "Katana Demoníaca", "rarity": "Épico", "atk": 49},
        {"name": "Espada da Tempestade", "rarity": "Épico", "atk": 47},
        {"name": "Arco Celestial", "rarity": "Épico", "atk": 48},
        {"name": "Tridente de Poseidon", "rarity": "Épico", "atk": 50},
        {"name": "Lança da Fênix", "rarity": "Épico", "atk": 49},
        {"name": "Machado Infernal", "rarity": "Épico", "atk": 51},
        {"name": "Adaga da Morte", "rarity": "Épico", "atk": 46},
        {"name": "Espada do Eclipse", "rarity": "Épico", "atk": 48},
        {"name": "Cajado do Caos", "rarity": "Épico", "atk": 50},
        # Lendário
        {"name": "Excalibur", "rarity": "Lendário", "atk": 100},
        {"name": "Mjolnir", "rarity": "Lendário", "atk": 105},
        {"name": "Gungnir", "rarity": "Lendário", "atk": 103},
        {"name": "Kusanagi", "rarity": "Lendário", "atk": 102},
        {"name": "Durandal", "rarity": "Lendário", "atk": 104},
        {"name": "Gram", "rarity": "Lendário", "atk": 103},
        {"name": "Tyrfing", "rarity": "Lendário", "atk": 102},
        {"name": "Caladbolg", "rarity": "Lendário", "atk": 104},
        {"name": "Gáe Bolg", "rarity": "Lendário", "atk": 105},
        {"name": "Rhongomyniad", "rarity": "Lendário", "atk": 103},
        # Mítico
        {"name": "Espada do Criador", "rarity": "Mítico", "atk": 200},
        {"name": "Cetro da Eternidade", "rarity": "Mítico", "atk": 210},
        {"name": "Lâmina do Destino", "rarity": "Mítico", "atk": 205},
        {"name": "Arco do Apocalipse", "rarity": "Mítico", "atk": 208},
        # Divino (NOVO)
        {"name": "Espada da Ascensão", "rarity": "Divino", "atk": 380},
        {"name": "Cajado da Criação Divina", "rarity": "Divino", "atk": 400},
        {"name": "Lança do Juízo Final", "rarity": "Divino", "atk": 390},
        {"name": "Arco da Extinção", "rarity": "Divino", "atk": 395},
        {"name": "Foice do Ceifador Divino", "rarity": "Divino", "atk": 385},
        # Primordial (NOVO)
        {"name": "Fragmento da Primeira Arma", "rarity": "Primordial", "atk": 750},
        {"name": "Vontade Feita Lâmina", "rarity": "Primordial", "atk": 800},
        {"name": "O Começo e o Fim", "rarity": "Primordial", "atk": 780},
        {"name": "Peso da Existência", "rarity": "Primordial", "atk": 760}
    ],
    "armor": [
        # Comum
        {"name": "Armadura de Couro", "rarity": "Comum", "def": 3},
        {"name": "Robes Simples", "rarity": "Comum", "def": 4},
        {"name": "Túnica de Linho", "rarity": "Comum", "def": 3},
        {"name": "Peitoral de Bronze", "rarity": "Comum", "def": 4},
        {"name": "Capa Rasgada", "rarity": "Comum", "def": 3},
        {"name": "Colete de Couro", "rarity": "Comum", "def": 4},
        {"name": "Vestes Gastas", "rarity": "Comum", "def": 3},
        {"name": "Armadura Rachada", "rarity": "Comum", "def": 4},
        # Incomum
        {"name": "Armadura de Ferro", "rarity": "Incomum", "def": 8},
        {"name": "Cota de Malha", "rarity": "Incomum", "def": 10},
        {"name": "Armadura de Escamas", "rarity": "Incomum", "def": 9},
        {"name": "Robes Reforçados", "rarity": "Incomum", "def": 8},
        {"name": "Brigandina", "rarity": "Incomum", "def": 10},
        {"name": "Armadura de Couro Batido", "rarity": "Incomum", "def": 9},
        {"name": "Peitoral de Aço", "rarity": "Incomum", "def": 10},
        {"name": "Armadura de Anéis", "rarity": "Incomum", "def": 9},
        {"name": "Vestes de Batalha", "rarity": "Incomum", "def": 8},
        {"name": "Couraça Leve", "rarity": "Incomum", "def": 9},
        {"name": "Armadura Laminada", "rarity": "Incomum", "def": 10},
        {"name": "Gibão de Armas", "rarity": "Incomum", "def": 9},
        # Raro
        {"name": "Armadura Mística", "rarity": "Raro", "def": 18},
        {"name": "Armadura Élfica", "rarity": "Raro", "def": 20},
        {"name": "Placas de Aço", "rarity": "Raro", "def": 19},
        {"name": "Armadura Rúnica", "rarity": "Raro", "def": 21},
        {"name": "Cota Encantada", "rarity": "Raro", "def": 19},
        {"name": "Armadura de Mithril", "rarity": "Raro", "def": 20},
        {"name": "Vestes Arcanas", "rarity": "Raro", "def": 18},
        {"name": "Armadura Lunar", "rarity": "Raro", "def": 20},
        {"name": "Placas Reforçadas", "rarity": "Raro", "def": 21},
        {"name": "Armadura Cristalina", "rarity": "Raro", "def": 19},
        {"name": "Vestes do Sábio", "rarity": "Raro", "def": 18},
        {"name": "Armadura do Cavaleiro", "rarity": "Raro", "def": 21},
        {"name": "Couraça Élfica", "rarity": "Raro", "def": 20},
        {"name": "Armadura Sombria", "rarity": "Raro", "def": 19},
        {"name": "Placas de Dragão", "rarity": "Raro", "def": 21},
        # Épico
        {"name": "Armadura Dracônica", "rarity": "Épico", "def": 35},
        {"name": "Armadura das Sombras", "rarity": "Épico", "def": 38},
        {"name": "Placas do Titã", "rarity": "Épico", "def": 37},
        {"name": "Armadura Flamejante", "rarity": "Épico", "def": 36},
        {"name": "Vestes Estelares", "rarity": "Épico", "def": 35},
        {"name": "Armadura do Vazio", "rarity": "Épico", "def": 39},
        {"name": "Couraça Angelical", "rarity": "Épico", "def": 38},
        {"name": "Armadura Demoníaca", "rarity": "Épico", "def": 40},
        {"name": "Placas do Dragão Negro", "rarity": "Épico", "def": 39},
        {"name": "Armadura da Tempestade", "rarity": "Épico", "def": 37},
        {"name": "Vestes do Arcano Maior", "rarity": "Épico", "def": 36},
        {"name": "Armadura de Obsidiana", "rarity": "Épico", "def": 38},
        {"name": "Placas Celestiais", "rarity": "Épico", "def": 40},
        {"name": "Armadura do Fênix", "rarity": "Épico", "def": 37},
        {"name": "Couraça Infernal", "rarity": "Épico", "def": 39},
        {"name": "Armadura do Eclipse", "rarity": "Épico", "def": 38},
        {"name": "Vestes do Caos", "rarity": "Épico", "def": 36},
        # Lendário
        {"name": "Armadura Celestial", "rarity": "Lendário", "def": 80},
        {"name": "Égide Divina", "rarity": "Lendário", "def": 85},
        {"name": "Armadura de Odin", "rarity": "Lendário", "def": 83},
        {"name": "Placas de Adaman", "rarity": "Lendário", "def": 82},
        {"name": "Vestes do Arcano Supremo", "rarity": "Lendário", "def": 84},
        {"name": "Armadura de Zeus", "rarity": "Lendário", "def": 85},
        {"name": "Placas de Poseidon", "rarity": "Lendário", "def": 83},
        {"name": "Armadura de Ares", "rarity": "Lendário", "def": 84},
        {"name": "Vestes de Atena", "rarity": "Lendário", "def": 82},
        {"name": "Couraça de Thor", "rarity": "Lendário", "def": 85},
        # Mítico
        {"name": "Armadura do Primeiro Deus", "rarity": "Mítico", "def": 180},
        {"name": "Vestes da Criação", "rarity": "Mítico", "def": 190},
        {"name": "Placas da Eternidade", "rarity": "Mítico", "def": 185},
        {"name": "Armadura do Destino", "rarity": "Mítico", "def": 188},
        # Divino (NOVO)
        {"name": "Manto da Ascensão", "rarity": "Divino", "def": 350},
        {"name": "Armadura do Serafim", "rarity": "Divino", "def": 370},
        {"name": "Vestes do Julgamento", "rarity": "Divino", "def": 360},
        {"name": "Placas do Arcanjo Supremo", "rarity": "Divino", "def": 365},
        # Primordial (NOVO)
        {"name": "Pele da Primeira Criatura", "rarity": "Primordial", "def": 700},
        {"name": "Armadura do Antes do Começo", "rarity": "Primordial", "def": 750},
        {"name": "Vestes do Silêncio Eterno", "rarity": "Primordial", "def": 720},
        {"name": "Proteção do Vazio Consciente", "rarity": "Primordial", "def": 730}
    ]
}

# ================= ESTRUTURAS =================
STRUCTURES = [
    {
        "name": "🏛️ Cidade Mercante",
        "description": "Uma cidade movimentada onde comerciantes de todos os reinos se reúnem.",
        "narrator": "As ruas estão repletas de mercadores gritando seus produtos...",
        "worlds": [1, 10, 20, 30]
    },
    {
        "name": "⛪ Templo Abandonado",
        "description": "Um templo antigo que guarda segredos esquecidos.",
        "narrator": "O ar aqui é pesado... Algo sagrado já habitou este lugar.",
        "worlds": [10, 20, 30, 40]
    },
    {
        "name": "🏰 Fortaleza em Ruínas",
        "description": "Restos de uma fortaleza que já foi gloriosa.",
        "narrator": "Ecos de batalhas antigas ainda reverberam entre as pedras...",
        "worlds": [20, 30, 40, 50]
    },
    {
        "name": "🌉 Ponte Mística",
        "description": "Uma ponte que conecta dimensões.",
        "narrator": "Você sente a realidade se distorcendo ao cruzar...",
        "worlds": [40, 50, 60]
    },
    {
        "name": "🗿 Monumento dos Heróis",
        "description": "Estátuas de heróis lendários do passado.",
        "narrator": "Seus feitos estão gravados em pedra eterna...",
        "worlds": [30, 40, 50, 60]
    }
]

# ================= FALAS DO NARRADOR =================
NARRATOR_WARNINGS = [
    "Logo ele enfrentará seu maior pesadelo...",
    "O destino está prestes a testar sua verdadeira força...",
    "Algo terrível se aproxima nas sombras...",
    "Os dados do destino estão prestes a rolar...",
    "Uma presença maligna observa cada passo seu...",
    "A morte espreita além do próximo horizonte...",
    "Seu nome será lembrado... ou esquecido para sempre.",
    "As estrelas tremem com o que está por vir...",
    "Nem todos os heróis sobrevivem às suas jornadas...",
    "O fim de uma era se aproxima..."
]

# ================= SISTEMA DE SORTE =================
LUCK_SYSTEM = {
    1: {"emoji": "💀", "name": "Azar extremo"},
    2: {"emoji": "☠️", "name": "Muito azar"},
    3: {"emoji": "😵", "name": "Azar"},
    4: {"emoji": "😐", "name": "Ruim"},
    5: {"emoji": "😶", "name": "Neutro"},
    6: {"emoji": "🙂", "name": "Bom"},
    7: {"emoji": "😄", "name": "Sorte"},
    8: {"emoji": "🍀", "name": "Muita sorte"},
    9: {"emoji": "✨", "name": "Sorte extrema"},
    10: {"emoji": "🌟", "name": "Lenda"}
}

# ================= BANCO DE DADOS =================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS players (
        user_id TEXT PRIMARY KEY,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,
        hp INTEGER DEFAULT 100,
        max_hp INTEGER DEFAULT 100,
        coins INTEGER DEFAULT 0,
        inventory TEXT DEFAULT '[]',
        weapon TEXT DEFAULT NULL,
        armor TEXT DEFAULT NULL,
        worlds TEXT DEFAULT '[1]',
        bosses TEXT DEFAULT '[]',
        class TEXT DEFAULT NULL,
        pet TEXT DEFAULT NULL,
        guild_id INTEGER DEFAULT NULL,
        active_effects TEXT DEFAULT '{}',
        active_quest TEXT DEFAULT NULL,
        completed_quests TEXT DEFAULT '[]',
        mana INTEGER DEFAULT 50,
        max_mana INTEGER DEFAULT 50,
        pvp_battles TEXT DEFAULT '{}',
        alignment_points INTEGER DEFAULT 0,
        pet_farm TEXT DEFAULT '[]',
        discovered_map TEXT DEFAULT '{}'
    )''')

    # Migração segura de colunas novas
    for col_def in [
        "ALTER TABLE players ADD COLUMN mana INTEGER DEFAULT 50",
        "ALTER TABLE players ADD COLUMN max_mana INTEGER DEFAULT 50",
        "ALTER TABLE players ADD COLUMN pvp_battles TEXT DEFAULT '{}'",
        "ALTER TABLE players ADD COLUMN alignment_points INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN pet_farm TEXT DEFAULT '[]'",
        "ALTER TABLE players ADD COLUMN discovered_map TEXT DEFAULT '{}'",
        "ALTER TABLE players ADD COLUMN job TEXT DEFAULT NULL",
        "ALTER TABLE players ADD COLUMN job_since INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN city_title TEXT DEFAULT NULL",
        "ALTER TABLE players ADD COLUMN knights TEXT DEFAULT '[]'",
        "ALTER TABLE players ADD COLUMN last_work INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN last_defend INTEGER DEFAULT 0",
    ]:
        try:
            c.execute(col_def)
        except: pass

    c.execute('''CREATE TABLE IF NOT EXISTS pvp_battles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenger_id TEXT,
        target_id TEXT,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS coin_exchange_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        username TEXT,
        csi_coins INTEGER,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS guilds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        leader_id TEXT,
        members TEXT DEFAULT '[]',
        total_xp INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS trade_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user TEXT,
        to_user TEXT,
        from_items TEXT,
        to_items TEXT,
        status TEXT DEFAULT 'pending',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS team_quests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quest_id TEXT,
        leader_id TEXT,
        members TEXT DEFAULT '[]',
        status TEXT DEFAULT 'recruiting',
        progress INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS boss_battles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boss_name TEXT,
        leader_id TEXT,
        members TEXT DEFAULT '[]',
        world_level INTEGER,
        status TEXT DEFAULT 'recruiting',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

def get_player_db(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id = ?", (str(user_id),))
    result = c.fetchone()
    conn.close()

    if result:
        return {
            "level": result[1],
            "xp": result[2],
            "hp": result[3],
            "max_hp": result[4],
            "coins": result[5],
            "inventory": json.loads(result[6]),
            "weapon": result[7],
            "armor": result[8],
            "worlds": json.loads(result[9]),
            "bosses": json.loads(result[10]),
            "class": result[11],
            "pet": result[12],
            "guild_id": result[13],
            "active_effects": json.loads(result[14]) if result[14] else {},
            "active_quest": json.loads(result[15]) if result[15] else None,
            "completed_quests": json.loads(result[16]) if result[16] else [],
            "mana": result[17] if len(result) > 17 else 50,
            "max_mana": result[18] if len(result) > 18 else 50,
            "pvp_battles": json.loads(result[19]) if len(result) > 19 and result[19] else {},
            "alignment_points": result[20] if len(result) > 20 else 0,
            "pet_farm": json.loads(result[21]) if len(result) > 21 and result[21] else [],
            "discovered_map": json.loads(result[22]) if len(result) > 22 and result[22] else {},
            "job": result[23] if len(result) > 23 else None,
            "job_since": result[24] if len(result) > 24 else 0,
            "city_title": result[25] if len(result) > 25 else None,
            "knights": json.loads(result[26]) if len(result) > 26 and result[26] else [],
            "last_work": result[27] if len(result) > 27 else 0,
            "last_defend": result[28] if len(result) > 28 else 0,
        }
    return None

def save_player_db(user_id, player):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''INSERT OR REPLACE INTO players
                 (user_id, level, xp, hp, max_hp, coins, inventory, weapon, armor,
                  worlds, bosses, class, pet, guild_id, active_effects, active_quest, completed_quests,
                  mana, max_mana, pvp_battles, alignment_points, pet_farm, discovered_map,
                  job, job_since, city_title, knights, last_work, last_defend)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (str(user_id), player["level"], player["xp"], player["hp"], player["max_hp"],
               player["coins"], json.dumps(player["inventory"]), player["weapon"], player["armor"],
               json.dumps(player["worlds"]), json.dumps(player["bosses"]), player.get("class"),
               player.get("pet"), player.get("guild_id"),
               json.dumps(player.get("active_effects", {})),
               json.dumps(player.get("active_quest")) if player.get("active_quest") else None,
               json.dumps(player.get("completed_quests", [])),
               player.get("mana", 50), player.get("max_mana", 50),
               json.dumps(player.get("pvp_battles", {})),
               player.get("alignment_points", 0),
               json.dumps(player.get("pet_farm", [])),
               json.dumps(player.get("discovered_map", {})),
               player.get("job"), player.get("job_since", 0),
               player.get("city_title"),
               json.dumps(player.get("knights", [])),
               player.get("last_work", 0), player.get("last_defend", 0)))

    conn.commit()
    conn.close()

# ================= FUNÇÕES BASE =================

def roll_dice():
    return random.randint(1, 10)

def roll_with_bonus(player):
    """Rola dado com bônus de raridade de itens e classe"""
    roll = roll_dice()
    item_bonus = get_item_dice_bonus(player)
    if player.get("class") == "Bardo":
        roll = min(10, roll + 1)
    roll = min(10, roll + item_bonus)
    return roll

def get_luck(roll):
    return LUCK_SYSTEM.get(roll, LUCK_SYSTEM[5])

def calc_xp(level):
    return (level ** 2) * 20

def get_world(level, player=None):
    """Retorna o mundo atual do jogador. Se player fornecido, respeita travas de boss."""
    if player:
        # Mundos desbloqueados = apenas os que estão na lista player["worlds"]
        available = sorted([k for k in WORLDS.keys() if k in player["worlds"]], reverse=True)
    else:
        levels = sorted([k for k in WORLDS.keys() if k <= level], reverse=True)
        available = levels
    return WORLDS[available[0]] if available else WORLDS[1]

def create_player(user_id):
    player = {
        "level": 1,
        "xp": 0,
        "hp": 100,
        "max_hp": 100,
        "coins": 0,
        "inventory": [],
        "weapon": None,
        "armor": None,
        "worlds": [1],
        "bosses": [],
        "class": None,
        "pet": None,
        "guild_id": None,
        "active_effects": {},
        "active_quest": None,
        "completed_quests": [],
        "mana": 50,
        "max_mana": 50,
        "pvp_battles": {},
        "alignment_points": 0,
        "pet_farm": [],
        "discovered_map": {},
        "job": None,
        "job_since": 0,
        "city_title": None,
        "knights": [],
        "last_work": 0,
        "last_defend": 0,
    }
    save_player_db(user_id, player)
    return player

def get_player(user_id):
    player = get_player_db(user_id)
    if not player:
        player = create_player(user_id)
    return player

def calc_max_mana(player):
    """Calcula mana máxima baseada na classe e nível"""
    cls = player.get("class")
    if not cls or cls not in CLASS_MANA:
        return 50 + player["level"] * 2
    base = CLASS_MANA[cls]["base_mana"]
    per_level = CLASS_MANA[cls]["mana_per_level"]
    return base + (player["level"] - 1) * per_level

def get_item_dice_bonus(player):
    """Retorna bônus no dado baseado na raridade dos equipamentos"""
    bonus = 0
    if player.get("weapon"):
        for w in ITEMS["weapons"]:
            if w["name"] == player["weapon"]:
                bonus += RARITY_DICE_BONUS.get(w["rarity"], 0)
                break
    if player.get("armor"):
        for a in ITEMS["armor"]:
            if a["name"] == player["armor"]:
                bonus += RARITY_DICE_BONUS.get(a["rarity"], 0)
                break
    return bonus

def get_item_sell_price(item_name):
    for weapon in ITEMS["weapons"]:
        if weapon["name"] == item_name:
            rarity_prices = {
                "Comum": 2, "Incomum": 8, "Raro": 20,
                "Épico": 60, "Lendário": 200, "Mítico": 600,
                "Divino": 1500, "Primordial": 4000
            }
            return rarity_prices.get(weapon["rarity"], 5)

    for armor in ITEMS["armor"]:
        if armor["name"] == item_name:
            rarity_prices = {
                "Comum": 2, "Incomum": 8, "Raro": 20,
                "Épico": 60, "Lendário": 200, "Mítico": 600,
                "Divino": 1500, "Primordial": 4000
            }
            return rarity_prices.get(armor["rarity"], 5)

    if item_name in POTIONS:
        rarity_prices = {
            "Comum": 3, "Incomum": 10, "Raro": 30,
            "Épico": 80, "Lendário": 250, "Mítico": 800,
            "Divino": 2000
        }
        return rarity_prices.get(POTIONS[item_name]["rarity"], 5)

    return 3  # recursos

def add_xp(user_id, amount):
    player = get_player(user_id)

    # XP aumentado significativamente
    amount = int(amount * 2.5)

    if player.get("class") == "Bardo":
        amount = int(amount * 1.2)

    player["xp"] += amount
    leveled = False

    while player["xp"] >= calc_xp(player["level"]):
        player["xp"] -= calc_xp(player["level"])
        player["level"] += 1

        class_bonus = 0
        if player.get("class") and player["class"] in CLASSES:
            class_bonus = CLASSES[player["class"]]["hp_bonus"] // 10

        player["max_hp"] += (10 + class_bonus)
        player["hp"] = player["max_hp"]

        # Atualiza mana ao subir de nível
        new_max_mana = calc_max_mana(player)
        player["max_mana"] = new_max_mana
        player["mana"] = new_max_mana  # Recupera toda a mana ao subir de nível

        leveled = True

        # MUNDOS SÓ SÃO DESBLOQUEADOS AO DERROTAR O BOSS DE NÍVEL
        # (não automático ao subir de level)

    save_player_db(user_id, player)

    if player.get("guild_id"):
        distribute_guild_xp(player["guild_id"], amount)

    return leveled

def distribute_guild_xp(guild_id, amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT members FROM guilds WHERE id = ?", (guild_id,))
    result = c.fetchone()

    if result:
        members = json.loads(result[0])
        for member_id in members:
            member = get_player(member_id)
            if member:
                member["xp"] += amount
                while member["xp"] >= calc_xp(member["level"]):
                    member["xp"] -= calc_xp(member["level"])
                    member["level"] += 1
                    class_bonus = 0
                    if member.get("class") and member["class"] in CLASSES:
                        class_bonus = CLASSES[member["class"]]["hp_bonus"] // 10
                    member["max_hp"] += (10 + class_bonus)
                    member["hp"] = member["max_hp"]
                    for wl in WORLDS.keys():
                        if member["level"] >= wl and wl not in member["worlds"]:
                            member["worlds"].append(wl)
                save_player_db(member_id, member)

    conn.close()

def remove_xp(user_id, amount):
    player = get_player(user_id)
    world = get_world(player["level"], player)

    adjusted_loss = int(amount * world.get("xp_loss_multiplier", 1.0))
    player["xp"] -= adjusted_loss

    while player["xp"] < 0 and player["level"] > 1:
        player["level"] -= 1
        player["xp"] += calc_xp(player["level"])

    if player["xp"] < 0:
        player["xp"] = 0

    if player["level"] == 1 and player["xp"] == 0:
        player["inventory"] = []
        player["weapon"] = None
        player["armor"] = None
        player["worlds"] = [1]
        player["bosses"] = []
        player["hp"] = 100
        player["max_hp"] = 100
        player["coins"] = 0
        player["class"] = None
        player["pet"] = None
        player["active_quest"] = None
        save_player_db(user_id, player)
        return "reset", adjusted_loss

    save_player_db(user_id, player)
    return "ok", adjusted_loss

def add_coins(user_id, amount):
    player = get_player(user_id)
    player["coins"] += amount
    save_player_db(user_id, player)

def remove_coins(user_id, amount):
    player = get_player(user_id)
    if player["coins"] >= amount:
        player["coins"] -= amount
        save_player_db(user_id, player)
        return True
    return False

def get_level_boss(level):
    """Retorna boss de level correspondente ao nível do jogador"""
    boss_levels = {
        9: 1, 19: 10, 29: 20, 39: 30, 49: 40, 59: 50
    }
    world_key = boss_levels.get(level)
    if world_key:
        return WORLDS[world_key]["boss"]
    return None

# ================= VIEWS / BOTÕES =================

class ClassSelectButton(discord.ui.View):
    def __init__(self, user_id, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.answered = False

        class_names = list(CLASSES.keys())[:5]
        for class_name in class_names:
            class_data = CLASSES[class_name]
            button = discord.ui.Button(
                label=class_name, style=discord.ButtonStyle.primary, emoji=class_data["emoji"]
            )
            button.callback = self.create_callback(class_name)
            self.add_item(button)

    def create_callback(self, class_name):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta escolha não é sua!", ephemeral=True)
            if self.answered:
                return
            self.answered = True
            player = get_player(self.user_id)
            player["class"] = class_name
            class_data = CLASSES[class_name]
            player["max_hp"] += class_data["hp_bonus"]
            player["hp"] = player["max_hp"]
            save_player_db(self.user_id, player)

            embed = discord.Embed(
                title=f"{class_data['emoji']} Classe Escolhida!",
                description=f"*O narrador anuncia:*\n\n'Você se tornou um **{class_name}**!'\n\n{class_data['description']}",
                color=discord.Color.gold()
            )
            embed.add_field(name="💪 Bônus de ATK", value=f"+{class_data['atk_bonus']}", inline=True)
            embed.add_field(name="🛡️ Bônus de DEF", value=f"+{class_data['def_bonus']}", inline=True)
            embed.add_field(name="❤️ Bônus de HP", value=f"+{class_data['hp_bonus']}", inline=True)
            await interaction.response.edit_message(embed=embed, view=None)
        return callback


class ClassSelectButton2(discord.ui.View):
    def __init__(self, user_id, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.answered = False

        class_names = list(CLASSES.keys())[5:]
        for class_name in class_names:
            class_data = CLASSES[class_name]
            button = discord.ui.Button(
                label=class_name, style=discord.ButtonStyle.primary, emoji=class_data["emoji"]
            )
            button.callback = self.create_callback(class_name)
            self.add_item(button)

    def create_callback(self, class_name):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta escolha não é sua!", ephemeral=True)
            if self.answered:
                return
            self.answered = True
            player = get_player(self.user_id)
            player["class"] = class_name
            class_data = CLASSES[class_name]
            player["max_hp"] += class_data["hp_bonus"]
            player["hp"] = player["max_hp"]
            save_player_db(self.user_id, player)

            embed = discord.Embed(
                title=f"{class_data['emoji']} Classe Escolhida!",
                description=f"*O narrador anuncia:*\n\n'Você se tornou um **{class_name}**!'\n\n{class_data['description']}",
                color=discord.Color.gold()
            )
            embed.add_field(name="💪 Bônus de ATK", value=f"+{class_data['atk_bonus']}", inline=True)
            embed.add_field(name="🛡️ Bônus de DEF", value=f"+{class_data['def_bonus']}", inline=True)
            embed.add_field(name="❤️ Bônus de HP", value=f"+{class_data['hp_bonus']}", inline=True)
            await interaction.response.edit_message(embed=embed, view=None)
        return callback


class PetTameButton(discord.ui.View):
    def __init__(self, user_id, pet, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.pet = pet
        self.answered = False

    @discord.ui.button(label="Tentar Domesticar", style=discord.ButtonStyle.green, emoji="🤝")
    async def tame(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Este pet não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True

        roll = roll_dice()
        luck = get_luck(roll)
        embed = discord.Embed(title=f"🎲 Tentativa de Domesticação", color=discord.Color.blue())
        embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 3:
            player = get_player(self.user_id)
            dmg = random.randint(20, 40)
            player["hp"] -= dmg
            if player["hp"] <= 0:
                player["hp"] = 1
            save_player_db(self.user_id, player)
            embed.add_field(name="💥 O Pet Ataca!", value=f"*'{self.pet['name']} se assusta e ataca você!'*\n\n💔 **−{dmg} HP**", inline=False)
            embed.color = discord.Color.red()
        elif roll <= 6:
            embed.add_field(name="🏃 Fuga!", value=f"*'{self.pet['name']} não confia em você e foge...'*", inline=False)
            embed.color = discord.Color.orange()
        else:
            player = get_player(self.user_id)
            player["pet"] = self.pet["name"]
            save_player_db(self.user_id, player)
            embed.add_field(
                name="✨ Domesticado!",
                value=f"*'{self.pet['emoji']} **{self.pet['name']}** agora é seu companheiro!'*\n\n💪 **+{self.pet['bonus_atk']} ATK**\n❤️ **+{self.pet['bonus_hp']} HP**",
                inline=False
            )
            embed.color = discord.Color.gold()

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Deixar Ir", style=discord.ButtonStyle.gray, emoji="👋")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esta escolha não é sua!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"*'Você decide não arriscar e deixa {self.pet['name']} em paz...'*", view=None
        )


class EquipButton(discord.ui.View):
    def __init__(self, user_id, item_name, item_type, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.item_name = item_name
        self.item_type = item_type
        self.answered = False

    @discord.ui.button(label="Equipar", style=discord.ButtonStyle.green, emoji="⚔️")
    async def equip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse item não é seu!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        player = get_player(self.user_id)
        old_item = player[self.item_type]
        player[self.item_type] = self.item_name
        save_player_db(self.user_id, player)

        if old_item:
            response = f"✅ **Equipado!**\n\n🔄 Você substituiu **{old_item}** por **{self.item_name}**!\n\n*'Seu poder aumenta...'*"
        else:
            response = f"✅ **Equipado!**\n\n⚔️ Você equipou **{self.item_name}**!\n\n*'Você está mais forte agora.'*"

        await interaction.response.edit_message(content=response, view=None)

    @discord.ui.button(label="Guardar", style=discord.ButtonStyle.gray, emoji="🎒")
    async def keep(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse item não é seu!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        player = get_player(self.user_id)
        player["inventory"].append(self.item_name)
        save_player_db(self.user_id, player)
        await interaction.response.edit_message(
            content=f"🎒 **Guardado!**\n\nVocê guarda **{self.item_name}** no inventário.\n\n*'Pode ser útil depois...'*",
            view=None
        )


class BossButton(discord.ui.View):
    def __init__(self, user_id, boss_name, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.boss_name = boss_name
        self.answered = False

    @discord.ui.button(label="Enfrentar Sozinho", style=discord.ButtonStyle.red, emoji="⚔️")
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse não é seu boss!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"⚔️ **Você avança em direção ao {self.boss_name}!**\n\n*A batalha épica começa...*", view=None
        )
        await asyncio.sleep(2)
        await fight_boss(interaction.channel, self.user_id)

    @discord.ui.button(label="Chamar Aliados", style=discord.ButtonStyle.blurple, emoji="👥")
    async def call_allies(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse não é seu boss!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"📣 **{interaction.user.mention} está convocando aliados para enfrentar o {self.boss_name}!**\n\nUse `juntar boss` para participar desta batalha!\n\nO líder deverá usar `iniciar batalha boss` quando estiver pronto.",
            view=None
        )
        # Registra na DB
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        player = get_player(self.user_id)
        world_level = max([k for k in WORLDS.keys() if k <= player["level"]])
        c.execute("INSERT INTO boss_battles (boss_name, leader_id, members, world_level) VALUES (?, ?, ?, ?)",
                  (self.boss_name, str(self.user_id), json.dumps([str(self.user_id)]), world_level))
        conn.commit()
        conn.close()

    @discord.ui.button(label="Recuar", style=discord.ButtonStyle.gray, emoji="🏃")
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse não é seu boss!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"🏃 **Você recua estrategicamente.**\n\n*'A prudência também é sabedoria.'*", view=None
        )


class TradeButton(discord.ui.View):
    def __init__(self, from_user, to_user, from_items, to_items, timeout=300):
        super().__init__(timeout=timeout)
        self.from_user = from_user
        self.to_user = to_user
        self.from_items = from_items
        self.to_items = to_items
        self.answered = False

    @discord.ui.button(label="Aceitar Troca", style=discord.ButtonStyle.green, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.to_user):
            return await interaction.response.send_message("❌ Esta troca não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True

        from_player = get_player(self.from_user)
        to_player = get_player(self.to_user)

        for item in self.from_items:
            if item in from_player["inventory"]:
                from_player["inventory"].remove(item)
        for item in self.to_items:
            if item in to_player["inventory"]:
                to_player["inventory"].remove(item)
        for item in self.to_items:
            from_player["inventory"].append(item)
        for item in self.from_items:
            to_player["inventory"].append(item)

        save_player_db(self.from_user, from_player)
        save_player_db(self.to_user, to_player)

        await interaction.response.edit_message(
            content=f"✅ **Troca Realizada!**\n\n*'Os itens mudam de mãos...'*\n\n🔄 Troca concluída!", view=None
        )

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.red, emoji="❌")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.to_user):
            return await interaction.response.send_message("❌ Esta troca não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(content=f"❌ **Troca Recusada**\n\n*'Talvez em outra ocasião...'*", view=None)


class ShopButton(discord.ui.View):
    def __init__(self, user_id, items, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.items = items

    @discord.ui.button(label="Comprar Item 1", style=discord.ButtonStyle.green, emoji="💰")
    async def buy1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.buy_item(interaction, 0)

    @discord.ui.button(label="Comprar Item 2", style=discord.ButtonStyle.green, emoji="💰")
    async def buy2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.buy_item(interaction, 1)

    @discord.ui.button(label="Comprar Item 3", style=discord.ButtonStyle.green, emoji="💰")
    async def buy3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.buy_item(interaction, 2)

    @discord.ui.button(label="Sair", style=discord.ButtonStyle.gray, emoji="🚪")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🚪 **Você sai da loja.**\n\n*'Até a próxima, viajante...'*", view=None)

    async def buy_item(self, interaction, index):
        if index >= len(self.items):
            return await interaction.response.send_message("❌ Item inválido!", ephemeral=True)
        item = self.items[index]
        player = get_player(interaction.user.id)

        if player["coins"] < item["price"]:
            return await interaction.response.send_message(
                f"❌ **Moedas insuficientes!**\n\nVocê precisa de **{item['price']} CSI** mas tem apenas **{player['coins']} CSI**.",
                ephemeral=True
            )

        remove_coins(interaction.user.id, item["price"])
        if item["type"] in ["weapon", "armor"]:
            player = get_player(interaction.user.id)
            player["inventory"].append(item["name"])
            save_player_db(interaction.user.id, player)
        elif item["type"] == "potion":
            player = get_player(interaction.user.id)
            player["inventory"].append(item["name"])
            save_player_db(interaction.user.id, player)

        await interaction.response.send_message(
            f"✅ **Compra realizada!**\n\nVocê comprou **{item['name']}** por **{item['price']} CSI**!\n\n*'Uma boa escolha!'*",
            ephemeral=True
        )


class DungeonSelectButton(discord.ui.View):
    def __init__(self, user_id, dungeons, world, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.dungeons = dungeons
        self.world = world
        self.answered = False

        for i, dungeon in enumerate(dungeons[:3]):
            button = discord.ui.Button(
                label=dungeon["name"], style=discord.ButtonStyle.primary,
                emoji="🏛️", custom_id=f"dungeon_{i}"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)

    def create_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta dungeon não é para você!", ephemeral=True)
            if self.answered:
                return
            self.answered = True
            await interaction.response.edit_message(
                content=f"🏛️ **Você entra na {self.dungeons[index]['name']}!**\n\n*'Que a sorte esteja com você...'*",
                view=None
            )
            await asyncio.sleep(2)
            await explore_dungeon(interaction.channel, self.user_id, self.dungeons[index], self.world)
        return callback


class QuestAcceptButton(discord.ui.View):
    def __init__(self, user_id, quest, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.quest = quest
        self.answered = False

    @discord.ui.button(label="Aceitar Quest", style=discord.ButtonStyle.green, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esta quest não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        player = get_player(self.user_id)

        if player.get("active_quest"):
            return await interaction.response.edit_message(
                content="❌ Você já tem uma quest ativa! Abandone-a primeiro com `abandonar quest`.", view=None
            )
        if self.quest["id"] in player.get("completed_quests", []):
            return await interaction.response.edit_message(
                content="❌ Você já completou esta quest!", view=None
            )

        quest_data = dict(self.quest)
        quest_data["progress"] = 0
        quest_data["started_at"] = datetime.now().isoformat()
        player["active_quest"] = quest_data
        save_player_db(self.user_id, player)

        embed = discord.Embed(
            title=f"📜 Quest Aceita: {self.quest['name']}",
            description=f"*{self.quest['npc']} sorri e diz:*\n\n*'{self.quest['lore']}'*",
            color=discord.Color.gold()
        )
        embed.add_field(name="🎯 Objetivo", value=self.quest["description"], inline=False)
        embed.add_field(name="⭐ Recompensa XP", value=str(self.quest["reward_xp"]), inline=True)
        embed.add_field(name="💰 Recompensa Coins", value=str(self.quest["reward_coins"]), inline=True)
        if self.quest.get("reward_item"):
            embed.add_field(name="🎁 Item Recompensa", value=self.quest["reward_item"], inline=True)

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.gray, emoji="❌")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(content="*Você declina a quest e segue em frente.*", view=None)


class PvPChallengeButton(discord.ui.View):
    def __init__(self, challenger_id, target_id, challenger_name, target_name, timeout=120):
        super().__init__(timeout=timeout)
        self.challenger_id = challenger_id
        self.target_id = target_id
        self.challenger_name = challenger_name
        self.target_name = target_name
        self.answered = False

    @discord.ui.button(label="⚔️ Aceitar Duelo!", style=discord.ButtonStyle.red, emoji="⚔️")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.target_id):
            return await interaction.response.send_message("❌ Esse desafio não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"⚔️ **{self.target_name}** aceita o desafio! A batalha começa!",
            view=None
        )
        await asyncio.sleep(1)
        await fight_pvp(interaction.channel, self.challenger_id, self.target_id)

    @discord.ui.button(label="🏃 Recusar", style=discord.ButtonStyle.gray)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.target_id):
            return await interaction.response.send_message("❌ Esse desafio não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"🏃 **{self.target_name}** recusou o desafio de **{self.challenger_name}**...\n\n*'A coragem é necessária para um duelo.'*",
            view=None
        )


async def fight_pvp(channel, challenger_id, target_id):
    """Batalha PvP estilo Pokémon entre dois jogadores"""
    challenger = get_player(challenger_id)
    target = get_player(target_id)

    try:
        challenger_user = await bot.fetch_user(int(challenger_id))
        target_user = await bot.fetch_user(int(target_id))
        ch_name = challenger_user.display_name
        tg_name = target_user.display_name
    except:
        ch_name = "Desafiante"
        tg_name = "Alvo"

    ch_cls = challenger.get("class", "Guerreiro")
    tg_cls = target.get("class", "Guerreiro")
    ch_skills = CLASS_SKILLS.get(ch_cls, CLASS_SKILLS["Guerreiro"])
    tg_skills = CLASS_SKILLS.get(tg_cls, CLASS_SKILLS["Guerreiro"])

    # Stats de batalha (baseados nos stats reais + nível)
    ch_hp = challenger["max_hp"]
    tg_hp = target["max_hp"]
    ch_mana = calc_max_mana(challenger)
    tg_mana = calc_max_mana(target)
    ch_atk_base = CLASSES[ch_cls]["atk_bonus"] + challenger["level"] * 2
    tg_atk_base = CLASSES[tg_cls]["atk_bonus"] + target["level"] * 2
    ch_def = CLASSES[ch_cls]["def_bonus"] + challenger["level"]
    tg_def = CLASSES[tg_cls]["def_bonus"] + target["level"]

    # Bônus de item
    def get_item_atk_bonus(player):
        bonus = 0
        if player.get("weapon"):
            for w in ITEMS["weapons"]:
                if w["name"] == player["weapon"]:
                    bonus += w.get("atk", 0) // 5
                    break
        return bonus

    def get_item_def_bonus(player):
        bonus = 0
        if player.get("armor"):
            for a in ITEMS["armor"]:
                if a["name"] == player["armor"]:
                    bonus += a.get("def", 0) // 5
                    break
        return bonus

    ch_atk_base += get_item_atk_bonus(challenger)
    tg_atk_base += get_item_atk_bonus(target)
    ch_def += get_item_def_bonus(challenger)
    tg_def += get_item_def_bonus(target)

    ch_cur_hp = ch_hp
    tg_cur_hp = tg_hp
    ch_cur_mana = ch_mana
    tg_cur_mana = tg_mana

    ch_icon = CLASSES[ch_cls]["emoji"]
    tg_icon = CLASSES[tg_cls]["emoji"]

    # Intro épica
    intro = discord.Embed(
        title="⚔️ DUELO INICIADO! ⚔️",
        description=f"*O narrador anuncia com voz trovejante:*\n\n**'{ch_name} vs {tg_name}!'**\n\n*'Que o mais digno prevaleça!'*",
        color=discord.Color.dark_red()
    )
    intro.add_field(
        name=f"{ch_icon} {ch_name} ({ch_cls})",
        value=f"❤️ HP: `{ch_cur_hp}` | ✨ Mana: `{ch_cur_mana}`\n⚔️ ATK: `{ch_atk_base}` | 🛡️ DEF: `{ch_def}`\nArma: {challenger.get('weapon') or 'Nenhuma'}",
        inline=True
    )
    intro.add_field(
        name=f"{tg_icon} {tg_name} ({tg_cls})",
        value=f"❤️ HP: `{tg_cur_hp}` | ✨ Mana: `{tg_cur_mana}`\n⚔️ ATK: `{tg_atk_base}` | 🛡️ DEF: `{tg_def}`\nArma: {target.get('weapon') or 'Nenhuma'}",
        inline=True
    )
    await channel.send(embed=intro)
    await asyncio.sleep(2)

    # Sistema de batalha em turnos (max 6 turnos)
    battle_log = []
    turn = 1
    ch_poison = False
    tg_poison = False
    ch_weakened = False
    tg_weakened = False

    while ch_cur_hp > 0 and tg_cur_hp > 0 and turn <= 6:
        turn_embed = discord.Embed(
            title=f"⚔️ TURNO {turn}",
            color=discord.Color.red()
        )

        # === Ação do Desafiante ===
        # Escolhe habilidade (prioriza com mana disponível)
        available_ch = [s for s in ch_skills if s["mana_cost"] <= ch_cur_mana]
        if not available_ch:
            available_ch = [ch_skills[0]]  # fallback: ataque básico
        ch_skill = random.choice(available_ch)
        ch_cur_mana = max(0, ch_cur_mana - ch_skill["mana_cost"])

        # Calcula dano
        ch_dmg_raw = int(ch_atk_base * ch_skill["dmg_mult"])
        if ch_weakened:
            ch_dmg_raw = int(ch_dmg_raw * 0.7)
        # Chance de crítico
        if random.random() < ch_skill.get("crit_chance", 0.1):
            ch_dmg_raw = int(ch_dmg_raw * 1.8)
            ch_skill_name = f"💥 CRÍTICO! {ch_skill['name']}"
        else:
            ch_skill_name = ch_skill["name"]
        # Ignora defesa se skill especifica
        if ch_skill.get("ignore_def"):
            ch_dmg = max(1, ch_dmg_raw)
        else:
            ch_dmg = max(1, ch_dmg_raw - tg_def)

        # Aplica dano alvo
        tg_cur_hp -= ch_dmg

        # Efeitos especiais do atacante
        if ch_skill.get("self_heal"):
            heal = ch_skill["self_heal"]
            ch_cur_hp = min(ch_hp, ch_cur_hp + heal)

        # Efeitos no alvo
        stun_tg = False
        if random.random() < ch_skill.get("stun_chance", 0):
            stun_tg = True
        if ch_skill.get("poison"):
            tg_poison = True
        if ch_skill.get("weaken"):
            tg_weakened = True

        # Log do ataque
        ch_hp_bar = "❤️" * max(1, int(ch_cur_hp / ch_hp * 5)) + "🖤" * (5 - max(1, int(ch_cur_hp / ch_hp * 5)))
        tg_hp_bar = "❤️" * max(1, int(max(0, tg_cur_hp) / tg_hp * 5)) + "🖤" * (5 - max(1, int(max(0, tg_cur_hp) / tg_hp * 5)))

        ch_action = f"{ch_icon} **{ch_name}** usa {ch_skill_name}!\n💥 `−{ch_dmg} HP` para {tg_name}\n{ch_skill['desc']}"
        if stun_tg:
            ch_action += f"\n⚡ **{tg_name} foi paralisado!**"
        if ch_skill.get("poison") and tg_poison:
            ch_action += f"\n☠️ **{tg_name} foi envenenado!**"
        if ch_skill.get("self_heal"):
            ch_action += f"\n💚 **{ch_name} se curou em {ch_skill['self_heal']} HP!**"

        turn_embed.add_field(name=f"🔴 Ação de {ch_name}", value=ch_action, inline=False)

        if tg_cur_hp <= 0:
            turn_embed.add_field(
                name="💀 BATALHA ENCERRADA!",
                value=f"**{tg_name}** não aguenta mais!",
                inline=False
            )
            await channel.send(embed=turn_embed)
            break

        # Veneno do alvo
        if tg_poison:
            poison_dmg = max(5, int(tg_hp * 0.05))
            tg_cur_hp -= poison_dmg
            turn_embed.add_field(name="☠️ Veneno!", value=f"**{tg_name}** sofre `{poison_dmg}` de veneno!", inline=False)
            if tg_cur_hp <= 0:
                await channel.send(embed=turn_embed)
                break

        # === Ação do Alvo (se não stunado) ===
        if not stun_tg:
            available_tg = [s for s in tg_skills if s["mana_cost"] <= tg_cur_mana]
            if not available_tg:
                available_tg = [tg_skills[0]]
            tg_skill = random.choice(available_tg)
            tg_cur_mana = max(0, tg_cur_mana - tg_skill["mana_cost"])

            tg_dmg_raw = int(tg_atk_base * tg_skill["dmg_mult"])
            if tg_weakened:
                tg_dmg_raw = int(tg_dmg_raw * 0.7)
            if random.random() < tg_skill.get("crit_chance", 0.1):
                tg_dmg_raw = int(tg_dmg_raw * 1.8)
                tg_skill_name = f"💥 CRÍTICO! {tg_skill['name']}"
            else:
                tg_skill_name = tg_skill["name"]

            if tg_skill.get("ignore_def"):
                tg_dmg = max(1, tg_dmg_raw)
            else:
                tg_dmg = max(1, tg_dmg_raw - ch_def)

            ch_cur_hp -= tg_dmg

            if tg_skill.get("self_heal"):
                tg_cur_hp = min(tg_hp, tg_cur_hp + tg_skill["self_heal"])
            if tg_skill.get("poison"):
                ch_poison = True
            if tg_skill.get("weaken"):
                ch_weakened = True
            stun_ch = random.random() < tg_skill.get("stun_chance", 0)

            tg_action = f"{tg_icon} **{tg_name}** usa {tg_skill_name}!\n💥 `−{tg_dmg} HP` para {ch_name}\n{tg_skill['desc']}"
            if stun_ch:
                tg_action += f"\n⚡ **{ch_name} foi paralisado!**"
            if tg_skill.get("poison") and ch_poison:
                tg_action += f"\n☠️ **{ch_name} foi envenenado!**"
            if tg_skill.get("self_heal"):
                tg_action += f"\n💚 **{tg_name} se curou em {tg_skill['self_heal']} HP!**"

            turn_embed.add_field(name=f"🔵 Ação de {tg_name}", value=tg_action, inline=False)
        else:
            turn_embed.add_field(name=f"⚡ {tg_name} estava paralisado!", value="Perdeu o turno!", inline=False)

        # Veneno do challenger
        if ch_poison:
            p_dmg = max(5, int(ch_hp * 0.05))
            ch_cur_hp -= p_dmg
            turn_embed.add_field(name="☠️ Veneno!", value=f"**{ch_name}** sofre `{p_dmg}` de veneno!", inline=False)

        # HP bars no final do turno
        ch_pct = max(0, int(ch_cur_hp / ch_hp * 100))
        tg_pct = max(0, int(tg_cur_hp / tg_hp * 100))
        ch_bar = "🟥" * (ch_pct // 20) + "⬛" * (5 - ch_pct // 20)
        tg_bar = "🟦" * (tg_pct // 20) + "⬛" * (5 - tg_pct // 20)

        turn_embed.add_field(
            name="📊 Status",
            value=f"{ch_icon} **{ch_name}**: {ch_bar} `{max(0, ch_cur_hp)}/{ch_hp} HP` | 💙 `{ch_cur_mana}` mana\n"
                  f"{tg_icon} **{tg_name}**: {tg_bar} `{max(0, tg_cur_hp)}/{tg_hp} HP` | 💙 `{tg_cur_mana}` mana",
            inline=False
        )

        await channel.send(embed=turn_embed)
        await asyncio.sleep(2)
        turn += 1

    # Determina vencedor
    await asyncio.sleep(1)
    result_embed = discord.Embed(
        title="🏆 RESULTADO DO DUELO!",
        color=discord.Color.gold()
    )

    if ch_cur_hp <= 0 and tg_cur_hp <= 0:
        winner_id = None
        result_embed.description = f"*'Ambos caem simultaneamente!'*\n\n**EMPATE ÉPICO!**"
        result_embed.color = discord.Color.orange()
    elif ch_cur_hp <= 0:
        winner_id = target_id
        loser_id = challenger_id
        result_embed.description = f"*O narrador anuncia:*\n\n'**{tg_name}** vence o duelo com maestria!'"
        result_embed.color = discord.Color.blue()
        xp_win = 150 + target["level"] * 5
        add_xp(target_id, xp_win)
        result_embed.add_field(name=f"🏆 {tg_name} (Vencedor)", value=f"+{xp_win} XP | +1 Vitória PvP", inline=True)
        result_embed.add_field(name=f"💀 {ch_name} (Derrotado)", value="Melhor sorte na próxima!", inline=True)
    elif tg_cur_hp <= 0:
        winner_id = challenger_id
        loser_id = target_id
        result_embed.description = f"*O narrador anuncia:*\n\n'**{ch_name}** vence o duelo gloriosamente!'"
        result_embed.color = discord.Color.red()
        xp_win = 150 + challenger["level"] * 5
        add_xp(challenger_id, xp_win)
        result_embed.add_field(name=f"🏆 {ch_name} (Vencedor)", value=f"+{xp_win} XP | +1 Vitória PvP", inline=True)
        result_embed.add_field(name=f"💀 {tg_name} (Derrotado)", value="Melhor sorte na próxima!", inline=True)
    else:
        # Decidido por HP restante
        if ch_cur_hp >= tg_cur_hp:
            winner_id = challenger_id
            result_embed.description = f"*'Tempo esgotado! **{ch_name}** tinha mais HP!'*\n\n**{ch_name} vence por resistência!**"
            xp_win = 80 + challenger["level"] * 3
            add_xp(challenger_id, xp_win)
            result_embed.add_field(name=f"🏆 {ch_name}", value=f"+{xp_win} XP", inline=True)
            result_embed.add_field(name=f"⚔️ {tg_name}", value=f"HP restante: {max(0, tg_cur_hp)}", inline=True)
        else:
            winner_id = target_id
            result_embed.description = f"*'Tempo esgotado! **{tg_name}** tinha mais HP!'*\n\n**{tg_name} vence por resistência!**"
            xp_win = 80 + target["level"] * 3
            add_xp(target_id, xp_win)
            result_embed.add_field(name=f"🏆 {tg_name}", value=f"+{xp_win} XP", inline=True)
            result_embed.add_field(name=f"⚔️ {ch_name}", value=f"HP restante: {max(0, ch_cur_hp)}", inline=True)

    result_embed.add_field(
        name="📜 Narrador Final",
        value=random.choice([
            "*'Uma batalha que será lembrada por gerações!'*",
            "*'O sangue de guerreiros corre nessas veias!'*",
            "*'Que honra testemunhar tamanha bravura!'*",
            "*'Os deuses assistiram esta batalha com interesse!'*",
            "*'Lendas nacem de combates como este!'*",
        ]),
        inline=False
    )
    await channel.send(embed=result_embed)


# ================= FUNÇÕES DE BATALHA E EXPLORAÇÃO =================

async def fight_boss(channel, user_id, is_dungeon=False, dungeon_boss=None, allies=None):
    player = get_player(user_id)

    if is_dungeon and dungeon_boss:
        boss_data = dungeon_boss
    else:
        # Check for a custom boss set via encontrar boss command
        effects = player.get("active_effects", {})
        pending_boss = effects.pop("pending_boss", None)
        if pending_boss:
            player["active_effects"] = effects
            save_player_db(user_id, player)
            boss_data = pending_boss
        else:
            boss_levels = {9: 1, 19: 10, 29: 20, 39: 30, 49: 40, 59: 50}
            world_key = boss_levels.get(player["level"])
            if world_key is None:
                # Usa boss do mundo atual — randomizado da pool de variantes
                world_level = max([k for k in WORLDS.keys() if k <= player["level"]])
                boss_pool = WORLD_BOSSES_VARIANTS.get(world_level, [])
                if boss_pool:
                    boss_data = random.choice(boss_pool)
                else:
                    boss_data = WORLDS[world_level]["boss"]
            else:
                boss_pool = WORLD_BOSSES_VARIANTS.get(world_key, [])
                if boss_pool:
                    boss_data = random.choice(boss_pool)
                else:
                    boss_data = WORLDS[world_key]["boss"]

    # Calcula bônus de aliados
    ally_bonus_roll = 0
    ally_names = []
    if allies:
        for ally_id in allies:
            if str(ally_id) != str(user_id):
                ally_player = get_player(ally_id)
                if ally_player:
                    ally_bonus_roll += 1  # +1 no dado por aliado
                    try:
                        ally_user = await bot.fetch_user(int(ally_id))
                        ally_names.append(ally_user.name)
                    except:
                        pass

    roll = roll_dice()
    if player.get("class") == "Bardo":
        roll = min(10, roll + 1)
    roll = min(10, roll + ally_bonus_roll)
    luck = get_luck(roll)

    player_atk = 0
    player_def = 0
    if player.get("class") and player["class"] in CLASSES:
        player_atk += CLASSES[player["class"]]["atk_bonus"]
        player_def += CLASSES[player["class"]]["def_bonus"]
    if player.get("pet"):
        try:
            pet_obj = json.loads(player["pet"]) if isinstance(player["pet"], str) else player["pet"]
            player_atk += pet_obj.get("bonus_atk", 0)
        except:
            for world_pets in PETS.values():
                for pet in world_pets:
                    if pet["name"] == player["pet"]:
                        player_atk += pet["bonus_atk"]

    embed = discord.Embed(
        title=f"👹 BATALHA ÉPICA",
        description=f"**{'Equipe' if ally_names else player.display_name if hasattr(player, 'display_name') else 'Você'} vs {boss_data['name']}**\n\n*O narrador narra intensamente a batalha...*",
        color=discord.Color.dark_red()
    )

    if ally_names:
        embed.add_field(name="👥 Aliados de Batalha", value="\n".join(ally_names), inline=False)
    embed.add_field(name="🎲 Dado do Destino", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

    if roll <= 4:
        result, xp_loss = remove_xp(user_id, random.randint(100, 200))
        narratives_pool = [
            [
                f"💥 *O {boss_data['name']} dá um rugido ensurdecedor que faz o chão tremer!*",
                f"⚔️ *Você avança com determinação, mas o boss desvia com velocidade sobrenatural!*",
                f"💀 *Um golpe devastador te atinge em cheio — você voa metros para trás!*",
                f"🩸 *Sangrando e exausto, você cai de joelhos. A batalha se encerra.*",
            ],
            [
                f"🌑 *{boss_data['name']} ergue os braços e o céu escurece ao redor!*",
                f"⚡ *Uma descarga de energia sombria te atravessa antes que você possa reagir!*",
                f"💫 *Sua visão gira. Seus joelhos cedem. O poder é grande demais...*",
                f"😵 *'Fraco.'* — sussurra o boss enquanto você cai.*",
            ],
            [
                f"🔥 *O {boss_data['name']} ataca com uma velocidade impossível para sua classe!*",
                f"🗡️ *Você tenta aparar o golpe mas a força é três vezes maior que a sua!*",
                f"💔 *Cada osso do seu corpo ressoa com a dor do impacto!*",
                f"🏃 *Você recua às pressas, derrotado mais uma vez pelo colosso.*",
            ],
            [
                f"👹 *{boss_data['name']} ri de você — um som que ecoa por todo o mundo!*",
                f"🌀 *Uma onda de energia te joga contra a parede com força devastadora!*",
                f"⚰️ *As estrelas piscam à sua frente enquanto a consciência escapa...*",
                f"🔴 *'Volte quando for digno.'* — ecoa na sua mente enquanto você foge.*",
            ],
        ]
        narratives = random.choice(narratives_pool)
        embed.add_field(
            name="💀 Derrota Devastadora",
            value="\n".join(narratives) + f"\n\n❌ **−{xp_loss} XP**\n\n*'Nem todo herói vence na primeira tentativa... Treine mais!'*",
            inline=False
        )
        if result == "reset":
            embed.add_field(
                name="🌑 Fim da Jornada",
                value="*'Sua visão escurece... tudo que você conquistou se perde nas sombras...'*\n\n**Você desperta novamente nos Campos Iniciais, sem memórias.**",
                inline=False
            )
            embed.color = discord.Color.black()

    elif roll <= 6:
        result, xp_loss = remove_xp(user_id, random.randint(50, 80))
        narratives_pool = [
            [
                f"⚔️ *Você e o {boss_data['name']} trocam golpes por longos minutos!*",
                f"💢 *Cada ataque seu encontra uma defesa. Cada golpe dele, você desvia por pouco!*",
                f"😰 *Mas a resistência não é eterna — você começa a ceder...*",
                f"🚪 *Ferido e esgotado, você recua antes que seja tarde demais.*",
            ],
            [
                f"🔥 *A batalha é intensa! Você está se saindo melhor que da última vez!*",
                f"💥 *Você até acerta o boss! Mas ele mal sente o impacto...*",
                f"😤 *'Interessante.'* — diz o boss, pela primeira vez te levando a sério.*",
                f"🩹 *Mas o preço foi alto. Você precisa de mais poder para vencer.*",
            ],
        ]
        narratives = random.choice(narratives_pool)
        embed.add_field(
            name="😰 Empate Amargo",
            value="\n".join(narratives) + f"\n\n❌ **−{xp_loss} XP**\n\n*'Você está mais próximo. Continue tentando.'*",
            inline=False
        )
        embed.color = discord.Color.orange()

    else:
        xp = boss_data["xp"] + (300 if roll >= 9 else 100)
        coins = max(1, random.randint(boss_data["coins"][0] // 3, boss_data["coins"][1] // 3))

        if boss_data["name"] not in player["bosses"]:
            player["bosses"].append(boss_data["name"])

        save_player_db(user_id, player)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)

        # Drop de poção do boss
        if random.random() < 0.3:
            potion_rarities = ["Raro", "Épico", "Lendário"]
            weights = [50, 35, 15]
            chosen_rarity = random.choices(potion_rarities, weights=weights)[0]
            potions_of_rarity = [name for name, data in POTIONS.items() if data["rarity"] == chosen_rarity]
            if potions_of_rarity:
                dropped_potion = random.choice(potions_of_rarity)
                player = get_player(user_id)
                player["inventory"].append(dropped_potion)
                save_player_db(user_id, player)

        narratives_pool = [
            [
                f"⚡ *Você esquiva do primeiro golpe do {boss_data['name']} com precisão cirúrgica!*",
                f"🗡️ *Contra-ataca na abertura perfeita — o boss recua pela primeira vez!*",
                f"💫 *A batalha se intensifica, mas você mantém a vantagem!*",
                f"✨ *Um golpe final com toda sua força — o {boss_data['name']} cai rugindo!*",
                f"🌟 *Um silêncio épico... e então o chão treme com a queda do colosso.*",
            ],
            [
                f"🔥 *'Você está diferente hoje!'* — grunhe o {boss_data['name']} sentindo sua força!*",
                f"⚔️ *Uma sequência de ataques impecáveis — cada golpe encontra seu alvo!*",
                f"💥 *O boss tenta sua técnica mais letal... mas você já conhecia o movimento!*",
                f"🏆 *Com um grito de vitória, você desferindo o golpe decisivo!*",
                f"👑 *{boss_data['name']} cai de joelhos. Derrotado. Por você.*",
            ],
            [
                f"🌀 *A batalha começa com uma explosão de energia que ilumina o céu!*",
                f"😤 *Você absorve cada golpe e responde com o dobro de força!*",
                f"🩸 *O boss sangra — algo que parecia impossível até agora!*",
                f"💀 *'Como...?!'* — não consegue terminar a frase. O golpe final o cala.*",
                f"🎺 *Lendas serão contadas desta batalha por gerações.*",
            ],
        ]
        narratives = random.choice(narratives_pool)

        embed.add_field(
            name="🏆 VITÓRIA GLORIOSA!",
            value="\n".join(narratives) + f"\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**\n\n*'Uma lenda nasce!'*",
            inline=False
        )

        # Desbloqueia próximo mundo APENAS ao derrotar boss
        boss_to_world = {
            "Slime Rei": 10, "Ent Ancião": 20, "Faraó Amaldiçoado": 30,
            "Yeti Colossal": 40, "Dragão de Magma": 50, "Senhor das Sombras": 60
        }
        next_world = boss_to_world.get(boss_data["name"])
        if next_world and next_world in WORLDS:
            player = get_player(user_id)
            if next_world not in player["worlds"]:
                player["worlds"].append(next_world)
                save_player_db(user_id, player)
                embed.add_field(
                    name="🗺️ Novo Mundo Revelado!",
                    value=f"*'As correntes se rompem! As névoas se dissipam!'*\n\n{WORLDS[next_world]['emoji']} **{WORLDS[next_world]['name']}** foi desbloqueado!\n\n*'Novos desafios — e novas glórias — aguardam!'*",
                    inline=False
                )

        if roll >= 9:
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            legendary = [i for i in ITEMS[item_list] if i["rarity"] in ["Lendário", "Mítico", "Divino"]]
            item = random.choice(legendary)

            embed.add_field(
                name="🌟 Drop Lendário!",
                value=f"Do corpo do {boss_data['name']} surge:\n\n{RARITIES[item['rarity']]['emoji']} **{item['name']}**\n\n*'Os deuses sorriem para você!'*",
                inline=False
            )

            await channel.send(embed=embed)
            await asyncio.sleep(1)
            view = EquipButton(user_id, item["name"], item_type)
            await channel.send(
                f"⚔️ **{item['name']}** brilha em suas mãos!\n\n*'Deseja equipar?'*", view=view
            )
            return

        if leveled:
            player = get_player(user_id)
            embed.add_field(name="🆙 Ascensão!", value=f"*'Seu corpo pulsa com nova energia!'*\n\n**Nível {player['level']}**", inline=False)

        embed.color = discord.Color.gold()

    await channel.send(embed=embed)


async def explore_dungeon(channel, user_id, dungeon, world):
    player = get_player(user_id)
    roll = roll_with_bonus(player)
    luck = get_luck(roll)
    is_secret = dungeon.get("secret", False)
    level_mult = get_dungeon_difficulty_multiplier(player)  # mais difícil por nível

    SECRET_EVENTS = [
        "🌑 *As paredes sangram símbolos antigos...*",
        "👁️ *Mil olhos te observam das trevas...*",
        "🌀 *A realidade distorce ao seu redor...*",
        "⚡ *Energia arcana pulsa sob seus pés...*",
        "🔮 *Vozes sussurram segredos proibidos...*",
    ]

    flavor = random.choice(SECRET_EVENTS) if is_secret else "*A dungeon é escura e úmida... Você sente perigo em cada sombra.*"

    embed = discord.Embed(
        title=f"{'🔮 MASMORRA SECRETA:' if is_secret else '🏛️'} {dungeon['name']}",
        description=flavor,
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="🎲 Dado da Exploração", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

    if is_secret:
        embed.set_footer(text=f"⚔️ Masmorra Secreta — Dificuldade ×{level_mult:.1f} | Recompensas ×{level_mult:.1f}")

    if roll == 1:
        dmg = int(random.randint(40, 70) * (level_mult if is_secret else 1))
        player["hp"] -= dmg
        if player["hp"] <= 0:
            player["hp"] = player["max_hp"] // 3
        save_player_db(user_id, player)
        xp_loss_base = random.randint(150, 250) if is_secret else random.randint(100, 150)
        xp_loss_total = int(xp_loss_base * level_mult)
        result, xp_loss = remove_xp(user_id, xp_loss_total)

        trap_msgs = [
            "Uma armadilha de cristal explode ao seu toque! Fragmentos cortam por todo lado!",
            "Garras gigantes surgem do chão! Você é lançado contra a parede!",
            "O teto desaba em blocos de pedra mágica! Esmagamento inevitável!",
            "Um campo arcano eletrifica tudo ao redor! Você convulsiona de dor!",
        ] if is_secret else ["Uma armadilha antiga é ativada! Lâminas surgem de todas as direções!"]

        embed.add_field(
            name="💀 ARMADILHA MORTAL!",
            value=f"*'{random.choice(trap_msgs)}'*\n\n❌ **−{xp_loss} XP**\n💔 **−{dmg} HP**",
            inline=False
        )
        embed.color = discord.Color.dark_red()

    elif roll <= 3:
        xp_loss_base = random.randint(80, 120) if is_secret else random.randint(50, 80)
        xp_loss_total = int(xp_loss_base * (level_mult if is_secret else 1))
        result, xp_loss = remove_xp(user_id, xp_loss_total)
        if is_secret:
            msgs = [
                "Entidades do vazio bloqueiam seu caminho e drenam sua energia!",
                "Um labirinto dimensional te faz andar em círculos por horas!",
                "A masmorra te estuda. Você sai mais fraco do que entrou.",
            ]
            embed.add_field(
                name="☠️ Pesadelo Dimensional",
                value=f"*'{random.choice(msgs)}'*\n\n❌ **−{xp_loss} XP**",
                inline=False
            )
        else:
            embed.add_field(
                name="☠️ Exploração Perigosa",
                value=f"*'Você se perde nos corredores sombrios...'*\n\n❌ **−{xp_loss} XP**",
                inline=False
            )
        embed.color = discord.Color.red()

    elif roll <= 5:
        resources = random.sample(world["resources"], min(3 if is_secret else 2, len(world["resources"])))
        for r in resources:
            player["inventory"].append(r)
        save_player_db(user_id, player)
        items_text = "\n".join([f"• **{r}**" for r in resources])
        xp_bonus = int(random.randint(100, 200) * (level_mult if is_secret else 1))
        add_xp(user_id, xp_bonus)
        embed.add_field(
            name="📦 Câmara de Recursos",
            value=f"*'Uma câmara intocada há séculos...'*\n\n{items_text}\n⭐ **+{xp_bonus} XP**", inline=False
        )
        embed.color = discord.Color.blue()

    elif roll <= 7:
        xp_base = random.randint(500, 900) if is_secret else random.randint(80, 150)
        coins_base = random.randint(20, 50) if is_secret else random.randint(10, 25)
        xp = int(xp_base * level_mult)
        coins = int(coins_base * level_mult)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)

        if random.random() < (0.50 if is_secret else 0.25):
            potion_list = list(POTIONS.keys())
            dropped_potion = random.choice(potion_list[-5:] if is_secret else potion_list)
            player = get_player(user_id)
            player["inventory"].append(dropped_potion)
            save_player_db(user_id, player)

        embed.add_field(
            name="💎 Câmara do Tesouro!",
            value=f"*'{'Um tesouro ancestral brilha com luz própria!' if is_secret else 'Você encontra um baú antigo cheio de riquezas!'}'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**",
            inline=False
        )
        if leveled:
            player = get_player(user_id)
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        embed.color = discord.Color.green()

    elif roll <= 9:
        item_type = random.choice(["weapon", "armor"])
        item_list = "weapons" if item_type == "weapon" else "armor"
        if is_secret:
            rarity_pool = ["Mítico", "Divino", "Primordial"]
            weights = [50, 35, 15]
        else:
            rarity_pool = ["Raro", "Épico", "Lendário"]
            weights = [40, 40, 20]
        rarity = random.choices(rarity_pool, weights=weights)[0]
        items_filtered = [i for i in ITEMS[item_list] if i["rarity"] == rarity]
        item = random.choice(items_filtered) if items_filtered else random.choice(ITEMS[item_list])

        xp_base = random.randint(800, 1500) if is_secret else random.randint(120, 200)
        coins_base = random.randint(30, 80) if is_secret else random.randint(15, 35)
        xp = int(xp_base * level_mult)
        coins = int(coins_base * level_mult)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)

        rarity_info = RARITIES[item["rarity"]]
        embed.add_field(
            name=f"{'🌟 ITEM LENDÁRIO DA MASMORRA!' if is_secret else '✨ Equipamento Raro!'}",
            value=f"*'{'Um artefato que não deveria existir...' if is_secret else 'Em uma sala secreta, você encontra um equipamento magnífico!'}'*\n\n{rarity_info['emoji']} **{item['name']}**\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**",
            inline=False
        )
        if leveled:
            player = get_player(user_id)
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        embed.color = rarity_info["color"]

        await channel.send(embed=embed)
        await asyncio.sleep(1)
        view = EquipButton(user_id, item["name"], item_type)
        await channel.send(f"✨ **{item['name']}** aguarda por você!\n\n*'Deseja equipar?'*", view=view)
        return

    else:  # roll == 10
        if is_secret:
            boss_power_msgs = [
                "👁️ *Uma entidade primordial abre os olhos. Ela existia antes do tempo.*",
                "🌑 *O guardião final da masmorra desperta. Você sentiu isso vindo.*",
                "💀 *Morte personificada bloqueia a câmara central. Não há fuga.*",
            ]
            embed.add_field(
                name="👹 GUARDIÃO FINAL DA MASMORRA SECRETA!",
                value=f"{random.choice(boss_power_msgs)}\n\n**{dungeon['boss']}** surge das sombras com poder incompreensível!",
                inline=False
            )
        else:
            embed.add_field(
                name="👹 O BOSS APARECE!",
                value=f"*'No fim da dungeon, uma presença maligna surge!\n\n**{dungeon['boss']}** bloqueia seu caminho!'*",
                inline=False
            )
        embed.color = discord.Color.dark_red()
        await channel.send(embed=embed)
        await asyncio.sleep(2)

        # Boss de dungeon secreta é MUITO mais forte
        if is_secret:
            boss_data = {
                "name": dungeon["boss"],
                "hp": int((500 + dungeon["level"] * 100) * level_mult),
                "atk": int((45 + dungeon["level"] * 8) * level_mult),
                "xp": int((1000 + dungeon["level"] * 200) * level_mult),
                "coins": (int((30 + dungeon["level"] * 5) * level_mult), int((80 + dungeon["level"] * 10) * level_mult))
            }
        else:
            boss_data = {
                "name": dungeon["boss"],
                "hp": 200 + (dungeon["level"] * 50),
                "atk": 20 + (dungeon["level"] * 3),
                "xp": 150 + (dungeon["level"] * 40),
                "coins": (10 + dungeon["level"] * 2, 25 + dungeon["level"] * 4)
            }
        await fight_boss(channel, user_id, is_dungeon=True, dungeon_boss=boss_data)
        return

    await channel.send(embed=embed)

# ================= TAREFAS PERIÓDICAS =================

@tasks.loop(minutes=20)
async def random_world_events():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=CANAL_BETA)
        if not channel:
            continue

        event_type = random.choice(["structure", "narrator", "merchant", "pet", "book"])

        if event_type == "structure":
            structure = random.choice(STRUCTURES)
            embed = discord.Embed(
                title=f"{structure['name']} Avistada!",
                description=f"*'{structure['narrator']}'*",
                color=discord.Color.purple()
            )
            embed.add_field(name="📍 Descrição", value=structure["description"], inline=False)
            await channel.send(embed=embed)

        elif event_type == "narrator":
            warning = random.choice(NARRATOR_WARNINGS)
            try:
                members = [m for m in guild.members if not m.bot]
                if members:
                    random_member = random.choice(members)
                    embed = discord.Embed(
                        title="📖 O Narrador Fala",
                        description=f"*Uma voz ecoa direcionada a {random_member.mention}...*\n\n**\"{warning}\"**",
                        color=discord.Color.dark_gold()
                    )
                    await channel.send(embed=embed)
            except:
                pass

        elif event_type == "merchant":
            items_for_sale = []
            weapon = random.choice([i for i in ITEMS["weapons"] if i["rarity"] in ["Incomum", "Raro", "Épico"]])
            weapon_price = {"Incomum": 300, "Raro": 900, "Épico": 2000}[weapon["rarity"]]
            items_for_sale.append({"name": weapon["name"], "type": "weapon", "price": weapon_price})

            armor = random.choice([i for i in ITEMS["armor"] if i["rarity"] in ["Incomum", "Raro", "Épico"]])
            armor_price = {"Incomum": 300, "Raro": 900, "Épico": 2000}[armor["rarity"]]
            items_for_sale.append({"name": armor["name"], "type": "armor", "price": armor_price})

            items_for_sale.append({"name": "Poção de Vida", "type": "potion", "price": 150})

            embed = discord.Embed(
                title="🏪 Mercador Errante Apareceu!",
                description="*'Um mercador misterioso surge do nada oferecendo seus produtos...'*",
                color=discord.Color.gold()
            )
            for i, item in enumerate(items_for_sale, 1):
                embed.add_field(name=f"Item {i}: {item['name']}", value=f"💰 **Preço: {item['price']} CSI**", inline=False)

            await channel.send(embed=embed, view=ShopButton(None, items_for_sale))

        elif event_type == "pet":
            world_levels = list(PETS.keys())
            chosen_world = random.choice(world_levels)
            pet = random.choice(PETS[chosen_world])
            embed = discord.Embed(
                title=f"{pet['emoji']} Criatura Selvagem Apareceu!",
                description=f"*'Um **{pet['name']}** selvagem aparece no horizonte!'*",
                color=RARITIES[pet["rarity"]]["color"]
            )
            embed.add_field(name="✨ Raridade", value=f"{RARITIES[pet['rarity']]['emoji']} {pet['rarity']}", inline=True)
            embed.add_field(name="💪 Bônus ATK", value=f"+{pet['bonus_atk']}", inline=True)
            embed.add_field(name="❤️ Bônus HP", value=f"+{pet['bonus_hp']}", inline=True)
            embed.set_footer(text="Use 'domesticar' para tentar capturá-lo!")
            await channel.send(embed=embed)

        elif event_type == "book":
            # Livro de lore aleatório aparece
            world_key = random.choice(list(LORE_BOOKS.keys()))
            book = random.choice(LORE_BOOKS[world_key])
            embed = discord.Embed(
                title=f"📚 Um Livro Antigo Foi Encontrado!",
                description=f"*'As páginas se abrem sozinhas...'*",
                color=discord.Color.dark_gold()
            )
            embed.add_field(name=book["title"], value=book["content"][:1024], inline=False)
            await channel.send(embed=embed)


# ================= PRÓLOGO =================
async def send_prologue(guild):
    channel = discord.utils.get(guild.text_channels, name=CANAL_BETA)
    if not channel:
        return

    await asyncio.sleep(1)

    # ══════════════════════════════════════════
    # EMBED 1 — Abertura épica do narrador
    # ══════════════════════════════════════════
    embed1 = discord.Embed(
        title="📖  W O R L D   C S I  📖",
        description=(
            "```\n"
            "╔══════════════════════════════════════╗\n"
            "║   O Narrador Desperta...             ║\n"
            "║   Uma Nova Saga Começa Aqui.         ║\n"
            "╚══════════════════════════════════════╝\n"
            "```\n"
            "*Uma voz grave ecoa por todo o servidor...*\n\n"
            "**\"No princípio, havia apenas o Vazio — um silêncio perfeito e eterno.**\n"
            "Então, a Primeira Chama surgiu do nada, e com ela nasceu o Mundo.\n\n"
            "Sete reinos se formaram das cinzas da criação.\n"
            "Cada um guarda segredos que poucos ousam descobrir.\n"
            "Cada um testa aqueles que o atravessam de formas diferentes.\n\n"
            "**Você... é o próximo herói desta história.**\n"
            "Ou talvez o próximo vilão. O destino é seu para escrever.\"\n\n"
            "*— O Narrador, antes que a história comece*"
        ),
        color=0x2C2F33
    )
    embed1.set_footer(text="🎭 O Narrador observa cada passo seu...")
    await channel.send(embed=embed1)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 2 — Os Sete Reinos (lore)
    # ══════════════════════════════════════════
    embed2 = discord.Embed(
        title="🗺️ Os Sete Reinos do Mundo",
        description="*O pergaminho se desenrola revelando terras que poucos mortais conhecem...*",
        color=0x8B4513
    )
    embed2.add_field(
        name="🌱 Campos Iniciais — O Berço",
        value=(
            "*\"Todo herói começa aqui. Não existe vergonha no começo humilde.\n"
            "O guerreiro mais poderoso que existiu começou matando um slime.\"*\n"
            "— Historiador Pell\n\n"
            "Terras abertas onde os primeiros seres vivos deram seus primeiros passos.\n"
            "O Slime Rei reina sobre estas planícies... por enquanto."
        ),
        inline=False
    )
    embed2.add_field(
        name="🌲 Floresta Sombria — A Que Respira",
        value=(
            "*\"A floresta não é apenas árvores. Ela é um ser vivo, consciente,\n"
            "e muito, muito antiga. Ela ouve você. E lembra de tudo.\"*\n"
            "— Druida Sylvara\n\n"
            "O Ent Ancião de 3.000 anos guarda segredos que nenhum livro registrou.\n"
            "Os sussurros entre os galhos contam histórias do tempo dos dragões."
        ),
        inline=False
    )
    embed2.add_field(
        name="🏜️ Deserto das Almas — O Jardim Perdido",
        value=(
            "*\"Esta areia foi mar profundo uma vez. Sob ela ainda dormem\n"
            "as maravilhas do jardim original — esperando um digno.\"*\n"
            "— Sábia Nefertiri\n\n"
            "O Faraó Kha-Mentu foi traído por seus sacerdotes e amaldiçoado\n"
            "para guardar seus próprios tesouros por toda a eternidade."
        ),
        inline=False
    )
    await channel.send(embed=embed2)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 3 — Mais reinos
    # ══════════════════════════════════════════
    embed3 = discord.Embed(
        title="🗺️ Os Reinos Além",
        description="*...o pergaminho continua se desenrolando...*",
        color=0x4B0082
    )
    embed3.add_field(
        name="❄️ Montanhas Geladas — O Grito dos Titãs",
        value=(
            "*\"Vivi 80 invernos nestas montanhas. O frio não é inimigo — é professor.\n"
            "O Yeti não é um monstro. É um guardião mal compreendido.\"*\n"
            "— Ancião Bjorn\n\n"
            "Os Titãs do Gelo criaram o Cristal do Inverno Eterno — um arquivo\n"
            "de tudo que já morreu no frio. O Yeti Colossal sente cada memória."
        ),
        inline=False
    )
    embed3.add_field(
        name="🌋 Reino Vulcânico — Onde o Fogo Pensa",
        value=(
            "*\"O fogo não destrói. Transforma. Os Forjadores sabiam disso —\n"
            "por isso criaram armas que tinham alma.\"*\n"
            "— Profeta Ignar\n\n"
            "Ignarius, o Dragão de Magma, é o segundo elemento.\n"
            "Dentro dele vivem as memórias de uma civilização inteira."
        ),
        inline=False
    )
    embed3.add_field(
        name="🌌 Abismo Arcano — O Antes e o Depois",
        value=(
            "*\"Quanto mais você sabe, mais entende que não sabe nada.\n"
            "As entidades do Vazio não são más. São antigas demais.\"*\n"
            "— Arquimago Zephyr\n\n"
            "Cada alma que nasce vem do Abismo. Cada alma que morre, retorna.\n"
            "O Senhor das Sombras administra esse trânsito eterno."
        ),
        inline=False
    )
    embed3.add_field(
        name="👑 Trono Celestial — O Teste Final",
        value=(
            "*\"O Imperador Astral não é um inimigo — é o último teste.\n"
            "O Trono não é um lugar. É um estado de ser.\"*\n"
            "— Guardião Estelar Auron\n\n"
            "Aquele que chegar aqui não será mais mortal.\n"
            "A história foi escrita. Apenas você decide como ela termina."
        ),
        inline=False
    )
    await channel.send(embed=embed3)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 4 — Lore: A Guerra Primordial
    # ══════════════════════════════════════════
    embed4 = discord.Embed(
        title="📜 Crônicas da Guerra Primordial",
        description=(
            "*Um livro antigo se abre sozinho nas páginas proibidas...*\n\n"
            "**'O Que Existia Antes do Tempo'**\n\n"
            "Antes que o universo existisse, houve uma guerra.\n\n"
            "De um lado: a **Luz Primordial**, que queria existência, forma, vida.\n"
            "Do outro: o **Vazio Eterno**, que queria silêncio, paz, nada.\n\n"
            "Eles lutaram por uma eternidade que não tinha nome ainda.\n"
            "A batalha terminou sem vencedor — ambos exaustos, fizeram um acordo:\n"
            "criariam algo novo. Algo que contivesse os dois.\n\n"
            "Chamaram isso de ***Universo***.\n\n"
            "E plantaram dentro de cada ser vivo uma centelha de cada lado.\n"
            "*É por isso que todo ser carrega tanto amor quanto destruição.*\n\n"
            "**A guerra não terminou. Apenas mudou de palco.**\n\n"
            "*— Fragmento encontrado no 'Além do Trono', autor desconhecido*"
        ),
        color=0x1a0033
    )
    embed4.set_footer(text="📚 Lore desbloqueável: explore o mundo para encontrar mais fragmentos.")
    await channel.send(embed=embed4)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 5 — Sistema de Alinhamento
    # ══════════════════════════════════════════
    embed5 = discord.Embed(
        title="⚖️ O Peso das Escolhas",
        description=(
            "*O Narrador observa você com olhos que viram mil histórias...*\n\n"
            "**Neste mundo, suas ações têm consequências morais.**\n\n"
            "Salvar uma cidade ou saqueá-la.\n"
            "Ajudar um viajante ou roubá-lo.\n"
            "Proteger os inocentes ou usá-los como escudo.\n\n"
            "Cada escolha molda quem você é:"
        ),
        color=0x9B59B6
    )
    embed5.add_field(
        name="✨ Herói (+30 pontos ou mais)",
        value="*'Sua luz guia aqueles que estão perdidos.'*\nAcesso a missões de proteção, recompensas divinas e respeito do povo.",
        inline=False
    )
    embed5.add_field(
        name="⚖️ Anti-Herói (-5 a -29 pontos)",
        value="*'Você faz o bem pelos motivos errados... ou o errado pelos motivos certos.'*\nMissões de moral cinza com recompensas únicas.",
        inline=False
    )
    embed5.add_field(
        name="💀 Vilão (-30 pontos ou menos)",
        value="*'O poder não se pede. Se toma.'*\nMissões de conquista e destruição com XP massivo — e consequências.",
        inline=False
    )
    embed5.add_field(
        name="🎭 Como funciona",
        value="Use `cenário` para enfrentar dilemas morais!\nUse `alinhamento` para ver seu estado atual.",
        inline=False
    )
    await channel.send(embed=embed5)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 6 — Empregos e Títulos
    # ══════════════════════════════════════════
    embed6 = discord.Embed(
        title="💼 Empregos & Títulos do Reino",
        description=(
            "*O taberneiro pregou uma lista de oportunidades na parede...*\n\n"
            "**A partir do nível 5**, você pode trabalhar e ganhar salário!\n"
            "Cada emprego tem benefícios únicos que afetam sua jornada."
        ),
        color=0xE67E22
    )
    embed6.add_field(name="⚒️ Ferreiro (Nv.5)", value="Forja armas únicas, 20% desc. em lojas", inline=True)
    embed6.add_field(name="🔮 Arcano (Nv.5)", value="+15 mana máx, acesso a grimórios", inline=True)
    embed6.add_field(name="💚 Curandeiro (Nv.5)", value="Cura aliados, poções 30% mais baratas", inline=True)
    embed6.add_field(name="💰 Mercador (Nv.5)", value="Vende 25% a mais, mercado negro", inline=True)
    embed6.add_field(name="📜 Escriba (Nv.5)", value="Descobre locais 2× mais rápido", inline=True)
    embed6.add_field(name="⚔️ Cavaleiro (Nv.10)", value="+20 HP, defende cidades de invasões", inline=True)
    embed6.add_field(name="🛡️ Guarda Real (Nv.15)", value="+35 HP, comanda a guarda do reino", inline=True)
    embed6.add_field(name="👑 Rei (Nv.30)", value="Governa, nomeia cavaleiros, recebe tributo", inline=True)
    embed6.add_field(
        name="📣 Como começar",
        value="`procurar emprego` → escolha sua profissão → `trabalhar` a cada 30 min!",
        inline=False
    )
    await channel.send(embed=embed6)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 7 — Comandos completos
    # ══════════════════════════════════════════
    embed7 = discord.Embed(
        title="⚔️ Guia de Comandos",
        description="*Tudo que você precisa para começar sua lenda:*",
        color=0x3498DB
    )
    embed7.add_field(
        name="🌍 Exploração",
        value="`explorar` | `caçar` | `coletar` | `minerar` | `dungeon` | `procurar pet` | `procurar cidade`",
        inline=False
    )
    embed7.add_field(
        name="👹 Boss & Combate",
        value="`encontrar boss` | `desafiar boss` | `juntar boss` | `iniciar batalha boss` | `desafiar @jogador`",
        inline=False
    )
    embed7.add_field(
        name="📋 Quests & Moral",
        value="`ver quests` | `realizar quest` | `finalizar quest` | `cenário` | `missão moral` | `alinhamento`",
        inline=False
    )
    embed7.add_field(
        name="👤 Personagem",
        value="`ver perfil` | `inventário` | `escolher classe` | `ver mana` | `ver emprego`",
        inline=False
    )
    embed7.add_field(
        name="🐾 Pets & Fazenda",
        value="`fazenda` | `trocar pet` | `guardar pet` | `procurar pet` | `domesticar`",
        inline=False
    )
    embed7.add_field(
        name="💼 Empregos & Títulos",
        value="`procurar emprego` | `trabalhar` | `largar emprego` | `me tornar rei` | `defender cidade`",
        inline=False
    )
    embed7.add_field(
        name="🗺️ Mapa & Viagem",
        value="`abrir mapa` | `viajar <local>` | `procurar cidade`",
        inline=False
    )
    embed7.add_field(
        name="🏰 Social & Guilda",
        value="`criar guilda` | `entrar guilda` | `ver guilda` | `trocar [item] com @user`",
        inline=False
    )
    embed7.add_field(
        name="🛒 Itens & Economia",
        value="`[poção], usar` | `vender [item]` | `equipar [item]` | `trocar coins <valor>` | `minerar baú`",
        inline=False
    )
    embed7.add_field(
        name="📚 Lore",
        value="`falar npc especial` | `procurar cidade` — descubra histórias dos NPCs e livros escondidos!",
        inline=False
    )
    embed7.set_footer(text="🌟 \"E assim, uma nova história começa...\" — O Narrador")
    await channel.send(embed=embed7)
    await asyncio.sleep(1)

    # ══════════════════════════════════════════
    # MENSAGEM FINAL — Chamada para ação
    # ══════════════════════════════════════════
    embed8 = discord.Embed(
        title="🌟 Sua Jornada Começa Agora",
        description=(
            "*O Narrador fecha o livro e te olha diretamente...*\n\n"
            "**\"Você está pronto? Ou acha que está?\"**\n\n"
            "Os Campos Iniciais aguardam seus primeiros passos.\n"
            "Um Slime está por aí, inocente demais para saber o que está prestes a acontecer.\n\n"
            "Use `explorar` para começar.\n"
            "Use `ver perfil` para ver seu estado.\n"
            "Use `escolher classe` quando chegar ao nível 2.\n\n"
            "*Lembre-se: toda lenda começa com um único passo.*\n\n"
            "**Boa sorte, aventureiro. Você vai precisar.** 🎭"
        ),
        color=0xF1C40F
    )
    embed8.set_footer(text="⚠️ O boss só aparece nos níveis 9, 19, 29, 39, 49, 59 — e só passará de reino ao vencê-lo!")
    await channel.send(embed=embed8)


# ================= EVENTOS DO BOT =================

@bot.event
async def on_ready():
    init_db()
    print(f"🎮 {bot.user} está online!")
    print(f"📊 Servidores: {len(bot.guilds)}")

    if not random_world_events.is_running():
        random_world_events.start()

    for guild in bot.guilds:
        await send_prologue(guild)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA:
        return

    content = message.content.lower().strip()
    user_id = message.author.id

    # ======================================================
    # ================= USAR POÇÃO (novo formato) ==========
    # ======================================================
    # Formato: "poção de vida, usar" ou "elixir de xp, usar" etc.
    if ", usar" in content or ",usar" in content:
        clean = content.replace(",usar", ", usar")
        item_part = clean.split(", usar")[0].strip()

        player = get_player(user_id)

        # Tenta encontrar a poção
        found_potion = None
        for potion_name in POTIONS.keys():
            if item_part in potion_name.lower():
                found_potion = potion_name
                break

        # Tenta encontrar equipamento a equipar
        if not found_potion:
            found_weapon = None
            found_armor = None
            for w in ITEMS["weapons"]:
                if item_part in w["name"].lower() and w["name"] in player["inventory"]:
                    found_weapon = w
                    break
            for a in ITEMS["armor"]:
                if item_part in a["name"].lower() and a["name"] in player["inventory"]:
                    found_armor = a
                    break

            if found_weapon:
                player["weapon"] = found_weapon["name"]
                save_player_db(user_id, player)
                await message.channel.send(f"⚔️ **{found_weapon['name']}** equipado!")
                return
            elif found_armor:
                player["armor"] = found_armor["name"]
                save_player_db(user_id, player)
                await message.channel.send(f"🛡️ **{found_armor['name']}** equipado!")
                return
            else:
                await message.channel.send(f"❌ Item **{item_part}** não encontrado no inventário!")
                return

        if found_potion not in player["inventory"]:
            await message.channel.send(f"❌ Você não tem **{found_potion}**!")
            return

        potion = POTIONS[found_potion]
        player["inventory"].remove(found_potion)

        embed = discord.Embed(
            title=f"{potion['emoji']} Poção Consumida!",
            description=f"*'Você bebe **{found_potion}**...'*",
            color=RARITIES.get(potion["rarity"], {"color": 0xFFFFFF})["color"]
        )

        if "hp_restore" in potion:
            old_hp = player["hp"]
            player["hp"] = min(player["hp"] + potion["hp_restore"], player["max_hp"])
            healed = player["hp"] - old_hp
            embed.add_field(name="💚 HP Restaurado", value=f"+{healed} HP", inline=False)

        if "xp_gain" in potion:
            add_xp(user_id, potion["xp_gain"])
            embed.add_field(name="⭐ XP Ganho", value=f"+{potion['xp_gain']} XP", inline=False)

        if "revive" in potion and potion["revive"]:
            player["hp"] = player["max_hp"]
            embed.add_field(name="💀 Ressurreição", value="HP completamente restaurado!", inline=False)

        save_player_db(user_id, player)
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= EQUIPAR ITEM =======================
    # ======================================================
    if content.startswith("equipar "):
        item_name_search = content[8:].strip()
        player = get_player(user_id)

        found_item = None
        item_type = None
        for w in ITEMS["weapons"]:
            if item_name_search in w["name"].lower() and w["name"] in player["inventory"]:
                found_item = w["name"]
                item_type = "weapon"
                break
        if not found_item:
            for a in ITEMS["armor"]:
                if item_name_search in a["name"].lower() and a["name"] in player["inventory"]:
                    found_item = a["name"]
                    item_type = "armor"
                    break

        if not found_item:
            await message.channel.send(f"❌ Item não encontrado no inventário. Verifique com `inventário`.")
            return

        view = EquipButton(user_id, found_item, item_type)
        await message.channel.send(f"⚔️ **{found_item}** encontrado!\n\n*Deseja equipar?*", view=view)
        return

    # ======================================================
    # ================= ESCOLHER CLASSE ====================
    # ======================================================
    if any(word in content for word in ["escolher classe", "ver classes", "classes"]):
        player = get_player(user_id)

        if player.get("class"):
            await message.channel.send(f"❌ Você já é um **{player['class']}**! Não pode mudar de classe.")
            return
        if player["level"] < 2:
            await message.channel.send("❌ Você precisa ser **nível 2** para escolher uma classe!")
            return

        embed = discord.Embed(
            title="🎭 Escolha sua Classe",
            description="*'Qual caminho você deseja seguir?'*",
            color=discord.Color.blue()
        )
        for class_name in list(CLASSES.keys())[:5]:
            class_data = CLASSES[class_name]
            embed.add_field(
                name=f"{class_data['emoji']} {class_name}",
                value=f"{class_data['description']}\n**ATK:** +{class_data['atk_bonus']} | **DEF:** +{class_data['def_bonus']} | **HP:** +{class_data['hp_bonus']}",
                inline=False
            )
        view = ClassSelectButton(user_id)
        await message.channel.send(embed=embed, view=view)
        await asyncio.sleep(1)

        embed2 = discord.Embed(title="🎭 Mais Classes", color=discord.Color.blue())
        for class_name in list(CLASSES.keys())[5:]:
            class_data = CLASSES[class_name]
            embed2.add_field(
                name=f"{class_data['emoji']} {class_name}",
                value=f"{class_data['description']}\n**ATK:** +{class_data['atk_bonus']} | **DEF:** +{class_data['def_bonus']} | **HP:** +{class_data['hp_bonus']}",
                inline=False
            )
        view2 = ClassSelectButton2(user_id)
        await message.channel.send(embed=embed2, view=view2)
        return

    # ======================================================
    # ================= PROCURAR PET =======================
    # ======================================================
    elif any(word in content for word in ["procurar pet", "procurar criatura", "buscar pet"]):
        player = get_player(user_id)

        if player.get("pet"):
            await message.channel.send(f"❌ Você já tem um pet: **{player['pet']}**!")
            return

        world = get_world(player["level"], player)
        roll = roll_dice()
        luck = get_luck(roll)

        embed = discord.Embed(
            title="🔍 Procurando Criaturas...",
            description="*'Você vasculha o ambiente em busca de criaturas selvagens...'*",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado da Busca", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 2:
            # Encontra inimigo em vez de pet
            monster_name = random.choice(list(world["monsters"].keys()))
            monster = world["monsters"][monster_name]
            dmg = random.randint(15, 35)
            player["hp"] -= dmg
            if player["hp"] <= 0:
                player["hp"] = 1
            save_player_db(user_id, player)
            result, xp_loss = remove_xp(user_id, random.randint(20, 40))

            embed.add_field(
                name="⚠️ Emboscada!",
                value=f"*'Em vez de um pet, você encontra um **{monster_name}** furioso que te ataca!'*\n\n💔 **−{dmg} HP**\n❌ **−{xp_loss} XP**",
                inline=False
            )
            embed.color = discord.Color.red()
            await message.channel.send(embed=embed)
            return

        elif roll <= 4:
            embed.add_field(
                name="😔 Nada Encontrado",
                value="*'Você vasculha por horas, mas só encontra rastros. As criaturas parecem evitar você.'*",
                inline=False
            )
            embed.color = discord.Color.light_grey()
            await message.channel.send(embed=embed)
            return

        elif roll <= 6:
            # Pet comum do mundo
            world_level = max([k for k in PETS.keys() if k <= player["level"]])
            available = PETS[world_level]
            pet = random.choice([p for p in available if p["rarity"] in ["Comum", "Incomum"]] or available)

            embed.add_field(
                name=f"{pet['emoji']} Criatura Avistada!",
                value=f"*'Você encontra um **{pet['name']}** ({pet['rarity']}) nas proximidades!'*",
                inline=False
            )
            embed.color = RARITIES[pet["rarity"]]["color"]
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            view = PetTameButton(user_id, pet)
            await message.channel.send(f"{pet['emoji']} **{pet['name']}** está próximo!", view=view)

        else:  # 7-10: maior chance de pet raro
            world_level = max([k for k in PETS.keys() if k <= player["level"]])
            available = PETS[world_level]
            if roll >= 9:
                pets_filtered = [p for p in available if p["rarity"] in ["Raro", "Épico", "Lendário", "Mítico", "Divino", "Primordial"]]
            else:
                pets_filtered = [p for p in available if p["rarity"] in ["Incomum", "Raro", "Épico"]]
            pet = random.choice(pets_filtered or available)

            embed.add_field(
                name=f"{pet['emoji']} Criatura Rara Avistada!",
                value=f"*'Incrível! Você detecta um **{pet['name']}** ({RARITIES[pet['rarity']]['emoji']} {pet['rarity']}) escondido!'*",
                inline=False
            )
            embed.color = RARITIES[pet["rarity"]]["color"]
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            view = PetTameButton(user_id, pet)
            await message.channel.send(f"{pet['emoji']} **{pet['name']}** apareceu!", view=view)
        return

    # ======================================================
    # ================= DOMESTICAR PET =====================
    # ======================================================
    elif any(word in content for word in ["domesticar", "tentar domesticar", "domar"]):
        player = get_player(user_id)
        if player.get("pet"):
            await message.channel.send(f"❌ Você já tem um pet: **{player['pet']}**!")
            return

        world_level = player["level"] - (player["level"] % 10)
        if world_level == 0:
            world_level = 1
        if world_level not in PETS:
            world_level = max([w for w in PETS.keys() if w <= player["level"]])

        available_pets = PETS[world_level]
        pet = random.choice(available_pets)

        embed = discord.Embed(
            title=f"{pet['emoji']} {pet['name']} Apareceu!",
            description=f"*'Um **{pet['name']}** selvagem aparece diante de você!'*",
            color=RARITIES[pet["rarity"]]["color"]
        )
        embed.add_field(name="✨ Raridade", value=f"{RARITIES[pet['rarity']]['emoji']} {pet['rarity']}", inline=True)
        embed.add_field(name="💪 Bônus ATK", value=f"+{pet['bonus_atk']}", inline=True)
        embed.add_field(name="❤️ Bônus HP", value=f"+{pet['bonus_hp']}", inline=True)

        view = PetTameButton(user_id, pet)
        await message.channel.send(embed=embed, view=view)
        return

    # ======================================================
    # ================= DESAFIAR / IR ATRÁS DO BOSS ========
    # ======================================================
    elif any(word in content for word in ["desafiar boss", "ir atrás do boss", "ir atras do boss", "chamar boss", "invocar boss", "enfrentar boss"]):
        player = get_player(user_id)

        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        # Verifica se tem boss de level
        boss_data = get_level_boss(player["level"])
        if not boss_data:
            world_level = max([k for k in WORLDS.keys() if k <= player["level"]])
            boss_data = WORLDS[world_level]["boss"]

        embed = discord.Embed(
            title="⚠️ PRESENÇA AMEAÇADORA",
            description=f"*'O ar fica pesado... Uma sombra colossal se ergue diante de você...'*\n\n👹 **{boss_data['name']}** bloqueia seu caminho!",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="❤️ HP do Boss", value=str(boss_data["hp"]), inline=True)
        embed.add_field(name="⚔️ ATK do Boss", value=str(boss_data["atk"]), inline=True)
        embed.add_field(name="⭐ XP de Recompensa", value=str(boss_data["xp"]), inline=True)
        embed.add_field(
            name="💡 Dica",
            value="Você pode chamar aliados para aumentar suas chances de vitória!",
            inline=False
        )

        view = BossButton(user_id, boss_data["name"])
        await message.channel.send(embed=embed, view=view)
        return

    # ======================================================
    # ================= JUNTAR BOSS (co-op) ================
    # ======================================================
    elif any(word in content for word in ["juntar boss", "ajudar boss", "participar boss"]):
        player = get_player(user_id)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, boss_name, leader_id, members FROM boss_battles WHERE status = 'recruiting' ORDER BY created_at DESC LIMIT 1")
        result = c.fetchone()
        conn.close()

        if not result:
            await message.channel.send("❌ Não há batalhas de boss abertas no momento!")
            return

        battle_id, boss_name, leader_id, members_json = result
        members = json.loads(members_json)

        if str(user_id) in members:
            await message.channel.send("❌ Você já está nesta batalha!")
            return

        if len(members) >= 3:
            await message.channel.send("❌ Esta batalha já está cheia (máximo 3 jogadores)!")
            return

        members.append(str(user_id))
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE boss_battles SET members = ? WHERE id = ?", (json.dumps(members), battle_id))
        conn.commit()
        conn.close()

        await message.channel.send(
            f"✅ **{message.author.mention}** entrou na batalha contra **{boss_name}**!\n\n👥 Jogadores: {len(members)}/3\n\nO líder pode usar `iniciar batalha boss` quando estiver pronto!"
        )
        return

    # ======================================================
    # ================= INICIAR BATALHA BOSS (co-op) =======
    # ======================================================
    elif any(word in content for word in ["iniciar batalha boss", "começar batalha boss", "start boss"]):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, boss_name, leader_id, members, world_level FROM boss_battles WHERE leader_id = ? AND status = 'recruiting'", (str(user_id),))
        result = c.fetchone()

        if not result:
            await message.channel.send("❌ Você não tem uma batalha de boss ativa. Use `desafiar boss` e escolha 'Chamar Aliados'.")
            conn.close()
            return

        battle_id, boss_name, leader_id, members_json, world_level = result
        members = json.loads(members_json)

        c.execute("UPDATE boss_battles SET status = 'active' WHERE id = ?", (battle_id,))
        conn.commit()
        conn.close()

        boss_data = WORLDS.get(world_level, WORLDS[1])["boss"]

        member_names = []
        for mid in members:
            try:
                u = await bot.fetch_user(int(mid))
                member_names.append(u.mention)
            except:
                pass

        embed = discord.Embed(
            title=f"⚔️ BATALHA ÉPICA INICIADA!",
            description=f"**{'  |  '.join(member_names)}** vs **{boss_name}**!\n\n*'Que os deuses guiem suas espadas!'*",
            color=discord.Color.dark_red()
        )
        await message.channel.send(embed=embed)
        await asyncio.sleep(2)
        await fight_boss(message.channel, user_id, allies=members)
        return


    # ======================================================
    # ================= CRIAR GUILDA =======================
    # ======================================================
    elif "criar guilda" in content or "criar guild" in content:
        player = get_player(user_id)
        if player.get("guild_id"):
            await message.channel.send("❌ Você já está em uma guilda!")
            return

        guild_name = content.replace("criar guilda", "").replace("criar guild", "").strip()
        if not guild_name:
            await message.channel.send("❌ Use: `criar guilda [nome]`")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO guilds (name, leader_id, members) VALUES (?, ?, ?)",
                      (guild_name, str(user_id), json.dumps([str(user_id)])))
            guild_id = c.lastrowid
            conn.commit()
            player["guild_id"] = guild_id
            save_player_db(user_id, player)

            embed = discord.Embed(
                title="🏰 Guilda Criada!",
                description=f"*'A guilda **{guild_name}** foi fundada!'*",
                color=discord.Color.gold()
            )
            embed.add_field(name="👑 Líder", value=message.author.mention, inline=True)
            embed.set_footer(text="Outros podem usar 'entrar guilda' para se juntar!")
            await message.channel.send(embed=embed)
        except sqlite3.IntegrityError:
            await message.channel.send("❌ Já existe uma guilda com esse nome!")
        finally:
            conn.close()
        return

    # ======================================================
    # ================= ENTRAR GUILDA ======================
    # ======================================================
    elif "entrar guilda" in content or "entrar na guilda" in content:
        player = get_player(user_id)
        if player.get("guild_id"):
            await message.channel.send("❌ Você já está em uma guilda!")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, name, leader_id, members FROM guilds")
        guilds = c.fetchall()
        conn.close()

        if not guilds:
            await message.channel.send("❌ Não há guildas! Crie uma com `criar guilda [nome]`")
            return

        embed = discord.Embed(title="🏰 Guildas Disponíveis", color=discord.Color.blue())
        for guild_row in guilds:
            guild_id, name, leader_id, members_json = guild_row
            members = json.loads(members_json)
            embed.add_field(name=f"{guild_id}. {name}", value=f"👥 Membros: {len(members)}", inline=False)
        await message.channel.send(embed=embed)

        def check(m):
            return m.author.id == user_id and m.content.isdigit()

        try:
            response = await bot.wait_for('message', check=check, timeout=30.0)
            guild_id_choice = int(response.content)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT name, members FROM guilds WHERE id = ?", (guild_id_choice,))
            result = c.fetchone()
            if not result:
                await message.channel.send("❌ Guilda não encontrada!")
                conn.close()
                return
            guild_name, members_json = result
            members = json.loads(members_json)
            members.append(str(user_id))
            c.execute("UPDATE guilds SET members = ? WHERE id = ?", (json.dumps(members), guild_id_choice))
            conn.commit()
            conn.close()
            player["guild_id"] = guild_id_choice
            save_player_db(user_id, player)
            await message.channel.send(f"✅ **Você entrou na guilda {guild_name}!**")
        except asyncio.TimeoutError:
            await message.channel.send("⏰ Tempo esgotado!")
        return

    # ======================================================
    # ================= VER GUILDA =========================
    # ======================================================
    elif any(word in content for word in ["ver guilda", "minha guilda"]):
        player = get_player(user_id)
        if not player.get("guild_id"):
            await message.channel.send("❌ Você não está em nenhuma guilda!")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name, leader_id, members, total_xp FROM guilds WHERE id = ?", (player["guild_id"],))
        result = c.fetchone()
        conn.close()

        if not result:
            await message.channel.send("❌ Guilda não encontrada!")
            return

        guild_name, leader_id, members_json, total_xp = result
        members = json.loads(members_json)
        embed = discord.Embed(title=f"🏰 {guild_name}", color=discord.Color.gold())
        embed.add_field(name="👥 Membros", value=len(members), inline=True)
        embed.add_field(name="⭐ XP Total", value=total_xp, inline=True)
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= BEBER POÇÃO (formato antigo) =======
    # ======================================================
    elif any(word in content for word in ["beber", "usar poção", "tomar"]):
        player = get_player(user_id)
        potion_name = None
        for potion in POTIONS.keys():
            if potion.lower() in content:
                potion_name = potion
                break

        if not potion_name:
            await message.channel.send("❌ Especifique qual poção! Formato: `[nome da poção], usar`")
            return

        if potion_name not in player["inventory"]:
            await message.channel.send(f"❌ Você não tem **{potion_name}**!")
            return

        potion = POTIONS[potion_name]
        player["inventory"].remove(potion_name)
        embed = discord.Embed(
            title=f"{potion['emoji']} Poção Consumida!",
            description=f"*'Você bebe **{potion_name}**...'*",
            color=RARITIES.get(potion["rarity"], {"color": 0xFFFFFF})["color"]
        )
        if "hp_restore" in potion:
            old_hp = player["hp"]
            player["hp"] = min(player["hp"] + potion["hp_restore"], player["max_hp"])
            embed.add_field(name="💚 HP Restaurado", value=f"+{player['hp'] - old_hp} HP", inline=False)
        if "xp_gain" in potion:
            add_xp(user_id, potion["xp_gain"])
            embed.add_field(name="⭐ XP Ganho", value=f"+{potion['xp_gain']} XP", inline=False)
        if "revive" in potion and potion["revive"]:
            player["hp"] = player["max_hp"]
            embed.add_field(name="💀 Ressurreição", value="HP completamente restaurado!", inline=False)
        save_player_db(user_id, player)
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= VENDER ITEM ========================
    # ======================================================
    elif content.startswith("vender"):
        player = get_player(user_id)
        item_name = content.replace("vender", "").strip()
        if not item_name:
            await message.channel.send("❌ Use: `vender [nome do item]`")
            return

        found_item = None
        for item in player["inventory"]:
            if item_name in item.lower():
                found_item = item
                break

        if not found_item:
            await message.channel.send(f"❌ Você não tem **{item_name}** no inventário!")
            return

        price = get_item_sell_price(found_item)
        player["inventory"].remove(found_item)
        player["coins"] += price
        save_player_db(user_id, player)

        embed = discord.Embed(
            title="💰 Item Vendido!",
            description=f"*'Você vendeu **{found_item}** por **{price} CSI**!'*",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Moedas Atuais", value=f"{player['coins']} CSI", inline=False)
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= TROCAR ITEMS =======================
    # ======================================================
    if "trocar" in content and "@" in message.content and "csi" not in content:
        parts = message.content.split("com")
        if len(parts) < 2:
            return

        from_items_text = parts[0].replace("trocar", "").strip()
        mentions = message.mentions
        if not mentions:
            await message.channel.send("❌ Mencione um usuário válido!")
            return

        to_user = mentions[0]
        to_user_id = to_user.id

        if to_user_id == user_id:
            await message.channel.send("❌ Você não pode trocar com você mesmo!")
            return

        await message.channel.send(f"{to_user.mention}, que item você oferece em troca de **{from_items_text}**?\n\nResponda com: `ofereço [nome do item]`")

        def check(m):
            return m.author.id == to_user_id and "ofereço" in m.content.lower()

        try:
            response = await bot.wait_for('message', check=check, timeout=60.0)
            to_items_text = response.content.replace("ofereço", "").strip()

            embed = discord.Embed(title="🔄 Proposta de Troca", color=discord.Color.blue())
            embed.add_field(name=f"📤 {message.author.name} oferece", value=f"**{from_items_text}**", inline=True)
            embed.add_field(name=f"📥 {to_user.name} oferece", value=f"**{to_items_text}**", inline=True)

            view = TradeButton(user_id, to_user_id, [from_items_text], [to_items_text])
            await message.channel.send(embed=embed, view=view)
        except asyncio.TimeoutError:
            await message.channel.send("⏰ Tempo esgotado! Proposta expirou.")
        return

    # ======================================================
    # ================= TROCAR COINS CSI ===================
    # ======================================================
    elif "trocar" in content and "csi" in content:
        player = get_player(user_id)
        embed = discord.Embed(
            title="💱 Solicitação de Conversão",
            description=f"{message.author.mention} deseja converter moedas CSI.",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Moedas CSI", value=f"`{player['coins']}` CSI", inline=False)
        await message.channel.send(embed=embed)
        try:
            admin = await bot.fetch_user(int(BOT_OWNER_ID))
            dm_embed = discord.Embed(title="🔔 Solicitação de Conversão", color=discord.Color.gold())
            dm_embed.add_field(name="Jogador", value=f"{message.author.name} ({message.author.id})", inline=False)
            dm_embed.add_field(name="💰 Moedas CSI", value=f"`{player['coins']}` CSI", inline=False)
            await admin.send(embed=dm_embed)
        except:
            pass
        return

    # ======================================================
    # ================= EXPLORAR ===========================
    # ======================================================
    if any(word in content for word in ["explorar", "vou explorar", "andar", "caminhar", "vou para"]):
        player = get_player(user_id)
        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        world = get_world(player["level"], player)
        roll = roll_with_bonus(player)
        luck = get_luck(roll)
        event = random.choice(world["events"])

        embed = discord.Embed(
            title=f"{world['emoji']} {world['name']}",
            description=f"*'{event}'*",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado do Destino", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll == 1:
            result, xp_loss = remove_xp(user_id, random.randint(30, 50))
            embed.add_field(
                name="💀 Desastre!",
                value=f"*'Seus passos tropeçam no destino cruel!'*\n\n❌ **−{xp_loss} XP**",
                inline=False
            )
            if result == "reset":
                embed.add_field(name="🌑 Fim da Jornada", value="*'Sua história encontra um fim abrupto...'*\n\n**Você desperta nos Campos Iniciais.**", inline=False)
                embed.color = discord.Color.dark_red()

        elif roll == 2:
            result, xp_loss = remove_xp(user_id, random.randint(15, 30))
            embed.add_field(name="☠️ Infortúnio", value=f"*'Nem sempre o caminho é gentil...'*\n\n❌ **−{xp_loss} XP**", inline=False)
            embed.color = discord.Color.red()

        elif roll in [3, 4]:
            embed.add_field(name="😐 Nada de Especial", value="*'Você continua sua jornada sem nada digno de nota.'*", inline=False)
            embed.color = discord.Color.light_grey()

        elif roll == 5:
            res = random.choice(world["resources"])
            player = get_player(user_id)
            player["inventory"].append(res)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(5, 15), player["max_hp"])
            save_player_db(user_id, player)
            embed.add_field(name="😶 Descoberta Modesta", value=f"*'Você encontra algo que pode ser útil...'*\n\n📦 **{res}**", inline=False)

            # Progresso de quest
            if player.get("active_quest") and player["active_quest"].get("objective") == "collect":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await complete_quest(message.channel, user_id, player)
                else:
                    save_player_db(user_id, player)

        elif roll in [6, 7]:
            xp = random.randint(20, 40)
            res = random.choice(world["resources"])
            player = get_player(user_id)
            player["inventory"].append(res)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(10, 20), player["max_hp"])
            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)

            embed.add_field(name="🙂 Boa Descoberta!", value=f"*'A sorte está ao seu lado hoje!'*\n\n📦 **{res}**\n⭐ **+{xp} XP**", inline=False)
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Evolução!", value=f"*'Um novo capítulo se abre!'*\n\n**Nível {player['level']}**", inline=False)
                embed.color = discord.Color.gold()
            else:
                embed.color = discord.Color.green()

            # Progresso de quest explore
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "explore":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await complete_quest(message.channel, user_id, player)
                else:
                    save_player_db(user_id, player)

        elif roll == 8:
            xp = random.randint(40, 70)
            resources = random.sample(world["resources"], min(2, len(world["resources"])))
            player = get_player(user_id)
            for r in resources:
                player["inventory"].append(r)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(15, 30), player["max_hp"])

            # Chance de dungeon secreta ao explorar
            secret_found = False
            if "secret_dungeons" in world and random.random() < 0.15:
                secret_dungeon = random.choice(world["secret_dungeons"])
                secret_found = True
                embed.add_field(
                    name="🔮 Dungeon Secreta Encontrada!",
                    value=f"*'Explorando os arredores, você descobre uma entrada oculta...'*\n\n**{secret_dungeon['name']}**",
                    inline=False
                )

            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)
            items_text = "\n".join([f"• **{r}**" for r in resources])
            embed.add_field(name="🍀 Tesouro Escondido!", value=f"*'Seus olhos captam o que outros perderiam!'*\n\n{items_text}\n⭐ **+{xp} XP**", inline=False)
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.green()

            if secret_found:
                await message.channel.send(embed=embed)
                await asyncio.sleep(1)
                view = DungeonSelectButton(user_id, [secret_dungeon], world)
                await message.channel.send("🔮 **Dungeon Secreta!** Deseja explorar?", view=view)
                return

        elif roll == 9:
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            rarity = random.choices(["Raro", "Épico", "Lendário"], weights=[50, 35, 15])[0]
            items_filtered = [i for i in ITEMS[item_list] if i["rarity"] == rarity]
            item = random.choice(items_filtered) if items_filtered else random.choice(ITEMS[item_list])
            xp = random.randint(60, 100)
            leveled = add_xp(user_id, xp)
            rarity_info = RARITIES[item["rarity"]]
            embed.add_field(
                name="✨ Descoberta Rara!",
                value=f"*'Seus olhos brilham ao ver algo extraordinário!'*\n\n{rarity_info['emoji']} **{item['name']}**\n⭐ **+{xp} XP**",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = rarity_info["color"]
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            view = EquipButton(user_id, item["name"], item_type)
            await message.channel.send(f"✨ **{item['name']}** aguarda!\n\n*'Deseja equipar?'*", view=view)
            await check_level_boss(message.channel, user_id)
            return

        else:  # roll == 10
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            legendary = [i for i in ITEMS[item_list] if i["rarity"] in ["Lendário", "Mítico", "Divino"]]
            item = random.choice(legendary)
            xp = random.randint(120, 200)
            leveled = add_xp(user_id, xp)
            embed.add_field(
                name="🌟 EVENTO LENDÁRIO!",
                value=f"*'OS DEUSES SORRIEM PARA VOCÊ!'*\n\n{RARITIES[item['rarity']]['emoji']} **{item['name']}**\n⭐ **+{xp} XP**",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Ascensão!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.gold()
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            view = EquipButton(user_id, item["name"], item_type)
            await message.channel.send(f"🌟 **{item['name']}** pulsa com poder divino!\n\n*'Deseja equipar?'*", view=view)
            await check_level_boss(message.channel, user_id)
            return

        await message.channel.send(embed=embed)
        await check_level_boss(message.channel, user_id)
        return

    # ======================================================
    # ================= CAÇAR ==============================
    # ======================================================
    elif any(word in content for word in ["caçar", "cacar", "lutar", "atacar", "batalhar"]):
        player = get_player(user_id)
        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        world = get_world(player["level"], player)
        monster_name = random.choice(list(world["monsters"].keys()))
        monster = world["monsters"][monster_name]
        roll = roll_with_bonus(player)
        luck = get_luck(roll)

        embed = discord.Embed(
            title=f"⚔️ Encontro de Batalha",
            description=f"*'Um **{monster_name}** surge diante de você!'*",
            color=discord.Color.red()
        )
        embed.add_field(name="🎲 Dado da Batalha", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 3:
            dmg = random.randint(10, 30)
            player = get_player(user_id)
            player["hp"] -= dmg
            if player["hp"] <= 0:
                player["hp"] = player["max_hp"] // 2
            save_player_db(user_id, player)
            result, xp_loss = remove_xp(user_id, random.randint(20, 40))
            embed.add_field(
                name="💀 Derrota Dolorosa",
                value=f"*'O {monster_name} te supera!'*\n\n❌ **−{xp_loss} XP**\n💔 **−{dmg} HP**",
                inline=False
            )
            embed.color = discord.Color.dark_red()

        elif roll <= 5:
            xp = random.randint(monster["xp"][0], monster["xp"][0] + 5)
            coins = random.randint(monster["coins"][0], monster["coins"][1])
            dmg = random.randint(5, 15)
            player = get_player(user_id)
            player["hp"] -= dmg
            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)
            add_coins(user_id, coins)
            embed.add_field(
                name="😓 Vitória Suada",
                value=f"*'A batalha foi feroz, mas você prevalece!'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**\n💔 **−{dmg} HP**",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Crescimento!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.orange()

        elif roll <= 7:
            xp = random.randint(monster["xp"][0], monster["xp"][1])
            coins = random.randint(monster["coins"][0], monster["coins"][1])
            leveled = add_xp(user_id, xp)
            add_coins(user_id, coins)
            # Chance de drop de poção (baixa)
            drop_potion = None
            if random.random() < 0.15:
                potion_list = [name for name, data in POTIONS.items() if data["rarity"] in ["Comum", "Incomum"]]
                drop_potion = random.choice(potion_list)
                p2 = get_player(user_id)
                p2["inventory"].append(drop_potion)
                save_player_db(user_id, p2)

            potion_text = f"\n🧪 Drop: **{drop_potion}**" if drop_potion else ""
            embed.add_field(
                name="⚔️ Vitória!",
                value=f"*'Cada golpe seu é preciso!'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**{potion_text}",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.green()

            # Progresso de quest de caça
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "hunt":
                if player["active_quest"].get("target", "") in monster_name or monster_name in player["active_quest"].get("target", ""):
                    player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                    if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                        await message.channel.send(embed=embed)
                        await complete_quest(message.channel, user_id, player)
                        return
                    else:
                        save_player_db(user_id, player)

        else:  # 8-10
            xp = random.randint(monster["xp"][1], monster["xp"][1] + 15)
            coins = random.randint(monster["coins"][1], monster["coins"][1] + 5)
            leveled = add_xp(user_id, xp)
            add_coins(user_id, coins)

            drop_item = None
            drop_potion = None

            if roll >= 9:
                if roll == 10:
                    item_type = random.choice(["weapon", "armor"])
                    item_list_key = "weapons" if item_type == "weapon" else "armor"
                    rarity = random.choices(["Raro", "Épico"], weights=[60, 40])[0]
                    items_filtered = [i for i in ITEMS[item_list_key] if i["rarity"] == rarity]
                    drop_item = random.choice(items_filtered) if items_filtered else None

                if random.random() < 0.3:
                    potion_rarities = ["Incomum", "Raro"]
                    drop_potion = random.choice([name for name, data in POTIONS.items() if data["rarity"] in potion_rarities])
                    p2 = get_player(user_id)
                    p2["inventory"].append(drop_potion)
                    save_player_db(user_id, p2)

            drop_text = ""
            if drop_potion:
                drop_text += f"\n🧪 **{drop_potion}**!"
            if drop_item:
                drop_text += f"\n{RARITIES[drop_item['rarity']]['emoji']} **{drop_item['name']}**!"

            embed.add_field(
                name="✨ Domínio Total!",
                value=f"*'Vitória absoluta!'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**{drop_text}",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Evolução!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.gold()

            await message.channel.send(embed=embed)

            if drop_item:
                await asyncio.sleep(1)
                view = EquipButton(user_id, drop_item["name"], item_type)
                await message.channel.send(f"⚔️ **{drop_item['name']}** está em suas mãos!\n\n*'Deseja equipar?'*", view=view)

            # Progresso de quest de caça
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "hunt":
                if player["active_quest"].get("target", "") in monster_name or monster_name in player["active_quest"].get("target", ""):
                    player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                    if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                        await complete_quest(message.channel, user_id, player)
                        return
                    else:
                        save_player_db(user_id, player)

            await check_level_boss(message.channel, user_id)
            return

        await message.channel.send(embed=embed)
        await check_level_boss(message.channel, user_id)
        return

    # ======================================================
    # ================= COLETAR ============================
    # ======================================================
    elif any(word in content for word in ["coletar", "minerar", "colher", "pegar recursos"]):
        player = get_player(user_id)
        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        world = get_world(player["level"], player)
        roll = roll_with_bonus(player)
        luck = get_luck(roll)

        embed = discord.Embed(
            title=f"⛏️ Coleta de Recursos",
            description=f"*'Você procura cuidadosamente por recursos valiosos...'*",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado da Sorte", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 3:
            embed.add_field(name="😔 Busca Infrutífera", value="*'Suas mãos voltam vazias...'*", inline=False)
            embed.color = discord.Color.light_grey()

            # Chance de dungeon secreta ao minerar (baixa)
            if "secret_dungeons" in world and random.random() < 0.08:
                secret_dungeon = random.choice(world["secret_dungeons"])
                embed.add_field(
                    name="🔮 Mas você encontra algo...",
                    value=f"*'Enquanto minerava, você descobre uma entrada oculta: **{secret_dungeon['name']}**!'*",
                    inline=False
                )
                await message.channel.send(embed=embed)
                await asyncio.sleep(1)
                view = DungeonSelectButton(user_id, [secret_dungeon], world)
                await message.channel.send("🔮 Explorar a dungeon secreta?", view=view)
                return

        elif roll <= 6:
            res = random.choice(world["resources"])
            player = get_player(user_id)
            player["inventory"].append(res)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(10, 20), player["max_hp"])
            save_player_db(user_id, player)
            embed.add_field(name="📦 Recurso Encontrado", value=f"*'Você encontra algo útil!'*\n\n**{res}**", inline=False)
            embed.color = discord.Color.green()

            # Progresso quest coleta
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "collect":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await message.channel.send(embed=embed)
                    await complete_quest(message.channel, user_id, player)
                    return
                else:
                    save_player_db(user_id, player)

        elif roll <= 8:
            resources = [random.choice(world["resources"]) for _ in range(2)]
            player = get_player(user_id)
            for r in resources:
                player["inventory"].append(r)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(15, 30), player["max_hp"])
            save_player_db(user_id, player)
            items_text = "\n".join([f"• **{r}**" for r in resources])
            embed.add_field(name="🍀 Coleta Proveitosa!", value=f"*'Múltiplos recursos encontrados!'*\n\n{items_text}", inline=False)
            embed.color = discord.Color.green()

            # Progresso quest
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "collect":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 2
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await message.channel.send(embed=embed)
                    await complete_quest(message.channel, user_id, player)
                    return
                else:
                    save_player_db(user_id, player)

        else:  # 9-10
            count = 3 if roll == 9 else 4
            resources = [random.choice(world["resources"]) for _ in range(count)]
            player = get_player(user_id)
            for r in resources:
                player["inventory"].append(r)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(20, 40), player["max_hp"])

            # Dungeon secreta ao minerar (chance maior em 9-10)
            secret_found = False
            if "secret_dungeons" in world and random.random() < 0.2:
                secret_dungeon = random.choice(world["secret_dungeons"])
                secret_found = True
                embed.add_field(
                    name="🔮 Dungeon Secreta Revelada!",
                    value=f"*'Sua ferramenta perfura uma parede falsa e revela: **{secret_dungeon['name']}**!'*",
                    inline=False
                )

            save_player_db(user_id, player)
            items_text = "\n".join([f"• **{r}**" for r in resources])
            embed.add_field(name="✨ Coleta Abundante!", value=f"*'Uma descoberta magnífica!'*\n\n{items_text}", inline=False)
            embed.color = discord.Color.gold()

            # Progresso quest
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "collect":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + count
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await message.channel.send(embed=embed)
                    if secret_found:
                        view = DungeonSelectButton(user_id, [secret_dungeon], world)
                        await message.channel.send("🔮 Explorar a dungeon secreta?", view=view)
                    await complete_quest(message.channel, user_id, player)
                    return
                else:
                    save_player_db(user_id, player)

            await message.channel.send(embed=embed)
            if secret_found:
                await asyncio.sleep(1)
                view = DungeonSelectButton(user_id, [secret_dungeon], world)
                await message.channel.send("🔮 Explorar a dungeon secreta?", view=view)
            return

        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= DUNGEON ============================
    # ======================================================
    elif any(word in content for word in ["achar dungeon", "procurar dungeon", "buscar dungeon", "dungeon"]):
        player = get_player(user_id)
        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        world = get_world(player["level"], player)
        if "dungeons" not in world or not world["dungeons"]:
            await message.channel.send("*'Não há dungeons conhecidas nesta região...'*")
            return

        roll = roll_dice()
        luck = get_luck(roll)

        embed = discord.Embed(
            title="🔍 Procurando Dungeons...",
            description="*'Você procura por entradas secretas e ruínas antigas...'*",
            color=discord.Color.purple()
        )
        embed.add_field(name="🎲 Dado da Busca", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 3:
            embed.add_field(name="❌ Busca Fracassada", value="*'Você vaga por horas mas não encontra nenhuma entrada...'*", inline=False)
            embed.color = discord.Color.red()
            await message.channel.send(embed=embed)
            return

        dungeons = list(world["dungeons"])

        # Dungeons secretas têm chance menor de aparecer
        if "secret_dungeons" in world and roll >= 8:
            for sd in world["secret_dungeons"]:
                if random.random() < 0.3:
                    dungeons.append(sd)

        embed.add_field(
            name="🏛️ Dungeons Encontradas!",
            value=f"*'Você descobre {len(dungeons)} dungeons nesta região!'*",
            inline=False
        )
        for i, dungeon in enumerate(dungeons, 1):
            secret_tag = " 🔮 *[SECRETA]*" if dungeon.get("secret") else ""
            embed.add_field(
                name=f"{i}. {dungeon['name']}{secret_tag} (Nível {dungeon['level']})",
                value=f"Boss: **{dungeon['boss']}**",
                inline=False
            )
        embed.color = discord.Color.gold()
        await message.channel.send(embed=embed)
        await asyncio.sleep(1)
        view = DungeonSelectButton(user_id, dungeons, world)
        await message.channel.send("*'Qual dungeon deseja explorar?'*", view=view)
        return

    # ======================================================
    # ================= VER PERFIL =========================
    # ======================================================
    elif any(word in content for word in ["ver perfil", "meu perfil", "perfil", "status"]):
        player = get_player(user_id)
        world = get_world(player["level"], player)
        xp_need = calc_xp(player["level"])

        embed = discord.Embed(
            title=f"👤 {message.author.display_name}",
            description=f"*'O narrador revela sua história até agora...'*",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.add_field(name="⭐ Nível", value=f"`{player['level']}`", inline=True)
        embed.add_field(name="✨ XP", value=f"`{player['xp']}/{xp_need}`", inline=True)
        embed.add_field(name="💰 Moedas CSI", value=f"`{player['coins']}`", inline=True)
        embed.add_field(name="❤️ HP", value=f"`{player['hp']}/{player['max_hp']}`", inline=True)

        if player.get("class"):
            max_mana = calc_max_mana(player)
            cur_mana = player.get("mana", max_mana)
            embed.add_field(name="💙 Mana", value=f"`{cur_mana}/{max_mana}`", inline=True)

        if player.get("class"):
            class_data = CLASSES[player["class"]]
            embed.add_field(name=f"{class_data['emoji']} Classe", value=player["class"], inline=True)
        if player.get("pet"):
            embed.add_field(name="🐉 Pet", value=player["pet"], inline=True)
        embed.add_field(name="🌍 Localização", value=f"{world['emoji']} **{world['name']}**", inline=False)
        embed.add_field(name="⚔️ Arma", value=player["weapon"] or "*Nenhuma*", inline=True)
        embed.add_field(name="🛡️ Armadura", value=player["armor"] or "*Nenhuma*", inline=True)
        embed.add_field(name="👹 Bosses Derrotados", value=f"`{len(player['bosses'])}`", inline=True)

        active_quest = player.get("active_quest")
        if active_quest:
            progress = active_quest.get("progress", 0)
            total = active_quest.get("count", 1)
            embed.add_field(name="📜 Quest Ativa", value=f"{active_quest['name']}\n**Progresso:** {progress}/{total}", inline=False)

        if player.get("guild_id"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT name FROM guilds WHERE id = ?", (player["guild_id"],))
            result = c.fetchone()
            conn.close()
            if result:
                embed.add_field(name="🏰 Guilda", value=result[0], inline=True)

        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= INVENTÁRIO =========================
    # ======================================================
    elif any(word in content for word in ["ver inventario", "inventario", "inventário", "mochila", "itens"]):
        player = get_player(user_id)
        embed = discord.Embed(
            title=f"🎒 Inventário de {message.author.display_name}",
            description=f"*'O narrador vasculha sua mochila...'*",
            color=discord.Color.gold()
        )

        if not player["inventory"]:
            embed.add_field(name="Vazio", value="*'Suas bolsas estão vazias...'*", inline=False)
        else:
            items_count = {}
            for item in player["inventory"]:
                items_count[item] = items_count.get(item, 0) + 1

            weapons_in_inv = [i for i in items_count if any(w["name"] == i for w in ITEMS["weapons"])]
            armors_in_inv = [i for i in items_count if any(a["name"] == i for a in ITEMS["armor"])]
            potions_in_inv = [i for i in items_count if i in POTIONS]
            resources_in_inv = [i for i in items_count if i not in potions_in_inv and i not in weapons_in_inv and i not in armors_in_inv]

            if weapons_in_inv:
                embed.add_field(name="⚔️ Armas", value="\n".join([f"• **{i}** x{items_count[i]}" for i in weapons_in_inv]), inline=False)
            if armors_in_inv:
                embed.add_field(name="🛡️ Armaduras", value="\n".join([f"• **{i}** x{items_count[i]}" for i in armors_in_inv]), inline=False)
            if potions_in_inv:
                embed.add_field(name="🧪 Poções", value="\n".join([f"• **{i}** x{items_count[i]}" for i in potions_in_inv]), inline=False)
            if resources_in_inv:
                embed.add_field(name="📦 Recursos", value="\n".join([f"• **{i}** x{items_count[i]}" for i in resources_in_inv]), inline=False)

        embed.set_footer(text=f"Total: {len(player['inventory'])} itens | Moedas CSI: {player['coins']}")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= VER MANA ==========================
    # ======================================================
    elif any(word in content for word in ["ver mana", "minha mana", "mana"]):
        player = get_player(user_id)
        max_mana = calc_max_mana(player)
        player["max_mana"] = max_mana
        if player.get("mana", 0) > max_mana:
            player["mana"] = max_mana
        save_player_db(user_id, player)

        cls = player.get("class", "Sem Classe")
        embed = discord.Embed(
            title="✨ Status de Mana",
            description=f"*O narrador examina sua energia arcana...*",
            color=discord.Color.blue()
        )
        mana_bar = "🔵" * (player["mana"] // 10) + "⚫" * ((max_mana - player["mana"]) // 10)
        embed.add_field(name="💙 Mana Atual", value=f"`{player['mana']}/{max_mana}`\n{mana_bar}", inline=False)
        if cls and cls in CLASS_SKILLS:
            skills_text = "\n".join([f"{s['name']} — {s['mana_cost']} mana | {s['desc']}" for s in CLASS_SKILLS[cls]])
            embed.add_field(name=f"⚡ Habilidades de {cls}", value=skills_text[:1024], inline=False)
        embed.set_footer(text="Mana se recupera ao subir de nível e ao descansar!")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= REALIZAR QUEST ====================
    # ======================================================
    elif any(word in content for word in ["realizar quest", "fazer quest", "iniciar quest", "minha quest", "status da quest"]):
        player = get_player(user_id)
        quest = player.get("active_quest")

        if not quest:
            await message.channel.send(
                "📋 **Você não tem nenhuma quest ativa!**\n\n*Use `ver quests` para ver as missões disponíveis e `aceitar quest [nome]` para iniciar uma.*"
            )
            return

        objective = quest.get("objective", "")
        progress = quest.get("progress", 0)
        total = quest.get("count", 1)
        pct = int((progress / total) * 100) if total > 0 else 0
        bar_filled = int(pct / 10)
        progress_bar = "🟩" * bar_filled + "⬛" * (10 - bar_filled)

        embed = discord.Embed(
            title=f"📜 Realizando: {quest['name']}",
            description=f"*{quest['npc']} aguarda seu progresso...*\n\n*'{quest['lore']}'*",
            color=discord.Color.gold()
        )
        embed.add_field(name="🎯 Objetivo", value=quest["description"], inline=False)
        embed.add_field(name="📊 Progresso", value=f"`{progress}/{total}` — {pct}%\n{progress_bar}", inline=False)

        obj_tip = {
            "hunt": f"**Como avançar:** Use `caçar` para derrotar **{quest.get('target', 'monstros')}**!",
            "collect": "**Como avançar:** Use `coletar` ou `minerar` para coletar recursos!",
            "explore": "**Como avançar:** Use `explorar` para percorrer o mundo!",
            "boss": "**Como avançar:** Use `desafiar boss` para enfrentar o boss da missão!",
        }
        embed.add_field(name="💡 Dica", value=obj_tip.get(objective, "Explore o mundo!"), inline=False)

        # Recompensas
        rewards = f"⭐ **{quest['reward_xp']} XP** | 💰 **{quest['reward_coins']} CSI**"
        if quest.get("reward_item"):
            rewards += f" | 🎁 **{quest['reward_item']}**"
        embed.add_field(name="🏆 Recompensas ao Completar", value=rewards, inline=False)
        embed.add_field(name="⚔️ Dificuldade", value=quest.get("difficulty", "?"), inline=True)

        if progress >= total:
            embed.add_field(name="✅ Status", value="**COMPLETO! Use `finalizar quest` para receber as recompensas!**", inline=False)
            embed.color = discord.Color.green()
        else:
            remaining = total - progress
            embed.add_field(name="⏳ Faltam", value=f"`{remaining}` ações para completar", inline=True)

        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= FINALIZAR QUEST ===================
    # ======================================================
    elif any(word in content for word in ["finalizar quest", "entregar quest", "completar quest"]):
        player = get_player(user_id)
        quest = player.get("active_quest")

        if not quest:
            await message.channel.send("❌ Você não tem quest ativa!")
            return

        progress = quest.get("progress", 0)
        total = quest.get("count", 1)

        if progress < total and quest.get("objective") != "boss":
            await message.channel.send(
                f"⏳ **Quest ainda não concluída!**\n\nProgresso: `{progress}/{total}`\n\n*Continue realizando as atividades para completar a missão!*"
            )
            return

        await complete_quest(message.channel, user_id, player)
        return

    # ======================================================
    # ================= ABANDONAR QUEST ===================
    # ======================================================
    elif any(word in content for word in ["abandonar quest", "desistir da quest", "cancelar quest"]):
        player = get_player(user_id)
        if not player.get("active_quest"):
            await message.channel.send("❌ Você não tem quest ativa!")
            return

        quest_name = player["active_quest"]["name"]
        player["active_quest"] = None
        save_player_db(user_id, player)

        embed = discord.Embed(
            title="🚫 Quest Abandonada",
            description=f"*'Você abandona **{quest_name}**...'*\n\n*O narrador suspira com decepção.*",
            color=discord.Color.red()
        )
        embed.set_footer(text="Use 'ver quests' para encontrar novas missões.")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= PROCURAR CIDADES / VILAREJOS =======
    # ======================================================
    elif any(word in content for word in ["procurar cidade", "procurar vilarejo", "buscar cidade",
                                           "explorar cidade", "visitar cidade", "visitar vilarejo",
                                           "ver cidades", "cidades próximas", "mapa de cidades"]):
        player = get_player(user_id)
        world_key = max([k for k in CITY_NPCS.keys() if k in player["worlds"]], default=1)
        city_data = CITY_NPCS[world_key]
        world = get_world(player["level"], player)

        embed = discord.Embed(
            title=f"🗺️ Explorando Cidades — {world['emoji']} {world['name']}",
            description=f"*O narrador revela os assentamentos desta região...*",
            color=discord.Color.blue()
        )

        # Mostra a cidade do mundo atual
        embed.add_field(
            name=f"📍 {city_data['city_name']}",
            value=f"**Habitantes notáveis:**\n" + "\n".join([f"{npc['emoji']} **{npc['name']}** — {npc['role']}" for npc in city_data["npcs"]]),
            inline=False
        )

        # Mostra outras cidades desbloqueadas
        other_cities = []
        for wk in sorted(player["worlds"]):
            if wk != world_key and wk in CITY_NPCS:
                cd = CITY_NPCS[wk]
                wn = WORLDS[wk]["name"]
                other_cities.append(f"{WORLDS[wk]['emoji']} **{cd['city_name']}** ({wn})")

        if other_cities:
            embed.add_field(name="🌍 Outras Cidades Conhecidas", value="\n".join(other_cities[:5]), inline=False)

        embed.add_field(
            name="💡 Comandos",
            value="`visitar cidade` — visita a cidade e conversa com NPCs\n`ver quests` — veja missões disponíveis",
            inline=False
        )
        await message.channel.send(embed=embed)

        # Visita automaticamente a cidade atual
        await asyncio.sleep(1)
        npc = random.choice(city_data["npcs"])
        dialogue = random.choice(npc["dialogues"])
        coins_found = random.randint(1, 3)
        add_coins(user_id, coins_found)

        visit_embed = discord.Embed(
            title=f"{npc['emoji']} {npc['name']} — {npc['role']}",
            description=f"*Você se aproxima do NPC na cidade...*\n\n*'{dialogue}'*",
            color=discord.Color.green()
        )
        visit_embed.add_field(name="💰 Recompensa pela Visita", value=f"+{coins_found} CSI", inline=True)

        # 25% chance de livro de lore ao visitar
        if random.random() < 0.25:
            all_books = list(LORE_BOOKS.get(world_key, [])) + list(LORE_BOOKS_EXTRA.get(world_key, []))
            if all_books:
                book = random.choice(all_books)
                visit_embed.add_field(name=f"📚 {book['title']}", value=book["content"][:512] + "...", inline=False)

        await message.channel.send(embed=visit_embed)
        return

    # ======================================================
    # ================= DESAFIAR @USER (PvP Pokémon) ======
    # ======================================================
    elif "desafiar" in content and "@" in message.content and "boss" not in content:
        mentions = message.mentions
        if not mentions:
            await message.channel.send("❌ Mencione um jogador! Ex: `desafiar @jogador`")
            return

        target_user = mentions[0]
        if target_user.id == user_id:
            await message.channel.send("❌ Você não pode se desafiar!")
            return
        if target_user.bot:
            await message.channel.send("❌ Você não pode desafiar um bot!")
            return

        challenger = get_player(user_id)
        target = get_player(target_user.id)

        if not challenger.get("class"):
            await message.channel.send("❌ Escolha uma classe primeiro! Use: `escolher classe`")
            return
        if not target.get("class"):
            await message.channel.send(f"❌ **{target_user.display_name}** ainda não escolheu uma classe!")
            return

        # Envia desafio
        view = PvPChallengeButton(user_id, target_user.id, message.author.display_name, target_user.display_name)
        embed = discord.Embed(
            title="⚔️ DESAFIO DE BATALHA!",
            description=f"*O narrador anuncia com emoção:*\n\n🥊 **{message.author.display_name}** desafia **{target_user.display_name}** para um duelo!",
            color=discord.Color.red()
        )
        cls_ch = CLASSES[challenger["class"]]
        cls_tg = CLASSES[target["class"]]
        embed.add_field(name=f"{cls_ch['emoji']} {message.author.display_name}", value=f"**{challenger['class']}** | Nível {challenger['level']} | HP: {challenger['max_hp']} | Mana: {calc_max_mana(challenger)}", inline=True)
        embed.add_field(name=f"{cls_tg['emoji']} {target_user.display_name}", value=f"**{target['class']}** | Nível {target['level']} | HP: {target['max_hp']} | Mana: {calc_max_mana(target)}", inline=True)
        embed.set_footer(text=f"{target_user.mention}, você aceita o desafio?")
        await message.channel.send(content=f"{target_user.mention}", embed=embed, view=view)
        return

    # ======================================================
    # ================= VER QUESTS ========================
    # ======================================================
    elif any(word in content for word in ["ver quests", "quests", "missões", "missoes", "aceitar quest"]):
        player = get_player(user_id)
        world_key = max([k for k in QUESTS.keys() if k in player["worlds"]], default=1)
        available_quests = list(QUESTS.get(world_key, []))
        # Adicionar quests extras do mundo
        available_quests += QUESTS_EXTRA.get(world_key, [])
        # Adicionar quests de alinhamento
        align = get_alignment(player)
        for key, qlist in ALIGNMENT_QUESTS.items():
            for q in qlist:
                req = q.get("align_required")
                if req is None or req == align:
                    available_quests.append(q)

        embed = discord.Embed(
            title="📋 Quadro de Missões",
            description=f"*{WORLDS[world_key]['emoji']} Missões disponíveis em **{WORLDS[world_key]['name']}**...*",
            color=discord.Color.gold()
        )
        info = ALIGNMENT_TITLES[align]
        embed.add_field(name=f"{info['emoji']} Alinhamento", value=f"**{align}** — Misões exclusivas desbloqueadas!", inline=True)

        if player.get("active_quest"):
            embed.add_field(
                name="⚠️ Quest Ativa",
                value=f"Você está em: **{player['active_quest']['name']}**\nProgresso: {player['active_quest'].get('progress', 0)}/{player['active_quest'].get('count', 1)}\n\nUse `realizar quest` para ver detalhes.",
                inline=False
            )

        completed = player.get("completed_quests", [])
        for quest in available_quests[:12]:
            status = "✅" if quest["id"] in completed else ("🔄" if player.get("active_quest") and player["active_quest"].get("id") == quest["id"] else "📌")
            q_type = "👥 Equipe" if quest.get("type") == "team" else "👤 Solo"
            xp_str = f"{quest['reward_xp']:,}"
            embed.add_field(
                name=f"{status} {quest['name']} [{q_type}]",
                value=f"**Dif:** {quest['difficulty']} | **XP:** {xp_str} | **Coins:** {quest['reward_coins']}\n{quest['description'][:80]}...",
                inline=False
            )

        embed.set_footer(text="Use 'aceitar quest [nome]' para iniciar uma missão! | 'missão moral' para quests de alinhamento")
        await message.channel.send(embed=embed)

        # Se o comando for "aceitar quest X"
        if "aceitar quest" in content:
            quest_name_search = content.replace("aceitar quest", "").strip()
            found_quest = None
            for quest in available_quests:
                if quest_name_search in quest["name"].lower() or quest_name_search in quest["id"]:
                    found_quest = quest
                    break

            if found_quest:
                view = QuestAcceptButton(user_id, found_quest)
                q_embed = discord.Embed(
                    title=f"📜 {found_quest['name']}",
                    description=f"*{found_quest['npc']} se aproxima:*\n\n*'{found_quest['lore']}'*",
                    color=discord.Color.gold()
                )
                q_embed.add_field(name="🎯 Missão", value=found_quest["description"], inline=False)
                q_embed.add_field(name="⭐ XP", value=f"{found_quest['reward_xp']:,}", inline=True)
                q_embed.add_field(name="💰 Coins", value=str(found_quest["reward_coins"]), inline=True)
                q_embed.add_field(name="⚔️ Dificuldade", value=found_quest["difficulty"], inline=True)
                await message.channel.send(embed=q_embed, view=view)
        return

    await bot.process_commands(message)
# ================= FUNÇÕES AUXILIARES =================
# ======================================================

async def check_level_boss(channel, user_id):
    """Verifica e anuncia boss de level se necessário"""
    player = get_player(user_id)
    boss_levels = [9, 19, 29, 39, 49, 59]

    if player["level"] in boss_levels:
        boss_data = get_level_boss(player["level"])
        if boss_data and boss_data["name"] not in player["bosses"]:
            await asyncio.sleep(2)
            embed = discord.Embed(
                title="⚠️ BOSS DE NÍVEL DETECTADO!",
                description=f"*'O ar fica pesado... Um poder colossal se aproxima!'*\n\n👹 **{boss_data['name']}** surge para testar você!\n\n*'Para avançar ao próximo reino, você deve derrotá-lo!'*",
                color=discord.Color.dark_red()
            )
            embed.add_field(name="❤️ HP", value=str(boss_data["hp"]), inline=True)
            embed.add_field(name="⚔️ ATK", value=str(boss_data["atk"]), inline=True)
            embed.add_field(name="💡 Dica", value="Use `desafiar boss` para enfrentá-lo, ou chame aliados!", inline=False)
            view = BossButton(user_id, boss_data["name"])
            await channel.send(embed=embed, view=view)


async def complete_quest(channel, user_id, player):
    """Completa uma quest e distribui recompensas"""
    quest = player["active_quest"]
    if not quest:
        return

    reward_xp = quest["reward_xp"]
    reward_coins = quest["reward_coins"]
    reward_item = quest.get("reward_item")

    completed = player.get("completed_quests", [])
    completed.append(quest["id"])
    player["completed_quests"] = completed
    player["active_quest"] = None

    save_player_db(user_id, player)
    add_xp(user_id, reward_xp)
    add_coins(user_id, reward_coins)

    if reward_item:
        player2 = get_player(user_id)
        player2["inventory"].append(reward_item)
        save_player_db(user_id, player2)

    embed = discord.Embed(
        title=f"🎉 QUEST COMPLETA!",
        description=f"**{quest['name']}** foi concluída!\n\n*'{quest['npc']} sorri e diz: Extraordinário! Você superou minhas expectativas!'*",
        color=discord.Color.gold()
    )
    embed.add_field(name="⭐ XP Ganho", value=str(reward_xp), inline=True)
    embed.add_field(name="💰 Coins Ganhos", value=str(reward_coins), inline=True)
    if reward_item:
        embed.add_field(name="🎁 Item Recebido", value=reward_item, inline=True)

    await channel.send(embed=embed)

    await channel.send(embed=embed)


# ================= HELPERS: ALINHAMENTO, MAPA, FAZENDA =================

def get_alignment(player):
    pts = player.get("alignment_points", 0)
    if pts >= 30:
        return "Heroi"
    elif pts <= -30:
        return "Vilao"
    elif -29 <= pts <= -5:
        return "Anti-Heroi"
    else:
        return "Neutro"

def get_alignment_info(player):
    align = get_alignment(player)
    return ALIGNMENT_TITLES[align]

def apply_alignment_points(user_id, points):
    player = get_player(user_id)
    cur = player.get("alignment_points", 0)
    player["alignment_points"] = max(-100, min(100, cur + points))
    save_player_db(user_id, player)
    return player

def get_player_map(player):
    """Retorna o mapa descoberto pelo jogador"""
    disc = player.get("discovered_map", {})
    result = {}
    for world_id, world_data in MAP_LOCATIONS.items():
        if world_id not in player.get("worlds", [1]):
            continue
        result[world_id] = {
            "world_name": world_data["world_name"],
            "locations": []
        }
        for loc in world_data["locations"]:
            # cidade principal sempre visível
            disc_locs = disc.get(str(world_id), [])
            visible = loc["discovered"] or loc["id"] in disc_locs
            result[world_id]["locations"].append({**loc, "visible": visible})
    return result

def discover_location(user_id, world_id, loc_id):
    player = get_player(user_id)
    disc = player.get("discovered_map", {})
    key = str(world_id)
    if key not in disc:
        disc[key] = []
    if loc_id not in disc[key]:
        disc[key].append(loc_id)
    player["discovered_map"] = disc
    save_player_db(user_id, player)

def get_dungeon_difficulty_multiplier(player):
    """Dungeons secretas ficam mais difíceis conforme o nível"""
    level = player.get("level", 1)
    return 1.0 + (level * 0.05)  # +5% por nível


# ================= VIEW: ESCOLHER PET DA FAZENDA =================
# ================= VIEW: EMPREGOS =================
class JobSelectView(discord.ui.View):
    def __init__(self, user_id, available_jobs):
        super().__init__(timeout=90)
        self.user_id = user_id
        for job_name in available_jobs[:5]:
            jdata = JOBS[job_name]
            btn = discord.ui.Button(
                label=f"{jdata['emoji']} {job_name}",
                style=discord.ButtonStyle.primary
            )
            btn.callback = self._make_cb(job_name)
            self.add_item(btn)
        cancel = discord.ui.Button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
        cancel.callback = self._cancel
        self.add_item(cancel)

    def _make_cb(self, job_name):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Não é sua escolha!", ephemeral=True)
            player = get_player(self.user_id)
            jdata = JOBS[job_name]
            old_job = player.get("job")
            player["job"] = job_name
            player["job_since"] = int(__import__("time").time())
            # Aplicar bônus permanente de HP
            if job_name == "Cavaleiro":
                player["max_hp"] += 20
                player["hp"] = min(player["hp"] + 20, player["max_hp"])
            elif job_name == "Guarda_Real":
                player["max_hp"] += 35
                player["hp"] = min(player["hp"] + 35, player["max_hp"])
            elif job_name == "Arcano":
                player["max_mana"] = player.get("max_mana", 50) + 15
            save_player_db(self.user_id, player)
            embed = discord.Embed(
                title=f"{jdata['emoji']} Emprego Aceito: **{job_name}**!",
                description=f"*{jdata['work_action']}*\n\n{jdata['description']}",
                color=discord.Color.green()
            )
            perks_text = "\n".join([f"• {p}" for p in jdata["perks"]])
            embed.add_field(name="✨ Benefícios", value=perks_text, inline=False)
            embed.add_field(name="💰 Salário", value=f"`{jdata['salary_coins'][0]}–{jdata['salary_coins'][1]}` coins por turno de trabalho", inline=True)
            embed.add_field(name="⭐ XP por trabalho", value=f"`{jdata['salary_xp'][0]}–{jdata['salary_xp'][1]}`", inline=True)
            if old_job:
                embed.add_field(name="⚠️ Emprego anterior", value=f"Você largou **{old_job}**.", inline=False)
            embed.set_footer(text="Use `trabalhar` para ganhar salário! | `ver emprego` para detalhes")
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    async def _cancel(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Não é sua!", ephemeral=True)
        await interaction.response.edit_message(content="❌ Escolha de emprego cancelada.", embed=None, view=None)


# ================= VIEW: DEFESA DE CIDADE =================
class CityDefenseView(discord.ui.View):
    def __init__(self, user_id, invasion, channel, guild):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.invasion = invasion
        self.channel = channel
        self.guild = guild
        self.helpers = []

        for i, opt in enumerate(invasion.get("dialogue_options", [])):
            btn = discord.ui.Button(
                label=opt["text"][:80],
                style=discord.ButtonStyle.blurple if "negoci" in opt["text"].lower() or "diálogo" in opt["text"].lower()
                      else discord.ButtonStyle.danger,
                row=i // 2
            )
            btn.callback = self._make_cb(i)
            self.add_item(btn)

        call_btn = discord.ui.Button(label="📯 Convocar Aliados", style=discord.ButtonStyle.success, row=2)
        call_btn.callback = self._call_allies
        self.add_item(call_btn)

    def _make_cb(self, idx):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id) and str(interaction.user.id) not in self.helpers:
                return await interaction.response.send_message("❌ Você não está na defesa!", ephemeral=True)
            opt = self.invasion["dialogue_options"][idx]
            import random
            success = random.random() < opt["success_chance"]
            apply_alignment_points(str(interaction.user.id), opt.get("align", 0))
            for h in self.helpers:
                apply_alignment_points(h, opt.get("align", 0) // 2)
            if success:
                xp = self.invasion["xp_reward"]
                coins = self.invasion["coins_reward"]
                add_xp(str(interaction.user.id), xp)
                add_coins(str(interaction.user.id), coins)
                for h in self.helpers:
                    add_xp(h, xp // 2)
                    add_coins(h, coins // 2)
                embed = discord.Embed(
                    title=f"🏆 INVASÃO REPELIDA! — {self.invasion['title']}",
                    description=f"*Sua estratégia funcionou! {self.invasion['enemy']}s recuam!*\n\n"
                                f"🗡️ Opção: **{opt['text'][:60]}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="⭐ XP", value=f"`+{xp}`", inline=True)
                embed.add_field(name="💰 Coins", value=f"`+{coins}`", inline=True)
                if self.helpers:
                    embed.add_field(name="👥 Aliados (XP/2)", value=f"{len(self.helpers)} jogadores ajudaram!", inline=True)
                embed.add_field(name="📣 Povo", value="_As pessoas gritam vivas nas ruas!_", inline=False)
            else:
                xp_loss = self.invasion["xp_reward"] // 4
                remove_xp(str(interaction.user.id), xp_loss)
                embed = discord.Embed(
                    title=f"💀 INVASÃO AVANÇA! — {self.invasion['title']}",
                    description=f"*Sua estratégia falhou! Os inimigos avançam mais!*\n\n"
                                f"❌ Opção: **{opt['text'][:60]}**",
                    color=discord.Color.red()
                )
                embed.add_field(name="❌ XP Perdido", value=f"`-{xp_loss}`", inline=True)
                embed.add_field(name="💡 Dica", value="Tente outra abordagem ou `lutar` diretamente!", inline=False)
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    async def _call_allies(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Só o defensor pode convocar!", ephemeral=True)
        embed = discord.Embed(
            title=f"📯 CONVOCAÇÃO DE DEFESA!",
            description=f"**{interaction.user.display_name}** convoca aliados para defender contra:\n"
                        f"**{self.invasion['title']}**\n\n"
                        f"*Responda `ajudar defesa` para participar!*\n"
                        f"👥 Mínimo necessário: **{self.invasion['min_defenders']}** defensores",
            color=discord.Color.orange()
        )
        await self.channel.send(embed=embed)
        await interaction.response.send_message("📯 Convocação enviada ao canal!", ephemeral=True)


class CityDefenseJoinView(discord.ui.View):
    """View para aliados entrarem na defesa ativa"""
    def __init__(self, defense_view: CityDefenseView):
        super().__init__(timeout=60)
        self.dview = defense_view

    @discord.ui.button(label="⚔️ Entrar na Defesa!", style=discord.ButtonStyle.danger)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        if uid == self.dview.user_id:
            return await interaction.response.send_message("Você já é o defensor principal!", ephemeral=True)
        if uid in self.dview.helpers:
            return await interaction.response.send_message("Você já está na defesa!", ephemeral=True)
        player = get_player(uid)
        if not player:
            return await interaction.response.send_message("❌ Crie seu personagem primeiro!", ephemeral=True)
        self.dview.helpers.append(uid)
        await interaction.response.send_message(
            f"⚔️ **{interaction.user.display_name}** entra na defesa! ({len(self.dview.helpers)+1} defensores total)",
            ephemeral=False
        )


class NomearCavaleiroView(discord.ui.View):
    """View para Rei nomear cavaleiros"""
    def __init__(self, king_id, target_user):
        super().__init__(timeout=60)
        self.king_id = king_id
        self.target_user = target_user

    @discord.ui.button(label="⚔️ Aceitar o Título", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.target_user.id):
            return await interaction.response.send_message("❌ Não é para você!", ephemeral=True)
        player = get_player(str(self.target_user.id))
        if player:
            player["city_title"] = "Cavaleiro"
            save_player_db(str(self.target_user.id), player)
            king = get_player(self.king_id)
            knights = king.get("knights", [])
            knights.append(str(self.target_user.id))
            king["knights"] = knights
            save_player_db(self.king_id, king)
        embed = discord.Embed(
            title="⚔️ Cavaleiro do Reino!",
            description=f"**{self.target_user.display_name}** aceita o título de **Cavaleiro** e ajoelha diante do Rei!\n\n*'Com este título, juro proteger o povo com minha vida!'*",
            color=discord.Color.gold()
        )
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Recusar", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.target_user.id):
            return await interaction.response.send_message("❌ Não é para você!", ephemeral=True)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="*O guerreiro recusa a genuflexão. Um rei deve respeitar isso.*", embed=None, view=self)


class PetFarmSelectView(discord.ui.View):
    def __init__(self, user_id, farm_pets):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.farm_pets = farm_pets
        for i, pet in enumerate(farm_pets[:5]):
            btn = discord.ui.Button(
                label=f"{pet.get('emoji','🐾')} {pet['name']}",
                style=discord.ButtonStyle.primary,
                custom_id=f"farm_pet_{i}"
            )
            btn.callback = self._make_callback(i)
            self.add_item(btn)

    def _make_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                await interaction.response.send_message("❌ Não é sua fazenda!", ephemeral=True)
                return
            player = get_player(self.user_id)
            chosen = self.farm_pets[index]
            old_pet = player.get("pet")
            farm = player.get("pet_farm", [])
            # Remover da fazenda e colocar equipado
            farm = [p for p in farm if p["name"] != chosen["name"]]
            # Enviar atual para fazenda se tinha
            if old_pet:
                try:
                    old_pet_obj = json.loads(old_pet) if isinstance(old_pet, str) else old_pet
                    farm.append(old_pet_obj)
                except:
                    pass
            player["pet"] = json.dumps(chosen)
            player["pet_farm"] = farm
            save_player_db(self.user_id, player)
            embed = discord.Embed(
                title=f"🔄 Pet Trocado!",
                description=f"{chosen.get('emoji','🐾')} **{chosen['name']}** saiu da fazenda e agora te acompanha!",
                color=discord.Color.green()
            )
            if old_pet:
                try:
                    old_obj = json.loads(old_pet) if isinstance(old_pet, str) else old_pet
                    embed.add_field(name="🏡 Enviado à Fazenda", value=f"{old_obj.get('emoji','🐾')} {old_obj['name']}", inline=False)
                except:
                    pass
            await interaction.response.edit_message(embed=embed, view=None)
        return callback


# ================= VIEW: MIMIC CHEST =================
class MimicChestView(discord.ui.View):
    def __init__(self, user_id, tier_idx, world):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.tier = MIMIC_TIERS[tier_idx]
        self.world = world

    @discord.ui.button(label="🔓 Abrir o Baú", style=discord.ButtonStyle.danger)
    async def open_chest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Não é seu baú!", ephemeral=True)
            return
        player = get_player(self.user_id)
        tier = self.tier
        is_mimic = random.random() < tier["mimic_chance"]

        if is_mimic:
            dmg = random.randint(*tier["mimic_dmg"])
            xp_loss = random.randint(*tier["mimic_xp_loss"])
            player["hp"] = max(1, player["hp"] - dmg)
            save_player_db(self.user_id, player)
            # Remove some XP
            remove_xp(self.user_id, xp_loss)
            embed = discord.Embed(
                title=f"💀 MIMIC! {tier['emoji']} — {tier['name']}",
                description=tier["mimic_desc"],
                color=discord.Color.dark_red()
            )
            embed.add_field(name="💥 Dano Sofrido", value=f"`-{dmg} HP`", inline=True)
            embed.add_field(name="💀 XP Perdido", value=f"`-{xp_loss} XP`", inline=True)
            embed.add_field(name="❤️ HP Restante", value=f"`{player['hp']}/{player['max_hp']}`", inline=True)
            embed.add_field(name="📝 Lição", value="_Mimics aprenderam a imitar baús para sobreviver. Você foi enganado pelo mais antigo truque das masmorras._", inline=False)
            embed.set_footer(text="Use `curar` para recuperar HP!")
        else:
            loot_xp = random.randint(*tier["loot_xp"])
            loot_coins = random.randint(*tier["loot_coins"])
            # Item aleatório pela raridade permitida
            rarity_pool = tier["loot_items"]
            loot_item = None
            world_items = WORLDS[self.world].get("items", []) if self.world in WORLDS else []
            filtered = [i for i in world_items if i.get("rarity") in rarity_pool]
            if filtered:
                loot_item = random.choice(filtered)["name"]
            add_xp(self.user_id, loot_xp)
            add_coins(self.user_id, loot_coins)
            if loot_item:
                p2 = get_player(self.user_id)
                p2["inventory"].append(loot_item)
                save_player_db(self.user_id, p2)
            embed = discord.Embed(
                title=f"✨ Baú Aberto! {tier['emoji']} — {tier['name']}",
                description=f"*O baú cede com um estalido. Uma aura dourada emana de dentro...*",
                color=discord.Color.gold()
            )
            embed.add_field(name="⭐ XP", value=f"`+{loot_xp}`", inline=True)
            embed.add_field(name="💰 Coins", value=f"`+{loot_coins}`", inline=True)
            if loot_item:
                embed.add_field(name="🎁 Item", value=f"`{loot_item}`", inline=True)

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🚶 Deixar pra lá", style=discord.ButtonStyle.secondary)
    async def leave_chest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Não é seu baú!", ephemeral=True)
            return
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🚶 Você se afastou do baú",
                description="*Às vezes a prudência é o maior tesouro.*",
                color=discord.Color.greyple()
            ), view=None
        )


# ================= VIEW: CENÁRIO MORAL =================
class ScenarioChoiceView(discord.ui.View):
    def __init__(self, user_id, scenario):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.scenario = scenario
        for i, choice in enumerate(scenario["choices"]):
            btn = discord.ui.Button(
                label=choice["text"][:80],
                style=discord.ButtonStyle.primary if choice["align"] > 0 else (
                    discord.ButtonStyle.danger if choice["align"] < -5 else discord.ButtonStyle.secondary
                ),
                row=i // 2
            )
            btn.callback = self._make_callback(i)
            self.add_item(btn)

    def _make_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                await interaction.response.send_message("❌ Não é sua escolha!", ephemeral=True)
                return
            choice = self.scenario["choices"][index]
            player = apply_alignment_points(self.user_id, choice["align"])
            add_xp(self.user_id, choice["xp"])
            add_coins(self.user_id, choice["coins"])
            new_align = get_alignment(player)
            info = ALIGNMENT_TITLES[new_align]
            color = discord.Color(info["color"])
            embed = discord.Embed(
                title=f"{info['emoji']} Consequência",
                description=f"*{choice['result']}*",
                color=color
            )
            if choice["xp"]:
                embed.add_field(name="⭐ XP", value=f"`+{choice['xp']}`", inline=True)
            if choice["coins"]:
                embed.add_field(name="💰 Coins", value=f"`+{choice['coins']}`", inline=True)
            align_pts = player.get("alignment_points", 0)
            embed.add_field(name=f"{info['emoji']} Alinhamento", value=f"**{new_align}** ({align_pts:+d} pts)", inline=False)
            embed.set_footer(text=info["desc"])
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
        return callback


# ================= COMANDOS NOVOS =================
BOT_OWNER_ID = os.getenv("OWNER_ID", str(ADMIN_ID))  # Defina no .env OWNER_ID=seu_discord_id

@bot.listen("on_message")
async def handle_new_commands(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    # ===== FAZENDA DE PETS =====
    if content in ["fazenda", "minha fazenda", "pet fazenda", "pets fazenda"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro com `começar`!")
            return
        farm = player.get("pet_farm", [])
        current_pet = player.get("pet")
        embed = discord.Embed(title="🏡 Sua Fazenda de Pets", color=discord.Color.green())
        if current_pet:
            try:
                cp = json.loads(current_pet) if isinstance(current_pet, str) else current_pet
                embed.add_field(
                    name="🐾 Pet Equipado",
                    value=f"{cp.get('emoji','🐾')} **{cp['name']}** [{cp.get('rarity','?')}]\n`+{cp.get('bonus_hp',0)} HP` | `+{cp.get('bonus_atk',0)} ATK`",
                    inline=False
                )
            except:
                embed.add_field(name="🐾 Pet Equipado", value=str(current_pet), inline=False)
        else:
            embed.add_field(name="🐾 Pet Equipado", value="_Nenhum_", inline=False)

        if farm:
            farm_text = ""
            for i, pet in enumerate(farm[:10]):
                farm_text += f"{i+1}. {pet.get('emoji','🐾')} **{pet['name']}** [{pet.get('rarity','?')}] — `+{pet.get('bonus_hp',0)} HP` / `+{pet.get('bonus_atk',0)} ATK`\n"
            embed.add_field(name=f"🌾 Na Fazenda ({len(farm)} pets)", value=farm_text, inline=False)
            embed.set_footer(text="Use `trocar pet` para escolher um da fazenda!")
        else:
            embed.add_field(name="🌾 Na Fazenda", value="_Vazia. Caçe pets para populá-la!_", inline=False)
        await message.channel.send(embed=embed)

    # ===== TROCAR PET =====
    elif content in ["trocar pet", "mudar pet", "escolher pet"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        farm = player.get("pet_farm", [])
        if not farm:
            await message.channel.send("🏡 Sua fazenda está vazia! Não há pets para trocar.\nCapture mais pets caçando com `caçar`.")
            return
        embed = discord.Embed(
            title="🔄 Trocar Pet",
            description="Escolha um pet da fazenda para equipar. O pet atual será enviado para a fazenda.",
            color=discord.Color.blurple()
        )
        for pet in farm[:5]:
            embed.add_field(
                name=f"{pet.get('emoji','🐾')} {pet['name']}",
                value=f"Raridade: **{pet.get('rarity','?')}**\n`+{pet.get('bonus_hp',0)} HP` | `+{pet.get('bonus_atk',0)} ATK`",
                inline=True
            )
        view = PetFarmSelectView(uid, farm)
        await message.channel.send(embed=embed, view=view)

    # ===== ENVIAR PET PARA FAZENDA =====
    elif content.startswith("enviar pet fazenda") or content in ["guardar pet", "depositar pet"]:
        player = get_player(uid)
        if not player:
            return
        current_pet = player.get("pet")
        if not current_pet:
            await message.channel.send("❌ Você não tem pet equipado!")
            return
        try:
            cp = json.loads(current_pet) if isinstance(current_pet, str) else current_pet
            farm = player.get("pet_farm", [])
            farm.append(cp)
            player["pet"] = None
            player["pet_farm"] = farm
            save_player_db(uid, player)
            embed = discord.Embed(
                title="🏡 Pet Enviado!",
                description=f"{cp.get('emoji','🐾')} **{cp['name']}** foi para a fazenda feliz!",
                color=discord.Color.green()
            )
            embed.set_footer(text="Use `trocar pet` para escolhê-lo de volta quando quiser.")
            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"❌ Erro ao enviar pet: {e}")

    # ===== TROCAR CSI COINS POR MONSTRINHOS COINS =====
    elif content.startswith("trocar coins") or content.startswith("converter coins"):
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        parts = content.split()
        amount = 0
        for p in parts:
            if p.isdigit():
                amount = int(p)
                break
        if amount <= 0:
            await message.channel.send(
                "💱 **Como trocar coins:**\n`trocar coins 100` — envia pedido de troca de 100 CSI Coins por Monstrinhos Coins.\n"
                "O dono do servidor será notificado e aprovará a troca.\n\n"
                f"Seu saldo atual: **{player['coins']} CSI Coins** 💰"
            )
            return
        if player["coins"] < amount:
            await message.channel.send(f"❌ Você tem apenas **{player['coins']}** coins! Pediu {amount}.")
            return

        # Salvar pedido no DB
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO coin_exchange_requests (user_id, username, csi_coins) VALUES (?, ?, ?)",
                  (uid, str(message.author), amount))
        req_id = c.lastrowid
        conn.commit()
        conn.close()

        # Notificar dono via DM
        owner_id = int(BOT_OWNER_ID) if BOT_OWNER_ID != "0" else None
        if owner_id:
            try:
                owner = await bot.fetch_user(owner_id)
                dm_embed = discord.Embed(
                    title="💱 PEDIDO DE TROCA DE COINS",
                    description=f"**Usuário:** {message.author} (`{uid}`)\n**Servidor:** {message.guild.name if message.guild else 'DM'}\n**Pedido:** {amount} CSI Coins → Monstrinhos Coins\n**ID do Pedido:** #{req_id}",
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name="✅ Para APROVAR", value=f"`aprovar troca {req_id}`", inline=True)
                dm_embed.add_field(name="❌ Para RECUSAR", value=f"`recusar troca {req_id}`", inline=True)
                await owner.send(embed=dm_embed)
            except Exception as e:
                print(f"Erro ao enviar DM ao owner: {e}")

        embed = discord.Embed(
            title="📤 Pedido Enviado!",
            description=f"Seu pedido de troca de **{amount} CSI Coins** foi registrado e enviado ao administrador.\nAguarde a aprovação!",
            color=discord.Color.blurple()
        )
        embed.add_field(name="📋 ID do Pedido", value=f"#{req_id}", inline=True)
        embed.add_field(name="💰 Coins Solicitados", value=f"{amount}", inline=True)
        await message.channel.send(embed=embed)

    # ===== OWNER: APROVAR/RECUSAR TROCA =====
    elif content.startswith("aprovar troca ") and uid == BOT_OWNER_ID:
        parts = content.split()
        if len(parts) < 3 or not parts[2].isdigit():
            await message.channel.send("❌ Uso: `aprovar troca <id>`")
            return
        req_id = int(parts[2])
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_id, username, csi_coins, status FROM coin_exchange_requests WHERE id = ?", (req_id,))
        row = c.fetchone()
        if not row:
            await message.channel.send(f"❌ Pedido #{req_id} não encontrado.")
            conn.close()
            return
        req_uid, req_uname, req_coins, status = row
        if status != "pending":
            await message.channel.send(f"❌ Pedido #{req_id} já foi processado ({status}).")
            conn.close()
            return
        # Resetar coins do jogador
        player = get_player(req_uid)
        if player:
            old_coins = player["coins"]
            player["coins"] = max(0, player["coins"] - req_coins)
            save_player_db(req_uid, player)
        c.execute("UPDATE coin_exchange_requests SET status = 'approved' WHERE id = ?", (req_id,))
        conn.commit()
        conn.close()
        # Notificar jogador
        try:
            target_user = await bot.fetch_user(int(req_uid))
            notify_embed = discord.Embed(
                title="✅ Troca Aprovada!",
                description=f"Sua troca de **{req_coins} CSI Coins** por Monstrinhos Coins foi **APROVADA**!\nSeus coins foram descontados. Entre em contato com o administrador para receber seus Monstrinhos Coins! 🎉",
                color=discord.Color.green()
            )
            await target_user.send(embed=notify_embed)
        except:
            pass
        await message.channel.send(f"✅ Pedido #{req_id} de **{req_uname}** aprovado! {req_coins} coins descontados.")

    elif content.startswith("recusar troca ") and uid == BOT_OWNER_ID:
        parts = content.split()
        if len(parts) < 3 or not parts[2].isdigit():
            await message.channel.send("❌ Uso: `recusar troca <id>`")
            return
        req_id = int(parts[2])
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_id, username, csi_coins, status FROM coin_exchange_requests WHERE id = ?", (req_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            await message.channel.send(f"❌ Pedido #{req_id} não encontrado.")
            return
        req_uid, req_uname, req_coins, status = row
        conn2 = sqlite3.connect(DB_FILE)
        c2 = conn2.cursor()
        c2.execute("UPDATE coin_exchange_requests SET status = 'refused' WHERE id = ?", (req_id,))
        conn2.commit()
        conn2.close()
        try:
            target_user = await bot.fetch_user(int(req_uid))
            await target_user.send(embed=discord.Embed(
                title="❌ Troca Recusada",
                description=f"Seu pedido de troca de **{req_coins} CSI Coins** foi recusado. Entre em contato com o administrador para mais detalhes.",
                color=discord.Color.red()
            ))
        except:
            pass
        await message.channel.send(f"❌ Pedido #{req_id} de **{req_uname}** recusado.")

    # ===== ALINHAMENTO MORAL =====
    elif content in ["alinhamento", "meu alinhamento", "ver alinhamento", "moralidade"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        align = get_alignment(player)
        info = ALIGNMENT_TITLES[align]
        pts = player.get("alignment_points", 0)
        color = discord.Color(info["color"])

        bar_fill = int((pts + 100) / 200 * 20)
        bar = "🟥" * max(0, 10 - bar_fill // 2) + "⬛" * max(0, bar_fill - 10) if pts < 0 else "⬛" * max(0, 10 - bar_fill // 2) + "🟨" * max(0, bar_fill // 2)
        villain_bar = "🔴" * min(10, max(0, (-pts) // 10))
        hero_bar = "🟡" * min(10, max(0, pts // 10))
        full_bar = "💀" * max(0, 10 - len(villain_bar) - len(hero_bar)) + villain_bar + "⚖️" + hero_bar + "✨" * max(0, 10 - len(hero_bar))

        embed = discord.Embed(
            title=f"{info['emoji']} {align} — {message.author.display_name}",
            description=f"*{info['desc']}*",
            color=color
        )
        embed.add_field(name="📊 Pontos de Alinhamento", value=f"`{pts:+d} / 100`", inline=True)
        evil_bar = "🔴" * min(10, max(0, 10 - (pts + 100) // 20))
        good_bar = "🟡" * min(10, max(0, (pts + 100) // 20))
        embed.add_field(name="☯️ Espectro Moral", value=f"💀 {evil_bar}|{good_bar} ✨", inline=False)
        embed.add_field(
            name="🎯 Próximo Alinhamento",
            value=(
                f"**Herói** em `{max(0, 30 - pts)} pts`" if pts < 30 else
                f"**Vilão** em `{max(0, pts + 30)} pts negativos`" if pts > -30 else
                "Você está no extremo!"
            ),
            inline=False
        )
        quests_available = []
        for key, qlist in ALIGNMENT_QUESTS.items():
            for q in qlist:
                req = q.get("align_required")
                if req is None or req == align:
                    quests_available.append(q["name"])
        if quests_available:
            embed.add_field(name="📋 Quests Disponíveis pro seu Alinhamento", value="\n".join(quests_available[:5]), inline=False)
        await message.channel.send(embed=embed)

    # ===== CENÁRIO MORAL =====
    elif content in ["cenário", "cenario", "evento moral", "situação", "situacao"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        world_key = max(k for k in player.get("worlds", [1]))
        scenario_pool = ALIGNMENT_SCENARIOS.get(world_key, ALIGNMENT_SCENARIOS.get(1, []))
        if not scenario_pool:
            await message.channel.send("🌍 Não há cenários para este reino ainda.")
            return
        scenario = random.choice(scenario_pool)
        embed = discord.Embed(
            title=f"{scenario['emoji']} {scenario['title']}",
            description=scenario["description"],
            color=discord.Color.gold()
        )
        align = get_alignment(player)
        info = ALIGNMENT_TITLES[align]
        embed.set_footer(text=f"Alinhamento atual: {info['emoji']} {align} | Suas escolhas definem quem você é.")
        view = ScenarioChoiceView(uid, scenario)
        await message.channel.send(embed=embed, view=view)

    # ===== ABRIR MAPA =====
    elif content in ["abrir mapa", "mapa", "meu mapa", "ver mapa"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        player_map = get_player_map(player)
        embed = discord.Embed(
            title="🗺️ Mapa do Mundo",
            description="Locais descobertos durante sua jornada. Use `viajar <nome do local>` para se locomover.",
            color=discord.Color.blue()
        )
        current_world = max(player.get("worlds", [1]))
        for world_id, wdata in player_map.items():
            locs_text = ""
            for loc in wdata["locations"]:
                if loc.get("visible"):
                    type_icons = {
                        "cidade": "🏙️", "recurso": "⛏️", "dungeon": "🕳️", "dungeon_secreta": "🔮",
                        "boss_local": "💀", "lore": "📜", "loja": "🏪", "crafting": "⚒️",
                        "portal": "🌀", "evento_especial": "⭐", "npc_especial": "🧙"
                    }
                    icon = type_icons.get(loc["type"], "📍")
                    marker = "📌" if world_id == current_world else ""
                    locs_text += f"{icon} {loc['name']} {marker}\n"
                else:
                    locs_text += f"❓ *Local Desconhecido*\n"
            if locs_text:
                current_marker = " ← **AQUI**" if world_id == current_world else ""
                embed.add_field(
                    name=f"{wdata['world_name']}{current_marker}",
                    value=locs_text or "_Nenhum local descoberto_",
                    inline=False
                )
        embed.set_footer(text="💡 Dica: Explore com `explorar` para descobrir novos locais!")
        await message.channel.send(embed=embed)

    # ===== VIAJAR =====
    elif content.startswith("viajar ") or content.startswith("ir para ") or content.startswith("ir pra "):
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        destination = content.split(maxsplit=1)[1].strip().lower()
        player_map = get_player_map(player)
        found_loc = None
        found_world = None
        for world_id, wdata in player_map.items():
            for loc in wdata["locations"]:
                if loc.get("visible") and destination in loc["name"].lower():
                    found_loc = loc
                    found_world = world_id
                    break
        # Também verificar por número de mundo
        if not found_loc:
            for world_id in player.get("worlds", [1]):
                world_name = MAP_LOCATIONS.get(world_id, {}).get("world_name", "")
                if destination in world_name.lower():
                    found_world = world_id
                    found_loc = {"name": world_name, "id": f"world_{world_id}", "type": "cidade"}
                    break
        if not found_loc:
            await message.channel.send(
                f"❓ Local '**{destination}**' não encontrado ou ainda não descoberto.\n"
                "Use `abrir mapa` para ver seus locais conhecidos."
            )
            return
        # Verificar se o mundo está desbloqueado
        if found_world not in player.get("worlds", [1]):
            await message.channel.send(f"🔒 O reino **{MAP_LOCATIONS.get(found_world, {}).get('world_name', '?')}** ainda está bloqueado! Derrote o boss do reino anterior.")
            return
        # Atualizar mundo atual do jogador
        worlds = player.get("worlds", [1])
        if found_world not in worlds:
            await message.channel.send(f"🔒 Você ainda não desbloqueou este reino!")
            return
        # Registrar viagem (mover o "mundo ativo" para o escolhido)
        player["worlds"] = worlds  # mantém tudo que já tem
        save_player_db(uid, player)
        world_name = MAP_LOCATIONS.get(found_world, {}).get("world_name", str(found_world))
        embed = discord.Embed(
            title=f"✈️ Viajando para {found_loc['name']}",
            description=f"*Você parte em direção a **{world_name}**...*\n\nChegou em **{found_loc['name']}**! O ar aqui é diferente.",
            color=discord.Color.teal()
        )
        embed.add_field(name="📍 Local", value=found_loc["name"], inline=True)
        embed.add_field(name="🌍 Reino", value=world_name, inline=True)
        embed.set_footer(text="Use `explorar` para começar a aventura neste local!")
        # Descobrir local se ainda não estava marcado
        disc = player.get("discovered_map", {})
        key = str(found_world)
        if key not in disc:
            disc[key] = []
        if found_loc.get("id") and found_loc["id"] not in disc[key]:
            disc[key].append(found_loc["id"])
            player["discovered_map"] = disc
            save_player_db(uid, player)
            embed.add_field(name="🗺️ Descoberta!", value=f"Local adicionado ao mapa!", inline=False)
        await message.channel.send(embed=embed)

    # ===== MISSÃO MORAL =====
    elif content in ["missão moral", "missao moral", "quest moral", "missão alinhamento"]:
        player = get_player(uid)
        if not player:
            return
        align = get_alignment(player)
        all_quests = []
        for key, qlist in ALIGNMENT_QUESTS.items():
            for q in qlist:
                req = q.get("align_required")
                if req is None or req == align:
                    all_quests.append(q)
        if not all_quests:
            await message.channel.send("❌ Nenhuma missão disponível para seu alinhamento.")
            return
        quest = random.choice(all_quests)
        if player.get("active_quest"):
            await message.channel.send("❌ Você já tem uma quest ativa! Use `finalizar quest` ou `abandonar quest`.")
            return
        info = ALIGNMENT_TITLES[align]
        embed = discord.Embed(
            title=f"{info['emoji']} {quest['name']}",
            description=quest["description"],
            color=discord.Color(info["color"])
        )
        embed.add_field(name="📝 Lore", value=quest["lore"], inline=False)
        embed.add_field(name="👤 NPC", value=quest["npc"], inline=True)
        embed.add_field(name="⚔️ Dificuldade", value=quest["difficulty"], inline=True)
        embed.add_field(name="⭐ Recompensa XP", value=f"{quest['reward_xp']:,}", inline=True)
        embed.add_field(name="💰 Recompensa Coins", value=str(quest["reward_coins"]), inline=True)
        view = QuestAcceptButton(str(uid), quest)
        await message.channel.send(embed=embed, view=view)

    # ===== DESCOBRIR LOCAL (ao explorar) — trigger automático =====
    # Isso é chamado internamente, não diretamente pelo usuário

    # ===== VER PEDIDOS DE TROCA (admin) =====
    elif content in ["ver trocas", "pedidos de troca"] and uid == BOT_OWNER_ID:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, user_id, username, csi_coins, status, created_at FROM coin_exchange_requests WHERE status = 'pending' ORDER BY created_at DESC LIMIT 10")
        rows = c.fetchall()
        conn.close()
        if not rows:
            await message.channel.send("📋 Nenhum pedido de troca pendente.")
            return
        embed = discord.Embed(title="💱 Pedidos de Troca Pendentes", color=discord.Color.orange())
        for row in rows:
            req_id, req_uid, req_uname, req_coins, req_status, created = row
            embed.add_field(
                name=f"#{req_id} — {req_uname}",
                value=f"💰 **{req_coins}** CSI Coins\n`aprovar troca {req_id}` | `recusar troca {req_id}`",
                inline=False
            )
        await message.channel.send(embed=embed)

    # ===== EMPREGOS =====
    elif content in ["procurar emprego", "empregos", "quero emprego", "ver empregos", "escolher emprego"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        if player["level"] < 5:
            await message.channel.send(
                f"⚠️ Você precisa ser **nível 5** para procurar emprego!\n"
                f"Nível atual: **{player['level']}**\nContinue explorando!"
            )
            return
        current_job = player.get("job")
        avail = [name for name, jdata in JOBS.items() if player["level"] >= jdata["min_level"]]
        embed = discord.Embed(
            title="💼 Empregos do Reino",
            description="*O taberneiro pregou uma lista de vagas na parede. Você se aproxima para ler...*",
            color=discord.Color.blurple()
        )
        if current_job:
            jd = JOBS.get(current_job, {})
            embed.add_field(
                name=f"🔖 Emprego Atual: {jd.get('emoji','?')} {current_job}",
                value=f"_{jd.get('description','')}_\nUse `trabalhar` para ganhar salário!",
                inline=False
            )
        for jname in avail:
            jd = JOBS[jname]
            embed.add_field(
                name=f"{jd['emoji']} {jname} (Nível {jd['min_level']}+)",
                value=f"_{jd['description']}_\n💰 `{jd['salary_coins'][0]}–{jd['salary_coins'][1]}` coins | ⭐ `{jd['salary_xp'][0]}–{jd['salary_xp'][1]}` XP",
                inline=True
            )
        embed.set_footer(text="Escolha um emprego abaixo! Você pode trocar a qualquer momento.")
        view = JobSelectView(uid, avail)
        await message.channel.send(embed=embed, view=view)

    elif content in ["ver emprego", "meu emprego", "emprego atual"]:
        player = get_player(uid)
        if not player:
            return
        job = player.get("job")
        if not job:
            await message.channel.send("💼 Você não tem emprego! Use `procurar emprego` para ver vagas disponíveis.")
            return
        jd = JOBS[job]
        import time
        since = player.get("job_since", 0)
        hours_working = int((time.time() - since) / 3600) if since else 0
        embed = discord.Embed(
            title=f"{jd['emoji']} Seu Emprego: **{job}**",
            description=f"*{jd['work_action']}*\n\n{jd['description']}",
            color=discord.Color.green()
        )
        perks_text = "\n".join([f"• {p}" for p in jd["perks"]])
        embed.add_field(name="✨ Benefícios", value=perks_text, inline=False)
        embed.add_field(name="💰 Salário por turno", value=f"`{jd['salary_coins'][0]}–{jd['salary_coins'][1]}` coins", inline=True)
        embed.add_field(name="⭐ XP por turno", value=f"`{jd['salary_xp'][0]}–{jd['salary_xp'][1]}`", inline=True)
        embed.add_field(name="⏱️ Trabalhando há", value=f"`{hours_working}h`", inline=True)
        title = player.get("city_title")
        if title:
            embed.add_field(name="🏅 Título na Cidade", value=f"**{title}**", inline=False)
        embed.set_footer(text="Use `trabalhar` para ganhar salário!")
        await message.channel.send(embed=embed)

    elif content in ["trabalhar", "ir trabalhar", "fazer trabalho"]:
        import time
        player = get_player(uid)
        if not player:
            return
        job = player.get("job")
        if not job:
            await message.channel.send("💼 Você não tem emprego! Use `procurar emprego`.")
            return
        jd = JOBS[job]
        last_work = player.get("last_work", 0)
        now = int(time.time())
        cooldown = 1800  # 30 min
        if now - last_work < cooldown:
            remaining = cooldown - (now - last_work)
            mins = remaining // 60
            await message.channel.send(f"⏳ Você já trabalhou recentemente! Próximo turno em **{mins} minutos**.")
            return
        coins = random.randint(*jd["salary_coins"])
        xp = random.randint(*jd["salary_xp"])
        work_msg = random.choice(jd["work_msgs"])
        # Bônus de curandeiro
        hp_bonus = 0
        if job == "Curandeiro":
            hp_bonus = 10
            player["hp"] = min(player["max_hp"], player["hp"] + hp_bonus)
        player["last_work"] = now
        save_player_db(uid, player)
        add_coins(uid, coins)
        leveled = add_xp(uid, xp)
        embed = discord.Embed(
            title=f"{jd['emoji']} Turno de Trabalho — {job}",
            description=work_msg,
            color=discord.Color.green()
        )
        embed.add_field(name="💰 Salário", value=f"`+{coins}` coins", inline=True)
        embed.add_field(name="⭐ XP", value=f"`+{xp}`", inline=True)
        if hp_bonus:
            embed.add_field(name="💚 Cura", value=f"`+{hp_bonus} HP`", inline=True)
        if leveled:
            p2 = get_player(uid)
            embed.add_field(name="🆙 Level Up!", value=f"Nível **{p2['level']}**!", inline=False)
        embed.set_footer(text="Próximo turno em 30 minutos.")
        await message.channel.send(embed=embed)

    elif content in ["largar emprego", "demissao", "demissão", "sair do emprego"]:
        player = get_player(uid)
        if not player:
            return
        job = player.get("job")
        if not job:
            await message.channel.send("💼 Você não tem emprego para largar!")
            return
        jd = JOBS[job]
        player["job"] = None
        save_player_db(uid, player)
        await message.channel.send(
            embed=discord.Embed(
                title=f"{jd['emoji']} Você largou o emprego de **{job}**",
                description=f"*Você entrega sua ferramenta e parte. Um novo capítulo começa.*",
                color=discord.Color.greyple()
            )
        )

    # ===== DEFENDER CIDADE (Cavaleiro/Guarda/Rei) =====
    elif content in ["defender cidade", "patrulhar", "defender reino", "modo defesa"]:
        import time
        player = get_player(uid)
        if not player:
            return
        job = player.get("job")
        title = player.get("city_title")
        has_defense_role = job in ["Cavaleiro", "Guarda_Real", "Rei"] or title in ["Cavaleiro", "Rei"]
        if not has_defense_role:
            await message.channel.send(
                "⚔️ Apenas **Cavaleiros**, **Guardas Reais** e **Reis** podem defender a cidade!\n"
                "Use `procurar emprego` para se tornar um cavaleiro (requer nível 10)."
            )
            return
        last_defend = player.get("last_defend", 0)
        now = int(time.time())
        if now - last_defend < 3600:
            remaining = (3600 - (now - last_defend)) // 60
            await message.channel.send(f"⏳ Você já patrulhou! Próxima defesa em **{remaining} minutos**.")
            return
        world_key = max(k for k in player.get("worlds", [1]))
        world_invasions = CITY_INVASION_EVENTS.get(world_key, CITY_INVASION_EVENTS.get(1, []))
        invasion = random.choice(world_invasions)
        player["last_defend"] = now
        save_player_db(uid, player)
        jd = JOBS.get(job, JOBS.get("Cavaleiro", {}))
        embed = discord.Embed(
            title=f"🚨 INVASÃO! — {invasion['title']}",
            description=f"*{invasion['description']}*\n\n"
                        f"👹 Inimigo: **{invasion['enemy']}** ×{invasion['enemy_count']}\n"
                        f"💪 Min. defensores: **{invasion['min_defenders']}**",
            color=discord.Color.red()
        )
        embed.add_field(name="⭐ Recompensa", value=f"`+{invasion['xp_reward']} XP` | `+{invasion['coins_reward']} coins`", inline=True)
        embed.add_field(
            name="💡 Como agir",
            value="Escolha sua estratégia abaixo!\nUse **📯 Convocar Aliados** para chamar outros jogadores.",
            inline=False
        )
        embed.set_footer(text=f"Defensor: {message.author.display_name} | {jd.get('emoji','⚔️')} {job}")
        view = CityDefenseView(uid, invasion, message.channel, message.guild)
        await message.channel.send(embed=embed, view=view)

    elif content in ["ajudar defesa", "defender junto", "entrar defesa"]:
        await message.channel.send(
            embed=discord.Embed(
                title="⚔️ Prontidão para Defesa",
                description=f"**{message.author.display_name}** está pronto para defender!\nAguardando convocação ativa de um Cavaleiro ou Rei.",
                color=discord.Color.blue()
            )
        )

    # ===== NOMEAR CAVALEIRO (só Rei) =====
    elif content.startswith("nomear cavaleiro ") or content.startswith("nomear guerreiro "):
        player = get_player(uid)
        if not player:
            return
        if player.get("job") != "Rei" and player.get("city_title") != "Rei":
            await message.channel.send("👑 Apenas o **Rei** pode nomear cavaleiros!")
            return
        mentions = message.mentions
        if not mentions:
            await message.channel.send("❌ Mencione o jogador: `nomear cavaleiro @usuario`")
            return
        target = mentions[0]
        tplayer = get_player(str(target.id))
        if not tplayer:
            await message.channel.send("❌ Esse jogador ainda não começou sua jornada!")
            return
        embed = discord.Embed(
            title="⚔️ Cerimônia de Nomeação",
            description=f"**{message.author.display_name}** deseja nomear **{target.display_name}** como **Cavaleiro do Reino**!\n\n{target.mention}, você aceita a responsabilidade?",
            color=discord.Color.gold()
        )
        view = NomearCavaleiroView(uid, target)
        await message.channel.send(embed=embed, view=view)

    # ===== TORNAR-SE REI =====
    elif content in ["me tornar rei", "quero ser rei", "proclamar rei", "assumir trono"]:
        player = get_player(uid)
        if not player:
            return
        if player["level"] < 30:
            await message.channel.send(f"👑 Você precisa ser **nível 30** para assumir um trono!\nNível atual: **{player['level']}**")
            return
        if player.get("job") == "Rei":
            await message.channel.send("👑 Você **já é** Rei! Governe com sabedoria.")
            return
        embed = discord.Embed(
            title="👑 PROCLAMAÇÃO REAL",
            description=f"*{message.author.display_name} ergue a espada diante do povo reunido...*\n\n"
                        f"Tornar-se Rei significa:\n"
                        f"• Responsabilidade por **defender a cidade**\n"
                        f"• Receber **tributo diário** de coins\n"
                        f"• Poder **nomear cavaleiros** com `nomear cavaleiro @user`\n"
                        f"• Receber **alertas de invasão** em primeira mão\n\n"
                        f"⚠️ Requer: Nível 30+ e dedicação!",
            color=discord.Color.gold()
        )
        confirm_view = discord.ui.View(timeout=30)
        yes_btn = discord.ui.Button(label="👑 Assumir o Trono", style=discord.ButtonStyle.success)
        no_btn = discord.ui.Button(label="❌ Recusar", style=discord.ButtonStyle.secondary)

        async def yes_cb(interaction: discord.Interaction):
            if str(interaction.user.id) != uid:
                return await interaction.response.send_message("❌ Não é você!", ephemeral=True)
            p = get_player(uid)
            old_job = p.get("job")
            p["job"] = "Rei"
            p["city_title"] = "Rei"
            p["job_since"] = int(__import__("time").time())
            save_player_db(uid, p)
            crown_embed = discord.Embed(
                title="👑 LONGA VIDA AO REI!",
                description=f"*O povo ajoelha enquanto a coroa pousa na cabeça de **{interaction.user.display_name}**!*\n\n"
                            f"Que seu reino seja próspero e justo!",
                color=discord.Color.gold()
            )
            crown_embed.add_field(name="📜 Seus poderes", value="Use `trabalhar` | `defender cidade` | `nomear cavaleiro @user` | `ver emprego`", inline=False)
            for item in confirm_view.children:
                item.disabled = True
            await interaction.response.edit_message(embed=crown_embed, view=confirm_view)

        async def no_cb(interaction: discord.Interaction):
            if str(interaction.user.id) != uid:
                return
            for item in confirm_view.children:
                item.disabled = True
            await interaction.response.edit_message(content="*O trono aguarda outro dia.*", embed=None, view=confirm_view)

        yes_btn.callback = yes_cb
        no_btn.callback = no_cb
        confirm_view.add_item(yes_btn)
        confirm_view.add_item(no_btn)
        await message.channel.send(embed=embed, view=confirm_view)

    # ===== ENCONTRAR BOSS (boss variado por mundo) =====
    elif content in ["encontrar boss", "procurar boss", "buscar boss", "caçar boss", "boss do reino"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        if not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return
        world_key = max(k for k in player.get("worlds", [1]))
        boss_pool = WORLD_BOSSES_VARIANTS.get(world_key, WORLD_BOSSES_VARIANTS.get(1, []))
        boss = random.choice(boss_pool)
        world_info = MAP_LOCATIONS.get(world_key, {})
        world_name = world_info.get("world_name", "este reino")
        intro_msgs = [
            "🌑 O ar fica pesado de magia maligna...",
            "⚡ Um trovão ecoa sem nuvens no céu...",
            "💀 A temperatura cai dez graus de repente...",
            "👁️ Você sente que está sendo observado há minutos...",
            "🔥 O chão treme levemente sob seus pés...",
        ]
        embed = discord.Embed(
            title=f"⚠️ BOSS ENCONTRADO — {world_name}",
            description=f"*{random.choice(intro_msgs)}*\n\n{boss['intro']}",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="👹 Boss", value=f"**{boss['name']}**", inline=True)
        embed.add_field(name="❤️ HP", value=f"`{boss['hp']:,}`", inline=True)
        embed.add_field(name="⚔️ ATK", value=f"`{boss['atk']}`", inline=True)
        embed.add_field(name="⭐ XP", value=f"`{boss['xp']:,}`", inline=True)
        embed.add_field(name="💰 Coins", value=f"`{boss['coins'][0]}–{boss['coins'][1]}`", inline=True)
        embed.add_field(name="📖 Lore", value=f"_{boss['desc']}_", inline=False)
        embed.set_footer(text="Use os botões para lutar, chamar aliados ou fugir!")
        view = BossButton(uid, boss["name"])
        # Passar os dados do boss customizado para a batalha
        # Armazenar no player para a fight_boss poder pegar
        player2 = get_player(uid)
        effects = player2.get("active_effects", {})
        effects["pending_boss"] = boss
        player2["active_effects"] = effects
        save_player_db(uid, player2)
        await message.channel.send(embed=embed, view=view)


# ================= MODIFICAR MINERAR PARA INCLUIR MIMIC CHEST =================
# (Hook aplicado no on_message principal — ver abaixo)

@bot.listen("on_message")
async def handle_mining_mimic(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["minerar baú", "minerar bau", "abrir bau", "abrir baú", "bau secreto", "baú secreto"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        world_key = max(k for k in player.get("worlds", [1]))
        # Nível do baú baseado no nível do mundo
        tier_idx = min(len(MIMIC_TIERS) - 1, list(MAP_LOCATIONS.keys()).index(world_key) if world_key in MAP_LOCATIONS else 0)
        tier = MIMIC_TIERS[tier_idx]
        embed = discord.Embed(
            title=f"🔮 Baú Encontrado! — {tier['emoji']} {tier['name']}",
            description=(
                f"*Enquanto minerava, você encontrou um baú misterioso...*\n\n"
                f"**Chance de ser Mimic:** `{int(tier['mimic_chance']*100)}%`\n"
                f"**XP potencial:** `{tier['loot_xp'][0]}–{tier['loot_xp'][1]}`\n"
                f"**Coins potenciais:** `{tier['loot_coins'][0]}–{tier['loot_coins'][1]}`\n\n"
                f"⚠️ *Mimics podem te atacar e roubar XP! Você abre sabendo do risco?*"
            ),
            color=discord.Color.dark_gold()
        )
        view = MimicChestView(uid, tier_idx, world_key)
        await message.channel.send(embed=embed, view=view)


# ================= MODIFICAR EXPLORAR PARA DESCOBRIR LOCAIS =================
@bot.listen("on_message")
async def handle_map_discovery(message):
    """Ao explorar, há chance de descobrir novo local no mapa"""
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["explorar", "explorar região", "explorar regiao"]:
        # Este listener só faz a descoberta de local — o explorar principal continua normalmente
        await asyncio.sleep(0.5)  # leve delay para não conflitar
        player = get_player(uid)
        if not player:
            return
        if random.random() < 0.20:  # 20% de chance de descobrir algo
            world_key = max(k for k in player.get("worlds", [1]))
            world_locs = MAP_LOCATIONS.get(world_key, {}).get("locations", [])
            disc = player.get("discovered_map", {})
            key = str(world_key)
            known = disc.get(key, [])
            unknown = [l for l in world_locs if not l["discovered"] and l["id"] not in known]
            if unknown:
                new_loc = random.choice(unknown)
                discover_location(uid, world_key, new_loc["id"])
                type_icons = {
                    "cidade": "🏙️", "recurso": "⛏️", "dungeon": "🕳️", "dungeon_secreta": "🔮",
                    "boss_local": "💀", "lore": "📜", "loja": "🏪", "crafting": "⚒️",
                    "portal": "🌀", "evento_especial": "⭐", "npc_especial": "🧙"
                }
                icon = type_icons.get(new_loc["type"], "📍")
                await message.channel.send(
                    embed=discord.Embed(
                        title=f"🗺️ Novo Local Descoberto!",
                        description=f"{icon} **{new_loc['name']}** foi adicionado ao seu mapa!\nUse `abrir mapa` para ver.",
                        color=discord.Color.teal()
                    )
                )

# ================= MASMORRAS SECRETAS MAIS DIFÍCEIS =================
# A função explore_dungeon já existe — vamos sobrecarregar o XP e dificuldade

@bot.listen("on_message")
async def handle_npc_lore(message):
    """NPCs extras que contam lore"""
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["falar npc especial", "conversar npc especial", "npc lore", "falar lore npc"]:
        player = get_player(uid)
        if not player:
            return
        world_key = max(k for k in player.get("worlds", [1]))
        npc_pool = WORLD_NPCS_EXTRA.get(world_key, WORLD_NPCS_EXTRA.get(1, []))
        if not npc_pool:
            await message.channel.send("🤷 Nenhum NPC especial aqui.")
            return
        npc = random.choice(npc_pool)
        dialogue = random.choice(npc["dialogues"])
        embed = discord.Embed(
            title=f"{npc['emoji']} {npc['name']} — _{npc['role']}_",
            description=f'*"{dialogue}"*',
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Fale novamente para ouvir mais histórias deste NPC.")
        await message.channel.send(embed=embed)




# ================= RUN BOT =================
bot.run(TOKEN)
