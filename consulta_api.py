import json
import urllib.request

URL_POST = "https://miliogo.com/cupom/consulta.php"
#URL_POST = "http://localhost/miliogo/cupom/consulta.php"

#data = {"nome": "ovos"}
data = {"codigo": "7894474002638"}

json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    URL_POST,
    data=json_bytes,
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "miliogo-cupom-client/1.0"
    },    
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    resposta = resp.read().decode("utf-8")
    print(resposta)