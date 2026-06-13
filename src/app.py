import streamlit as st
import pandas as pd

# 1. IMPORTAÇÕES DA CAMADA DE DADOS E FILTROS
from queries import buscar_vendas_gerais, buscar_custos_operacionais
from components.filter import renderizar_central_de_filtros

# 💡 COMPONENTES VISUAIS: Blocos CSS/HTML customizados do styles.py
from components.styles import criar_card_lucro_destaque, criar_card_contratos_destaque, criar_card_cac_destaque

# 2. IMPORTAÇÕES DAS CAMADAS DE SERVIÇO
from financeiro_service import calcular_dre_executiva
from analise_service import gerar_tabela_performance_canais, gerar_grafico_evolucao_temporal # ✅ Linha limpa e unificada

# 1. Configuração da Janela do Navegador
st.set_page_config(page_title="DashInsights | BI", layout="wide")

# 2. Título Principal do Dashboard
st.title("📊 DashInsights — Performance Comercial & DRE")
st.markdown("Análise estratégica focada na geração de caixa real para o negócio.")
st.markdown("---")

# =========================================================================
# CONEXÃO COM O BANCO & PROCESSAMENTO (FLUXO ÚNICO)
# =========================================================================
df_bruto_vendas = buscar_vendas_gerais()
df_bruto_custos = buscar_custos_operacionais()

if not df_bruto_vendas.empty and not df_bruto_custos.empty:
    
    # A) Injeta a Central de Filtros na barra lateral (Sidebar)
    df_filtrado = renderizar_central_de_filtros(df_bruto_vendas)
    
    # B) Aciona o Service Core para processar a matemática financeira
    dados_dre = calcular_dre_executiva(df_filtrado, df_bruto_custos)
    
    # =========================================================================
    # PRIMEIRO BLOCO: O CARD PRINCIPAL DE LUCRO LÍQUIDO REAL (DESTAQUE ISOLADO)
    # =========================================================================
    
    # Grid de proporção [1, 4, 1] para deixar o lucro gigante bem no meio da tela
    _, col_lucro_centro, _ = st.columns([1, 4, 1])
    
    with col_lucro_centro:
        criar_card_lucro_destaque(dados_dre['lucro_liquido'])
    
    st.markdown("---")
    
    # =========================================================================
    # SEGUNDO BLOCO: GRID DE ALTO IMPACTO (CONTRATOS vs CAC MÉDIO)
    # =========================================================================
    col_esquerda, col_direita = st.columns([4, 4])
    
    with col_esquerda:
        total_linhas_filtradas = len(df_filtrado)
        criar_card_contratos_destaque(total_linhas_filtradas)
        
    with col_direita:
        if not df_filtrado.empty:
            cac_medio_dinamico = df_filtrado['custo_cac'].mean()
        else:
            cac_medio_dinamico = 0.0
            
        criar_card_cac_destaque(cac_medio_dinamico)
    
    st.markdown("---")
    
    # =========================================================================
    # =========================================================================
    # TERCEIRO BLOCO: SEÇÃO DA EVOLUÇÃO TEMPORAL INTERATIVA (SÉRIE TEMPORAL)
    # =========================================================================
    st.subheader("📈 Linha do Tempo: Crescimento de Contratos")
    
    # Criamos as opções deixando o Reset como padrão absoluto na tela
    col_combo, _ = st.columns([3, 5])
    with col_combo:
        escopo_selecionado = st.selectbox(
            "Selecione o Escopo Visual:",
            [
                "🔄 Resetar para Visão Geral", # ✨ Opção explícita de segurança
                "☀️ Visão: Dia a Dia", 
                "📆 Visão: Semanal", 
                "📅 Visão: Mensal"
            ],
            index=0 # Começa apontando para o Reset
        )
    
    # Tratamos a escolha: se for o "Resetar", mandamos o service plotar o padrão "Dia a Dia" limpo
    if escopo_selecionado == "🔄 Resetar para Visão Geral":
        escopo_ajustado = "☀️ Dia a Dia"
    else:
        # Remove o prefixo "Visão: " para o service entender o texto puro
        escopo_ajustado = escopo_selecionado.replace("Visão: ", "")
    
    # 1. A função processa os dados passando o escopo ajustado e limpo
    fig_temporal = gerar_grafico_evolucao_temporal(df_filtrado, escopo_ajustado)
    
    # 2. Renderiza de forma limpa e responsiva na tela
    st.plotly_chart(fig_temporal, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    # =========================================================================
    # QUARTO BLOCO: PERFORMANCE DE LUCRO POR CANAL (TABELA VERDE)
    # =========================================================================
    st.subheader("🎯 Eficiência Financeira por Canal de Aquisição")
    
    df_canais = gerar_tabela_performance_canais(df_filtrado)
    
    df_estilizado = df_canais.style.format({
        'Fat. Bruto (Total)': 'R$ {:,.2f}',
        'Lucro Líquido (Total)': 'R$ {:,.2f}',
        'Lucro Médio por Contrato': 'R$ {:,.2f}'
    }).background_gradient(subset=['Lucro Médio por Contrato'], cmap='Greens')
    
    st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
    st.markdown("---")

else:
    st.error("Erro Crítico: A conexão com o banco de dados falhou ou retornou tabelas vazias.")