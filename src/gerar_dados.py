import random
from datetime import datetime
from faker import Faker
from database import conectar_banco, criar_tabela
import config_regras as regras

fake = Faker('pt_BR')

def popular_banco(total_registros=1200):
    conn = conectar_banco()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados.")
        return
    
    cursor = conn.cursor()
    
    # -------------------------------------------------------------------------
    # PASSAGEM DO RODO: Limpa todas as tabelas na ordem correta devido às Foreign Keys
    # -------------------------------------------------------------------------
    print("🧹 [Engine] Limpando dados antigos das tabelas relacionais...")
    cursor.execute("TRUNCATE TABLE vendas_cursos, alunos, planos, custo_operacional RESTART IDENTITY CASCADE;")
    
    # -------------------------------------------------------------------------
    # STEP 1: Popular a tabela de PLANOS e capturar os IDs gerados
    # -------------------------------------------------------------------------
    print("🏗️ [Engine] Cadastrando planos de alto padrão B2B...")
    id_planos_mapeados = {}
    for nome_plano, valor_tabela in regras.PLANOS.items():
        cursor.execute("""
            INSERT INTO planos (nome_plano, valor_tabela) 
            VALUES (%s, %s) RETURNING id_plano;
        """, (nome_plano, valor_tabela))
        id_planos_mapeados[nome_plano] = cursor.fetchone()[0]

    # -------------------------------------------------------------------------
# -------------------------------------------------------------------------
    # STEP 2: Popular a tabela de CUSTO OPERACIONAL (OpEx) dos últimos 12 meses
    # -------------------------------------------------------------------------
    print("📉 [Engine] Lançando folha de pagamento e custos de infraestrutura retroativos...")
    # Vamos gerar custos para os meses de 2025 e 2026 para cobrir o período das vendas
    meses_gerar = [f"2025-{m:02d}" for m in range(1, 13)] + [f"2026-{m:02d}" for m in range(1, 7)]
    
    for mes in meses_gerar:
        # Lançando a Folha de Pagamento fixa do mês
        for cargo, salario in regras.FOLHA_PAGAMENTO.items():
            cursor.execute("""
                INSERT INTO custo_operacional (mes_referencia, categoria, descricao, valor_custo)
                VALUES (%s, 'Folha de Pagamento', %s, %s);
            """, (mes, cargo, salario))
            
        # Lançando a Infraestrutura fixa do mês
        for sistema, custo in regras.INFRAESTRUTURA_MENSAL.items():
            cursor.execute("""
                INSERT INTO custo_operacional (mes_referencia, categoria, descricao, valor_custo)
                VALUES (%s, 'Infraestrutura', %s, %s);
            """, (mes, sistema, custo))
            
        # Lançando o Bônus de Metas do mês
        cursor.execute("""
            INSERT INTO custo_operacional (mes_referencia, categoria, descricao, valor_custo)
            VALUES (%s, 'Comercial', 'Bônus de Metas do Time', %s);
        """, (mes, regras.BONUS_METAS_MES))
# -------------------------------------------------------------------------
    # STEP 3: Loop Principal - Gerar Alunos e suas respectivas Vendas (Tabela Fato)
    # -------------------------------------------------------------------------
    print(f"🚀 [Engine] Gerando {total_registros} contratos B2B cruzando chaves...")
    
    for i in range(total_registros): # <- Mudamos de '_' para 'i' para usar o número como contador único
        # 1. Cria os dados demográficos do Aluno
        nome = fake.name()
        
        # 🔥 SOLUÇÃO: Injetamos o número do loop 'i' antes do @ para garantir e-mails 100% únicos
        email_base = fake.free_email() # Usar free_email evita alguns domínios repetidos do Faker
        email_usuario, dominio = email_base.split('@')
        email = f"{email_usuario}_{i}@{dominio}" 
        
        idade = random.randint(22, 55)
        genero = random.choice(regras.GENEROS) 
        estado = random.choice(regras.ESTADOS)        
        # Insere o aluno e captura o ID gerado pelo SERIAL do Postgres
        cursor.execute("""
            INSERT INTO alunos (nome_aluno, email, idade, genero, estado)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_aluno;
        """, (nome, email, idade, genero, estado))
        id_aluno_gerado = cursor.fetchone()[0]
        
        # 2. Sorteia as regras da Venda Corporativa
        plano_nome = random.choice(list(regras.PLANOS.keys()))
        id_plano_relacionado = id_planos_mapeados[plano_nome]
        valor_pago = regras.PLANOS[plano_nome]
        
        forma_pagto = random.choice(regras.FORMAS_PAGAMENTO)
        canal = random.choice(regras.CANAIS_AQUISICAO)
        status = random.choice(regras.STATUS_CURSO)
        nps = random.randint(1, 10)
        data_venda = fake.date_between(start_date='-1y', end_date='today')
        
        # Regra de Parcelas
        parcelas = 1 if forma_pagto == 'À Vista' else random.randint(2, 12)
            
        # Regra de inadimplência (Boleto corporativo tem risco de 30%)
        inadimplente = False
        if forma_pagto == 'Parcelado Boleto':
            inadimplente = random.choices([True, False], weights=[30, 70])[0]
        
        # 3. Insere na Tabela Fato (vendas_cursos) usando os IDs de ligação
        cursor.execute("""
            INSERT INTO vendas_cursos (
                id_aluno, id_plano, valor_pago, forma_pagamento, 
                quantidade_parcelas, canal_aquisicao, status_curso, 
                nota_nps, inadimplente, data_venda
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (id_aluno_gerado, id_plano_relacionado, valor_pago, forma_pagto, 
              parcelas, canal, status, nps, inadimplente, data_venda))
        
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ [Engine] Sucesso Absoluto! Ecossistema de BI relacional povoado.")

if __name__ == "__main__":
    # 1. Cria a nova arquitetura de tabelas se não existirem
    criar_tabela()
    # 2. Executa a carga pesada relacional
    popular_banco()