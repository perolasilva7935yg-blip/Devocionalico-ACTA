import os
import json
import random
import urllib.request
import urllib.error
import sys

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
MEMBER_ROLE_ID = os.environ.get("MEMBER_ROLE_ID", "").strip()

API_URL = "https://api.midvash.com/v1"

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
            "User-Agent": "Devocionalico/6.0",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(requisicao, timeout=30) as resposta:
        return json.loads(
            resposta.read().decode("utf-8")
        )


def escolher_versiculo():
    for tentativa in range(10):
        nome_livro, slug, quantidade_capitulos = random.choice(LIVROS)
        capitulo = random.randint(1, quantidade_capitulos)

        try:
            url = f"{API_URL}/naa/{slug}/{capitulo}"
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
                numero_versiculo,
            )

        except Exception as erro:
            print(
                f"⚠️ Tentativa {tentativa + 1} falhou: {erro}"
            )

    raise Exception(
        "Não foi possível escolher um versículo."
    )


def pegar_versiculo(slug, capitulo, versiculo):
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

    dados = {
        "content": mensagem,
    }

    if MEMBER_ROLE_ID:
        dados["allowed_mentions"] = {
            "roles": [MEMBER_ROLE_ID]
        }

    corpo = json.dumps(dados).encode("utf-8")

    requisicao = urllib.request.Request(
        url,
        data=corpo,
        method="POST",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Devocionalico/6.0",
        },
    )

    try:
        with urllib.request.urlopen(
            requisicao,
            timeout=30
        ) as resposta:

            status = resposta.status

            print(
                f"📨 Discord respondeu: {status}"
            )

            if status not in (200, 201):
                raise Exception(
                    f"Discord respondeu: {status}"
                )

    except urllib.error.HTTPError as erro:
        detalhes = erro.read().decode("utf-8")

        print(
            f"❌ Discord respondeu com erro {erro.code}:"
        )
        print(detalhes)

        raise


def main():
    print("=" * 50)
    print("🤖 DEVOCIONALICO")
    print("🚀 Arquivo bot.py executado!")
    print("=" * 50)

    nome_livro, slug, capitulo, versiculo = (
        escolher_versiculo()
    )

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
        versiculo,
    )

    if MEMBER_ROLE_ID:
        mencao = (
            f"<@&{MEMBER_ROLE_ID}>\n\n"
        )
        print("👥 Cargo Membro será mencionado.")
    else:
        mencao = ""
        print(
            "⚠️ MEMBER_ROLE_ID não configurado."
        )

    mensagem = f"""{mencao}📖 **DEVOCIONALICO**

✨ **{referencia}**

📘 **NAA — Nova Almeida Atualizada**
> {texto_naa}

🙏 Que a Palavra de Deus abençoe o seu dia!

— 🤖 **Devocionalico**
ᴮᵒᵗ ᵈᵒ ACTA
"""

    print("📨 Enviando mensagem para o Discord...")

    enviar_discord(mensagem)

    print("✅ VERSÍCULO ENVIADO COM SUCESSO!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print("=" * 50)
        print("❌ O DEVOCIONALICO FALHOU!")
        print(f"Erro: {erro}")
        print("=" * 50)
        sys.exit(1)
