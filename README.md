# 🤖 Bot Discord com Controle de Painel via Navegador

Este projeto é um bot de Discord que automatiza ações em um painel web (como reiniciar um servidor) utilizando um navegador **Google Chrome real** com login manual. Ele evita bloqueios de Cloudflare ao se conectar a uma sessão já aberta e autenticada. Além disso, o bot agora pode entrar em canais de voz e tocar áudios de vídeos do YouTube.

---

## ✅ Pré-requisitos

- Python 3.8+
- Google Chrome instalado
- FFmpeg instalado e adicionado ao PATH do Windows
- pip + ambiente virtual

---

## 📦 Instalação

1. Clone o repositório:

```bash
git clone https://github.com/Andrewsrj/bot-discord-lura
cd bot-discord-lura
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# ou source venv/bin/activate   ← Linux/macOS
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Instale o FFmpeg e adicione ao PATH do Windows:

- Baixe em: https://www.gyan.dev/ffmpeg/builds/
- Extraia o conteúdo em `C:\ffmpeg`
- Adicione `C:\ffmpeg\bin` ao **PATH do Windows**
- Feche e abra o terminal novamente para validar com `ffmpeg -version`

---

## 🔐 Configure seu `.env`

Crie um arquivo `.env` com o seguinte conteúdo:

```env
DISCORD_TOKEN=seu_token_discord_aqui
URL=https://painel.lurahosting.com.br/server/<id_do_servidor>/
ID_CHANNEL=<id_do_canal>
```

---

## 🌐 Configurar o Chrome para depuração

### Crie um atalho no Windows com o seguinte destino:

```text
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-session"
```

> 📌 Dica: Crie uma pasta chamada `chrome-session` em `C:\` para manter seu perfil isolado.

Esse comando irá:

- Abrir o Chrome em modo de depuração (porta 9222)
- Usar um perfil exclusivo, mantendo sessões, cookies e logins
- Permitir que o bot controle essa sessão com Selenium

### Passos:

1. Feche qualquer instância do Chrome antes
2. Use o atalho para abrir o Chrome
3. Faça login no painel desejado e **deixe a aba aberta**

---

## ▶️ Rodar o bot

Com o navegador aberto e logado, execute:

```bash
python bot.py
```

Você verá algo como:

```
🤖 Bot conectado como PainelBot#1234
✅ Navegador iniciado com sucesso.
🧠 Pronto para receber comandos.
```

---

## 💬 Comandos disponíveis

- `!chuva` → Entra em um canal de voz ocupado e toca um áudio divertido, além de enviar uma mensagem com emojis
- `!reiniciar` → Clica no botão de reiniciar do painel, limitado a cada 10 minutos

---

## 🛑 Encerrando

Ao encerrar o bot, o navegador permanecerá aberto (você pode fechar manualmente ou desligar o Chrome quando quiser).

---

## 📌 Observações

- O Chrome **deve ser iniciado com `--remote-debugging-port`** sempre que quiser usar o bot
- O Selenium **não conseguirá automatizar logins protegidos por captcha/Cloudflare** — por isso usamos essa abordagem
- FFmpeg deve estar instalado e funcionando no PATH para que o bot possa tocar áudios
- O bot gerencia cache de áudio para evitar downloads repetidos
- Esse método **não usa `headless`** justamente para permitir controle humano inicial

---
