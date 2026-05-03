import json
import urllib.request

#URL_POST = "https://miliogo.com/cupom/usuario.php"
URL_POST = "http://localhost/miliogo/cupom/usuario.php"

prompt = """
Digite >
1 para criar
2 para login
3 para alterar senha
4 para excluir conta
5 para excluir cupons
Escolha sua opção: 
"""
p = input(prompt)

if p == "1": ## Criar
    nome = input("Nome: ")
    senha = input("Senha: ")
    data = {
        "nome": nome,
        "senha": senha,
        "funcao": "criar"
    }
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
    try:
        with urllib.request.urlopen(req) as resp:
            resposta = resp.read().decode("utf-8")
            print(resposta)
    except urllib.error.URLError as e:
        print(f"Erro: {e.read().decode('utf-8')}")          

elif p == "2": ## Login
    nome = input("Nome: ")
    senha = input("Senha: ")
    data = {
        "nome": nome,
        "senha": senha,
        "funcao": "login"
    }
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
    try:
        with urllib.request.urlopen(req) as resp:
            resposta = resp.read().decode("utf-8")
            print(resposta)
    except urllib.error.URLError as e:
        print(f"Erro: {e.read().decode('utf-8')}")

elif p == "3": ## Alterar senha
    nome = input("Nome: ")
    senha_atual = input("Senha atual: ")
    nova_senha = input("Nova senha: ")
    data = {
        "nome": nome,
        "senha": senha_atual,
        "nova_senha": nova_senha,
        "funcao": "mudar_senha"
    }
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
    try:
        with urllib.request.urlopen(req) as resp:
            resposta = resp.read().decode("utf-8")
            print(resposta)
    except urllib.error.URLError as e:
        print(f"Erro: {e.read().decode('utf-8')}") 

elif p == "4": ## Excluir conta
    nome = input("Nome: ")
    senha = input("Senha: ")
    data = {
        "nome": nome,
        "senha": senha,
        "funcao": "excluir",
        "excluir_usuario": True
    }
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
    try:
        with urllib.request.urlopen(req) as resp:
            resposta = resp.read().decode("utf-8")
            print(resposta)
    except urllib.error.URLError as e:
        print(f"Erro: {e.read().decode('utf-8')}")

elif p == "5": ## Excluir cupons
    nome = input("Nome: ")
    senha = input("Senha: ")
    dias = int(input("Excluir cupons recentes (em dias, zero para todos): "))
    data = {
        "nome": nome,
        "senha": senha,
        "funcao": "excluir",
        "excluir_usuario": False,
        "dias": dias
    }
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
    try:
        with urllib.request.urlopen(req) as resp:
            resposta = resp.read().decode("utf-8")
            print(resposta)
    except urllib.error.URLError as e:
        print(f"Erro: {e.read().decode('utf-8')}")
        