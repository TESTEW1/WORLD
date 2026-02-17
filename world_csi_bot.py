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
CANAL_BETA = "mundo-beta"
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
        "description": "Músico encantador, bônus de XP e sorte aumentada."
    }
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
        completed_quests TEXT DEFAULT '[]'
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
            "completed_quests": json.loads(result[16]) if result[16] else []
        }
    return None

def save_player_db(user_id, player):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''INSERT OR REPLACE INTO players
                 (user_id, level, xp, hp, max_hp, coins, inventory, weapon, armor,
                  worlds, bosses, class, pet, guild_id, active_effects, active_quest, completed_quests)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (str(user_id), player["level"], player["xp"], player["hp"], player["max_hp"],
               player["coins"], json.dumps(player["inventory"]), player["weapon"], player["armor"],
               json.dumps(player["worlds"]), json.dumps(player["bosses"]), player.get("class"),
               player.get("pet"), player.get("guild_id"),
               json.dumps(player.get("active_effects", {})),
               json.dumps(player.get("active_quest")) if player.get("active_quest") else None,
               json.dumps(player.get("completed_quests", []))))

    conn.commit()
    conn.close()

# ================= FUNÇÕES BASE =================

def roll_dice():
    return random.randint(1, 10)

def get_luck(roll):
    return LUCK_SYSTEM.get(roll, LUCK_SYSTEM[5])

def calc_xp(level):
    return (level ** 2) * 20

def get_world(level):
    levels = sorted([k for k in WORLDS.keys() if k <= level], reverse=True)
    return WORLDS[levels[0]] if levels else WORLDS[1]

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
        "completed_quests": []
    }
    save_player_db(user_id, player)
    return player

def get_player(user_id):
    player = get_player_db(user_id)
    if not player:
        player = create_player(user_id)
    return player

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
        leveled = True

        for wl in WORLDS.keys():
            if player["level"] >= wl and wl not in player["worlds"]:
                player["worlds"].append(wl)

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
    world = get_world(player["level"])

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


# ================= FUNÇÕES DE BATALHA E EXPLORAÇÃO =================

async def fight_boss(channel, user_id, is_dungeon=False, dungeon_boss=None, allies=None):
    player = get_player(user_id)

    if is_dungeon and dungeon_boss:
        boss_data = dungeon_boss
    else:
        boss_levels = {9: 1, 19: 10, 29: 20, 39: 30, 49: 40, 59: 50}
        world_key = boss_levels.get(player["level"])
        if world_key is None:
            # Usa boss do mundo atual
            world_level = max([k for k in WORLDS.keys() if k <= player["level"]])
            boss_data = WORLDS[world_level]["boss"]
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
        narratives = [
            f"O {boss_data['name']} ergue sua arma com força descomunal!",
            "Você tenta se defender, mas o golpe é devastador!",
            "Seu corpo é arremessado longe pelo impacto!",
            "Você cai de joelhos, sentindo sua força se esvair..."
        ]
        embed.add_field(
            name="💀 Derrota Devastadora",
            value="\n".join(narratives) + f"\n\n❌ **−{xp_loss} XP**\n\n*'Nem todo herói vence na primeira tentativa...'*",
            inline=False
        )
        if result == "reset":
            embed.add_field(
                name="🌑 Fim da Jornada",
                value="*'Sua visão escurece... tudo que você conquistou se perde...'*\n\n**Você desperta novamente nos Campos Iniciais.**",
                inline=False
            )
            embed.color = discord.Color.black()

    elif roll <= 6:
        result, xp_loss = remove_xp(user_id, random.randint(50, 80))
        narratives = [
            f"Você e o {boss_data['name']} trocam golpes furiosos!",
            "A batalha é intensa, mas você não consegue vencer!",
            "Ferido e exausto, você precisa recuar!",
            "O boss urra vitorioso enquanto você foge..."
        ]
        embed.add_field(
            name="😰 Empate Amargo",
            value="\n".join(narratives) + f"\n\n❌ **−{xp_loss} XP**\n\n*'Volte mais forte...'*",
            inline=False
        )
        embed.color = discord.Color.orange()

    else:
        xp = boss_data["xp"] + (150 if roll >= 9 else 0)
        coins = random.randint(boss_data["coins"][0], boss_data["coins"][1])

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

        narratives = [
            f"Você esquiva do primeiro golpe do {boss_data['name']}!",
            "Contra-ataca com precisão mortal!",
            "A batalha é épica, mas sua determinação é maior!",
            "Com um golpe final devastador, o boss cai derrotado!"
        ]

        embed.add_field(
            name="🏆 VITÓRIA GLORIOSA!",
            value="\n".join(narratives) + f"\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**\n\n*'Uma lenda nasce!'*",
            inline=False
        )

        # Desbloqueia próximo mundo
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
                    value=f"*'As névoas se dissipam...'*\n\n{WORLDS[next_world]['emoji']} **{WORLDS[next_world]['name']}** foi desbloqueado!\n\n*'Novos desafios aguardam...'*",
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
    roll = roll_dice()
    luck = get_luck(roll)
    is_secret = dungeon.get("secret", False)

    embed = discord.Embed(
        title=f"{'🔮' if is_secret else '🏛️'} {dungeon['name']}",
        description=f"*'A dungeon{'secreta ' if is_secret else ''}é escura e úmida... Você sente perigo em cada sombra.'*",
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="🎲 Dado da Exploração", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

    if roll == 1:
        dmg = random.randint(30, 50)
        player["hp"] -= dmg
        if player["hp"] <= 0:
            player["hp"] = player["max_hp"] // 2
        save_player_db(user_id, player)
        result, xp_loss = remove_xp(user_id, random.randint(100, 150))

        embed.add_field(
            name="💀 ARMADILHA MORTAL!",
            value=f"*'Uma armadilha antiga é ativada! Lâminas surgem de todas as direções!'*\n\n❌ **−{xp_loss} XP**\n💔 **−{dmg} HP**",
            inline=False
        )
        embed.color = discord.Color.dark_red()

    elif roll <= 3:
        result, xp_loss = remove_xp(user_id, random.randint(50, 80))
        embed.add_field(
            name="☠️ Exploração Perigosa",
            value=f"*'Você se perde nos corredores sombrios...'*\n\n❌ **−{xp_loss} XP**",
            inline=False
        )
        embed.color = discord.Color.red()

    elif roll <= 5:
        resources = random.sample(world["resources"], min(2, len(world["resources"])))
        for r in resources:
            player["inventory"].append(r)
        save_player_db(user_id, player)
        items_text = "\n".join([f"• **{r}**" for r in resources])
        embed.add_field(
            name="📦 Recursos Encontrados",
            value=f"*'Você encontra alguns recursos úteis...'*\n\n{items_text}", inline=False
        )
        embed.color = discord.Color.blue()

    elif roll <= 7:
        xp = random.randint(80, 150)
        coins = random.randint(10, 25)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)

        if random.random() < 0.25:
            potion_list = list(POTIONS.keys())
            dropped_potion = random.choice(potion_list)
            player = get_player(user_id)
            player["inventory"].append(dropped_potion)
            save_player_db(user_id, player)

        embed.add_field(
            name="💎 Tesouro Escondido!",
            value=f"*'Você encontra um baú antigo cheio de riquezas!'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**",
            inline=False
        )
        if leveled:
            player = get_player(user_id)
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        embed.color = discord.Color.green()

    elif roll <= 9:
        # Item drop
        item_type = random.choice(["weapon", "armor"])
        item_list = "weapons" if item_type == "weapon" else "armor"
        rarity_pool = ["Épico", "Lendário", "Mítico"] if is_secret else ["Raro", "Épico", "Lendário"]
        weights = [25, 50, 25] if is_secret else [40, 40, 20]
        rarity = random.choices(rarity_pool, weights=weights)[0]
        items_filtered = [i for i in ITEMS[item_list] if i["rarity"] == rarity]
        item = random.choice(items_filtered) if items_filtered else random.choice(ITEMS[item_list])

        xp = random.randint(120, 200)
        coins = random.randint(15, 35)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)

        rarity_info = RARITIES[item["rarity"]]
        embed.add_field(
            name="✨ Equipamento Raro!",
            value=f"*'Em uma sala secreta, você encontra um equipamento magnífico!'*\n\n{rarity_info['emoji']} **{item['name']}**\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**",
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
        embed.add_field(
            name="👹 O BOSS APARECE!",
            value=f"*'No fim da dungeon, uma presença maligna surge!\n\n**{dungeon['boss']}** bloqueia seu caminho!'*",
            inline=False
        )
        embed.color = discord.Color.dark_red()
        await channel.send(embed=embed)
        await asyncio.sleep(2)

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

    prologue = """
╔═══════════════════════════════════════════════════════════════╗
║                    🌍 **WORLD CSI** 🌍                        ║
║            *O Narrador Desperta Para Contar Sua História*    ║
╚═══════════════════════════════════════════════════════════════╝

*O narrador limpa a garganta e começa...*

"Era uma vez, quando as estrelas ainda eram jovens e os dragões dominavam os céus, sete reinos coexistiam em harmonia frágil..."

🌱 **Campos Iniciais** — O berço de todo herói
🌲 **Floresta Sombria** — Sussurra segredos proibidos
🏜️ **Deserto das Almas** — Guarda civilizações engolidas pela areia
❄️ **Montanhas Geladas** — Ecoam lamentos de guerreiros caídos
🌋 **Reino Vulcânico** — Ferve com a ira de deuses esquecidos
🌌 **Abismo Arcano** — Distorce a própria essência da realidade
👑 **Trono Celestial** — Aguarda aquele digno o suficiente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 **Comandos Principais:**

**EXPLORAÇÃO:** `explorar` | `caçar` | `coletar` | `dungeon` | `procurar pet` | `explorar cidade`
**BOSS:** `desafiar boss` | `ir atrás do boss` | `juntar boss` | `iniciar batalha boss`
**QUESTS:** `ver quests` | `minha quest` | `abandonar quest`
**PERSONAGEM:** `ver perfil` | `inventário` | `escolher classe`
**SOCIAL:** `trocar [item] com @user` | `criar guilda` | `entrar guilda` | `ver guilda`
**ITENS:** `[poção], usar` | `vender [item]` | `equipar [item]`

*O narrador acompanhará cada passo seu!* 🎭

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 *"E assim, uma nova história começa..."* 🌟
"""
    await channel.send(prologue)


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

        world = get_world(player["level"])
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
    # ================= VER QUESTS =========================
    # ======================================================
    elif any(word in content for word in ["ver quests", "quests disponíveis", "quests", "missões"]):
        player = get_player(user_id)
        world_level = max([k for k in QUESTS.keys() if k <= player["level"]])
        available_quests = QUESTS.get(world_level, [])

        embed = discord.Embed(
            title=f"📜 Quests Disponíveis",
            description=f"*Quests do reino atual | Completadas: {len(player.get('completed_quests', []))}*",
            color=discord.Color.gold()
        )

        for quest in available_quests:
            completed = quest["id"] in player.get("completed_quests", [])
            active = player.get("active_quest") and player["active_quest"].get("id") == quest["id"]
            status = "✅ Completa" if completed else ("🔄 Ativa" if active else f"📋 {quest['difficulty']}")
            q_type = "👥 Equipe" if quest["type"] == "team" else "👤 Individual"
            embed.add_field(
                name=f"{quest['name']} [{q_type}] — {status}",
                value=f"{quest['description'][:100]}...\n**NPC:** {quest['npc']} | **XP:** {quest['reward_xp']} | **CSI:** {quest['reward_coins']}",
                inline=False
            )

        embed.set_footer(text="Use 'aceitar quest [nome]' para iniciar uma missão!")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= ACEITAR QUEST ======================
    # ======================================================
    elif content.startswith("aceitar quest"):
        quest_name_search = content.replace("aceitar quest", "").strip()
        player = get_player(user_id)
        world_level = max([k for k in QUESTS.keys() if k <= player["level"]])
        available_quests = QUESTS.get(world_level, [])

        found_quest = None
        for quest in available_quests:
            if quest_name_search in quest["name"].lower() or quest_name_search in quest["id"]:
                found_quest = quest
                break

        if not found_quest and available_quests:
            found_quest = available_quests[0]

        if not found_quest:
            await message.channel.send("❌ Quest não encontrada! Use `ver quests` para listar as disponíveis.")
            return

        embed = discord.Embed(
            title=f"📜 {found_quest['name']}",
            description=f"**NPC: {found_quest['npc']}** diz:\n\n*'{found_quest['lore']}'*",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎯 Objetivo", value=found_quest["description"], inline=False)
        embed.add_field(name="⭐ Recompensa XP", value=str(found_quest["reward_xp"]), inline=True)
        embed.add_field(name="💰 Recompensa CSI", value=str(found_quest["reward_coins"]), inline=True)
        if found_quest.get("reward_item"):
            embed.add_field(name="🎁 Item", value=found_quest["reward_item"], inline=True)
        quest_type_text = f"👥 Equipe ({found_quest.get('min_players', 1)}-{found_quest.get('max_players', 1)} jogadores)" if found_quest["type"] == "team" else "👤 Individual"
        embed.add_field(name="📋 Tipo", value=quest_type_text, inline=True)
        embed.add_field(name="⚡ Dificuldade", value=found_quest["difficulty"], inline=True)

        view = QuestAcceptButton(user_id, found_quest)
        await message.channel.send(embed=embed, view=view)
        return

    # ======================================================
    # ================= MINHA QUEST ========================
    # ======================================================
    elif any(word in content for word in ["minha quest", "quest ativa", "ver quest"]):
        player = get_player(user_id)

        if not player.get("active_quest"):
            await message.channel.send("❌ Você não tem uma quest ativa! Use `ver quests` para ver as disponíveis.")
            return

        quest = player["active_quest"]
        embed = discord.Embed(
            title=f"📜 Quest Ativa: {quest['name']}",
            description=quest["description"],
            color=discord.Color.gold()
        )
        progress = quest.get("progress", 0)
        total = quest.get("count", 1)
        embed.add_field(name="📊 Progresso", value=f"{progress}/{total}", inline=True)
        embed.add_field(name="⭐ Recompensa XP", value=str(quest["reward_xp"]), inline=True)
        embed.add_field(name="💰 Recompensa CSI", value=str(quest["reward_coins"]), inline=True)
        embed.add_field(name="📖 Lore do NPC", value=f"*'{quest['lore']}'*", inline=False)

        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= ABANDONAR QUEST ===================
    # ======================================================
    elif any(word in content for word in ["abandonar quest", "cancelar quest", "desistir quest"]):
        player = get_player(user_id)

        if not player.get("active_quest"):
            await message.channel.send("❌ Você não tem uma quest ativa!")
            return

        quest_name = player["active_quest"]["name"]
        player["active_quest"] = None
        save_player_db(user_id, player)
        await message.channel.send(f"❌ Você abandonou a quest **{quest_name}**.\n\n*'O NPC suspira desapontado...'*")
        return

    # ======================================================
    # ================= EXPLORAR CIDADE ====================
    # ======================================================
    elif any(word in content for word in ["explorar cidade", "visitar cidade", "cidade", "vila"]):
        player = get_player(user_id)
        world_level = max([k for k in CITY_NPCS.keys() if k <= player["level"]])
        city_data = CITY_NPCS.get(world_level, CITY_NPCS[1])

        embed = discord.Embed(
            title=f"{city_data['city_name']}",
            description=f"*'Você adentra a cidade. O burburinho ao redor conta histórias de suas próprias...'*",
            color=discord.Color.blue()
        )

        for npc in city_data["npcs"]:
            dialogue = random.choice(npc["dialogues"])
            embed.add_field(
                name=f"{npc['emoji']} {npc['name']} — {npc['role']}",
                value=f"*\"{dialogue}\"*",
                inline=False
            )

        # Chance de encontrar livro de lore
        if random.random() < 0.3:
            lore_world = max([k for k in LORE_BOOKS.keys() if k <= player["level"]])
            book = random.choice(LORE_BOOKS[lore_world])
            embed.add_field(
                name=f"📚 Você encontra: {book['title']}",
                value=book["content"][:512] + ("..." if len(book["content"]) > 512 else ""),
                inline=False
            )

        # Pequena recompensa por explorar
        coins_reward = random.randint(1, 5)
        add_coins(user_id, coins_reward)
        embed.set_footer(text=f"+{coins_reward} CSI por explorar a cidade")

        await message.channel.send(embed=embed)
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
            admin = await bot.fetch_user(ADMIN_ID)
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

        world = get_world(player["level"])
        roll = roll_dice()
        if player.get("class") == "Bardo":
            roll = min(10, roll + 1)
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

        world = get_world(player["level"])
        monster_name = random.choice(list(world["monsters"].keys()))
        monster = world["monsters"][monster_name]
        roll = roll_dice()
        if player.get("class") == "Bardo":
            roll = min(10, roll + 1)
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

        world = get_world(player["level"])
        roll = roll_dice()
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

        world = get_world(player["level"])
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
        world = get_world(player["level"])
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

    await bot.process_commands(message)


# ======================================================
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


# ================= RUN BOT =================
bot.run(TOKEN)
