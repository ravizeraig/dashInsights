# =========================================================================
# 1. VALORES, PRODUTOS E REGRAS DEMOGRÁFICAS B2B ENTERPRISE
# =========================================================================

# Valores e Planos vigentes corporativos
PLANOS = {
    'Bronze': 20000.00,
    'Prata': 45000.00,
    'Ouro': 75000.00,
    'Diamante': 100000.00
}

# Dados demográficos e geográficos para segmentação do Data Lake
ESTADOS = ['SP', 'RJ', 'MG', 'SC', 'PR', 'RS', 'BA', 'PE', 'DF', 'GO', 'AM', 'CE']
GENEROS = ['Masculino', 'Feminino']

# Regras de Vendas e CRM (🔥 ALINHADOS CIRURGICAMENTE COM O GERADOR DE DADOS)
FORMAS_PAGAMENTO = ['À Vista', 'Parcelado Boleto', 'Parcelado Cartão']
CANAIS_AQUISICAO = ['Google Ads', 'Meta Ads', 'YouTube', 'E-mail Marketing', 'Orgânico', 'Indicação']
STATUS_CURSO = ['Não Iniciado', 'Em Andamento', 'Concluido', 'Cancelado']


# =========================================================================
# 2. REGRAS FINANCEIRAS DE OPEX REALISTAS (OPERAÇÃO ENTERPRISE)
# =========================================================================

# Folha de Pagamento de Grande Porte (Múltiplos Times Comercial, CS e Tech)
FOLHA_PAGAMENTO = {
    "Diretoria Executiva (C-Level)": 85000.00,
    "Gerentes de Vendas e CS (3 pessoas)": 45000.00,
    "Closers / Executivos de Contas (15 pessoas)": 105000.00, # R$ 7k cada
    "SDRs / Pré-vendedores (25 pessoas)": 100000.00,          # R$ 4k cada
    "Customer Success / Implantação (12 pessoas)": 60000.00,  # R$ 5k cada
    "Time de Engenharia de Dados e BI": 35000.00,
    "Time de Marketing Interno (Growth/Design)": 28000.00,
    "Administrativo, RH e Jurídico": 25000.00
}

# Custos de Infraestrutura e Ferramentas em Larga Escala (Mensal)
# Com tanta gente usando HubSpot, licenças e nuvem corporativa custam caro!
INFRAESTRUTURA_MENSAL = {
    "Datacenter Corporativo (AWS/Azure Multi-Região)": 38000.00,
    "Contrato HubSpot Enterprise (CRM & Marketing)": 22000.00,
    "Dados & Prospecção (Apollo, Lusha, LinkedIn Sales Navigator)": 14000.00,
    "ERP Corporativo (SAP/Totvs) & Ferramentas Gerais": 12000.00,
    "Segurança, Firewall & Compliance de Dados": 8500.00
}

# Comissões Agressivas e Bônus sobre Contratos de R$ 100k (Mensal)
# O motor real do Inside Sales de alta performance
BONUS_METAS_MES = 120000.00

# CAC B2B Enterprise (🔥 CHAVES ESPELHADAS COM O PROVEDOR DE MARKETING DO POSTGRES)
CAC_POR_CANAL = {
    'Google Ads': 3500.00,
    'Meta Ads': 2800.00,
    'YouTube': 3000.00,
    'E-mail Marketing': 800.00,
    'Orgânico': 0.00,
    'Indicação': 500.00
}


# =========================================================================
# 3. ALÍQUOTAS FISCAIS E TAXAS DE OPERAÇÃO (DEDUÇÕES DA DRE)
# =========================================================================

# Alíquota de Impostos diretos sobre a Nota Fiscal (PIS, COFINS, ISS)
# 0.14 representa 14% de imposto sobre o faturamento bruto
ALIQUOTA_IMPOSTO = 0.14

# Margem de Custo de Entrega do Produto / Atendimento / Sucesso do Cliente (COGS)
# 0.15 representa 15% do faturamento bruto destinado a manter os clientes ativos
TAXA_COGS = 0.15