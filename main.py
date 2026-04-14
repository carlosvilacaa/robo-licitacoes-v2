import requests
from bs4 import BeautifulSoup
import pdfplumber
import re
from datetime import datetime

# ================= CONFIG =================

PALAVRAS_OBRA = [
    "pavimentação", "asfalto", "recapeamento",
    "terraplanagem", "drenagem", "obra",
    "infraestrutura", "engenharia", "construção"
]

PALAVRAS_LICITACAO = [
    "aviso de licitação",
    "licitação",
    "concorrência",
    "tomada de preços",
    "pregão"
]

# ==========================================

def enviar_telegram(msg):
    TOKEN = "8749489427:AAGph4ZejogI1viJZf29Q75f_33YOzVxSwM"
    CHAT_ID = "8373941356"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# ================= IOEPA =================

def buscar_pdf_ioepa():
    url = "https://www.ioepa.com.br/portal/diario-oficial"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    links = soup.find_all("a")

    for link in links:
        href = link.get("href")
        if href and ".pdf" in href:
            return href

    return None


def baixar_pdf(url):
    nome = "doe.pdf"
    r = requests.get(url)

    with open(nome, "wb") as f:
        f.write(r.content)

    return nome


def extrair_texto(pdf):
    texto = ""

    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            try:
                texto += page.extract_text() + "\n"
            except:
                pass

    return texto.lower()


# ================= INTELIGÊNCIA =================

def dividir_blocos(texto):
    padrao = r"(aviso de licitação|licitação|pregão|concorrência)"
    blocos = re.split(padrao, texto)

    blocos_formatados = []
    for i in range(1, len(blocos), 2):
        bloco = blocos[i] + blocos[i+1]
        blocos_formatados.append(bloco)

    return blocos_formatados


def analisar_bloco(bloco):
    score = 0
    palavras_encontradas = []

    for palavra in PALAVRAS_OBRA:
        if palavra in bloco:
            score += 2
            palavras_encontradas.append(palavra)

    cidade = "Não identificada"

    cidade_match = re.search(r"município de ([a-z\s]+)", bloco)
    if cidade_match:
        cidade = cidade_match.group(1).strip().title()
        score += 2

    trecho = bloco[:500]

    return {
        "score": score,
        "cidade": cidade,
        "palavras": list(set(palavras_encontradas)),
        "trecho": trecho
    }


def classificar(score):
    if score >= 6:
        return "🔥 ALTA"
    elif score >= 3:
        return "⚠️ MÉDIA"
    else:
        return "🔍 BAIXA"


# ================= EXECUÇÃO =================

def executar_robo():
    print("🔎 Buscando IOEPA...")

    pdf_url = buscar_pdf_ioepa()

    if not pdf_url:
        return {
            "total": 0,
            "melhor": None
        }

    pdf = baixar_pdf(pdf_url)
    texto = extrair_texto(pdf)

    blocos = dividir_blocos(texto)

    resultados = []

    for bloco in blocos:
        resultado = analisar_bloco(bloco)

        if resultado["score"] >= 3:
            resultados.append(resultado)

    if not resultados:
        return {
            "total": 0,
            "melhor": None
        }

    melhor = max(resultados, key=lambda x: x["score"])

    return {
        "total": len(resultados),
        "melhor": melhor
    }


# ================= RELATÓRIO =================

def gerar_relatorio_ioepa():
    dados = executar_robo()

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    msg = f"📊 RELATÓRIO DE LICITAÇÕES\n"
    msg += f"🕒 {agora}\n\n"

    msg += f"🧠 RADAR DE OBRAS PÚBLICAS\n\n"

    if dados["melhor"]:
        melhor = dados["melhor"]

        msg += f"📍 Cidade: {melhor['cidade']}\n"
        msg += f"📊 Score: {melhor['score']}\n"
        msg += f"🚀 Chance: {classificar(melhor['score'])}\n\n"

        msg += f"📌 Palavras: {', '.join(melhor['palavras'])}\n\n"
        msg += f"📄 Trecho encontrado:\n{melhor['trecho'][:300]}...\n\n"
    else:
        msg += f"❌ Nenhuma oportunidade relevante\n\n"

    msg += f"🏛️ IOEPA: {dados['total']}\n"
    msg += f"🔎 Monitoramento ativo"

    return msg


# ================= TESTE =================

if __name__ == "__main__":
    mensagem = gerar_relatorio_ioepa()
    print(mensagem)
