import streamlit as st

# =========================================================================
# PALETA DE CORES MANUAL
# =========================================================================
COR_FUNDO_CARD = "#1C1F26"     
COR_DESTAQUE = "#CCFF00"       
COR_TEXTO_MUTED = "#8A9299"    

def criar_banner_faturamento(valor_numerico):
    """
    Gera o bloco de faturamento centralizado usando alinhamento nativo.
    """
    # 1. Formatação do dinheiro real vindo do banco
    faturamento_txt = f"R$ {valor_numerico:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    with st.container():
        # === AQUI ESTÁ A ALTERAÇÃO: ESTA LINHA CRIA O ALINHAMENTO CENTRALIZADO ===
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <p style='margin: 0; color: #8A9299; font-size: 1.2rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>
                    💰 Faturamento Total
                </p>
                <p style='margin: 10px 0 0 0; color: #CCFF00; font-size: 3.5rem; font-weight: 800; font-family: sans-serif;'>
                    {faturamento_txt}
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )