import pandas as pd
import config_regras as reglas

def calcular_dre_executiva(df_vendas_filtrado: pd.DataFrame, df_custos_bruto: pd.DataFrame) -> dict:
    """
    Calcula os indicadores financeiros unificando as nomenclaturas.
    """
    if df_vendas_filtrado.empty:
        return {
            "faturamento_bruto": 0.0, "impostos": 0.0, "faturamento_liquido": 0.0,
            "cogs": 0.0, "cac_marketing": 0.0, "opex_proporcional": 0.0,
            "lucro_liquido": 0.0, "margem_liquida": 0.0, "meses_ativos": 1
        }

    # Mapeamento do CAC
    df_vendas_filtrado['custo_cac'] = df_vendas_filtrado['canal_aquisicao'].map(reglas.CAC_POR_CANAL)
    
# Faturamento Bruto
    faturamento_bruto = df_vendas_filtrado[df_vendas_filtrado['inadimplente'] == False]['valor_pago'].sum()
    
    # CORREÇÃO AQUI: Mudamos para 'impostos_deducoes' com O para padronizar
    impostos_deducoes = faturamento_bruto * reglas.ALIQUOTA_IMPOSTO
    faturamento_liquido = faturamento_bruto - impostos_deducoes  # ✅ Agora o Python vai encontrar a variável!    
    # Custos e OpEx
    custo_cogs = faturamento_bruto * reglas.TAXA_COGS
    total_marketing_cac = df_vendas_filtrado['custo_cac'].sum()
    
    df_vendas_filtrado['mes_ref'] = df_vendas_filtrado['data_venda'].dt.to_period('M').astype(str)
    meses_ativos = max(df_vendas_filtrado['mes_ref'].nunique(), 1)
    
    custo_opex_mensal = df_custos_bruto['valor_custo'].sum() / 18
    custo_opex_proporcional = custo_opex_mensal * meses_ativos
    
    # Lucro e Margem
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

def gerar_tabela_dre_vertical(df_vendas_filtrado: pd.DataFrame, df_custos_bruto: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o DataFrame para exibição da DRE.
    """
    valores = calcular_dre_executiva(df_vendas_filtrado, df_custos_bruto)
    
    dados_dre = {
        "Indicador Financeiro (DRE)": [
            "💰 (+) FATURAMENTO BRUTO COMERCIAL",
            "💸 (-) Impostos e Deduções Fiscais (14%)",
            "🌍 (=) RECEITA LÍQUIDA OPERACIONAL",
            "📦 (-) Custo de Entrega e Infraestrutura (COGS 15%)",
            "📢 (-) Custo de Aquisição de Clientes (CAC Marketing)",
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