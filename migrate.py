import sqlite3
import os

db_path = "secure_vault.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN enc_settings BLOB")
    except: pass
    try:
        cursor.execute("ALTER TABLE transactions ADD COLUMN integrity_token TEXT")
    except: pass
    try:
        cursor.execute("ALTER TABLE caixinhas ADD COLUMN integrity_token TEXT")
    except: pass
    conn.commit()
    conn.close()
    print("Esquema do Vault atualizado para Cryptografia Atômica (v4).")
else:
    print("Banco de dados não encontrado, será criado ao iniciar o app.")
