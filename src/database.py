import psycopg2
from psycopg2 import OperationalError

import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def conectar_banco():
    try:
        # Puxamos os dados direto do seu .env de forma protegida
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=os.getenv("DB_PORT", "5433"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD") # Lê a senha 'admin_password_123' com segurança
        )
        return conn
    except OperationalError as e:
        print(f"❌ Erro ao conectar no PostgreSQL: {e}")
        return None
    
def criar_tabela():
    """
    Cria a arquitetura relacional do ecossistema de BI (4 tabelas integradas).
    """
    conn = conectar_banco()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        print("🏗️  [Database] Construindo arquitetura relacional no Postgres...")
        
        # 1. Tabela de Planos (Dimensão)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planos (
                id_plano SERIAL PRIMARY KEY,
                nome_plano VARCHAR(50) UNIQUE NOT NULL,
                valor_tabela NUMERIC(10,2) NOT NULL
            );
        """)
        
        # 2. Tabela de Alunos (Dimensão)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id_aluno SERIAL PRIMARY KEY,
                nome_aluno VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                idade INT NOT NULL,
                genero VARCHAR(20) NOT NULL,
                estado VARCHAR(2) NOT NULL
            );
        """)
        
        # 3. Tabela de Custo Operacional - OpEx (Dimensão/Lancamentos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custo_operacional (
                id_custo SERIAL PRIMARY KEY,
                mes_referencia VARCHAR(7) NOT NULL, -- Formato 'YYYY-MM'
                categoria VARCHAR(50) NOT NULL,     -- 'Folha de Pagamento', 'Infraestrutura'
                descricao VARCHAR(150) NOT NULL,    -- 'Salário Diretor', 'Servidores AWS'
                valor_custo NUMERIC(10,2) NOT NULL
            );
        """)
        
        # 4. Tabela Principal de Vendas (Tabela Fato)
        # Ela se conecta com alunos e planos através de chaves estrangeiras (FOREIGN KEY)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas_cursos (
                id_venda SERIAL PRIMARY KEY,
                id_aluno INT REFERENCES alunos(id_aluno) ON DELETE CASCADE,
                id_plano INT REFERENCES planos(id_plano),
                valor_pago NUMERIC(10,2) NOT NULL,
                forma_pagamento VARCHAR(50) NOT NULL,
                quantidade_parcelas INT NOT NULL,
                canal_aquisicao VARCHAR(50) NOT NULL,
                status_curso VARCHAR(50) NOT NULL,
                nota_nps INT NOT NULL,
                inadimplente BOOLEAN NOT NULL DEFAULT FALSE,
                data_venda DATE NOT NULL
            );
        """)
        
        conn.commit()
        print("✅ [Database] Todas as 4 tabelas de alta performance foram criadas com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao criar a estrutura de tabelas: {e}")
    finally:
        cursor.close()
        conn.close()