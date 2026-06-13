import pandas as pd
import plotly.graph_objects as go

def gerar_tabela_performance_canais(df_vendas_filtrado: pd.DataFrame) -> pd.DataFrame:
    """
    Isolado em analise_service: Processa o agrupamento por canal 
    especificamente para a tabela executiva do Dashboard.
    """
    if df_vendas_filtrado.empty:
        return pd.DataFrame(columns=['Canal de Aquisição', 'Qtd Vendas', 'Fat. Bruto (Total)', 'Lucro Líquido (Total)', 'Lucro Médio por Contrato'])
    
    # 1. Copia os dados para segurança
    df_temp = df_vendas_filtrado.copy()
    
    # 2. Executa a matemática rápida de linhas (14% imposto e 15% COGS)
    df_temp['faturamento_bruto_linha'] = df_temp.apply(
        lambda row: row['valor_pago'] if row['inadimplente'] == False else 0.0, axis=1
    )
    df_temp['lucro_linha'] = df_temp['faturamento_bruto_linha'] * (1 - 0.14 - 0.15) - df_temp['custo_cac']
    
    # 3. Agrupamento idêntico ao do laboratório do Notebook
    analise_canais = df_temp.groupby('canal_aquisicao').agg(
        total_vendas=('id_venda', 'count'),
        faturamento_bruto=('faturamento_bruto_linha', 'sum'),
        lucro_gerado=('lucro_linha', 'sum')
    ).reset_index()
    
    analise_canais['lucro_medio_por_venda'] = analise_canais['lucro_gerado'] / analise_canais['total_vendas']
    
    # 4. Estruturação final das colunas
    tabela_dre_canais = analise_canais[[
        'canal_aquisicao', 'total_vendas', 'faturamento_bruto', 'lucro_gerado', 'lucro_medio_por_venda'
    ]].copy()
    
    tabela_dre_canais.columns = [
        'Canal de Aquisição', 'Qtd Vendas', 'Fat. Bruto (Total)', 'Lucro Líquido (Total)', 'Lucro Médio por Contrato'
    ]
    
    return tabela_dre_canais.sort_values(by='Lucro Médio por Contrato', ascending=False)

def gerar_grafico_evolucao_temporal(df_vendas_filtrado: pd.DataFrame, escopo: str) -> go.Figure:
    """
    Camada de Serviço: Cria o gráfico temporal com base no escopo selecionado (Dia/Semana/Mês)
    no front-end, limpando o estado do gráfico automaticamente.
    """
    if df_vendas_filtrado.empty:
        fig_vazia = go.Figure()
        fig_vazia.update_layout(title="Nenhum dado encontrado para os filtros.", template='plotly_dark')
        return fig_vazia

    # 1. Modelagem de Dados
    df_temporal = df_vendas_filtrado.copy()
    df_temporal['data_venda'] = pd.to_datetime(df_temporal['data_venda'])

    df_temporal['Visao_Dia'] = df_temporal['data_venda'].dt.strftime('%Y-%m-%d')
    df_temporal['Visao_Semana'] = df_temporal['data_venda'].dt.strftime('%Y-Sem %W')
    df_temporal['Visao_Mes'] = df_temporal['data_venda'].dt.strftime('%Y-%m')

    # 2. Seleção de Agrupamento baseado no parâmetro do Streamlit
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

    # 3. Montagem do Gráfico Puro
    lista_canais = df_temporal['canal_aquisicao'].unique()
    fig = go.Figure()

    for canal in lista_canais:
        df_c = df_agrupado[df_agrupado['canal_aquisicao'] == canal]
        fig.add_trace(go.Scatter(
            x=df_c[col_x], y=df_c['Contratos'], name=canal, 
            mode='lines', line_shape='spline',
            fill='tozeroy', fillcolor='rgba(0, 242, 254, 0.05)'
        ))

    # 4. Layout Limpo (Sem updatemenus internos do Plotly)
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