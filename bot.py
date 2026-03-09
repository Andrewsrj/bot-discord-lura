import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.navegador import reiniciar_servidor
from discord import FFmpegPCMAudio
from yt_dlp import YoutubeDL
import asyncio
import random
import requests
from bs4 import BeautifulSoup
from collections import defaultdict


# =====================================================
#   CARREGAR VARIAVEIS DE AMBIENTE
# =====================================================
load_dotenv()

ID_CHANNEL = int(os.getenv("ID_CHANNEL"))
TOKEN = os.getenv("DISCORD_TOKEN")
URL = os.getenv("URL")
AUDIO_CACHE_DIR = "audio_cache"
AUDIO_FILENAME = "chuva.mp3"
BASE_URL = "https://www.myinstants.com"
MIN_DISCORD_PY_VOICE_VERSION = (2, 6, 0)


# =====================================================
#   CONFIGURACAO DO BOT
# =====================================================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)
guild_voice_locks = defaultdict(asyncio.Lock)


# =====================================================
#   EVENTO DE INICIALIZACAO
# =====================================================
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    print("Pronto para receber comandos.")
    dependency_issue = get_voice_dependency_issue()
    if dependency_issue:
        print(f"[Voice] {dependency_issue}")


# =====================================================
#   LIMITE: o bot so responde no canal configurado
# =====================================================
@bot.check
async def canal_autorizado(ctx):
    return ctx.channel.id == ID_CHANNEL


# =====================================================
#   AUXILIARES DE VOZ
# =====================================================
def channel_has_human_member(channel):
    return any(not member.bot for member in channel.members)


def get_discord_version_tuple():
    version_info = getattr(discord, "version_info", None)
    if version_info is not None:
        return (version_info.major, version_info.minor, version_info.micro)

    parts = []
    for raw_part in discord.__version__.split("."):
        digits = "".join(char for char in raw_part if char.isdigit())
        if not digits:
            break
        parts.append(int(digits))
        if len(parts) == 3:
            break

    while len(parts) < 3:
        parts.append(0)

    return tuple(parts)


def is_voice_library_compatible():
    return get_discord_version_tuple() >= MIN_DISCORD_PY_VOICE_VERSION


def get_voice_dependency_issue():
    if is_voice_library_compatible():
        return None

    return (
        f"discord.py {discord.__version__} tem um bug conhecido de voz que pode gerar "
        "o erro 4006. Atualize para discord.py[voice]>=2.6.0 no mesmo Python usado "
        "para executar o bot."
    )


def select_target_voice_channel(ctx):
    # Prioriza o canal do autor se tiver pelo menos 1 pessoa real.
    if ctx.author.voice and ctx.author.voice.channel:
        if channel_has_human_member(ctx.author.voice.channel):
            return ctx.author.voice.channel

    # Caso contrario, usa o primeiro canal ocupado por pessoa real.
    return next(
        (channel for channel in ctx.guild.voice_channels if channel_has_human_member(channel)),
        None,
    )


async def disconnect_voice_client(voice_client):
    if not voice_client:
        return

    try:
        if voice_client.is_playing():
            voice_client.stop()
        if voice_client.is_connected():
            await voice_client.disconnect()
    except Exception as error:
        print(f"[Voice] Erro ao desconectar: {error}")


async def connect_voice_safely(ctx, channel):
    voice_client = ctx.guild.voice_client

    if voice_client and voice_client.is_connected() and voice_client.channel == channel:
        return voice_client

    if voice_client and voice_client.is_connected():
        try:
            await voice_client.move_to(channel, timeout=15)
            current = ctx.guild.voice_client
            if current and current.is_connected() and current.channel == channel:
                return current
        except Exception as error:
            print(f"[Voice] Erro ao mover canal: {error}")
            await disconnect_voice_client(voice_client)
            await asyncio.sleep(1)

    for attempt in range(3):
        try:
            return await channel.connect(timeout=15, reconnect=True, self_deaf=True)
        except Exception as error:
            print(f"[Voice] Erro ao conectar (tentativa {attempt + 1}/3): {error}")
            await asyncio.sleep(2 + attempt)

    return None


async def tocar_audio_em_canal(ctx, caminho, titulo=None):
    dependency_issue = get_voice_dependency_issue()
    if dependency_issue:
        await ctx.send(dependency_issue)
        return

    channel = select_target_voice_channel(ctx)
    if not channel:
        await ctx.send("Nenhum canal de voz com pessoas foi encontrado.")
        return

    async with guild_voice_locks[ctx.guild.id]:
        voice_client = await connect_voice_safely(ctx, channel)
        if not voice_client:
            await ctx.send("Nao consegui conectar ao canal de voz.")
            return

        if titulo:
            await ctx.send(f"Tocando: **{titulo}** no canal `{channel.name}`")
        else:
            await ctx.send(f"Tocando no canal de voz: `{channel.name}`")

        finished = asyncio.Event()

        def after_playback(error):
            if error:
                print(f"[Voice] Erro durante reproducao: {error}")
            bot.loop.call_soon_threadsafe(finished.set)

        try:
            try:
                source = FFmpegPCMAudio(caminho)
            except Exception:
                source = FFmpegPCMAudio(caminho, executable="C:/ffmpeg/bin/ffmpeg.exe")

            voice_client.play(source, after=after_playback)
            await finished.wait()
        except Exception as error:
            print(f"[Voice] Falha ao tocar audio: {error}")
            await ctx.send("Erro ao reproduzir o audio.")
        finally:
            await disconnect_voice_client(voice_client)


# =====================================================
#   PEGAR AUDIO ALEATORIO DO MYINSTANTS
# =====================================================
async def pegar_audio_aleatorio_myinstants():
    lista_url = f"{BASE_URL}/pt/index/br/"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(lista_url, headers=headers, timeout=10)
    if resp.status_code != 200:
        print("Erro ao baixar pagina de lista:", resp.status_code)
        return None, None

    soup = BeautifulSoup(resp.text, "html.parser")

    links = soup.select("a[href^='/pt/instant/']")
    instants = []
    vistos = set()

    for a in links:
        href = a.get("href")
        if href and href.startswith("/pt/instant/") and href not in vistos:
            instants.append(a)
            vistos.add(href)

    if not instants:
        return None, None

    escolhido = random.choice(instants)
    link_pagina = BASE_URL + escolhido["href"]
    titulo = escolhido.get_text(strip=True)

    # Abrir pagina do audio
    resp_audio = requests.get(link_pagina, headers=headers, timeout=10)
    if resp_audio.status_code != 200:
        return None, None

    soup_audio = BeautifulSoup(resp_audio.text, "html.parser")

    # 1 - Procurar link "Baixar MP3"
    for a in soup_audio.find_all("a", href=True):
        texto = a.get_text(strip=True)
        if "Baixar MP3" in texto:
            href_mp3 = a["href"]
            mp3_url = href_mp3 if href_mp3.startswith("http") else BASE_URL + href_mp3
            return mp3_url, titulo

    # 2 - Procurar player dentro do iframe
    iframe = soup_audio.find("iframe", src=True)
    if iframe:
        embed_url = iframe["src"]
        if embed_url.startswith("//"):
            embed_url = "https:" + embed_url
        elif embed_url.startswith("/"):
            embed_url = BASE_URL + embed_url

        resp_embed = requests.get(embed_url, headers=headers, timeout=10)
        if resp_embed.status_code == 200:
            soup_embed = BeautifulSoup(resp_embed.text, "html.parser")
            source_tag = soup_embed.select_one("audio source")
            if source_tag and source_tag.get("src"):
                src = source_tag["src"]
                mp3_url = src if src.startswith("http") else BASE_URL + src
                return mp3_url, titulo

    print("Nao foi possivel encontrar o MP3 para:", link_pagina)
    return None, None


# Criar diretorio de cache de audio
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)


# =====================================================
#   COMANDO: !audio -> busca do MyInstants
# =====================================================
@bot.command()
async def audio(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected() and ctx.voice_client.is_playing():
        await ctx.send("Ja estou tocando em outro canal.")
        return

    usuario = ctx.author.display_name
    await ctx.send(
        f"Buscando aqui na minha base de dados um audio que represente **{usuario}**..."
    )

    mp3_url, titulo = await pegar_audio_aleatorio_myinstants()
    if not mp3_url:
        await ctx.send("Nao consegui buscar um audio aleatorio.")
        return

    caminho = os.path.join(AUDIO_CACHE_DIR, "random_temp.mp3")
    try:
        r = requests.get(mp3_url, timeout=20)
        with open(caminho, "wb") as f:
            f.write(r.content)
    except Exception:
        await ctx.send("Erro ao baixar o audio.")
        return

    await tocar_audio_em_canal(ctx, caminho, titulo)


# =====================================================
#   COMANDO: !chuva (Youtube)
# =====================================================
@bot.command()
async def chuva(ctx):
    mensagem = (
        "Chuva de arroz, rosas no buque...\n"
        "Que essa vibe boa contagie o servidor!"
    )
    url = "https://youtube.com/shorts/jvGETIIk_E0?si=Jh_5Sx6jS8YJobFX"

    caminho = os.path.join(AUDIO_CACHE_DIR, AUDIO_FILENAME)

    # Baixar se ainda nao existe
    if not os.path.exists(caminho):
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "outtmpl": caminho,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    await ctx.send(mensagem)
    await tocar_audio_em_canal(ctx, caminho, titulo="CHUVA")


# =====================================================
#   COMANDO: !reiniciar
# =====================================================
@bot.command()
@commands.cooldown(1, 600, commands.BucketType.guild)
async def reiniciar(ctx):
    usuario = ctx.author.display_name
    await ctx.send(f"{usuario} esta reiniciando o servidor...")

    if reiniciar_servidor(URL):
        await ctx.send("Servidor reiniciado com sucesso!")
    else:
        await ctx.send("Erro ao reiniciar o servidor.")


@reiniciar.error
async def reiniciar_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Calma! Este comando so pode ser usado novamente em {round(error.retry_after)} segundos."
        )


# =====================================================
#   EXECUTAR BOT
# =====================================================
if __name__ == "__main__":
    bot.run(TOKEN)
