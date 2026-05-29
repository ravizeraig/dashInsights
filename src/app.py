import streamlit as st
import plotly.express as px
# Importando a função da nossa camada de dados isolada
from queries import buscar_vendas_gerais

# Configuração de Layout Executivo
st.set_page_config(page_title="DashInsights | Inteligência", layout="wide")

# Customização visual dos Cards de Métricas
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 DashInsights - Painel Executivo de Vendas")
st.markdown("---")

# Consumindo a camada de dados
df = buscar_vendas_gerais()

if not df.empty:
    # 1. Filtro Lateral baseado na coluna 'plano'
    st.sidebar.header("Filtros")
    planos_disponiveis = st.sidebar.multiselect(
        "Filtrar por Plano", 
        options=df['plano'].unique(), 
        default=df['plano'].unique()
    )
    
    # Aplicando o filtro no DataFrame
    df_filtrado = df[df['plano'].isin(planos_disponiveis)]
    
    # 2. Cálculo dos KPIs com as colunas reais do banco
    faturamento_total = df_filtrado['valor_pago'].sum()
    total_alunos = len(df_filtrado)
    nps_medio = df_filtrado['nota_nps'].mean()
    
    # Calculando a taxa de inadimplência baseada na coluna booleana 'inadimplente'
    # Como 'True' equivale a 1 e 'False' a 0, a média nos dá a proporção de inadimplentes
    taxa_inadimplencia = df_filtrado['inadimplente'].mean() * 100
    
    # 3. Exibição dos KPIs Principais (Cards)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
    with col2:
        st.metric("Alunos Ativos", f"{total_alunos}")
    with col3:
        st.metric("NPS Médio", f"{nps_medio:.1f}")
    with col4:
        st.metric("Inadimplência", f"{taxa_inadimplencia:.1f}%")
        
    st.markdown("---")
    
    # 4. Gráficos Visuais de Alta Performance
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.subheader("💰 Desempenho Financeiro por Plano")
        df_grafico = df_filtrado.groupby('plano')['valor_pago'].sum().reset_index()
        fig_barras = px.bar(df_grafico, x='plano', y='valor_pago', color='plano', 
                             labels={'plano': 'Plano', 'valor_pago': 'Faturamento (R$)'},
                             template="plotly_white")
        st.plotly_chart(fig_barras, use_container_width=True)
        
    with col_graph2:
        st.subheader("📈 Tendência de Ingressos de Alunos")
        # Agrupando os dados por mês para ver a linha de crescimento
        df_mensal = df_filtrado.set_index('data_venda').resample('ME').size().reset_index(name='quantidade_vendas')
        fig_linha = px.line(df_mensal, x='data_venda', y='quantidade_vendas', markers=True,
                             labels={'data_venda': 'Mês', 'quantidade_vendas': 'Novos Alunos'},
                             template="plotly_white")
        st.plotly_chart(fig_linha, use_container_width=True)

    # 5. Tabela de Dados Detalhada (Opcional/Expansível)
    with st.expander("Ver Detalhamento dos Registros de Alunos"):
        st.dataframe(df_filtrado.sort_values(by='data_venda', ascending=False), use_container_width=True)

else:
    st.error("Falha ao carregar a camada de dados do projeto.")