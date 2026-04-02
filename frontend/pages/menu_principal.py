import streamlit as st
from api.client import get


def show():
    st.title("🛡️ CIAPPI — Painel Inicial")
    st.divider()

    try:
        ativos = get("/relatorios/casos-ativos")
        ouvidoria = get("/ouvidoria/avencer")
        col1, col2, col3 = st.columns(3)
        # casos-ativos retorna {"total": N, "casos": [...]} — len() do dict daria 2
        col1.metric("Casos Ativos", ativos.get("total", 0))
        col2.metric("Ouvidoria a Vencer", len(ouvidoria))
        col3.metric("Sistema", "Online", delta="✓")
    except Exception:
        st.info("Conecte a API para ver os indicadores.")

    st.divider()
    st.caption("Sistema de Proteção ao Idoso — Secretaria de Justiça e Direitos Humanos de Pernambuco")
