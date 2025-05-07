from rcon.source import Client

def enviar_comando_rcon(ip, porta, senha, comando):
    try:
        with Client(ip, porta, passwd=senha) as client:
            resposta = client.run(comando)
            return resposta
    except Exception as e:
        return f"Erro ao conectar via RCON: {e}"