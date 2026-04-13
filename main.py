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

    horarios_execucao = [8, 10, 13, 16, 17]
    horarios_executados = set()

    while True:
        agora = datetime.now(brasil)
        hora = agora.hour
        minuto = agora.minute

        horario_str = f"{hora}:{minuto}"

        # roda apenas nos horários definidos (minuto 0)
        if hora in horarios_execucao and minuto == 0:
            if horario_str not in horarios_executados:
                print(f"⏰ Executando {hora}:00")

                ioepa = buscar_ioepa()
                pncp = buscar_pncp()
                pref = buscar_prefeituras()

                msg = montar_mensagem(ioepa, pncp, pref)
                enviar(msg)

                print("✅ Mensagem enviada\n")

                horarios_executados.add(horario_str)

        # limpa controle todo dia meia noite
        if hora == 0 and minuto == 0:
            horarios_executados.clear()

        time.sleep(30)

# START
executar()
