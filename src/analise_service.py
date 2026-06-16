import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Garante acesso à taxa de impostos e cogs corporativos do config_regras
caminho_src = os.path.abspath("../src")
if caminho_src not in sys.path:
    sys.path.append(caminho_src)
import config_regras as regras


def gerar_tabela_performance_canais(df_vendas_filtrado: pd.DataFrame, df_marketing_filtrado: pd.DataFrame) -> pd.DataFrame:
    """
    Isolado em analise_service: Processa o cruzamento de vendas e a nova tabela
    de custos de marketing para calcular o lucro líquido e CAC real por canal.
    """
    # Se vendas estiver vazio, retorna a tabela estruturada vazia
    if df_vendas_filtrado.empty:
        return pd.DataFrame(columns=['Canal de Aquisição', 'Qtd Vendas', 'Fat. Bruto (Total)', 'Lucro Líquido (Total)', 'Lucro Médio por Contrato'])
    
    # 1. Agrupamento das Vendas por Canal (Tratando Inadimplência)
    df_vendas_temp = df_vendas_filtrado.copy()
    df_vendas_temp['faturamento_bruto_linha'] = df_vendas_temp.apply(
        lambda row: row['valor_pago'] if not row['inadimplente'] else 0.0, axis=1
    )
    
    resumo_vendas = df_vendas_temp.groupby('canal_aquisicao').agg(
        total_vendas=('id_venda', 'count'),
        faturamento_bruto=('faturamento_bruto_linha', 'sum')
    ).reset_index()
    
    # 2. Agrupamento dos Custos de Marketing Reais por Canal
    if not df_marketing_filtrado.empty:
        resumo_marketing = df_marketing_filtrado.groupby('canal_aquisicao')['valor_investido'].sum().reset_index(name='custo_marketing_total')
    else:
        resumo_marketing = pd.DataFrame(columns=['canal_aquisicao', 'custo_marketing_total'])
        
    # 3. Consolidação Financeira por Canal (Merge)
    df_consolidado = pd.merge(resumo_vendas, resumo_marketing, on='canal_aquisicao', how='left').fillna(0)
    
    # 4. Aplicação das Alíquotas Oficiais e Deduções
    df_consolidado['impostos'] = df_consolidado['faturamento_bruto'] * regras.ALIQUOTA_IMPOSTO
    df_consolidado['cogs'] = df_consolidado['faturamento_bruto'] * regras.TAXA_COGS
    
    # Lucro Líquido por Canal = Faturamento - Impostos - COGS - Investimento de Marketing real do banco
    df_consolidado['lucro_total'] = (
        df_consolidado['faturamento_bruto'] - 
        df_consolidado['impostos'] - 
        df_consolidado['cogs'] - 
        df_consolidado['custo_marketing_total']
    )
    
    df_consolidado['lucro_medio'] = df_consolidado['lucro_total'] / df_consolidado['total_vendas']
    
    # 5. Estruturação final para entrega ao painel executivo
    tabela_performance = df_consolidado[[
        'canal_aquisicao', 'total_vendas', 'faturamento_bruto', 'lucro_total', 'lucro_medio'
    ]].copy()
    
    tabela_performance.columns = [
        'Canal de Aquisição', 'Qtd Vendas', 'Fat. Bruto (Total)', 'Lucro Líquido (Total)', 'Lucro Médio por Contrato'
    ]
    
    return tabela_performance.sort_values(by='Lucro Líquido (Total)', ascending=False)


def gerar_grafico_dispersao_cac_estado(df_vendas_filtrado: pd.DataFrame, df_marketing_filtrado: pd.DataFrame) -> go.Figure:
    """
    Camada de Serviço: Cruza volume de contratos e investimento de marketing por Estado
    para plotar uma matriz de eficiência de CAC (Gráfico de Dispersão).
    """
    if df_vendas_filtrado.empty or df_marketing_filtrado.empty:
        fig_vazia = go.Figure()
        fig_vazia.update_layout(title="Dados insuficientes para gerar a matriz de CAC por Estado.", template='plotly_dark')
        return fig_vazia

    # 1. Agrupa volume de contratos por estado
    vendas_estado = df_vendas_filtrado.groupby('estado').size().reset_index(name='Qtd_Vendas')

    # 2. Agrupa investimento total de marketing por estado
    mkt_estado = df_marketing_filtrado.groupby('estado_foco')['valor_investido'].sum().reset_index()
    mkt_estado.columns = ['estado', 'Total_Investido']

    # 3. Cruza as duas visões
    df_cac_estado = pd.merge(vendas_estado, mkt_estado, on='estado', how='inner')
    
    # 4. Calcula o CAC Real do Estado
    df_cac_estado['CAC_Real'] = round(df_cac_estado['Total_Investido'] / df_cac_estado['Qtd_Vendas'], 2)

    # 5. Montagem do Gráfico de Dispersão usando Plotly Express
    fig = px.scatter(
        df_cac_estado,
        x="Qtd_Vendas",
        y="CAC_Real",
        text="estado",
        size="Total_Investido",  # O tamanho da bolha reflete o tamanho da verba gasta
        color="CAC_Real",       # A cor muda conforme o CAC fica mais caro
        color_continuous_scale="RdYlGn_r", # Vermelho (Caro) para Verde (Barato)
        labels={"Qtd_Vendas": "Volume de Contratos Fechados", "CAC_Real": "Custo de Aquisição (CAC Real)"},
        title="🎯 Matriz de Eficiência: CAC vs Volume de Contratos por Estado"
    )

    # 6. Ajustes de Layout Profissional
    fig.update_traces(
        textposition='top center', 
        marker=dict(sizemode='area', sizeref=150) # Calibra o tamanho das bolhas
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=500,
        hovermode='closest',
        font=dict(family='sans-serif', size=12),
        margin=dict(l=20, r=20, t=80, b=60),
        coloraxis_showscale=False # Remove a barra lateral de cor para limpar o visual
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#333')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#333')

    return fig

def gerar_grafico_evolucao_temporal(df_vendas_filtrado: pd.DataFrame, escopo: str) -> go.Figure:
    """
    Camada de Serviço: Cria o gráfico temporal com base no volume de contratos fechados.
    Permanece intacto pois monitora volumetria da tabela fato de vendas.
    """
    if df_vendas_filtrado.empty:
        fig_vazia = go.Figure()
        fig_vazia.update_layout(title="Nenhum dado encontrado para os filtros.", template='plotly_dark')
        return fig_vazia

    df_temporal = df_vendas_filtrado.copy()
    df_temporal['data_venda'] = pd.to_datetime(df_temporal['data_venda'])

    df_temporal['Visao_Dia'] = df_temporal['data_venda'].dt.strftime('%Y-%m-%d')
    df_temporal['Visao_Semana'] = df_temporal['data_venda'].dt.strftime('%Y-Sem %W')
    df_temporal['Visao_Mes'] = df_temporal['data_venda'].dt.strftime('%Y-%m')

    if escopo == "☀️ Dia a Dia":
        df_agrupado = df_temporal.groupby(['Visao_Dia', 'canal_aquisicao']).size().reset_index(name='Contratos').sort_values('Visao_Dia')
        col_x = 'Visao_Dia'
        label_x = "Cronologia (Dia a Dia)"
    elif escopo == "📆 Semanal":
        df_agrupado = df_temporal.groupby(['Visao_Semana', 'canal_aquisicao']).size().reset_index(name='Contratos').sort_values('Visao_Semana')
        col_x = 'Visao_Semana'
        label_x = "Cronologia (Semanas do Ano)"
    else:
        df_agrupado = df_temporal.groupby(['Visao_Mes', 'canal_aquisicao']).size().reset_index(name='Contratos').sort_values('Visao_Mes')
        col_x = 'Visao_Mes'
        label_x = "Cronologia (Meses Consolidados)"

    lista_canais = df_temporal['canal_aquisicao'].unique()
    fig = go.Figure()

    for canal in lista_canais:
        df_c = df_agrupado[df_agrupado['canal_aquisicao'] == canal]
        fig.add_trace(go.Scatter(
            x=df_c[col_x], y=df_c['Contratos'], name=canal, 
            mode='lines', line_shape='spline',
            fill='tozeroy', fillcolor='rgba(0, 242, 254, 0.05)'
        ))

    fig.update_layout(
        title=dict(text='📈 Evolução Temporal de Contratos por Canal', pad=dict(b=20)),
        template='plotly_dark',
        height=500,
        legend_title='Canais de Marketing',
        hovermode='x unified',
        font=dict(family='sans-serif', size=12),
        margin=dict(l=20, r=20, t=120, b=60), 
        xaxis=dict(tickangle=45, title=dict(text=label_x)),
        yaxis=dict(title=None),
        annotations=[
            dict(
                text="👤 Volume de Contratos Fechados",
                xref="paper", yref="paper",
                x=0.0, y=1.12,
                showarrow=False,
                font=dict(family="sans-serif", size=12, color="#8A9299"),
                align="left"
            )
        ]
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#333')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#333')

    return fig