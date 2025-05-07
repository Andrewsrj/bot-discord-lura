import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.navegador import enviar_comando_rcon
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
RCON_IP = os.getenv("IP")
RCON_PORTA = os.getenv("PORTA")
RCON_SENHA = os.getenv("RCON_PASSWORD")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def reiniciar(ctx):
    await ctx.send("🔄 Salvando o servidor antes de reiniciar...")

    resposta_save = enviar_comando_rcon(RCON_IP, RCON_PORTA, RCON_SENHA, "save")
    await ctx.send(f"💾 Resposta do comando save: {resposta_save}")

    await asyncio.sleep(3)  # Aguarda 3 segundos para garantir que o save foi processado

    resposta_quit = enviar_comando_rcon(RCON_IP, RCON_PORTA, RCON_SENHA, "quit")
    await ctx.send(f"⛔ Servidor reiniciado. Resposta: {resposta_quit}")

@bot.command()
async def chuva(ctx):
    mensagem = (
        "🌧️🎶 *Chuva de arroz, rosas no buquê...* 💐🎶\n"
        "✨ Que essa vibe boa contagie o servidor! ✨\n"
        "💍💒💃🕺"
    )
    await ctx.send(mensagem)

bot.run(TOKEN)