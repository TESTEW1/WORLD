import discord
from discord.ext import commands
import json
import random
import os
import asyncio
from typing import Optional, Dict, List

# ============================================================
# CONFIGURAÇÃO DO BOT
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ============================================================
# ARMAZENAMENTO DE DADOS
# ============================================================
DATA_FILE = 'world_csi_data.json'
BETA_CHANNEL_NAME = 'mundo-beta'

game_data = {
    'players': {},      # user_id: player_data
    'characters': {},   # user_id: {char_name: character_data}
    'active_chars': {}  # user_id: char_name atual
}

# ============================================================
# SISTEMA DE SORTE (DADOS 1-10)
# ============================================================
LUCK_SYSTEM = {
    1: {'emoji': '💀', 'name': 'Azar extremo', 'desc': 'Falha crítica'},
    2: {'emoji': '☠️', 'name': 'Muito azar', 'desc': 'Perde recursos ou leva dano'},
    3: {'emoji': '😵', 'name': 'Azar', 'desc': 'Resultado fraco'},
    4: {'emoji': '😐', 'name': 'Ruim', 'desc': 'Efeito mínimo'},
    5: {'emoji': '😶', 'name': 'Neutro', 'desc': 'Resultado básico'},
    6: {'emoji': '🙂', 'name': 'Bom', 'desc': 'Resultado positivo'},
    7: {'emoji': '😄', 'name': 'Sorte', 'desc': 'Ação melhorada'},
    8: {'emoji': '🍀', 'name': 'Muita sorte', 'desc': 'Recompensa extra'},
    9: {'emoji': '✨', 'name': 'Sorte extrema', 'desc': 'Drop raro ou crítico'},
    10: {'emoji': '🌟', 'name': 'Lenda', 'desc': 'Evento épico'}
}

# ============================================================
# MUNDOS DO JOGO
# ============================================================
WORLDS = {
    1: {
        'name': '🌱 Campos Iniciais',
        'emoji': '🌱',
        'monsters': {
            'Slime': {'xp': (5, 10), 'hp': 30, 'atk': 5},
            'Rato Selvagem': {'xp': (7, 12), 'hp': 25, 'atk': 7}
        },
        'boss': {'name': 'Slime Rei', 'hp': 150, 'atk': 15, 'xp': 150, 'level': 9},
        'resources': ['Pedra fraca', 'Grama mágica', 'Couro de rato'],
        'description': 'Campos verdejantes onde sua jornada começa...',
        'explore_texts': [
            'Você caminha entre campos floridos.',
            'O sol brilha suavemente sobre a grama.',
            'Uma brisa tranquila passa por você.'
        ]
    },
    10: {
        'name': '🌲 Floresta Sombria',
        'emoji': '🌲',
        'monsters': {
            'Goblin': {'xp': (15, 25), 'hp': 60, 'atk': 12},
            'Lobo Negro': {'xp': (18, 30), 'hp': 70, 'atk': 15}
        },
        'boss': {'name': 'Ent Ancião', 'hp': 300, 'atk': 25, 'xp': 250, 'level': 19},
        'resources': ['Madeira escura', 'Ervas raras', 'Pele de lobo'],
        'description': 'Árvores antigas guardam segredos obscuros...',
        'explore_texts': [
            'Você caminha entre árvores antigas.',
            'O vento sussurra histórias esquecidas...',
            'Sombras dançam entre os galhos.'
        ]
    },
    20: {
        'name': '🏜️ Deserto das Almas',
        'emoji': '🏜️',
        'monsters': {
            'Escorpião Gigante': {'xp': (25, 35), 'hp': 100, 'atk': 20},
            'Múmia': {'xp': (30, 40), 'hp': 120, 'atk': 22}
        },
        'boss': {'name': 'Faraó Amaldiçoado', 'hp': 500, 'atk': 35, 'xp': 400, 'level': 29},
        'resources': ['Areia mágica', 'Ossos antigos', 'Vendas místicas'],
        'description': 'Dunas infinitas escondem ruínas ancestrais...',
        'explore_texts': [
            'Você atravessa dunas escaldantes.',
            'O calor distorce o horizonte...',
            'Ruínas surgem da areia.'
        ]
    },
    30: {
        'name': '❄️ Montanhas Geladas',
        'emoji': '❄️',
        'monsters': {
            'Lobo de Gelo': {'xp': (35, 45), 'hp': 150, 'atk': 28},
            'Golem de Neve': {'xp': (40, 50), 'hp': 180, 'atk': 30}
        },
        'boss': {'name': 'Yeti Colossal', 'hp': 750, 'atk': 45, 'xp': 600, 'level': 39},
        'resources': ['Cristal de gelo', 'Minério frio', 'Pele de yeti'],
        'description': 'Picos congelados onde o vento corta como lâmina...',
        'explore_texts': [
            'Você escala montanhas geladas.',
            'O frio penetra até os ossos...',
            'Cristais de gelo refletem a luz.'
        ]
    },
    40: {
        'name': '🌋 Reino Vulcânico',
        'emoji': '🌋',
        'monsters': {
            'Salamandra': {'xp': (45, 55), 'hp': 200, 'atk': 38},
            'Demônio de Lava': {'xp': (50, 60), 'hp': 230, 'atk': 42}
        },
        'boss': {'name': 'Dragão de Magma', 'hp': 1000, 'atk': 55, 'xp': 800, 'level': 49},
        'resources': ['Pedra vulcânica', 'Núcleo de fogo', 'Escamas de dragão'],
        'description': 'Rios de lava iluminam a escuridão ardente...',
        'explore_texts': [
            'Você atravessa rios de lava.',
            'O calor é quase insuportável...',
            'A terra treme sob seus pés.'
        ]
    },
    50: {
        'name': '🌌 Abismo Arcano',
        'emoji': '🌌',
        'monsters': {
            'Espectro': {'xp': (55, 70), 'hp': 280, 'atk': 48},
            'Mago Sombrio': {'xp': (60, 75), 'hp': 300, 'atk': 52}
        },
        'boss': {'name': 'Senhor das Sombras', 'hp': 1500, 'atk': 70, 'xp': 1200, 'level': 59},
        'resources': ['Essência arcana', 'Fragmento sombrio', 'Cristal do vazio'],
        'description': 'Energias místicas distorcem a realidade...',
        'explore_texts': [
            'Você flutua no vazio arcano.',
            'Energias místicas pulsam ao redor...',
            'A realidade se curva e torce.'
        ]
    },
    60: {
        'name': '👑 Trono Celestial',
        'emoji': '👑',
        'monsters': {
            'Guardião Celestial': {'xp': (80, 100), 'hp': 400, 'atk': 65}
        },
        'boss': {'name': 'Imperador Astral', 'hp': 2500, 'atk': 100, 'xp': 2000, 'level': 60},
        'resources': ['Essência celestial', 'Fragmento estelar', 'Coroa divina'],
        'description': 'O trono dos deuses aguarda o digno...',
        'explore_texts': [
            'Você ascende aos céus.',
            'Estrelas dançam ao seu redor...',
            'O poder divino ressoa.'
        ]
    }
}

# ============================================================
# ITENS E EQUIPAMENTOS
# ============================================================
RARITIES = {
    'Comum': {'color': 0xFFFFFF, 'emoji': '⚪'},
    'Incomum': {'color': 0x00FF00, 'emoji': '🟢'},
    'Raro': {'color': 0x0000FF, 'emoji': '🔵'},
    'Épico': {'color': 0x800080, 'emoji': '🟣'},
    'Lendário': {'color': 0xFFD700, 'emoji': '🟡'}
}

ITEMS_POOL = {
    'weapons': [
        {'name': 'Espada Enferrujada', 'rarity': 'Comum', 'atk': 5},
        {'name': 'Espada de Ferro', 'rarity': 'Incomum', 'atk': 12},
        {'name': 'Espada de Madeira Negra', 'rarity': 'Raro', 'atk': 25},
        {'name': 'Lâmina Flamejante', 'rarity': 'Épico', 'atk': 45},
        {'name': 'Excalibur', 'rarity': 'Lendário', 'atk': 100},
    ],
    'armor': [
        {'name': 'Armadura de Couro', 'rarity': 'Comum', 'def': 3},
        {'name': 'Armadura de Ferro', 'rarity': 'Incomum', 'def': 8},
        {'name': 'Armadura Mística', 'rarity': 'Raro', 'def': 18},
        {'name': 'Armadura Dracônica', 'rarity': 'Épico', 'def': 35},
        {'name': 'Armadura Celestial', 'rarity': 'Lendário', 'def': 80},
    ]
}

# ============================================================
# FUNÇÕES DE UTILIDADE
# ============================================================

def save_data():
    """Salva os dados do jogo"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, indent=4, ensure_ascii=False)

def load_data():
    """Carrega os dados do jogo"""
    global game_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            game_data = json.load(f)

def roll_dice():
    """Rola um dado de 1 a 10"""
    return random.randint(1, 10)

def get_luck_info(roll):
    """Retorna informações sobre o resultado do dado"""
    return LUCK_SYSTEM.get(roll, LUCK_SYSTEM[5])

def calculate_xp_needed(level):
    """Calcula XP necessário para o próximo nível"""
    return (level ** 2) * 25

def get_current_world(level):
    """Retorna o mundo atual baseado no nível"""
    world_levels = sorted([k for k in WORLDS.keys() if k <= level], reverse=True)
    return WORLDS[world_levels[0]] if world_levels else WORLDS[1]

def get_next_world(level):
    """Retorna o próximo mundo a ser desbloqueado"""
    for world_level in sorted(WORLDS.keys()):
        if world_level > level:
            return WORLDS[world_level]
    return None

def create_player(user_id):
    """Cria um novo jogador"""
    game_data['players'][str(user_id)] = {
        'level': 1,
        'xp': 0,
        'hp': 100,
        'max_hp': 100,
        'inventory': [],
        'equipment': {'weapon': None, 'armor': None},
        'unlocked_worlds': [1],
        'boss_defeated': []
    }
    save_data()

def get_player(user_id):
    """Retorna os dados do jogador"""
    user_id_str = str(user_id)
    if user_id_str not in game_data['players']:
        create_player(user_id)
    return game_data['players'][user_id_str]

def add_xp(user_id, amount):
    """Adiciona XP ao jogador e verifica level up"""
    player = get_player(user_id)
    player['xp'] += amount
    
    leveled_up = False
    while player['xp'] >= calculate_xp_needed(player['level']):
        player['xp'] -= calculate_xp_needed(player['level'])
        player['level'] += 1
        player['max_hp'] += 10
        player['hp'] = player['max_hp']
        leveled_up = True
        
        # Desbloquear novo mundo
        for world_level in WORLDS.keys():
            if player['level'] >= world_level and world_level not in player['unlocked_worlds']:
                player['unlocked_worlds'].append(world_level)
    
    save_data()
    return leveled_up

def remove_xp(user_id, amount):
    """Remove XP do jogador (pode causar perda de nível)"""
    player = get_player(user_id)
    player['xp'] -= amount
    
    level_lost = False
    while player['xp'] < 0 and player['level'] > 1:
        player['level'] -= 1
        player['xp'] += calculate_xp_needed(player['level'])
        level_lost = True
    
    if player['xp'] < 0:
        player['xp'] = 0
    
    # Reset completo se chegar a 0 XP no nível 1
    if player['level'] == 1 and player['xp'] == 0:
        player['inventory'] = []
        player['equipment'] = {'weapon': None, 'armor': None}
        player['unlocked_worlds'] = [1]
        player['boss_defeated'] = []
        player['hp'] = 100
        player['max_hp'] = 100
        save_data()
        return 'reset'
    
    save_data()
    return 'level_lost' if level_lost else 'xp_lost'

# ============================================================
# SISTEMA DE PERSONAGENS (ESTILO TUPPERBOX)
# ============================================================

def get_active_character(user_id):
    """Retorna o personagem ativo do usuário"""
    user_id_str = str(user_id)
    if user_id_str not in game_data['active_chars']:
        return None
    
    char_name = game_data['active_chars'][user_id_str]
    if user_id_str in game_data['characters'] and char_name in game_data['characters'][user_id_str]:
        return game_data['characters'][user_id_str][char_name]
    return None

async def send_as_character(message, text, user_id):
    """Envia mensagem como personagem (estilo Tupperbox)"""
    char = get_active_character(user_id)
    if not char:
        return await message.channel.send(text)
    
    # Criar webhook para enviar como personagem
    webhooks = await message.channel.webhooks()
    webhook = None
    
    for wh in webhooks:
        if wh.name == "WORLD CSI RP":
            webhook = wh
            break
    
    if not webhook:
        webhook = await message.channel.create_webhook(name="WORLD CSI RP")
    
    try:
        # Deleta a mensagem original
        await message.delete()
    except:
        pass
    
    # Envia como personagem
    await webhook.send(
        content=text,
        username=char['name'],
        avatar_url=char['avatar_url']
    )

# ============================================================
# EVENTOS DO BOT
# ============================================================

@bot.event
async def on_ready():
    load_data()
    print(f'🎮 {bot.user} está online!')
    print(f'📊 Servidores: {len(bot.guilds)}')
    print(f'👥 Jogadores registrados: {len(game_data["players"])}')
    await bot.change_presence(activity=discord.Game(name="WORLD CSI | !help"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Verifica se está no canal beta
    is_beta_channel = message.channel.name == BETA_CHANNEL_NAME
    
    # Detecta uso do comando personalizado do personagem
    user_id = str(message.author.id)
    if user_id in game_data['characters'] and not message.content.startswith('!'):
        for char_name, char_data in game_data['characters'][user_id].items():
            command = char_data['command']
            if message.content.startswith(f"{command}:"):
                # Extrai a mensagem após o comando
                rp_message = message.content[len(command)+1:].strip()
                if rp_message:
                    # Temporariamente ativa o personagem
                    old_char = game_data['active_chars'].get(user_id)
                    game_data['active_chars'][user_id] = char_name
                    await send_as_character(message, rp_message, message.author.id)
                    # Restaura personagem anterior
                    if old_char:
                        game_data['active_chars'][user_id] = old_char
                    return
    
    # Processa comandos normalmente
    await bot.process_commands(message)
    
    # Sistema de RP natural (sem !) apenas no canal beta
    if is_beta_channel and not message.content.startswith('!'):
        content_lower = message.content.lower()
        
        # Detecta ações naturais
        if any(word in content_lower for word in ['eu vou', 'vou para', 'vou explorar', 'explorar']):
            ctx = await bot.get_context(message)
            await explorar(ctx)
            return
        
        elif any(word in content_lower for word in ['caçar', 'lutar', 'batalhar', 'atacar']):
            ctx = await bot.get_context(message)
            await cacar(ctx)
            return
        
        elif any(word in content_lower for word in ['coletar', 'pegar recursos', 'minerar']):
            ctx = await bot.get_context(message)
            await coletar(ctx)
            return

# ============================================================
# COMANDOS - SISTEMA DE PERSONAGENS
# ============================================================

@bot.command(name='ficha')
async def criar_ficha(ctx):
    """Cria uma ficha de personagem"""
    user_id = str(ctx.author.id)
    
    # Inicializa estrutura se necessário
    if user_id not in game_data['characters']:
        game_data['characters'][user_id] = {}
    
    embed = discord.Embed(
        title="📋 Criar Ficha de Personagem",
        description="Vamos criar seu personagem! Responda as perguntas abaixo:",
        color=discord.Color.blue()
    )
    embed.add_field(name="1️⃣", value="Qual o **nome** do personagem?", inline=False)
    await ctx.send(embed=embed)
    
    # Aguarda nome
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        char_name = msg.content.strip()
        
        if char_name in game_data['characters'][user_id]:
            return await ctx.send(f"❌ Você já tem um personagem chamado **{char_name}**!")
        
        # Pede avatar
        embed = discord.Embed(
            title="📸 Avatar do Personagem",
            description=f"Personagem: **{char_name}**\n\nEnvie uma **imagem** ou **URL** para o avatar:",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        
        msg = await bot.wait_for('message', check=check, timeout=120.0)
        
        avatar_url = None
        if msg.attachments:
            avatar_url = msg.attachments[0].url
        elif msg.content.startswith('http'):
            avatar_url = msg.content.strip()
        else:
            return await ctx.send("❌ URL ou imagem inválida!")
        
        # Pede comando personalizado
        embed = discord.Embed(
            title="⌨️ Comando do Personagem",
            description=f"Qual comando você quer usar para falar como **{char_name}**?\n\nExemplo: `{char_name.lower()}:`\n\n*Digite o comando (sem espaços):*",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        command = msg.content.strip().lower().replace(' ', '_')
        
        # Salva personagem
        game_data['characters'][user_id][char_name] = {
            'name': char_name,
            'avatar_url': avatar_url,
            'command': command,
            'created_at': str(ctx.message.created_at)
        }
        
        # Define como personagem ativo
        game_data['active_chars'][user_id] = char_name
        save_data()
        
        # Cria jogador se não existir
        if user_id not in game_data['players']:
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

@bot.command(name='personagens', aliases=['chars', 'fichas'])
async def listar_personagens(ctx):
    """Lista todos os personagens do usuário"""
    user_id = str(ctx.author.id)
    
    if user_id not in game_data['characters'] or not game_data['characters'][user_id]:
        return await ctx.send("❌ Você não tem personagens! Use `!ficha` para criar.")
    
    chars = game_data['characters'][user_id]
    active_char = game_data['active_chars'].get(user_id)
    
    embed = discord.Embed(
        title=f"📚 Personagens de {ctx.author.display_name}",
        description="Seus personagens criados:",
        color=discord.Color.blue()
    )
    
    for char_name, char_data in chars.items():
        status = "✅ **Ativo**" if char_name == active_char else "⚪ Inativo"
        embed.add_field(
            name=f"{char_name} {status}",
            value=f"Comando: `{char_data['command']}:`",
            inline=False
        )
    
    embed.set_footer(text="Use !char <nome> para trocar de personagem")
    await ctx.send(embed=embed)

@bot.command(name='char', aliases=['personagem'])
async def trocar_personagem(ctx, *, char_name: str = None):
    """Troca o personagem ativo"""
    user_id = str(ctx.author.id)
    
    if not char_name:
        return await listar_personagens(ctx)
    
    if user_id not in game_data['characters']:
        return await ctx.send("❌ Você não tem personagens! Use `!ficha` para criar.")
    
    # Busca personagem (case insensitive)
    found_char = None
    for name, data in game_data['characters'][user_id].items():
        if name.lower() == char_name.lower():
            found_char = name
            break
    
    if not found_char:
        return await ctx.send(f"❌ Personagem **{char_name}** não encontrado!")
    
    game_data['active_chars'][user_id] = found_char
    save_data()
    
    char_data = game_data['characters'][user_id][found_char]
    embed = discord.Embed(
        title="✅ Personagem Ativo",
        description=f"Agora você está usando **{found_char}**!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=char_data['avatar_url'])
    embed.add_field(name="⌨️ Comando", value=f"`{char_data['command']}:`")
    await ctx.send(embed=embed)

@bot.command(name='deletar_personagem', aliases=['del_char'])
async def deletar_personagem(ctx, *, char_name: str):
    """Deleta um personagem"""
    user_id = str(ctx.author.id)
    
    if user_id not in game_data['characters']:
        return await ctx.send("❌ Você não tem personagens!")
    
    # Busca personagem
    found_char = None
    for name in game_data['characters'][user_id].keys():
        if name.lower() == char_name.lower():
            found_char = name
            break
    
    if not found_char:
        return await ctx.send(f"❌ Personagem **{char_name}** não encontrado!")
    
    # Confirmação
    await ctx.send(f"⚠️ Tem certeza que quer deletar **{found_char}**? Digite `sim` para confirmar (30s)")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'sim'
    
    try:
        await bot.wait_for('message', check=check, timeout=30.0)
        
        del game_data['characters'][user_id][found_char]
        
        # Remove de ativo se for o personagem ativo
        if game_data['active_chars'].get(user_id) == found_char:
            del game_data['active_chars'][user_id]
        
        save_data()
        await ctx.send(f"✅ **{found_char}** foi deletado!")
        
    except asyncio.TimeoutError:
        await ctx.send("❌ Cancelado.")

# ============================================================
# COMANDOS - PERFIL E STATUS
# ============================================================

@bot.command(name='perfil', aliases=['profile', 'status'])
async def perfil(ctx):
    """Mostra o perfil do jogador"""
    player = get_player(ctx.author.id)
    world = get_current_world(player['level'])
    next_world = get_next_world(player['level'])
    xp_needed = calculate_xp_needed(player['level'])
    
    embed = discord.Embed(
        title=f"👤 Perfil de {ctx.author.display_name}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    # Status
    embed.add_field(name="⭐ Nível", value=f"`{player['level']}`", inline=True)
    embed.add_field(name="✨ XP", value=f"`{player['xp']}/{xp_needed}`", inline=True)
    embed.add_field(name="❤️ HP", value=f"`{player['hp']}/{player['max_hp']}`", inline=True)
    
    # Mundo atual
    embed.add_field(
        name=f"🌍 Mundo Atual",
        value=f"{world['emoji']} **{world['name']}**",
        inline=False
    )
    
    # Próximo mundo
    if next_world:
        next_level = [k for k in WORLDS.keys() if WORLDS[k] == next_world][0]
        embed.add_field(
            name="🔒 Próximo Mundo",
            value=f"{next_world['emoji']} **{next_world['name']}** (Nível {next_level})",
            inline=False
        )
    
    # Equipamentos
    weapon = player['equipment']['weapon'] or "Nenhuma"
    armor = player['equipment']['armor'] or "Nenhuma"
    embed.add_field(name="⚔️ Arma", value=weapon, inline=True)
    embed.add_field(name="🛡️ Armadura", value=armor, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='inventario', aliases=['inv', 'bag'])
async def inventario(ctx):
    """Mostra o inventário do jogador"""
    player = get_player(ctx.author.id)
    
    embed = discord.Embed(
        title=f"🎒 Inventário de {ctx.author.display_name}",
        color=discord.Color.gold()
    )
    
    if not player['inventory']:
        embed.description = "*Inventário vazio*"
    else:
        # Agrupa itens
        items_count = {}
        for item in player['inventory']:
            items_count[item] = items_count.get(item, 0) + 1
        
        inv_text = ""
        for item, count in items_count.items():
            inv_text += f"• **{item}** x{count}\n"
        
        embed.description = inv_text
    
    embed.set_footer(text=f"Total de itens: {len(player['inventory'])}")
    await ctx.send(embed=embed)

# ============================================================
# COMANDOS - EXPLORAÇÃO
# ============================================================

@bot.command(name='explorar', aliases=['explore'])
async def explorar(ctx):
    """Explora o mundo atual"""
    # Verifica canal
    if ctx.channel.name != BETA_CHANNEL_NAME:
        return await ctx.send(f"❌ Use este comando no canal **#{BETA_CHANNEL_NAME}**!")
    
    player = get_player(ctx.author.id)
    world = get_current_world(player['level'])
    
    # Rola o dado
    roll = roll_dice()
    luck = get_luck_info(roll)
    
    # Texto narrativo inicial
    explore_text = random.choice(world['explore_texts'])
    
    embed = discord.Embed(
        title=f"{world['emoji']} Explorando {world['name']}",
        description=explore_text,
        color=discord.Color.blue()
    )
    embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    # Determina o evento baseado no dado
    if roll == 1:  # Desastre
        xp_loss = random.randint(30, 50)
        result = remove_xp(ctx.author.id, xp_loss)
        
        disasters = [
            "Você pisa em um terreno instável.\nO chão cede sob seus pés!",
            "Uma armadilha escondida se ativa!\nVocê escapa, mas paga o preço...",
            "Um desmoronamento quase te esmaga!\nVocê se fere gravemente..."
        ]
        
        embed.add_field(
            name="💀 Desastre!",
            value=random.choice(disasters) + f"\n\n❌ **−{xp_loss} XP**",
            inline=False
        )
        
        if result == 'reset':
            embed.add_field(
                name="🌑 Reset Completo",
                value="Seu poder se esvai completamente...\nVocê desperta novamente nos Campos Iniciais.\n\n*Sua jornada recomeça.*",
                inline=False
            )
            embed.color = discord.Color.dark_red()
    
    elif roll == 2:  # Muito azar
        xp_loss = random.randint(15, 30)
        remove_xp(ctx.author.id, xp_loss)
        
        embed.add_field(
            name="☠️ Muito Azar",
            value=f"Você tropeça e cai em um buraco!\nFerimentos leves.\n\n❌ **−{xp_loss} XP**",
            inline=False
        )
        embed.color = discord.Color.red()
    
    elif roll in [3, 4]:  # Azar/Ruim
        embed.add_field(
            name="😵 Nada Encontrado",
            value="Você procura, mas não encontra nada de útil...",
            inline=False
        )
        embed.color = discord.Color.light_grey()
    
    elif roll == 5:  # Neutro - recurso básico
        resource = random.choice(world['resources'])
        player['inventory'].append(resource)
        save_data()
        
        embed.add_field(
            name="😶 Recurso Encontrado",
            value=f"Você encontra algo.\n\n📦 **{resource}**",
            inline=False
        )
        embed.color = discord.Color.greyple()
    
    elif roll in [6, 7]:  # Bom/Sorte - XP e recurso
        xp_gain = random.randint(15, 30)
        resource = random.choice(world['resources'])
        player['inventory'].append(resource)
        leveled = add_xp(ctx.author.id, xp_gain)
        
        embed.add_field(
            name="🙂 Descoberta!",
            value=f"Você encontra algo interessante!\n\n📦 **{resource}**\n⭐ **+{xp_gain} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(
                name="🆙 Level Up!",
                value=f"⭐ Você sente seu poder crescer.\nUm novo caminho se abre no horizonte...\n\n**Nível {player['level']}**",
                inline=False
            )
            embed.color = discord.Color.gold()
        else:
            embed.color = discord.Color.green()
    
    elif roll == 8:  # Muita sorte - baú
        xp_gain = random.randint(30, 50)
        resources = random.sample(world['resources'], min(2, len(world['resources'])))
        for res in resources:
            player['inventory'].append(res)
        leveled = add_xp(ctx.author.id, xp_gain)
        
        items_text = "\n".join([f"• **{r}**" for r in resources])
        
        embed.add_field(
            name="🍀 Baú Descoberto!",
            value=f"Um baú antigo jaz esquecido...\n\n🎁 **Conteúdo:**\n{items_text}\n⭐ **+{xp_gain} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.green()
    
    elif roll == 9:  # Sorte extrema - item raro
        item_type = random.choice(['weapons', 'armor'])
        rarity_roll = random.randint(1, 100)
        
        if rarity_roll <= 50:
            rarity = 'Raro'
        elif rarity_roll <= 80:
            rarity = 'Épico'
        else:
            rarity = 'Lendário'
        
        items = [i for i in ITEMS_POOL[item_type] if i['rarity'] == rarity]
        item = random.choice(items) if items else random.choice(ITEMS_POOL[item_type])
        
        player['inventory'].append(item['name'])
        xp_gain = random.randint(40, 70)
        leveled = add_xp(ctx.author.id, xp_gain)
        
        rarity_info = RARITIES[item['rarity']]
        
        embed.add_field(
            name="✨ Descoberta Épica!",
            value=f"Uma luz brilha entre as sombras...\n\n{rarity_info['emoji']} **{item['name']}** ({item['rarity']})\n⭐ **+{xp_gain} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = rarity_info['color']
    
    else:  # roll == 10 - Lendário
        item_type = random.choice(['weapons', 'armor'])
        legendary_items = [i for i in ITEMS_POOL[item_type] if i['rarity'] == 'Lendário']
        item = random.choice(legendary_items)
        
        player['inventory'].append(item['name'])
        xp_gain = random.randint(80, 150)
        leveled = add_xp(ctx.author.id, xp_gain)
        
        embed.add_field(
            name="🌟 EVENTO LENDÁRIO!",
            value=f"O mundo estremece!\nUma energia divina emana do solo...\n\n🟡 **{item['name']}** (Lendário)\n⭐ **+{xp_gain} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.gold()
    
    await ctx.send(embed=embed)
    
    # Verifica se deve aparecer boss
    boss_levels = [9, 19, 29, 39, 49, 59]
    if player['level'] in boss_levels:
        await asyncio.sleep(2)
        
        boss_world_level = player['level'] - (player['level'] % 10) + 1
        boss_world = WORLDS.get(boss_world_level)
        
        if boss_world and boss_world['boss']['name'] not in player['boss_defeated']:
            boss_embed = discord.Embed(
                title="⚠️ BOSS APARECEU!",
                description=f"Uma presença poderosa bloqueia seu caminho...\n\n**{boss_world['boss']['name']}** emergiu das sombras!",
                color=discord.Color.dark_red()
            )
            boss_embed.add_field(
                name="💀 Desafio",
                value=f"Use `!boss` para enfrentá-lo!\n\n*Você precisa derrotá-lo para avançar.*",
                inline=False
            )
            await ctx.send(embed=boss_embed)

# ============================================================
# COMANDOS - COMBATE
# ============================================================

@bot.command(name='cacar', aliases=['hunt', 'caçar', 'lutar'])
async def cacar(ctx):
    """Caça monstros no mundo atual"""
    if ctx.channel.name != BETA_CHANNEL_NAME:
        return await ctx.send(f"❌ Use este comando no canal **#{BETA_CHANNEL_NAME}**!")
    
    player = get_player(ctx.author.id)
    world = get_current_world(player['level'])
    
    # Escolhe monstro aleatório
    monster_name = random.choice(list(world['monsters'].keys()))
    monster = world['monsters'][monster_name]
    
    # Rola dado para combate
    roll = roll_dice()
    luck = get_luck_info(roll)
    
    embed = discord.Embed(
        title=f"⚔️ Caçando em {world['name']}",
        description=f"Você encontra um **{monster_name}**!\n\n*A batalha começa...*",
        color=discord.Color.red()
    )
    embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    if roll <= 3:  # Derrota
        xp_loss = random.randint(20, 40)
        damage = random.randint(10, 30)
        player['hp'] -= damage
        
        if player['hp'] <= 0:
            player['hp'] = player['max_hp'] // 2
            xp_loss = xp_loss * 2
        
        remove_xp(ctx.author.id, xp_loss)
        
        embed.add_field(
            name="💀 Derrota!",
            value=f"O {monster_name} te domina!\n\n❌ **−{xp_loss} XP**\n💔 **−{damage} HP**",
            inline=False
        )
        embed.color = discord.Color.dark_red()
    
    elif roll <= 5:  # Vitória difícil
        xp_gain = random.randint(monster['xp'][0], monster['xp'][0] + 5)
        damage = random.randint(5, 15)
        player['hp'] -= damage
        
        leveled = add_xp(ctx.author.id, xp_gain)
        
        embed.add_field(
            name="😓 Vitória Difícil",
            value=f"Você derrota o {monster_name}, mas se fere.\n\n⭐ **+{xp_gain} XP**\n💔 **−{damage} HP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.orange()
    
    elif roll <= 7:  # Vitória normal
        xp_gain = random.randint(monster['xp'][0], monster['xp'][1])
        leveled = add_xp(ctx.author.id, xp_gain)
        
        embed.add_field(
            name="⚔️ Vitória!",
            value=f"Você derrota o {monster_name}!\n\n⭐ **+{xp_gain} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.green()
    
    else:  # Vitória perfeita (8-10)
        xp_gain = random.randint(monster['xp'][1], monster['xp'][1] + 10)
        leveled = add_xp(ctx.author.id, xp_gain)
        
        # Chance de drop
        drop_chance = roll >= 9
        dropped_item = None
        
        if drop_chance:
            resource = random.choice(world['resources'])
            player['inventory'].append(resource)
            dropped_item = resource
        
        drop_text = f"\n📦 **{dropped_item}**" if dropped_item else ""
        
        embed.add_field(
            name="✨ Vitória Perfeita!",
            value=f"Você aniquila o {monster_name} com maestria!\n\n⭐ **+{xp_gain} XP**{drop_text}",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.gold()
    
    save_data()
    await ctx.send(embed=embed)

@bot.command(name='boss')
async def enfrentar_boss(ctx):
    """Enfrenta o boss do nível atual"""
    if ctx.channel.name != BETA_CHANNEL_NAME:
        return await ctx.send(f"❌ Use este comando no canal **#{BETA_CHANNEL_NAME}**!")
    
    player = get_player(ctx.author.id)
    
    # Verifica se está no nível de boss
    boss_levels = [9, 19, 29, 39, 49, 59]
    if player['level'] not in boss_levels:
        return await ctx.send("❌ Não há boss disponível no seu nível atual!")
    
    # Pega o boss correspondente
    boss_world_level = player['level'] - (player['level'] % 10) + 1
    boss_world = WORLDS.get(boss_world_level)
    
    if not boss_world:
        return await ctx.send("❌ Erro ao encontrar boss!")
    
    boss = boss_world['boss']
    
    # Verifica se já derrotou
    if boss['name'] in player['boss_defeated']:
        return await ctx.send(f"✅ Você já derrotou **{boss['name']}**! Continue explorando.")
    
    # Rola dado
    roll = roll_dice()
    luck = get_luck_info(roll)
    
    embed = discord.Embed(
        title=f"👹 BATALHA DE BOSS",
        description=f"**{boss['name']}** se ergue diante de você!\n\n*Esta é uma batalha lendária...*",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="💀 Boss", value=boss['name'], inline=True)
    embed.add_field(name="❤️ HP", value=f"`{boss['hp']}`", inline=True)
    embed.add_field(name="⚔️ ATK", value=f"`{boss['atk']}`", inline=True)
    embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    if roll <= 4:  # Derrota crítica
        xp_loss = random.randint(100, 200)
        result = remove_xp(ctx.author.id, xp_loss)
        
        embed.add_field(
            name="💀 Derrota Esmagadora!",
            value=f"O {boss['name']} te derrota!\n\n*{boss_world['name'][2:]} rejeita sua presença...*\n\n❌ **−{xp_loss} XP**",
            inline=False
        )
        
        if result == 'reset':
            embed.add_field(
                name="🌑 Reset Completo",
                value="Seu poder se esvai completamente...\nVocê desperta novamente nos Campos Iniciais.",
                inline=False
            )
        
        embed.color = discord.Color.dark_red()
    
    elif roll <= 6:  # Empate/quase
        xp_loss = random.randint(50, 80)
        remove_xp(ctx.author.id, xp_loss)
        
        embed.add_field(
            name="😰 Batalha Intensa",
            value=f"Vocês lutam ferozmente, mas você precisa recuar!\n\n❌ **−{xp_loss} XP**\n\n*Tente novamente quando estiver mais forte...*",
            inline=False
        )
        embed.color = discord.Color.orange()
    
    elif roll <= 8:  # Vitória difícil
        xp_gain = boss['xp']
        player['boss_defeated'].append(boss['name'])
        leveled = add_xp(ctx.author.id, xp_gain)
        
        # Desbloqueia próximo mundo
        next_world_level = boss_world_level + 10
        if next_world_level in WORLDS and next_world_level not in player['unlocked_worlds']:
            player['unlocked_worlds'].append(next_world_level)
            next_world = WORLDS[next_world_level]
            
            embed.add_field(
                name="🗺️ Novo Mundo Desbloqueado!",
                value=f"{next_world['emoji']} **{next_world['name']}**\n\n*{next_world['description']}*",
                inline=False
            )
        
        embed.add_field(
            name="🏆 VITÓRIA!",
            value=f"Após uma batalha épica, você derrota o {boss['name']}!\n\n⭐ **+{xp_gain} XP**",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.gold()
    
    else:  # Vitória perfeita (9-10)
        xp_gain = boss['xp'] + random.randint(50, 150)
        player['boss_defeated'].append(boss['name'])
        leveled = add_xp(ctx.author.id, xp_gain)
        
        # Item lendário
        item_type = random.choice(['weapons', 'armor'])
        legendary = [i for i in ITEMS_POOL[item_type] if i['rarity'] == 'Lendário']
        item = random.choice(legendary)
        player['inventory'].append(item['name'])
        
        # Desbloqueia próximo mundo
        next_world_level = boss_world_level + 10
        if next_world_level in WORLDS and next_world_level not in player['unlocked_worlds']:
            player['unlocked_worlds'].append(next_world_level)
            next_world = WORLDS[next_world_level]
            
            embed.add_field(
                name="🗺️ Novo Mundo Desbloqueado!",
                value=f"{next_world['emoji']} **{next_world['name']}**",
                inline=False
            )
        
        embed.add_field(
            name="🌟 VITÓRIA LENDÁRIA!",
            value=f"Você derrota o {boss['name']} com poder absoluto!\n\n⭐ **+{xp_gain} XP**\n🟡 **{item['name']}** (Lendário)",
            inline=False
        )
        
        if leveled:
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        
        embed.color = discord.Color.gold()
    
    save_data()
    await ctx.send(embed=embed)

# ============================================================
# COMANDOS - COLETA
# ============================================================

@bot.command(name='coletar', aliases=['collect', 'gather'])
async def coletar(ctx):
    """Coleta recursos do mundo atual"""
    if ctx.channel.name != BETA_CHANNEL_NAME:
        return await ctx.send(f"❌ Use este comando no canal **#{BETA_CHANNEL_NAME}**!")
    
    player = get_player(ctx.author.id)
    world = get_current_world(player['level'])
    
    roll = roll_dice()
    luck = get_luck_info(roll)
    
    embed = discord.Embed(
        title=f"⛏️ Coletando em {world['name']}",
        description="Você procura por recursos...",
        color=discord.Color.blue()
    )
    embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)
    
    if roll <= 3:  # Falha
        embed.add_field(
            name="😔 Sem Sorte",
            value="Você não encontra nada útil...",
            inline=False
        )
        embed.color = discord.Color.light_grey()
    
    elif roll <= 6:  # 1 recurso
        resource = random.choice(world['resources'])
        player['inventory'].append(resource)
        
        embed.add_field(
            name="📦 Recurso Coletado",
            value=f"**{resource}**",
            inline=False
        )
        embed.color = discord.Color.green()
    
    elif roll <= 8:  # 2 recursos
        resources = [random.choice(world['resources']) for _ in range(2)]
        for res in resources:
            player['inventory'].append(res)
        
        items_text = "\n".join([f"• **{r}**" for r in resources])
        
        embed.add_field(
            name="🍀 Boa Coleta!",
            value=items_text,
            inline=False
        )
        embed.color = discord.Color.green()
    
    else:  # 9-10: 3+ recursos
        count = 3 if roll == 9 else 4
        resources = [random.choice(world['resources']) for _ in range(count)]
        for res in resources:
            player['inventory'].append(res)
        
        items_text = "\n".join([f"• **{r}**" for r in resources])
        
        embed.add_field(
            name="✨ Coleta Abundante!",
            value=items_text,
            inline=False
        )
        embed.color = discord.Color.gold()
    
    save_data()
    await ctx.send(embed=embed)

# ============================================================
# COMANDO DE AJUDA
# ============================================================

@bot.command(name='help', aliases=['ajuda', 'comandos'])
async def help_command(ctx):
    """Mostra todos os comandos disponíveis"""
    
    embed = discord.Embed(
        title="📖 WORLD CSI - Guia de Comandos",
        description="Bem-vindo ao WORLD CSI! Aqui estão todos os comandos:",
        color=discord.Color.blue()
    )
    
    # Personagens
    embed.add_field(
        name="👤 Sistema de Personagens",
        value="""
`!ficha` - Criar novo personagem
`!personagens` - Ver seus personagens
`!char <nome>` - Trocar personagem ativo
`!deletar_personagem <nome>` - Deletar personagem

💡 **Como usar:** Após criar com `!ficha`, use o comando personalizado que você definiu seguido de `:` para falar como o personagem!
Exemplo: `arthur: Olá a todos!`
        """,
        inline=False
    )
    
    # Perfil
    embed.add_field(
        name="📊 Perfil & Status",
        value="""
`!perfil` - Ver seu status
`!inventario` - Ver inventário
`!xp` - Ver XP atual
        """,
        inline=False
    )
    
    # Exploração (apenas em mundo-beta)
    embed.add_field(
        name=f"🗺️ Exploração (Canal #{BETA_CHANNEL_NAME})",
        value="""
`!explorar` - Explorar o mundo
`!caçar` - Caçar monstros
`!coletar` - Coletar recursos
`!boss` - Enfrentar boss

💡 **Modo Natural:** Você também pode usar:
• "eu vou explorar" → explora
• "vou caçar" → caça
• "vou coletar" → coleta
        """,
        inline=False
    )
    
    # Sistema
    embed.add_field(
        name="🎲 Sistema de Sorte",
        value="""
Todas as ações usam um dado de 1 a 10:
`1-2` 💀 Azar (perde XP/HP)
`3-4` 😐 Ruim (pouco/nada)
`5-6` 🙂 Bom (recompensa básica)
`7-8` 🍀 Sorte (recompensa extra)
`9-10` ✨ Lenda (itens raros/épicos)
        """,
        inline=False
    )
    
    embed.set_footer(text="Use !perfil para começar sua jornada!")
    await ctx.send(embed=embed)

# ============================================================
# COMANDO XP
# ============================================================

@bot.command(name='xp')
async def mostrar_xp(ctx):
    """Mostra XP detalhado"""
    player = get_player(ctx.author.id)
    xp_needed = calculate_xp_needed(player['level'])
    progress = (player['xp'] / xp_needed) * 100
    
    # Barra de progresso
    bar_length = 20
    filled = int((progress / 100) * bar_length)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    embed = discord.Embed(
        title="✨ Experiência",
        color=discord.Color.blue()
    )
    embed.add_field(name="⭐ Nível", value=f"`{player['level']}`", inline=True)
    embed.add_field(name="📊 XP", value=f"`{player['xp']}/{xp_needed}`", inline=True)
    embed.add_field(name="📈 Progresso", value=f"`{progress:.1f}%`", inline=True)
    embed.add_field(name="━━━━━━━━━━", value=f"`{bar}`", inline=False)
    
    # Próximos níveis
    next_levels = ""
    for i in range(1, 4):
        next_lvl = player['level'] + i
        if next_lvl <= 60:
            next_xp = calculate_xp_needed(next_lvl)
            next_levels += f"Nível {next_lvl}: `{next_xp} XP`\n"
    
    if next_levels:
        embed.add_field(name="🎯 Próximos Níveis", value=next_levels, inline=False)
    
    await ctx.send(embed=embed)

# ============================================================
# EXECUTAR BOT
# ============================================================

if __name__ == '__main__':
    print("🎮 Iniciando WORLD CSI Bot...")
    print("📝 Certifique-se de ter um arquivo .env com:")
    print("   DISCORD_TOKEN=seu_token_aqui")
    print()
    
    # Carrega token
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ Token não encontrado!")
        print("Crie um arquivo .env com: DISCORD_TOKEN=seu_token")
        exit(1)
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
