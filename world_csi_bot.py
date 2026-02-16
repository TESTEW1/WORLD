import discord
from discord.ext import commands, tasks
import random
import os
import asyncio
import sqlite3
from datetime import datetime

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
ADMIN_ID = 769951556388257812  # Seu ID para notificações

# ================= BANCO DE DADOS =================

def init_db():
    """Inicializa banco de dados SQLite"""
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
        bosses TEXT DEFAULT '[]'
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
    
    conn.commit()
    conn.close()

def get_player_db(user_id):
    """Busca jogador no banco"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id = ?", (str(user_id),))
    result = c.fetchone()
    conn.close()
    
    if result:
        import json
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
            "bosses": json.loads(result[10])
        }
    return None

def save_player_db(user_id, player):
    """Salva jogador no banco"""
    import json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''INSERT OR REPLACE INTO players 
                 (user_id, level, xp, hp, max_hp, coins, inventory, weapon, armor, worlds, bosses)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (str(user_id), player["level"], player["xp"], player["hp"], player["max_hp"],
               player["coins"], json.dumps(player["inventory"]), player["weapon"], player["armor"],
               json.dumps(player["worlds"]), json.dumps(player["bosses"])))
    
    conn.commit()
    conn.close()

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

# ================= MUNDOS E EVENTOS =================
WORLDS = {
    1: {
        "name": "🌱 Campos Iniciais",
        "emoji": "🌱",
        "xp_loss_multiplier": 0.3,  # Perde menos XP
        "monsters": {
            "Slime": {"xp": (5, 10), "hp": 30, "atk": 5, "coins": (3, 8)},
            "Rato Selvagem": {"xp": (7, 12), "hp": 25, "atk": 7, "coins": (5, 10)},
            "Coelho Raivoso": {"xp": (6, 11), "hp": 20, "atk": 6, "coins": (4, 9)},
            "Javali Jovem": {"xp": (8, 13), "hp": 35, "atk": 8, "coins": (6, 12)},
            "Vespa Gigante": {"xp": (7, 11), "hp": 22, "atk": 7, "coins": (5, 10)}
        },
        "boss": {"name": "Slime Rei", "hp": 150, "atk": 15, "xp": 150, "level": 9, "coins": (50, 100)},
        "resources": ["Pedra fraca", "Grama mágica", "Couro de rato", "Flor silvestre", "Mel selvagem"],
        "dungeons": [
            {"name": "Caverna dos Slimes", "level": 1, "boss": "Slime Ancião"},
            {"name": "Toca dos Ratos", "level": 2, "boss": "Rato Rei"},
            {"name": "Ninho de Vespas", "level": 3, "boss": "Vespa Rainha"}
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
            "Goblin": {"xp": (15, 25), "hp": 60, "atk": 12, "coins": (15, 30)},
            "Lobo Negro": {"xp": (18, 30), "hp": 70, "atk": 15, "coins": (20, 35)},
            "Aranha Gigante": {"xp": (20, 28), "hp": 65, "atk": 14, "coins": (18, 32)},
            "Ogro Menor": {"xp": (22, 32), "hp": 80, "atk": 16, "coins": (25, 40)},
            "Espectro Florestal": {"xp": (19, 29), "hp": 55, "atk": 13, "coins": (17, 33)}
        },
        "boss": {"name": "Ent Ancião", "hp": 300, "atk": 25, "xp": 250, "level": 19, "coins": (100, 200)},
        "resources": ["Madeira escura", "Ervas raras", "Pele de lobo", "Teia mágica", "Musgo brilhante"],
        "dungeons": [
            {"name": "Covil dos Goblins", "level": 4, "boss": "Chefe Goblin"},
            {"name": "Ninho de Aranhas", "level": 5, "boss": "Aranha Rainha"},
            {"name": "Caverna do Ogro", "level": 6, "boss": "Ogro Cruel"}
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
            "Escorpião Gigante": {"xp": (25, 35), "hp": 100, "atk": 20, "coins": (35, 60)},
            "Múmia": {"xp": (30, 40), "hp": 120, "atk": 22, "coins": (40, 70)},
            "Serpente de Areia": {"xp": (28, 38), "hp": 110, "atk": 21, "coins": (38, 65)},
            "Guardião de Tumba": {"xp": (32, 42), "hp": 130, "atk": 24, "coins": (45, 75)},
            "Espírito do Deserto": {"xp": (29, 39), "hp": 105, "atk": 20, "coins": (37, 67)}
        },
        "boss": {"name": "Faraó Amaldiçoado", "hp": 500, "atk": 35, "xp": 400, "level": 29, "coins": (200, 350)},
        "resources": ["Areia mágica", "Ossos antigos", "Vendas místicas", "Escaravelho dourado", "Papiro antigo"],
        "dungeons": [
            {"name": "Pirâmide Perdida", "level": 7, "boss": "Faraó Esquecido"},
            {"name": "Tumba dos Reis", "level": 8, "boss": "Anúbis Menor"},
            {"name": "Templo Subterrâneo", "level": 9, "boss": "Esfinge Guardiã"}
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
            "Lobo de Gelo": {"xp": (35, 45), "hp": 150, "atk": 28, "coins": (60, 100)},
            "Golem de Neve": {"xp": (40, 50), "hp": 180, "atk": 30, "coins": (70, 110)},
            "Ogro Glacial": {"xp": (38, 48), "hp": 160, "atk": 29, "coins": (65, 105)},
            "Dragão de Gelo Jovem": {"xp": (45, 55), "hp": 200, "atk": 32, "coins": (80, 120)},
            "Elemental de Gelo": {"xp": (42, 52), "hp": 170, "atk": 31, "coins": (75, 115)}
        },
        "boss": {"name": "Yeti Colossal", "hp": 750, "atk": 45, "xp": 600, "level": 39, "coins": (350, 500)},
        "resources": ["Cristal de gelo", "Minério frio", "Pele de yeti", "Neve eterna", "Gema congelada"],
        "dungeons": [
            {"name": "Caverna Congelada", "level": 10, "boss": "Guardião do Gelo"},
            {"name": "Fortaleza de Gelo", "level": 11, "boss": "Rei do Inverno"},
            {"name": "Abismo Glacial", "level": 12, "boss": "Dragão Ancestral"}
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
            "Salamandra": {"xp": (45, 55), "hp": 200, "atk": 38, "coins": (100, 150)},
            "Demônio de Lava": {"xp": (50, 60), "hp": 230, "atk": 42, "coins": (120, 170)},
            "Elemental de Fogo": {"xp": (48, 58), "hp": 210, "atk": 40, "coins": (110, 160)},
            "Hidra de Magma": {"xp": (55, 65), "hp": 250, "atk": 45, "coins": (130, 180)},
            "Fênix Negra": {"xp": (52, 62), "hp": 220, "atk": 43, "coins": (125, 175)}
        },
        "boss": {"name": "Dragão de Magma", "hp": 1000, "atk": 55, "xp": 800, "level": 49, "coins": (500, 700)},
        "resources": ["Pedra vulcânica", "Núcleo de fogo", "Escamas de dragão", "Obsidiana pura", "Cinza sagrada"],
        "dungeons": [
            {"name": "Caldeirão de Lava", "level": 13, "boss": "Senhor do Fogo"},
            {"name": "Forja Infernal", "level": 14, "boss": "Titã Flamejante"},
            {"name": "Coração do Vulcão", "level": 15, "boss": "Ifrit Primordial"}
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
            "Espectro": {"xp": (55, 70), "hp": 280, "atk": 48, "coins": (150, 220)},
            "Mago Sombrio": {"xp": (60, 75), "hp": 300, "atk": 52, "coins": (170, 240)},
            "Devorador de Almas": {"xp": (58, 73), "hp": 290, "atk": 50, "coins": (160, 230)},
            "Lich": {"xp": (65, 80), "hp": 320, "atk": 55, "coins": (180, 250)},
            "Golem Arcano": {"xp": (62, 77), "hp": 310, "atk": 53, "coins": (175, 245)}
        },
        "boss": {"name": "Senhor das Sombras", "hp": 1500, "atk": 70, "xp": 1200, "level": 59, "coins": (700, 1000)},
        "resources": ["Essência arcana", "Fragmento sombrio", "Cristal do vazio", "Poeira estelar", "Runa mística"],
        "dungeons": [
            {"name": "Torre Arcana", "level": 16, "boss": "Arquimago Corrupto"},
            {"name": "Dimensão Sombria", "level": 17, "boss": "Entidade do Vazio"},
            {"name": "Biblioteca Proibida", "level": 18, "boss": "Guardião do Conhecimento"}
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
            "Guardião Celestial": {"xp": (80, 100), "hp": 400, "atk": 65, "coins": (250, 350)},
            "Anjo Caído": {"xp": (85, 105), "hp": 420, "atk": 68, "coins": (270, 370)},
            "Serafim Corrompido": {"xp": (90, 110), "hp": 450, "atk": 70, "coins": (290, 390)},
            "Querubim Guerreiro": {"xp": (95, 115), "hp": 480, "atk": 73, "coins": (310, 410)},
            "Arcanjo Negro": {"xp": (100, 120), "hp": 500, "atk": 75, "coins": (330, 430)}
        },
        "boss": {"name": "Imperador Astral", "hp": 2500, "atk": 100, "xp": 2000, "level": 60, "coins": (1000, 1500)},
        "resources": ["Essência celestial", "Fragmento estelar", "Coroa divina", "Lágrima de deus", "Pluma sagrada"],
        "dungeons": [
            {"name": "Santuário Celestial", "level": 19, "boss": "Avatar Divino"},
            {"name": "Palácio Estelar", "level": 20, "boss": "Deus Menor"},
            {"name": "Portal da Eternidade", "level": 21, "boss": "Guardião Final"}
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

# ================= ITENS EXPANDIDOS =================
RARITIES = {
    "Comum": {"color": 0xFFFFFF, "emoji": "⚪"},
    "Incomum": {"color": 0x00FF00, "emoji": "🟢"},
    "Raro": {"color": 0x0000FF, "emoji": "🔵"},
    "Épico": {"color": 0x800080, "emoji": "🟣"},
    "Lendário": {"color": 0xFFD700, "emoji": "🟡"},
    "Mítico": {"color": 0xFF0000, "emoji": "🔴"}
}

ITEMS = {
    "weapons": [
        # Comum
        {"name": "Espada Enferrujada", "rarity": "Comum", "atk": 5},
        {"name": "Adaga de Pedra", "rarity": "Comum", "atk": 6},
        {"name": "Cajado de Madeira", "rarity": "Comum", "atk": 5},
        {"name": "Machado Quebrado", "rarity": "Comum", "atk": 6},
        {"name": "Lança de Bambu", "rarity": "Comum", "atk": 5},
        # Incomum
        {"name": "Espada de Ferro", "rarity": "Incomum", "atk": 12},
        {"name": "Machado de Batalha", "rarity": "Incomum", "atk": 14},
        {"name": "Arco Composto", "rarity": "Incomum", "atk": 13},
        {"name": "Martelo de Guerra", "rarity": "Incomum", "atk": 15},
        {"name": "Katana Básica", "rarity": "Incomum", "atk": 13},
        {"name": "Mangual de Ferro", "rarity": "Incomum", "atk": 14},
        # Raro
        {"name": "Espada de Madeira Negra", "rarity": "Raro", "atk": 25},
        {"name": "Lança Mística", "rarity": "Raro", "atk": 27},
        {"name": "Arco Élfico", "rarity": "Raro", "atk": 26},
        {"name": "Machado Rúnico", "rarity": "Raro", "atk": 28},
        {"name": "Cimitarra de Prata", "rarity": "Raro", "atk": 26},
        {"name": "Alabarda Encantada", "rarity": "Raro", "atk": 27},
        {"name": "Tridente de Aço", "rarity": "Raro", "atk": 25},
        # Épico
        {"name": "Lâmina Flamejante", "rarity": "Épico", "atk": 45},
        {"name": "Cajado Arcano", "rarity": "Épico", "atk": 48},
        {"name": "Espada do Vento", "rarity": "Épico", "atk": 46},
        {"name": "Machado Titânico", "rarity": "Épico", "atk": 50},
        {"name": "Arco das Estrelas", "rarity": "Épico", "atk": 47},
        {"name": "Lança do Dragão", "rarity": "Épico", "atk": 49},
        {"name": "Foice Sombria", "rarity": "Épico", "atk": 48},
        {"name": "Martelo do Trovão", "rarity": "Épico", "atk": 51},
        # Lendário
        {"name": "Excalibur", "rarity": "Lendário", "atk": 100},
        {"name": "Mjolnir", "rarity": "Lendário", "atk": 105},
        {"name": "Gungnir", "rarity": "Lendário", "atk": 103},
        {"name": "Kusanagi", "rarity": "Lendário", "atk": 102},
        {"name": "Durandal", "rarity": "Lendário", "atk": 104},
        # Mítico
        {"name": "Espada do Criador", "rarity": "Mítico", "atk": 200},
        {"name": "Cetro da Eternidade", "rarity": "Mítico", "atk": 210}
    ],
    "armor": [
        # Comum
        {"name": "Armadura de Couro", "rarity": "Comum", "def": 3},
        {"name": "Robes Simples", "rarity": "Comum", "def": 4},
        {"name": "Túnica de Linho", "rarity": "Comum", "def": 3},
        {"name": "Peitoral de Bronze", "rarity": "Comum", "def": 4},
        {"name": "Capa Rasgada", "rarity": "Comum", "def": 3},
        # Incomum
        {"name": "Armadura de Ferro", "rarity": "Incomum", "def": 8},
        {"name": "Cota de Malha", "rarity": "Incomum", "def": 10},
        {"name": "Armadura de Escamas", "rarity": "Incomum", "def": 9},
        {"name": "Robes Reforçados", "rarity": "Incomum", "def": 8},
        {"name": "Brigandina", "rarity": "Incomum", "def": 10},
        {"name": "Armadura de Couro Batido", "rarity": "Incomum", "def": 9},
        # Raro
        {"name": "Armadura Mística", "rarity": "Raro", "def": 18},
        {"name": "Armadura Élfica", "rarity": "Raro", "def": 20},
        {"name": "Placas de Aço", "rarity": "Raro", "def": 19},
        {"name": "Armadura Rúnica", "rarity": "Raro", "def": 21},
        {"name": "Cota Encantada", "rarity": "Raro", "def": 19},
        {"name": "Armadura de Mithril", "rarity": "Raro", "def": 20},
        {"name": "Vestes Arcanas", "rarity": "Raro", "def": 18},
        # Épico
        {"name": "Armadura Dracônica", "rarity": "Épico", "def": 35},
        {"name": "Armadura das Sombras", "rarity": "Épico", "def": 38},
        {"name": "Placas do Titã", "rarity": "Épico", "def": 37},
        {"name": "Armadura Flamejante", "rarity": "Épico", "def": 36},
        {"name": "Vestes Estelares", "rarity": "Épico", "def": 35},
        {"name": "Armadura do Vazio", "rarity": "Épico", "def": 39},
        {"name": "Couraça Angelical", "rarity": "Épico", "def": 38},
        {"name": "Armadura Demoníaca", "rarity": "Épico", "def": 40},
        # Lendário
        {"name": "Armadura Celestial", "rarity": "Lendário", "def": 80},
        {"name": "Égide Divina", "rarity": "Lendário", "def": 85},
        {"name": "Armadura de Odin", "rarity": "Lendário", "def": 83},
        {"name": "Placas de Adaman", "rarity": "Lendário", "def": 82},
        {"name": "Vestes do Arcano Supremo", "rarity": "Lendário", "def": 84},
        # Mítico
        {"name": "Armadura do Primeiro Deus", "rarity": "Mítico", "def": 180},
        {"name": "Vestes da Criação", "rarity": "Mítico", "def": 190}
    ]
}

# ================= ESTRUTURAS E EVENTOS ESPECIAIS =================
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

# ================= FUNÇÕES =================

def roll_dice():
    return random.randint(1, 10)

def get_luck(roll):
    return LUCK_SYSTEM.get(roll, LUCK_SYSTEM[5])

def calc_xp(level):
    return (level ** 2) * 25

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
        "bosses": []
    }
    save_player_db(user_id, player)
    return player

def get_player(user_id):
    player = get_player_db(user_id)
    if not player:
        player = create_player(user_id)
    return player

def add_xp(user_id, amount):
    player = get_player(user_id)
    player["xp"] += amount
    leveled = False
    
    while player["xp"] >= calc_xp(player["level"]):
        player["xp"] -= calc_xp(player["level"])
        player["level"] += 1
        player["max_hp"] += 10
        player["hp"] = player["max_hp"]
        leveled = True
        
        for wl in WORLDS.keys():
            if player["level"] >= wl and wl not in player["worlds"]:
                player["worlds"].append(wl)
    
    save_player_db(user_id, player)
    return leveled

def remove_xp(user_id, amount):
    player = get_player(user_id)
    world = get_world(player["level"])
    
    # Aplica multiplicador baseado no mundo
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

# ================= CLASSE PARA BOTÕES =================

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
            response = f"✅ **Equipado!**\n\n🔄 Você substituiu **{old_item}** por **{self.item_name}**!\n\n*O narrador observa: Seu poder aumenta...*"
        else:
            response = f"✅ **Equipado!**\n\n⚔️ Você equipou **{self.item_name}**!\n\n*O narrador observa: Você está mais forte agora.*"
        
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
            content=f"🎒 **Guardado!**\n\nVocê guarda **{self.item_name}** no inventário.\n\n*O narrador murmura: Pode ser útil depois...*",
            view=None
        )

class BossButton(discord.ui.View):
    def __init__(self, user_id, boss_name, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.boss_name = boss_name
        self.answered = False
    
    @discord.ui.button(label="Enfrentar", style=discord.ButtonStyle.red, emoji="⚔️")
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse não é seu boss!", ephemeral=True)
        
        if self.answered:
            return
        
        self.answered = True
        await interaction.response.edit_message(
            content=f"⚔️ **Você avança em direção ao {self.boss_name}!**\n\n*O narrador: A batalha épica começa...*",
            view=None
        )
        
        await asyncio.sleep(2)
        await fight_boss(interaction.channel, self.user_id)
    
    @discord.ui.button(label="Recuar", style=discord.ButtonStyle.gray, emoji="🏃")
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse não é seu boss!", ephemeral=True)
        
        if self.answered:
            return
        
        self.answered = True
        await interaction.response.edit_message(
            content=f"🏃 **Você recua estrategicamente.**\n\nO {self.boss_name} permanece aguardando...\n\n*O narrador: A prudência também é sabedoria.*",
            view=None
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
        
        # Executa a troca
        from_player = get_player(self.from_user)
        to_player = get_player(self.to_user)
        
        # Remove itens
        for item in self.from_items:
            if item in from_player["inventory"]:
                from_player["inventory"].remove(item)
        
        for item in self.to_items:
            if item in to_player["inventory"]:
                to_player["inventory"].remove(item)
        
        # Adiciona itens
        for item in self.to_items:
            from_player["inventory"].append(item)
        
        for item in self.from_items:
            to_player["inventory"].append(item)
        
        save_player_db(self.from_user, from_player)
        save_player_db(self.to_user, to_player)
        
        await interaction.response.edit_message(
            content=f"✅ **Troca Realizada!**\n\n*O narrador: Os itens mudam de mãos...*\n\n🔄 Troca concluída com sucesso!",
            view=None
        )
    
    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.red, emoji="❌")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.to_user):
            return await interaction.response.send_message("❌ Esta troca não é para você!", ephemeral=True)
        
        if self.answered:
            return
        
        self.answered = True
        await interaction.response.edit_message(
            content=f"❌ **Troca Recusada**\n\n*O narrador: Talvez em outra ocasião...*",
            view=None
        )

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
        await interaction.response.edit_message(
            content="🚪 **Você sai da loja.**\n\n*O narrador: Até a próxima, viajante...*",
            view=None
        )
    
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
        
        if item["type"] == "weapon" or item["type"] == "armor":
            player["inventory"].append(item["name"])
            save_player_db(interaction.user.id, player)
        elif item["type"] == "potion":
            player["hp"] = min(player["hp"] + 50, player["max_hp"])
            save_player_db(interaction.user.id, player)
        
        await interaction.response.send_message(
            f"✅ **Compra realizada!**\n\nVocê comprou **{item['name']}** por **{item['price']} CSI**!\n\n*O narrador: Uma boa escolha!*",
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
                label=dungeon["name"],
                style=discord.ButtonStyle.primary,
                emoji="🏛️",
                custom_id=f"dungeon_{i}"
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
                content=f"🏛️ **Você entra na {self.dungeons[index]['name']}!**\n\n*O narrador: Que a sorte esteja com você...*",
                view=None
            )
            await asyncio.sleep(2)
            await explore_dungeon(interaction.channel, self.user_id, self.dungeons[index], self.world)
        
        return callback

async def fight_boss(channel, user_id, is_dungeon=False, dungeon_boss=None):
    """Executa a batalha contra o boss"""
    player = get_player(user_id)
    
    if is_dungeon and dungeon_boss:
        boss_data = dungeon_boss
    else:
        boss_world_lvl = player["level"] - (player["level"] % 10) + 1
        boss_world = WORLDS.get(boss_world_lvl)
        
        if not boss_world:
            return
        
        boss_data = boss_world["boss"]
    
    roll = roll_dice()
    luck = get_luck(roll)
    
    embed = discord.Embed(
        title=f"👹 BATALHA ÉPICA",
        description=f"**Você vs {boss_data['name']}**\n\n*O narrador narra intensamente a batalha...*",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="🎲 Dado do Destino", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    if roll <= 4:
        result, xp_loss = remove_xp(user_id, random.randint(100, 200))
        
        narratives = [
            f"O {boss_data['name']} ergue sua arma com força descomunal!",
            f"Você tenta se defender, mas o golpe é devastador!",
            f"Seu corpo é arremessado longe pelo impacto!",
            f"Você cai de joelhos, sentindo sua força se esvair..."
        ]
        
        embed.add_field(
            name="💀 Derrota Devastadora",
            value="\n".join(narratives) + f"\n\n❌ **−{xp_loss} XP**\n\n*O narrador: Nem todo herói vence na primeira tentativa...*",
            inline=False
        )
        
        if result == "reset":
            embed.add_field(
                name="🌑 Fim da Jornada",
                value="*Sua visão escurece...*\n*Tudo que você conquistou se perde...*\n*Você desperta novamente nos Campos Iniciais.*\n\n**Sua história recomeça do início.**",
                inline=False
            )
            embed.color = discord.Color.black()
    
    elif roll <= 6:
        result, xp_loss = remove_xp(user_id, random.randint(50, 80))
        
        narratives = [
            f"Você e o {boss_data['name']} trocam golpes furiosos!",
            f"A batalha é intensa, mas você não consegue vencer!",
            f"Ferido e exausto, você precisa recuar!",
            f"O boss urra vitorioso enquanto você foge..."
        ]
        
        embed.add_field(
            name="😰 Empate Amargo",
            value="\n".join(narratives) + f"\n\n❌ **−{xp_loss} XP**\n\n*O narrador: Volte mais forte...*",
            inline=False
        )
        embed.color = discord.Color.orange()
    
    else:
        xp = boss_data["xp"] + (100 if roll >= 9 else 0)
        coins = random.randint(boss_data["coins"][0], boss_data["coins"][1])
        
        if not is_dungeon:
            player["bosses"].append(boss_data["name"])
        
        save_player_db(user_id, player)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)
        
        narratives = [
            f"Você esquiva do primeiro golpe do {boss_data['name']}!",
            f"Contra-ataca com precisão mortal!",
            f"A batalha é épica, mas sua determinação é maior!",
            f"Com um golpe final devastador, o boss cai derrotado!"
        ]
        
        embed.add_field(
            name="🏆 VITÓRIA GLORIOSA!",
            value="\n".join(narratives) + f"\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**\n\n*O narrador: Uma lenda nasce!*",
            inline=False
        )
        
        if not is_dungeon:
            boss_world_lvl = player["level"] - (player["level"] % 10) + 1
            next_world_lvl = boss_world_lvl + 10
            if next_world_lvl in WORLDS:
                player = get_player(user_id)
                if next_world_lvl not in player["worlds"]:
                    player["worlds"].append(next_world_lvl)
                    save_player_db(user_id, player)
                    next_world = WORLDS[next_world_lvl]
                    embed.add_field(
                        name="🗺️ Novo Mundo Revelado!",
                        value=f"*As névoas se dissipam...*\n\n{next_world['emoji']} **{next_world['name']}** foi desbloqueado!\n\n*O narrador: Novos desafios aguardam...*",
                        inline=False
                    )
        
        if roll >= 9:
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            legendary = [i for i in ITEMS[item_list] if i["rarity"] in ["Lendário", "Mítico"]]
            item = random.choice(legendary)
            
            embed.add_field(
                name="🌟 Drop Lendário!",
                value=f"Do corpo do {boss_data['name']} surge:\n\n{RARITIES[item['rarity']]['emoji']} **{item['name']}**\n\n*O narrador: Os deuses sorriem para você!*",
                inline=False
            )
            
            await channel.send(embed=embed)
            await asyncio.sleep(1)
            
            view = EquipButton(user_id, item["name"], item_type)
            await channel.send(
                f"⚔️ **{item['name']}** brilha em suas mãos!\n\n*O narrador pergunta: Deseja equipar?*",
                view=view
            )
            return
        
        if leveled:
            player = get_player(user_id)
            embed.add_field(
                name="🆙 Ascensão!",
                value=f"*Seu corpo pulsa com nova energia!*\n\n**Nível {player['level']}**\n\n*O narrador: Você evoluiu!*",
                inline=False
            )
        
        embed.color = discord.Color.gold()
    
    await channel.send(embed=embed)

async def explore_dungeon(channel, user_id, dungeon, world):
    """Explora uma dungeon"""
    player = get_player(user_id)
    roll = roll_dice()
    luck = get_luck(roll)
    
    embed = discord.Embed(
        title=f"🏛️ {dungeon['name']}",
        description=f"*O narrador descreve:*\n\n'A dungeon é escura e úmida... Você sente perigo em cada sombra.'",
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
            value=f"*O narrador grita:*\n\n'Uma armadilha antiga é ativada! Lâminas surgem de todas as direções!'\n\n❌ **−{xp_loss} XP**\n💔 **−{dmg} HP**",
            inline=False
        )
        embed.color = discord.Color.dark_red()
    
    elif roll <= 3:
        result, xp_loss = remove_xp(user_id, random.randint(50, 80))
        
        embed.add_field(
            name="☠️ Exploração Perigosa",
            value=f"*O narrador narra:*\n\n'Você se perde nos corredores sombrios... Horas se passam antes de encontrar a saída.'\n\n❌ **−{xp_loss} XP**",
            inline=False
        )
        embed.color = discord.Color.red()
    
    elif roll <= 5:
        resources = random.sample(world["resources"], min(2, len(world["resources"])))
        for r in resources:
            player["inventory"].append(r)
        save_player_db(user_id, player)
        
        items = "\n".join([f"• **{r}**" for r in resources])
        
        embed.add_field(
            name="📦 Recursos Encontrados",
            value=f"*O narrador anota:*\n\n'Você encontra alguns recursos úteis...'\n\n{items}",
            inline=False
        )
        embed.color = discord.Color.blue()
    
    elif roll <= 7:
        xp = random.randint(50, 100)
        coins = random.randint(30, 60)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)
        
        embed.add_field(
            name="💎 Tesouro Escondido!",
            value=f"*O narrador celebra:*\n\n'Você encontra um baú antigo cheio de riquezas!'\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**",
            inline=False
        )
        
        if leveled:
            player = get_player(user_id)
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.green()
    
    elif roll <= 9:
        item_type = random.choice(["weapon", "armor"])
        item_list = "weapons" if item_type == "weapon" else "armor"
        rarity = random.choices(["Raro", "Épico", "Lendário"], weights=[40, 40, 20])[0]
        items_filtered = [i for i in ITEMS[item_list] if i["rarity"] == rarity]
        item = random.choice(items_filtered) if items_filtered else random.choice(ITEMS[item_list])
        
        xp = random.randint(80, 150)
        coins = random.randint(50, 100)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)
        
        rarity_info = RARITIES[item["rarity"]]
        
        embed.add_field(
            name="✨ Equipamento Raro!",
            value=f"*O narrador exclama:*\n\n'Em uma sala secreta, você encontra um equipamento magnífico!'\n\n{rarity_info['emoji']} **{item['name']}**\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**",
            inline=False
        )
        
        if leveled:
            player = get_player(user_id)
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = rarity_info["color"]
        
        await channel.send(embed=embed)
        await asyncio.sleep(1)
        
        view = EquipButton(user_id, item["name"], item_type)
        await channel.send(
            f"✨ **{item['name']}** aguarda por você!\n\n*O narrador pergunta: Deseja equipar?*",
            view=view
        )
        return
    
    else:  # roll == 10
        embed.add_field(
            name="👹 O BOSS APARECE!",
            value=f"*O narrador grita com tensão:*\n\n'No fim da dungeon, uma presença maligna surge!\n\n**{dungeon['boss']}** bloqueia seu caminho!",
            inline=False
        )
        embed.color = discord.Color.dark_red()
        
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        
        boss_data = {
            "name": dungeon['boss'],
            "hp": 200 + (dungeon['level'] * 50),
            "atk": 20 + (dungeon['level'] * 3),
            "xp": 100 + (dungeon['level'] * 30),
            "coins": (50 + (dungeon['level'] * 10), 100 + (dungeon['level'] * 20))
        }
        
        await fight_boss(channel, user_id, is_dungeon=True, dungeon_boss=boss_data)
        return
    
    await channel.send(embed=embed)

# ================= SISTEMA DE EVENTOS ALEATÓRIOS =================

@tasks.loop(minutes=random.randint(10, 30))
async def random_world_events():
    """Envia eventos aleatórios no canal"""
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=CANAL_BETA)
        if not channel:
            continue
        
        event_type = random.choice(["structure", "narrator", "merchant"])
        
        if event_type == "structure":
            structure = random.choice(STRUCTURES)
            
            embed = discord.Embed(
                title=f"{structure['name']} Avistada!",
                description=f"*O narrador murmura:*\n\n'{structure['narrator']}'",
                color=discord.Color.purple()
            )
            embed.add_field(name="📍 Descrição", value=structure['description'], inline=False)
            embed.set_footer(text="Esta estrutura está disponível para exploração!")
            
            await channel.send(embed=embed)
        
        elif event_type == "narrator":
            warning = random.choice(NARRATOR_WARNINGS)
            
            # Pega um jogador aleatório do servidor
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
            
            # Arma aleatória
            weapon = random.choice([i for i in ITEMS["weapons"] if i["rarity"] in ["Incomum", "Raro", "Épico"]])
            weapon_price = {"Incomum": 100, "Raro": 300, "Épico": 600}[weapon["rarity"]]
            items_for_sale.append({"name": weapon["name"], "type": "weapon", "price": weapon_price})
            
            # Armadura aleatória
            armor = random.choice([i for i in ITEMS["armor"] if i["rarity"] in ["Incomum", "Raro", "Épico"]])
            armor_price = {"Incomum": 100, "Raro": 300, "Épico": 600}[armor["rarity"]]
            items_for_sale.append({"name": armor["name"], "type": "armor", "price": armor_price})
            
            # Poção
            items_for_sale.append({"name": "Poção de Cura (+50 HP)", "type": "potion", "price": 50})
            
            embed = discord.Embed(
                title="🏪 Mercador Errante Apareceu!",
                description="*O narrador anuncia:*\n\n'Um mercador misterioso surge do nada oferecendo seus produtos...'",
                color=discord.Color.gold()
            )
            
            for i, item in enumerate(items_for_sale, 1):
                embed.add_field(
                    name=f"Item {i}: {item['name']}",
                    value=f"💰 **Preço: {item['price']} CSI**",
                    inline=False
                )
            
            embed.set_footer(text="Use os botões abaixo para comprar! O mercador ficará por tempo limitado...")
            
            await channel.send(embed=embed, view=ShopButton(None, items_for_sale))

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

"Era uma vez, quando as estrelas ainda eram jovens e os dragões dominavam
os céus, sete reinos coexistiam em harmonia frágil..."

*Os **Campos Iniciais** guardam os primeiros passos de todo herói.*
*A **Floresta Sombria** sussurra segredos que nenhum mortal deveria saber.*
*O **Deserto das Almas** esconde civilizações que a areia engoliu.*
*As **Montanhas Geladas** ecoam com lamentos de guerreiros caídos.*

*E além, onde apenas os mais corajosos chegam...*

*O **Reino Vulcânico** ferve com a ira de deuses esquecidos.*
*O **Abismo Arcano** distorce a própria essência da realidade.*
*E no fim de tudo, o **Trono Celestial** aguarda aquele digno o suficiente.*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎲 *Os dados do destino aguardam seu comando...*
⚔️ *Criaturas despertas já sentem sua presença...*
👑 *O Imperador Astral observa de seu trono distante...*
💰 *Moedas CSI aguardam para serem conquistadas...*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 **Como jogar:**

Basta falar naturalmente! Exemplos:
- "explorar" ou "vou explorar" - Explorar o mundo
- "caçar" ou "vou caçar" - Caçar monstros
- "coletar" ou "pegar recursos" - Coletar recursos
- "achar dungeon" - Procurar dungeons para explorar
- "trocar [item] com @usuário" - Trocar itens
- "trocar coins csi" - Converter moedas CSI
- "ver meu perfil" - Ver seu status
- "ver inventário" - Ver seus itens

*O narrador acompanhará cada passo seu!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 *"E assim, uma nova história começa..."* 🌟

*O narrador aguarda ansiosamente suas primeiras palavras...*
"""
    
    await channel.send(prologue)

# ================= EVENTOS =================

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
    
    # ================= TROCAR ITEMS =================
    if "trocar" in content and "@" in message.content:
        # Parse da mensagem
        parts = message.content.split("com")
        if len(parts) != 2:
            return
        
        from_items_text = parts[0].replace("trocar", "").strip()
        to_user_mention = parts[1].strip()
        
        # Identifica usuário mencionado
        mentions = message.mentions
        if not mentions:
            await message.channel.send("❌ Você precisa mencionar um usuário válido!")
            return
        
        to_user = mentions[0]
        to_user_id = to_user.id
        
        if to_user_id == user_id:
            await message.channel.send("❌ Você não pode trocar com você mesmo!")
            return
        
        # Pede os itens que quer em troca
        await message.channel.send(f"{to_user.mention}, que item você oferece em troca de **{from_items_text}**?\n\n*Responda com: 'ofereço [nome do item]'*")
        
        def check(m):
            return m.author.id == to_user_id and "ofereço" in m.content.lower()
        
        try:
            response = await bot.wait_for('message', check=check, timeout=60.0)
            to_items_text = response.content.replace("ofereço", "").strip()
            
            # Cria a proposta de troca
            embed = discord.Embed(
                title="🔄 Proposta de Troca",
                description=f"*O narrador observa a negociação...*",
                color=discord.Color.blue()
            )
            embed.add_field(name=f"📤 {message.author.name} oferece", value=f"**{from_items_text}**", inline=True)
            embed.add_field(name=f"📥 {to_user.name} oferece", value=f"**{to_items_text}**", inline=True)
            embed.set_footer(text="A troca será realizada se ambos concordarem")
            
            view = TradeButton(user_id, to_user_id, [from_items_text], [to_items_text])
            await message.channel.send(embed=embed, view=view)
            
        except asyncio.TimeoutError:
            await message.channel.send("⏰ Tempo esgotado! A proposta de troca expirou.")
        
        return
    
    # ================= TROCAR COINS CSI =================
    elif "trocar" in content and ("coins csi" in content or "moedas csi" in content or "csi" in content):
        player = get_player(user_id)
        
        embed = discord.Embed(
            title="💱 Solicitação de Conversão",
            description=f"*O narrador anota seu pedido...*\n\n{message.author.mention} deseja converter suas moedas CSI.",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Moedas CSI Disponíveis", value=f"`{player['coins']}` CSI", inline=False)
        embed.set_footer(text="O administrador foi notificado!")
        
        await message.channel.send(embed=embed)
        
        # Envia DM para o admin
        try:
            admin = await bot.fetch_user(ADMIN_ID)
            dm_embed = discord.Embed(
                title="🔔 Nova Solicitação de Conversão",
                description=f"**Jogador:** {message.author.name} ({message.author.id})\n**Server:** {message.guild.name}",
                color=discord.Color.gold()
            )
            dm_embed.add_field(name="💰 Moedas CSI", value=f"`{player['coins']}` CSI", inline=False)
            dm_embed.add_field(name="📊 Status do Jogador", value=f"**Nível:** {player['level']}\n**XP:** {player['xp']}", inline=False)
            
            await admin.send(embed=dm_embed)
        except:
            print(f"Não foi possível enviar DM ao admin")
        
        return
    
    # ================= EXPLORAR =================
    if any(word in content for word in ["explorar", "vou explorar", "vou para", "andar", "caminhar"]):
        player = get_player(user_id)
        world = get_world(player["level"])
        roll = roll_dice()
        luck = get_luck(roll)
        
        event = random.choice(world["events"])
        
        embed = discord.Embed(
            title=f"{world['emoji']} {world['name']}",
            description=f"*O narrador conta:*\n\n{event}",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado do Destino", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
        
        if roll == 1:
            result, xp_loss = remove_xp(user_id, random.randint(30, 50))
            
            embed.add_field(
                name="💀 Desastre!",
                value=f"*O narrador narra dramaticamente:*\n\n'Seus passos tropeçam no destino cruel! O chão trai você, e a dor vem rápida!'\n\n❌ **−{xp_loss} XP**",
                inline=False
            )
            
            if result == "reset":
                embed.add_field(
                    name="🌑 Fim da Jornada",
                    value="*O narrador sussurra tristemente:*\n\n'Sua história encontra um fim abrupto... Mas todo fim é um novo começo.'\n\n**Você desperta nos Campos Iniciais novamente.**",
                    inline=False
                )
                embed.color = discord.Color.dark_red()
        
        elif roll == 2:
            result, xp_loss = remove_xp(user_id, random.randint(15, 30))
            embed.add_field(
                name="☠️ Infortúnio",
                value=f"*O narrador comenta:*\n\n'Nem sempre o caminho é gentil com os viajantes...'\n\n❌ **−{xp_loss} XP**",
                inline=False
            )
            embed.color = discord.Color.red()
        
        elif roll in [3, 4]:
            embed.add_field(
                name="😐 Nada de Especial",
                value="*O narrador boceja:*\n\n'Você continua sua jornada... sem nada digno de nota.'",
                inline=False
            )
            embed.color = discord.Color.light_grey()
        
        elif roll == 5:
            res = random.choice(world["resources"])
            player["inventory"].append(res)
            save_player_db(user_id, player)
            
            embed.add_field(
                name="😶 Descoberta Modesta",
                value=f"*O narrador anota:*\n\n'Você encontra algo que pode ser útil...'\n\n📦 **{res}**",
                inline=False
            )
        
        elif roll in [6, 7]:
            xp = random.randint(15, 30)
            res = random.choice(world["resources"])
            player["inventory"].append(res)
            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)
            
            embed.add_field(
                name="🙂 Boa Descoberta!",
                value=f"*O narrador sorri:*\n\n'A sorte parece estar ao seu lado hoje!'\n\n📦 **{res}**\n⭐ **+{xp} XP**",
                inline=False
            )
            
            if leveled:
                player = get_player(user_id)
                embed.add_field(
                    name="🆙 Evolução!",
                    value=f"*O narrador exclama:*\n\n'Seu poder cresce! Um novo capítulo se abre!'\n\n**Nível {player['level']}**",
                    inline=False
                )
                embed.color = discord.Color.gold()
            else:
                embed.color = discord.Color.green()
        
        elif roll == 8:
            xp = random.randint(30, 50)
            resources = random.sample(world["resources"], min(2, len(world["resources"])))
            for r in resources:
                player["inventory"].append(r)
            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)
            
            items = "\n".join([f"• **{r}**" for r in resources])
            
            embed.add_field(
                name="🍀 Tesouro Escondido!",
                value=f"*O narrador se anima:*\n\n'Seus olhos captam o que outros perderiam!'\n\n{items}\n⭐ **+{xp} XP**",
                inline=False
            )
            
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            
            embed.color = discord.Color.green()
        
        elif roll == 9:
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            rarity = random.choices(["Raro", "Épico", "Lendário"], weights=[50, 35, 15])[0]
            items_filtered = [i for i in ITEMS[item_list] if i["rarity"] == rarity]
            item = random.choice(items_filtered) if items_filtered else random.choice(ITEMS[item_list])
            
            xp = random.randint(40, 70)
            leveled = add_xp(user_id, xp)
            
            rarity_info = RARITIES[item["rarity"]]
            
            embed.add_field(
                name="✨ Descoberta Rara!",
                value=f"*O narrador grita animado:*\n\n'Seus olhos brilham ao ver algo extraordinário!'\n\n{rarity_info['emoji']} **{item['name']}**\n⭐ **+{xp} XP**",
                inline=False
            )
            
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            
            embed.color = rarity_info["color"]
            
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            
            view = EquipButton(user_id, item["name"], item_type)
            await message.channel.send(
                f"✨ **{item['name']}** aguarda em suas mãos!\n\n*O narrador pergunta: Deseja equipar?*",
                view=view
            )
            
            player = get_player(user_id)
            boss_lvls = [9, 19, 29, 39, 49, 59]
            if player["level"] in boss_lvls:
                await asyncio.sleep(2)
                boss_world_lvl = player["level"] - (player["level"] % 10) + 1
                boss_world = WORLDS.get(boss_world_lvl)
                
                if boss_world and boss_world["boss"]["name"] not in player["bosses"]:
                    boss_name = boss_world["boss"]["name"]
                    
                    boss_embed = discord.Embed(
                        title="⚠️ PRESENÇA AMEAÇADORA",
                        description=f"*O narrador sussurra com tensão:*\n\n'O ar fica pesado... Uma sombra colossal se ergue diante de você...'\n\n**{boss_name}** bloqueia seu caminho!",
                        color=discord.Color.dark_red()
                    )
                    boss_embed.add_field(
                        name="💀 O Desafio",
                        value=f"*O narrador questiona:*\n\n'Você ousa enfrentar {boss_name}?'",
                        inline=False
                    )
                    
                    view = BossButton(user_id, boss_name)
                    await message.channel.send(embed=boss_embed, view=view)
            
            return
        
        else:  # roll == 10
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            legendary = [i for i in ITEMS[item_list] if i["rarity"] in ["Lendário", "Mítico"]]
            item = random.choice(legendary)
            
            xp = random.randint(80, 150)
            leveled = add_xp(user_id, xp)
            
            embed.add_field(
                name="🌟 EVENTO LENDÁRIO!",
                value=f"*O narrador grita extasiado:*\n\n'OS DEUSES SORRIEM PARA VOCÊ! O mundo estremece com tamanha sorte!'\n\n{RARITIES[item['rarity']]['emoji']} **{item['name']}**\n⭐ **+{xp} XP**",
                inline=False
            )
            
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Ascensão!", value=f"**Nível {player['level']}**", inline=False)
            
            embed.color = discord.Color.gold()
            
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            
            view = EquipButton(user_id, item["name"], item_type)
            await message.channel.send(
                f"🌟 **{item['name']}** pulsa com poder divino!\n\n*O narrador pergunta reverentemente: Deseja equipar esta relíquia?*",
                view=view
            )
            
            player = get_player(user_id)
            boss_lvls = [9, 19, 29, 39, 49, 59]
            if player["level"] in boss_lvls:
                await asyncio.sleep(2)
                boss_world_lvl = player["level"] - (player["level"] % 10) + 1
                boss_world = WORLDS.get(boss_world_lvl)
                
                if boss_world and boss_world["boss"]["name"] not in player["bosses"]:
                    boss_name = boss_world["boss"]["name"]
                    
                    boss_embed = discord.Embed(
                        title="⚠️ PRESENÇA AMEAÇADORA",
                        description=f"*O narrador sussurra com tensão:*\n\n'Uma sombra colossal se ergue...'\n\n**{boss_name}** apareceu!",
                        color=discord.Color.dark_red()
                    )
                    
                    view = BossButton(user_id, boss_name)
                    await message.channel.send(embed=boss_embed, view=view)
            
            return
        
        await message.channel.send(embed=embed)
        
        player = get_player(user_id)
        boss_lvls = [9, 19, 29, 39, 49, 59]
        if player["level"] in boss_lvls:
            await asyncio.sleep(2)
            boss_world_lvl = player["level"] - (player["level"] % 10) + 1
            boss_world = WORLDS.get(boss_world_lvl)
            
            if boss_world and boss_world["boss"]["name"] not in player["bosses"]:
                boss_name = boss_world["boss"]["name"]
                
                boss_embed = discord.Embed(
                    title="⚠️ PRESENÇA AMEAÇADORA",
                    description=f"*O narrador sussurra com tensão:*\n\n'O ar fica pesado... Você não está sozinho...'\n\n**{boss_name}** emerge das sombras!",
                    color=discord.Color.dark_red()
                )
                boss_embed.add_field(
                    name="💀 O Desafio",
                    value=f"*O narrador questiona:*\n\n'Você tem coragem de enfrentar?'",
                    inline=False
                )
                
                view = BossButton(user_id, boss_name)
                await message.channel.send(embed=boss_embed, view=view)
        
        return
    
    # ================= CAÇAR =================
    elif any(word in content for word in ["caçar", "cacar", "lutar", "atacar", "vou caçar", "batalhar"]):
        player = get_player(user_id)
        world = get_world(player["level"])
        
        monster_name = random.choice(list(world["monsters"].keys()))
        monster = world["monsters"][monster_name]
        
        roll = roll_dice()
        luck = get_luck(roll)
        
        embed = discord.Embed(
            title=f"⚔️ Encontro de Batalha",
            description=f"*O narrador anuncia dramaticamente:*\n\n'Um **{monster_name}** surge diante de você! Seus olhos brilham com fome de batalha!'",
            color=discord.Color.red()
        )
        embed.add_field(name="🎲 Dado da Batalha", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
        
        if roll <= 3:
            dmg = random.randint(10, 30)
            player["hp"] -= dmg
            
            if player["hp"] <= 0:
                player["hp"] = player["max_hp"] // 2
            
            save_player_db(user_id, player)
            result, xp_loss = remove_xp(user_id, random.randint(20, 40))
            
            narratives = [
                f"'O {monster_name} ataca primeiro!'",
                f"'Você tenta se defender, mas o golpe é certeiro!'",
                f"'Sangue escorre... A dor é intensa!'",
                f"'Você cai derrotado!'"
            ]
            
            embed.add_field(
                name="💀 Derrota Dolorosa",
                value=f"*O narrador narra:*\n\n" + "\n".join(narratives) + f"\n\n❌ **−{xp_loss} XP**\n💔 **−{dmg} HP**",
                inline=False
            )
            embed.color = discord.Color.dark_red()
        
        elif roll <= 5:
            xp = random.randint(monster["xp"][0], monster["xp"][0] + 5)
            coins = random.randint(monster["coins"][0], monster["coins"][0] + 5)
            dmg = random.randint(5, 15)
            player["hp"] -= dmg
            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)
            add_coins(user_id, coins)
            
            narratives = [
                f"'A batalha é feroz!'",
                f"'Vocês trocam golpes violentos!'",
                f"'Você leva um ferimento, mas persiste!'",
                f"'Com esforço, você prevalece!'"
            ]
            
            embed.add_field(
                name="😓 Vitória Suada",
                value=f"*O narrador descreve:*\n\n" + "\n".join(narratives) + f"\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**\n💔 **−{dmg} HP**",
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
            
            narratives = [
                f"'Você se move com agilidade!'",
                f"'Seus golpes são precisos!'",
                f"'O {monster_name} cai derrotado!'",
                f"'Vitória limpa!'"
            ]
            
            embed.add_field(
                name="⚔️ Vitória!",
                value=f"*O narrador celebra:*\n\n" + "\n".join(narratives) + f"\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**",
                inline=False
            )
            
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            
            embed.color = discord.Color.green()
        
        else:  # 8-10
            xp = random.randint(monster["xp"][1], monster["xp"][1] + 10)
            coins = random.randint(monster["coins"][1], monster["coins"][1] + 15)
            leveled = add_xp(user_id, xp)
            add_coins(user_id, coins)
            
            drop = None
            drop_item = None
            if roll >= 9:
                if roll == 10:
                    item_type = random.choice(["weapon", "armor"])
                    item_list = "weapons" if item_type == "weapon" else "armor"
                    rarity = random.choices(["Raro", "Épico"], weights=[60, 40])[0]
                    items_filtered = [i for i in ITEMS[item_list] if i["rarity"] == rarity]
                    drop_item = random.choice(items_filtered) if items_filtered else None
                else:
                    drop = random.choice(world["resources"])
                    player["inventory"].append(drop)
                    save_player_db(user_id, player)
            
            narratives = [
                f"'Você se move como um mestre da guerra!'",
                f"'Cada golpe seu é devastador!'",
                f"'O {monster_name} não tem chance!'",
                f"'Vitória absoluta!'"
            ]
            
            drop_text = ""
            if drop:
                drop_text = f"\n\n*O narrador nota:*\n'Do corpo, você extrai: **{drop}**'"
            elif drop_item:
                drop_text = f"\n\n*O narrador exclama:*\n'O monstro deixa cair: {RARITIES[drop_item['rarity']]['emoji']} **{drop_item['name']}**!'"
            
            embed.add_field(
                name="✨ Domínio Total!",
                value=f"*O narrador exalta:*\n\n" + "\n".join(narratives) + f"\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**{drop_text}",
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
                await message.channel.send(
                    f"⚔️ **{drop_item['name']}** está em suas mãos!\n\n*O narrador pergunta: Deseja equipar?*",
                    view=view
                )
            
            return
        
        await message.channel.send(embed=embed)
        return
    
    # ================= COLETAR =================
    elif any(word in content for word in ["coletar", "pegar recursos", "minerar", "vou coletar", "colher"]):
        player = get_player(user_id)
        world = get_world(player["level"])
        
        roll = roll_dice()
        luck = get_luck(roll)
        
        embed = discord.Embed(
            title=f"⛏️ Coleta de Recursos",
            description=f"*O narrador observa:*\n\n'Você procura cuidadosamente por recursos valiosos...'",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado da Sorte", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
        
        if roll <= 3:
            embed.add_field(
                name="😔 Busca Infrutífera",
                value="*O narrador comenta:*\n\n'Suas mãos voltam vazias... Nada de valor foi encontrado.'",
                inline=False
            )
            embed.color = discord.Color.light_grey()
        
        elif roll <= 6:
            res = random.choice(world["resources"])
            player["inventory"].append(res)
            save_player_db(user_id, player)
            
            embed.add_field(
                name="📦 Recurso Encontrado",
                value=f"*O narrador anota:*\n\n'Você encontra algo útil!'\n\n**{res}**",
                inline=False
            )
            embed.color = discord.Color.green()
        
        elif roll <= 8:
            resources = [random.choice(world["resources"]) for _ in range(2)]
            for r in resources:
                player["inventory"].append(r)
            save_player_db(user_id, player)
            
            items = "\n".join([f"• **{r}**" for r in resources])
            
            embed.add_field(
                name="🍀 Coleta Proveitosa!",
                value=f"*O narrador se surpreende:*\n\n'Seus olhos atentos encontram múltiplos recursos!'\n\n{items}",
                inline=False
            )
            embed.color = discord.Color.green()
        
        else:  # 9-10
            count = 3 if roll == 9 else 4
            resources = [random.choice(world["resources"]) for _ in range(count)]
            for r in resources:
                player["inventory"].append(r)
            save_player_db(user_id, player)
            
            items = "\n".join([f"• **{r}**" for r in resources])
            
            embed.add_field(
                name="✨ Coleta Abundante!",
                value=f"*O narrador exclama:*\n\n'Uma descoberta magnífica! Recursos por toda parte!'\n\n{items}",
                inline=False
            )
            embed.color = discord.Color.gold()
        
        await message.channel.send(embed=embed)
        return
    
    # ================= ACHAR DUNGEON =================
    elif any(word in content for word in ["achar dungeon", "procurar dungeon", "buscar dungeon", "encontrar dungeon", "dungeon"]):
        player = get_player(user_id)
        world = get_world(player["level"])
        
        if "dungeons" not in world or not world["dungeons"]:
            await message.channel.send(
                f"*O narrador informa:*\n\n'Não há dungeons conhecidas nesta região ainda... Explore mais!'"
            )
            return
        
        roll = roll_dice()
        luck = get_luck(roll)
        
        embed = discord.Embed(
            title="🔍 Procurando Dungeons...",
            description=f"*O narrador narra:*\n\n'Você procura por entradas secretas e ruínas antigas...'",
            color=discord.Color.purple()
        )
        embed.add_field(name="🎲 Dado da Busca", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
        
        if roll <= 3:
            embed.add_field(
                name="❌ Busca Fracassada",
                value="*O narrador lamenta:*\n\n'Você vaga por horas mas não encontra nenhuma entrada... Talvez na próxima.'",
                inline=False
            )
            embed.color = discord.Color.red()
            await message.channel.send(embed=embed)
            return
        
        dungeons = world["dungeons"]
        
        embed.add_field(
            name="🏛️ Dungeons Encontradas!",
            value=f"*O narrador se anima:*\n\n'Você descobre {len(dungeons)} dungeons escondidas nesta região!'",
            inline=False
        )
        
        for i, dungeon in enumerate(dungeons, 1):
            embed.add_field(
                name=f"{i}. {dungeon['name']} (Nível {dungeon['level']})",
                value=f"Boss: **{dungeon['boss']}**",
                inline=False
            )
        
        embed.color = discord.Color.gold()
        embed.set_footer(text="Escolha qual dungeon explorar usando os botões!")
        
        await message.channel.send(embed=embed)
        await asyncio.sleep(1)
        
        view = DungeonSelectButton(user_id, dungeons, world)
        await message.channel.send(
            "*O narrador pergunta:*\n\n'Qual dungeon você deseja explorar?'",
            view=view
        )
        return
    
    # ================= VER PERFIL =================
    elif any(word in content for word in ["ver perfil", "meu perfil", "perfil", "status", "ver status"]):
        player = get_player(user_id)
        world = get_world(player["level"])
        xp_need = calc_xp(player["level"])
        
        embed = discord.Embed(
            title=f"👤 {message.author.display_name}",
            description=f"*O narrador revela sua história até agora...*",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=message.author.display_avatar.url)
        
        embed.add_field(name="⭐ Nível", value=f"`{player['level']}`", inline=True)
        embed.add_field(name="✨ XP", value=f"`{player['xp']}/{xp_need}`", inline=True)
        embed.add_field(name="💰 Moedas CSI", value=f"`{player['coins']}`", inline=True)
        embed.add_field(name="❤️ HP", value=f"`{player['hp']}/{player['max_hp']}`", inline=True)
        
        embed.add_field(
            name="🌍 Localização Atual",
            value=f"{world['emoji']} **{world['name']}**",
            inline=False
        )
        
        weapon = player["weapon"] or "*Nenhuma*"
        armor = player["armor"] or "*Nenhuma*"
        embed.add_field(name="⚔️ Arma Equipada", value=weapon, inline=True)
        embed.add_field(name="🛡️ Armadura Equipada", value=armor, inline=True)
        
        bosses_defeated = len(player["bosses"])
        embed.add_field(name="👹 Bosses Derrotados", value=f"`{bosses_defeated}`", inline=True)
        
        await message.channel.send(embed=embed)
        return
    
    # ================= VER INVENTÁRIO =================
    elif any(word in content for word in ["ver inventario", "inventario", "mochila", "itens", "ver itens"]):
        player = get_player(user_id)
        
        embed = discord.Embed(
            title=f"🎒 Inventário",
            description=f"*O narrador vasculha sua mochila...*",
            color=discord.Color.gold()
        )
        
        if not player["inventory"]:
            embed.add_field(
                name="Vazio",
                value="*O narrador comenta:*\n\n'Suas bolsas estão vazias... Por enquanto.'",
                inline=False
            )
        else:
            items_count = {}
            for item in player["inventory"]:
                items_count[item] = items_count.get(item, 0) + 1
            
            text = "\n".join([f"• **{i}** x{c}" for i, c in items_count.items()])
            embed.add_field(name="📦 Seus Itens", value=text, inline=False)
        
        embed.set_footer(text=f"Total: {len(player['inventory'])} itens | Moedas CSI: {player['coins']}")
        await message.channel.send(embed=embed)
        return

# ================= RUN =================

bot.run(TOKEN)
