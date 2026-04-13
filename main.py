import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import threading

# 🔐 TELEGRAM
TOKEN = "8749489427:AAGph4ZejogI1viJZf29Q75f_33YOzVxSwM"
CHAT_ID = "8373941356"

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 🌎 HORÁRIO BRASIL
brasil = pytz.timezone("America/Sao_Paulo")

# ================= RADAR COMPLETO =================

def analisar_noticia(texto):
    texto = texto.lower()
    score = 0

    # 🔥 OBRAS PESADAS
    if "pavimentação" in texto: score += 3
    if "asfalto" in texto: score += 3
    if "recapeamento" in texto: score += 3
    if "tapa buraco" in texto: score += 2

    # 🔥 BASE / PREPARAÇÃO
    if "terraplanagem" in texto: score += 3
    if "movimentação de terra" in texto: score += 3
    if "regularização" in texto: score += 2
    if "compactação" in texto: score += 2
    if "topografia" in texto: score += 2

    # 🔥 DRENAGEM
    if "drenagem" in texto: score += 3
    if "bueiro" in texto: score += 2
    if "galeria" in texto: score += 2

    # 🔥 GERAL
    if "infraestrutura" in texto: score += 2
    if "urbanização" in texto: score += 2

    # 🔥 SINAIS DE LICITAÇÃO
    if "licitação" in texto: score += 5
    if "edital" in texto: score += 5
    if "convênio" in texto: score += 2
    if "contratação" in texto: score += 3

    # 📍 CIDADES (expandível)
    cidades = [
        "parauapebas", "marabá", "belém", "altamira",
        "santarém", "redenção", "castanhal", "ananindeua",
        "itaituba", "tucuruí", "xinguara"
    ]

    cidade_detectada = None

    for c in cidades:
        if c in texto:
            score += 2
            cidade_detectada = c.title()

    # 🎯 CLASSIFICAÇÃO
    if score >= 10:
        chance = "🔥🔥 MUITO ALTA"
    elif score >= 7:
        chance = "🔥 ALTA"
    elif score >= 4:
        chance = "⚠️ MÉDIA"
    else:
        chance = "🔎 BAIXA"

    return score, chance, cidade_detectada

# ================= IOEPA =================

def buscar_ioepa():
    try:
        url = "https://www.ioepa.com.br/pages/search"
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        texto = soup.get_text().lower()

        score, chance, cidade = analisar_noticia(texto)

        return {
            "score": score,
            "chance": chance,
            "cidade": cidade
        }

    except Exception as e:
        print("Erro IOEPA:", e)
        return None

# ================= PNCP =================

def buscar_pncp():
    return 0

# ================= PREFEITURAS =================

def buscar_prefeituras():
    return []

# ================= MENSAGEM =================

def montar_mensagem(ioepa, pncp, pref):
    agora = datetime.now(brasil).strftime("%d/%m/%Y %H:%M")

    if ioepa:
        cidade = ioepa["cidade"] if ioepa["cidade"] else "Não identificada"

        inteligencia = f"""
🧠 RADAR DE OBRAS PÚBLICAS

📍 Cidade: {cidade}
📊 Score: {ioepa['score']}
🚀 Chance: {ioepa['chance']}
"""
    else:
        inteligencia = "❌ Nenhuma oportunidade detectada"

    return f"""
📊 RELATÓRIO DE LICITAÇÕES

🕒 {agora}

{inteligencia}

🌎 PNCP: {pncp}
🏙️ Prefeituras: {len(pref)}

🔍 Monitoramento ativo
"""

# ================= RESUMO =================

def montar_resumo(ioepa):
    if not ioepa:
        return "❌ Nenhuma oportunidade encontrada"

    return f"""
📊 RESUMO RÁPIDO

📍 {ioepa['cidade']}
🚀 Chance: {ioepa['chance']}
📊 Score: {ioepa['score']}
"""

# ================= TOP =================

def montar_top(ioepa):
    if not ioepa or not ioepa["cidade"]:
        return "❌ Sem dados suficientes"

    return f"""
🏆 MELHOR OPORTUNIDADE

📍 {ioepa['cidade']}
🚀 Chance: {ioepa['chance']}
"""

# ================= LOOP =================

def loop_principal():
    print("🚀 Radar de obras iniciado")

    horarios = [8, 10, 13, 16, 17]
    executados = set()

    while True:
        agora = datetime.now(brasil)
        hora = agora.hour
        minuto = agora.minute

        key = f"{hora}:{minuto}"

        if hora in horarios and minuto == 0:
            if key not in executados:

                ioepa = buscar_ioepa()
                pncp = buscar_pncp()
                pref = buscar_prefeituras()

                enviar(montar_mensagem(ioepa, pncp, pref))

                executados.add(key)

        if hora == 0 and minuto == 0:
            executados.clear()

        time.sleep(30)

# ================= COMANDOS =================

def escutar_comandos():
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

            ioepa = buscar_ioepa()

            if texto in ["/teste", "/relat"]:
                enviar(montar_mensagem(ioepa, 0, []))

            elif texto == "/status":
                enviar("✅ Radar ativo e funcionando")

            elif texto == "/resumo":
                enviar(montar_resumo(ioepa))

            elif texto == "/top":
                enviar(montar_top(ioepa))

# ================= START =================

t1 = threading.Thread(target=loop_principal)
t2 = threading.Thread(target=escutar_comandos)

t1.start()
t2.start()

t1.join()
t2.join()
