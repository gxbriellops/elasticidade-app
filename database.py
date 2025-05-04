import sqlite3
import os
import shutil
from datetime import datetime
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("database")

def dataDado():
    """Return current datetime formatted string"""
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return data_atual

def conectar_bd():
    """Create a connection to the database with error handling"""
    try:
        conn = sqlite3.connect("dados.db")
        conn.row_factory = sqlite3.Row  # Enable row factory for named columns
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        raise

def criarBanco():
    """Create the database and required tables if they don't exist"""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        
        # Create main sales table with improved structure
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_adicionada TEXT NOT NULL,
            precoInicio REAL,
            precoFinal REAL,
            quantidadeInicio REAL,
            quantidadeFinal REAL,
            elasticidade REAL,
            produto_id INTEGER DEFAULT 1,
            observacoes TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
        """)
        
        # Create products table to support multiple products
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            categoria TEXT,
            ativo INTEGER DEFAULT 1
        )
        """)
        
        # Create costs table to track ingredient costs over time
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS custos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            data TEXT NOT NULL,
            custo_ingredientes REAL,
            custo_mao_obra REAL,
            custo_operacional REAL,
            observacoes TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
        """)
        
        # Add default product if it doesn't exist
        cursor.execute("SELECT COUNT(*) FROM produtos")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO produtos (nome, descricao, categoria) 
            VALUES ('Salgado Geral', 'Categoria geral de salgados', 'Salgados')
            """)
        
        conn.commit()
        logger.info("Banco de dados criado/verificado com sucesso")
        return True
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        return False
    finally:
        if conn:
            conn.close()

def backup_banco():
    """Create a backup of the database"""
    try:
        data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_backup = f"backup_dados_{data_atual}.db"
        
        # Ensure backups directory exists
        if not os.path.exists("backups"):
            os.makedirs("backups")
        
        # Copy the database file
        shutil.copyfile("dados.db", os.path.join("backups", nome_backup))
        logger.info(f"Backup criado com sucesso: {nome_backup}")
        return nome_backup
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        raise

def limpar_dados():
    """Clear all data from the database but keep the structure"""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        
        # Create a backup before clearing data
        backup_banco()
        
        # Clear tables but keep the structure
        cursor.execute("DELETE FROM vendas")
        cursor.execute("DELETE FROM custos")
        cursor.execute("DELETE FROM produtos WHERE id > 1")  # Keep default product
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('vendas', 'custos')")
        cursor.execute("UPDATE sqlite_sequence SET seq = 1 WHERE name = 'produtos'")
        
        conn.commit()
        logger.info("Dados limpos com sucesso")
        return True
    except sqlite3.Error as e:
        logger.error(f"Erro ao limpar dados: {e}")
        return False
    finally:
        if conn:
            conn.close()

def inserirDados(data_adicionada, precoInicio, precoFinal, quantidadeInicio, quantidadeFinal, elasticidade, produto_id=1, observacoes=None):
    """Insert sales data into the database with validation"""
    try:
        # Validate inputs
        if not all(isinstance(x, (int, float)) for x in [precoInicio, precoFinal, quantidadeInicio, quantidadeFinal]):
            raise ValueError("Valores numéricos inválidos")
        
        if precoInicio <= 0 or precoFinal <= 0:
            raise ValueError("Preços devem ser maiores que zero")
        
        if quantidadeInicio < 0 or quantidadeFinal < 0:
            raise ValueError("Quantidades não podem ser negativas")
        
        conn = conectar_bd()
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE id = ?", (produto_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Produto com ID {produto_id} não encontrado")
        
        cursor.execute("""
        INSERT INTO vendas (
            data_adicionada, 
            precoInicio, 
            precoFinal, 
            quantidadeInicio, 
            quantidadeFinal, 
            elasticidade,
            produto_id,
            observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data_adicionada, 
            precoInicio, 
            precoFinal, 
            quantidadeInicio, 
            quantidadeFinal, 
            elasticidade,
            produto_id,
            observacoes
        ))
        
        conn.commit()
        logger.info(f"Dados inseridos com sucesso: {cursor.lastrowid}")
        return cursor.lastrowid
    except (sqlite3.Error, ValueError) as e:
        logger.error(f"Erro ao inserir dados: {e}")
        raise
    finally:
        if conn:
            conn.close()

def buscarUltimosDados(produto_id=None):
    """Fetch the last inserted data, optionally filtered by product"""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            precoInicio, 
            precoFinal, 
            quantidadeInicio, 
            quantidadeFinal, 
            elasticidade 
        FROM vendas 
        """
        
        params = []
        if produto_id is not None:
            query += " WHERE produto_id = ? "
            params.append(produto_id)
        
        query += " ORDER BY id DESC LIMIT 1"
        
        cursor.execute(query, params)
        dados = cursor.fetchone()
        
        if dados:
            return tuple(dados)
        else:
            return None
    except sqlite3.Error as e:
        logger.error(f"Erro ao buscar últimos dados: {e}")
        return None
    finally:
        if conn:
            conn.close()

def atualizarElasticidade(elasticidade, registro_id=None):
    """Update elasticity on the last record or a specific record"""
    try:
        if not isinstance(elasticidade, (int, float)):
            raise ValueError("Elasticidade deve ser um valor numérico")
        
        conn = conectar_bd()
        cursor = conn.cursor()
        
        if registro_id is None:
            # Update the last record
            cursor.execute(
                "UPDATE vendas SET elasticidade = ? WHERE id = (SELECT MAX(id) FROM vendas)",
                (elasticidade,)
            )
        else:
            # Update specific record
            cursor.execute(
                "UPDATE vendas SET elasticidade = ? WHERE id = ?",
                (elasticidade, registro_id)
            )
        
        if cursor.rowcount == 0:
            raise ValueError("Nenhum registro encontrado para atualizar")
        
        conn.commit()
        logger.info(f"Elasticidade atualizada com sucesso: {elasticidade}")
        return True
    except (sqlite3.Error, ValueError) as e:
        logger.error(f"Erro ao atualizar elasticidade: {e}")
        raise
    finally:
        if conn:
            conn.close()

def buscarDados(periodo=None, produto_id=None, limit=100):
    """Fetch data with optional filtering by period and product"""
    try:
        conn = conectar_bd()
        query = """
        SELECT v.*, p.nome as produto_nome
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        """
        
        params = []
        where_clauses = []
        
        if periodo:
            data_limite = (datetime.now() - pd.Timedelta(days=periodo)).strftime('%Y-%m-%d')
            where_clauses.append("v.data_adicionada >= ?")
            params.append(data_limite)
        
        if produto_id:
            where_clauses.append("v.produto_id = ?")
            params.append(produto_id)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY v.data_adicionada DESC LIMIT ?"
        params.append(limit)
        
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except (sqlite3.Error, pd.io.sql.DatabaseError) as e:
        logger.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def cadastrar_produto(nome, descricao=None, categoria=None):
    """Register a new product"""
    try:
        if not nome or len(nome.strip()) == 0:
            raise ValueError("Nome do produto é obrigatório")
        
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO produtos (nome, descricao, categoria) 
        VALUES (?, ?, ?)
        """, (nome, descricao, categoria))
        
        conn.commit()
        logger.info(f"Produto cadastrado com sucesso: {cursor.lastrowid}")
        return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Erro ao cadastrar produto: {e}")
        raise
    finally:
        if conn:
            conn.close()

def listar_produtos(apenas_ativos=True):
    """List all products, optionally filtering for active only"""
    try:
        conn = conectar_bd()
        
        query = "SELECT * FROM produtos"
        if apenas_ativos:
            query += " WHERE ativo = 1"
        
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        logger.error(f"Erro ao listar produtos: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def registrar_custo(produto_id, custo_ingredientes, custo_mao_obra, custo_operacional, observacoes=None):
    """Register cost information for a product"""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO custos (
            produto_id, 
            data, 
            custo_ingredientes, 
            custo_mao_obra, 
            custo_operacional, 
            observacoes
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            produto_id,
            dataDado(),
            custo_ingredientes,
            custo_mao_obra,
            custo_operacional,
            observacoes
        ))
        
        conn.commit()
        logger.info(f"Custo registrado com sucesso: {cursor.lastrowid}")
        return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Erro ao registrar custo: {e}")
        raise
    finally:
        if conn:
            conn.close()

def estatisticas_produtos():
    """Get statistics about products and sales"""
    try:
        conn = conectar_bd()
        
        query = """
        SELECT 
            p.id,
            p.nome,
            COUNT(v.id) as total_registros,
            AVG(v.precoFinal) as preco_medio,
            AVG(v.quantidadeFinal) as quantidade_media,
            AVG(v.elasticidade) as elasticidade_media
        FROM produtos p
        LEFT JOIN vendas v ON p.id = v.produto_id
        WHERE p.ativo = 1
        GROUP BY p.id, p.nome
        """
        
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def exportar_dados(formato="csv"):
    """Export data to CSV or Excel format"""
    try:
        # Get data from database
        conn = conectar_bd()
        
        # Vendas data
        vendas_df = pd.read_sql_query("SELECT * FROM vendas", conn)
        
        # Produtos data
        produtos_df = pd.read_sql_query("SELECT * FROM produtos", conn)
        
        # Custos data
        custos_df = pd.read_sql_query("SELECT * FROM custos", conn)
        
        # Export path
        data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if formato.lower() == "csv":
            # Export to CSV
            if not os.path.exists("exports"):
                os.makedirs("exports")
                
            vendas_df.to_csv(f"exports/vendas_{data_atual}.csv", index=False)
            produtos_df.to_csv(f"exports/produtos_{data_atual}.csv", index=False)
            custos_df.to_csv(f"exports/custos_{data_atual}.csv", index=False)
            
            return {
                "vendas": f"exports/vendas_{data_atual}.csv",
                "produtos": f"exports/produtos_{data_atual}.csv",
                "custos": f"exports/custos_{data_atual}.csv"
            }
        elif formato.lower() == "excel":
            # Export to Excel
            if not os.path.exists("exports"):
                os.makedirs("exports")
                
            with pd.ExcelWriter(f"exports/dados_{data_atual}.xlsx") as writer:
                vendas_df.to_excel(writer, sheet_name="Vendas", index=False)
                produtos_df.to_excel(writer, sheet_name="Produtos", index=False)
                custos_df.to_excel(writer, sheet_name="Custos", index=False)
                
            return {
                "excel": f"exports/dados_{data_atual}.xlsx"
            }
        else:
            raise ValueError(f"Formato não suportado: {formato}")
    except Exception as e:
        logger.error(f"Erro ao exportar dados: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Initialize the database if this module is run directly
if __name__ == "__main__":
    criarBanco()