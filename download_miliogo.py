import json
import sqlite3
import os
import urllib.request
import sqlite_sat 

# ====== CONFIGURAÇÕES ======
ARQUIVO_DB = "banco.db"
#URL_POST = "http://localhost/miliogo/cupom/consulta_cupom.php"
URL_POST = "https://miliogo.com/cupom/consulta_cupom.php"
# ============================

def download(ultimo_id):
    try:
        secret_file_name = "secret_key.txt"
        if not os.path.isfile(secret_file_name):
            raise FileNotFoundError(f"Arquivo de segredo não encontrado: {secret_file_name}")
        secret_file = open(secret_file_name, "r")
        secret_key = secret_file.read().strip()
        secret_file.close()
        
        data = {
            "ultimo_id": ultimo_id
        }
        json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            URL_POST,
            data=json_bytes,
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "miliogo-cupom-client/1.0",
                "secret-key": secret_key
            },
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            resposta = resp.read().decode("utf-8")
            return json.loads(resposta)
            
    except Exception as e:
        raise e        



def main():
    ultimo_id = 0
    if os.path.exists(ARQUIVO_DB):
        conn = sqlite3.connect(ARQUIVO_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id_miliogo) FROM cupom")
        ultimo_id = cursor.fetchone()[0]
        conn.close()

    a = download(ultimo_id)
    print(f"Foram baixados {len(a)} cupons.")
    for cupom in a:
        print(cupom["id"], cupom["data_hora_emissao"], cupom["numero_cfe"])
        sqlite_sat.save_json_to_sqlite(
            cupom, 
            user_obs_inf = "download-miliogo", 
            preparar=False
        )
    print("Concluído.")

if __name__ == "__main__":
    main()
