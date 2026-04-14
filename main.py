import requests
import pdfplumber
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import threading
import os

# ================= TELEGRAM =================

TOKEN = "8749489427:AAGph4ZejogI1viJZf29Q75f_33YOzVxSwM"
CHAT_ID = "8373941356"

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

brasil = pytz.timezone("America/Sao_Paulo")

# ================= PALAVRAS =================

PALAVRAS_OBRA = [
    "pavimentação",
    "asfalto",
    "terraplanagem",
    "drenagem",
    "infraestrutura",
    "recapeamento",
    "obra",
    "engenharia",
    "galeria pluvial",
    "rede de esgoto",
    "urbanização",
    "construção civil"
]

PALAVRAS_LICITACAO = [
    "licitação",
    "edital",
    "pregão",
    "concorrência",
    "contratação"
]

PALAVRAS_EXCLUIR = [
    "limpeza",
    "fornecimento",
    "locação",
    "aluguel",
    "material de expediente",
    "serviço comum"
]

# ================= INTELIGÊNCIA =================

def eh_obra_real(texto):
    texto = texto.lower()

    if any(p in texto for p in PALAVRAS_EXCLUIR):
        return False

    tem_licitacao = any(p in texto for p in PALAVRAS_LICITACAO)
    tem_obra = any(p in texto for p in PALAVRAS_OBRA)

    return tem_licitacao and tem_obra

# ================= IOEPA PDF =================

def buscar_ioepa_pdf():
    try:
        print("🔎 Buscando DOE...")

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
            print("❌ PDF não encontrado")
            return []

        if not pdf_link.startswith("http"):
            pdf_link = "https://www.ioepa.com.br" + pdf_link

        print("📄 PDF:", pdf_link)

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

                # 🔥 detectar área de municípios/prefeituras
                if (
                    "município" in texto_lower or
                    "municípios" in texto_lower or
                    "prefeitura" in texto_lower
                ):
                    encontrou_secao = True

                if not encontrou_secao:
                    continue

                # 🔥 aplicar inteligência de obra
                if eh_obra_real(texto_lower):

                    trecho = texto.replace("\n", " ")

                    resultados.append({
                        "pagina": i + 1,
                        "trecho": trecho[:400]
                    })

        return resultados

    except Exception as e:
        print("Erro IOEPA:", e)
        return []

# ================= MENSAGEM =================

def montar_relatorio():
    agora = datetime.now(brasil).strftime("%d/%m/%Y %H:%M")

    resultados = buscar_ioepa_pdf()

    if not resultados:
        return f"""📊 RELATÓRIO DOE (IOEPA)
🕒 {agora}

❌ Nenhuma licitação de OBRA encontrada
"""

    msg = f"""📊 RELATÓRIO DOE (IOEPA)
🕒 {agora}

🔥 OBRAS ENCONTRADAS:

"""

    for r in resultados[:3]:
        msg += f"""📄 Página: {r['pagina']}
📝 {r['trecho']}

---------------------

"""

    return msg

# ================= LOOP =================

def loop():
    print("🚀 Robô DOE iniciado")

    horarios = [8, 10, 13, 16, 17]

    while True:
        agora = datetime.now(brasil)

        if agora.hour in horarios and agora.minute == 0:
            print(f"⏰ Executando {agora.hour}:00")

            enviar(montar_relatorio())

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

            elif texto == "/status":
                enviar("✅ Robô DOE ativo")

# ================= START =================

t1 = threading.Thread(target=loop)
t2 = threading.Thread(target=comandos)

t1.start()
t2.start()

t1.join()
t2.join()
