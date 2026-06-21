import random
from datetime import datetime
from faker import Faker
from database import conectar_banco, criar_tabela
import config_regras as regras

# Inicializa o gerador oficial em português brasileiro
fake = Faker('pt_BR')

def popular_banco(total_registros=2630):
    conn = conectar_banco()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados.")
        return
    
    cursor = conn.cursor()
    
    # -------------------------------------------------------------------------
    # PASSAGEM DO RODO: Limpa dados antigos mantendo a integridade referencial
    # -------------------------------------------------------------------------
    print("🧹 [Engine] Limpando dados antigos das 5 tabelas relacionais...")
    cursor.execute("""
        TRUNCATE TABLE vendas_cursos, alunos, planos, custo_operacional, custo_marketing_canal 
        RESTART IDENTITY CASCADE;
    """)
    
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
    # STEP 2: Popular a tabela de CUSTO OPERACIONAL (OpEx) e MARKETING por REGIÃO
    # -------------------------------------------------------------------------
    print("📉 [Engine] Lançando folha de pagamento, infraestrutura e marketing retroativos...")
    # 🔥 EVOLUÇÃO: Gera uma sequência contínua de 3 anos e meio (2023, 2024, 2025 e 2026)
    meses_gerar = (
        [f"2023-{m:02d}" for m in range(1, 13)] +  # Todo o ano de 2023
        [f"2024-{m:02d}" for m in range(1, 13)] +  # Todo o ano de 2024
        [f"2025-{m:02d}" for m in range(1, 13)] +  # Todo o ano de 2025
        [f"2026-{m:02d}" for m in range(1, 7)]     # Primeiro semestre de 2026
    )   
    
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

        # Injetando investimentos com foco regionalizado (estado_foco)
        pesos_investimento = {
            'Google Ads': 15000.00,
            'Meta Ads': 12000.00,
            'YouTube': 8000.00,
            'E-mail Marketing': 1500.00,
            'Orgânico': 0.00,
            'Indicação': 0.00
        }
        
        for canal, valor_base in pesos_investimento.items():
            estado_campanha = random.choice(regras.ESTADOS) if valor_base > 0 else 'BR'
            variacao = random.uniform(0.85, 1.15) if valor_base > 0 else 1.0
            valor_final = round(valor_base * variacao, 2)
            
            cursor.execute("""
                INSERT INTO custo_marketing_canal (mes_referencia, canal_aquisicao, estado_foco, valor_investido)
                VALUES (%s, %s, %s, %s);
            """, (mes, canal, estado_campanha, valor_final))

    # -------------------------------------------------------------------------
    # STEP 3: Loop Principal - Gerar Alunos e suas respectivas Vendas (Tabela Fato)
    # -------------------------------------------------------------------------
    print(f"🚀 [Engine] Gerando {total_registros} contratos B2B cruzando chaves...")
    
    for i in range(total_registros):
        nome = fake.name()
        
        # Criação de e-mail limpo e incremental baseado no Faker
        email_base = fake.free_email()
        email_usuario, dominio = email_base.split('@')
        email = f"{email_usuario}_{i}@{dominio}" 
        
        idade = random.randint(22, 55)
        genero = random.choice(regras.GENEROS) 
        estado = random.choice(regras.ESTADOS)        

        cursor.execute("""
            INSERT INTO alunos (nome_aluno, email, idade, genero, estado)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_aluno;
        """, (nome, email, idade, genero, estado))
        id_aluno_gerado = cursor.fetchone()[0]
        
        plano_nome = random.choice(list(regras.PLANOS.keys()))
        id_plano_relacionado = id_planos_mapeados[plano_nome]
        valor_pago = rules_valor if (rules_valor := regras.PLANOS[plano_nome]) else 0.0
        
        forma_pagto = random.choice(regras.FORMAS_PAGAMENTO)
        canal = random.choice(regras.CANAIS_AQUISICAO)
        status = random.choice(regras.STATUS_CURSO)
        nps = random.randint(1, 10)
        
        # Escopo temporal de 1 ano
        ano = random.choice([2025, 2026])
        mes_venda = random.randint(1, 12) if ano == 2025 else random.randint(1, 6)
        dia = random.randint(1, 28)
        data_venda = f"{ano}-{mes_venda:02d}-{dia:02d}"
        
        parcelas = 1 if forma_pagto == 'À Vista' else random.randint(2, 12)
            
        inadimplente = False
        if forma_pagto == 'Parcelado Boleto':
            inadimplente = random.choices([True, False], weights=[30, 70])[0]
        
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
    print(f"✅ [Engine] Sucesso Absoluto! Ecossistema de BI relacional povoado com {total_registros} registros via Faker.")

if __name__ == "__main__":
    criar_tabela()
    popular_banco()