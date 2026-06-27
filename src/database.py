import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import streamlit as st  # 🔥 Adicionado para ler as secrets da nuvem

# 🔥 SISTEMA INTELIGENTE DE BUSCA DO .ENV (Para rodar local na sua máquina)
if not load_dotenv():  
    if not load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env')):
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'infra', '.env'))

def conectar_banco():
    try:
        # =========================================================================
        # ☁️ MODO ATIVO NA NUVEM: Se detectar as Secrets do Streamlit Cloud
        # =========================================================================
        if hasattr(st, "secrets") and "DB_HOST" in st.secrets:
            host = st.secrets["DB_HOST"]
            port = st.secrets["DB_PORT"]
            database = st.secrets["DB_NAME"]
            user = st.secrets["DB_USER"]
            password = st.secrets["DB_PASSWORD"]
        
        # =========================================================================
        # 💻 MODO LOCAL: Fallback para ler o arquivo .env da sua máquina
        # =========================================================================
        else:
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT")
            database = os.getenv("DB_NAME")
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
        
        # Faz a conexão limpa (funciona tanto para as variáveis locais quanto nuvem)
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=3  
        )
        return conn
        
    except OperationalError as e:
        print("\n❌ [Erro Crítico de Conexão] Não foi possível alcançar o banco de dados!")
        print(f"   • Dados lidos -> Host: {host} | Porta: {port} | Banco: {database} | Usuário: {user}")
        print(f"   • Detalhes do erro do Postgres: {e}\n")
        return None

# ... O RESTANTE DO SEU CÓDIGO (criar_tabela) CONTINUA IGUAL ABAIXO ...                
def criar_tabela():
    """
    Cria a arquitetura relacional do ecossistema de BI (5 tabelas integradas e regionalizadas).
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

        # 4. TABELA ATUALIZADA: Custo de Marketing por Canal e Região (Foco Geográfico)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custo_marketing_canal (
                id_custo_canal SERIAL PRIMARY KEY,
                mes_referencia VARCHAR(7) NOT NULL,    -- Formato 'YYYY-MM'
                canal_aquisicao VARCHAR(50) NOT NULL,  -- 'Google Ads', 'Meta Ads', etc.
                estado_foco VARCHAR(2) NOT NULL,       -- Identificador geográfico ('SP', 'SC')
                valor_investido NUMERIC(10,2) NOT NULL -- Valor injetado na plataforma
            );
        """)
        
        # 5. Tabela Principal de Vendas (Tabela Fato)
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
        print("✅ [Database] Todas as 5 tabelas de alta performance foram criadas com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao criar a estrutura de tabelas: {e}")
    finally:
        cursor.close()
        conn.close()