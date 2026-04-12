import os
import urllib.request
import json

#URL_POST = "http://localhost/miliogo/cupom/url.php"
URL_POST = "https://miliogo.com/cupom/url.php"

secret_file_name = "secret_key.txt"
if not os.path.isfile(secret_file_name):
    raise FileNotFoundError(f"Arquivo de segredo não encontrado: {secret_file_name}")
secret_file = open(secret_file_name, "r")
secret_key = secret_file.read().strip()
secret_file.close()

req = urllib.request.Request(
    URL_POST,
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "miliogo-cupom-client/1.0",
        "secret-key": secret_key
    },
    method="POST",
    data = json.dumps({
        "url": "https://www.nfce.fazenda.sp.gov.br/NFCeConsultaPublica/Paginas/ConsultaQRCode.aspx?p=35260447603246000111652230000024501000357094|2|1|1|d2edae4484112693a86fd9138e6ff4155b65688f"
    }, ensure_ascii=False).encode("utf-8")
)
try:
    with urllib.request.urlopen(req) as resp:
        resposta = resp.read().decode("utf-8")
        print("Ok:", resposta)
except urllib.error.HTTPError as e:
    print("Erro HTTP:", e.code, e.reason, e.read().decode("utf-8"))
     


