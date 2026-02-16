import discord
import os
import logging

# Configuração de Logs para você ver o que acontece no painel do Railway
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")

# Configuração das "Intents" (As permissões do cérebro do bot)
intents = discord.Intents.default()
intents.message_content = True  # Permite ler comandos como !ficha
intents.members = True          # Permite ver os jogadores

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logging.info(f'🟢 SUCESSO! O bot {client.user} está online e pronto para o RPG!')
    # Muda o status do bot para "Jogando WORLD CSI"
    await client.change_presence(activity=discord.Game(name="WORLD CSI RPG"))

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith('!oi'):
        await message.channel.send(f'⚔️ Saudações, {message.author.name}! O sistema WORLD CSI está operacional.')

if __name__ == "__main__":
    if not TOKEN:
        logging.error("❌ ERRO: A variável 'TOKEN' não foi encontrada nas Settings do Railway!")
    else:
        try:
            logging.info("🚀 Iniciando conexão com o Discord...")
            client.run(TOKEN)
        except Exception as e:
            logging.error(f"❌ FALHA AO LOGAR: {e}")
