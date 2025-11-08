import sqlite3

nfces = []
sats = []
nfces_lines = dict()
sats_lines = dict()

f = open("urls.txt", "r")
for line in f:
    idx = line.find("?p=")
    if idx != -1:
        chave = line[idx+3:idx+47]
        nfces.append(chave)
        nfces_lines[chave] = line.strip()
f.close()

f = open("chaves.txt", "r")
for line in f:
    idx = line.find(".")
    if idx != -1:
        chave = line[idx+1:idx+45]
        sats.append(chave)
        sats_lines[chave] = line.strip()
f.close()

db_file = "banco.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

for chave in nfces:
    cursor.execute("select id from cupom where chave_acesso = ?", (chave,))
    row = cursor.fetchone()
    if not row:
        print(nfces_lines[chave])
    else:
        id_cupom = row[0]
        cursor.execute("update cupom set url_consulta = ? where id = ?", (nfces_lines[chave], id_cupom))

for chave in sats:
    cursor.execute("select id from cupom where chave_acesso = ?", (chave,))
    row = cursor.fetchone()
    if not row:
        print(sats_lines[chave])

conn.commit()
conn.close()