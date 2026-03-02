import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.navegador import iniciar_navegador, reiniciar_servidor
from discord import FFmpegPCMAudio
from yt_dlp import YoutubeDL
import asyncio
import random
import requests
from bs4 import BeautifulSoup


# =====================================================
#   CARREGAR VARIÁVEIS DE AMBIENTE
# =====================================================
load_dotenv()

ID_CHANNEL = int(os.getenv("ID_CHANNEL"))
TOKEN = os.getenv("DISCORD_TOKEN")
URL = os.getenv("URL")
AUDIO_CACHE_DIR = "audio_cache"
AUDIO_FILENAME = "chuva.mp3"
BASE_URL = "https://www.myinstants.com"


# =====================================================
#   CONFIGURAÇÃO DO BOT
# =====================================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# =====================================================
#   EVENTO DE INICIALIZAÇÃO
# =====================================================
@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    print("🧠 Pronto para receber comandos.")


# =====================================================
#   LIMITE: o bot só responde no canal configurado
# =====================================================
@bot.check
async def canal_autorizado(ctx):
    return ctx.channel.id == ID_CHANNEL


# =====================================================
#   FUNÇÃO DE CONEXÃO SEGURA AO CANAL DE VOZ
# =====================================================
async def connect_voice_safely(ctx, channel):
    vc = ctx.guild.voice_client

    # Já está no canal certo → usar a mesma conexão
    if vc and vc.is_connected() and vc.channel == channel:
        return vc

    # Está conectado em outro canal → desconectar primeiro
    if vc and vc.is_connected():
        try:
            await vc.disconnect(force=True)
        except:
            pass
        await asyncio.sleep(0.7)  # necessário para Discord limpar o estado

    # Tentar conectar com retry
    for tentativa in range(3):
        try:
            new_vc = await channel.connect(timeout=10, reconnect=True)
            return new_vc
        except Exception as e:
            print(f"[Voice] Erro ao conectar (tentativa {tentativa+1}): {e}")
            await asyncio.sleep(1.5)

    return None


# =====================================================
#   PEGAR ÁUDIO ALEATÓRIO DO MYINSTANTS
# =====================================================
async def pegar_audio_aleatorio_myinstants():
    lista_url = f"{BASE_URL}/pt/index/br/"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(lista_url, headers=headers, timeout=10)
    if resp.status_code != 200:
        print("Erro ao baixar página de lista:", resp.status_code)
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

    # Abrir página do áudio
    resp_audio = requests.get(link_pagina, headers=headers, timeout=10)
    if resp_audio.status_code != 200:
        return None, None

    soup_audio = BeautifulSoup(resp_audio.text, "html.parser")

    # 1 — Procurar link "Baixar MP3"
    for a in soup_audio.find_all("a", href=True):
        texto = a.get_text(strip=True)
        if "Baixar MP3" in texto:
            href_mp3 = a["href"]
            mp3_url = href_mp3 if href_mp3.startswith("http") else BASE_URL + href_mp3
            return mp3_url, titulo

    # 2 — Procurar player dentro do iframe
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

    print("Não foi possível encontrar o MP3 para:", link_pagina)
    return None, None


# Criar diretório de cache de áudio
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)


# =====================================================
#   FUNÇÃO PARA TOCAR ÁUDIO (GENÉRICA)
# =====================================================
async def tocar_audio_em_canal(ctx, caminho, titulo=None):
    canal_com_membros = next((c for c in ctx.guild.voice_channels if c.members), None)

    if not canal_com_membros:
        await ctx.send("❌ Nenhum canal de voz ocupado foi encontrado.")
        return

    voice_client = await connect_voice_safely(ctx, canal_com_membros)
    if not voice_client:
        await ctx.send("❌ Não consegui conectar ao canal de voz.")
        return

    if titulo:
        await ctx.send(f"🔊 **Tocando:** {titulo}\n🎵 No canal: `{canal_com_membros.name}`")
    else:
        await ctx.send(f"🎵 Tocando no canal de voz: {canal_com_membros.name}")

    # Tocar áudio com FFmpeg
    try:
        source = FFmpegPCMAudio(caminho)
        voice_client.play(source)
    except:
        try:
            source = FFmpegPCMAudio(caminho, executable="C:/ffmpeg/bin/ffmpeg.exe")
            voice_client.play(source)
        except Exception:
            await ctx.send("❌ FFmpeg não encontrado.")
            return

    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()


# =====================================================
#   COMANDO: !audio → busca do MyInstants
# =====================================================
@bot.command()
async def audio(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.send("❌ Já estou tocando em outro canal.")
        return

    usuario = ctx.author.display_name
    await ctx.send(
        f"🧠 *Buscando aqui na minha base de dados um áudio que represente* **{usuario}**..."
    )

    mp3_url, titulo = await pegar_audio_aleatorio_myinstants()
    if not mp3_url:
        await ctx.send("❌ Não consegui buscar um áudio aleatório.")
        return

    caminho = os.path.join(AUDIO_CACHE_DIR, "random_temp.mp3")
    try:
        r = requests.get(mp3_url)
        with open(caminho, "wb") as f:
            f.write(r.content)
    except:
        await ctx.send("❌ Erro ao baixar o áudio.")
        return

    await tocar_audio_em_canal(ctx, caminho, titulo)


# =====================================================
#   COMANDO: !chuva (Youtube)
# =====================================================
@bot.command()
async def chuva(ctx):
    mensagem = (
        "🌧️🎶 *Chuva de arroz, rosas no buquê...* 💐🎶\n"
        "✨ Que essa vibe boa contagie o servidor! ✨\n"
        "💍💒💃🕺"
    )
    url = "https://youtube.com/shorts/jvGETIIk_E0?si=Jh_5Sx6jS8YJobFX"

    caminho = os.path.join(AUDIO_CACHE_DIR, AUDIO_FILENAME)

    # Baixar se ainda não existe
    if not os.path.exists(caminho):
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "outtmpl": caminho,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    canal_com_membros = next((c for c in ctx.guild.voice_channels if c.members), None)
    if not canal_com_membros:
        await ctx.send("❌ Nenhum canal de voz ocupado.")
        return

    voice_client = await connect_voice_safely(ctx, canal_com_membros)
    if not voice_client:
        await ctx.send("❌ Erro ao conectar ao canal.")
        return

    await ctx.send(f"🎵 Tocando CHUVA no canal `{canal_com_membros.name}`\n{mensagem}")

    try:
        source = FFmpegPCMAudio(caminho)
        voice_client.play(source)
    except:
        await ctx.send("❌ Erro ao usar FFmpeg.")
        return

    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()


# =====================================================
#   COMANDO: !reiniciar
# =====================================================
@bot.command()
@commands.cooldown(1, 600, commands.BucketType.guild)
async def reiniciar(ctx):
    usuario = ctx.author.display_name
    await ctx.send(f"🔄 {usuario} está reiniciando o servidor...")

    if reiniciar_servidor(URL):
        await ctx.send("✅ Servidor reiniciado com sucesso!")
    else:
        await ctx.send("❌ Erro ao reiniciar o servidor.")


@reiniciar.error
async def reiniciar_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"⏳ Calma! Este comando só pode ser usado novamente em {round(error.retry_after)} segundos."
        )


# =====================================================
#   EXECUTAR BOT
# =====================================================
bot.run(TOKEN)
