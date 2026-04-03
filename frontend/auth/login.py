import streamlit as st
from api.client import login


def show_login():
    # Centraliza o formulário com colunas
    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        st.markdown("""
            <div style="text-align:center;padding:32px 0 24px">
                <div style="font-size:52px">🛡️</div>
                <div style="font-size:26px;font-weight:800;color:#1a3a5c;margin-top:8px">CIAPPI</div>
                <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                    Sistema de Proteção ao Idoso<br>
                    Secretaria de Justiça e Direitos Humanos — PE
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### Acesso ao Sistema")
            nome  = st.text_input("Nome do Técnico", placeholder="Digite seu nome completo")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            entrar = st.button("Entrar →", use_container_width=True, type="primary")

        if entrar:
            if not nome or not senha:
                st.error("⚠️ Informe o nome e a senha.")
                return
            try:
                dados = login(nome, senha)
                st.session_state["token"]         = dados["access_token"]
                st.session_state["nivel"]         = dados["nivel"]
                st.session_state["usuario_nome"]  = dados["nome"]
                st.session_state["autenticado"]   = True
                st.rerun()
            except Exception:
                st.error("❌ Nome do técnico ou senha incorretos.")

        st.markdown("""
            <div style="text-align:center;font-size:11px;color:#adb5bd;padding-top:16px">
                CIAPPI v2.0 · SJDH/PE · 2025
            </div>
        """, unsafe_allow_html=True)


def logout():
    for chave in ["token", "nivel", "usuario_nome", "autenticado", "pagina"]:
        st.session_state.pop(chave, None)
    st.rerun()
