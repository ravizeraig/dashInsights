import os
from dotenv import load_dotenv
import psycopg2

print("⏳ [TASK 1.2] Iniciando script de diagnóstico...")

# Força a busca do .env usando caminhos relativos para não ter erro de pasta
if not load_dotenv():
    if not load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env')):
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'infra', '.env'))

print("\n🔍 --- CREDENCIAIS QUE O PYTHON LEU DO .ENV ---")
print(f"   • Host:     {os.getenv('DB_HOST')}")
print(f"   • Porta:    {os.getenv('DB_PORT')}")
print(f"   • Banco:    {os.getenv('DB_NAME')}")
print(f"   • Usuário:  {os.getenv('DB_USER')}")
print(f"   • Senha:    {'******' if os.getenv('DB_PASSWORD') else 'Vazia/None'}")
print("-----------------------------------------------\n")

print("📡 Tentando disparar o handshake com o Docker...")
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=3 # Se o Docker não responder em 3s, ele aborta
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    versao = cursor.fetchone()
    print("\n✅ SINAL VERDE: CONEXÃO ESTABELECIDA COM SUCESSO!")
    print(f"   • {versao[0]}\n")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"\n❌ ERRO DETECTADO NA CONEXÃO: {e}\n")