import os
import json
import urllib.request
from datetime import datetime, timezone

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

API_URL = "https://api.midvash.com/v1"

VERSICULOS = [
    ("João", "john", 3, 16),
    ("Salmos", "psalms", 23, 1),
    ("Filipenses", "philippians", 4, 13),
    ("Jeremias", "jeremiah", 29, 11),
    ("Provérbios", "proverbs", 3, 5),
    ("Isaías", "isaiah", 41, 10),
    ("Romanos", "romans", 8, 28),
    ("Salmos", "psalms", 46, 1),
    ("Josué", "joshua", 1, 9),
    ("Mateus", "matthew", 11, 28),
    ("Salmos", "psalms", 121, 1),
    ("Isaías", "isaiah", 43, 2),
    ("2 Timóteo", "2timothy", 1, 7),
    ("Salmos", "psalms", 37, 5),
    ("Mateus", "matthew", 6, 33),
    ("Romanos", "romans", 12, 12),
    ("Salmos", "psalms", 34, 18),
    ("Hebreus", "hebrews", 11, 1),
    ("1 Pedro", "1peter", 5, 7),
    ("Salmos", "psalms", 91, 1),
]


def pegar_versiculo(versao, livro, capitulo, versiculo):

    url = (
        f"{API_URL}/{versao}/"
        f"{livro}/{capitulo}/{versiculo}"
    )

    requisicao = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "Devocionalico/1.0",
            "Accept": "application/json"
        }
    )

    with urllib.request.urlopen(
        requisicao,
        timeout=30
    ) as resposta:

        dados = json.loads(
            resposta.read().decode("utf-8")
        )

    return dados["data"]["text"]


def escolher_versiculo():

    agora = datetime.now(timezone.utc)

    dia = agora.timetuple().tm_yday
    hora = agora.hour

    if hora < 13:
        periodo = 0
    elif hora < 19:
        periodo = 1
    else:
        periodo = 2

    indice = (dia * 3 + periodo) % len(VERSICULOS)

    return VERSICULOS[indice]


def enviar_discord(mensagem):

    url = (
        f"https://discord.com/api/v10/"
        f"channels/{CHANNEL_ID}/messages"
    )

    dados = json.dumps({
        "content": mensagem
    }).encode("utf-8")

    requisicao = urllib.request.Request(
        url,
        data=dados,
        method="POST",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Devocionalico/1.0"
        }
    )

    with urllib.request.urlopen(
        requisicao,
        timeout=30
    ) as resposta:

        if resposta.status not in (200, 201):
            raise Exception(
                f"Discord respondeu: {resposta.status}"
            )


def main():

    nome_livro, livro_api, capitulo, versiculo = (
        escolher_versiculo()
    )

    texto_naa = pegar_versiculo(
        "naa",
        livro_api,
        capitulo,
        versiculo
    )

    texto_ara = pegar_versiculo(
        "ara",
        livro_api,
        capitulo,
        versiculo
    )

    referencia = (
        f"{nome_livro} {capitulo}:{versiculo}"
    )

    mensagem = f"""📖 **DEVOCIONALICO**

✨ **{referencia}**

📘 **NAA — Nova Almeida Atualizada**
> {texto_naa}

📜 **ARA — Almeida Revista e Atualizada**
> {texto_ara}

🙏 Que a Palavra de Deus abençoe o seu dia!

— 🤖 **Devocionalico**
"""

    enviar_discord(mensagem)


if __name__ == "__main__":
    main()
