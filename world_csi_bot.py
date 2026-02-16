import discord
from discord.ext import commands, tasks
import json
import random
import os
import asyncio
from datetime import datetime

# ================= INTENTS =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
DATA_FILE = "world_csi_data.json"
CANAL_BETA = "mundo-beta"

# ================= DADOS =================
game_data = {
    "players": {},
    "characters": {},
    "active_chars": {}
}

# ================= SISTEMA DE SORTE (1-10) =================
LUCK_SYSTEM = {
    1: {"emoji": "💀", "name": "Azar extremo", "desc": "Falha crítica"},
    2: {"emoji": "☠️", "name": "Muito azar", "desc": "Perde recursos"},
    3: {"emoji": "😵", "name": "Azar", "desc": "Resultado fraco"},
    4: {"emoji": "😐", "name": "Ruim", "desc": "Efeito mínimo"},
    5: {"emoji": "😶", "name": "Neutro", "desc": "Resultado básico"},
    6: {"emoji": "🙂", "name": "Bom", "desc": "Resultado positivo"},
    7: {"emoji": "😄", "name": "Sorte", "desc": "Ação melhorada"},
    8: {"emoji": "🍀", "name": "Muita sorte", "desc": "Recompensa extra"},
    9: {"emoji": "✨", "name": "Sorte extrema", "desc": "Drop raro"},
    10: {"emoji": "🌟", "name": "Lenda", "desc": "Evento épico"}
}

# ================= MUNDOS =================
WORLDS = {
    1: {
        "name": "🌱 Campos Iniciais",
        "emoji": "🌱",
        "monsters": {
            "Slime": {"xp": (5, 10), "hp": 30, "atk": 5},
            "Rato Selvagem": {"xp": (7, 12), "hp": 25, "atk": 7}
        },
        "boss": {"name": "Slime Rei", "hp": 150, "atk": 15, "xp": 150, "level": 9},
        "resources": ["Pedra fraca", "Grama mágica", "Couro de rato"],
        "texts": [
            "Você caminha entre campos floridos.",
            "O sol brilha suavemente sobre a grama.",
            "Uma brisa tranquila passa por você."
        ]
    },
    10: {
        "name": "🌲 Floresta Sombria",
        "emoji": "🌲",
        "monsters": {
            "Goblin": {"xp": (15, 25), "hp": 60, "atk": 12},
            "Lobo Negro": {"xp": (18, 30), "hp": 70, "atk": 15}
        },
        "boss": {"name": "Ent Ancião", "hp": 300, "atk": 25, "xp": 250, "level": 19},
        "resources": ["Madeira escura", "Ervas raras", "Pele de lobo"],
        "texts": [
            "Você caminha entre árvores antigas.",
            "O vento sussurra histórias esquecidas…",
            "Sombras dançam entre os galhos."
        ]
    },
    20: {
        "name": "🏜️ Deserto das Almas",
        "emoji": "🏜️",
        "monsters": {
            "Escorpião Gigante": {"xp": (25, 35), "hp": 100, "atk": 20},
            "Múmia": {"xp": (30, 40), "hp": 120, "atk": 22}
        },
        "boss": {"name": "Faraó Amaldiçoado", "hp": 500, "atk": 35, "xp": 400, "level": 29},
        "resources": ["Areia mágica", "Ossos antigos", "Vendas místicas"],
        "texts": [
            "Você atravessa dunas escaldantes.",
            "O calor distorce o horizonte…",
            "Ruínas surgem da areia."
        ]
    },
    30: {
        "name": "❄️ Montanhas Geladas",
        "emoji": "❄️",
        "monsters": {
            "Lobo de Gelo": {"xp": (35, 45), "hp": 150, "atk": 28},
            "Golem de Neve": {"xp": (40, 50), "hp": 180, "atk": 30}
        },
        "boss": {"name": "Yeti Colossal", "hp": 750, "atk": 45, "xp": 600, "level": 39},
        "resources": ["Cristal de gelo", "Minério frio", "Pele de yeti"],
        "texts": [
            "Você escala montanhas geladas.",
            "O frio penetra até os ossos…",
            "Cristais de gelo refletem a luz."
        ]
    },
    40: {
        "name": "🌋 Reino Vulcânico",
        "emoji": "🌋",
        "monsters": {
            "Salamandra": {"xp": (45, 55), "hp": 200, "atk": 38},
            "Demônio de Lava": {"xp": (50, 60), "hp": 230, "atk": 42}
        },
        "boss": {"name": "Dragão de Magma", "hp": 1000, "atk": 55, "xp": 800, "level": 49},
        "resources": ["Pedra vulcânica", "Núcleo de fogo", "Escamas de dragão"],
        "texts": [
            "Você atravessa rios de lava.",
            "O calor é quase insuportável…",
            "A terra treme sob seus pés."
        ]
    },
    50: {
        "name": "🌌 Abismo Arcano",
        "emoji": "🌌",
        "monsters": {
            "Espectro": {"xp": (55, 70), "hp": 280, "atk": 48},
            "Mago Sombrio": {"xp": (60, 75), "hp": 300, "atk": 52}
        },
        "boss": {"name": "Senhor das Sombras", "hp": 1500, "atk": 70, "xp": 1200, "level": 59},
        "resources": ["Essência arcana", "Fragmento sombrio", "Cristal do vazio"],
        "texts": [
            "Você flutua no vazio arcano.",
            "Energias místicas pulsam ao redor…",
            "A realidade se curva e torce."
        ]
    },
    60: {
        "name": "👑 Trono Celestial",
        "emoji": "👑",
        "monsters": {
            "Guardião Celestial": {"xp": (80, 100), "hp": 400, "atk": 65}
        },
        "boss": {"name": "Imperador Astral", "hp": 2500, "atk": 100, "xp": 2000, "level": 60},
        "resources": ["Essência celestial", "Fragmento estelar", "Coroa divina"],
        "texts": [
            "Você ascende aos céus.",
            "Estrelas dançam ao seu redor…",
            "O poder divino ressoa."
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
        {"name": "Espada de Ferro", "rarity": "Incomum", "atk": 12},
        {"name": "Espada de Madeira Negra", "rarity": "Raro", "atk": 25},
        {"name": "Lâmina Flamejante", "rarity": "Épico", "atk": 45},
        {"name": "Excalibur", "rarity": "Lendário", "atk": 100}
    ],
    "armor": [
        {"name": "Armadura de Couro", "rarity": "Comum", "def": 3},
        {"name": "Armadura de Ferro", "rarity": "Incomum", "def": 8},
        {"name": "Armadura Mística", "rarity": "Raro", "def": 18},
        {"name": "Armadura Dracônica", "rarity": "Épico", "def": 35},
        {"name": "Armadura Celestial", "rarity": "Lendário", "def": 80}
    ]
}

# ================= FUNÇÕES =================

def save_data():
    """Salva dados do jogo"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(game_data, f, indent=4, ensure_ascii=False)

def load_data():
    """Carrega dados do jogo"""
    global game_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            game_data = json.load(f)

def roll_dice():
    """Rola dado de 1 a 10"""
    return random.randint(1, 10)

def get_luck(roll):
    """Retorna info do dado"""
    return LUCK_SYSTEM.get(roll, LUCK_SYSTEM[5])

def calc_xp(level):
    """Calcula XP necessário: nível² × 25"""
    return (level ** 2) * 25

def get_world(level):
    """Retorna mundo atual baseado no nível"""
    levels = sorted([k for k in WORLDS.keys() if k <= level], reverse=True)
    return WORLDS[levels[0]] if levels else WORLDS[1]

def create_player(user_id):
    """Cria novo jogador"""
    game_data["players"][str(user_id)] = {
        "level": 1,
        "xp": 0,
        "hp": 100,
        "max_hp": 100,
        "inventory": [],
        "equipment": {"weapon": None, "armor": None},
        "worlds": [1],
        "bosses": []
    }
    save_data()

def get_player(user_id):
    """Retorna dados do jogador"""
    uid = str(user_id)
    if uid not in game_data["players"]:
        create_player(user_id)
    return game_data["players"][uid]

def add_xp(user_id, amount):
    """Adiciona XP e verifica level up"""
    player = get_player(user_id)
    player["xp"] += amount
    leveled = False
    
    while player["xp"] >= calc_xp(player["level"]):
        player["xp"] -= calc_xp(player["level"])
        player["level"] += 1
        player["max_hp"] += 10
        player["hp"] = player["max_hp"]
        leveled = True
        
        # Desbloqueia mundos
        for wl in WORLDS.keys():
            if player["level"] >= wl and wl not in player["worlds"]:
                player["worlds"].append(wl)
    
    save_data()
    return leveled

def remove_xp(user_id, amount):
    """Remove XP (pode perder nível)"""
    player = get_player(user_id)
    player["xp"] -= amount
    
    while player["xp"] < 0 and player["level"] > 1:
        player["level"] -= 1
        player["xp"] += calc_xp(player["level"])
    
    if player["xp"] < 0:
        player["xp"] = 0
    
    # Reset completo se XP = 0 no nível 1
    if player["level"] == 1 and player["xp"] == 0:
        player["inventory"] = []
        player["equipment"] = {"weapon": None, "armor": None}
        player["worlds"] = [1]
        player["bosses"] = []
        player["hp"] = 100
        player["max_hp"] = 100
        save_data()
        return "reset"
    
    save_data()
    return "ok"

async def send_as_char(message, text):
    """Envia mensagem como personagem (estilo Tupperbox)"""
    uid = str(message.author.id)
    if uid not in game_data["active_chars"]:
        return await message.channel.send(text)
    
    char_name = game_data["active_chars"][uid]
    if uid in game_data["characters"] and char_name in game_data["characters"][uid]:
        char = game_data["characters"][uid][char_name]
        
        # Busca ou cria webhook
        webhooks = await message.channel.webhooks()
        webhook = None
        for wh in webhooks:
            if wh.name == "WORLD CSI RP":
                webhook = wh
                break
        
        if not webhook:
            webhook = await message.channel.create_webhook(name="WORLD CSI RP")
        
        try:
            await message.delete()
        except:
            pass
        
        await webhook.send(content=text, username=char["name"], avatar_url=char["avatar_url"])
    else:
        await message.channel.send(text)

# ================= EVENTOS =================

@bot.event
async def on_ready():
    load_data()
    print(f"🎮 {bot.user} está online!")
    print(f"📊 Servidores: {len(bot.guilds)}")
    print(f"👥 Jogadores: {len(game_data['players'])}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    uid = str(message.author.id)
    is_beta = message.channel.name == CANAL_BETA
    
    # Sistema de personagem com comando customizado (ex: arthur: mensagem)
    if uid in game_data["characters"] and not message.content.startswith("!"):
        for char_name, char_data in game_data["characters"][uid].items():
            cmd = char_data["command"]
            if message.content.startswith(f"{cmd}:"):
                rp_msg = message.content[len(cmd)+1:].strip()
                if rp_msg:
                    old_char = game_data["active_chars"].get(uid)
                    game_data["active_chars"][uid] = char_name
                    await send_as_char(message, rp_msg)
                    if old_char:
                        game_data["active_chars"][uid] = old_char
                    return
    
    await bot.process_commands(message)
    
    # Modo natural APENAS no canal mundo-beta
    if is_beta and not message.content.startswith("!"):
        lower = message.content.lower()
        
        if any(w in lower for w in ["eu vou", "vou explorar", "vou para", "explorar"]):
            ctx = await bot.get_context(message)
            await explorar(ctx)
        elif any(w in lower for w in ["caçar", "lutar", "atacar", "cacar", "vou caçar"]):
            ctx = await bot.get_context(message)
            await cacar(ctx)
        elif any(w in lower for w in ["coletar", "pegar recursos", "minerar", "vou coletar"]):
            ctx = await bot.get_context(message)
            await coletar(ctx)

# ================= COMANDOS - PERSONAGENS =================

@bot.command(name="ficha")
async def criar_ficha(ctx):
    """Cria ficha de personagem (funciona em qualquer canal)"""
    uid = str(ctx.author.id)
    
    if uid not in game_data["characters"]:
        game_data["characters"][uid] = {}
    
    embed = discord.Embed(
        title="📋 Criar Ficha de Personagem",
        description="Vamos criar seu personagem!",
        color=discord.Color.blue()
    )
    embed.add_field(name="1️⃣", value="Qual o **nome** do personagem?", inline=False)
    await ctx.send(embed=embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        # Nome
        msg = await bot.wait_for("message", check=check, timeout=60)
        char_name = msg.content.strip()
        
        if char_name in game_data["characters"][uid]:
            return await ctx.send(f"❌ Você já tem um personagem chamado **{char_name}**!")
        
        # Avatar
        embed = discord.Embed(
            title="📸 Avatar do Personagem",
            description=f"Personagem: **{char_name}**\n\nEnvie uma **imagem** ou **URL**:",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        
        msg = await bot.wait_for("message", check=check, timeout=120)
        
        avatar_url = None
        if msg.attachments:
            avatar_url = msg.attachments[0].url
        elif msg.content.startswith("http"):
            avatar_url = msg.content.strip()
        else:
            return await ctx.send("❌ URL ou imagem inválida!")
        
        # Comando
        embed = discord.Embed(
            title="⌨️ Comando do Personagem",
            description=f"Qual **comando** para falar como **{char_name}**?\n\nExemplo: `{char_name.lower()}`\n\n*Digite sem espaços:*",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        
        msg = await bot.wait_for("message", check=check, timeout=60)
        command = msg.content.strip().lower().replace(" ", "_")
        
        # Salva personagem
        game_data["characters"][uid][char_name] = {
            "name": char_name,
            "avatar_url": avatar_url,
            "command": command,
            "created_at": str(datetime.now())
        }
        
        game_data["active_chars"][uid] = char_name
        save_data()
        
        # Cria jogador se não existir
        if uid not in game_data["players"]:
            create_player(ctx.author.id)
        
        embed = discord.Embed(
            title="✅ Personagem Criado!",
            description=f"**{char_name}** foi criado com sucesso!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="📝 Nome", value=char_name, inline=True)
        embed.add_field(name="⌨️ Comando", value=f"`{command}:`", inline=True)
        embed.add_field(
            name="💡 Como usar",
            value=f"Digite `{command}: sua mensagem` para falar como o personagem!\n\nOu use `!char {char_name}` para ativá-lo.",
            inline=False
        )
        await ctx.send(embed=embed)
        
    except asyncio.TimeoutError:
        await ctx.send("⏱️ Tempo esgotado! Use `!ficha` novamente.")

@bot.command(name="personagens", aliases=["chars", "fichas"])
async def listar_chars(ctx):
    """Lista personagens do usuário"""
    uid = str(ctx.author.id)
    
    if uid not in game_data["characters"] or not game_data["characters"][uid]:
        return await ctx.send("❌ Você não tem personagens! Use `!ficha` para criar.")
    
    chars = game_data["characters"][uid]
    active = game_data["active_chars"].get(uid)
    
    embed = discord.Embed(
        title=f"📚 Personagens de {ctx.author.display_name}",
        description="Seus personagens criados:",
        color=discord.Color.blue()
    )
    
    for name, data in chars.items():
        status = "✅ **Ativo**" if name == active else "⚪ Inativo"
        embed.add_field(
            name=f"{name} {status}",
            value=f"Comando: `{data['command']}:`",
            inline=False
        )
    
    embed.set_footer(text="Use !char <nome> para trocar de personagem")
    await ctx.send(embed=embed)

@bot.command(name="char", aliases=["personagem"])
async def trocar_char(ctx, *, char_name: str = None):
    """Troca personagem ativo"""
    uid = str(ctx.author.id)
    
    if not char_name:
        return await listar_chars(ctx)
    
    if uid not in game_data["characters"]:
        return await ctx.send("❌ Você não tem personagens! Use `!ficha` para criar.")
    
    # Busca personagem (case insensitive)
    found = None
    for name in game_data["characters"][uid].keys():
        if name.lower() == char_name.lower():
            found = name
            break
    
    if not found:
        return await ctx.send(f"❌ Personagem **{char_name}** não encontrado!")
    
    game_data["active_chars"][uid] = found
    save_data()
    
    char_data = game_data["characters"][uid][found]
    embed = discord.Embed(
        title="✅ Personagem Ativo",
        description=f"Agora você está usando **{found}**!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=char_data["avatar_url"])
    embed.add_field(name="⌨️ Comando", value=f"`{char_data['command']}:`")
    await ctx.send(embed=embed)

@bot.command(name="deletar_personagem", aliases=["del_char"])
async def del_char(ctx, *, char_name: str):
    """Deleta um personagem"""
    uid = str(ctx.author.id)
    
    if uid not in game_data["characters"]:
        return await ctx.send("❌ Você não tem personagens!")
    
    found = None
    for name in game_data["characters"][uid].keys():
        if name.lower() == char_name.lower():
            found = name
            break
    
    if not found:
        return await ctx.send(f"❌ Personagem **{char_name}** não encontrado!")
    
    await ctx.send(f"⚠️ Tem certeza que quer deletar **{found}**? Digite `sim` para confirmar (30s)")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "sim"
    
    try:
        await bot.wait_for("message", check=check, timeout=30)
        
        del game_data["characters"][uid][found]
        
        if game_data["active_chars"].get(uid) == found:
            del game_data["active_chars"][uid]
        
        save_data()
        await ctx.send(f"✅ **{found}** foi deletado!")
        
    except asyncio.TimeoutError:
        await ctx.send("❌ Cancelado.")

# ================= COMANDOS - STATUS =================

@bot.command(name="perfil", aliases=["profile", "status"])
async def perfil(ctx):
    """Mostra perfil do jogador"""
    player = get_player(ctx.author.id)
    world = get_world(player["level"])
    xp_need = calc_xp(player["level"])
    
    embed = discord.Embed(
        title=f"👤 Perfil de {ctx.author.display_name}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    embed.add_field(name="⭐ Nível", value=f"`{player['level']}`", inline=True)
    embed.add_field(name="✨ XP", value=f"`{player['xp']}/{xp_need}`", inline=True)
    embed.add_field(name="❤️ HP", value=f"`{player['hp']}/{player['max_hp']}`", inline=True)
    
    embed.add_field(
        name="🌍 Mundo Atual",
        value=f"{world['emoji']} **{world['name']}**",
        inline=False
    )
    
    weapon = player["equipment"]["weapon"] or "Nenhuma"
    armor = player["equipment"]["armor"] or "Nenhuma"
    embed.add_field(name="⚔️ Arma", value=weapon, inline=True)
    embed.add_field(name="🛡️ Armadura", value=armor, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name="inventario", aliases=["inv", "bag"])
async def inventario(ctx):
    """Mostra inventário"""
    player = get_player(ctx.author.id)
    
    embed = discord.Embed(
        title=f"🎒 Inventário de {ctx.author.display_name}",
        color=discord.Color.gold()
    )
    
    if not player["inventory"]:
        embed.description = "*Inventário vazio*"
    else:
        items_count = {}
        for item in player["inventory"]:
            items_count[item] = items_count.get(item, 0) + 1
        
        text = "\n".join([f"• **{i}** x{c}" for i, c in items_count.items()])
        embed.description = text
    
    embed.set_footer(text=f"Total: {len(player['inventory'])} itens")
    await ctx.send(embed=embed)

@bot.command(name="xp")
async def mostrar_xp(ctx):
    """Mostra XP detalhado"""
    player = get_player(ctx.author.id)
    xp_need = calc_xp(player["level"])
    progress = (player["xp"] / xp_need) * 100
    
    bar_len = 20
    filled = int((progress / 100) * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    
    embed = discord.Embed(title="✨ Experiência", color=discord.Color.blue())
    embed.add_field(name="⭐ Nível", value=f"`{player['level']}`", inline=True)
    embed.add_field(name="📊 XP", value=f"`{player['xp']}/{xp_need}`", inline=True)
    embed.add_field(name="📈 Progresso", value=f"`{progress:.1f}%`", inline=True)
    embed.add_field(name="━━━━━━━━━━", value=f"`{bar}`", inline=False)
    
    # Próximos níveis
    next_levels = ""
    for i in range(1, 4):
        next_lvl = player["level"] + i
        if next_lvl <= 60:
            next_xp = calc_xp(next_lvl)
            next_levels += f"Nível {next_lvl}: `{next_xp} XP`\n"
    
    if next_levels:
        embed.add_field(name="🎯 Próximos Níveis", value=next_levels, inline=False)
    
    await ctx.send(embed=embed)

# ================= COMANDOS - RPG (APENAS EM mundo-beta) =================

@bot.command(name="explorar", aliases=["explore"])
async def explorar(ctx):
    """Explora o mundo atual"""
    if ctx.channel.name != CANAL_BETA:
        return await ctx.send(f"❌ Use este comando no canal **#{CANAL_BETA}**!")
    
    player = get_player(ctx.author.id)
    world = get_world(player["level"])
    roll = roll_dice()
    luck = get_luck(roll)
    
    # Texto narrativo
    text = random.choice(world["texts"])
    
    embed = discord.Embed(
        title=f"{world['emoji']} Explorando {world['name']}",
        description=text,
        color=discord.Color.blue()
    )
    embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    # Eventos baseados no dado
    if roll == 1:  # Azar extremo
        xp_loss = random.randint(30, 50)
        result = remove_xp(ctx.author.id, xp_loss)
        
        disasters = [
            "Você pisa em um terreno instável.\nO chão cede sob seus pés!",
            "Uma armadilha escondida se ativa!\nVocê escapa, mas paga o preço…",
            "Um desmoronamento quase te esmaga!"
        ]
        
        embed.add_field(
            name="💀 Desastre!",
            value=random.choice(disasters) + f"\n\n❌ **−{xp_loss} XP**",
            inline=False
        )
        
        if result == "reset":
            embed.add_field(
                name="🌑 Reset Completo",
                value="Seu poder se esvai completamente…\nVocê desperta novamente nos Campos Iniciais.\n\n*Sua jornada recomeça.*",
                inline=False
            )
            embed.color = discord.Color.dark_red()
    
    elif roll == 2:  # Muito azar
        xp_loss = random.randint(15, 30)
        remove_xp(ctx.author.id, xp_loss)
        embed.add_field(
            name="☠️ Muito Azar…",
            value=f"Você tropeça e cai!\nFerimentos leves.\n\n❌ **−{xp_loss} XP**",
            inline=False
        )
        embed.color = discord.Color.red()
    
    elif roll in [3, 4]:  # Azar/Ruim
        embed.add_field(
            name="😵 Nada Encontrado",
            value="Você procura, mas não encontra nada de útil…",
            inline=False
        )
        embed.color = discord.Color.light_grey()
    
    elif roll == 5:  # Neutro
        res = random.choice(world["resources"])
        player["inventory"].append(res)
        save_data()
        embed.add_field(
            name="😶 Recurso Encontrado",
            value=f"Você encontra algo.\n\n📦 **{res}**",
            inline=False
        )
        embed.color = discord.Color.greyple()
    
    elif roll in [6, 7]:  # Bom/Sorte
        xp = random.randint(15, 30)
        res = random.choice(world["resources"])
        player["inventory"].append(res)
        leveled = add_xp(ctx.author.id, xp)
        
        embed.add_field(
            name="🙂 Descoberta!",
            value=f"Você encontra algo interessante!\n\n📦 **{res}**\n⭐ **+{xp} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(
                name="🆙 Level Up!",
                value=f"⭐ Você sente seu poder crescer.\nUm novo caminho se abre no horizonte…\n\n**Nível {player['level']}**",
                inline=False
            )
            embed.color = discord.Color.gold()
        else:
            embed.color = discord.Color.green()
    
    elif roll == 8:  # Muita sorte
        xp = random.randint(30, 50)
        resources = random.sample(world["resources"], min(2, len(world["resources"])))
        for r in resources:
            player["inventory"].append(r)
        leveled = add_xp(ctx.author.id, xp)
        
        items = "\n".join([f"• **{r}**" for r in resources])
        
        embed.add_field(
            name="🍀 Baú Descoberto!",
            value=f"Um baú antigo jaz esquecido…\n\n🎁 **Conteúdo:**\n{items}\n⭐ **+{xp} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.green()
    
    elif roll == 9:  # Sorte extrema
        item_type = random.choice(["weapons", "armor"])
        rarity = random.choices(["Raro", "Épico", "Lendário"], weights=[50, 35, 15])[0]
        items = [i for i in ITEMS[item_type] if i["rarity"] == rarity]
        item = random.choice(items) if items else random.choice(ITEMS[item_type])
        
        player["inventory"].append(item["name"])
        xp = random.randint(40, 70)
        leveled = add_xp(ctx.author.id, xp)
        
        rarity_info = RARITIES[item["rarity"]]
        
        embed.add_field(
            name="✨ Descoberta Épica!",
            value=f"Uma luz brilha entre as sombras…\n\n{rarity_info['emoji']} **{item['name']}** ({item['rarity']})\n⭐ **+{xp} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = rarity_info["color"]
    
    else:  # roll == 10 - Lendário
        item_type = random.choice(["weapons", "armor"])
        legendary = [i for i in ITEMS[item_type] if i["rarity"] == "Lendário"]
        item = random.choice(legendary)
        
        player["inventory"].append(item["name"])
        xp = random.randint(80, 150)
        leveled = add_xp(ctx.author.id, xp)
        
        embed.add_field(
            name="🌟 EVENTO LENDÁRIO!",
            value=f"O mundo estremece!\nUma energia divina emana do solo…\n\n🟡 **{item['name']}** (Lendário)\n⭐ **+{xp} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.gold()
    
    await ctx.send(embed=embed)
    
    # Verifica aparição de boss
    boss_lvls = [9, 19, 29, 39, 49, 59]
    if player["level"] in boss_lvls:
        await asyncio.sleep(2)
        
        boss_world_lvl = player["level"] - (player["level"] % 10) + 1
        boss_world = WORLDS.get(boss_world_lvl)
        
        if boss_world and boss_world["boss"]["name"] not in player["bosses"]:
            boss_embed = discord.Embed(
                title="⚠️ BOSS APARECEU!",
                description=f"Uma presença poderosa bloqueia seu caminho…\n\n**{boss_world['boss']['name']}** emergiu das sombras!",
                color=discord.Color.dark_red()
            )
            boss_embed.add_field(
                name="💀 Desafio",
                value=f"Use `!boss` para enfrentá-lo!\n\n*Você precisa derrotá-lo para avançar.*",
                inline=False
            )
            await ctx.send(embed=boss_embed)

@bot.command(name="cacar", aliases=["caçar", "hunt", "lutar"])
async def cacar(ctx):
    """Caça monstros"""
    if ctx.channel.name != CANAL_BETA:
        return await ctx.send(f"❌ Use em **#{CANAL_BETA}**!")
    
    player = get_player(ctx.author.id)
    world = get_world(player["level"])
    
    monster_name = random.choice(list(world["monsters"].keys()))
    monster = world["monsters"][monster_name]
    
    roll = roll_dice()
    luck = get_luck(roll)
    
    embed = discord.Embed(
        title=f"⚔️ Caçando em {world['name']}",
        description=f"Você encontra um **{monster_name}**!\n\n*A batalha começa…*",
        color=discord.Color.red()
    )
    embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    if roll <= 3:  # Derrota
        xp_loss = random.randint(20, 40)
        dmg = random.randint(10, 30)
        player["hp"] -= dmg
        
        if player["hp"] <= 0:
            player["hp"] = player["max_hp"] // 2
            xp_loss *= 2
        
        remove_xp(ctx.author.id, xp_loss)
        
        embed.add_field(
            name="💀 Derrota!",
            value=f"O {monster_name} te domina!\n\n❌ **−{xp_loss} XP**\n💔 **−{dmg} HP**",
            inline=False
        )
        embed.color = discord.Color.dark_red()
    
    elif roll <= 5:  # Vitória difícil
        xp = random.randint(monster["xp"][0], monster["xp"][0] + 5)
        dmg = random.randint(5, 15)
        player["hp"] -= dmg
        leveled = add_xp(ctx.author.id, xp)
        
        embed.add_field(
            name="😓 Vitória Difícil",
            value=f"Você derrota o {monster_name}, mas se fere.\n\n⭐ **+{xp} XP**\n💔 **−{dmg} HP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.orange()
    
    elif roll <= 7:  # Vitória normal
        xp = random.randint(monster["xp"][0], monster["xp"][1])
        leveled = add_xp(ctx.author.id, xp)
        
        embed.add_field(
            name="⚔️ Vitória!",
            value=f"Você derrota o {monster_name}!\n\n⭐ **+{xp} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.green()
    
    else:  # 8-10 Vitória perfeita
        xp = random.randint(monster["xp"][1], monster["xp"][1] + 10)
        leveled = add_xp(ctx.author.id, xp)
        
        drop = None
        if roll >= 9:
            drop = random.choice(world["resources"])
            player["inventory"].append(drop)
        
        drop_text = f"\n📦 **{drop}**" if drop else ""
        
        embed.add_field(
            name="✨ Vitória Perfeita!",
            value=f"Você aniquila o {monster_name} com maestria!\n\n⭐ **+{xp} XP**{drop_text}",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.gold()
    
    save_data()
    await ctx.send(embed=embed)

@bot.command(name="boss")
async def boss(ctx):
    """Enfrenta o boss"""
    if ctx.channel.name != CANAL_BETA:
        return await ctx.send(f"❌ Use em **#{CANAL_BETA}**!")
    
    player = get_player(ctx.author.id)
    boss_lvls = [9, 19, 29, 39, 49, 59]
    
    if player["level"] not in boss_lvls:
        return await ctx.send("❌ Não há boss disponível no seu nível atual!")
    
    boss_world_lvl = player["level"] - (player["level"] % 10) + 1
    boss_world = WORLDS.get(boss_world_lvl)
    
    if not boss_world:
        return await ctx.send("❌ Erro ao encontrar boss!")
    
    boss_data = boss_world["boss"]
    
    if boss_data["name"] in player["bosses"]:
        return await ctx.send(f"✅ Você já derrotou **{boss_data['name']}**! Continue explorando.")
    
    roll = roll_dice()
    luck = get_luck(roll)
    
    embed = discord.Embed(
        title=f"👹 BATALHA DE BOSS",
        description=f"**{boss_data['name']}** se ergue diante de você!\n\n*Esta é uma batalha lendária…*",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="💀 Boss", value=boss_data["name"], inline=True)
    embed.add_field(name="❤️ HP", value=f"`{boss_data['hp']}`", inline=True)
    embed.add_field(name="⚔️ ATK", value=f"`{boss_data['atk']}`", inline=True)
    embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    if roll <= 4:  # Derrota crítica
        xp_loss = random.randint(100, 200)
        result = remove_xp(ctx.author.id, xp_loss)
        
        embed.add_field(
            name="💀 Derrota Esmagadora!",
            value=f"O {boss_data['name']} te derrota!\n\n*{boss_world['name'][2:]} rejeita sua presença…*\n\n❌ **−{xp_loss} XP**",
            inline=False
        )
        
        if result == "reset":
            embed.add_field(
                name="🌑 Reset Completo",
                value="Seu poder se esvai completamente…\nVocê desperta novamente nos Campos Iniciais.",
                inline=False
            )
        
        embed.color = discord.Color.dark_red()
    
    elif roll <= 6:  # Empate
        xp_loss = random.randint(50, 80)
        remove_xp(ctx.author.id, xp_loss)
        
        embed.add_field(
            name="😰 Batalha Intensa",
            value=f"Vocês lutam ferozmente, mas você precisa recuar!\n\n❌ **−{xp_loss} XP**\n\n*Tente novamente quando estiver mais forte…*",
            inline=False
        )
        embed.color = discord.Color.orange()
    
    else:  # Vitória
        xp = boss_data["xp"] + (50 if roll >= 9 else 0)
        player["bosses"].append(boss_data["name"])
        leveled = add_xp(ctx.author.id, xp)
        
        # Desbloqueia próximo mundo
        next_world_lvl = boss_world_lvl + 10
        if next_world_lvl in WORLDS and next_world_lvl not in player["worlds"]:
            player["worlds"].append(next_world_lvl)
            next_world = WORLDS[next_world_lvl]
            embed.add_field(
                name="🗺️ Novo Mundo Desbloqueado!",
                value=f"{next_world['emoji']} **{next_world['name']}**\n\n*Um novo caminho se abre…*",
                inline=False
            )
        
        # Item lendário em vitória perfeita
        if roll >= 9:
            item_type = random.choice(["weapons", "armor"])
            legendary = [i for i in ITEMS[item_type] if i["rarity"] == "Lendário"]
            item = random.choice(legendary)
            player["inventory"].append(item["name"])
            
            embed.add_field(
                name="🌟 VITÓRIA LENDÁRIA!",
                value=f"Você derrota o {boss_data['name']} com poder absoluto!\n\n⭐ **+{xp} XP**\n🟡 **{item['name']}** (Lendário)",
                inline=False
            )
        else:
            embed.add_field(
                name="🏆 VITÓRIA!",
                value=f"Após uma batalha épica, você derrota o {boss_data['name']}!\n\n⭐ **+{xp} XP**",
                inline=False
            )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.gold()
    
    save_data()
    await ctx.send(embed=embed)

@bot.command(name="coletar", aliases=["collect", "gather"])
async def coletar(ctx):
    """Coleta recursos"""
    if ctx.channel.name != CANAL_BETA:
        return await ctx.send(f"❌ Use em **#{CANAL_BETA}**!")
    
    player = get_player(ctx.author.id)
    world = get_world(player["level"])
    
    roll = roll_dice()
    luck = get_luck(roll)
    
    embed = discord.Embed(
        title=f"⛏️ Coletando em {world['name']}",
        description="Você procura por recursos…",
        color=discord.Color.blue()
    )
    embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    if roll <= 3:
        embed.add_field(name="😔 Sem Sorte", value="Você não encontra nada útil…", inline=False)
        embed.color = discord.Color.light_grey()
    
    elif roll <= 6:
        res = random.choice(world["resources"])
        player["inventory"].append(res)
        embed.add_field(name="📦 Recurso Coletado", value=f"**{res}**", inline=False)
        embed.color = discord.Color.green()
    
    elif roll <= 8:
        resources = [random.choice(world["resources"]) for _ in range(2)]
        for r in resources:
            player["inventory"].append(r)
        items = "\n".join([f"• **{r}**" for r in resources])
        embed.add_field(name="🍀 Boa Coleta!", value=items, inline=False)
        embed.color = discord.Color.green()
    
    else:  # 9-10
        count = 3 if roll == 9 else 4
        resources = [random.choice(world["resources"]) for _ in range(count)]
        for r in resources:
            player["inventory"].append(r)
        items = "\n".join([f"• **{r}**" for r in resources])
        embed.add_field(name="✨ Coleta Abundante!", value=items, inline=False)
        embed.color = discord.Color.gold()
    
    save_data()
    await ctx.send(embed=embed)

# ================= COMANDO DE AJUDA =================

@bot.command(name="help", aliases=["ajuda", "comandos"])
async def help_cmd(ctx):
    """Mostra comandos"""
    embed = discord.Embed(
        title="📖 WORLD CSI - Guia de Comandos",
        description="Bem-vindo ao WORLD CSI!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="👤 Sistema de Personagens",
        value="""
`!ficha` - Criar personagem
`!personagens` - Ver personagens
`!char <nome>` - Trocar personagem
`!deletar_personagem <nome>` - Deletar

💡 **Como usar:**
Após criar com `!ficha`, use:
`comando: sua mensagem`
Exemplo: `arthur: Olá!`
        """,
        inline=False
    )
    
    embed.add_field(
        name="📊 Perfil & Status",
        value="`!perfil` `!xp` `!inventario`",
        inline=False
    )
    
    embed.add_field(
        name=f"🗺️ Exploração (Canal #{CANAL_BETA})",
        value="""
`!explorar` - Explorar mundo
`!caçar` - Caçar monstros
`!coletar` - Coletar recursos
`!boss` - Enfrentar boss

💡 **Modo Natural:**
• "eu vou explorar" → explora
• "vou caçar" → caça
• "vou coletar" → coleta
        """,
        inline=False
    )
    
    embed.add_field(
        name="🎲 Sistema de Sorte (Dado 1-10)",
        value="""
`1-2` 💀 Azar (perde XP/HP)
`3-4` 😐 Ruim (pouco)
`5-6` 🙂 Bom (recompensa)
`7-8` 🍀 Sorte (extra)
`9-10` ✨ Lenda (épico)
        """,
        inline=False
    )
    
    embed.set_footer(text="Use !perfil para começar!")
    await ctx.send(embed=embed)

# ================= EXECUTAR BOT =================

bot.run(TOKEN)
