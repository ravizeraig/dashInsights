import streamlit as st

def renderizar_central_de_filtros(df):
    """
    Desenha os componentes de filtro na barra lateral e 
    retorna o DataFrame já filtrado em cascata.
    """
    st.sidebar.header("🎯 Central de Filtros")
    st.sidebar.markdown("Selecione os parâmetros para análise:")

    # 1. Filtro de Plano
    planos = st.sidebar.multiselect(
        "Planos:", 
        options=df['plano'].unique(), 
        default=list(df['plano'].unique())
    )
    
    # 2. Filtro de Canal de Aquisição
    canais = st.sidebar.multiselect(
        "Canais de Aquisição:", 
        options=df['canal_aquisicao'].unique(), 
        default=list(df['canal_aquisicao'].unique())
    )
    
    # 3. Filtro de Estado (UF) - Organizado em ordem alfabética
    estados = st.sidebar.multiselect(
        "Estados (UF):", 
        options=sorted(df['estado'].unique()), 
        default=list(df['estado'].unique())
    )

    # 4. Filtro de Gênero (Agora 100% limpo com Masculino/Feminino da origem!)
    generos = st.sidebar.multiselect(
        "Gênero:",
        options=df['genero'].unique(),
        default=list(df['genero'].unique())
    )

    # 5. Filtro de Forma de Pagamento
    formas_pagamento = st.sidebar.multiselect(
        "Forma de Pagamento:",
        options=df['forma_pagamento'].unique(),
        default=list(df['forma_pagamento'].unique())
    )

    # 6. Filtro de Idade (Slider dinâmico pegando o mínimo e máximo real do banco)
    idade_min, idade_max = int(df['idade'].min()), int(df['idade'].max())
    faixa_idade = st.sidebar.slider(
        "Faixa Etária (Idade):",
        min_value=idade_min,
        max_value=idade_max,
        value=(idade_min, idade_max)  # Inicia com o intervalo total selecionado
    )

    # --- Aplicação da lógica de filtragem cruzada do Pandas ---
    df_filtrado = df[
        (df['plano'].isin(planos)) & 
        (df['canal_aquisicao'].isin(canais)) & 
        (df['estado'].isin(estados)) &
        (df['genero'].isin(generos)) &
        (df['forma_pagamento'].isin(formas_pagamento)) &
        (df['idade'].between(faixa_idade[0], faixa_idade[1]))
    ]
    
    return df_filtrado