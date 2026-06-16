import pandas as pd
from database import conectar_banco

def buscar_vendas_gerais():
    """
    Busca todas as vendas do banco trazendo os dados dos alunos e planos 
    através de JOINs e formata as colunas necessárias para o dashboard.
    """
    try:
        conn = conectar_banco()
        
        # 🔥 SQL JOIN: Juntamos as tabelas relacionais usando as Foreign Keys
        query = """
            SELECT 
                v.id_venda,
                a.nome_aluno,
                a.email,
                a.idade,
                a.genero,
                a.estado,
                p.nome_plano AS plano,
                v.valor_pago,
                v.forma_pagamento,
                v.quantidade_parcelas,
                v.canal_aquisicao,
                v.status_curso,
                v.nota_nps,
                v.inadimplente,
                v.data_venda
            FROM vendas_cursos v
            INNER JOIN alunos a ON v.id_aluno = a.id_aluno
            INNER JOIN planos p ON v.id_plano = p.id_plano;
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Tratamento de dados centralizado
        if not df.empty:
            df['data_venda'] = pd.to_datetime(df['data_venda'])
            
        return df
    except Exception as e:
        print(f"Erro na camada de dados (queries.py): {e}")
        return pd.DataFrame()


def buscar_custos_operacionais():
    """
    Busca todos os lançamentos de custos operacionais (OpEx) do banco
    para cálculo do lucro real corporativo.
    """
    try:
        conn = conectar_banco()
        query = "SELECT * FROM custo_operacional;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao buscar custos operacionais (queries.py): {e}")
        return pd.DataFrame()


# 🔥 NOVA FUNÇÃO ADICIONADA PARA CONECTAR A 5ª TABELA DE MARKETING
def buscar_custos_marketing_canal():
    """
    Busca os investimentos de tráfego pago por canal (CAC) do banco
    para distribuição na matriz de dispersão e cálculo de eficiência financeira.
    """
    try:
        conn = conectar_banco()
        query = "SELECT * FROM custo_marketing_canal;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao buscar custos de marketing por canal (queries.py): {e}")
        return pd.DataFrame()