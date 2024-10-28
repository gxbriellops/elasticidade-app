import sqlite3
from datetime import datetime

def dataDado():
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return data_atual

# Função para criar o banco de dados e a tabela (executar uma única vez)
def criarBanco():
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_adicionada TEXT NOT NULL,
        precoInicio REAL,
        precoFinal REAL,
        quantidadeInicio REAL,
        quantidadeFinal REAL,
        elasticidade REAL
    )
    """)
    conn.commit()
    conn.close()

# Função para inserir dados no banco de dados
def inserirDados(data_adicionada, precoInicio, precoFinal, quantidadeInicio, quantidadeFinal, elasticidade):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("""INSERT INTO vendas (data_adicionada, precoInicio, precoFinal, quantidadeInicio, quantidadeFinal, elasticidade)
                  VALUES (?, ?, ?, ?, ?, ?)""", (data_adicionada, precoInicio, precoFinal, quantidadeInicio, quantidadeFinal, elasticidade))
    conn.commit()
    conn.close()

# Função para buscar os últimos dados inseridos
def buscarUltimosDados():
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("SELECT precoInicio, precoFinal, quantidadeInicio, quantidadeFinal, elasticidade FROM vendas ORDER BY id DESC LIMIT 1")
    dados = c.fetchone()
    conn.close()
    return dados

# Função para atualizar a elasticidade no último registro
def atualizarElasticidade(elasticidade):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("UPDATE vendas SET elasticidade = ? WHERE id = (SELECT MAX(id) FROM vendas)", (elasticidade,))
    conn.commit()
    conn.close()