import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import threading

# ================= TELEGRAM =================

TOKEN = "8749489427:AAGph4ZejogI1viJZf29Q75f_33YOzVxSwM"
CHAT_ID = "8373941356"

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

brasil = pytz.timezone("America/Sao_Paulo")

# ================= IOEPA =================

def buscar_ioepa():
    try:
        url = "https://www.ioepa.com.br"
        resp = requests.get(url, timeout=10)
        texto = resp.text.lower()

        palavras = [
            "licitação",
            "edital",
            "pavimentação",
            "asfalto",
            "obra",
            "infraestrutura"
        ]

        encontrados = [p for p in palavras if p in texto]

        return len(encontrados)

    except Exception as e:
        print("Erro IOEPA:", e)
        return 0

# ================= PNCP =================

def buscar_pncp():
    try:
        url = "https://pncp.gov.br/app/editais?q=obra"
        resp = requests.get(url, timeout=10)

        if "obra" in resp.text.lower():
            return 1
        return 0

    except Exception as e:
        print("Erro PNCP:", e)
        return 0

# ================= PREFEITURAS =================

def buscar_prefeituras():
    try:
        url = "https://www.google.com/search?q=licitação+prefeitura+obra"
        resp = requests.get(url, timeout=10)

        if "licitação" in resp.text.lower():
            return 1
        return 0

    except Exception as e:
        print("Erro Prefeituras:", e)
        return 0

# ================= INTELIGÊNCIA =================

def analisar_total(ioepa, pncp, pref):
    score = ioepa * 2 + pncp * 3 + pref * 2

    if score >= 5:
        chance = "🔥 ALTA"
    elif score >= 3:
        chance = "⚠️ MÉDIA"
    else:
        chance = "🔎 BAIXA"

    return score, chance

# ================= RELATÓRIO =================

def montar_relatorio():
    agora = datetime.now(brasil).strftime("%d/%m/%Y %H:%M")

    ioepa = buscar_ioepa()
    pncp = buscar_pncp()
    pref = buscar_prefeituras()

    score, chance = analisar_total(ioepa, pncp, pref)

    msg = f"""📊 RELATÓRIO DE LICITAÇÕES
🕒 {agora}

🧠 RADAR DE OBRAS PÚBLICAS

📍 Cidade: Monitoramento geral
📊 Score: {score}
🚀 Chance: {chance}

🌎 PNCP: {pncp}
🏛️ Prefeituras: {pref}
📰 IOEPA: {ioepa}

🔎 Monitoramento ativo
"""

    return msg

# ================= LOOP =================

def loop():
    print("🚀 Robô iniciado")

    horarios = [8, 10, 13, 16, 17]

    while True:
        agora = datetime.now(brasil)

        if agora.hour in horarios and agora.minute == 0:
            print(f"⏰ Executando {agora.hour}:00")

            msg = montar_relatorio()
            enviar(msg)

            time.sleep(60)

        time.sleep(30)

# ================= COMANDOS =================

def comandos():
    print("📡 Escutando comandos...")

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    offset = None

    while True:
        params = {"timeout": 100}
        if offset:
            params["offset"] = offset

        resp = requests.get(url, params=params).json()

        for update in resp.get("result", []):
            offset = update["update_id"] + 1

            try:
                texto = update["message"]["text"]
                chat_id = update["message"]["chat"]["id"]
            except:
                continue

            if str(chat_id) != CHAT_ID:
                continue

            if texto == "/relat":
                enviar(montar_relatorio())

            if texto == "/status":
                enviar("✅ Robô online")

# ================= START =================

t1 = threading.Thread(target=loop)
t2 = threading.Thread(target=comandos)

t1.start()
t2.start()

t1.join()
t2.join()
