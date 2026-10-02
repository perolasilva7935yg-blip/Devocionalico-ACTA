import os
import json
import random
import urllib.request

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# O cargo Membro é opcional.
# Se o segredo não existir, o bot continua funcionando.
MEMBER_ROLE_ID = os.environ.get("MEMBER_ROLE_ID", "")

API_URL = "https://api.midvash.com/v1"


# --------------------------------------------------
# FAZER REQUISIÇÃO À API
# --------------------------------------------------

def consultar_api(url):

    requisicao = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "Devocionalico/3.0",
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


# --------------------------------------------------
# LIVROS DA BÍBLIA
# --------------------------------------------------

LIVROS = [
    ("Gênesis", "genesis", 50),
    ("Êxodo", "exodo", 40),
    ("Levítico", "levitico", 27),
    ("Números", "numeros", 36),
    ("Deuteronômio", "deuteronomio", 34),
    ("Josué", "josue", 24),
    ("Juízes", "juizes", 21),
    ("Rute", "rute", 4),
    ("1 Samuel", "1-samuel", 31),
    ("2 Samuel", "2-samuel", 24),
    ("1 Reis", "1-reis", 22),
    ("2 Reis", "2-reis", 25),
    ("1 Crônicas", "1-cronicas", 29),
    ("2 Crônicas", "2-cronicas", 36),
    ("Esdras", "esdras", 10),
    ("Neemias", "neemias", 13),
    ("Ester", "ester", 10),
    ("Jó", "jo", 42),
    ("Salmos", "salmos", 150),
    ("Provérbios", "proverbios", 31),
    ("Eclesiastes", "eclesiastes", 12),
    ("Cânticos", "canticos", 8),
    ("Isaías", "isaias", 66),
    ("Jeremias", "jeremias", 52),
    ("Lamentações", "lamentacoes", 5),
    ("Ezequiel", "ezequiel", 48),
    ("Daniel", "daniel", 12),
    ("Oseias", "oseias", 14),
    ("Joel", "joel", 3),
    ("Amós", "amos", 9),
    ("Obadias", "obadias", 1),
    ("Jonas", "jonas", 4),
    ("Miqueias", "miqueias", 7),
    ("Naum", "naum", 3),
    ("Habacuque", "habacuque", 3),
    ("Sofonias", "sofonias", 3),
    ("Ageu", "ageu", 2),
    ("Zacarias", "zacarias", 14),
    ("Malaquias", "malaquias", 4),

    ("Mateus", "mateus", 28),
    ("Marcos", "marcos", 16),
    ("Lucas", "lucas", 24),
    ("João", "joao", 21),
    ("Atos", "atos", 28),
    ("Romanos", "romanos", 16),
    ("1 Coríntios", "1-corintios", 16),
    ("2 Coríntios", "2-corintios", 13),
    ("Gálatas", "galatas", 6),
    ("Efésios", "efesios", 6),
    ("Filipenses", "filipenses", 4),
    ("Colossenses", "colossenses", 4),
    ("1 Tessalonicenses", "1-tessalonicenses", 5),
    ("2 Tessalonicenses", "2-tessalonicenses", 3),
    ("1 Timóteo", "1-timoteo", 6),
    ("2 Timóteo", "2-timoteo", 4),
    ("Tito", "tito", 3),
    ("Filemom", "filemom", 1),
    ("Hebreus", "hebreus", 13),
    ("Tiago", "tiago", 5),
    ("1 Pedro", "1-pedro", 5),
    ("2 Pedro", "2-pedro", 3),
    ("1 João", "1-joao", 5),
    ("2 João", "2-joao", 1),
    ("3 João", "3-joao", 1),
    ("Judas", "judas", 1),
    ("Apocalipse", "apocalipse", 22)
]


# --------------------------------------------------
# ESCOLHER UM VERSÍCULO REAL
# --------------------------------------------------

def escolher_versiculo():

    while True:

        nome_livro, slug, quantidade_capitulos = (
            random.choice(LIVROS)
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


# --------------------------------------------------
# PEGAR TEXTO DO VERSÍCULO
# --------------------------------------------------

def pegar_versiculo(
    versao,
    slug,
    capitulo,
    versiculo
):

    url = (
        f"{API_URL}/{versao}/"
        f"{slug}/{capitulo}/{versiculo}"
    )

    dados = consultar_api(url)

    return dados["data"]["text"]


# --------------------------------------------------
# ENVIAR PARA O DISCORD
# --------------------------------------------------

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
            "User-Agent": "Devocionalico/3.0"
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


# --------------------------------------------------
# PROGRAMA PRINCIPAL
# --------------------------------------------------

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
        "naa",
        slug,
        capitulo,
        versiculo
    )

    texto_ara = pegar_versiculo(
        "ara",
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

📜 **ARA — Almeida Revista e Atualizada**
> {texto_ara}

🙏 Que a Palavra de Deus abençoe o seu dia!

— 🤖 **Devocionalico**
"""

    enviar_discord(mensagem)

    print(
        "✅ Versículo enviado com sucesso!"
    )


if __name__ == "__main__":
    main()
