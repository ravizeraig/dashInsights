import streamlit as st
# IMPORTAÇÃO 1: Buscando a query que se conecta ao PostgreSQL do Docker
from queries import buscar_vendas_gerais
# IMPORTAÇÃO 2: Sua fábrica de blocos visuais em HTML
from components.styles import criar_banner_faturamento
# IMPORTAÇÃO 3: Sua nova Central de Filtros Modular
from components.filter import renderizar_central_de_filtros

# 1. Configuração da Janela do Navegador
st.set_page_config(
    page_title="DashInsights | BI", 
    layout="wide"  
)

# 2. Renderizando o Título Principal do Dashboard
st.title("📊 DashInsights — Performance Comercial")

# 3. Uma descrição sutil logo abaixo
st.markdown("Análise estratégica de faturamento corporativo construída bloco a bloco.")

# 4. Uma linha divisória para organizar o visual
st.markdown("---")

# =========================================================================
# BLOCO 2 & 3: CONEXÃO COM O BANCO & BANNER DE FATURAMENTO REAL
# =========================================================================

# Buscamos os dados brutos através do arquivo queries.py
df_bruto = buscar_vendas_gerais()

# Se o banco retornar os dados com sucesso (tabela não estiver vazia):
if not df_bruto.empty:
    
    # =========================================================================
    # NOVO BLOCO 4: CENTRAL DE FILTROS (BARRA LATERAL)
    # =========================================================================
    # Passamos o DataFrame bruto e recebemos apenas os dados filtrados pelo usuário
    df_filtrado = renderizar_central_de_filtros(df_bruto)
    
    # Calculamos o faturamento real somando a coluna 'valor_pago' do DataFrame FILTRADO
    faturamento_real = df_filtrado['valor_pago'].sum()

    # Chamamos a função passando o dado 100% dinâmico e filtrado do banco
    criar_banner_faturamento(faturamento_real)
    
    # Feedback visual temporário para sabermos quantas linhas restaram após filtrar
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df_bruto)} registros com base nos filtros selecionados.")

else:
    # Caso o contêiner do Docker esteja desligado ou sem dados
    st.error("Erro Crítico: A busca no banco retornou um DataFrame vazio.")

st.markdown("---")