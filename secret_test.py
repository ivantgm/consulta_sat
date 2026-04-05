import os
import urllib.request

URL_POST = "https://miliogo.com/cupom/api.php"

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
    method="GET"
)
try:
    with urllib.request.urlopen(req) as resp:
        resposta = resp.read().decode("utf-8")
        print("Secret Válido. Resposta da API:", resposta)
except urllib.error.HTTPError as e:
    print("Erro HTTP:", e.code, e.reason, e.read().decode("utf-8"))
     


