import os
import psycopg2
from dotenv import load_dotenv

# Caminho absoluto à prova de falhas para o arquivo .env na raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Caminho da pasta 'src'
ENV_PATH = os.path.join(BASE_DIR, '..', '.env')       # Volta uma pasta e acha o '.env'

# Carrega o .env explicitamente
load_dotenv(dotenv_path=ENV_PATH)

def conectar_banco():
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    
    # PRINT DE DIAGNÓSTICO DIDÁTICO (Para o seu produto/curso)
    print("\n🔍 --- [DEBUG DE CONEXÃO] ---")
    print(f"Lendo do .env -> HOST: {host} | PORTA: {port} | USUÁRIO: {user} | BANCO: {database}")
    print("-----------------------------\n")
    
    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas_cursos (
            id SERIAL PRIMARY KEY,
            nome_aluno VARCHAR(150),
            email VARCHAR(150),
            idade INT,
            genero VARCHAR(20),
            plano VARCHAR(50),
            valor_pago NUMERIC(10, 2),
            estado VARCHAR(2),
            forma_pagamento VARCHAR(50),
            quantidade_parcelas INT,
            canal_aquisicao VARCHAR(50),
            status_curso VARCHAR(50),
            nota_nps INT,
            inadimplente BOOLEAN,
            data_venda DATE
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("ℹ️ [Database] Tabela 'vendas_cursos' verificada/criada com sucesso.")