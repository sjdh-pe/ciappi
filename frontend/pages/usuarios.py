import streamlit as st
import pandas as pd
from api.client import get


def show():
    st.markdown("""
        <div style="padding:4px 0 16px">
            <h2 style="margin:0;color:#1a3a5c">👤 Usuários</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Idosos atendidos pelo programa
            </div>
        </div>
        <hr style="border:none;border-top:2px solid #e0e9f4;margin-bottom:20px">
    """, unsafe_allow_html=True)

    aba = st.tabs(["🔍 Buscar por Nome", "📄 Detalhe do Cadastro"])

    # ── Buscar por Nome ──────────────────────────────────────────────────────
    with aba[0]:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            nome   = col1.text_input("Nome do Idoso", placeholder="Digite parte do nome...",
                                     label_visibility="collapsed")
            buscar = col2.button("🔍 Buscar", use_container_width=True, type="primary")

        if buscar:
            with st.spinner("Buscando..."):
                try:
                    dados = get("/usuarios/", {"nome": nome} if nome else {})
                    if dados:
                        df = pd.DataFrame(dados)
                        cols_disp = ["tbnumerocadastro", "tbnome", "tbcaso",
                                     "tbidade", "tbsexo", "tbmunicipio"]
                        df = df[[c for c in cols_disp if c in df.columns]].copy()
                        df.columns = ["Nº Cadastro", "Nome", "Caso",
                                      "Idade", "Sexo", "Município"][:len(df.columns)]
                        st.success(f"✅ {len(df)} usuário(s) encontrado(s).")
                        st.dataframe(
                            df, use_container_width=True, hide_index=True,
                            column_config={
                                "Nº Cadastro": st.column_config.NumberColumn("Nº", format="%d", width="small"),
                                "Nome": st.column_config.TextColumn("Nome", width="large"),
                                "Caso": st.column_config.NumberColumn("Caso", format="%d", width="small"),
                                "Idade": st.column_config.NumberColumn("Idade", format="%d anos", width="small"),
                                "Sexo": st.column_config.TextColumn("Sexo", width="small"),
                                "Município": st.column_config.TextColumn("Município"),
                            }
                        )
                    else:
                        st.info("Nenhum usuário encontrado.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Detalhe ──────────────────────────────────────────────────────────────
    with aba[1]:
        with st.container(border=True):
            col_n, col_b = st.columns([2, 1])
            num    = col_n.number_input("Nº do Cadastro", min_value=1, step=1,
                                        label_visibility="collapsed")
            carregar = col_b.button("📂 Carregar", use_container_width=True, type="primary")

        if carregar:
            with st.spinner("Carregando..."):
                try:
                    u = get(f"/usuarios/{num}")
                    st.markdown(f"""
                        <div style="background:#f8fbff;border:1px solid #cfe2ff;border-radius:10px;
                             padding:16px 20px;margin:8px 0">
                            <div style="font-size:18px;font-weight:700;color:#1a3a5c;margin-bottom:12px">
                                {u.get('tbnome','—')}
                            </div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px 24px">
                                <div><span style="color:#6b7c93;font-size:12px">CPF</span><br>
                                     <strong>{u.get('tbcpf','—')}</strong></div>
                                <div><span style="color:#6b7c93;font-size:12px">Caso Nº</span><br>
                                     <strong>{u.get('tbcaso','—')}</strong></div>
                                <div><span style="color:#6b7c93;font-size:12px">Sexo</span><br>
                                     <strong>{u.get('tbsexo','—')}</strong></div>
                                <div><span style="color:#6b7c93;font-size:12px">Idade</span><br>
                                     <strong>{u.get('tbidade','—')} anos</strong></div>
                                <div><span style="color:#6b7c93;font-size:12px">Município</span><br>
                                     <strong>{u.get('tbmunicipio','—')}</strong></div>
                                <div><span style="color:#6b7c93;font-size:12px">Faixa de Renda</span><br>
                                     <strong>{u.get('tbfaixarenda','—')}</strong></div>
                                <div><span style="color:#6b7c93;font-size:12px">Deficiência</span><br>
                                     <strong>{u.get('tbdeficiencia','—')}</strong></div>
                                <div><span style="color:#6b7c93;font-size:12px">Mora com</span><br>
                                     <strong>{u.get('tbcomquemmora','—')}</strong></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erro: {e}")
