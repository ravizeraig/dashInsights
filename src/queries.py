import pandas as pd
from database import conectar_banco

def buscar_vendas_gerais():
    """Busca todas as vendas do banco e formata as colunas necessárias."""
    try:
        conn = conectar_banco()
        query = "SELECT * FROM vendas_cursos;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Tratamento de dados centralizado
        if not df.empty:
            df['data_venda'] = pd.to_datetime(df['data_venda'])
            
        return df
    except Exception as e:
        print(f"Erro na camada de dados (queries.py): {e}")
        return pd.DataFrame()