import os
from database import criar_tabela, conectar_banco

print("⚡ --- INICIANDO VALIDAÇÃO COMPORTAMENTAL DO DATABASE --- ⚡\n")

print("1. Verificando leitura de ambiente e handshake inicial...")
conn = conectar_banco()

if conn:
    print("✅ Conexão estabelecida com sucesso na função nativa!")
    conn.close()
    print("-" * 60)
    
    print("2. Disparando a criação física das tabelas no Postgres...")
    # Chama a função que você colou para construir o Schema
    criar_tabela()
    
    print("\n📦 Verificação concluída. Vá ao Jupyter Notebook e rode os .head() para conferir!")
else:
    print("❌ Falha crítica: O database.py não conseguiu conectar.")