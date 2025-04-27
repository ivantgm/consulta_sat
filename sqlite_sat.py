import sqlite3
import json
import os
from datetime import datetime

CREATE_TABLE_CUPOM = '''
CREATE TABLE IF NOT EXISTS cupom (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora_emissao TEXT,
    numero_cfe TEXT,
    numero_serie_sat TEXT,
    chave_acesso TEXT UNIQUE,
    valor_total REAL,
    total_tributos REAL,
    obs_cupom TEXT,
    obs_inf TEXT,
    emitente_cnpj TEXT,
    emitente_ie TEXT,
    emitente_im TEXT,
    emitente_nome TEXT,                   
    emitente_fantasia TEXT,
    emitente_endereco TEXT,
    emitente_bairro TEXT,
    emitente_cep TEXT,
    emitente_municipio TEXT,
    cpf_consumidor TEXT,
    razao_social_consumidor TEXT
);
CREATE INDEX IF NOT EXISTS idx_cupom_data_hora_emissao ON cupom (data_hora_emissao);
CREATE INDEX IF NOT EXISTS idx_cupom_emitente_cnpj ON cupom (emitente_cnpj);
'''

CREATE_TABLE_CUPOM_ITEM = '''
CREATE TABLE IF NOT EXISTS cupom_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cupom INTEGER,
    seq INTEGER,
    codigo TEXT,
    descricao TEXT,
    qtde REAL,
    un TEXT,
    valor_unit REAL,
    tributos REAL,
    valor_total REAL
);
CREATE INDEX IF NOT EXISTS idx_cupom_item_id_cupom ON cupom_item (id_cupom);
CREATE INDEX IF NOT EXISTS idx_cupom_item_codigo ON cupom_item (codigo);    
CREATE INDEX IF NOT EXISTS idx_cupom_item_descricao ON cupom_item (descricao);
'''

INSERT_CUPOM = '''
INSERT INTO cupom (
    data_hora_emissao,
    numero_cfe,      
    numero_serie_sat,       
    chave_acesso,           
    valor_total,            
    obs_cupom,              
    obs_inf,                
    total_tributos,         
    emitente_cnpj,          
    emitente_ie,            
    emitente_im,           
    emitente_nome,          
    emitente_fantasia,      
    emitente_endereco,      
    emitente_bairro,        
    emitente_cep,           
    emitente_municipio,     
    cpf_consumidor,         
    razao_social_consumidor            
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

INSERT_CUPOM_ITEM = '''
INSERT INTO cupom_item (
    id_cupom,
    seq,
    codigo,
    descricao,
    qtde,
    un,
    valor_unit,
    tributos,
    valor_total
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

def save_json_to_sqlite(cupom, user_obs_inf=""):
    db_file = "banco.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.executescript(CREATE_TABLE_CUPOM)

    data_hora_emissao       = cupom["data_hora_emissao"]
    numero_cfe              = cupom["numero_cfe"]
    numero_serie_sat        = cupom["numero_serie_sat"]
    chave_acesso            = cupom["chave_acesso"]
    valor_total             = cupom["valor_total"]
    obs_cupom               = cupom["obs"]
    obs_inf                 = user_obs_inf
    total_tributos          = cupom["total_tributos"]
    emitente_cnpj           = cupom["emitente"]["cnpj"]
    emitente_ie             = cupom["emitente"]["ie"]
    emitente_im             = cupom["emitente"]["im"]
    emitente_nome           = cupom["emitente"]["nome"]
    emitente_fantasia       = cupom["emitente"]["fantasia"]
    emitente_endereco       = cupom["emitente"]["endereco"]
    emitente_bairro         = cupom["emitente"]["bairro"]
    emitente_cep            = cupom["emitente"]["cep"]
    emitente_municipio      = cupom["emitente"]["municipio"]
    cpf_consumidor          = cupom["consumidor"]["cpf_consumidor"]
    razao_social_consumidor = cupom["consumidor"]["razao_social_consumidor"]

    data_hora_emissao = prepare_datetime(data_hora_emissao)
    valor_total = prepare_float(valor_total)
    total_tributos = prepare_float(total_tributos)

    cupom_data = (
        data_hora_emissao,
        numero_cfe,
        numero_serie_sat,
        chave_acesso,
        valor_total,
        obs_cupom,
        obs_inf,
        total_tributos,
        emitente_cnpj,
        emitente_ie,
        emitente_im,
        emitente_nome,
        emitente_fantasia,
        emitente_endereco,
        emitente_bairro,
        emitente_cep,
        emitente_municipio,
        cpf_consumidor,
        razao_social_consumidor
    )
    cursor.execute(INSERT_CUPOM, cupom_data)
    last_insert_id = cursor.lastrowid

    cursor.executescript(CREATE_TABLE_CUPOM_ITEM)

    for item in cupom["itens"]:
        seq = item["seq"]
        codigo = item["codigo"]
        descricao = item["descricao"]
        qtde = item["qtde"]
        un = item["un"]
        valor_unit = item["valor_unit"]
        tributos = item["tributos"]
        valor_total_item = item["valor_total"]

        qtde = prepare_float(qtde)
        valor_unit = prepare_float(valor_unit)
        tributos = prepare_float(tributos)
        valor_total_item = prepare_float(valor_total_item)

        cupom_item_data = (
            last_insert_id,
            seq,
            codigo,
            descricao,
            qtde,
            un,
            valor_unit,
            tributos,
            valor_total_item
        )
        cursor.execute(INSERT_CUPOM_ITEM, cupom_item_data)    

    conn.commit()
    conn.close()

def prepare_datetime(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y - %H:%M:%S").strftime("%Y%m%d%H%M%S")

def prepare_float(value):
    return float(
        value
            .replace(".", "")
            .replace(",", ".")
            .replace("(", "")
            .replace(")", "")
            .replace("X\n", "")
            .strip()
        )

if __name__ == "__main__":
    json_file_path = "./json/35250447603246000111590012086000099597428471.json"
    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
            save_json_to_sqlite(json_data)
