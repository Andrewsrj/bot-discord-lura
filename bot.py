import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.navegador import iniciar_navegador, reiniciar_servidor

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
URL = os.getenv("URL")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    iniciar_navegador()  # ← inicia o Chrome assim que o bot sobe (Faça o login manualmente)
    print("🧠 Pronto para receber comandos.")

@bot.command()
async def reiniciar(ctx):
    await ctx.send("🔄 Reiniciando servidor...")

    resposta_save = reiniciar_servidor(URL)
    if resposta_save:
        await ctx.send("✅ Servidor reiniciado com sucesso!")
    else:
        await ctx.send("❌ Erro ao reiniciar o servidor.")

@bot.command()
async def chuva(ctx):
    mensagem = (
        "🌧️🎶 *Chuva de arroz, rosas no buquê...* 💐🎶\n"
        "✨ Que essa vibe boa contagie o servidor! ✨\n"
        "💍💒💃🕺"
    )
    await ctx.send(mensagem)

bot.run(TOKEN)