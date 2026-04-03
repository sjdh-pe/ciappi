import streamlit as st
import pandas as pd
from api.client import get, post, put
from components.styles import card_section
from components.listas import municipios


def show():
    st.markdown("""
        <div style="padding:4px 0 16px">
            <h2 style="margin:0;color:#1a3a5c">🏛️ ILPIs</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Instituições de Longa Permanência para Idosos
            </div>
        </div>
        <hr style="border:none;border-top:2px solid #e0e9f4;margin-bottom:20px">
    """, unsafe_allow_html=True)

    aba = st.tabs(["📋 Listar", "➕ Cadastrar", "✏️ Atualizar"])

    # ── Listar ───────────────────────────────────────────────────────────────
    with aba[0]:
        if st.button("🔄 Carregar ILPIs", type="primary"):
            with st.spinner("Carregando..."):
                try:
                    dados = get("/ilpis/")
                    if dados:
                        df = pd.DataFrame(dados)
                        cols_show = ["CODIGOILPI", "NOMEILPI", "MUNICIPIO",
                                     "CAPACIDADEIDOSOS", "IDOSOSRESIDENTES", "STATUS"]
                        df = df[[c for c in cols_show if c in df.columns]].copy()
                        df.columns = ["Código", "Nome", "Município",
                                      "Capacidade", "Residentes", "Status"][:len(df.columns)]
                        st.success(f"✅ {len(df)} ILPI(s) cadastrada(s).")
                        st.dataframe(
                            df, use_container_width=True, hide_index=True,
                            column_config={
                                "Código": st.column_config.NumberColumn("Cód.", format="%d", width="small"),
                                "Nome": st.column_config.TextColumn("Nome", width="large"),
                                "Município": st.column_config.TextColumn("Município"),
                                "Capacidade": st.column_config.NumberColumn("Capacidade", format="%d", width="small"),
                                "Residentes": st.column_config.NumberColumn("Residentes", format="%d", width="small"),
                                "Status": st.column_config.TextColumn("Status", width="small"),
                            }
                        )
                    else:
                        st.info("Nenhuma ILPI cadastrada.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Cadastrar ────────────────────────────────────────────────────────────
    with aba[1]:
        with st.container(border=True):
            card_section("Identificação")
            nome = st.text_input("Nome da ILPI *", placeholder="Nome completo da instituição")

            col1, col2 = st.columns(2)
            responsavel = col1.text_input("Responsável *", placeholder="Nome do responsável")
            tipo = col2.selectbox("Tipo de Entidade *", ["Pública", "Privada", "Filantrópica"])

            card_section("Capacidade")
            col3, col4 = st.columns(2)
            capacidade = col3.number_input("Capacidade Total *", min_value=0)
            residentes = col4.number_input("Residentes Atuais *", min_value=0)

            card_section("Endereço")
            logradouro = st.text_input("Logradouro *", placeholder="Rua, Av., etc.")
            col5, col6 = st.columns(2)
            bairro    = col5.text_input("Bairro *")
            municipio = col6.selectbox("Município *", [""] + municipios(), key="ilpi_mun")

            status = st.selectbox("Status", ["Ativo", "Inativo"])
            salvar = st.button("💾 Cadastrar ILPI", use_container_width=True, type="primary")

        if salvar:
            if not all([nome, responsavel, logradouro, bairro]) or not municipio:
                st.error("⚠️ Todos os campos obrigatórios (*) devem ser preenchidos.")
            else:
                with st.spinner("Cadastrando..."):
                    try:
                        post("/ilpis/", {
                            "NOMEILPI":         nome.upper(),
                            "RESPONSAVELILPI":  responsavel.upper(),
                            "TIPOENTIDADE":     tipo,
                            "CAPACIDADEIDOSOS": capacidade,
                            "IDOSOSRESIDENTES": residentes,
                            "LOGRADOURO":       logradouro.upper(),
                            "BAIRRO":           bairro.upper(),
                            "MUNICIPIO":        municipio.upper(),
                            "STATUS":           status,
                        })
                        st.success("✅ ILPI cadastrada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro: {e}")

    # ── Atualizar ────────────────────────────────────────────────────────────
    with aba[2]:
        with st.container(border=True):
            col_c, col_b = st.columns([2, 1])
            codigo = col_c.number_input("Código da ILPI", min_value=1, step=1,
                                        label_visibility="collapsed")
            if col_b.button("📂 Carregar", use_container_width=True):
                with st.spinner("Carregando..."):
                    try:
                        st.session_state["ilpi_edicao"] = get(f"/ilpis/{codigo}")
                    except Exception:
                        st.error("ILPI não encontrada.")

        if "ilpi_edicao" in st.session_state:
            i = st.session_state["ilpi_edicao"]
            st.markdown(
                f"""<div style="background:#f8fbff;border:1px solid #cfe2ff;border-radius:10px;
                    padding:14px 18px;margin:8px 0">
                    <strong style="font-size:16px">{i.get('NOMEILPI','')}</strong>
                    <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                        {i.get('MUNICIPIO','')} · {i.get('TIPOENTIDADE','')} ·
                        Responsável: {i.get('RESPONSAVELILPI','')}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )
            with st.form("form_atu_ilpi"):
                col1, col2 = st.columns(2)
                nova_cap = col1.number_input("Capacidade", value=int(i.get("CAPACIDADEIDOSOS") or 0))
                novos_res = col2.number_input("Residentes Atuais", value=int(i.get("IDOSOSRESIDENTES") or 0))
                status_idx = 0 if i.get("STATUS") == "Ativo" else 1
                novo_status = st.selectbox("Status", ["Ativo", "Inativo"], index=status_idx)
                salvar_atu = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")

            if salvar_atu:
                with st.spinner("Salvando..."):
                    try:
                        put(f"/ilpis/{i['CODIGOILPI']}", {
                            "CAPACIDADEIDOSOS": nova_cap,
                            "IDOSOSRESIDENTES": novos_res,
                            "STATUS": novo_status,
                        })
                        st.success("✅ ILPI atualizada com sucesso!")
                        del st.session_state["ilpi_edicao"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
