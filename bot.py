import os
import json
import urllib.request
import urllib.error

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

MIDVASH_URL = "https://api.midvash.com/v1/votd"


def pegar_versiculo(versao):
    url = f"{MIDVASH_URL}?language=pt-br&version={versao}"

    with urllib.request.urlopen(url, timeout=30) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    return {
        "referencia": dados["reference"],
        "texto": dados["text"]
    }


def enviar_discord(mensagem):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

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

    with urllib.request.urlopen(requisicao, timeout=30) as resposta:
        if resposta.status not in (200, 201):
            raise Exception(f"Discord respondeu: {resposta.status}")


def main():
    naa = pegar_versiculo("naa")
    ara = pegar_versiculo("ara")

    if naa["referencia"] != ara["referencia"]:
        raise Exception("As duas versões retornaram referências diferentes.")

    mensagem = f"""📖 **VERSÍCULO DO DIA**

✨ **{naa["referencia"]}**

**NAA — Nova Almeida Atualizada**
> {naa["texto"]}

**ARA — Almeida Revista e Atualizada**
> {ara["texto"]}

🙏 Que a Palavra de Deus abençoe o seu dia!

— 🤖 **Devocionalico**
"""

    enviar_discord(mensagem)


if __name__ == "__main__":
    main()
