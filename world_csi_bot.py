import discord
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # ESSENCIAL PARA LER COMANDOS

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'🟢 SUCESSO! O bot logou como: {client.user}')

try:
    if TOKEN:
        print("📡 Tentando conectar ao Discord...")
        client.run(TOKEN)
    else:
        print("❌ ERRO: A variável TOKEN está vazia no Railway!")
except discord.errors.LoginFailure:
    print("❌ ERRO: O Token fornecido é inválido. Tente dar Reset no Token no Developer Portal.")
except Exception as e:
    print(f"❌ OCORREU UM ERRO INESPERADO: {e}")
