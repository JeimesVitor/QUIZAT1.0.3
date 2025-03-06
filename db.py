import sqlite3
import os

# Caminho relativo para o banco de dados
DB_PATH = os.path.join(os.getcwd(), 'alunos.db')

def init_db():
    # Conectar ao banco de dados (será criado se não existir)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Criar a tabela de alunos caso não exista
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

    print("Banco de dados inicializado com sucesso!")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
