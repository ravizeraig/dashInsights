import os
import sys
import pandas as pd

# Garante acesso à taxa de impostos e cogs corporativos do config_regras
caminho_src = os.path.abspath("../src")
if caminho_src not in sys.path:
    sys.path.append(caminho_src)
import config_regras as regras


def calcular_dre_executiva(df_vendas_filtrado: pd.DataFrame, df_custos_bruto: pd.DataFrame, df_marketing_filtrado: pd.DataFrame) -> dict:
    """
    Calcula os indicadores financeiros unificando as nomenclaturas com dados reais do Postgres.
    """
    if df_vendas_filtrado.empty:
        return {
            "faturamento_bruto": 0.0, "impostos": 0.0, "faturamento_liquido": 0.0,
            "cogs": 0.0, "cac_marketing": 0.0, "opex_proporcional": 0.0,
            "lucro_liquido": 0.0, "margem_liquida": 0.0, "meses_ativos": 1
        }

    # 1. Faturamento Bruto (Apenas contratos não inadimplentes)
    faturamento_bruto = df_vendas_filtrado[df_vendas_filtrado['inadimplente'] == False]['valor_pago'].sum()
    
    # 2. Deduções Fiscais e Faturamento Líquido
    impostos_deducoes = faturamento_bruto * regras.ALIQUOTA_IMPOSTO
    faturamento_liquido = faturamento_bruto - impostos_deducoes     
    
    # 3. Custo COGS (Entrega e Atendimento)
    custo_cogs = faturamento_bruto * regras.TAXA_COGS
    
    # 🔥 NOVIDADE: Custo de Marketing Real vindo da 4ª tabela do banco de dados (sem CAC fixo mapeado)
    if not df_marketing_filtrado.empty:
        total_marketing_cac = df_marketing_filtrado['valor_investido'].sum()
    else:
        total_marketing_cac = 0.0
    
    # 4. Cálculo de Meses Ativos no Filtro
    df_vendas_filtrado['mes_ref'] = df_vendas_filtrado['data_venda'].dt.to_period('M').astype(str)
    meses_ativos = max(df_vendas_filtrado['mes_ref'].nunique(), 1)
    
    # 5. Cálculo Dinâmico do OpEx Proporcional (Sem engessar em /18 fixo)
    if not df_custos_bruto.empty:
        df_custos_bruto['mes_ref'] = df_custos_bruto['mes_referencia'].astype(str)
        total_meses_banco = max(df_custos_bruto['mes_ref'].nunique(), 1)
        
        custo_opex_mensal = df_custos_bruto['valor_custo'].sum() / total_meses_banco
        custo_opex_proporcional = custo_opex_mensal * meses_ativos
    else:
        custo_opex_proporcional = 0.0
    
    # 6. Lucro Real e Margem Executiva
    lucro_real = faturamento_liquido - (custo_cogs + total_marketing_cac + custo_opex_proporcional)
    margem_liquida = (lucro_real / faturamento_bruto) * 100 if faturamento_bruto > 0 else 0
    
    return {
        "faturamento_bruto": faturamento_bruto,
        "impostos": impostos_deducoes,
        "faturamento_liquido": faturamento_liquido,
        "cogs": custo_cogs,
        "cac_marketing": total_marketing_cac,
        "opex_proporcional": custo_opex_proporcional,
        "lucro_liquido": lucro_real,
        "margem_liquida": margem_liquida,
        "meses_ativos": meses_ativos
    }


def gerar_tabela_dre_vertical(df_vendas_filtrado: pd.DataFrame, df_custos_bruto: pd.DataFrame, df_marketing_filtrado: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o DataFrame estruturado para exibição da DRE Verticalizada no Streamlit.
    """
    # 🔥 Repassa o novo parâmetro df_marketing_filtrado para a função de cálculo
    valores = calcular_dre_executiva(df_vendas_filtrado, df_custos_bruto, df_marketing_filtrado)
    
    dados_dre = {
        "Indicador Financeiro (DRE)": [
            "💰 (+) FATURAMENTO BRUTO COMERCIAL",
            "💸 (-) Impostos e Deduções Fiscais (14%)",
            "🌍 (=) RECEITA LÍQUIDA OPERACIONAL",
            "📦 (-) Custo de Entrega e Infraestrutura (COGS 15%)",
            "📢 (-) Custo de Aquisição de Clientes (CAC Marketing Real)",
            "📉 (-) Custo Fixo de Estrutura (OpEx Proporcional)",
            "🚀 (=) LUCRO LÍQUIDO REAL CORPORATIVO"
        ],
        "Valor Acumulado": [
            valores["faturamento_bruto"],
            -valores["impostos"],
            valores["faturamento_liquido"],
            -valores["cogs"],
            -valores["cac_marketing"],
            -valores["opex_proporcional"],
            valores["lucro_liquido"]
        ]
    }
    
    return pd.DataFrame(dados_dre)