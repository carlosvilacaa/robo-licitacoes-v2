import requests
import pdfplumber
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

# ================= PALAVRAS =================

PALAVRAS_OBRA = [
    "pavimentação","asfalto","terraplanagem","drenagem",
    "infraestrutura","recapeamento","obra","engenharia",
    "galeria","urbanização"
]

PALAVRAS_LICITACAO = [
    "licitação","edital","pregão","concorrência","contratação"
]

PALAVRAS_EXCLUIR = [
    "limpeza","fornecimento","locação","aluguel"
]

# ================= INTELIGÊNCIA =================

def eh_obra_real(texto):
    texto = texto.lower()

    if any(p in texto for p in PALAVRAS_EXCLUIR):
        return False

    tem_licitacao = any(p in texto for p in PALAVRAS_LICITACAO)
    tem_obra = any(p in texto for p in PALAVRAS_OBRA)

    return tem_licitacao and tem_obra

# ================= IOEPA PDF (AJUSTADO) =================

def buscar_ioepa():
    try:
        url = "https://www.ioepa.com.br/pages/diario"
        resp = requests.get(url, timeout=10)

        soup = BeautifulSoup(resp.text, "html.parser")

        pdf_link = None
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if ".pdf" in href:
                pdf_link = href
                break

        if not pdf_link:
            return []

        if not pdf_link.startswith("http"):
            pdf_link = "https://www.ioepa.com.br" + pdf_link

        pdf = requests.get(pdf_link, timeout=20)

        with open("ioepa.pdf", "wb") as f:
            f.write(pdf.content)

        resultados = []

        with pdfplumber.open("ioepa.pdf") as pdf:

            encontrou_secao = False

            for i, page in enumerate(pdf.pages):
                texto = page.extract_text()
                if not texto:
                    continue

                texto_lower = texto.lower()

                # 🔎 detectar município/prefeitura
                if (
                    "município" in texto_lower or
                    "municípios" in texto_lower or
                    "prefeitura" in texto_lower
                ):
                    encontrou_secao = True

                if not encontrou_secao:
                    continue

                # 🔥 NOVA REGRA ESPECÍFICA (SÓ ASFALTO/PAVIMENTAÇÃO)
                if (
                    "licitação" in texto_lower and
                    ("asfalto" in texto_lower or "pavimentação" in texto_lower)
                ):
                    resultados.append({
                        "pagina": i + 1,
                        "trecho": texto[:200]
                    })

        return resultados

    except Exception as e:
        print("Erro IOEPA:", e)
        return []

# ================= PNCP =================

def buscar_pncp():
    try:
        url = "https://pncp.gov.br/app/editais?q=obra"
        resp = requests.get(url, timeout=10)

        texto = resp.text.lower()
        blocos = texto.split("edital")

        total = 0
        for bloco in blocos:
            if eh_obra_real(bloco):
                total += 1

        return total

    except:
        return 0

# ================= PREFEITURAS =================

def buscar_prefeituras():
    try:
        url = "https://www.google.com/search?q=licitação+obra+prefeitura"
        resp = requests.get(url, timeout=10)

        texto = resp.text.lower()

        if eh_obra_real(texto):
            return 1

        return 0

    except:
        return 0

# ================= RELATÓRIO =================

def montar_relatorio():
    agora = datetime.now(brasil).strftime("%d/%m/%Y %H:%M")

    ioepa_resultados = buscar_ioepa()
    pncp = buscar_pncp()
    pref = buscar_prefeituras()

    score = (len(ioepa_resultados)*3) + (pncp*4) + (pref*2)

    if score >= 6:
        chance = "🔥 ALTA"
    elif score >= 3:
        chance = "⚠️ MÉDIA"
    else:
        chance = "🔎 BAIXA"

    msg = f"""📊 RELATÓRIO DE LICITAÇÕES
🕒 {agora}

🧠 RADAR DE OBRAS PÚBLICAS

📍 Cidade: Monitoramento geral
📊 Score: {score}
🚀 Chance: {chance}

🌎 PNCP: {pncp}
🏛️ Prefeituras: {pref}
📰 IOEPA: {len(ioepa_resultados)}
"""

    if ioepa_resultados:
        msg += "\n📄 DETALHES IOEPA:\n\n"

        for r in ioepa_resultados[:2]:
            msg += f"""📄 Página {r['pagina']}
📝 {r['trecho']}

"""

    msg += "\n🔎 Monitoramento ativo"

    return msg

# ================= LOOP =================

def loop():
    horarios = [8, 10, 13, 16, 17]

    while True:
        agora = datetime.now(brasil)

        if agora.hour in horarios and agora.minute == 0:
            enviar(montar_relatorio())
            time.sleep(60)

        time.sleep(30)

# ================= COMANDOS =================

def comandos():
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

            elif texto == "/status":
                enviar("✅ Robô online")

# ================= START =================

t1 = threading.Thread(target=loop)
t2 = threading.Thread(target=comandos)

t1.start()
t2.start()

t1.join()
t2.join()
