import sqlite3
import os

db_path = "secure_vault.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN enc_settings BLOB")
        conn.commit()
        print("Coluna enc_settings adicionada com sucesso!")
    except sqlite3.OperationalError as e:
        print(f"Nota: {e}")
    finally:
        conn.close()
else:
    print("Banco de dados não encontrado, será criado ao iniciar o app.")
