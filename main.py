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

    url = "https://www.ioepa.com.br/pages/search"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    textos = soup.get_text().lower()

    palavras = ["asfalto", "pavimentação", "drenagem", "infraestrutura"]

    encontrados = []
    for p in palavras:
        if p in textos:
            encontrados.append(p)

    return encontrados

# ================= PNCP (SIMPLES MOCK POR ENQUANTO) =================

def buscar_pncp():
    print("🌎 Buscando PNCP...")
    return 0  # depois melhoramos

# ================= PREFEITURAS (SIMPLES MOCK) =================

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

        if agora.minute == 0:  # roda de hora em hora
            print(f"⏰ Rodando {agora.hour}:00")

            ioepa = buscar_ioepa()
            pncp = buscar_pncp()
            pref = buscar_prefeituras()

            msg = montar_mensagem(ioepa, pncp, pref)
            enviar(msg)

            time.sleep(60)

        time.sleep(10)

# START
executar()
