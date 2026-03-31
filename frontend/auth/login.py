import streamlit as st
from api.client import login


def show_login():
    st.title("CIAPPI")
    st.subheader("Sistema de Proteção ao Idoso — SJDH/PE")
    st.divider()

    with st.form("form_login"):
        nome = st.text_input("Nome do Técnico")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar", use_container_width=True)

    if entrar:
        if not nome or not senha:
            st.error("Informe o nome e a senha.")
            return

        try:
            dados = login(nome, senha)
            st.session_state["token"] = dados["access_token"]
            st.session_state["nivel"] = dados["nivel"]
            st.session_state["usuario_nome"] = dados["nome"]
            st.session_state["autenticado"] = True
            st.rerun()
        except Exception as e:
            st.error("Nome do Técnico e Senha não conferem.")


def logout():
    for chave in ["token", "nivel", "usuario_nome", "autenticado"]:
        st.session_state.pop(chave, None)
    st.rerun()
