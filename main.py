import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time

# 🔐 TELEGRAM
TOKEN = "8749489427:AAGph4ZejogI1viJZf29Q75f_33YOzVxSwM"
CHAT_ID = "8373941356"

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 🌎 HORÁRIO BRASIL
brasil = pytz.timezone("America/Sao_Paulo")

# ================= INTELIGÊNCIA =================

def analisar_noticia(texto):
    texto = texto.lower()
    score = 0

    if "pavimentação" in texto: score += 3
    if "asfalto" in texto: score += 3
    if "drenagem" in texto: score += 3
    if "infraestrutura" in texto: score += 2
    if "recapeamento" in texto: score += 3
    if "licitação" in texto: score += 5
    if "convênio" in texto: score += 2

    cidades = [
        "parauapebas", "marabá", "belém",
        "altamira", "santarém", "redenção",
        "castanhal", "ananindeua"
    ]

    cidade_detectada = None

    for c in cidades:
        if c in texto:
            score += 2
            cidade_detectada = c.title()

    if score >= 8:
        chance = "🔥 Alta"
    elif score >= 4:
        chance = "⚠️ Média"
    else:
        chance = "Baixa"

    return score, chance, cidade_detectada

# ================= IOEPA =================

def buscar_ioepa():
    print("🔎 Buscando IOEPA...")

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
    print("🌎 Buscando PNCP...")
    return 0  # depois evoluímos

# ================= PREFEITURAS =================

def buscar_prefeituras():
    print("🏙️ Buscando Prefeituras...")
    return []

# ================= MENSAGEM =================

def montar_mensagem(ioepa, pncp, pref):
    agora = datetime.now(brasil).strftime("%d/%m/%Y %H:%M")

    if ioepa:
        cidade = ioepa["cidade"] if ioepa["cidade"] else "Não identificada"

        inteligencia = f"""
🧠 INTELIGÊNCIA DE MERCADO

📍 Cidade: {cidade}
📊 Score: {ioepa['score']}
🚀 Chance: {ioepa['chance']}
"""
    else:
        inteligencia = "❌ Nenhum dado relevante"

    msg = f"""
📊 RELATÓRIO DE LICITAÇÕES

🕒 {agora}

{inteligencia}

🌎 PNCP: {pncp}
🏙️ Prefeituras: {len(pref)}

🔍 Sistema ativo
"""
    return msg

# ================= EXECUÇÃO =================

def executar():
    print("🚀 Robô inteligente iniciado...")

    horarios_execucao = [8, 10, 13, 16, 17]
    horarios_executados = set()

    while True:
        agora = datetime.now(brasil)
        hora = agora.hour
        minuto = agora.minute

        horario_str = f"{hora}:{minuto}"

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

        if hora == 0 and minuto == 0:
            horarios_executados.clear()

        time.sleep(30)

# START
executar()
