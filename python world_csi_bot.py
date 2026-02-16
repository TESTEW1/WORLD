import discord
from discord.ext import commands
import random
import os
import sqlite3

# Configuração do Bot e Token
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- BANCO DE DADOS (Persistência) ---
def init_db():
    conn = sqlite3.connect('world_csi.db')
    c = conn.cursor()
    # Tabela de Jogadores: Nível, XP, Mundo, Local, etc.
    c.execute('''CREATE TABLE IF NOT EXISTS players 
                 (user_id INTEGER PRIMARY KEY, lv INTEGER, xp INTEGER, mundo TEXT)''')
    # Tabela de Tuppers: Nome, Foto, Prefixo
    c.execute('''CREATE TABLE IF NOT EXISTS tuppers 
                 (user_id INTEGER, prefixo TEXT, nome TEXT, foto TEXT, PRIMARY KEY(user_id, prefixo))''')
    conn.commit()
    conn.close()

init_db()

# --- SISTEMA DE TUPPER (SIMILAR AO TUPPERBOX) ---

@bot.command()
async def ficha(ctx):
    def check(m): return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("🎭 **Criação de Personagem - WORLD CSI**\nQual será o **NOME** do herói?")
    nome = (await bot.wait_for('message', check=check)).content

    await ctx.send(f"📸 Envie a **URL da imagem** de perfil para {nome}:")
    foto = (await bot.wait_for('message', check=check)).content

    await ctx.send(f"⌨️ Qual o **PREFIXO** para usar este personagem? (Exemplo: `>>` ou `.` )")
    prefixo = (await bot.wait_for('message', check=check)).content

    conn = sqlite3.connect('world_csi.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO tuppers VALUES (?, ?, ?, ?)", (ctx.author.id, prefixo, nome, foto))
    # Inicializa jogador se for novo
    c.execute("INSERT OR IGNORE INTO players VALUES (?, ?, ?, ?)", (ctx.author.id, 1, 0, "Campos Iniciais"))
    conn.commit()
    conn.close()

    await ctx.send(f"✅ **{nome}** registrado! Para falar como ele, digite: `{prefixo} sua mensagem`")

# --- LÓGICA DE MENSAGENS E WEBHOOK ---

@bot.event
async def on_message(message):
    if message.author.bot: return

    # Checa se a mensagem começa com um prefixo de Tupper registrado
    conn = sqlite3.connect('world_csi.db')
    c = conn.cursor()
    c.execute("SELECT nome, foto, prefixo FROM tuppers WHERE user_id = ?", (message.author.id,))
    user_tuppers = c.fetchall()
    conn.close()

    for nome, foto, prefixo in user_tuppers:
        if message.content.startswith(prefixo):
            texto = message.content[len(prefixo):].strip()
            await message.delete()
            
            webhooks = await message.channel.webhooks()
            webhook = next((wh for wh in webhooks if wh.name == "CSI_System"), None)
            if not webhook:
                webhook = await message.channel.create_webhook(name="CSI_System")
            
            await webhook.send(content=texto, username=nome, avatar_url=foto)
            return

    await bot.process_commands(message)

# --- COMANDO EXPLORAR E SISTEMA DE RISCO ---

@bot.command()
async def explorar(ctx):
    conn = sqlite3.connect('world_csi.db')
    c = conn.cursor()
    c.execute("SELECT lv, xp, mundo FROM players WHERE user_id = ?", (ctx.author.id,))
    row = c.fetchone()

    if not row:
        return await ctx.send("❌ Você ainda não tem uma ficha! Use `!ficha`.")

    lv, xp, mundo = row
    dado = random.randint(1, 10)
    
    # Lógica de Ganho/Perda baseada no seu sistema
    recompensa_xp = 0
    desc = ""

    if dado == 1:
        recompensa_xp = -50
        desc = "💀 **DESASTRE!** Você caiu em uma armadilha de espinhos e perdeu muito sangue (e XP)."
    elif dado <= 3:
        recompensa_xp = -20
        desc = "☠️ **AZAR!** Um bando de Slimes te emboscou. Você fugiu, mas deixou sua experiência para trás."
    elif dado <= 5:
        recompensa_xp = 10
        desc = "😐 **RUIM...** Você explorou as bordas do mapa, mas não encontrou nada interessante."
    elif dado <= 8:
        recompensa_xp = 35
        desc = "🍀 **SORTE!** Você encontrou um altar antigo e sentiu uma energia renovadora."
    else:
        recompensa_xp = 80
        desc = "✨ **EXTREMO!** Você descobriu uma passagem secreta com relíquias do passado!"

    novo_xp = xp + recompensa_xp
    
    # SISTEMA DE RESET (Morte)
    if novo_xp < 0:
        c.execute("UPDATE players SET lv = 1, xp = 0, mundo = 'Campos Iniciais' WHERE user_id = ?", (ctx.author.id,))
        conn.commit()
        return await ctx.send(f"🌑 **MORTE TOTAL.** {ctx.author.mention}, seu XP chegou a zero. Você perdeu suas memórias e voltou ao Nível 1.")

    # SISTEMA DE BOSS (Barreira de Nível)
    xp_prox_nivel = (lv ** 2) * 25
    if novo_xp >= xp_prox_nivel:
        await ctx.send(f"⚠️ **BOSS DETECTADO!** {ctx.author.mention}, uma aura massiva bloqueia seu caminho. Derrote o Boss do mundo **{mundo}** para avançar!")
        # Aqui você pode travar o XP até ele usar !boss
        novo_xp = xp_prox_nivel - 1 

    c.execute("UPDATE players SET xp = ? WHERE user_id = ?", (novo_xp, ctx.author.id))
    conn.commit()
    conn.close()

    embed = discord.Embed(title=f"🧭 Explorando {mundo}...", description=desc, color=0x7289da)
    embed.add_field(name="🎲 Dado", value=f"**{dado}**")
    embed.add_field(name="XP", value=f"{'+' if recompensa_xp > 0 else ''}{recompensa_xp}")
    embed.set_footer(text=f"Total: {novo_xp} XP | Nível: {lv}")
    await ctx.send(embed=embed)

@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(title="📜 Manual do WORLD CSI", color=0x00ff00)
    embed.add_field(name="!ficha", value="Cria seu personagem (Nome, Foto, Prefixo).", inline=False)
    embed.add_field(name="!explorar", value="Aventure-se pelo mapa. Cuidado: falhas retiram XP!", inline=False)
    embed.add_field(name="!perfil", value="Veja seu nível e XP atual.", inline=False)
    embed.set_footer(text="Dica: Use seu prefixo para falar como o personagem!")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("ERRO: Variável TOKEN não encontrada!")
