import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import json

# 🔐 TELEGRAM
TOKEN = "8749489427:AAGph4ZejogI1viJZf29Q75f_33YOzVxSwM"
CHAT_ID = "8373941356"

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 🌎 HORÁRIO BRASIL
brasil = pytz.timezone("America/Sao_Paulo")

# ================= IOEPA =================

def buscar_ioepa():
    print("🔎 Buscando IOEPA...")

    try:
        url = "https://www.ioepa.com.br/pages/search"
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        textos = soup.get_text().lower()

        palavras = [
            "asfalto",
            "pavimentação",
            "drenagem",
            "infraestrutura",
            "recapeamento",
            "tapa buraco"
        ]

        encontrados = []
        for p in palavras:
            if p in textos:
                encontrados.append(p)

        return encontrados

    except Exception as e:
        print("Erro IOEPA:", e)
        return []

# ================= PNCP =================

def buscar_pncp():
    print("🌎 Buscando PNCP...")
    return 0

# ================= PREFEITURAS =================

def buscar_prefeituras():
    print("🏙️ Buscando Prefeituras...")
    return []

# ================= MENSAGEM =================

def montar_mensagem(ioepa, pncp, pref):
    agora = datetime.now(brasil).strftime("%d/%m/%Y %H:%M")

    msg = f"""
📊 RELATÓRIO DE LICITAÇÕES

🕒 {agora}

🌐 IOEPA:
{ "✅ Encontrado: " + ", ".join(ioepa) if ioepa else "❌ Nenhum resultado" }

🌎 PNCP:
{pncp} oportunidades

🏙️ Prefeituras:
{len(pref)} oportunidades

🔍 Sistema ativo
"""
    return msg

# ================= EXECUTAR =================

def executar():
    print("🚀 Robô iniciado...")

    while True:
        agora = datetime.now(brasil)

        print(f"⏰ Rodando agora: {agora.strftime('%H:%M:%S')}")

        ioepa = buscar_ioepa()
        pncp = buscar_pncp()
        pref = buscar_prefeituras()

        msg = montar_mensagem(ioepa, pncp, pref)
        enviar(msg)

        print("✅ Mensagem enviada\n")

        time.sleep(60)  # roda a cada 1 minuto

# START
executar()
