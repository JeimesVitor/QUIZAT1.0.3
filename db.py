import sqlite3
import os

# Caminho relativo ao diretório do script
DB_PATH = os.path.join(os.path.dirname(__file__), 'alunos.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            escola TEXT NOT NULL,
            turma TEXT NOT NULL,
            cidade TEXT,
            genero TEXT NOT NULL,
            pontuacao INTEGER NOT NULL,
            data TEXT NOT NULL DEFAULT CURRENT_DATE
        )
    ''')

    print(f"Banco de dados '{DB_PATH}' inicializado com sucesso!")

    conn.commit()
    conn.close()

init_db()
