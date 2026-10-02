import os
import json
import random
import urllib.request

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# ID do cargo "Membro"
# Se não existir, o bot continua funcionando sem marcar o cargo.
MEMBER_ROLE_ID = os.environ.get("MEMBER_ROLE_ID", "")

API_URL = "https://api.midvash.com/v1"

# Livros permitidos
LIVROS = [
    ("Salmos", "psalms", 150),
    ("Provérbios", "proverbs", 31),
    ("Eclesiastes", "ecclesiastes", 12),
]


def consultar_api(url):

    requisicao = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "Devocionalico/5.0",
            "Accept": "application/json"
        }
    )

    with urllib.request.urlopen(
        requisicao,
        timeout=30
    ) as resposta:

        return json.loads(
            resposta.read().decode("utf-8")
        )


def escolher_versiculo():

    while True:

        nome_livro, slug, quantidade_capitulos = random.choice(
            LIVROS
        )

        capitulo = random.randint(
            1,
            quantidade_capitulos
        )

        try:

            url = (
                f"{API_URL}/naa/"
                f"{slug}/{capitulo}"
            )

            dados = consultar_api(url)

            versiculos = dados["data"]["verses"]

            if not versiculos:
                continue

            numero_versiculo = random.randint(
                1,
                len(versiculos)
            )

            return (
                nome_livro,
                slug,
                capitulo,
                numero_versiculo
            )

        except Exception:
            continue


def pegar_versiculo(
    slug,
    capitulo,
    versiculo
):

    url = (
        f"{API_URL}/naa/"
        f"{slug}/{capitulo}/{versiculo}"
    )

    dados = consultar_api(url)

    return dados["data"]["text"]


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
            "User-Agent": "Devocionalico/5.0"
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

    print("📖 Devocionalico iniciado!")

    (
        nome_livro,
        slug,
        capitulo,
        versiculo
    ) = escolher_versiculo()

    referencia = (
        f"{nome_livro} "
        f"{capitulo}:{versiculo}"
    )

    print(
        f"📖 Versículo escolhido: {referencia}"
    )

    texto_naa = pegar_versiculo(
        slug,
        capitulo,
        versiculo
    )

    if MEMBER_ROLE_ID:
        mencao = (
            f"<@&{MEMBER_ROLE_ID}>\n\n"
        )
    else:
        mencao = ""

    mensagem = f"""{mencao}📖 **DEVOCIONALICO**

✨ **{referencia}**

📘 **NAA — Nova Almeida Atualizada**
> {texto_naa}

🙏 Que a Palavra de Deus abençoe o seu dia!

— 🤖 **Devocionalico**
ᴮᵒᵗ ᵈᵒ ACTA
"""

    enviar_discord(mensagem)

    print(
        "✅ Versículo enviado com sucesso!"
    )


if __name__ == "__main__":
    main()
