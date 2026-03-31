import streamlit as st
from api.client import get
import streamlit as st


def show():
    nivel = st.session_state.get("nivel", 1)
    if nivel < 2:
        st.error("Acesso restrito. Somente gestores podem acessar esta área.")
        return

    st.title("⚙️ Tabelas Auxiliares (Admin)")
    st.caption("Tabelas de apoio ao sistema — equivalente ao menu protegido por senha no Access.")

    tabela = st.selectbox("Selecione a tabela", [
        "Motivos de Atendimento",
        "Motivos de Encerramento",
        "Tipo de Ação",
        "Tipo de Evento",
        "Origem (Como Chegou ao Programa)",
        "Órgãos",
        "Municípios",
        "Técnicos",
        "Motivos de Visita",
    ])

    endpoint_map = {
        "Motivos de Atendimento": "/tabelas/motivos-atendimento",
        "Motivos de Encerramento": "/tabelas/motivos-encerramento",
        "Tipo de Ação": "/tabelas/tipo-acao",
        "Tipo de Evento": "/tabelas/tipo-evento",
        "Origem (Como Chegou ao Programa)": "/tabelas/origem",
        "Órgãos": "/tabelas/orgaos",
        "Municípios": "/tabelas/municipios",
        "Técnicos": "/tabelas/tecnicos",
        "Motivos de Visita": "/tabelas/motivos-visita",
    }

    if st.button("Carregar"):
        try:
            dados = get(endpoint_map[tabela])
            if dados:
                import pandas as pd
                st.dataframe(pd.DataFrame(dados), use_container_width=True)
            else:
                st.info("Tabela vazia.")
        except Exception as e:
            st.error(f"Erro: {e}")
