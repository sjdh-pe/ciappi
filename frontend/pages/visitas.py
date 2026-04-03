import streamlit as st
import pandas as pd
from api.client import get, post
from datetime import datetime
from components.styles import card_section


def show():
    st.markdown("""
        <div style="padding:4px 0 16px">
            <h2 style="margin:0;color:#1a3a5c">🏢 Visitas Institucionais</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Registro de visitas a órgãos e instituições parceiras
            </div>
        </div>
        <hr style="border:none;border-top:2px solid #e0e9f4;margin-bottom:20px">
    """, unsafe_allow_html=True)

    aba = st.tabs(["📋 Listar", "➕ Registrar Visita"])

    # ── Listar ───────────────────────────────────────────────────────────────
    with aba[0]:
        if st.button("🔄 Carregar Visitas", type="primary"):
            with st.spinner("Carregando..."):
                try:
                    dados = get("/visitas/inst")
                    if dados:
                        df = pd.DataFrame(dados)
                        cols_show = ["codigovisita", "nomeinstituicao", "datavista", "assuntovisita"]
                        df = df[[c for c in cols_show if c in df.columns]].copy()
                        df.columns = ["Código", "Instituição", "Data", "Assunto"][:len(df.columns)]
                        if "Data" in df.columns:
                            df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
                        st.success(f"✅ {len(df)} visita(s) encontrada(s).")
                        st.dataframe(
                            df, use_container_width=True, hide_index=True,
                            column_config={
                                "Código": st.column_config.NumberColumn("Cód.", format="%d", width="small"),
                                "Instituição": st.column_config.TextColumn("Instituição", width="large"),
                                "Data": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY"),
                                "Assunto": st.column_config.TextColumn("Assunto"),
                            }
                        )
                    else:
                        st.info("Nenhuma visita registrada.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Registrar ────────────────────────────────────────────────────────────
    with aba[1]:
        with st.container(border=True):
            card_section("Identificação")
            instituicao = st.text_input("Nome da Instituição *", placeholder="Ex: Delegacia da Mulher")
            col1, col2 = st.columns(2)
            dt_visita   = col1.date_input("Data da Visita *")
            responsavel = col2.text_input("Responsável pela Instituição")
            assunto     = st.text_input("Assunto da Visita *", placeholder="Ex: Reunião de alinhamento")

            card_section("Relatório")
            relatorio = st.text_area("Relatório *", height=130,
                                     placeholder="Descreva o que foi tratado na visita...")
            lembrete  = st.date_input("Lembrete (opcional)", value=None)

            salvar = st.button("💾 Registrar Visita", use_container_width=True, type="primary")

        if salvar:
            if not all([instituicao, assunto, relatorio]):
                st.error("⚠️ Preencha os campos obrigatórios (*).")
            else:
                with st.spinner("Registrando..."):
                    try:
                        dados = {
                            "nomeinstituicao":        instituicao,
                            "datavista":              str(datetime.combine(dt_visita, datetime.min.time())),
                            "assuntovisita":          assunto,
                            "responsavelinstituicao": responsavel,
                            "relatorio":              relatorio,
                        }
                        if lembrete:
                            dados["lembrete"] = str(datetime.combine(lembrete, datetime.min.time()))
                        post("/visitas/inst", dados)
                        st.success("✅ Visita registrada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro: {e}")
