import sqlite3

nfces = []
sats = []

f = open("urls.txt", "r")
for line in f:
    idx = line.find("?p=")
    if idx != -1:
        chave = line[idx+3:idx+47]
        nfces.append(chave)
f.close()

f = open("chaves.txt", "r")
for line in f:
    idx = line.find(".")
    if idx != -1:
        chave = line[idx+1:idx+45]
        sats.append(chave)
f.close()

db_file = "banco.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

for chave in nfces:
    cursor.execute("select id from cupom where chave_acesso = ?", (chave,))
    row = cursor.fetchone()
    if not row:
        print(f"NFCe {chave} não encontrada no banco de dados.")

for chave in sats:
    cursor.execute("select id from cupom where chave_acesso = ?", (chave,))
    row = cursor.fetchone()
    if not row:
        print(f"SAT {chave} não encontrada no banco de dados.")

conn.close()