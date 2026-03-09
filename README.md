# Bot Discord com Controle de Painel via Navegador

Este projeto e um bot de Discord que automatiza acoes em um painel web, como reiniciar um servidor, usando um Google Chrome real com login manual. Ele evita bloqueios de Cloudflare ao reutilizar uma sessao ja autenticada. O bot tambem pode entrar em canais de voz e tocar audios de videos do YouTube.

---

## Pre-requisitos

- Python 3.8+
- Google Chrome instalado
- FFmpeg instalado e adicionado ao PATH do Windows
- `pip`
- ambiente virtual Python

---

## Instalacao

1. Clone o repositorio:

```bash
git clone https://github.com/Andrewsrj/bot-discord-lura
cd bot-discord-lura
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# ou source venv/bin/activate   # Linux/macOS
```

3. Instale as dependencias:

```bash
venv\Scripts\python -m pip install -r requirements.txt
```

4. Instale o FFmpeg e adicione ao PATH do Windows:

- Baixe em: https://www.gyan.dev/ffmpeg/builds/
- Extraia o conteudo em `C:\ffmpeg`
- Adicione `C:\ffmpeg\bin` ao PATH do Windows
- Feche e abra o terminal novamente para validar com `ffmpeg -version`

---

## Configure seu `.env`

Crie um arquivo `.env` com o seguinte conteudo:

```env
DISCORD_TOKEN=seu_token_discord_aqui
URL=https://painel.lurahosting.com.br/server/<id_do_servidor>/
ID_CHANNEL=<id_do_canal>
```

---

## Configurar o Chrome para depuracao

Crie um atalho no Windows com o seguinte destino:

```text
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-session"
```

Esse comando vai:

- Abrir o Chrome em modo de depuracao na porta `9222`
- Usar um perfil exclusivo, mantendo sessoes, cookies e logins
- Permitir que o bot controle essa sessao com Selenium

Passos:

1. Feche qualquer instancia do Chrome antes.
2. Use o atalho para abrir o Chrome.
3. Faca login no painel desejado e deixe a aba aberta.

---

## Rodar o bot

Com o navegador aberto e logado, execute:

```bash
venv\Scripts\python bot.py
```

Voce vera algo como:

```text
Bot conectado como PainelBot#1234
Pronto para receber comandos.
```

---

## Comandos disponiveis

- `!chuva`: entra em um canal de voz ocupado e toca um audio divertido
- `!audio`: busca um audio aleatorio no MyInstants e toca no canal de voz
- `!reiniciar`: clica no botao de reiniciar do painel, limitado a cada 10 minutos

---

## Observacoes

- O Chrome deve ser iniciado com `--remote-debugging-port` sempre que quiser usar o bot
- O Selenium nao conseguira automatizar logins protegidos por captcha ou Cloudflare
- FFmpeg deve estar instalado e funcionando no PATH para que o bot possa tocar audios
- O bot gerencia cache de audio para evitar downloads repetidos
- Este metodo nao usa `headless` para permitir controle humano inicial

---

## Solucao para erro 4006 ao entrar no canal de voz

Se o traceback mostrar `discord.errors.ConnectionClosed` com codigo `4006`, a causa mais comum e usar `discord.py 2.5.2` ou outra versao antiga da stack de voz. Os mantenedores do `discord.py` corrigiram esse problema em junho de 2025.

Atualize a biblioteca no mesmo interpretador que executa o bot:

```bash
python -m pip install --upgrade "discord.py[voice]>=2.6.0,<3.0"
python -m pip install -r requirements.txt
```

Se o caminho do traceback apontar para `AppData\Local\Programs\Python\Python311\Lib\site-packages`, o bot esta rodando no Python global e nao no `venv` do projeto.
