import streamlit as st
import pandas as pd

def renderizar_central_de_filtros(df):
    """
    Desenha os componentes de filtro na barra lateral e 
    retorna o DataFrame filtrado, incluindo um menu de seleção de anos comerciais.
    """
    st.sidebar.header("🎯 Central de Filtros")
    st.sidebar.markdown("Selecione os parâmetros para análise:")

    # Certifica-se de que a coluna de data está no formato datetime
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    df['Ano'] = df['data_venda'].dt.year.astype(str)

    # =========================================================================
    # 🔥 NOVO MENU: SELEÇÃO DE ANOS COMERCIAIS
    # =========================================================================
    anos_disponiveis = sorted(df['Ano'].unique(), reverse=True) # Ex: ['2026', '2025', '2024', '2023']
    
    anos_selecionados = st.sidebar.multiselect(
        "📆 Anos em Análise:",
        options=anos_disponiveis,
        default=anos_disponiveis # Inicia mostrando TODOS os anos (3 anos e meio)
    )

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
    
    # 3. Filtro de Estado (UF) - Sincronizado
    estados_unicos = sorted(df['estado'].unique())
    estados = st.sidebar.multiselect(
        "Estados (UF):", 
        options=estados_unicos, 
        default=estados_unicos
    )

    # 4. Filtro de Gênero
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

    # 6. Filtro de Idade
    idade_min, idade_max = int(df['idade'].min()), int(df['idade'].max())
    faixa_idade = st.sidebar.slider(
        "Faixa Etária (Idade):",
        min_value=idade_min,
        max_value=idade_max,
        value=(idade_min, idade_max)
    )

    # --- Aplicação da lógica de filtragem cruzada do Pandas ---
    df_filtrado = df[
        (df['Ano'].isin(anos_selecionados)) & # 🔥 Aplica o novo menu de anos
        (df['plano'].isin(planos)) & 
        (df['canal_aquisicao'].isin(canais)) & 
        (df['estado'].isin(estados)) &
        (df['genero'].isin(generos)) &
        (df['forma_pagamento'].isin(formas_pagamento)) &
        (df['idade'].between(faixa_idade[0], faixa_idade[1]))
    ]
    
    return df_filtrado