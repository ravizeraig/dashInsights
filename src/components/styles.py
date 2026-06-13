import streamlit as st

# =========================================================================
# CONFIGURAÇÃO DE IDENTIDADE VISUAL (SISTEMA DE DESIGN)
# =========================================================================
COR_FUNDO_CARD = "#1C1F26"     
COR_DESTAQUE = "#CCFF00"       
COR_TEXTO_MUTED = "#8A9299"    

# -------------------------------------------------------------------------
# BLOCO 1: CARD PRINCIPAL DE LUCRO LÍQUIDO REAL
# -------------------------------------------------------------------------
def criar_card_lucro_destaque(valor_numerico):
    """
    Desenha o card exclusivo do Lucro Líquido Real centralizado,
    com fundo escuro e efeito de brilho neon verde.
    """
    valor_txt = f"R$ {valor_numerico:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(
        f"""
        <div style='
            background-color: {COR_FUNDO_CARD};
            padding: 35px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #333;
            box-shadow: 0 4px 20px rgba(204, 255, 0, 0.15);
            margin: 10px 0;
        '>
            <p style='margin: 0; color: {COR_TEXTO_MUTED}; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;'>
                🚀 Lucro Líquido Real (Dinheiro no Caixa)
            </p>
            <p style='
                margin: 15px 0 0 0; 
                color: {COR_DESTAQUE}; 
                font-size: 4rem; 
                font-weight: 900; 
                text-shadow: 0 0 25px rgba(204, 255, 0, 0.4);
                font-family: sans-serif;
            '>
                {valor_txt}
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# -------------------------------------------------------------------------
# BLOCO 2 (ESQUERDA): CARD DE CONTRATOS ATIVOS
# -------------------------------------------------------------------------
def criar_card_contratos_destaque(total_linhas):
    """
    Desenha o card ultra destacado de Contratos Ativos com fonte ampliada,
    fundo escuro e brilho neon azul/ciano. Altura pareada com o card de CAC.
    """
    contratos_txt = f"{total_linhas:,}".replace(",", ".")
    st.markdown(
        f"""
        <div style='
            background-color: {COR_FUNDO_CARD};
            padding: 40px 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #333;
            box-shadow: 0 6px 25px rgba(0, 242, 254, 0.2);
            margin: 10px 0;
            min-height: 250px; /* Garante que os dois cards tenham a mesma altura */
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <p style='margin: 0; color: #FFFFFF; font-size: 1.4rem; font-weight: 900; text-transform: uppercase; letter-spacing: 2px;'>
                📋 CONTRATOS ATIVOS
            </p>
            <p style='
                margin: 20px 0 10px 0; 
                color: #00F2FE; 
                font-size: clamp(3rem, 5vw, 4.5rem); 
                font-weight: 900; 
                text-shadow: 0 0 30px rgba(0, 242, 254, 0.6);
                font-family: sans-serif;
                line-height: 1;
            '>
                {contratos_txt}
            </p>
            <p style='margin: 10px 0 0 0; color: {COR_TEXTO_MUTED}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;'>
                Volume Total Homologado na Base
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# -------------------------------------------------------------------------
# BLOCO 2 (DIREITA): CARD DE CAC MÉDIO
# -------------------------------------------------------------------------
def criar_card_cac_destaque(valor_cac_medio):
    """
    Desenha o card de CAC Médio por Cliente com fonte ampliada,
    fundo escuro e brilho neon laranja. Altura pareada com o card de Contratos.
    """
    cac_txt = f"R$ {valor_cac_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(
        f"""
        <div style='
            background-color: {COR_FUNDO_CARD};
            padding: 40px 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #333;
            box-shadow: 0 6px 25px rgba(255, 102, 0, 0.15);
            margin: 10px 0;
            min-height: 250px; /* Garante que os dois cards tenham a mesma altura */
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <p style='margin: 0; color: #FFFFFF; font-size: 1.4rem; font-weight: 900; text-transform: uppercase; letter-spacing: 2px;'>
                📢 CAC MÉDIO POR CLIENTE
            </p>
            <p style='
                margin: 20px 0 10px 0; 
                color: #FF6600; 
                font-size: clamp(3rem, 5vw, 4.5rem); 
                font-weight: 900; 
                text-shadow: 0 0 30px rgba(255, 102, 0, 0.5);
                font-family: sans-serif;
                line-height: 1;
            '>
                {cac_txt}
            </p>
            <p style='margin: 10px 0 0 0; color: {COR_TEXTO_MUTED}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;'>
                Custo de Investimento por Nova Assinatura
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )