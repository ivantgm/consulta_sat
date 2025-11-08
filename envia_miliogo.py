import json
import sqlite3
import os
import urllib.request

# ====== CONFIGURAÇÕES ======
ARQUIVO_DB = "banco.db"
#URL_POST = "http://localhost/miliogo/cupom/import_json.php"
URL_POST = "https://miliogo.com/cupom/import_json.php"
# ============================

def enviar_json(data):
    """Envia um JSON via POST para o servidor PHP"""
    try:
        secret_file_name = "secret_key.txt"
        if not os.path.isfile(secret_file_name):
            raise FileNotFoundError(f"Arquivo de segredo não encontrado: {secret_file_name}")
        secret_file = open(secret_file_name, "r")
        secret_key = secret_file.read().strip()
        secret_file.close()
        
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
            print("Resposta:", resposta)
    except Exception as e:
        raise e        

def carregar_cupons(conn):
    """Carrega todos os cupons com emitente e itens"""
    cupons = []
    cursor = conn.cursor()

    # Busca todos os cupons
    cursor.execute("SELECT * FROM cupom WHERE enviado = 0")
    cupons_db = cursor.fetchall()
    colunas_cupom = [desc[0] for desc in cursor.description]

    for cupom_row in cupons_db:
        cupom = dict(zip(colunas_cupom, cupom_row))

        # Atualiza o status do cupom para enviado
        cursor.execute("UPDATE cupom SET enviado = 1 WHERE id = ?", (cupom["id"],))

        # Emitente
        cursor.execute("SELECT * FROM emitente WHERE cnpj = ?", (cupom["cnpj_emitente"],))
        emitente = cursor.fetchone()
        if emitente:
            emitente_dict = dict(zip([d[0] for d in cursor.description], emitente))
        else:
            emitente_dict = {}


        # Itens
        cursor.execute("SELECT * FROM cupom_item WHERE id_cupom = ?", (cupom["id"],))
        itens = cursor.fetchall()
        colunas_itens = [desc[0] for desc in cursor.description]
        itens_list = []
        for item in itens:
            item_dict = dict(zip(colunas_itens, item))
            item_dict.pop("id", None)
            item_dict.pop("id_cupom", None)
            itens_list.append(item_dict)

        # Monta JSON no formato esperado
        cupom_json = {
            "obs": cupom.get("obs", ""),
            "emitente": emitente_dict,
            "consumidor": {
                "cpf_consumidor": "",
                "razao_social_consumidor": ""                
            },
            "itens": itens_list,
            "chave_acesso": cupom.get("chave_acesso"),
            "url_consulta": cupom.get("url_consulta"),
            "numero_cfe": cupom.get("numero_cfe"),
            "numero_serie_sat": cupom.get("numero_serie_sat"),
            "data_hora_emissao": cupom.get("data_hora_emissao"),
            "valor_total": cupom.get("valor_total"),
            "total_tributos": cupom.get("total_tributos")
        }

        cupons.append(cupom_json)

    return cupons


def main():
    conn = sqlite3.connect(ARQUIVO_DB)
    conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna

    cupons = carregar_cupons(conn)
    print(f"Encontrados {len(cupons)} cupons para envio.\n")

    for i, cupom in enumerate(cupons, 1):
        print(f"Enviando cupom {i}/{len(cupons)} - chave {cupom['chave_acesso']}")
        enviar_json(cupom)
        print("-" * 50)

    conn.commit()
    conn.close()
    print("Processo concluído!")


if __name__ == "__main__":
    main()
