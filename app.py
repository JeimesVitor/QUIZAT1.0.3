from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from db import init_db
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import sys
from dotenv import load_dotenv
import os


load_dotenv('.env')



# Chame o init_db para garantir que a tabela 'alunos' seja criada
init_db()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')

DB_PATH = os.getenv('DB_PATH')  # Defina um caminho único
# Definir uma senha fixa
PASSWORD = os.getenv('PASSWORD')



def gerar_grafico(escola=None, cidade=None, genero=None, idade=None, pontuacao=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Construindo a query com os filtros
    query = "SELECT pontuacao FROM alunos WHERE 1=1"
    params = []

    if escola:
        query += " AND escola LIKE ?"
        params.append(f"%{escola}%")
    if cidade:
        query += " AND cidade LIKE ?"
        params.append(f"%{cidade}%")
    if genero:
        query += " AND genero = ?"
        params.append(genero)
    if idade:
        query += " AND idade = ?"
        params.append(idade)
    if pontuacao:
        query += " AND pontuacao = ?"
        params.append(pontuacao)

    cursor.execute(query, params)
    dados = cursor.fetchall()
    conn.close()

    if not dados:
        return None  # Se não houver dados, não gera gráfico

    # Convertendo os resultados para uma lista de pontuações
    pontuacoes = [row[0] for row in dados]

    # Contando as ocorrências de cada pontuação
    unique_scores, counts = np.unique(pontuacoes, return_counts=True)

    # Calculando porcentagens
    total_alunos = len(pontuacoes)
    porcentagens = (counts / total_alunos) * 100

    # Criando o gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(unique_scores, porcentagens, color='skyblue', label="Porcentagem de Pontuação")

    # Linha da média
    media = np.mean(pontuacoes)
    ax.axhline(y=media, color='red', linestyle='--', label=f'Média: {media:.2f}')

    # Adicionando rótulos e título
    ax.set_xlabel('Pontuação')
    ax.set_ylabel('Porcentagem (%)')
    ax.set_title('Distribuição de Pontuação dos Alunos')
    ax.legend()

    # Salvando o gráfico
    grafico = 'static/grafico.png'
    fig.savefig(grafico)

    return grafico





# Função para inserir dados no banco de dados
def salvar_no_banco(nome, idade, escola, turma, cidade, genero, pontuacao):
    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        c.execute('''
        INSERT INTO alunos (nome, idade, escola, turma, cidade, genero, pontuacao)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, idade, escola, turma, cidade, genero, pontuacao))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao inserir no banco: {e}")
    finally:
        conn.close()

   




@app.route('/')
def home():
    return redirect(url_for('cadastro'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        idade = request.form.get('idade')
        escola = request.form.get('escola')
        turma = request.form.get('turma')
        cidade = request.form.get('cidade')
        genero = request.form.get('genero')

        # Verifica se todos os campos estão preenchidos
        if nome and idade and escola and turma and cidade and genero:
            # Armazenar os dados na sessão
            session['nome'] = nome
            session['idade'] = idade
            session['escola'] = escola
            session['turma'] = turma
            session['cidade'] = cidade
            session['genero'] = genero
            
            session['pontuacao'] = 0  # Inicializa a pontuação
            session['pergunta_atual'] = 0  # Começa na primeira pergunta
            return redirect(url_for('perguntas_page'))  # Atualizado
        else:
            # Se algum campo estiver vazio, retorna uma mensagem de erro
            return render_template('cadastro.html', erro="Todos os campos são obrigatórios!")

    return render_template('cadastro.html')





def get_alunos(escola=None, cidade=None, genero=None, idade=None, pontuacao=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT id, nome, escola, cidade, genero, idade, pontuacao FROM alunos WHERE 1=1"
    params = []

    if escola:
        query += " AND escola LIKE ?"
        params.append(f"%{escola}%")
    if cidade:
        query += " AND cidade LIKE ?"
        params.append(f"%{cidade}%")
    if genero:
        query += " AND genero = ?"
        params.append(genero)
    if idade:
        query += " AND idade = ?"
        params.append(idade)
    if pontuacao:
        query += " AND pontuacao = ?"
        params.append(pontuacao)
    
    cursor.execute(query, params)
    alunos = cursor.fetchall()
    conn.close()
    return alunos


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha = request.form.get('password')  
        if senha == PASSWORD:  
            session['logged_in'] = True  
            return redirect(url_for('relatorio'))  
        else:
            return render_template('login.html', erro="Senha incorreta!")

    return render_template('login.html')  


@app.route('/relatorio', methods=['GET', 'POST'])
def relatorio():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Buscar valores distintos do banco de dados
    cursor.execute("SELECT DISTINCT escola FROM alunos")
    escolas = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT cidade FROM alunos")
    cidades = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT genero FROM alunos")
    generos = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT pontuacao FROM alunos ORDER BY pontuacao ASC")
    pontuacoes = [row[0] for row in cursor.fetchall()]

    conn.close()

    # Capturar filtros do formulário
    escola = request.form.get('escola')
    cidade = request.form.get('cidade')
    genero = request.form.get('genero')
    idade = request.form.get('idade')
    pontuacao = request.form.get('pontuacao')

    # Buscar alunos aplicando os filtros
    alunos = get_alunos(escola, cidade, genero, idade, pontuacao)

    # Gerar gráfico aplicando os filtros corretamente
    grafico = gerar_grafico(escola, cidade, genero, idade, pontuacao) if alunos else None

    return render_template(
        'relatorio.html',
        alunos=alunos,
        escolas=escolas,
        cidades=cidades,
        generos=generos,
        pontuacoes=pontuacoes,
        grafico=grafico
    )








@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


# Lista das perguntas
perguntas = [
    "Você já tem ou já teve alguma fonte de renda, como salário, mesada ou dinheiro extra?",
    "Você costuma anotar ou controlar os seus gastos mensais?",
    "Você pensa em guardar parte do seu dinheiro para emergências ou para realizar sonhos no futuro?",
    "Antes de comprar algo mais caro, você pesquisa e compara preços?",
    "Você já comprou algo por impulso e depois se arrependeu?",
    "Você sabe a diferença entre 'desejo' e 'necessidade' ao comprar algo?",
    "Você já ouviu falar sobre investimentos como poupança, Tesouro Direto ou ações?",
    "Você sabe o que significa reserva de emergência?",
    "Você conversa sobre dinheiro e planejamento financeiro com sua família ou amigos?",
    "Você acha que aprender sobre educação financeira pode ajudar no seu futuro?"
]

@app.route('/perguntas', methods=['GET', 'POST'])
def perguntas_page():
    if 'indice' not in session:
        session['indice'] = 0
        session['pontuacao'] = 0

    if request.method == 'POST':
        resposta = request.form.get('resposta')
        if resposta == 'A':
            session['pontuacao'] += 10
        elif resposta == 'B':
            session['pontuacao'] += 5

        session['indice'] += 1
        if session['indice'] >= len(perguntas):
            return redirect(url_for('finalizar'))

    indice = session['indice']  # Agora é atualizado após o POST

    if indice < len(perguntas):
        return render_template('perguntas.html', pergunta=perguntas[indice], pergunta_atual=indice+1)

    return redirect(url_for('finalizar'))


@app.route('/finalizar', methods=['GET', 'POST'])
def finalizar():
    nome = session.get('nome')
    idade = session.get('idade')
    escola = session.get('escola')
    turma = session.get('turma')
    cidade = session.get('cidade')
    genero = session.get('genero')
    pontuacao = session.get('pontuacao', 0)

    # Salvar os dados no banco de dados
    salvar_no_banco(nome, idade, escola, turma, cidade, genero, pontuacao)

    session.clear()  # Reseta a sessão após finalizar
    return render_template('finalizar.html', pontuacao=pontuacao)



print("tkinter" in sys.modules)  # Retorna True se o Tkinter foi carregado


if __name__ == '__main__':
    app.run(debug=True)
