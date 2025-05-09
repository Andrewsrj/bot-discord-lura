import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.navegador import iniciar_navegador, reiniciar_servidor
from discord import FFmpegPCMAudio
from yt_dlp import YoutubeDL
import asyncio

load_dotenv()
# CANAL_ID = 123456789012345678  # Substitua pelo ID do canal desejado
ID_CHANNEL = int(os.getenv("ID_CHANNEL"))
TOKEN = os.getenv("DISCORD_TOKEN")
URL = os.getenv("URL")
AUDIO_CACHE_DIR = "audio_cache"
AUDIO_FILENAME = "chuva.mp3"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    if iniciar_navegador():  # ← inicia o Chrome assim que o bot sobe (Faça o login manualmente)
        print("✅ Navegador iniciado com sucesso.")
    else:
        print("❌ Erro ao conectar ao navegador.")
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


# Garante que a pasta de cache exista
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

async def tocar_audio_em_canal_ocupado(ctx, url, mensagem):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.send("❌ Já estou tocando em outro canal.")
        return

    canal_com_membros = next((c for c in ctx.guild.voice_channels if c.members), None)

    if canal_com_membros is None:
        await ctx.send("❌ Nenhum canal de voz ocupado foi encontrado.")
        return

    voice_client = await canal_com_membros.connect()
    await ctx.send(f"🎵 Tocando no canal de voz: {canal_com_membros.name}")

    audio_path = os.path.join(AUDIO_CACHE_DIR, AUDIO_FILENAME)

    if not os.path.exists(audio_path):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': audio_path,
            'noplaylist': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    # Primeira tentativa (usando FFmpeg do PATH)
    try:
        source = FFmpegPCMAudio(audio_path)
        voice_client.play(source)
        await ctx.send(mensagem)
    except Exception as e1:
        # Segunda tentativa (usando caminho absoluto)
        try:
            source = FFmpegPCMAudio(audio_path, executable="C:/ffmpeg/bin/ffmpeg.exe")
            voice_client.play(source)
            await ctx.send(mensagem)
        except Exception as e2:
            await ctx.send("❌ Erro ao tentar rodar o FFmpeg. Verifique se está instalado e configurado corretamente.")
            print(f"Erro 1: {e1}")
            print(f"Erro 2: {e2}")
            await voice_client.disconnect()
            return

    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()

@bot.command()
async def chuva(ctx):
    mensagem = (
        "🌧️🎶 *Chuva de arroz, rosas no buquê...* 💐🎶\n"
        "✨ Que essa vibe boa contagie o servidor! ✨\n"
        "💍💒💃🕺"
    )
    await tocar_audio_em_canal_ocupado(ctx, "https://youtube.com/shorts/jvGETIIk_E0?si=Jh_5Sx6jS8YJobFX", mensagem)

bot.run(TOKEN)