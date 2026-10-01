import os
import json
import urllib.request
from datetime import datetime, timezone

# ============================================================
# CONFIGURAÇÕES
# ============================================================

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

API_URL = "https://api.midvash.com/v1"


# ============================================================
# VERSÍCULOS
# ============================================================
# O Devocionalico escolherá automaticamente 3 referências
# diferentes ao longo do dia.
#
# Cada referência será buscada tanto na NAA quanto na ARA.

VERSICULOS = [
    ("João", "john", 3, 16),
    ("Salmos", "salmos", 23, 1),
    ("Filipenses", "filipenses", 4, 13),
    ("Jeremias", "jeremias", 29, 11),
    ("Provérbios", "proverbios", 3, 5),
    ("Isaías", "isaias", 41, 10),
    ("Romanos", "romanos", 8, 28),
    ("Salmos", "salmos", 46, 1),
    ("Josué", "josue", 1, 9),
    ("Mateus", "mateus", 11, 28),
    ("Salmos", "salmos", 121, 1),
    ("Isaías", "isaias", 43, 2),
    ("2 Timóteo", "2-timoteo", 1, 7),
    ("Salmos", "salmos", 37, 5),
    ("Mateus", "mateus", 6, 33),
    ("Romanos", "romanos", 12, 12),
    ("Salmos", "salmos", 34, 18),
    ("Hebreus", "hebreus", 11, 1),
    ("1 Pedro", "1-pedro", 5, 7),
    ("Salmos", "salmos", 91, 1),
]


# ============================================================
# BUSCAR VERSÍCULO
# ============================================================

def pegar_versiculo(versao, livro, capitulo, versiculo):
    """
    Busca uma referência específica na Midvash API.
    """

    url = (
        f"{API_URL}/{versao}/"
        f"{livro}/{capitulo}/{versiculo}"
    )

    requisicao = urllib.request.Request(
        url,
        method="GET"
    )

    with urllib.request.urlopen(
        requisicao,
        timeout=30
    ) as resposta:

        dados = json.loads(
            resposta.read().decode("utf-8")
        )

    return dados["data"]["text"]


# ============================================================
# ESCOLHER O VERSÍCULO
# ============================================================

def escolher_versiculo():
    """
    Escolhe um versículo diferente para cada horário.

    07h → período 0
    12h → período 1
    19h → período 2

    A escolha também muda de acordo com o dia.
    """

    agora = datetime.now(timezone.utc)

    # Número do dia dentro do ano.
    dia = agora.timetuple().tm_yday

    # Horário UTC usado pelo GitHub Actions.
    hora = agora.hour

    if hora < 13:
        periodo = 0
    elif hora < 19:
        periodo = 1
    else:
        periodo = 2

    # Faz a sequência mudar a cada dia.
    indice = (dia * 3 + periodo) % len(VERSICULOS)

    return VERSICULOS[indice]


# ============================================================
# ENVIAR MENSAGEM PARA O DISCORD
# ============================================================

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
            "Content-Type": "application/json"
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


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    # Escolhe a referência do momento.
    nome_livro, livro_api, capitulo, versiculo = (
        escolher_versiculo()
    )

    # Busca a MESMA referência nas duas traduções.
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


# ============================================================
# INICIAR
# ============================================================

if __name__ == "__main__":
    main()
