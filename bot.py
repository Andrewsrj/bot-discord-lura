import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.navegador import iniciar_navegador, reiniciar_servidor

# CANAL_ID = 123456789012345678  # Substitua pelo ID do canal desejado
ID_CHANNEL = os.getenv("ID_CHANNEL")

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

@bot.check
async def canal_autorizado(ctx):
    return ctx.channel.id == ID_CHANNEL

@bot.command()
@commands.cooldown(1, 600, commands.BucketType.guild)  # 1 uso a cada 600 segundos (10 minutos) por servidor
async def reiniciar(ctx):
    usuario = ctx.author.display_name
    await ctx.send(f"🔄 {usuario} está reiniciando o servidor...")

    resposta_save = reiniciar_servidor(URL)
    if resposta_save:
        await ctx.send("✅ Servidor reiniciado com sucesso!")
    else:
        await ctx.send("❌ Erro ao reiniciar o servidor.")

@reiniciar.error
async def reiniciar_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Calma! Este comando só pode ser usado novamente em {round(error.retry_after)} segundos.")

@bot.command()
async def chuva(ctx):
    mensagem = (
        "🌧️🎶 *Chuva de arroz, rosas no buquê...* 💐🎶\n"
        "✨ Que essa vibe boa contagie o servidor! ✨\n"
        "💍💒💃🕺"
    )
    await ctx.send(mensagem)

bot.run(TOKEN)