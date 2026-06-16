import streamlit as st
import pandas as pd
import os
import sys

# Garante o mapeamento correto da pasta src
caminho_src = os.path.abspath("../src")
if caminho_src not in sys.path:
    sys.path.append(caminho_src)

# 1. IMPORTAÇÕES DA CAMADA DE DADOS DA TRÍADE DO POSTGRES
from queries import buscar_vendas_gerais, buscar_custos_operacionais, buscar_custos_marketing_canal
from components.filter import renderizar_central_de_filtros

# 💡 COMPONENTES VISUAIS: Blocos CSS/HTML customizados do styles.py
from components.styles import criar_card_lucro_destaque, criar_card_contratos_destaque, criar_card_cac_destaque

# 2. IMPORTAÇÕES DAS CAMADAS DE SERVIÇO ATUALIZADAS
from financeiro_service import calcular_dre_executiva
from analise_service import gerar_tabela_performance_canais, gerar_grafico_evolucao_temporal, gerar_grafico_dispersao_cac_estado

# 1. Configuração da Janela do Navegador
st.set_page_config(page_title="DashInsights | BI", layout="wide")

# 2. Título Principal do Dashboard
st.title("📊 DashInsights — Performance Comercial & DRE")
st.markdown("Análise estratégica focada na geração de caixa real para o negócio.")
st.markdown("---")

# =========================================================================
# CONEXÃO COM O BANCO & PROCESSAMENTO (FLUXO DA TRÍADE DE DADOS)
# =========================================================================
df_bruto_vendas = buscar_vendas_gerais()
df_bruto_custos = buscar_custos_operacionais()
df_bruto_marketing = buscar_custos_marketing_canal() # 🔥 Carregando a 4ª tabela de marketing

# Verifica se o Data Lake está pulsando
if not df_bruto_vendas.empty and not df_bruto_custos.empty and not df_bruto_marketing.empty:
    
    # A) Injeta a Central de Filtros na barra lateral (Sidebar)
    # 💡 Nota: Se o seu componente filter.py só aceitar um DataFrame hoje, 
    # nós criamos a lógica de espelhamento abaixo para blindar a aplicação.
    df_vendas_filtrado = renderizar_central_de_filtros(df_bruto_vendas)
    
    # Sincroniza o filtro de marketing com os estados selecionados nas vendas de forma automática
    estados_ativos = df_vendas_filtrado['estado'].unique()
    df_marketing_filtrado = df_bruto_marketing[df_bruto_marketing['estado_foco'].isin(estados_ativos)]
    
    # B) Aciona o Service Core passando a tríade consolidada de dados
    dados_dre = calcular_dre_executiva(df_vendas_filtrado, df_bruto_custos, df_marketing_filtrado)
    
    # =========================================================================
    # PRIMEIRO BLOCO: O CARD PRINCIPAL DE LUCRO LÍQUIDO REAL (DESTAQUE ISOLADO)
    # =========================================================================
    
    # Grid de proporção [1, 4, 1] para deixar o lucro gigante bem no meio da tela
    _, col_lucro_centro, _ = st.columns([1, 4, 1])
    
    with col_lucro_centro:
        criar_card_lucro_destaque(dados_dre['lucro_liquido'])
    
    st.markdown("---")
    
    # =========================================================================
    # SEGUNDO BLOCO: GRID DE ALTO IMPACTO (CONTRATOS vs CAC DINÂMICO REAL)
    # =========================================================================
    col_esquerda, col_direita = st.columns([4, 4])
    
    with col_esquerda:
        total_linhas_filtradas = len(df_vendas_filtrado)
        criar_card_contratos_destaque(total_linhas_filtradas)
        
    with col_direita:
        # 🔥 CÁLCULO DE CAC REAL: Investimento total de marketing / Qtd de vendas reais do período
        if total_linhas_filtradas > 0:
            total_investido_mkt = df_marketing_filtrado['valor_investido'].sum()
            cac_real_dinamico = total_investido_mkt / total_linhas_filtradas
        else:
            cac_real_dinamico = 0.0
            
        criar_card_cac_destaque(cac_real_dinamico)
    
    st.markdown("---")
    
    # =========================================================================
    # TERCEIRO BLOCO: SEÇÃO DA EVOLUÇÃO TEMPORAL INTERATIVA (SÉRIE TEMPORAL)
    # =========================================================================
    st.subheader("📈 Linha do Tempo: Crescimento de Contratos")
    
    col_combo, _ = st.columns([3, 5])
    with col_combo:
        escopo_selecionado = st.selectbox(
            "Selecione o Escopo Visual:",
            [
                "🔄 Resetar para Visão Geral",
                "☀️ Visão: Dia a Dia", 
                "📆 Visão: Semanal", 
                "📅 Visão: Mensal"
            ],
            index=0
        )
    
    if escopo_selecionado == "🔄 Resetar para Visão Geral":
        escopo_ajustado = "☀️ Dia a Dia"
    else:
        escopo_ajustado = escopo_selecionado.replace("Visão: ", "")
    
    fig_temporal = gerar_grafico_evolucao_temporal(df_vendas_filtrado, escopo_ajustado)
    st.plotly_chart(fig_temporal, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    
    # =========================================================================
    # QUINTO BLOCO: MATRIZ DE EFICIÊNCIA GEOGRÁFICA (DISPERSÃO DE CAC)
    # =========================================================================
    st.subheader("🗺️ Análise de Eficiência Regional do CAC")
    
    # 1. Importe a nova função de analise_service no topo do seu app.py se necessário
    fig_dispersao_cac = gerar_grafico_dispersao_cac_estado(df_vendas_filtrado, df_marketing_filtrado)
    
    # 2. Renderiza o gráfico dinamicamente na tela
    st.plotly_chart(fig_dispersao_cac, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")

    
    # =========================================================================
    # QUARTO BLOCO: PERFORMANCE DE LUCRO POR CANAL (TABELA EXECUTIVA ADAPTADA)
    # =========================================================================
    st.subheader("🎯 Eficiência Financeira por Canal de Aquisição")
    
    # 🔥 Passando os dois DataFrames para a função atualizada cruzar os custos reais do banco
    df_canais = gerar_tabela_performance_canais(df_vendas_filtrado, df_marketing_filtrado)
    
    df_estilizado = df_canais.style.format({
        'Fat. Bruto (Total)': 'R$ {:,.2f}',
        'Lucro Líquido (Total)': 'R$ {:,.2f}',
        'Lucro Médio por Contrato': 'R$ {:,.2f}'
    }).background_gradient(subset=['Lucro Médio por Contrato'], cmap='Greens')
    
    st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
    st.markdown("---")

else:
    st.error("Erro Crítico: A conexão com o banco de dados falhou ou retornou tabelas vazias na Tríade.")