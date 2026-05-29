import random
from faker import Faker
from database import conectar_banco, criar_tabela
import config_regras as regras

fake = Faker('pt_BR')

def popular_banco(total_registros=1200):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Limpa dados anteriores para evitar duplicações em testes
    cursor.execute("TRUNCATE TABLE vendas_cursos;")
    
    print(f"🚀 [Engine] Gerando {total_registros} registros corporativos modulares...")
    
    for _ in range(total_registros):
        plano = random.choice(list(regras.PLANOS.keys()))
        valor = regras.PLANOS[plano]
        forma_pagto = random.choice(regras.FORMAS_PAGAMENTO)
        
        # Regra de Parcelas baseada na forma de pagamento
        if forma_pagto == 'À Vista':
            parcelas = 1
        else:
            parcelas = random.randint(2, 12)
            
        # Regra de inadimplência (Boleto tem mais risco)
        inadimplente = False
        if forma_pagto == 'Parcelado Boleto':
            inadimplente = random.choices([True, False], weights=[30, 70])[0] # 30% risco
            
        # Dados do Aluno
        nome = fake.name()
        email = fake.email()
        idade = random.randint(22, 55) # Público corporativo de alto padrão
        genero = random.choice(regras.GENEROS)
        estado = random.choice(regras.ESTADOS)
        
        # Dados de engajamento e satisfação
        canal = random.choice(regras.CANAIS_AQUISICAO)
        status = random.choice(regras.STATUS_CURSO)
        nps = random.randint(1, 10) # Nota de satisfação de 1 a 10
        
        data_venda = fake.date_between(start_date='-1y', end_date='today')
        
        cursor.execute("""
            INSERT INTO vendas_cursos (
                nome_aluno, email, idade, genero, plano, valor_pago, 
                estado, forma_pagamento, quantidade_parcelas, 
                canal_aquisicao, status_curso, nota_nps, inadimplente, data_venda
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (nome, email, idade, genero, plano, valor, estado, forma_pagto, parcelas, canal, status, nps, inadimplente, data_venda))
        
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ [Engine] Sucesso! Banco de dados populado com as novas métricas de Diretoria.")

if __name__ == "__main__":
    # 1. Cria a tabela se ela não existir
    criar_tabela()
    # 2. Popula o banco com os dados estruturados
    popular_banco()