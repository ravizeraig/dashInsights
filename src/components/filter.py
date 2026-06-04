import streamlit as st

def renderizar_central_de_filtros(df):
    """
    Desenha os componentes de filtro na barra lateral e 
    retorna o DataFrame já filtrado em cascata.
    """
    st.sidebar.header("🎯 Central de Filtros")
    st.sidebar.markdown("Selecione os parâmetros para análise:")

    # Filtros extraídos dinamicamente do DataFrame
    planos = st.sidebar.multiselect("Planos:", options=df['plano'].unique(), default=df['plano'].unique())
    canais = st.sidebar.multiselect("Canais de Aquisição:", options=df['canal_aquisicao'].unique(), default=df['canal_aquisicao'].unique())
    estados = st.sidebar.multiselect("Estados (UF):", options=sorted(df['estado'].unique()), default=df['estado'].unique())

    # Aplicação da lógica de filtragem do Pandas
    df_filtrado = df[
        (df['plano'].isin(planos)) & 
        (df['canal_aquisicao'].isin(canais)) & 
        (df['estado'].isin(estados))
    ]
    
    return df_filtrado