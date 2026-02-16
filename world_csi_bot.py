import discord
from discord.ext import commands
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
        inventory TEXT DEFAULT '[]',
        weapon TEXT DEFAULT NULL,
        armor TEXT DEFAULT NULL,
        worlds TEXT DEFAULT '[1]',
        bosses TEXT DEFAULT '[]'
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
            "inventory": json.loads(result[5]),
            "weapon": result[6],
            "armor": result[7],
            "worlds": json.loads(result[8]),
            "bosses": json.loads(result[9])
        }
    return None

def save_player_db(user_id, player):
    """Salva jogador no banco"""
    import json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''INSERT OR REPLACE INTO players 
                 (user_id, level, xp, hp, max_hp, inventory, weapon, armor, worlds, bosses)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (str(user_id), player["level"], player["xp"], player["hp"], player["max_hp"],
               json.dumps(player["inventory"]), player["weapon"], player["armor"],
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
        "monsters": {
            "Slime": {"xp": (5, 10), "hp": 30, "atk": 5},
            "Rato Selvagem": {"xp": (7, 12), "hp": 25, "atk": 7},
            "Coelho Raivoso": {"xp": (6, 11), "hp": 20, "atk": 6}
        },
        "boss": {"name": "Slime Rei", "hp": 150, "atk": 15, "xp": 150, "level": 9},
        "resources": ["Pedra fraca", "Grama mágica", "Couro de rato", "Flor silvestre"],
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
        "monsters": {
            "Goblin": {"xp": (15, 25), "hp": 60, "atk": 12},
            "Lobo Negro": {"xp": (18, 30), "hp": 70, "atk": 15},
            "Aranha Gigante": {"xp": (20, 28), "hp": 65, "atk": 14}
        },
        "boss": {"name": "Ent Ancião", "hp": 300, "atk": 25, "xp": 250, "level": 19},
        "resources": ["Madeira escura", "Ervas raras", "Pele de lobo", "Teia mágica"],
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
        "monsters": {
            "Escorpião Gigante": {"xp": (25, 35), "hp": 100, "atk": 20},
            "Múmia": {"xp": (30, 40), "hp": 120, "atk": 22},
            "Serpente de Areia": {"xp": (28, 38), "hp": 110, "atk": 21}
        },
        "boss": {"name": "Faraó Amaldiçoado", "hp": 500, "atk": 35, "xp": 400, "level": 29},
        "resources": ["Areia mágica", "Ossos antigos", "Vendas místicas", "Escaravelho dourado"],
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
        "monsters": {
            "Lobo de Gelo": {"xp": (35, 45), "hp": 150, "atk": 28},
            "Golem de Neve": {"xp": (40, 50), "hp": 180, "atk": 30},
            "Ogro Glacial": {"xp": (38, 48), "hp": 160, "atk": 29}
        },
        "boss": {"name": "Yeti Colossal", "hp": 750, "atk": 45, "xp": 600, "level": 39},
        "resources": ["Cristal de gelo", "Minério frio", "Pele de yeti", "Neve eterna"],
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
        "monsters": {
            "Salamandra": {"xp": (45, 55), "hp": 200, "atk": 38},
            "Demônio de Lava": {"xp": (50, 60), "hp": 230, "atk": 42},
            "Elemental de Fogo": {"xp": (48, 58), "hp": 210, "atk": 40}
        },
        "boss": {"name": "Dragão de Magma", "hp": 1000, "atk": 55, "xp": 800, "level": 49},
        "resources": ["Pedra vulcânica", "Núcleo de fogo", "Escamas de dragão", "Obsidiana pura"],
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
        "monsters": {
            "Espectro": {"xp": (55, 70), "hp": 280, "atk": 48},
            "Mago Sombrio": {"xp": (60, 75), "hp": 300, "atk": 52},
            "Devorador de Almas": {"xp": (58, 73), "hp": 290, "atk": 50}
        },
        "boss": {"name": "Senhor das Sombras", "hp": 1500, "atk": 70, "xp": 1200, "level": 59},
        "resources": ["Essência arcana", "Fragmento sombrio", "Cristal do vazio", "Poeira estelar"],
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
        "monsters": {
            "Guardião Celestial": {"xp": (80, 100), "hp": 400, "atk": 65},
            "Anjo Caído": {"xp": (85, 105), "hp": 420, "atk": 68},
            "Serafim Corrompido": {"xp": (90, 110), "hp": 450, "atk": 70}
        },
        "boss": {"name": "Imperador Astral", "hp": 2500, "atk": 100, "xp": 2000, "level": 60},
        "resources": ["Essência celestial", "Fragmento estelar", "Coroa divina", "Lágrima de deus"],
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

# ================= ITENS =================
RARITIES = {
    "Comum": {"color": 0xFFFFFF, "emoji": "⚪"},
    "Incomum": {"color": 0x00FF00, "emoji": "🟢"},
    "Raro": {"color": 0x0000FF, "emoji": "🔵"},
    "Épico": {"color": 0x800080, "emoji": "🟣"},
    "Lendário": {"color": 0xFFD700, "emoji": "🟡"}
}

ITEMS = {
    "weapons": [
        {"name": "Espada Enferrujada", "rarity": "Comum", "atk": 5},
        {"name": "Adaga de Pedra", "rarity": "Comum", "atk": 6},
        {"name": "Espada de Ferro", "rarity": "Incomum", "atk": 12},
        {"name": "Machado de Batalha", "rarity": "Incomum", "atk": 14},
        {"name": "Espada de Madeira Negra", "rarity": "Raro", "atk": 25},
        {"name": "Lança Mística", "rarity": "Raro", "atk": 27},
        {"name": "Lâmina Flamejante", "rarity": "Épico", "atk": 45},
        {"name": "Cajado Arcano", "rarity": "Épico", "atk": 48},
        {"name": "Excalibur", "rarity": "Lendário", "atk": 100},
        {"name": "Mjolnir", "rarity": "Lendário", "atk": 105}
    ],
    "armor": [
        {"name": "Armadura de Couro", "rarity": "Comum", "def": 3},
        {"name": "Robes Simples", "rarity": "Comum", "def": 4},
        {"name": "Armadura de Ferro", "rarity": "Incomum", "def": 8},
        {"name": "Cota de Malha", "rarity": "Incomum", "def": 10},
        {"name": "Armadura Mística", "rarity": "Raro", "def": 18},
        {"name": "Armadura Élfica", "rarity": "Raro", "def": 20},
        {"name": "Armadura Dracônica", "rarity": "Épico", "def": 35},
        {"name": "Armadura das Sombras", "rarity": "Épico", "def": 38},
        {"name": "Armadura Celestial", "rarity": "Lendário", "def": 80},
        {"name": "Égide Divina", "rarity": "Lendário", "def": 85}
    ]
}

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
    player["xp"] -= amount
    
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
        save_player_db(user_id, player)
        return "reset"
    
    save_player_db(user_id, player)
    return "ok"

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
        
        # Simula a batalha do boss
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

async def fight_boss(channel, user_id):
    """Executa a batalha contra o boss"""
    player = get_player(user_id)
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
        xp_loss = random.randint(100, 200)
        result = remove_xp(user_id, xp_loss)
        
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
        xp_loss = random.randint(50, 80)
        remove_xp(user_id, xp_loss)
        
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
        player["bosses"].append(boss_data["name"])
        save_player_db(user_id, player)
        leveled = add_xp(user_id, xp)
        
        narratives = [
            f"Você esquiva do primeiro golpe do {boss_data['name']}!",
            f"Contra-ataca com precisão mortal!",
            f"A batalha é épica, mas sua determinação é maior!",
            f"Com um golpe final devastador, o boss cai derrotado!"
        ]
        
        embed.add_field(
            name="🏆 VITÓRIA GLORIOSA!",
            value="\n".join(narratives) + f"\n\n⭐ **+{xp} XP**\n\n*O narrador: Uma lenda nasce!*",
            inline=False
        )
        
        # Desbloqueia mundo
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
        
        # Item lendário
        if roll >= 9:
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            legendary = [i for i in ITEMS[item_list] if i["rarity"] == "Lendário"]
            item = random.choice(legendary)
            
            embed.add_field(
                name="🌟 Drop Lendário!",
                value=f"Do corpo do {boss_data['name']} surge:\n\n🟡 **{item['name']}**\n\n*O narrador: Os deuses sorriem para você!*",
                inline=False
            )
            
            # Pergunta se quer equipar
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 **Como jogar:**

Basta falar naturalmente! Exemplos:
• "explorar" ou "vou explorar" - Explorar o mundo
• "caçar" ou "vou caçar" - Caçar monstros
• "coletar" ou "pegar recursos" - Coletar recursos
• "ver meu perfil" - Ver seu status
• "ver inventário" - Ver seus itens

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
    
    # ================= EXPLORAR =================
    if any(word in content for word in ["explorar", "vou explorar", "vou para", "andar", "caminhar"]):
        player = get_player(user_id)
        world = get_world(player["level"])
        roll = roll_dice()
        luck = get_luck(roll)
        
        # Evento aleatório
        event = random.choice(world["events"])
        
        embed = discord.Embed(
            title=f"{world['emoji']} {world['name']}",
            description=f"*O narrador conta:*\n\n{event}",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado do Destino", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
        
        # Eventos baseados no dado
        if roll == 1:
            xp_loss = random.randint(30, 50)
            result = remove_xp(user_id, xp_loss)
            
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
            xp_loss = random.randint(15, 30)
            remove_xp(user_id, xp_loss)
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
            
            # Botão para equipar
            view = EquipButton(user_id, item["name"], item_type)
            await message.channel.send(
                f"✨ **{item['name']}** aguarda em suas mãos!\n\n*O narrador pergunta: Deseja equipar?*",
                view=view
            )
            
            # Verifica boss
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
            legendary = [i for i in ITEMS[item_list] if i["rarity"] == "Lendário"]
            item = random.choice(legendary)
            
            xp = random.randint(80, 150)
            leveled = add_xp(user_id, xp)
            
            embed.add_field(
                name="🌟 EVENTO LENDÁRIO!",
                value=f"*O narrador grita extasiado:*\n\n'OS DEUSES SORRIEM PARA VOCÊ! O mundo estremece com tamanha sorte!'\n\n🟡 **{item['name']}**\n⭐ **+{xp} XP**",
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
            
            # Verifica boss
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
        
        # Verifica boss
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
            xp_loss = random.randint(20, 40)
            dmg = random.randint(10, 30)
            player["hp"] -= dmg
            
            if player["hp"] <= 0:
                player["hp"] = player["max_hp"] // 2
                xp_loss *= 2
            
            save_player_db(user_id, player)
            remove_xp(user_id, xp_loss)
            
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
            dmg = random.randint(5, 15)
            player["hp"] -= dmg
            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)
            
            narratives = [
                f"'A batalha é feroz!'",
                f"'Vocês trocam golpes violentos!'",
                f"'Você leva um ferimento, mas persiste!'",
                f"'Com esforço, você prevalece!'"
            ]
            
            embed.add_field(
                name="😓 Vitória Suada",
                value=f"*O narrador descreve:*\n\n" + "\n".join(narratives) + f"\n\n⭐ **+{xp} XP**\n💔 **−{dmg} HP**",
                inline=False
            )
            
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Crescimento!", value=f"**Nível {player['level']}**", inline=False)
            
            embed.color = discord.Color.orange()
        
        elif roll <= 7:
            xp = random.randint(monster["xp"][0], monster["xp"][1])
            leveled = add_xp(user_id, xp)
            
            narratives = [
                f"'Você se move com agilidade!'",
                f"'Seus golpes são precisos!'",
                f"'O {monster_name} cai derrotado!'",
                f"'Vitória limpa!'"
            ]
            
            embed.add_field(
                name="⚔️ Vitória!",
                value=f"*O narrador celebra:*\n\n" + "\n".join(narratives) + f"\n\n⭐ **+{xp} XP**",
                inline=False
            )
            
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            
            embed.color = discord.Color.green()
        
        else:  # 8-10
            xp = random.randint(monster["xp"][1], monster["xp"][1] + 10)
            leveled = add_xp(user_id, xp)
            
            drop = None
            if roll >= 9:
                drop = random.choice(world["resources"])
                player["inventory"].append(drop)
                save_player_db(user_id, player)
            
            narratives = [
                f"'Você se move como um mestre da guerra!'",
                f"'Cada golpe seu é devastador!'",
                f"'O {monster_name} não tem chance!'",
                f"'Vitória absoluta!'"
            ]
            
            drop_text = f"\n\n*O narrador nota:*\n'Do corpo, você extrai: **{drop}**'" if drop else ""
            
            embed.add_field(
                name="✨ Domínio Total!",
                value=f"*O narrador exalta:*\n\n" + "\n".join(narratives) + f"\n\n⭐ **+{xp} XP**{drop_text}",
                inline=False
            )
            
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Evolução!", value=f"**Nível {player['level']}**", inline=False)
            
            embed.color = discord.Color.gold()
        
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
        
        embed.set_footer(text=f"Total: {len(player['inventory'])} itens")
        await message.channel.send(embed=embed)
        return

# ================= RUN =================

bot.run(TOKEN)
