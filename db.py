import sqlite3

DB_PATH = r'C:\QUIZAT1.0.3\alunos.db' 

def init_db():
    # Conectar ao banco de dados (será criado se não existir)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Verificar se a tabela alunos existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alunos';")
    if not c.fetchone():
        # Criar a tabela de alunos caso não exista
        c.execute('''
        CREATE TABLE alunos (
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

        print("Tabela 'alunos' criada com sucesso!")
    else:
        print("Tabela 'alunos' já existe.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
